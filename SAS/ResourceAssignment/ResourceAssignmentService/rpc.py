#!/usr/bin/env python3

# Copyright (C) 2017
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

import logging
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.sas.resourceassignment.resourceassignmentservice.config import DEFAULT_RADB_SERVICENAME

''' Simple RPC client for Service lofarbus.*Z
'''

logger = logging.getLogger(__name__)


class RADBRPCException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "RADBRPCException: " + str(self.message)


class RADBRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the RADBRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_RADB_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_RADB_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_RPC_TIMEOUT):
        """Create a MoMQueryRPC connecting to the given exchange/broker on the default DEFAULT_RADB_SERVICENAME service"""
        return RADBRPC(RPCClient(service_name=DEFAULT_RADB_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def getResourceClaimStatuses(self):
        return self._rpc_client.execute('GetResourceClaimStatuses')

    def getResourceClaimPropertyTypes(self):
        return self._rpc_client.execute('GetResourceClaimPropertyTypes')

    def getResourceClaimProperties(self, claim_ids=None, task_id=None):
        return self._rpc_client.execute('GetResourceClaimProperties', claim_ids=claim_ids, task_id=task_id)

    def insertResourceClaimProperty(self, claim_id, property_type, value, io_type):
        return self._rpc_client.execute('InsertResourceClaimProperty', claim_id=claim_id,
                                                       property_type=property_type,
                                                       value=value,
                                                       io_type=io_type)

    def getResourceClaims(self, claim_ids=None, lower_bound=None, upper_bound=None, resource_ids=None, task_ids=None,
                          status=None, resource_type=None, extended=False, include_properties=False):
        return self._rpc_client.execute('GetResourceClaims', claim_ids=claim_ids,
                                               lower_bound=lower_bound,
                                               upper_bound=upper_bound,
                                               resource_ids=resource_ids,
                                               task_ids=task_ids,
                                               status=status,
                                               resource_type=resource_type,
                                               extended=extended,
                                               include_properties=include_properties)

    def getResourceClaim(self, id):
        return self._rpc_client.execute('GetResourceClaim', id=id)

    def insertResourceClaim(self, resource_id, task_id, starttime, endtime, status, claim_size, username,
                            user_id, used_rcus=None, properties=None):
        return self._rpc_client.execute('InsertResourceClaim', resource_id=resource_id,
                                                    task_id=task_id,
                                                    starttime=starttime,
                                                    endtime=endtime,
                                                    status=status,
                                                    claim_size=claim_size,
                                                    username=username,
                                                    used_rcus=used_rcus,
                                                    user_id=user_id,
                                                    properties=properties)

    def insertResourceClaims(self, task_id, claims, username, user_id):
        return self._rpc_client.execute('InsertResourceClaims', task_id=task_id,
                                                claims=claims,
                                                username=username,
                                                user_id=user_id)

    def deleteResourceClaim(self, id):
        return self._rpc_client.execute('DeleteResourceClaim', id=id)

    def updateResourceClaim(self, id, resource_id=None, task_id=None, starttime=None, endtime=None, status=None, claim_size=None, username=None, used_rcus=None, user_id=None):
        return self._rpc_client.execute('UpdateResourceClaim', id=id,
                                                    resource_id=resource_id,
                                                    task_id=task_id,
                                                    starttime=starttime,
                                                    endtime=endtime,
                                                    status=status,
                                                    claim_size=claim_size,
                                                    username=username,
                                                    used_rcus=used_rcus,
                                                    user_id=user_id)

    def updateResourceClaims(self, where_resource_claim_ids=None, where_task_ids=None, where_resource_types=None,
                             resource_id=None, task_id=None, starttime=None, endtime=None,
                             status=None, claim_size=None, username=None, used_rcus=None, user_id=None,
                             commit=True):
        return self._rpc_client.execute('UpdateResourceClaims', where_resource_claim_ids=where_resource_claim_ids,
                                                where_task_ids=where_task_ids,
                                                where_resource_types=where_resource_types,
                                                resource_id=resource_id,
                                                task_id=task_id,
                                                starttime=starttime,
                                                endtime=endtime,
                                                status=status,
                                                claim_size=claim_size,
                                                username=username,
                                                used_rcus=used_rcus,
                                                user_id=user_id)

    def updateTaskAndResourceClaims(self, task_id, starttime=None, endtime=None, task_status=None, claim_status=None, username=None, used_rcus=None, user_id=None, where_resource_types=None):
        return self._rpc_client.execute('UpdateTaskAndResourceClaims', task_id=task_id,
                                                       starttime=starttime,
                                                       endtime=endtime,
                                                       task_status=task_status,
                                                       claim_status=claim_status,
                                                       username=username,
                                                       used_rcus=used_rcus,
                                                       user_id=user_id,
                                                       where_resource_types=where_resource_types)


    def getResourceUsages(self, lower_bound=None, upper_bound=None, resource_ids=None, status=None):
        return self._rpc_client.execute('GetResourceUsages',
                              lower_bound=lower_bound,
                              upper_bound=upper_bound,
                              resource_ids=resource_ids,
                              status=status)

    def getResourceGroupTypes(self):
        return self._rpc_client.execute('GetResourceGroupTypes')

    def getResourceGroups(self):
        return self._rpc_client.execute('GetResourceGroups')

    def getResourceGroupNames(self, resourceGroupTypeName):
        return self._rpc_client.execute('GetResourceGroupNames',
                        resourceGroupTypeName=resourceGroupTypeName)

    def getResourceGroupMemberships(self):
        return self._rpc_client.execute('GetResourceGroupMemberships')

    def getResourceTypes(self):
        return self._rpc_client.execute('GetResourceTypes')

    def getResources(self, resource_ids=None, resource_types=None, include_availability=False):
        return self._rpc_client.execute('GetResources', resource_ids=resource_ids, resource_types=resource_types, include_availability=include_availability)

    # instantiate this object and call this function to update DRAGNET active (config file), avail_cap (df(1) and config file override) and total_cap (config file) values
    def updateResourceAvailability(self, resource_id, active=None, available_capacity=None, total_capacity=None):
        return self._rpc_client.execute('UpdateResourceAvailability',
                        resource_id=resource_id,
                        active=active,
                        available_capacity=available_capacity,
                        total_capacity=total_capacity)

    def getTask(self, id=None, mom_id=None, otdb_id=None, specification_id=None):
        '''get a task for either the given (task)id, or for the given mom_id, or for the given otdb_id, or for the given specification_id'''
        return self._rpc_client.execute('GetTask', id=id, mom_id=mom_id, otdb_id=otdb_id, specification_id=specification_id)

    def insertTask(self, mom_id, otdb_id, task_status, task_type, specification_id):
        return self._rpc_client.execute('InsertTask', mom_id=mom_id,
                                           otdb_id=otdb_id,
                                           task_status=task_status,
                                           task_type=task_type,
                                           specification_id=specification_id)

    def deleteTask(self, id):
        return self._rpc_client.execute('DeleteTask', id=id)

    def updateTask(self, task_id, mom_id=None, otdb_id=None, task_status=None, task_type=None, specification_id=None):
        return self._rpc_client.execute('UpdateTask',
                         id=task_id,
                         mom_id=mom_id,
                         otdb_id=otdb_id,
                         task_status=task_status,
                         task_type=task_type,
                         specification_id=specification_id)

    def updateTaskStatusForOtdbId(self, otdb_id, task_status):
        return self._rpc_client.execute('UpdateTaskStatusForOtdbId',
                         otdb_id=otdb_id,
                         task_status=task_status)

    def getTasksTimeWindow(self, task_ids=None, mom_ids=None, otdb_ids=None):
        return self._rpc_client.execute('GetTasksTimeWindow', task_ids=task_ids, mom_ids=mom_ids, otdb_ids=otdb_ids)

    def getTasks(self, lower_bound=None, upper_bound=None, task_ids=None, task_status=None, task_type=None, mom_ids=None, otdb_ids=None, cluster=None):
        '''getTasks let's you query tasks from the radb with many optional filters.
        :param lower_bound: datetime specifies the lower_bound of a time window above which to select tasks
        :param upper_bound: datetime specifies the upper_bound of a time window below which to select tasks
        :param task_ids: int/list/tuple specifies one or more task_ids to select
        :param task_status: int/string/list specifies one or more task_statuses to select in either task_status_id or task_status_name form
        :param task_type: int/string/list specifies one or more task_types to select in either task_type_id or task_type_name form
        :param mom_ids: int/list/tuple specifies one or more mom_ids to select
        :param otdb_ids: int/list/tuple specifies one or more otdb_ids to select
        :param cluster: string specifies the cluster to select
        '''
        return self._rpc_client.execute('GetTasks', lower_bound=lower_bound, upper_bound=upper_bound, task_ids=task_ids, task_status=task_status, task_type=task_type, mom_ids=mom_ids, otdb_ids=otdb_ids, cluster=cluster)

    def getTaskPredecessorIds(self, id=None):
        return self._rpc_client.execute('GetTaskPredecessorIds', id=id)

    def getTaskSuccessorIds(self, **kwargs):
        return self._rpc_client.execute('GetTaskSuccessorIds', id=id)

    def insertTaskPredecessor(self, task_id, predecessor_id):
        return self._rpc_client.execute('InsertTaskPredecessor', task_id=task_id, predecessor_id=predecessor_id)

    def insertTaskPredecessors(self, task_id, predecessor_ids):
        return self._rpc_client.execute('InsertTaskPredecessors', task_id=task_id, predecessor_ids=predecessor_ids)

    def getTaskTypes(self):
        return self._rpc_client.execute('GetTaskTypes')

    def getTaskStatuses(self):
        return self._rpc_client.execute('GetTaskStatuses')

    def getSpecification(self, id):
        return self._rpc_client.execute('GetSpecification', id=id)

    def insertOrUpdateSpecificationAndTask(self, mom_id, otdb_id, task_status, task_type, starttime, endtime, content, cluster):
        return self._rpc_client.execute('insertOrUpdateSpecificationAndTask',
                        mom_id=mom_id,
                        otdb_id=otdb_id,
                        task_status=task_status,
                        task_type=task_type,
                        starttime=starttime,
                        endtime=endtime,
                        content=content,
                        cluster=cluster)

    def insertSpecification(self, starttime, endtime, content, cluster):
        return self._rpc_client.execute('InsertSpecification',
                        starttime=starttime,
                        endtime=endtime,
                        content=content,
                        cluster=cluster)

    def deleteSpecification(self, id):
        return self._rpc_client.execute('DeleteSpecification', id=id)

    def updateSpecification(self, id, starttime=None, endtime=None, content=None, cluster=None):
        return self._rpc_client.execute('UpdateSpecification',
                         id=id,
                         starttime=starttime,
                         endtime=endtime,
                         content=content,
                         cluster=cluster)

    def getSpecifications(self):
        return self._rpc_client.execute('GetSpecifications')

    def getUnits(self):
        return self._rpc_client.execute('GetUnits')

    def getResourceAllocationConfig(self, sql_like_name_pattern=None):
        return self._rpc_client.execute('GetResourceAllocationConfig',
                        sql_like_name_pattern=sql_like_name_pattern)

    def get_conflicting_overlapping_claims(self, claim_id):
        '''returns a list of claimed claims which overlap with given claim(s) and which prevent the given claim(s) to be claimed (cause it to be in conflict)'''
        return self._rpc_client.execute('get_overlapping_claims',
                        claim_id=claim_id)

    def get_conflicting_overlapping_tasks(self, claim_id):
        '''returns a list of tasks which overlap with given claim(s) and which prevent the given claim(s) to be claimed (cause it to be in conflict)'''
        return self._rpc_client.execute('get_overlapping_tasks',
                        claim_id=claim_id)

    def get_max_resource_usage_between(self, resource_id, lower_bound, upper_bound, claim_status='claimed'):
        return self._rpc_client.execute('get_max_resource_usage_between',
                          resource_id=resource_id,
                          lower_bound=lower_bound,
                          upper_bound=upper_bound,
                          claim_status=claim_status)

    def get_resource_claimable_capacity(self, resource_id, lower_bound, upper_bound):
        '''get the claimable capacity for the given resource within the timewindow given by lower_bound and upper_bound.
        this is the resource's available capacity (total-used) minus the maximum allocated usage in that timewindow.'''
        return self._rpc_client.execute('get_resource_claimable_capacity', resource_id=resource_id,
                                                           lower_bound=lower_bound,
                                                           upper_bound=upper_bound).get('resource_claimable_capacity')


def do_tests(exchange=DEFAULT_BUSNAME):
    from datetime import datetime, timedelta
    with RADBRPC.create(exchange=exchange) as rpc:
        tasks = rpc.getTasks(lower_bound=datetime.utcnow()-timedelta(days=1))
        print(tasks)
        return

        #for t in tasks:
            #print rpc.getTask(t['id'])
            #for i in range(4,9):
                #rcId = rpc.insertResourceClaim(i, t['id'], datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(hours=1), 'TENTATIVE', 1, 10, 'einstein', -1)['id']
            ##print rpc.deleteTask(t['id'])
            ##print rpc.getTasks()
            ##print rpc.getResourceClaims()

        #print
        #taskId = tasks[0]['id']
        #print 'taskId=', taskId
        #print rpc.getResourceClaimsForTask(taskId)
        #print rpc.updateResourceClaimsForTask(taskId, starttime=datetime.datetime.utcnow(), endtime=datetime.datetime.utcnow() + datetime.timedelta(hours=3))
        #print rpc.getResourceClaimsForTask(taskId)

        #print rpc.getTasks()
        #print rpc.getResourceClaims()
        #print rpc.getResources()
        #print rpc.getResourceGroups()
        #print rpc.getResourceGroupNames('cluster')
        #print rpc.getResourceGroupMemberships()

        #rpc.deleteTask(taskId)

        #print rpc.getTasks()
        #print rpc.getResourceClaims()
        #print rpc.getResourceAllocationConfig()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    do_tests()
