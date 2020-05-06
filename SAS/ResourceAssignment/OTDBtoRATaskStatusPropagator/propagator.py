#!/usr/bin/env python3
# $Id$

'''
TODO: add doc
'''
import logging
from datetime import datetime, timedelta
from optparse import OptionParser
from lofar.common.util import waitForInterrupt
from lofar.common.datetimeutils import parseDatetime
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, UsingToBusMixin
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.common import dbcredentials

logger = logging.getLogger(__name__)

STORAGE_CLAIM_EXTENSION=timedelta(days=365)

class OTDBtoRATaskStatusPropagator(UsingToBusMixin, OTDBEventMessageHandler):
    def __init__(self):
        super().__init__()
        self.otdb = None
        self.radb = None

    def init_tobus(self, exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER):
        super().init_tobus(exchange, broker)
        self.otdb  = OTDBRPC.create(exchange=exchange, broker=broker)
        self.radb = RADBRPC.create(exchange=exchange, broker=broker)

    def start_handling(self):
        self.otdb.open()
        self.radb.open()
        super().start_handling()

    def stop_handling(self):
        self.otdb.close()
        self.radb.close()
        super().stop_handling()

    def _update_radb_task_status(self, otdb_id, task_status):
        try:
            if task_status in ['approved', 'prescheduled', 'obsolete']:
                radb_task = self.radb.getTask(otdb_id=otdb_id)
                if (radb_task and radb_task['status'] in ['queued', 'active', 'completing']):
                    # set task to aborted first, so other controls (e.g. pipelinecontrol)
                    # can respond to the aborted event
                    logger.info("aborting radb-task with otdb_id %s from status %s" % (otdb_id, radb_task['status']))
                    result = self.radb.updateTaskStatusForOtdbId(otdb_id=otdb_id, task_status='aborted')

            logger.info("updating radb-task with otdb_id %s to status %s" % (otdb_id, task_status))
            result = self.radb.updateTaskStatusForOtdbId(otdb_id=otdb_id, task_status=task_status)

            radb_task = self.radb.getTask(otdb_id=otdb_id)

            if result:
                logger.info("updated task with otdb_id %s to status %s", otdb_id, radb_task['status'] if radb_task else 'unknown')
            else:
                logger.warning("could not update task with otdb_id %s to status %s. Current status = %s ", otdb_id, task_status, radb_task['status'] if radb_task else 'unknown')
        except Exception as e:
            logger.error(e)

    def _updateStartStopTimesFromSpecification(self, treeId):
        # cep2 jobs still get scheduled via old scheduler
        # so, if the start/endtime were changed in the old scheduler
        # and the times are different to the radb times, then propagate these to radb
        try:
            radb_task = self.radb.getTask(otdb_id=treeId)
            if radb_task:
                # all tasks other than for CEP2 have storage claim(s)
                # and we do not want OTDB to update our RA scheduled tasks
                # so check if we have storage claims
                claims = self.radb.getResourceClaims(task_ids=radb_task['id'], resource_type='storage')

                if not claims:
                    #this is a CEP2 task, modified by the old scheduler
                    #update start/stop time
                    spec = self.otdb.taskGetSpecification(otdb_id=treeId)['specification']
                    new_startime = spec['ObsSW.Observation.startTime']
                    new_endtime = spec['ObsSW.Observation.stopTime']

                    new_startime = parseDatetime(new_startime)
                    new_endtime = parseDatetime(new_endtime)
                    new_endtime = max(new_endtime, radb_task['starttime']+timedelta(seconds=1)) # make sure endtime is always > starttime

                    logger.info("Updating task (otdb_id=%s, radb_id=%s, status=%s) startime to \'%s\' and endtime to \'%s\'", treeId, radb_task['id'], radb_task['status'], new_startime, new_endtime)
                    self.radb.updateTaskAndResourceClaims(radb_task['id'], starttime=new_startime, endtime=new_endtime)
        except Exception as e:
            logger.error(e)

    def onObservationPrepared(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'prepared')

    def onObservationApproved(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'approved')
        self._updateStartStopTimesFromSpecification(treeId)

    def onObservationOnHold(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'on_hold')

    def onObservationConflict(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'conflict')

    def onObservationError(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'error')

    def onObservationObsolete(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'obsolete')

    def onObservationPrescheduled(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'prescheduled')

    def onObservationScheduled(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'scheduled')
        self._updateStartStopTimesFromSpecification(treeId)

        try:
            radb_task = self.radb.getTask(otdb_id=treeId)
            if radb_task:
                #reschedule all scheduled successor tasks
                #because they might need to update their specification due to this scheduled task
                successor_tasks = self.radb.getTasks(task_ids=radb_task['successor_ids'], task_status=['scheduled', 'queued'])
                for successor_task in successor_tasks:
                    logger.info('rescheduling otdb_id=%s because it is a successor of the just scheduled task otdb_id=%s', successor_task['otdb_id'], radb_task['otdb_id'])
                    self.otdb.taskSetStatus(successor_task['otdb_id'], 'prescheduled')
        except Exception as e:
            logger.error(e)

    def onObservationQueued(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'queued')

        try:
            # pipeline control puts tasks in queued state for pipelines,
            # and gives the pipeline to slurm
            # from that moment it is not known exactly when the task will run.
            # we do know however that it will run after its predecessors, and after 'now'
            # reflect that in radb for pipelines
            task = self.radb.getTask(otdb_id=treeId)
            if task and task['type'] == 'pipeline' and 'predecessor_ids' in task:
                predecessor_tasks = [self.radb.getTask(pid) for pid in task['predecessor_ids']]
                if predecessor_tasks:
                    pred_endtimes = [t['endtime'] for t in predecessor_tasks]
                    max_pred_endtime = max(pred_endtimes)
                    new_startime = max([max_pred_endtime, datetime.utcnow()])
                    new_endtime = new_startime + timedelta(seconds=task['duration'])

                    logger.info("Updating task %s (otdb_id=%s, status=active) startime to \'%s\' and endtime to \'%s\' except for storage claims",
                                task['id'], treeId, new_startime, new_endtime)

                    #update task and all claim start/endtimes, except for storage claims.
                    non_storage_resource_type_ids = [rt['id'] for rt in self.radb.getResourceTypes() if rt['name'] != 'storage']
                    self.radb.updateTaskAndResourceClaims(task['id'],
                                                        where_resource_types=non_storage_resource_type_ids,
                                                        starttime=new_startime,
                                                        endtime=new_endtime)

                    #get remaining storage claims...
                    #and update storage start/end times (including 1 year extra)
                    logger.info("Updating storage claims for task %s (otdb_id=%s, status=active) startime to \'%s\' and endtime to \'%s\' (with extra storage claim time)",
                                task['id'], treeId, new_startime, new_endtime+STORAGE_CLAIM_EXTENSION)

                    storage_claims = self.radb.getResourceClaims(task_ids=task['id'], resource_type='storage')
                    storage_claim_ids = [c['id'] for c in storage_claims]
                    self.radb.updateResourceClaims(where_resource_claim_ids=storage_claim_ids,
                                                starttime=new_startime,
                                                endtime=new_endtime+STORAGE_CLAIM_EXTENSION)

        except Exception as e:
            logger.error(e)

    def onObservationStarted(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'active')

        # otdb adjusts starttime when starting,
        # reflect that in radb for pipelines
        radb_task = self.radb.getTask(otdb_id=treeId)
        if radb_task and radb_task['type'] == 'pipeline':
            otdb_task = self.otdb.taskGetTreeInfo(otdb_id=treeId)
            if otdb_task:
                new_startime = otdb_task['starttime']
                new_endtime = new_startime + timedelta(seconds=radb_task['duration'])

                logger.info("Updating task %s (otdb_id=%s, status=active) startime to \'%s\' and endtime to \'%s\' except for storage claims",
                            radb_task['id'], treeId, new_startime, new_endtime)

                #update task and all claim start/endtimes, except for storage claims.
                non_storage_resource_type_ids = [rt['id'] for rt in self.radb.getResourceTypes() if rt['name'] != 'storage']
                self.radb.updateTaskAndResourceClaims(radb_task['id'],
                                                      where_resource_types=non_storage_resource_type_ids,
                                                      starttime=new_startime,
                                                      endtime=new_endtime)

                #get remaining storage claims...
                #and update storage start/end times (including 1 year extra)
                logger.info("Updating storage claims for task %s (otdb_id=%s, status=active) startime to \'%s\' and endtime to \'%s\' with extra claim time",
                            radb_task['id'], treeId, new_startime, new_endtime)

                storage_claims = self.radb.getResourceClaims(task_ids=radb_task['id'], resource_type='storage')
                storage_claim_ids = [c['id'] for c in storage_claims]
                self.radb.updateResourceClaims(where_resource_claim_ids=storage_claim_ids,
                                               starttime=new_startime,
                                               endtime=new_endtime+STORAGE_CLAIM_EXTENSION)

    def onObservationCompleting(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'completing')

        # otdb adjusts stoptime when completing,
        self._updateStopTime(treeId, ['observation'])

    def _updateStopTime(self, treeId, task_types=None):
        radb_task = self.radb.getTask(otdb_id=treeId)
        if radb_task:
            if task_types and radb_task['type'] not in task_types:
                return

            otdb_task = self.otdb.taskGetTreeInfo(otdb_id=treeId)
            if otdb_task is None:
                logger.warning('could not find otdb task with id %s', treeId)
                return

            now = datetime.utcnow()
            if (now < otdb_task['stoptime'] #early stop/abort
                or otdb_task['starttime'] != radb_task['starttime'] or otdb_task['stoptime'] != radb_task['endtime']): #change in spec
                new_endtime = min(now, otdb_task['stoptime'])
                new_endtime = max(new_endtime, radb_task['starttime']+timedelta(seconds=1)) # make sure endtime is always > starttime

                logger.info("Updating task %s (otdb_id=%s, status=%s) endtime to \'%s\' except for storage resource claims", radb_task['id'], treeId, radb_task['status'], new_endtime)

                #update task and all claim endtimes, except for storage claims.
                non_storage_resource_type_ids = [rt['id'] for rt in self.radb.getResourceTypes() if rt['name'] != 'storage']
                self.radb.updateTaskAndResourceClaims(radb_task['id'],
                                                      where_resource_types=non_storage_resource_type_ids,
                                                      endtime=new_endtime)

                #get remaining storage claims...
                #and extend storage end time
                logger.info("Updating storage claims for task %s (otdb_id=%s, status=%s) endtime to \'%s\' (with extra storage claim time)",
                            radb_task['id'], treeId, radb_task['status'], new_endtime+STORAGE_CLAIM_EXTENSION)

                storage_claims = self.radb.getResourceClaims(task_ids=radb_task['id'], resource_type='storage')
                storage_claim_ids = [c['id'] for c in storage_claims]
                self.radb.updateResourceClaims(where_resource_claim_ids=storage_claim_ids,
                                               endtime=new_endtime+STORAGE_CLAIM_EXTENSION)

    def onObservationFinished(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'finished')

        # otdb adjusts stoptime when finishing,
        # reflect that in radb for pipelines
        self._updateStopTime(treeId, ['pipeline'])

    def onObservationAborted(self, treeId, modificationTime):
        self._update_radb_task_status(treeId, 'aborted')

        # otdb adjusts stoptime when aborted,
        self._updateStopTime(treeId)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='runs the resourceassignment database service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('-e', "--exchange", dest="exchange", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Bus or queue where the OTDB notifications are published. [default: %default]")
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")
    (options, args) = parser.parse_args()

    dbcreds = dbcredentials.parse_options(options)
    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    with OTDBBusListener(handler_type=OTDBtoRATaskStatusPropagator,
                         exchange=options.exchange, broker=options.broker,
                         num_threads=1):
        waitForInterrupt()

if __name__ == '__main__':
    main()
