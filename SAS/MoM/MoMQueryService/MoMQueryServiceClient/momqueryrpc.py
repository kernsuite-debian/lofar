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

import sys
import logging
import pprint
from optparse import OptionParser
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.mom.momqueryservice.config import DEFAULT_MOMQUERY_SERVICENAME

''' Simple RPC client for Service momqueryservice
'''

logger = logging.getLogger(__name__)


class MoMQueryRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the MoMQueryRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_MOMQUERY_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_MOMQUERY_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_RPC_TIMEOUT):
        """Create a MoMQueryRPC connecting to the given exchange/broker on the default DEFAULT_MOMQUERY_SERVICENAME service"""
        return MoMQueryRPC(RPCClient(service_name=DEFAULT_MOMQUERY_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def add_trigger(self, user_name, host_name, project_name, meta_data):
        logger.info("Requestion add_trigger for user_name: %s, host_name: %s, project_name: %s and "
                    "meta_data: %s", user_name, host_name, project_name, meta_data)

        row_id = self._rpc_client.execute('add_trigger', user_name=user_name, host_name=host_name,
                                          project_name=project_name, meta_data=meta_data)

        logger.info("Received add_trigger for user_name (%s), host_name(%s), project_name(%s) and "
                    "meta_data(%s): %s",
                    user_name, host_name, project_name, meta_data, row_id)

        return row_id

    def get_project_priority(self, project_name):
        logger.info("Requestion get_project_priority for project_name: %s", project_name)

        priority = self._rpc_client.execute('get_project_priority', project_name=project_name)

        logger.info("Received get_project_priority for project_name (%s): %s", project_name,
                    priority)

        return priority

    def allows_triggers(self, project_name):
        """returns whether a project is allowed to submit triggers
        :param project_name:
        :return: Boolean
        """
        logger.info("Requesting allows_triggers for project_name: %s", project_name)

        result = self._rpc_client.execute('allows_triggers', project_name=project_name)

        logger.info("Received allows_triggers for project_name (%s): %s", project_name, result)

        return result

    def authorized_add_with_status(self, user_name, project_name, job_type, status):
        """returns whether user is allowed in project to move a certain jobtype to a certain state
        :param user_name:
        :param project_name:
        :param job_type:
        :param status:
        :return: Boolean
        """
        logger.info("Requesting authorized_add_with_status for user_name: %s project_name: %s "
                    "job_type: %s status: %s", user_name, project_name, job_type, status)
        result = self._rpc_client.execute('authorized_add_with_status', user_name=user_name,
                                          project_name=project_name, job_type=job_type, status=status)
        logger.info("Received authorized_add_with_status for user_name: %s project_name: %s "
                    "job_type: %s status: %s result: %s", user_name, project_name, job_type,
                    status, result)
        return result

    def folderExists(self, folder):
        """returns true if folder exists
        :param folder:
        :return: Boolean
        """
        logger.info("Requesting folder: %s exists", folder)
        result = self._rpc_client.execute('folder_exists', folder=folder)
        logger.info("Received folder exists: %s", result)
        return result

    def isProjectActive(self, project_name):
        """returns true if project is available and active
        :param project_name:
        :return: Boolean
        """
        logger.info("Requesting if project: %s is active", project_name)
        result = self._rpc_client.execute('is_project_active', project_name=project_name)
        logger.info("Received Project is active: %s", result)
        return result

    def isUserOperator(self, user_name):
        """returns true if a user has the operator role assigned
        :param user_name:
        :return: Boolean
        """
        logger.info("Requesting if user %s is an operator", user_name)
        result = self._rpc_client.execute('is_user_operator', user_name=user_name)
        logger.info("User %s is %san operator", user_name,
                    'not ' if result['is_operator'] is False else '')
        return result

    def get_triggers(self, user_name):
        """get all triggers for a user logged in as user_name.  If
        the user_name is empty (None), then all triggers will be
        returned.
        :param user_name:  string that contains the user's login name or None.
        :rtype dict with all triggers"""
        logger.info("Requesting triggers for user %s", user_name)
        triggers = self._rpc_client.execute('get_triggers', user_name=user_name)

        logger.info("Received %d triggers for user %s",
                    len(triggers), user_name)
        return triggers

    def get_trigger_spec(self, user_name, trigger_id):
        """get the trigger spec for a user logged in as user_name and
        tigger_id.  If the user_name is empty (None), then access will
        be granted to any trigger spec.
        :param user_name:  string that contains the user's login name or None.
        :param trigger_id: the trigger_id for which the spec needs to returned
        :rtype dict with all triggers"""
        logger.info("Requesting trigger spec for user %s and trigger id "
                    "%s", user_name, trigger_id)
        trigger_spec = self._rpc_client.execute('get_trigger_spec', user_name=user_name,
                                                trigger_id=trigger_id)

        logger.info("Received a trigger spec with size %d for trigger id "
                    "%s of user %s", len(trigger_spec['trigger_spec']), trigger_id,
                    user_name)
        return trigger_spec

    def get_trigger_id(self, mom_id):
        """returns trigger id if mom_id has a trigger else None
        :param mom_id:
        :return: Integer or None
        """
        logger.info("Requesting get_trigger_id for mom_id: %s", mom_id)
        result = self._rpc_client.execute('get_trigger_id', mom_id=mom_id)
        logger.info("Received get_trigger_id: %s", result)
        return result

    def get_trigger_quota(self, project_name):
        """returns trigger quota as (current,max) tuple for project with given name
        :param project_name
        :return: (Integer, Integer)
        """
        logger.info("Requesting get_trigger_quota for project: %s", project_name)
        result = self._rpc_client.execute('get_trigger_quota', project_name=project_name)
        logger.info("Received trigger quota: %s", result)
        return result

    def update_trigger_quota(self, project_name):
        """
        count all the accepted triggers that are not cancelled, and update the trigger quota field
        in mom accordingly returns updated quota as (current, max) tuple (same as get_trigger_quota)
        :param project_name
        :return: (Integer, Integer)
        """
        logger.info("Requesting update_trigger_quota for project: %s", project_name)
        result = self._rpc_client.execute('update_trigger_quota', project_name=project_name)
        logger.info("Received updated trigger quota: %s", result)
        return result

    def cancel_trigger(self, trigger_id, reason):
        """ flags trigger as canceled and returns updated trigger quota as (current, max) tuple
        :param trigger_id
        :param reason
        :return (Integer, Integer)
        """
        logger.info("Requesting cancel_trigger for trigger id: %s | reason: %s", trigger_id, reason)
        result = self._rpc_client.execute('cancel_trigger', trigger_id=trigger_id, reason=reason)
        logger.info("Requesting cancel_trigger for trigger id %s returned updated project trigger "
                    "quota: %s", trigger_id, result)
        return result

    def get_project_details(self, mom_id):
        """returns email addresses of pi and contact author for a project mom id
        :param mom_id
        :rtype dict with pi and contact author email addresses"""
        logger.info("Requesting get_project_details for mom_id: %s", mom_id)
        result = self._rpc_client.execute('get_project_details', mom_id=mom_id)
        logger.info("Received get_project_details: %s", result)
        return result

    def get_project_priorities_for_objects(self, mom_ids):
        """get the project priorities for one or more mom ids
        :param mom_ids single or list of mom ids
        :rtype dict with project priorities"""
        if isinstance(mom_ids, int) or isinstance(mom_ids, str):
            mom_ids = [mom_ids]
        mom_ids = [str(x) for x in mom_ids]
        ids_string = ', '.join(mom_ids)

        logger.info("Requesting project priorities for mom objects: %s", (str(ids_string)))
        result = self._rpc_client.execute('get_project_priorities_for_objects', mom_ids=ids_string)
        logger.info("Received project priorities for %s mom objects" % (len(result)))
        return result

    def getObjectDetails(self, ids):
        """get the object details for one or more mom ids
        :param ids single or list of mom ids
        :rtype dict with project details"""
        if ids is None:
            return {}

        if isinstance(ids, int) or isinstance(ids, str):
            ids = [ids]
        ids = [str(x) for x in ids]
        ids_string = ', '.join(ids)

        logger.debug("Requesting details for %s mom objects. mom_ids: %s", len(ids), ids_string)
        result = self._rpc_client.execute('getObjectDetails', mom_ids=ids_string)
        logger.debug("Received details for %s mom objects. mom_ids: %s", len(result), ids_string)
        return result

    def getProjects(self):
        """get all projects
        :rtype dict with all projects"""
        logger.info("Requesting all projects")
        projects = self._rpc_client.execute('getProjects')
        logger.info("Received %s projects", (len(projects)))
        return projects

    def getProject(self, project_mom2id):
        """get projects by mo2_id"""
        logger.info("getProject(%s)", project_mom2id)
        project = self._rpc_client.execute('getProject', project_mom2id=project_mom2id)
        return project

    def getProjectTaskIds(self, project_mom2id):
        """get all task mom2id's for the given project
        :rtype dict with all projects"""
        logger.info("getProjectTaskIds")
        task_ids = self._rpc_client.execute('getProjectTaskIds', project_mom2id=project_mom2id)
        return task_ids

    def getPredecessorIds(self, ids):
        logger.debug("getSuccessorIds(%s)", ids)
        result = self._rpc_client.execute('getPredecessorIds', mom_ids=ids)
        logger.info("getPredecessorIds(%s): %s", ids, result)
        return result

    def getSuccessorIds(self, ids):
        logger.debug("getSuccessorIds(%s)", ids)
        result = self._rpc_client.execute('getSuccessorIds', mom_ids=ids)
        logger.info("getSuccessorIds(%s): %s", ids, result)
        return result

    def getTaskIdsInGroup(self, mom_group_ids):
        logger.debug("getTaskIdsInGroup(%s)", mom_group_ids)
        result = self._rpc_client.execute('getTaskIdsInGroup', mom_group_ids=mom_group_ids)
        logger.info("getTaskIdsInGroup(%s): %s", mom_group_ids, result)
        return result

    def getTaskIdsInParentGroup(self, mom_parent_group_ids):
        logger.debug("getTaskIdsInParentGroup(%s)", mom_parent_group_ids)
        result = self._rpc_client.execute('getTaskIdsInParentGroup',
                                          mom_parent_group_ids=mom_parent_group_ids)
        logger.info("getTaskIdsInParentGroup(%s): %s", mom_parent_group_ids, result)
        return result

    def getDataProducts(self, ids):
        logger.debug("getDataProducts(%s)", ids)
        result = self._rpc_client.execute('getDataProducts', mom_ids=ids)
        logger.debug('Found # dataproducts per mom2id: %s', ', '.join(
            '%s:%s' % (dp_id, len(dps)) for dp_id, dps in list(result.items())))
        return result

    def getMoMIdsForOTDBIds(self, otdb_ids):
        """reverse lookup from otdb_id(s) to mom2id(s)
        returns: dict with otdb_id(s) in keys, mom2id(s) as values"""
        if isinstance(otdb_ids, int) or isinstance(otdb_ids, str):
            otdb_ids = [otdb_ids]
        logger.debug("getMoMIdsForOTDBIds(%s)", otdb_ids)
        result = self._rpc_client.execute('getMoMIdsForOTDBIds', otdb_ids=otdb_ids)
        return result

    def getOTDBIdsForMoMIds(self, mom_ids):
        """lookup from mom2id(s) to otdb_id(s)
        returns: dict with mom2id(s) in keys, otdb_id(s) as values"""
        if isinstance(mom_ids, int) or isinstance(mom_ids, str):
            mom_ids = [mom_ids]
        logger.debug("getOTDBIdsForMoMIds(%s)", mom_ids)
        result = self._rpc_client.execute('getOTDBIdsForMoMIds', mom_ids=mom_ids)
        return result

    def getTaskIdsGraph(self, mom2id):
        """Get the fully connected graph of interconnected tasks given any mom2id in that graph
        returns: dict with mom2id:node as key value pairs, where each node is a dict with items
        node_mom2id, predecessor_ids, successor_ids"""
        logger.debug("getTaskIdsGraph(%s)", mom2id)
        result = self._rpc_client.execute('getTaskIdsGraph', mom2id=mom2id)
        return result

    def get_station_selection(self, mom_id):
        """
        Get the station selection represented as resource groups with min/max values for given
        mom id.
        :param mom_id: int
        :return: list of dict
        """
        logger.info("Calling get_station_selection for mom id "+str(mom_id))
        station_selection = self._rpc_client.execute('get_station_selection', mom_id=mom_id)
        return station_selection

    def get_trigger_time_restrictions(self, mom_id):
        """
        Returns min start and max end times and duration for given mom id.
        :param mom_id: int
        :return: dict
        """
        logger.info("Calling get_trigger_time_restrictions for mom id "+str(mom_id))
        time_restrictions = self._rpc_client.execute('get_trigger_time_restrictions', mom_id=mom_id)
        return time_restrictions

    def get_storagemanager(self, mom_id):
        """
        Returns the storagemanager for given mom id.
        :param mom_id: int
        :return: string
        """
        logger.info("Calling get_storagemanager for mom id "+str(mom_id))
        storagemanager = self._rpc_client.execute('get_storagemanager', mom_id=mom_id)
        return storagemanager


def main():
    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='do requests to the momqueryservice from the commandline')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the broker, default: localhost')
    parser.add_option('-e', '--exchange', dest='exchange', type='string', default=DEFAULT_BUSNAME,
                      help='Name of the bus exchange on the broker, default: [%default]')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true',
                      help='verbose logging')
    parser.add_option('-P', '--projects', dest='projects', action='store_true',
                      help='get list of all projects')
    parser.add_option('-p', '--project_details', dest='project_details', type='int',
                      help='get project details for mom object with given id')
    parser.add_option('-O', '--objects_details', dest='objects_details', type='int',
                      help='get object details for mom object with given id')
    parser.add_option('--predecessors', dest='id_for_predecessors', type='int',
                      help='get the predecessor id\'s for the given mom2id')
    parser.add_option('--successors', dest='id_for_successors', type='int',
                      help='get the successors id\'s for the given mom2id')
    parser.add_option('-g', '--group', dest='group_id', type='int',
                      help='get the tasks ids in the given group mom2id')
    parser.add_option('--parent_group', dest='parent_group_id', type='int',
                      help='get the tasks ids in the given parent group mom2id')
    parser.add_option('-d', '--dataproducts', dest='id_for_dataproducts', type='int',
                      help='get the dataproducts for the given mom2id')
    parser.add_option('-o', '--otdb_id', dest='otdb_id', type='int',
                      help='get the mom2id for the given otdb_id')
    parser.add_option('-m', '--mom_id', dest='mom_id', type='int',
                      help='get the otdb_id for the given mom2id')
    parser.add_option('-t', '--task_graph', dest='task_graph_mom2id', type='int',
                      help='get the fully connected task graph given any mom2id in that graph')
    (options, args) = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if options.verbose else logging.WARN)

    with MoMQueryRPC.create(exchange=options.exchange, broker=options.broker) as rpc:
        if options.projects:
            projects = rpc.getProjects()
            for project in projects:
                print(project)

        if options.project_details:
            project_details = rpc.get_project_details(options.project_details)
            if project_details:
                for k, v in list(project_details.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.objects_details:
            objects_details = rpc.getObjectDetails(options.objects_details)
            if objects_details:
                for k, v in list(objects_details.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.id_for_predecessors:
            predecessor_ids = rpc.getPredecessorIds(options.id_for_predecessors)
            if predecessor_ids:
                for k, v in list(predecessor_ids.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.id_for_successors:
            successor_ids = rpc.getSuccessorIds(options.id_for_successors)
            if successor_ids:
                for k, v in list(successor_ids.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.group_id:
            task_ids = rpc.getTaskIdsInGroup(options.group_id)
            if task_ids:
                for k, v in list(task_ids.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.parent_group_id:
            task_ids = rpc.getTaskIdsInParentGroup(options.parent_group_id)
            if task_ids:
                for k, v in list(task_ids.items()):
                    print('  %s: %s' % (k, v))
            else:
                print('No results')

        if options.id_for_dataproducts:
            results = rpc.getDataProducts(options.id_for_dataproducts)
            if results:
                for mom2id, dps in list(results.items()):
                    print('  dataproducts for %s' % mom2id)
                    pprint.pprint(dps)
            else:
                print('No results')

        if options.otdb_id:
            results = rpc.getMoMIdsForOTDBIds(options.otdb_id)
            if results and options.otdb_id in results:
                print('mom2id=%s for otdb_id=%s' % (results[options.otdb_id], options.otdb_id))
            else:
                print('No results')

        if options.mom_id:
            results = rpc.getOTDBIdsForMoMIds(options.mom_id)
            if results and options.mom_id in results:
                print('otdb_id=%s for mom2id=%s' % (results[options.mom_id], options.mom_id))
            else:
                print('No results')

        if options.task_graph_mom2id:
            result = rpc.getTaskIdsGraph(options.task_graph_mom2id)
            pprint.pprint(result)


if __name__ == '__main__':
    main()
