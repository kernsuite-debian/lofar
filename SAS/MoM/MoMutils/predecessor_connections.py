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
'''
import logging
logger=logging.getLogger(__file__)

from time import sleep
from datetime import datetime, timedelta
from optparse import OptionParser

from lofar.common import dbcredentials
from lofar.mom.simpleapis.momhttpclient import SystemMoMClient
from lofar.mom.simpleapis.momdbclient import MoMDatabaseWrapper


def fix_predecessor_connection_if_needed(mom_id: int, dbcreds: dbcredentials.DBCredentials = None):
    '''
    check the predecessor topology string of the mom object given by mom_id, and fix it if needed.
    :param mom_id: a mom2id of a mom object
    :param dbcreds: the db credentials of the MoM database, defaults to 'MoM' credentials in ~/.lofar/dbcredentials.
    '''

    # little helper function to set the mom status via http (which is asynchronous)
    # and which then waits for the status to be as set.
    def setAndWaitForMomStatus(status):
        with SystemMoMClient() as momhttp:
            start_wait = datetime.utcnow()
            momhttp.setPipelineStatus(mom_id, status)
            object = momdb.getObjectDetails(mom_id)[mom_id]
            while object['object_status'] != status and object['object_status_pending']:
                logger.info('waiting for %s status change to %s. current status=%s pending=%s',
                            mom_id, status, object['object_status'], object['object_status_pending'])
                if datetime.utcnow() - start_wait > timedelta(seconds=60):
                    raise TimeoutError("Timeout while waiting for mom_id=%s to get '%s' status" % (mom_id, status))
                sleep(0.5)

    with MoMDatabaseWrapper(dbcreds) as momdb:
        object = momdb.getObjectDetails(mom_id)[mom_id]
        object_predecessor_string = object.get('object_predecessor_string') or ''
        object_predecessor_string_parts = [x.strip() for x in object_predecessor_string.split(',')]

        logger.info("checking mom_id=%s status=%s name=%s predecessors=%s group_id=%s group_name=%s",
                     mom_id, object['object_status'], object['object_name'], object_predecessor_string,
                     object['object_group_id'], object['object_group_name'])

        if len(object_predecessor_string_parts) == 0:
            logger.info("mom_id=%s name=%s has no predecessors", mom_id, object['object_name'])
            return

        unconnected_object_predecessor_string_parts = [p for p in object_predecessor_string_parts if not p.startswith('M')]
        if len(unconnected_object_predecessor_string_parts) == 0:
            logger.info("all predecessors of mom_id=%s status=%s name=%s predecessors=%s group_id=%s group_name=%s have a proper mom id",
                        mom_id, object['object_status'], object['object_name'], object_predecessor_string,
                        object['object_group_id'], object['object_group_name'])

            if object['object_status'] == 'opened':
                # trigger MoM-server status change handling, which actually connects the object to its predecessors
                setAndWaitForMomStatus('approved')
            return

        group_id = object['object_group_id']
        group_tasks = momdb.getObjectDetailsOfObservationsAndPipelinesInGroup(group_id)
        if len(group_tasks) == 0:
            logger.warning("there are no other tasks in group %s %s that %s could connect to", group_id, object['object_group_name'], mom_id)
            return

        if object['object_status'] not in ['opened', 'approved', 'prescheduled', 'scheduled']:
            logger.warning("Cannot connect object %s to its predecessors because its status is '%s'. predecessors: %s\nobject: %s",
                           mom_id, object['object_status'], object_predecessor_string, object)
            return

        # magic MoM-business-logic-like string parsing...
        # MoM specs encode precesessors with so called 'topology' strings (or comma seperated strings for multiple predecessors)
        # these topology strings are translated in mom2id's (prefixed with an M)
        # Find unconnected_predecessors based on these topologies.
        topopolgy_group_prefix = 'mom.G%d.' % (object['object_group_id'])
        unconnected_object_predecessor_topologies = ["%s%s" % (topopolgy_group_prefix, p) for p in unconnected_object_predecessor_string_parts]
        unconnected_predecessors = [t for t in group_tasks if t['object_topology'] in  unconnected_object_predecessor_topologies]

        if len(unconnected_predecessors) != len(unconnected_object_predecessor_string_parts):
            logger.warning("could not find all unconnected predecessors for %s in group %s", mom_id, group_id)

        if len(unconnected_predecessors):
            if object['object_status'] != 'opened':
                # make sure the status is opened
                setAndWaitForMomStatus('opened')
                object = momdb.getObjectDetails(mom_id)[mom_id]

            # connect each known predecessor
            for unconnected_predecessor in unconnected_predecessors:
                momdb.connect_to_predecessor(mom_id, unconnected_predecessor['object_mom2id'])

        if object['object_status'] == 'opened':
            # trigger MoM-server status change handling, which actually connects the object to its predecessors
            setAndWaitForMomStatus('approved')

def fix_predecessor_connections_in_group_if_needed(mom_group_id: int, dbcreds: dbcredentials.DBCredentials = None):
    '''
    check all the predecessor topology strings of all mom objects in the group given by mom_group_id, and fix them if needed.
    :param mom_group_id: a mom2id of a mom group object
    :param dbcreds: the db credentials of the MoM database, defaults to 'MoM' credentials in ~/.lofar/dbcredentials.
    '''
    with MoMDatabaseWrapper(dbcreds=dbcreds) as momdb:
        # first, let's see if the lobos_group_id is for a folder of of sub-folders...
        groups = momdb.getGroupsInGroup(mom_group_id)

        if len(groups) == 0:
            # not a folder of subfolders, so treat the given lobos_group_id as if its one of the subfolders...
            groups = momdb.getObjectDetails(mom_group_id).values()

        groups = sorted(groups, key=lambda g: g['object_mom2id'])

        logger.info("checking and fixing the following groups: %s",
                    ", ".join("%s %s" % (g['object_mom2id'], g['object_name']) for g in groups))

        for group in groups:
            group_id = group['object_mom2id']
            group_tasks = momdb.getObjectDetailsOfObservationsAndPipelinesInGroup(group_id)
            group_tasks = sorted(group_tasks, key=lambda t: t['object_mom2id'])

            logger.info("checking and fixing the following tasks in group %s %s: %s",
                        group['object_mom2id'], group['object_name'],
                        ", ".join("%s %s" % (t['object_mom2id'], t['object_name']) for t in group_tasks))

            for task in group_tasks:
                try:
                    if 'pipeline' in task['object_type'].lower():
                        fix_predecessor_connection_if_needed(task['object_mom2id'], dbcreds=dbcreds)
                except Exception as e:
                    logger.error(e)

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser('%prog <mom_id_of_LOBOS_group>', description='fix loose connections (unprocessed predecessor topologies) in the given LOBOS group and approved them.')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="MoM")
    (options, args) = parser.parse_args()

    dbcreds = dbcredentials.parse_options(options)
    print()
    print("Using dbcreds:", dbcreds.stringWithHiddenPassword())
    print("Using mom url:", SystemMoMClient().mom_base_url)
    print()

    if len(args) == 0:
        parser.print_help()
        exit()

    group_id = int(args[0])

    if input("Proceed with checking and fixing %s ? y/<n>: " % (group_id,)) == 'y':
        fix_predecessor_connections_in_group_if_needed(group_id, dbcreds)
    else:
        print("exiting...")

if __name__ == '__main__':
    main()
