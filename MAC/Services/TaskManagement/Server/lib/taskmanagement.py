#!/usr/bin/env python3

# Copyright (C) 2017 ASTRON (Netherlands Institute for Radio Astronomy)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
# $Id$

"""
TaskManagement
"""

import logging

from lofar.mac.services.taskmanagement.common.config import DEFAULT_SERVICENAME
from lofar.messaging import ServiceMessageHandler, RPCService, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.otdb.otdbrpc import OTDBRPC, OTDBPRCException
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.mac.observation_control_rpc import ObservationControlRPCClient

logger = logging.getLogger(__name__)


class TaskManagementHandler(ServiceMessageHandler):
    def handle_message(self, msg):
        pass

    def __init__(self):
        super(TaskManagementHandler, self).__init__()

        self.radb = RADBRPC()
        self.otdb = OTDBRPC()
        self.obs_ctrl = ObservationControlRPCClient()

    def AbortTask(self, otdb_id):
        """aborts tasks based on otdb id
        :param otdb_id:
        :return: dict with aborted key saying if aborting was succesful and otdb_id key
        """
        if self._is_active_observation(otdb_id):
            aborted = self._abort_active_observation(otdb_id)
        else:
            aborted = self._abort_inactive_task(otdb_id)

        return {"aborted": aborted, "otdb_id": otdb_id}

    def _is_active_observation(self, otdb_id):
        task_type, task_status = self._get_task_type_and_status(otdb_id)

        return task_type == "observation" and (task_status == "running" or task_status == "queued")

    def _abort_inactive_task(self, otdb_id):
        logger.info("Aborting inactive task: %s", otdb_id)

        try:
            self.otdb.taskSetStatus(otdb_id=otdb_id, new_status="aborted")
            aborted = True
        except OTDBPRCException:
            aborted = False
        return aborted

    def _abort_active_observation(self, otdb_id):
        logger.info("Aborting active task: %s", otdb_id)

        result = self.obs_ctrl.abort_observation(otdb_id)
        aborted = result["aborted"] is True
        return aborted

    def _get_task_type_and_status(self, otdb_id):
        task = self.radb.getTask(otdb_id)
        task_type = task["type"]
        task_status = task['status']
        return task_type, task_status


def createService(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
    return RPCService(service_name=DEFAULT_SERVICENAME,
                   handler_type=TaskManagementHandler,
                   exchange=exchange,
                   broker=broker,
                   num_threads=1)


def main():
    from optparse import OptionParser
    from lofar.common.util import waitForInterrupt

    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the resourceassignment database service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the qpid broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the qpid broker, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true',
                      help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with createService(exchange=options.exchange, broker=options.broker):
        waitForInterrupt()


if __name__ == '__main__':
    main()
