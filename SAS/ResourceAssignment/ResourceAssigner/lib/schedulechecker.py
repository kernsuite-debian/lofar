#!/usr/bin/env python3

#
# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#

import logging
from time import sleep
from threading import Thread

from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.sas.datamanagement.cleanup.rpc import CleanupRPC
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.messaging.rpc import RPCException

from lofar.sas.resourceassignment.resourceassigner.config import PIPELINE_CHECK_INTERVAL
from lofar.common.datetimeutils import *

logger = logging.getLogger(__name__)


def movePipelineAfterItsPredecessors(task, radbrpc, min_start_timestamp=None):
    try:
        #only reschedule pipelines which run on cep4
        if task and task['type'] == 'pipeline' and task.get('cluster') == 'CEP4':
            logger.info("checking pipeline starttime radb_id=%s otdb_id=%s starttime=%s",
                        task['id'], task['otdb_id'], task['starttime'])

            predecessor_tasks = radbrpc.getTasks(task_ids=task['predecessor_ids'])

            predecessor_endtimes = [t['endtime'] for t in predecessor_tasks]
            if min_start_timestamp:
                predecessor_endtimes.append(min_start_timestamp)

            max_pred_endtime = max(predecessor_endtimes)

            if (task['starttime'] < max_pred_endtime) or (min_start_timestamp and task['starttime'] > min_start_timestamp):
                shift = max_pred_endtime - task['starttime']
                newStartTime = task['starttime']+shift
                newEndTime = task['endtime']+shift

                # move pipeline even further ahead in case there are more than 2 overlapping scheduled/queued pipelines
                while True:
                    overlapping_pipelines = radbrpc.getTasks(lower_bound=newStartTime, upper_bound=newEndTime, task_type='pipeline', task_status=['scheduled', 'queued', 'active', 'completing'], cluster='CEP4')
                    #exclude self
                    overlapping_pipelines = [pl for pl in overlapping_pipelines if pl['id'] != task['id']]

                    if len(overlapping_pipelines) >= 1:
                        max_overlapping_pipeline_endtime = max([t['endtime'] for t in overlapping_pipelines])
                        shift = max_overlapping_pipeline_endtime + timedelta(minutes=1) - task['starttime']
                        newStartTime = task['starttime']+shift
                        newEndTime = task['endtime']+shift
                    else:
                        break

                if shift != timedelta(seconds=0):
                    logger.info("Moving %s pipeline radb_id=%s otdb_id=%s by %s from \'%s\' to \'%s\'", task['status'], task['id'], task['otdb_id'], format_timedelta(shift), task['starttime'], newStartTime)
                    try:
                        radbrpc.updateTaskAndResourceClaims(task['id'], starttime=newStartTime, endtime=newEndTime)
                    except RPCException as e:
                        logger.warning("Could not update start/endtime for pipeline radb_id=%s otdb_id=%s error: %s",
                                       task['id'], task['otdb_id'], e)

                    updated_task = radbrpc.getTask(task['id'])

                    if updated_task['status'] != task['status']:
                        logger.warning("Moving of pipeline radb_id=%s otdb_id=%s caused the status to change from %s to %s", updated_task['id'], updated_task['otdb_id'], task['status'], updated_task['status'])
                        #TODO: automatically resolve conflict status by moved pipeline in first free time slot.
    except Exception as e:
        logger.error("Error while checking pipeline starttime: %s", e)


class ScheduleChecker():
    def __init__(self,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):
        """
        """
        self._thread = None
        self._running = False
        self._radbrpc = RADBRPC.create(exchange=exchange, broker=broker)
        self._momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)
        self._curpc = CleanupRPC.create(exchange=exchange, broker=broker)
        self._otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker, timeout=180)

    def __enter__(self):
        """Internal use only. (handles scope 'with')"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Internal use only. (handles scope 'with')"""
        self.stop()

    def start(self):
        """Open rpc connections to radb service and resource estimator service"""
        self._radbrpc.open()
        self._momrpc.open()
        self._curpc.open()
        self._otdbrpc.open()
        self._running = True
        self._thread = Thread(target=self._check_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Close rpc connections to radb service and resource estimator service"""
        self._radbrpc.close()
        self._momrpc.close()
        self._curpc.close()
        self._otdbrpc.close()
        self._running = False
        self._thread.join(60)

    def checkRunningPipelines(self):
        """ Update the end time of pipelines if they are running
            beyond their scheduled end time. """

        try:
            now = datetime.utcnow()

            active_pipelines = self._radbrpc.getTasks(task_status='active', task_type='pipeline')

            if active_pipelines:
                logger.info('checking endtime of running pipelines')

            for task in active_pipelines:
                if task['endtime'] <= now:
                    new_endtime=now+timedelta(seconds=PIPELINE_CHECK_INTERVAL)
                    logger.info("Extending endtime to %s for pipeline radb_id=%s otdb_id=%s", new_endtime, task['id'], task['otdb_id'])
                    try:
                        self._radbrpc.updateTaskAndResourceClaims(task['id'], endtime=new_endtime)
                    except Exception as e:
                        logger.error("Could not extend endtime to %s for pipeline radb_id=%s otdb_id=%s error: %s",
                                     new_endtime, task['id'], task['otdb_id'], e)

        except Exception as e:
            logger.error("Error while checking running pipelines: %s", e)

    def checkScheduledAndQueuedPipelines(self):
        """ Move the start time of scheduled/queued pipelines back if their
            predecessor is still running. """
        try:
            now = datetime.utcnow()
            min_start_timestamp = now + timedelta(seconds=PIPELINE_CHECK_INTERVAL)
            #round to next minute
            min_start_timestamp = datetime(min_start_timestamp.year,
                                           min_start_timestamp.month ,
                                           min_start_timestamp.day,
                                           min_start_timestamp.hour,
                                           min_start_timestamp.minute+1)

            pipelines = self._radbrpc.getTasks(task_status=['scheduled', 'queued'], task_type='pipeline', cluster='CEP4')

            if pipelines:
                logger.info('checking starttime of %s scheduled/queued cep4 pipelines min_start_timestamp=%s', len(pipelines), min_start_timestamp)
                pipelines.sort(key=lambda pl: pl['starttime'], reverse=True)

                for task in pipelines:
                    # moving pipelines might take a while
                    # so this task might have changed status to active
                    # in that case we don't want to move it
                    uptodate_task = self._radbrpc.getTask(task['id'])
                    if uptodate_task['status'] in ['scheduled', 'queued']:
                        movePipelineAfterItsPredecessors(uptodate_task, self._radbrpc, min_start_timestamp)
        except Exception as e:
            logger.error("Error while checking scheduled pipelines: %s", e)

    def checkUnRunTasksForMoMOpenedStatus(self):
        """

          If tasks go to "opened" in MoM, they are deleted from OTDB without sending a notification.

          Here, we check for jobs that are yet to run, and are in "opened" in MoM. Such jobs are subsequently deleted from the RADB.
        """
        try:
            logger.info('checking unfinished tasks for status in mom')
            unrun_tasks = self._radbrpc.getTasks(task_status=['approved', 'scheduled', 'prescheduled', 'queued', 'error', 'aborted'],
                                                 task_type=['observation', 'pipeline'],
                                                 lower_bound=datetime.utcnow() - timedelta(minutes=30))
            mom_ids = [t['mom_id'] for t in unrun_tasks]
            mom_details = self._momrpc.getObjectDetails(mom_ids)

            for task in unrun_tasks:
                try:
                    mom_id = int(task['mom_id'])
                    mom_status = mom_details[mom_id].get('object_status') if mom_id in mom_details else None
                    if (mom_id not in mom_details or
                        mom_status in ['opened', 'described', 'suspended']):
                        logger.warning('task %s mom_id=%s otdb_id=%s has radb_status=%s and mom_status=%s => Would normally remove task from radb, ignoring for now',
                                    task['id'],
                                    task['mom_id'],
                                    task['otdb_id'],
                                    task['status'],
                                    mom_status)

                        if mom_status in ['opened', 'described']:
                            # auto delete data for tasks which went back to opened in mom (for pipeline restarts for example)
                            # The reason to delete it here is because otherwise the cleanupservice tries to get it's info from an already deleted task in radb/otdb
                            path_result = self._curpc.getPathForOTDBId(task['otdb_id'])
                            if path_result['found']:
                                logger.info("removing data on disk from previous run for otdb_id %s", task['otdb_id'])
                                result = self._curpc.removeTaskData(task['otdb_id'])

                                if not result['deleted']:
                                    logger.warning("could not remove all data on disk from previous run for otdb_id %s: %s", task['otdb_id'], result['message'])

                        # delete the spec (and task/claims etc via cascading delete) from radb to get it in sync again with mom
                        self._radbrpc.deleteSpecification(task['specification_id'])
                except Exception as e:
                    logger.error("Error while checking unrun task mom_id=%s otdb_id=%s radb_id=%s for MoM opened/described/suspended status: %s",
                                 task['mom_id'],
                                 task['otdb_id'],
                                 task['id'],
                                 e)
        except Exception as e:
            logger.error("Error while checking unrun tasks for  MoM opened/described/suspended status: %s", e)

    def checkUnRunReservations(self):
        """All non-mon tasks in otdb can be deleted in otdb without us knowing about it (there is no otdb-task-deleted event)
          Here, we check for all non-mom tasks that are yet to run if they still exist in otdb. If not, such jobs are subsequently deleted from the RADB.
        """
        try:
            logger.info('checking reservations in otdb')
            reservations = self._radbrpc.getTasks(task_type=['reservation'], lower_bound=datetime.utcnow())

            for reservation in reservations:
                try:
                    otdb_id = int(reservation['otdb_id'])
                    status = self._otdbrpc.taskGetStatus(otdb_id)
                    logger.info('reservation %s status = %s', otdb_id, status)

                    if status not in ['scheduled', 'unscheduled']:
                        logger.info('deleting reservation otdb_id=%s radb_id=%s otdb_status=%s from rabd',
                                    otdb_id, reservation['id'], status)
                        # delete the spec (and task/claims etc via cascading delete) from radb to get it in sync again with mom
                        self._radbrpc.deleteSpecification(reservation['specification_id'])
                except Exception as e:
                    logger.error("Error while checking reservation otdb_id=%s radb_id=%s in otdb: %s",
                                 reservation['otdb_id'],
                                 reservation['id'],
                                 e)
        except Exception as e:
            logger.error("Error while checking unrun tasks for  MoM opened/described/suspended status: %s", e)

    def _check_loop(self):
        while self._running:
            self.checkRunningPipelines()
            self.checkScheduledAndQueuedPipelines()
            self.checkUnRunTasksForMoMOpenedStatus()
            self.checkUnRunReservations()

            for i in range(PIPELINE_CHECK_INTERVAL):
                sleep(1)

                if not self._running:
                    break
