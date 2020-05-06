#!/usr/bin/env python3

# Copyright (C) 2015-2017
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
# $Id: resource_assigner.py 1580 2015-09-30 14:18:57Z loose $

"""
ResourceAssigner inserts/updates tasks and assigns resources to it based on incoming parset.
"""

import logging

from lofar.common.cache import cache
from lofar.messaging.messages import EventMessage
from lofar.messaging.messagebus import ToBus
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import single_line_with_single_spaces

from lofar.sas.resourceassignment.database.radb import RADatabase
from lofar.sas.otdb.otdbrpc import OTDBRPC

from lofar.sas.resourceassignment.resourceassigner.config import DEFAULT_RA_NOTIFICATION_PREFIX

from lofar.sas.resourceassignment.resourceassigner.resource_availability_checker import ResourceAvailabilityChecker
from lofar.sas.resourceassignment.resourceassigner.schedulers import BasicScheduler, DwellScheduler, PriorityScheduler

from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

from lofar.sas.datamanagement.storagequery.rpc import StorageQueryRPC
from lofar.sas.datamanagement.cleanup.rpc import CleanupRPC
from lofar.mac.observation_control_rpc import ObservationControlRPCClient

from lofar.sas.resourceassignment.resourceassignmentestimator.rpc import ResourceEstimatorRPC

from lofar.sas.resourceassignment.common.specification import Specification

logger = logging.getLogger(__name__)


class ResourceAssigner(object):
    """
    The ResourceAssigner inserts new tasks or updates existing tasks in the RADB and assigns resources to it based on
    a task's parset.
    """

    def __init__(self,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER,
                 radb_dbcreds=None):
        """
        Creates a ResourceAssigner instance

        :param exchange: name of the bus on which the services listen (default: lofar)
        :param ra_notification_prefix: prefix used in notification message subject (default: ResourceAssigner.)
        :param broker: Valid Qpid broker host (default: None, which means localhost)
        :param radb_dbcreds: the credentials to be used for accessing the RADB (default: None, which means default)
        """

        self.radb = RADatabase(dbcreds=radb_dbcreds)
        self.rerpc = ResourceEstimatorRPC.create(exchange=exchange, broker=broker)
        self.otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker)
        self.momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)
        self.sqrpc = StorageQueryRPC.create(exchange=exchange, broker=broker)
        self.curpc = CleanupRPC.create(exchange=exchange, broker=broker)
        self.ra_notification_bus = ToBus(exchange=exchange, broker=broker)
        self.obscontrol = ObservationControlRPCClient.create(exchange=exchange, broker=broker)

        self.resource_availability_checker = ResourceAvailabilityChecker(self.radb)

        # For the DwellScheduler instances created during run-time we store the following variables
        self.radb_creds = radb_dbcreds
        self.broker = broker

    def __enter__(self):
        """Internal use only. (handles scope 'with')"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Internal use only. (handles scope 'with')"""
        self.close()

    def open(self):
        """Open connections to various service/buses/databases"""
        logger.debug("resource_assigner opening all bus/db connections")
        self.radb.connect()
        self.rerpc.open()
        self.otdbrpc.open()
        self.momrpc.open()
        self.sqrpc.open()
        self.curpc.open()
        self.ra_notification_bus.open()
        self.obscontrol.open()
        logger.info("resource_assigner opened all bus/db connections")

    def close(self):
        """Close connections to various service/buses/databases"""
        logger.debug("resource_assigner closing all bus/db connections")
        self.obscontrol.close()
        self.radb.disconnect()
        self.rerpc.close()
        self.otdbrpc.close()
        self.momrpc.close()
        self.sqrpc.close()
        self.curpc.close()
        self.ra_notification_bus.close()
        logger.info("resource_assigner closed all bus/db connections")

    @property
    @cache
    def resource_types(self):
        """ Returns a dict of all the resource types, to convert name->id. """

        return {rt['name']: rt['id'] for rt in self.radb.getResourceTypes()}

    def do_assignment(self, otdb_id, specification_tree):
        """
        Makes the given task known to RADB and attempts to assign (schedule) its requested resources.

        If no list of requested resources could be determined for the task, its status will be set to "error" in RADB.
        If such list can be obtained but it is impossible to assign the requested resources, the task is in conflict
        with other tasks, hence its status will be set to "conflict" in RADB. If all requested resources are
        successfully assigned, its status will be put to "scheduled" in RADB.

        :param otdb_id: OTDB ID of the main task which resources need to be assigned
        :param specification_tree: the specification tree containing the main task and its resources

        :raises an Exception if something unforeseen happened while scheduling
        """

        logger.info('do_assignment: otdb_id=%s specification_tree=%s', otdb_id, specification_tree)

        spec = Specification(self.otdbrpc, self.momrpc, self.radb)
        spec.from_dict(specification_tree)
        spec.insert_into_radb() # TODO Move this to TaskSpecified?

        # Don't perform any scheduling for tasks that are only approved. Do this check after insertion of
        # specification, task and predecessor/successor relations, so approved tasks appear correctly in the web
        # scheduler.
        if spec.status == 'approved': # Only needed to send misc field info (storagemanager) to OTDB
            logger.info('Task otdb_id=%s is only approved, no resource assignment needed yet' % otdb_id)
            self._send_task_status_notification(spec, 'approved')
            return
        #TODO have Specification propagate to the estimator?
        if self._schedule_resources(spec, specification_tree):
            # Cleanup the data of any previous run of the task
            self._cleanup_earlier_generated_data(otdb_id, spec)

            # Scheduling of resources for this task succeeded, so change task status to "scheduled" and notify
            # our subscribers
            spec.set_status('scheduled')
            self._send_task_status_notification(spec, 'scheduled')
        else:
            # Scheduling of resources for this task failed,
            # check if any of the claims has status conflict,
            # and hence (by the radb triggers) the task has status conflict as well
            # if task not in conflict, then there was a specification/scheduling error
            # so put task status to error (not conflict!)
            spec.read_from_radb(spec.radb_id) #TODO cleanup
            if spec.status == 'conflict':
                # Updating the task status when it is already in 'conflict' seems unnecessary, but in order to
                # satisfy the existing unit tests we put it in here.
                # TODO: discuss if this can be removed
                spec.set_status('conflict')

                # No need for a status change, but do notify our subscribers
                self._send_task_status_notification(spec, 'conflict')
            else:
                # The task is in an unexpected state, so force it to 'error' state and notify our subscribers
                spec.set_status('error')
                self._send_task_status_notification(spec, 'error')

    def _send_task_status_notification(self, spec, new_status):
        """
        Sends a message about the task's status on the RA notification bus

        :param spec:    the task concerned
        :param new_status:  the task's status

        :raises Exception if sending the notification fails
        """
        #TODO can maybe move to Specification in the future? Logically it should be resource_assigner that sends the notification
        content = {
            'radb_id': spec.radb_id,
            'otdb_id': spec.otdb_id,
            'mom_id': spec.mom_id
        }
        subject = 'Task' + new_status[0].upper() + new_status[1:] #TODO this is MAGIC, needs explanation!
        event_message = EventMessage(subject="%s.%s" % (DEFAULT_RA_NOTIFICATION_PREFIX, subject), content=content)

        logger.info('Sending notification %s: %s' % (subject, single_line_with_single_spaces(content)))
        self.ra_notification_bus.send(event_message)

    def _kill_task(self, task):
        """
        Kill the given tasks. Currently observation jobs are only supported

        :param task: the task to kill
        :raises ScheduleException if a task can't be killed because it's not an observation job
        """

        logger.debug("kill_task: task: %s", task)

        if task.type == "observation":
            self.obscontrol.abort_observation(task.otdb_id)
        else:
                # Killing scheduled pipelines only makes sense when they use resources other than storage, which is not
                # the case for current pipelines
                logger.error("Cannot kill jobs of type %s yet" % task["type"])

    def _get_resource_estimates(self, specification_tree):
        """
        Obtains the resource estimates from the Resource Estimator for the main task in the specification tree and
        validates them.

        :param specification_tree: the task's specification tree

        :return A list of resource estimates for the given task or None in case none could be obtained or if the
                validation failed.
        """

        otdb_id = specification_tree['otdb_id']

        estimates = self.rerpc.get_estimated_resources(specification_tree)
        logger.info('Resource Estimator reply = %s', estimates)

        if estimates['errors']:
            for error in estimates['errors']:
                logger.error("Error from Resource Estimator: %s", error)
            raise ValueError("Error(s) in estimator for otdb_id=%s" % (otdb_id, ))

        if any('resource_types' not in est for est in estimates['estimates']):
            raise ValueError("missing 'resource_types' in 'estimates' in estimator results: %s" % estimates)

        estimates = estimates['estimates']

        if not all(int(est_val) > 0 for est in estimates for est_val in list(est['resource_types'].values())):
            # Avoid div by 0 and inf looping from estimate <= 0 later on.
            raise ValueError("at least one of the estimates is not a positive number")

        return estimates

    def _schedule_resources(self, spec, specification_tree):
        """
        Schedule the requested resources for a task

        :param spec:  the task's specification

        :returns: True if successful, or False otherwise
        """
        logger.info("Received good estimates, scheduling resources for task %i", spec.radb_id)
        try:
            if spec.isTriggered():
                min_starttime, max_starttime, duration = spec.calculate_dwell_values(spec.starttime, spec.duration,
                                                                                    spec.min_starttime, spec.max_endtime)
                scheduler = DwellScheduler(task_id=spec.radb_id,
                                           specification_tree=specification_tree,
                                           resource_estimator=self._get_resource_estimates,
                                           resource_availability_checker=self.resource_availability_checker,
                                           radb=self.radb,
                                           min_starttime=min_starttime,
                                           max_starttime=max_starttime,
                                           duration=duration)
            else:
                scheduler = PriorityScheduler(task_id=spec.radb_id,
                                              specification_tree=specification_tree,
                                              resource_estimator=self._get_resource_estimates,
                                              resource_availability_checker=self.resource_availability_checker,
                                              radb=self.radb)
        except Exception as e:
            logger.exception('Error in scheduler._schedule_resources: %s', e) #Why are we mentioning _schedule_resources here?
            return False

        try:
            with scheduler:
                (scheduler_result, changed_tasks) = scheduler.allocate_resources()
                if not scheduler_result:
                    # try again with basic scheduler to end up with a situation with the 'normal' conflicting resources, which can then be evaluated by users
                    basic_scheduler = BasicScheduler(task_id=spec.radb_id,
                                                     specification_tree=specification_tree,
                                                     resource_estimator=self._get_resource_estimates,
                                                     resource_availability_checker=self.resource_availability_checker,
                                                     radb=self.radb)
                    with basic_scheduler:
                        (scheduler_result, changed_tasks) = basic_scheduler.allocate_resources()
                        return scheduler_result
                elif changed_tasks:
                    for t in changed_tasks:
                        if t.status == 'aborted': #MAC_Scheduler can't handle queued right now See also schedulers.py around line 600
                            self._kill_task(t) # We kill the task through obscontrol and then wait for the status from OTDB.
                        else: # should be approved (unscheduled)
                            self._send_task_status_notification(t, t.status) # Tell OTDB

        except Exception as e:
            logger.exception('Error in calling scheduler.allocate_resources: %s', e)
            return False

        logger.info('Resources successfully allocated task_id=%s' % spec.radb_id)
        return True

    def _cleanup_earlier_generated_data(self, otdb_id, spec):
        """
        Remove any output and/or intermediate data from any previous run of the task

        :param otdb_id: the task's OTDB ID
        :param spec:  the task's specification
        """

        # Only needed for pipeline tasks
        if spec.type == 'pipeline':
            try:
                du_result = self.sqrpc.getDiskUsageForOTDBId(spec.otdb_id,
                                                             include_scratch_paths=True,
                                                             force_update=True)

                if du_result['found'] and du_result.get('disk_usage', 0) > 0:
                    logger.info("removing data on disk from previous run for otdb_id %s", otdb_id)
                    result = self.curpc.removeTaskData(spec.otdb_id)
                    if not result['deleted']:
                        logger.warning("could not remove all data on disk from previous run for otdb_id %s: %s",
                                       otdb_id, result['message'])
            except Exception as e:
                # in line with failure as warning just above: allow going to scheduled state here too
                logger.error("Exception in cleaning up earlier data: %s", str(e))

