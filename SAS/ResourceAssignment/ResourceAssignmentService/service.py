#!/usr/bin/env python3
# $Id$

'''
'''
import logging
from optparse import OptionParser
from lofar.messaging import RPCService, ServiceMessageHandler, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import waitForInterrupt
from lofar.sas.resourceassignment.database import radb
from lofar.sas.resourceassignment.resourceassignmentservice.config import DEFAULT_RADB_SERVICENAME
from lofar.common import dbcredentials

logger = logging.getLogger(__name__)

class RADBServiceMessageHandler(ServiceMessageHandler):
    def __init__(self, dbcreds: dbcredentials.Credentials):
        super().__init__()
        self.radb = radb.RADatabase(dbcreds=dbcreds)

    def init_service_handler(self, service_name: str=DEFAULT_RADB_SERVICENAME):
        super().init_service_handler(service_name)

        self.register_service_method('GetResourceClaimStatuses', self._getResourceClaimStatuses)
        self.register_service_method('GetResourceClaimProperties', self._getResourceClaimProperties)
        self.register_service_method('InsertResourceClaimProperty', self._insertResourceClaimProperty)
        self.register_service_method('GetResourceClaimPropertyTypes', self._getResourceClaimPropertyTypes)
        self.register_service_method('GetRcuSpecifications', self._getRcuSpecifications)
        self.register_service_method('GetRcuSpecification', self._getRcuSpecification)
        self.register_service_method('InsertRcuSpecifications', self._insertRcuSpecifications)
        self.register_service_method('InsertRcuSpecification', self._insertRcuSpecification)
        self.register_service_method('GetResourceClaims', self._getResourceClaims)
        self.register_service_method('GetResourceClaim', self._getResourceClaim)
        self.register_service_method('InsertResourceClaims', self._insertResourceClaims)
        self.register_service_method('InsertResourceClaim', self._insertResourceClaim)
        self.register_service_method('DeleteResourceClaim', self._deleteResourceClaim)
        self.register_service_method('UpdateResourceClaim', self._updateResourceClaim)
        self.register_service_method('UpdateResourceClaims', self._updateResourceClaims)
        self.register_service_method('UpdateTaskAndResourceClaims', self._updateTaskAndResourceClaims)
        self.register_service_method('GetResourceUsages', self._getResourceUsages)
        self.register_service_method('GetResourceGroupTypes', self._getResourceGroupTypes)
        self.register_service_method('GetResourceGroups', self._getResourceGroups)
        self.register_service_method('GetResourceGroupNames', self._getResourceGroupNames)
        self.register_service_method('GetResourceGroupMemberships', self._getResourceGroupMemberships)
        self.register_service_method('GetResourceTypes', self._getResourceTypes)
        self.register_service_method('GetResources', self._getResources)
        self.register_service_method('UpdateResourceAvailability', self._updateResourceAvailability)
        self.register_service_method('GetTasksTimeWindow', self._getTasksTimeWindow)
        self.register_service_method('GetTasks', self._getTasks)
        self.register_service_method('GetTask', self._getTask)
        self.register_service_method('InsertTask', self._insertTask)
        self.register_service_method('DeleteTask', self._deleteTask)
        self.register_service_method('UpdateTask', self._updateTask)
        self.register_service_method('UpdateTaskStatusForOtdbId', self._updateTaskStatusForOtdbId)
        self.register_service_method('GetTaskPredecessorIds', self._getTaskPredecessorIds)
        self.register_service_method('GetTaskSuccessorIds', self._getTaskSuccessorIds)
        self.register_service_method('InsertTaskPredecessor', self._insertTaskPredecessor)
        self.register_service_method('InsertTaskPredecessors', self._insertTaskPredecessors)
        self.register_service_method('GetTaskStatuses', self._getTaskStatuses)
        self.register_service_method('GetTaskTypes', self._getTaskTypes)
        self.register_service_method('GetSpecifications', self._getSpecifications)
        self.register_service_method('GetSpecification', self._getSpecification)
        self.register_service_method('insertOrUpdateSpecificationAndTask', self._insertOrUpdateSpecificationAndTask)
        self.register_service_method('InsertSpecification', self._insertSpecification)
        self.register_service_method('DeleteSpecification', self._deleteSpecification)
        self.register_service_method('UpdateSpecification', self._updateSpecification)
        self.register_service_method('GetUnits', self._getUnits)
        self.register_service_method('GetResourceAllocationConfig', self._getResourceAllocationConfig)
        self.register_service_method('get_overlapping_claims', self._get_overlapping_claims)
        self.register_service_method('get_overlapping_tasks', self._get_overlapping_tasks)
        self.register_service_method('get_max_resource_usage_between', self._get_max_resource_usage_between)
        self.register_service_method('get_resource_claimable_capacity', self._get_resource_claimable_capacity)

    def _getTaskStatuses(self):
        return self.radb.getTaskStatuses()

    def _getTaskTypes(self):
        return self.radb.getTaskTypes()

    def _getRcuSpecifications(self, **kwargs):
        return self.radb.getRcuSpecifications(rcu_ids=kwargs.get('rcu_ids'))

    def _getRcuSpecification(self, **kwargs):
        return self.radb.getRcuSpecification(rcu_id=kwargs.get('rcu_id'))

    def _insertRcuSpecifications(self, **kwargs):
        return self.radb.insertRcuSpecifications(rcu_patterns_list=kwargs.get('rcu_patterns_list'),
                                                 commit=kwargs.get('commit'))

    def _insertRcuSpecification(self, **kwargs):
        return self.radb.insertRcuSpecification(rcu_pattern=kwargs.get('rcu_pattern'),
                                                commit=kwargs.get('commit'))

    def _getResourceClaimStatuses(self):
        return self.radb.getResourceClaimStatuses()

    def _getResourceClaimPropertyTypes(self):
        return self.radb.getResourceClaimPropertyTypes()

    def _getResourceClaimProperties(self, **kwargs):
        return self.radb.getResourceClaimProperties(claim_ids=kwargs.get('claim_ids'), task_id=kwargs.get('task_id'))

    def _insertResourceClaimProperty(self, **kwargs):
        id = self.radb.insertResourceClaimProperty(kwargs.get('claim_id'), kwargs.get('property_type'), kwargs.get('value'), kwargs.get('io_type'))
        return {'id':id}

    def _getResourceClaims(self, **kwargs):
        return self.radb.getResourceClaims(claim_ids=kwargs.get('claim_ids'),
                                           lower_bound=kwargs.get('lower_bound'),
                                           upper_bound=kwargs.get('upper_bound'),
                                           resource_ids=kwargs.get('resource_ids'),
                                           task_ids=kwargs.get('task_ids'),
                                           status=kwargs.get('status'),
                                           resource_type=kwargs.get('resource_type'),
                                           extended=kwargs.get('extended', False),
                                           include_properties=kwargs.get('include_properties'))

    def _getResourceClaim(self, **kwargs):
        claim = self.radb.getResourceClaim(kwargs['id'])
        return claim

    def _insertResourceClaims(self, **kwargs):
        logger.info('InsertResourceClaims: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        claims = kwargs['claims']

        ids = self.radb.insertResourceClaims(kwargs['task_id'],
                                             claims,
                                             kwargs['username'],
                                             kwargs['user_id'])
        return {'ids':ids}

    def _insertResourceClaim(self, **kwargs):
        logger.info('InsertResourceClaim: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = self.radb.insertResourceClaim(kwargs['resource_id'],
                                           kwargs['task_id'],
                                           kwargs['starttime'],
                                           kwargs['endtime'],
                                           kwargs.get('status_id', kwargs.get('status')),
                                           kwargs['claim_size'],
                                           kwargs['username'],
                                           kwargs['user_id'],
                                           kwargs['rcu_id'],
                                           kwargs.get('properties'))
        return {'id':id}

    def _deleteResourceClaim(self, **kwargs):
        logger.info('DeleteResourceClaim: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        deleted = self.radb.deleteResourceClaim(id)
        return {'id': id, 'deleted': deleted}

    def _updateResourceClaim(self, **kwargs):
        logger.info('UpdateResourceClaim: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        updated = self.radb.updateResourceClaim(id,
                                                resource_id=kwargs.get('resource_id'),
                                                task_id=kwargs.get('task_id'),
                                                starttime=kwargs.get('starttime'),
                                                endtime=kwargs.get('endtime'),
                                                status=kwargs.get('status_id', kwargs.get('status')),
                                                claim_size=kwargs.get('claim_size'),
                                                username=kwargs.get('username'),
                                                user_id=kwargs.get('user_id'))
        return {'id': id, 'updated': updated}

    def _updateResourceClaims(self, **kwargs):
        logger.info('UpdateResourceClaims: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        task_id = kwargs['task_id']

        updated = self.radb.updateResourceClaims(where_resource_claim_ids=kwargs.get('where_resource_claim_ids'),
                                                 where_task_ids=kwargs.get('where_task_ids'),
                                                 where_resource_types=kwargs.get('where_resource_types'),
                                                 resource_id=kwargs.get('resource_id'),
                                                 task_id=kwargs.get('task_id'),
                                                 starttime=kwargs.get('starttime'),
                                                 endtime=kwargs.get('endtime'),
                                                 status=kwargs.get('status_id', kwargs.get('status')),
                                                 claim_size=kwargs.get('status'),
                                                 username=kwargs.get('username'),
                                                 user_id=kwargs.get('user_id'),
                                                 used_rcus=None)

        return {'where_resource_claim_ids': kwargs.get('where_resource_claim_ids'),
                'where_task_ids': kwargs.get('where_task_ids'),
                'where_resource_types': kwargs.get('where_resource_types'),
                'updated': updated}

    def _updateTaskAndResourceClaims(self, **kwargs):
        logger.info('UpdateTaskAndResourceClaims: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        task_id = kwargs['task_id']

        updated = self.radb.updateTaskAndResourceClaims(task_id,
                                                        starttime=kwargs.get('starttime'),
                                                        endtime=kwargs.get('endtime'),
                                                        task_status=kwargs.get('task_status_id', kwargs.get('task_status')),
                                                        claim_status=kwargs.get('claim_status_id', kwargs.get('claim_status')),
                                                        username=kwargs.get('username'),
                                                        user_id=kwargs.get('user_id'),
                                                        where_resource_types=kwargs.get('where_resource_types'),
                                                        commit=kwargs.get('commit', True))

        return {'task_id': task_id,
                'where_resource_types': kwargs.get('where_resource_types'),
                'updated': updated}

    def _getResourceUsages(self, **kwargs):
        return self.radb.getResourceUsages(lower_bound=kwargs.get('lower_bound'),
                                             upper_bound=kwargs.get('upper_bound'),
                                             resource_ids=kwargs.get('resource_ids'),
                                             claim_statuses=kwargs.get('status'))

    def _getResourceGroupTypes(self):
        return self.radb.getResourceGroupTypes()

    def _getResourceGroups(self):
        return self.radb.getResourceGroups()

    def _getResourceGroupNames(self, **kwargs):
        return self.radb.getResourceGroupNames(resourceGroupTypeName=kwargs.get('resourceGroupTypeName'))

    def _getResourceGroupMemberships(self):
        return self.radb.getResourceGroupMemberships()

    def _getResourceTypes(self):
        return self.radb.getResourceTypes()

    def _getResources(self, **kwargs):
        return self.radb.getResources(resource_ids=kwargs.get('resource_ids'),
                                      resource_types=kwargs.get('resource_types'),
                                      include_availability=kwargs.get('include_availability', False))

    def _updateResourceAvailability(self, **kwargs):
        updated = self.radb.updateResourceAvailability(resource_id=kwargs['resource_id'],
                                                       active=kwargs.get('active'),
                                                       available_capacity=kwargs.get('available_capacity'),
                                                       total_capacity=kwargs.get('total_capacity'))
        return {'resource_id': kwargs['resource_id'], 'updated': updated }

    def _getTasksTimeWindow(self, **kwargs):
        logger.info('GetTasksTimeWindow: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        return self.radb.getTasksTimeWindow(task_ids=kwargs.get('task_ids'),
                                            mom_ids=kwargs.get('mom_ids'),
                                            otdb_ids=kwargs.get('otdb_ids'))

    def _getTasks(self, **kwargs):
        logger.info('GetTasks: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        return self.radb.getTasks(lower_bound=kwargs.get('lower_bound'),
                                  upper_bound=kwargs.get('upper_bound'),
                                  task_ids=kwargs.get('task_ids'),
                                  task_status=kwargs.get('task_status'),
                                  task_type=kwargs.get('task_type'),
                                  mom_ids=kwargs.get('mom_ids'),
                                  otdb_ids=kwargs.get('otdb_ids'),
                                  cluster=kwargs.get('cluster'))

    def _getTask(self, **kwargs):
        logger.info('GetTask: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        task = self.radb.getTask(id=kwargs.get('id'), mom_id=kwargs.get('mom_id'), otdb_id=kwargs.get('otdb_id'), specification_id=kwargs.get('specification_id'))
        return task

    def _insertTask(self, **kwargs):
        logger.info('InsertTask: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        task_id = self.radb.insertTask(kwargs['mom_id'],
                                       kwargs['otdb_id'],
                                       kwargs.get('status_id', kwargs.get('task_status', 'prepared')),
                                       kwargs.get('type_id', kwargs.get('task_type')),
                                       kwargs['specification_id'])
        return {'id':task_id }

    def _deleteTask(self, **kwargs):
        logger.info('DeleteTask: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        deleted = self.radb.deleteTask(id)
        return {'id': id, 'deleted': deleted}

    def _updateTaskStatusForOtdbId(self, **kwargs):
        logger.info('UpdateTaskStatusForOtdbId: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        otdb_id=kwargs.get('otdb_id')
        updated = self.radb.updateTaskStatusForOtdbId(otdb_id=otdb_id,
                                                      task_status=kwargs.get('status_id', kwargs.get('task_status')))
        return {'otdb_id': otdb_id, 'updated': updated}

    def _updateTask(self, **kwargs):
        logger.info('UpdateTask: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        updated = self.radb.updateTask(id,
                                       mom_id=kwargs.get('mom_id'),
                                       otdb_id=kwargs.get('otdb_id'),
                                       task_status=kwargs.get('status_id', kwargs.get('task_status')),
                                       task_type=kwargs.get('type_id', kwargs.get('task_type')),
                                       specification_id=kwargs.get('specification_id'))
        return {'id': id, 'updated': updated}

    def _getTaskPredecessorIds(self, **kwargs):
        logger.info('GetTaskPredecessorIds: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        return self.radb.getTaskPredecessorIds(kwargs.get('id'))

    def _getTaskSuccessorIds(self, **kwargs):
        logger.info('GetTaskSuccessorIds: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        return self.radb.getTaskSuccessorIds(kwargs.get('id'))

    def _insertTaskPredecessor(self, **kwargs):
        id = self.radb.insertTaskPredecessor(kwargs['task_id'],
                                             kwargs['predecessor_id'])
        return {'id':id}

    def _insertTaskPredecessors(self, **kwargs):
        ids = self.radb.insertTaskPredecessors(kwargs['task_id'],
                                               kwargs['predecessor_ids'])
        return {'ids':ids}

    def _getSpecifications(self):
        return self.radb.getSpecifications()

    def _getSpecification(self, **kwargs):
        logger.info('GetSpecification: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        specification = self.radb.getSpecification(kwargs['id'])
        return specification

    def _insertOrUpdateSpecificationAndTask(self, **kwargs):
        logger.info('insertOrUpdateSpecificationAndTask: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None and k != 'content'}))
        return self.radb.insertOrUpdateSpecificationAndTask(kwargs['mom_id'],
                                                    kwargs['otdb_id'],
                                                    kwargs['task_status'],
                                                    kwargs['task_type'],
                                                    kwargs.get('starttime'),
                                                    kwargs.get('endtime'),
                                                    kwargs['content'],
                                                    kwargs['cluster'])

    def _insertSpecification(self, **kwargs):
        logger.info('InsertSpecification: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        specification_id = self.radb.insertSpecification(kwargs.get('starttime'),
                                                         kwargs.get('endtime'),
                                                         kwargs['content'],
                                                         kwargs['cluster'])
        return {'id':specification_id}

    def _deleteSpecification(self, **kwargs):
        logger.info('DeleteSpecification: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        deleted = self.radb.deleteSpecification(id)
        return {'id': id, 'deleted': deleted}

    def _updateSpecification(self, **kwargs):
        logger.info('UpdateSpecification: %s' % dict({k:v for k,v in list(kwargs.items()) if v != None}))
        id = kwargs['id']
        updated = self.radb.updateSpecification(id,
                                                starttime=kwargs['starttime'],
                                                endtime=kwargs['endtime'],
                                                content=kwargs.get('content'),
                                                cluster=kwargs.get('cluster'))
        return {'id': id, 'updated': updated}

    def _getUnits(self):
        return self.radb.getUnits()

    def _getResourceAllocationConfig(self, **kwargs):
        return self.radb.getResourceAllocationConfig(sql_like_name_pattern=kwargs.get('sql_like_name_pattern'))

    def _get_overlapping_claims(self, **kwargs):
        return self.radb.get_overlapping_claims(claim_id=kwargs.get('claim_id'))

    def _get_overlapping_tasks(self, **kwargs):
        return self.radb.get_overlapping_tasks(claim_id=kwargs.get('claim_id'))

    def _get_max_resource_usage_between(self, **kwargs):
        logger.info('get_max_resource_usage_between: %s' % kwargs)
        return self.radb.get_max_resource_usage_between(resource_id=kwargs.get('resource_id'),
                                                        lower_bound=kwargs['lower_bound'],
                                                        upper_bound=kwargs['upper_bound'],
                                                        claim_status=kwargs.get('claim_status', 'claimed'))

    def _get_resource_claimable_capacity(self, **kwargs):
        logger.info('get_resource_claimable_capacity: %s' % kwargs)
        resource_claimable_capacity = self.radb.get_resource_claimable_capacity(
            resource_id=kwargs.get('resource_id'),
            lower_bound=kwargs['lower_bound'],
            upper_bound=kwargs['upper_bound'])

        return { 'resource_claimable_capacity': resource_claimable_capacity}


def createService(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER, dbcreds=None):
    return RPCService(DEFAULT_RADB_SERVICENAME,
                      RADBServiceMessageHandler,
                      handler_kwargs={'dbcreds': dbcreds},
                      exchange=exchange,
                      broker=broker,
                      num_threads=4)

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the resourceassignment database service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME, help="Name of the bus exchange on the broker, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")
    (options, args) = parser.parse_args()

    dbcreds = dbcredentials.parse_options(options)

    logging.basicConfig(format='%(asctime)s %(thread)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    with createService(exchange=options.exchange,
                       broker=options.broker,
                       dbcreds=dbcreds):
        waitForInterrupt()

if __name__ == '__main__':
    main()
