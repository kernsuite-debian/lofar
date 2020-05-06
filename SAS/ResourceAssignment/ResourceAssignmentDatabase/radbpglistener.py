#!/usr/bin/env python3

# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id: radb.py 33394 2016-01-25 15:53:55Z schaap $

'''
TODO: documentation
'''
import logging
import psycopg2
import psycopg2.extras
from datetime import datetime
import time
import json
from optparse import OptionParser

from lofar.common.postgres import PostgresListener
from lofar.messaging import EventMessage, ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.database.config import DEFAULT_RADB_NOTIFICATION_PREFIX
from lofar.common import dbcredentials

from lofar.sas.resourceassignment.database.radb import RADatabase

logger = logging.getLogger(__name__)

class RADBPGListener(PostgresListener):
    def __init__(self,
                 exchange=DEFAULT_BUSNAME,
                 dbcreds=None,
                 broker=DEFAULT_BROKER):
        super(RADBPGListener, self).__init__(dbcreds=dbcreds)

        self.event_bus = ToBus(exchange=exchange, broker=broker)

        self.radb = RADatabase(dbcreds=dbcreds)

        self.subscribe('task_update', self.onTaskUpdated)
        self.subscribe('task_insert', self.onTaskInserted)
        self.subscribe('task_delete', self.onTaskDeleted)

        self.subscribe('task_predecessor_insert_column_task_id', self.onTaskPredecessorChanged)
        self.subscribe('task_predecessor_update_column_task_id', self.onTaskPredecessorChanged)
        self.subscribe('task_predecessor_delete_column_task_id', self.onTaskPredecessorChanged)

        self.subscribe('task_predecessor_insert_column_predecessor_id', self.onTaskSuccessorChanged)
        self.subscribe('task_predecessor_update_column_predecessor_id', self.onTaskSuccessorChanged)
        self.subscribe('task_predecessor_delete_column_predecessor_id', self.onTaskSuccessorChanged)

        # when the specification starttime and endtime are updated, then that effects the task as well
        self.subscribe('specification_update', self.onSpecificationUpdated)

        self.subscribe('resource_claim_update', self.onResourceClaimUpdated)
        self.subscribe('resource_claim_insert', self.onResourceClaimInserted)
        self.subscribe('resource_claim_delete', self.onResourceClaimDeleted)

        self.subscribe('resource_availability_update', self.onResourceAvailabilityUpdated)
        self.subscribe('resource_capacity_update', self.onResourceCapacityUpdated)

    def onTaskUpdated(self, payload = None):
        # Send notification for the given updated task
        task_id = payload        
        task = self.radb.getTask(task_id)
        self._sendNotification('TaskUpdated', task)

        # The "blocked_by_ids" property of the given task's successors might have been updated due to the given task 
        # status being updated. Therefore also send a notification for these successors - lazily ignoring that they 
        # might not have changed.
        suc_sched_tasks = self.radb.getTasks(task_ids=task['successor_ids'], task_status='scheduled')
        for suc_sched_task in suc_sched_tasks:
            self._sendNotification('TaskUpdated', suc_sched_task)

    def onTaskInserted(self, payload = None):
        self._sendNotification('TaskInserted', self.radb.getTask(payload))

    def onTaskDeleted(self, payload = None):
        self._sendNotification('TaskDeleted', payload)

    def onTaskPredecessorChanged(self, task_id):
        logger.info('onTaskPredecessorChanged(task_id=%s)', task_id)
        self._sendNotification('TaskUpdated', self.radb.getTask(task_id))

    def onTaskSuccessorChanged(self, task_id):
        logger.info('onTaskSuccessorChanged(task_id=%s)', task_id)
        self._sendNotification('TaskUpdated', self.radb.getTask(task_id))

    def onSpecificationUpdated(self, payload = None):
        # when the specification starttime and endtime are updated, then that effects the task as well
        self._sendNotification('TaskUpdated', self.radb.getTask(specification_id=payload))

    def onResourceClaimUpdated(self, payload = None):
        self._sendNotification('ResourceClaimUpdated', self.radb.getResourceClaim(payload))

    def onResourceClaimInserted(self, payload = None):
        self._sendNotification('ResourceClaimInserted', self.radb.getResourceClaim(payload))

    def onResourceClaimDeleted(self, payload = None):
        self._sendNotification('ResourceClaimDeleted', payload)

    def onResourceAvailabilityUpdated(self, payload = None):
        r = self.radb.getResources(resource_ids=[payload], include_availability=True)[0]
        r = {k:r[k] for k in ['id', 'active']}
        self._sendNotification('ResourceAvailabilityUpdated', r)

    def onResourceCapacityUpdated(self, payload = None):
        r = self.radb.getResources(resource_ids=[payload], include_availability=True)[0]
        r = {k:r[k] for k in ['id', 'total_capacity', 'available_capacity', 'used_capacity']}
        self._sendNotification('ResourceCapacityUpdated', r)

    def __enter__(self):
        super(RADBPGListener, self).__enter__()
        self.radb.connect()
        self.event_bus.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RADBPGListener, self).__exit__(exc_type, exc_val, exc_tb)
        self.radb.disconnect()
        self.event_bus.close()

    def _formatTimestampsAsIso(self, fields, contentDict):
        '''convert all requested fields in the contentDict to proper isoformat datetime strings.
        In postgres we use timestamps without timezone.
        By convention we only enter utc values.
        But, if they are json encoded by postgress, they are not properly formatted with the in isoformat with a 'Z' at the end.
        So, parse the requested fields, and return them as datetime.
        '''
        try:
            for field in fields:
                try:
                    if field in contentDict:
                        timestampStr = contentDict[field]
                        formatStr = '%Y-%m-%dT%H:%M:%S' if 'T' in timestampStr else '%Y-%m-%d %H:%M:%S'
                        if timestampStr.rfind('.') > -1:
                            formatStr += '.%f'

                        timestamp = datetime.strptime(timestampStr, formatStr)

                        contentDict[field] = timestamp
                except Exception as e:
                    logger.error('Could not convert field \'%s\' to datetime: %s' % (field, e))

            return contentDict
        except Exception as e:
            logger.error('Error while convering timestamp fields \'%s\'in %s\n%s' % (fields, contentDict, e))

    def _sendNotification(self, subject, contentDict):
        try:
            if subject and contentDict:
                msg = EventMessage(subject="%s.%s" % (DEFAULT_RADB_NOTIFICATION_PREFIX, subject), content=contentDict)
                logger.info('Sending notification %s to %s: %s', subject, self.event_bus.exchange, str(contentDict).replace('\n', ' '))
                self.event_bus.send(msg)
        except Exception as e:
            logger.error(str(e))

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the radb postgres listener which listens to changes on some tables in the radb and publishes the changes as notifications on the bus.')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the broker, [default: %default]")

    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    dbcreds = dbcredentials.parse_options(options)

    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    with RADBPGListener(exchange=options.exchange,
                        dbcreds=dbcreds,
                        broker=options.broker) as listener:
        listener.waitWhileListening()

if __name__ == '__main__':
    main()
