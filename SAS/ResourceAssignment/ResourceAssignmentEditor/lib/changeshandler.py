#!/usr/bin/env python3

# ChangesHandler.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: $

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.resourceassignment.database.radbbuslistener import RADBEventMessageBusListener, RADBEventMessageHandler
from lofar.sas.datamanagement.common.datamanagementbuslistener import DataManagementBusListener, DataManagementEventMessageHandler
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler
from lofar.lta.ingest.client.ingestbuslistener import IngestEventMesssageBusListener, IngestEventMessageHandler

from lofar.common.util import humanreadablesize
from lofar.common.util import waitForInterrupt
from lofar.sas.resourceassignment.resourceassignmenteditor.mom import updateTaskMomDetails

import logging
from datetime import datetime, timedelta
from threading import Lock, Condition

logger = logging.getLogger(__name__)

CHANGE_UPDATE_TYPE = 'update'
CHANGE_INSERT_TYPE = 'insert'
CHANGE_DELETE_TYPE = 'delete'

#special event type for events like 'deleted data from disk', 'status changed', etc
CHANGE_EVENT_TYPE = 'event'

class ChangesHandler:
    class _OTDBEventMessageHandler(OTDBEventMessageHandler):
        def __init__(self, changes_handler):
            self._changes_handler = changes_handler
            super().__init__()

        def onObservationStatusChanged(self, otdb_id, new_status, modificationTime):
            task = self._changes_handler._radbrpc.getTask(otdb_id=otdb_id)
            task_type = task.get('type', 'task') if task else 'task'
            message = 'Status of %s otdb_id %s changed to %s' % (task_type, otdb_id, new_status)
            change = {'changeType':CHANGE_EVENT_TYPE, 'objectType':'logevent', 'value':message}
            self._changes_handler._handleChange(change)

    class _RADBEventMessageHandler(RADBEventMessageHandler):
        def __init__(self, changes_handler):
            self._changes_handler = changes_handler
            super().__init__()

        def onTaskUpdated(self, updated_task):
            self._changes_handler.onTaskUpdated(updated_task)

        def onTaskInserted(self, updated_task):
            self._changes_handler.onTaskInserted(updated_task)

        def onTaskDeleted(self, updated_task):
            self._changes_handler.onTaskDeleted(updated_task)

        def onResourceClaimUpdated(self, updated_task):
            self._changes_handler.onResourceClaimUpdated(updated_task)

        def onResourceClaimInserted(self, updated_task):
            self._changes_handler.onResourceClaimInserted(updated_task)

        def onResourceClaimDeleted(self, updated_task):
            self._changes_handler.onResourceClaimDeleted(updated_task)

        def onResourceAvailabilityUpdated(self, updated_task):
            self._changes_handler.onResourceAvailabilityUpdated(updated_task)

        def onResourceCapacityUpdated(self, updated_task):
            self._changes_handler.onResourceCapacityUpdated(updated_task)

    class _DataManagementEventMessageHandler(DataManagementEventMessageHandler):
        def __init__(self, changes_handler):
            self._changes_handler = changes_handler
            super().__init__()

        def onTaskDeleting(self, otdb_id):
            self._changes_handler.onTaskDataDeletingFromDisk(otdb_id)

        def onTaskDeleted(self, otdb_id, deleted, paths, message=''):
            self._changes_handler.onTaskDataDeletedFromDisk(otdb_id, deleted, paths, message)

        def onTaskDataPinned(self, otdb_id, pinned):
            self._changes_handler.onTaskDataPinned(otdb_id, pinned)

        def onDiskUsageChanged(self, path, disk_usage, otdb_id=None):
            self._changes_handler.onDiskUsageChanged(path, disk_usage, otdb_id)

    class _IngestEventMessageHandler(IngestEventMessageHandler):
        def __init__(self, changes_handler):
            self._changes_handler = changes_handler
            super().__init__(log_subject_filters="TaskFinished")

        def onTaskFinished(self, ingest_task_dict):
            self._changes_handler.onIngestTaskFinished(ingest_task_dict)


    def __init__(self, busname=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER, momqueryrpc=None, radbrpc=None, sqrpc=None, **kwargs):
        """
        ChangesHandler listens on the lofar notification message bus and keeps track of all the change notifications.
        :param broker: valid Qpid broker host (default: None, which means localhost)
        additional parameters in kwargs:
            options=   <dict>  Dictionary of options passed to QPID
            exclusive= <bool>  Create an exclusive binding so no other services can consume duplicate messages (default: False)
            numthreads= <int>  Number of parallel threads processing messages (default: 1)
            verbose=   <bool>  Output extra logging over stdout (default: False)
        """
        self._otdb_listener = OTDBBusListener(ChangesHandler._OTDBEventMessageHandler,
                                              {'changes_handler': self},
                                              exchange=busname, broker=broker)

        self._radb_listener = RADBEventMessageBusListener(ChangesHandler._RADBEventMessageHandler,
                                                          {'changes_handler': self},
                                                          exchange=busname, broker=broker)


        self._dm_listener = DataManagementBusListener(ChangesHandler._DataManagementEventMessageHandler,
                                                      {'changes_handler': self},
                                                      exchange=busname, broker=broker)

        self._ingest_listener = IngestEventMesssageBusListener(ChangesHandler._IngestEventMessageHandler,
                                                               {'changes_handler': self},
                                                               exchange=busname, broker=broker)

        self._changes = []
        self._lock = Lock()
        self._changedCondition = Condition()
        self._changeNumber = 0
        self._momqueryrpc = momqueryrpc
        self._radbrpc = radbrpc
        self._sqrpc = sqrpc

    def __enter__(self):
        self.start_listening()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_listening()

    def start_listening(self):
        self._radb_listener.start_listening()
        self._dm_listener.start_listening()
        self._otdb_listener.start_listening()
        self._ingest_listener.start_listening()

    def stop_listening(self):
        self._radb_listener.stop_listening()
        self._dm_listener.stop_listening()
        self._otdb_listener.stop_listening()
        self._ingest_listener.stop_listening()

    def _handleChange(self, change):
        '''_handleChange appends a change in the changes list and calls the onChangedCallback.
        :param change: dictionary with the change'''
        with self._lock:
            change['timestamp'] = datetime.utcnow()
            self._changeNumber += 1
            change['changeNumber'] = self._changeNumber
            self._changes.append(change)

        self.clearChangesBefore(datetime.utcnow()-timedelta(minutes=5), datetime.utcnow()-timedelta(hours=6))

        with self._changedCondition:
            self._changedCondition.notifyAll()

    def onTaskUpdated(self, updated_task):
        '''onTaskUpdated is called upon receiving a TaskUpdated message.'''
        task_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'task', 'value':updated_task}
        self._handleChange(task_change)

    def onTaskInserted(self, new_task):
        '''onTaskInserted is called upon receiving a TaskInserted message.
        :param new_task: dictionary with the inserted task'''
        updateTaskMomDetails(new_task, self._momqueryrpc)
        task_change = {'changeType':CHANGE_INSERT_TYPE, 'objectType':'task', 'value':new_task}
        self._handleChange(task_change)

    def onTaskDeleted(self, old_task_id):
        '''onTaskDeleted is called upon receiving a TaskDeleted message.
        :param old_task_id: id of the deleted task'''
        task_change = {'changeType':CHANGE_DELETE_TYPE, 'objectType':'task', 'value':{'id':old_task_id}}
        self._handleChange(task_change)

    def onResourceClaimUpdated(self, updated_claim):
        '''onResourceClaimUpdated is called upon receiving a ResourceClaimUpdated message.
        :param updated_claim: dictionary with the updated claim'''
        claim_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'resourceClaim', 'value':updated_claim}
        self._handleChange(claim_change)

    def onResourceClaimInserted(self, new_claim):
        '''onResourceClaimInserted is called upon receiving a ResourceClaimInserted message.
        :param new_claim: dictionary with the inserted claim'''
        claim_change = {'changeType':CHANGE_INSERT_TYPE, 'objectType':'resourceClaim', 'value':new_claim}
        self._handleChange(claim_change)

    def onResourceClaimDeleted(self, old_claim_id):
        '''onResourceClaimDeleted is called upon receiving a ResourceClaimDeleted message.
        :param old_claim_id: id of the deleted claim'''
        claim_change = {'changeType':CHANGE_DELETE_TYPE, 'objectType':'resourceClaim', 'value':{'id': old_claim_id}}
        self._handleChange(claim_change)

    def onResourceAvailabilityUpdated(self, old_availability, updated_availability):
        claim_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'resourceAvailability', 'value':updated_availability}
        self._handleChange(claim_change)

    def onResourceCapacityUpdated(self, old_capacity, updated_capacity):
        claim_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'resourceCapacity', 'value':updated_capacity}
        self._handleChange(claim_change)

    def _handleDiskUsageChange(self, disk_usage, otdb_id):
        if otdb_id != None:
            task = self._radbrpc.getTask(otdb_id=otdb_id)
            if task:
                du_readable = humanreadablesize(disk_usage)
                logger.info('disk_usage change: otdb_id %s radb_id %s disk_usage %s %s', otdb_id, task['id'], disk_usage, du_readable)
                task['disk_usage'] = disk_usage
                task['disk_usage_readable'] = du_readable

                task_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'task', 'value':task}
                self._handleChange(task_change)

    def onDiskUsageChanged(self, path, disk_usage, otdb_id):
        self._handleDiskUsageChange(disk_usage, otdb_id)

    def onTaskDataDeletingFromDisk(self, otdb_id):
        task = self._radbrpc.getTask(otdb_id=otdb_id)
        task_type = task.get('type', 'task') if task else 'task'
        message = 'Deleting data from disk for %s with otdb_id %s ...' % (task_type, otdb_id)
        change = {'changeType':CHANGE_EVENT_TYPE, 'objectType':'logevent', 'value':message}
        self._handleChange(change)

    def onTaskDataDeletedFromDisk(self, otdb_id, deleted, paths, message=''):
        #get new actual disk_usage
        disk_usage_result = self._sqrpc.getDiskUsageForOTDBId(otdb_id, include_scratch_paths=True, force_update=True)
        disk_usage = disk_usage_result['disk_usage'] if disk_usage_result['found'] else 0
        self._handleDiskUsageChange(disk_usage, otdb_id)

        change = {'changeType':CHANGE_EVENT_TYPE, 'objectType':'logevent', 'value':message}
        self._handleChange(change)

    def onTaskDataPinned(self, otdb_id, pinned):
        updated_task = self._radbrpc.getTask(otdb_id=otdb_id)
        updated_task['data_pinned'] = pinned
        task_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'task', 'value':updated_task}
        self._handleChange(task_change)

    def onIngestTaskFinished(self, ingest_task_dict):
        if 'otdb_id' not in ingest_task_dict:
            return

        otdb_id = ingest_task_dict['otdb_id']
        updated_task = self._radbrpc.getTask(otdb_id=otdb_id)
        if not updated_task:
            return

        updated_task['ingest_status'] = 'ingested'
        task_change = {'changeType':CHANGE_UPDATE_TYPE, 'objectType':'task', 'value':updated_task}
        self._handleChange(task_change)

        task_type = updated_task.get('type', 'task')
        message = 'Data for %s with otdb_id %s has been ingested to the LTA' % (task_type, otdb_id)
        change = {'changeType':CHANGE_EVENT_TYPE, 'objectType':'logevent', 'value':message}
        self._handleChange(change)

    def getEventsSince(self, since_timestamp):
        with self._lock:
            return [x for x in self._changes if x['changeType'] == CHANGE_EVENT_TYPE and x['timestamp'] >= since_timestamp]

    def getMostRecentChangeNumber(self):
        with self._lock:
            if self._changes:
                return self._changes[-1]['changeNumber']
        return -1

    def clearChangesBefore(self, min_timestamp_for_changes, min_timestamp_for_logevents):
        with self._lock:
            self._changes = [x for x in self._changes
                             if ((x['changeType'] == CHANGE_EVENT_TYPE and x['timestamp'] >= min_timestamp_for_logevents) or
                                 (x['changeType'] != CHANGE_EVENT_TYPE and x['timestamp'] >= min_timestamp_for_changes))]

    def getChangesSince(self, changeNumber):
        with self._changedCondition:
            while True:
                with self._lock:
                    changesSince = [x for x in self._changes if x['changeNumber'] > changeNumber]

                    if changesSince:
                        return changesSince

                self._changedCondition.wait()
