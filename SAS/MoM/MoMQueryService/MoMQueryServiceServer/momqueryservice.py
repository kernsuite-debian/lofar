#!/usr/bin/env python3

# Copyright (C) 2017    ASTRON (Netherlands Institute for Radio Astronomy)
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

'''
Simple Service listening on momqueryservice.GetObjectDetails
which gives the project details for each requested mom object id

Example usage:
service side: just run this service somewhere where it can access the momdb and
a qpid broker.
Make sure the bus exists: qpid-config add exchange topic <busname>

client side: do a RPC call to the <busname>.GetObjectDetails with a
comma seperated string of mom2object id's as argument.
You get a dict of mom2id to project-details-dict back.

with RPC(busname, 'GetObjectDetails') as getObjectDetails:
    res, status = getObjectDetails(ids_string)

'''
import logging
from datetime import timedelta
from optparse import OptionParser
from mysql import connector
from mysql.connector.errors import OperationalError
import json

from lofar.messaging import ServiceMessageHandler, RPCService, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import waitForInterrupt
from lofar.mom.momqueryservice.config import DEFAULT_MOMQUERY_SERVICENAME
from lofar.common import dbcredentials
from lofar.mom.simpleapis.momdbclient import MoMDatabaseWrapper

logger=logging.getLogger(__file__)


class MoMQueryServiceMessageHandler(ServiceMessageHandler):
    """
    handler class for details query in mom db
    :param MoMDatabaseWrapper momdb inject database access via wrapper
    """
    def __init__(self, dbcreds):
        super(MoMQueryServiceMessageHandler, self).__init__()
        self.dbcreds = dbcreds

    def start_handling(self):
        self.momdb = MoMDatabaseWrapper(self.dbcreds)
        self.momdb.connect()
        super(MoMQueryServiceMessageHandler, self).start_handling()

    def stop_handling(self):
        self.momdb.disconnect()
        super(MoMQueryServiceMessageHandler, self).stop_handling()

    def add_trigger(self, user_name, host_name, project_name, meta_data):
        row_id = self.momdb.add_trigger(user_name, host_name, project_name, meta_data)
        self.momdb.update_trigger_quota(project_name)
        return {"row_id": row_id}

    def get_project_priority(self, project_name):
        priority = self.momdb.get_project_priority(project_name)
        return {"priority": priority}

    def allows_triggers(self, project_name):
        allows = self.momdb.allows_triggers(project_name)
        return {"allows": allows}

    def authorized_add_with_status(self, user_name, project_name, job_type, status):
        authorized = self.momdb.authorized_add_with_status(user_name, project_name, job_type, status)
        return {"authorized": authorized}

    def folder_exists(self, folder):
        exists = self.momdb.folder_exists(folder)
        return {"exists": exists}

    def is_project_active(self, project_name):
        is_active = self.momdb.is_project_active(project_name)
        return {"active": is_active}

    def is_user_operator(self, user_name):
        is_operator = self.momdb.is_user_operator(user_name)
        return {'is_operator': is_operator}

    def get_triggers(self, user_name):
        triggers = self.momdb.get_triggers(user_name)
        return {'triggers': triggers}

    def get_trigger_spec(self, user_name, trigger_id):
        trigger_spec =  self.momdb.get_trigger_spec(user_name, trigger_id)
        return {'trigger_spec': trigger_spec}

    def get_trigger_id(self, mom_id):
        trigger_id = self.momdb.get_trigger_id(mom_id)

        if trigger_id:
            return {'trigger_id': trigger_id, "status": "OK"}
        else:
            return {"trigger_id": None, "status": "Error",
                    "errors": ["No trigger_id for mom_id: " + str(mom_id)]}

    def update_trigger_quota(self, project_name):
        self.momdb.update_trigger_quota(project_name)
        current, max = self.momdb.get_trigger_quota(project_name)
        return {"used_triggers": current, "allocated_triggers": max}

    def get_trigger_quota(self, project_name):
        quota = self.momdb.get_trigger_quota(project_name)
        current, max = quota
        return {"used_triggers": current, "allocated_triggers": max}

    def cancel_trigger(self, trigger_id, reason):
        self.momdb.cancel_trigger(trigger_id, reason)
        project_name = self.momdb.get_projectname_for_trigger(trigger_id)
        self.momdb.update_trigger_quota(project_name)
        current, max = self.momdb.get_trigger_quota(project_name)
        return {"used_triggers": current, "allocated_triggers": max}

    def get_project_details(self, mom_id):
        return self.momdb.get_project_details(mom_id)

    def get_project_priorities_for_objects(self, mom_ids):
        return self.momdb.get_project_priorities_for_objects(mom_ids)

    def getObjectDetails(self, mom_ids):
        return self.momdb.getObjectDetails(mom_ids)

    def getProjects(self):
        return self.momdb.getProjects()

    def getProjectTaskIds(self, project_mom2id):
        return self.momdb.getProjectTaskIds(project_mom2id)

    def getProject(self, project_mom2id):
        return self.momdb.getProject(project_mom2id)

    def getPredecessorIds(self, mom_ids):
        return self.momdb.getPredecessorIds(mom_ids)

    def getSuccessorIds(self, mom_ids):
        return self.momdb.getSuccessorIds(mom_ids)

    def getTaskIdsInGroup(self, mom_group_ids):
        return self.momdb.getTaskIdsInGroup(mom_group_ids)

    def getTaskIdsInParentGroup(self, mom_parent_group_ids):
        return self.momdb.getTaskIdsInParentGroup(mom_parent_group_ids)

    def getDataProducts(self, mom_ids):
        return self.momdb.getDataProducts(mom_ids)

    def getMoMIdsForOTDBIds(self, otdb_ids):
        return self.momdb.getMoMIdsForOTDBIds(otdb_ids)

    def getOTDBIdsForMoMIds(self, mom_ids):
        return self.momdb.getOTDBIdsForMoMIds(mom_ids)

    def getTaskIdsGraph(self, mom2id):
        return self.momdb.getTaskIdsGraph(mom2id)

    def get_trigger_time_restrictions(self, mom_id):
        return self.momdb.get_trigger_time_restrictions(mom_id)

    def get_station_selection(self, mom_id):
        return self.momdb.get_station_selection(mom_id)

    def get_storagemanager(self, mom_id):
        return self.momdb.get_storagemanager(mom_id)


def main():
    """
    Starts the momqueryservice.GetObjectDetails service
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the momqueryservice')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the broker, [default: %default]")
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="MoM")
    (options, args) = parser.parse_args()

    dbcreds = dbcredentials.parse_options(options)

    logger.info("Using dbcreds: %s", dbcreds.stringWithHiddenPassword())

    with RPCService(service_name=DEFAULT_MOMQUERY_SERVICENAME,
                    handler_type=MoMQueryServiceMessageHandler, handler_kwargs={'dbcreds': dbcreds},
                    broker=options.broker, exchange=options.exchange,
                    num_threads=6):
        waitForInterrupt()

if __name__ == '__main__':
    main()
