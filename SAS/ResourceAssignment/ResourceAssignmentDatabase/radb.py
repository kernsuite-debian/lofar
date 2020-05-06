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

# $Id$

'''
TODO: documentation
'''
import logging
from datetime import datetime, timedelta
import collections
from optparse import OptionParser
from lofar.common.postgres import PostgresDatabaseConnection, PostgresDBQueryExecutionError, FETCH_ONE, FETCH_ALL, FETCH_NONE
from lofar.common import dbcredentials

logger = logging.getLogger(__name__)

class RADBError(Exception):
    pass

class RADatabase(PostgresDatabaseConnection):
    def __init__(self, dbcreds: dbcredentials.DBCredentials=None,
                 num_connect_retries: int=5,
                 connect_retry_interval: float=1.0):

        if dbcreds is None:
            dbcreds = dbcredentials.DBCredentials().get("RADB")
            logger.info("Read default RADB dbcreds from disk: %s" % dbcreds.stringWithHiddenPassword())

        super().__init__(dbcreds=dbcreds,
                         auto_commit_selects=False,
                         num_connect_retries=num_connect_retries,
                         connect_retry_interval=connect_retry_interval)
        self._taskStatusName2IdCache = {}
        self._taskTypeName2IdCache = {}
        self._claimStatusName2IdCache = {}
        self._claimStatusId2NameCache = {}

    def getTaskStatuses(self):
        query = '''SELECT * from resource_allocation.task_status;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getTaskStatusNames(self):
        return [x['name'] for x in self.getTaskStatuses()]

    def getTaskStatusId(self, status_name, from_cache=True):
        if from_cache and status_name in self._taskStatusName2IdCache:
            return self._taskStatusName2IdCache[status_name]

        query = '''SELECT id from resource_allocation.task_status
                   WHERE name = %s;'''
        result = self.executeQuery(query, [status_name], fetch=FETCH_ONE)

        if result:
            self._taskStatusName2IdCache[status_name] = result['id']
            return result['id']

        raise KeyError('No such status: %s Valid values are: %s' % (status_name, ', '.join(self.getTaskStatusNames())))

    def getTaskTypes(self):
        query = '''SELECT * from resource_allocation.task_type;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getTaskTypeNames(self):
        return [x['name'] for x in self.getTaskTypes()]

    def getTaskTypeId(self, type_name, from_cache=True):
        if from_cache and type_name in self._taskTypeName2IdCache:
            return self._taskTypeName2IdCache[type_name]

        query = '''SELECT id from resource_allocation.task_type
                   WHERE name = %s;'''
        result = self.executeQuery(query, [type_name], fetch=FETCH_ONE)

        if result:
            self._taskTypeName2IdCache[type_name] = result['id']
            return result['id']

        raise KeyError('No such type: %s Valid values are: %s' % (type_name, ', '.join(self.getTaskTypeNames())))

    def getResourceClaimStatuses(self):
        query = '''SELECT * from resource_allocation.resource_claim_status;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceClaimStatusNames(self):
        return [x['name'] for x in self.getResourceClaimStatuses()]

    def getResourceClaimStatusId(self, status_name, from_cache=True):
        if from_cache and status_name in self._claimStatusName2IdCache:
            return self._claimStatusName2IdCache[status_name]

        query = '''SELECT id from resource_allocation.resource_claim_status
                   WHERE name = %s;'''
        result = self.executeQuery(query, [status_name], fetch=FETCH_ONE)

        if result:
            self._claimStatusName2IdCache[status_name] = result['id']
            self._claimStatusId2NameCache[result['id']] = status_name
            return result['id']

        raise KeyError('No such status: %s. Valid values are: %s' % (status_name, ', '.join(self.getResourceClaimStatusNames())))

    def getResourceClaimStatusName(self, status_id, from_cache=True):
        if from_cache and status_id in self._claimStatusId2NameCache:
            return self._claimStatusId2NameCache[status_id]

        query = '''SELECT name from resource_allocation.resource_claim_status
                   WHERE id = %s;'''
        result = self.executeQuery(query, [status_id], fetch=FETCH_ONE)

        if result:
            self._claimStatusId2NameCache[status_id] = result['name']
            self._claimStatusName2IdCache[result['name']] = status_id
            return result['name']

        raise KeyError('No such status_id: %s. Valid values are: %s' % (status_id, ', '.join([x['id'] for x in self.getResourceClaimStatuses()])))

    def getTasksTimeWindow(self, task_ids=None, mom_ids=None, otdb_ids=None):
        if len([x for x in [task_ids, mom_ids, otdb_ids] if x != None]) > 1:
            raise KeyError("Provide either task_ids or mom_ids or otdb_ids, not multiple kinds.")

        query = '''SELECT min(starttime) as min_starttime, max(endtime) as max_endtime from resource_allocation.task_view'''

        conditions = []
        qargs = []

        if task_ids is not None:
            if isinstance(task_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(task_ids)
            elif len(task_ids) > 0: #assume a list/enumerable of id's
                conditions.append('id in %s')
                qargs.append(tuple(task_ids))
            elif len(task_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        if mom_ids is not None:
            if isinstance(mom_ids, int): # just a single id
                conditions.append('mom_id = %s')
                qargs.append(mom_ids)
            elif len(mom_ids) > 0: #assume a list/enumerable of id's
                conditions.append('mom_id in %s')
                qargs.append(tuple(mom_ids))
            elif len(mom_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        if otdb_ids is not None:
            if isinstance(otdb_ids, int): # just a single id
                conditions.append('otdb_id = %s')
                qargs.append(otdb_ids)
            elif len(otdb_ids) > 0: #assume a list/enumerable of id's
                conditions.append('otdb_id in %s')
                qargs.append(tuple(otdb_ids))
            elif len(otdb_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        result = self.executeQuery(query, qargs, fetch=FETCH_ALL)
        if result and len(result) == 1:
            result = dict(result[0])
        else:
            result = {'max_endtime': datetime.utcnow(), 'min_starttime': datetime.utcnow()}

        return result

    def getTasks(self, lower_bound=None, upper_bound=None, task_ids=None, task_status=None, task_type=None, mom_ids=None, otdb_ids=None, cluster=None):
        if len([x for x in [task_ids, mom_ids, otdb_ids] if x != None]) > 1:
            raise KeyError("Provide either task_ids or mom_ids or otdb_ids, not multiple kinds.")

        query = '''SELECT * from resource_allocation.task_view'''

        conditions = []
        qargs = []

        if lower_bound is not None:
            conditions.append('endtime >= %s')
            qargs.append(lower_bound)

        if upper_bound is not None:
            conditions.append('starttime <= %s')
            qargs.append(upper_bound)

        if task_ids is not None:
            if isinstance(task_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(task_ids)
            elif len(task_ids) > 0: #assume a list/enumerable of id's
                conditions.append('id in %s')
                qargs.append(tuple(task_ids))
            elif len(task_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        if mom_ids is not None:
            if isinstance(mom_ids, int): # just a single id
                conditions.append('mom_id = %s')
                qargs.append(mom_ids)
            elif len(mom_ids) > 0: #assume a list/enumerable of id's
                conditions.append('mom_id in %s')
                qargs.append(tuple(mom_ids))
            elif len(mom_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        if otdb_ids is not None:
            if isinstance(otdb_ids, int): # just a single id
                conditions.append('otdb_id = %s')
                qargs.append(otdb_ids)
            elif len(otdb_ids) > 0: #assume a list/enumerable of id's
                conditions.append('otdb_id in %s')
                qargs.append(tuple(otdb_ids))
            elif len(otdb_ids) == 0: #assume a list/enumerable of id's, length 0
                return []

        task_status, task_type = self._convertTaskTypeAndStatusToIds(task_status, task_type)

        if task_status is not None:
            if isinstance(task_status, int): # just a single id
                conditions.append('status_id = %s')
                qargs.append(task_status)
            elif len(task_status) > 0: #assume a list/enumerable of id's
                conditions.append('status_id in %s')
                qargs.append(tuple(task_status))
            elif len(task_status) == 0: #assume a list/enumerable of id's, length 0
                return []

        if task_type is not None:
            if isinstance(task_type, int): # just a single id
                conditions.append('type_id = %s')
                qargs.append(task_type)
            elif len(task_type) > 0: #assume a list/enumerable of id's
                conditions.append('type_id in %s')
                qargs.append(tuple(task_type))
            elif len(task_type) == 0: #assume a list/enumerable of id's, length 0
                return []

        if cluster is not None:
            conditions.append('cluster = %s')
            qargs.append(cluster)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        tasks = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))

        for task in tasks:
            if task['predecessor_ids'] is None:
                task['predecessor_ids'] = []

            if task['successor_ids'] is None:
                task['successor_ids'] = []

        return tasks


    def getTask(self, id=None, mom_id=None, otdb_id=None, specification_id=None):
        '''get a task for either the given (task)id, or for the given mom_id, or for the given otdb_id, or for the given specification_id'''
        ids = [id, mom_id, otdb_id, specification_id]
        validIds = [x for x in ids if x != None]

        if len(validIds) != 1:
            raise KeyError("Provide one and only one id: id=%s, mom_id=%s, otdb_id=%s, specification_id=%s" % (id, mom_id, otdb_id, specification_id))

        query = '''SELECT * from resource_allocation.task_view tv '''
        if id is not None:
            query += '''where tv.id = (%s);'''
        elif mom_id is not None:
            query += '''where tv.mom_id = (%s);'''
        elif otdb_id is not None:
            query += '''where tv.otdb_id = (%s);'''
        elif specification_id is not None:
            query += '''where tv.specification_id = (%s);'''

        result = self.executeQuery(query, validIds, fetch=FETCH_ONE)

        task = dict(result) if result else None

        if task:
            if task['predecessor_ids'] is None:
                task['predecessor_ids'] = []

            if task['successor_ids'] is None:
                task['successor_ids'] = []

        return task

    def _convertTaskStatusToId(self, task_status):
        '''converts task_status to id in case it is a string or list of strings'''
        if task_status is not None:
            if isinstance(task_status, str):
                return self.getTaskStatusId(task_status, True)
            else: #assume iterable
                return [self._convertTaskStatusToId(x) for x in task_status]

        return task_status

    def _convertTaskTypeToId(self, task_type):
        '''converts task_status to id in case it is a string or list of strings'''
        if task_type is not None:
            if isinstance(task_type, str):
                return self.getTaskTypeId(task_type, True)
            else: #assume iterable
                return [self._convertTaskTypeToId(x) for x in task_type]

        return task_type

    def _convertTaskTypeAndStatusToIds(self, task_status, task_type):
        '''converts task_status and task_type to id's in case one and/or the other are strings'''
        return self._convertTaskStatusToId(task_status), self._convertTaskTypeToId(task_type)

    def insertTask(self, mom_id, otdb_id, task_status, task_type, specification_id, commit=True):
        if isinstance(mom_id, int) and mom_id < 0:
            mom_id = None

        if isinstance(otdb_id, int) and otdb_id < 0:
            otdb_id = None

        logger.info('insertTask mom_id=%s, otdb_id=%s, task_status=%s, task_type=%s, specification_id=%s' %
                    (mom_id, otdb_id, task_status, task_type, specification_id))
        task_status, task_type = self._convertTaskTypeAndStatusToIds(task_status, task_type)

        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''INSERT INTO resource_allocation.task
        (mom_id, otdb_id, status_id, type_id, specification_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;'''

        id = self.executeQuery(query, (mom_id, otdb_id, task_status, task_type, specification_id), fetch=FETCH_ONE).get('id')
        if commit:
            self.commit()
        return id

    def deleteTask(self, task_id, commit=True):
        logger.info('deleteTask task_id=%s' % task_id)
        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''DELETE FROM resource_allocation.task
                   WHERE resource_allocation.task.id = %s;'''

        self.executeQuery(query, [task_id])
        if commit:
            self.commit()
        return self._cursor.rowcount > 0

    def updateTaskStatusForOtdbId(self, otdb_id, task_status, commit=True):
        '''converts task_status and task_type to id's in case one and/or the other are strings'''
        if task_status is not None and isinstance(task_status, str):
            #convert task_status string to task_status.id
            task_status = self.getTaskStatusId(task_status, True)

        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''UPDATE resource_allocation.task
        SET status_id = %s
        WHERE resource_allocation.task.otdb_id = %s;'''

        self.executeQuery(query, [task_status, otdb_id])
        if commit:
            self.commit()

        return self._cursor.rowcount > 0

    def updateTask(self, task_id, mom_id=None, otdb_id=None, task_status=None, task_type=None, specification_id=None, commit=True):
        '''Update the given paramenters for the task with given task_id.
        Inside the database consistency checks are made.
        When one or more claims of a task are in conflict status, then its task is set to conflict as well, and hence cannot be scheduled.
        When all claims of a task are not in conflict status anymore, then the task is set to approved, and hence it is possible the schedule the task.

        When a task is unscheduled (set to approved) then the claimed claims are set to tentative.
        '''
        task_status, task_type = self._convertTaskTypeAndStatusToIds(task_status, task_type)

        fields = []
        values = []

        if mom_id is not None :
            fields.append('mom_id')
            values.append(mom_id)

        if otdb_id is not None :
            fields.append('otdb_id')
            values.append(otdb_id)

        if task_status is not None :
            fields.append('status_id')
            values.append(task_status)

        if task_type is not None :
            fields.append('type_id')
            values.append(task_type)

        if specification_id is not None :
            fields.append('specification_id')
            values.append(specification_id)

        values.append(task_id)

        fields_str, value_placeholders_str = self._to_fields_and_value_placeholders_strings(fields)

        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''UPDATE resource_allocation.task
        SET {fields} = {value_placeholders}
        WHERE resource_allocation.task.id = {task_id_placeholder};'''.format(fields=fields_str,
                                                                             value_placeholders=value_placeholders_str,
                                                                             task_id_placeholder='%s')

        self.executeQuery(query, values)
        if commit:
            self.commit()

        return self._cursor.rowcount > 0

    def updateTaskStartEndTimes(self, task_id, starttime=None, endtime=None, commit=True):
        fields = []
        values = []

        if starttime:
            fields.append('starttime')
            values.append(starttime)

        if endtime:
            fields.append('endtime')
            values.append(endtime)

        if not fields:
            return False

        values.append(task_id)

        fields_str, value_placeholders_str = self._to_fields_and_value_placeholders_strings(fields)

        query = '''UPDATE resource_allocation.specification
        SET {fields} = {value_placeholders}
        WHERE resource_allocation.specification.id in 
        (SELECT t.specification_id FROM resource_allocation.task
         t WHERE t.id={id_placeholder});'''.format(fields=fields_str,
                                                   value_placeholders=value_placeholders_str,
                                                   id_placeholder='%s')
        self.executeQuery(query, values)
        if commit:
            self.commit()

        return self._cursor.rowcount > 0

    def getTaskPredecessorIds(self, id=None):
        query = '''SELECT * from resource_allocation.task_predecessor tp'''

        if id is not None :
            query += ' WHERE id=%s'

        items = list(self.executeQuery(query, [id] if id is not None else None, fetch=FETCH_ALL))

        predIdDict = {}
        for item in items:
            taskId = item['task_id']
            if taskId not in predIdDict:
                predIdDict[taskId] = []
            predIdDict[taskId].append(item['predecessor_id'])
        return predIdDict

    def getTaskSuccessorIds(self, id=None):
        query = '''SELECT * from resource_allocation.task_predecessor tp'''

        if id is not None:
            query += ' WHERE id=%s'

        items = list(self.executeQuery(query, [id] if id is not None else None, fetch=FETCH_ALL))

        succIdDict = {}
        for item in items:
            predId = item['predecessor_id']
            if predId not in succIdDict:
                succIdDict[predId] = []
            succIdDict[predId].append(item['task_id'])
        return succIdDict

    def getTaskPredecessorIdsForTask(self, task_id):
        query = '''SELECT * from resource_allocation.task_predecessor tp
        WHERE tp.task_id = %s;'''

        items = list(self.executeQuery(query, [task_id], fetch=FETCH_ALL))
        return [x['predecessor_id'] for x in items]

    def getTaskSuccessorIdsForTask(self, task_id):
        query = '''SELECT * from resource_allocation.task_predecessor tp
        WHERE tp.predecessor_id = %s;'''

        items = list(self.executeQuery(query, [task_id], fetch=FETCH_ALL))
        return [x['task_id'] for x in items]

    def insertTaskPredecessor(self, task_id, predecessor_id, commit=True):
        query = '''INSERT INTO resource_allocation.task_predecessor
        (task_id, predecessor_id)
        VALUES (%s, %s)
        RETURNING id;'''

        result = self.executeQuery(query, (task_id, predecessor_id), fetch=FETCH_ONE)

        if commit:
            self.commit()

        if result and 'id' in result:
            return result['id']

        return None

    def insertTaskPredecessors(self, task_id, predecessor_ids, commit=True):
        ids = [self.insertTaskPredecessor(task_id, predecessor_id, False) for predecessor_id in predecessor_ids]
        ids = [x for x in ids if x is not None]

        if commit:
            self.commit()
        return ids

    def getSpecifications(self, specification_ids = None):
        query = '''SELECT * from resource_allocation.specification'''

        conditions = []
        qargs = []

        if specification_ids is not None:
            if isinstance(specification_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(specification_ids)
            else: #assume a list/enumerable of id's
                if len(specification_ids):
                    conditions.append('id in %s')
                    qargs.append(tuple(specification_ids))

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        return list(self.executeQuery(query, qargs, fetch=FETCH_ALL))

    def getSpecification(self, specification_id):
        query = '''SELECT * from resource_allocation.specification spec
        WHERE spec.id = (%s);'''

        return self.executeQuery(query, [specification_id], fetch=FETCH_ONE)

    def insertSpecification(self, starttime, endtime, content, cluster, commit=True):
        logger.info('insertSpecification starttime=%s, endtime=%s cluster=%s' % (starttime, endtime, cluster))
        query = '''INSERT INTO resource_allocation.specification
        (starttime, endtime, content, cluster)
        VALUES (%s, %s, %s, %s)
        RETURNING id;'''

        id = self.executeQuery(query, (starttime, endtime, content, cluster), fetch=FETCH_ONE)['id']
        if commit:
            self.commit()
        return id

    def deleteSpecification(self, specification_id, commit=True):
        logger.info('deleteSpecification specification_id=%s' % (specification_id))
        query = '''DELETE FROM resource_allocation.specification
                   WHERE resource_allocation.specification.id = %s;'''

        self.executeQuery(query, [specification_id])
        if commit:
            self.commit()
        return self._cursor.rowcount > 0

    def updateSpecification(self, specification_id, starttime=None, endtime=None, content=None, cluster=None, commit=True):
        fields = []
        values = []

        if starttime:
            fields.append('starttime')
            values.append(starttime)

        if endtime:
            fields.append('endtime')
            values.append(endtime)

        if content is not None :
            fields.append('content')
            values.append(content)

        if cluster is not None :
            fields.append('cluster')
            values.append(cluster)

        values.append(specification_id)

        fields_str, value_placeholders_str = self._to_fields_and_value_placeholders_strings(fields)

        query = '''UPDATE resource_allocation.specification
        SET {fields} = {value_placeholders}
        WHERE resource_allocation.specification.id = {id_placeholder};'''.format(fields=fields_str,
                                                                                 value_placeholders=value_placeholders_str,
                                                                                 id_placeholder='%s')

        self.executeQuery(query, values)
        if commit:
            self.commit()

        return self._cursor.rowcount > 0

    def _to_fields_and_value_placeholders_strings(self, fields: collections.Iterable) -> (str, str):
        """convert a list of fields (column names) into a tuple of a comma-seperated string and a comma-seperated placeholder string
        For usage with prepared statements (postgres mogrify)"""
        fields_str = ', '.join(fields)
        value_placeholders_str = ', '.join('%s' for _ in fields)
        if len(fields) > 1:
            # for updating multiple columns, wrap the columns and values in parentheses
            fields_str = "(%s)" % fields_str
            value_placeholders_str = "(%s)" % value_placeholders_str
        return fields_str, value_placeholders_str

    def getResourceTypes(self):
        query = '''SELECT rt.*, rtu.units as unit
        from virtual_instrument.resource_type rt
        inner join virtual_instrument.unit rtu on rtu.id = rt.unit_id;
        '''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceTypeNames(self):
        return [x['name'] for x in self.getResourceTypes()]

    def getResourceTypeId(self, type_name):
        query = '''SELECT id from virtual_instrument.resource_type
                   WHERE name = %s;'''
        result = self.executeQuery(query, [type_name], fetch=FETCH_ONE)

        if result:
            return result['id']

        raise KeyError('No such type: %s Valid values are: %s' % (type_name, ', '.join(self.getResourceTypeNames())))

    def getResourceGroupTypes(self):
        query = '''SELECT * from virtual_instrument.resource_group_type;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceGroupTypeNames(self):
        return [x['name'] for x in self.getResourceGroupTypes()]

    def getResourceGroupTypeId(self, type_name):
        query = '''SELECT id from virtual_instrument.resource_group_type
                   WHERE name = %s;'''
        result = self.executeQuery(query, [type_name], fetch=FETCH_ONE)

        if result:
            return result['id']

        raise KeyError('No such type: %s Valid values are: %s' % (type_name, ', '.join(self.getResourceGroupTypeNames())))

    def getUnits(self):
        query = '''SELECT * from virtual_instrument.unit;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getUnitNames(self):
        return [x['units'] for x in self.getUnits()]

    def getUnitId(self, unit_name):
        query = '''SELECT * from virtual_instrument.unit
                   WHERE units = %s;'''
        result = self.executeQuery(query, [unit_name], fetch=FETCH_ONE)

        if result:
            return result['id']

        raise KeyError('No such unit: %s Valid values are: %s' % (unit_name, ', '.join(self.getUnitNames())))

    def getResources(self, resource_ids=None, resource_types=None, include_availability=False, claimable_capacity_lower_bound=None, claimable_capacity_upper_bound=None):
        '''get list of resources for the requested resource_ids and/or resource_types (may be None).
        By default, for each resource, no availability and total-, used- and available capacity are returned. Specify include_availability=True to get those as well.
        By default, for each resource, no claimable_capacity is returned. Specify claimable_capacity_lower_bound and claimable_capacity_upper_bound to get the claimable_capacity as well.
        :param resource_ids: only get the resources for the given ids
        :param resource_types: only get the resources for the given resource types
        :param resource_ids: when include_availability=True, also retreive the total-, used- and available capacity per resource. These number are only valid at 'now', because these numbers come from the system monitor which fill in the current situation. We can't monitor into the future.
        :param claimable_capacity_lower_bound: when claimable_capacity_lower_bound and claimable_capacity_upper_bound are given, then also get the (maximal) claimable_capacity per resource within the time window between lower- and claimable_capacity_upper_bound. The (maximal) claimable_capacity is only valid within the requested time window, and depends on the available_capacity and the peak of the claimed claimes within the time window.
        :param claimable_capacity_upper_bound: see claimable_capacity_lower_bound
        '''
        if include_availability:
            query = '''SELECT * from resource_monitoring.resource_view'''
        else:
            query = '''SELECT * from virtual_instrument.resource_view'''

        conditions = []
        qargs = []

        if resource_ids is not None:
            if isinstance(resource_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(resource_ids)
            elif resource_ids: #assume a list/enumerable of id's
                conditions.append('id in %s')
                qargs.append(tuple(resource_ids))

        if resource_types is not None:
            if isinstance(resource_types, str):
                resource_types = [resource_types]
            elif not isinstance(resource_types, collections.Iterable):
                resource_types = [resource_types]

            # convert any resource_type name to id
            resource_type_names = set([x for x in resource_types if isinstance(x, str)])
            if resource_type_names:
                resource_type_name_to_id = {x['name']:x['id'] for x in self.getResourceTypes()}
                resource_types = [resource_type_name_to_id[x] if isinstance(x, str) else x
                                  for x in resource_types]

            conditions.append('type_id in %s')
            qargs.append(tuple(resource_types))

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        resources = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))

        if claimable_capacity_lower_bound or claimable_capacity_upper_bound:
            if isinstance(claimable_capacity_lower_bound, datetime) and isinstance(claimable_capacity_upper_bound, datetime):
                claimable_capacities = self.get_resource_claimable_capacities([r['id'] for r in resources], claimable_capacity_lower_bound, claimable_capacity_upper_bound)
                for resource in resources:
                    resource['claimable_capacity'] = claimable_capacities[resource['id']]
            else:
                raise ValueError('you should supply both claimable_capacity_lower_bound and claimable_capacity_upper_bound (as datetimes)')

        if include_availability:
            # compute unaccounted-for usage,
            # which is the actual used_capacity minus the currently allocated total claim size
            # defaults to used_capacity if no currently allocated total claim size
            utcnow = datetime.utcnow()
            recent_claimed_usages = self.getResourceUsages(resource_ids=[r['id'] for r in resources],
                                                           lower_bound=utcnow-timedelta(days=7), upper_bound=utcnow,
                                                           claim_statuses=['claimed'])

            for resource in resources:
                resource['misc_used_capacity'] = resource['used_capacity']
                if resource['id'] in recent_claimed_usages and 'claimed' in recent_claimed_usages[resource['id']] and recent_claimed_usages[resource['id']]['claimed']:
                    current_claimed_usage = recent_claimed_usages[resource['id']]['claimed'][-1]
                    resource['misc_used_capacity'] = resource['used_capacity'] - current_claimed_usage['usage']

        return resources

    def get_current_resource_usage(self, resource_id, claim_status='claimed'):
        if isinstance(claim_status, str):
            claim_status_id = self.getResourceClaimStatusId(claim_status)
        else:
            claim_status_id = claim_status

        query = '''SELECT * from resource_allocation.get_current_resource_usage(%s, %s)'''
        result = self.executeQuery(query, (resource_id, claim_status_id), fetch=FETCH_ONE)

        if result is None or result.get('resource_id') is None:
            result = { 'resource_id': resource_id,
                       'status_id': claim_status_id,
                       'as_of_timestamp': datetime.utcnow(),
                       'usage': 0 }

        return result

    def get_resource_usage_at_or_before(self, resource_id, timestamp, claim_status='claimed', exactly_at=False, only_before=False):
        if isinstance(claim_status, str):
            claim_status_id = self.getResourceClaimStatusId(claim_status)
        else:
            claim_status_id = claim_status

        query = '''SELECT * from resource_allocation.get_resource_usage_at_or_before(%s, %s, %s, %s, %s, %s)'''
        result =  self.executeQuery(query, (resource_id, claim_status_id, timestamp, exactly_at, only_before, False), fetch=FETCH_ONE)

        if result is None or result.get('resource_id') is None:
            result = { 'resource_id': resource_id,
                       'status_id': claim_status_id,
                       'as_of_timestamp': timestamp,
                       'usage': 0 }
        return result

    def updateResourceAvailability(self, resource_id, active=None, available_capacity=None, total_capacity=None, commit=True):
        if active is not None:
            query = '''UPDATE resource_monitoring.resource_availability
            SET available = %s
            WHERE resource_id = %s;'''
            self.executeQuery(query, (active, resource_id))

        if available_capacity is not None and total_capacity is not None:
            query = '''UPDATE resource_monitoring.resource_capacity
            SET (available, total) = (%s, %s)
            WHERE resource_id = %s;'''
            self.executeQuery(query, (available_capacity, total_capacity, resource_id))
        elif available_capacity is not None:
            query = '''UPDATE resource_monitoring.resource_capacity
            SET available = %s
            WHERE resource_id = %s;'''
            self.executeQuery(query, (available_capacity, resource_id))
        elif total_capacity is not None:
            query = '''UPDATE resource_monitoring.resource_capacity
            SET total) = %s
            WHERE resource_id = %s;'''
            self.executeQuery(query, (total_capacity, resource_id))

        if commit:
            self.commit()
        return self._cursor.rowcount > 0

    def getResourceGroups(self):
        query = '''SELECT rg.*, rgt.name as type
        from virtual_instrument.resource_group rg
        inner join virtual_instrument.resource_group_type rgt on rgt.id = rg.type_id;
        '''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceGroupNames(self, resourceGroupTypeName):
        query = '''SELECT rg.name
        from virtual_instrument.resource_group rg
        inner join virtual_instrument.resource_group_type rgt on rgt.id = rg.type_id
        where rgt.name = %s;
        '''

        return list(self.executeQuery(query, (resourceGroupTypeName,), fetch=FETCH_ALL))

    def getResourceGroupMemberships(self):
        '''get a dict containing the resource->group and group->group relations:

           Returns dict result with:

           result["groups"]    = { id: { "resource_group_id": id,
                                         "resource_group_name": "...",
                                         "resource_group_type": "...",
                                         "child_ids": [],
                                         "parent_ids": [],
                                         "resource_ids": [] }
                                 }
           result["resources"] = { id: { "resource_id": id,
                                         "resource_name": "...",
                                         "parent_group_ids": [] }
                                 }
        '''
        query = '''select
                    prg.id as resource_group_parent_id,
                    prg.name as resource_group_parent_name,
                    crg.id as resource_group_id,
                    crg.name as resource_group_name,
                    rgt.name as resource_group_type
                    from virtual_instrument.resource_group_to_resource_group rg2rg
                    left join virtual_instrument.resource_group prg on rg2rg.parent_id = prg.id
                    inner join virtual_instrument.resource_group crg on rg2rg.child_id = crg.id
                    left join virtual_instrument.resource_group_type rgt on crg.type_id = rgt.id
        '''
        relations = self.executeQuery(query, fetch=FETCH_ALL)

        rg_items = {}
        # loop over list of relations
        # for each unique resource_group item create a dict, and add parent_ids to it
        for relation in relations:
            rg_item_id = relation['resource_group_id']
            if not rg_item_id in rg_items:
                rg_item = {k:relation[k] for k in ('resource_group_id', 'resource_group_name', 'resource_group_type')}
                rg_item['child_ids'] = []
                rg_item['parent_ids'] = []
                rg_item['resource_ids'] = []
                rg_items[rg_item_id] = rg_item

            parent_id = relation['resource_group_parent_id']
            if parent_id != None:
                rg_items[rg_item_id]['parent_ids'].append(parent_id)

        # now that we have a full list (dict.values) of rg_items...
        # add a child_id reference to each item's parent
        # this gives us a full bidirectional graph
        for rg_item in list(rg_items.values()):
            parentIds = rg_item['parent_ids']
            rg_item_id = rg_item['resource_group_id']
            for parentId in parentIds:
                if parentId in rg_items:
                    parentNode = rg_items[parentId]
                    parentNode['child_ids'].append(rg_item_id)

        query = '''select
                    prg.id as resource_group_parent_id,
                    prg.name as resource_group_parent_name,
                    cr.id as resource_id,
                    cr.name as resource_name
                    from virtual_instrument.resource_to_resource_group r2rg
                    left join virtual_instrument.resource_group prg on r2rg.parent_id = prg.id
                    inner join virtual_instrument.resource cr on r2rg.child_id = cr.id
        '''
        relations = self.executeQuery(query, fetch=FETCH_ALL)

        r_items = {}
        # loop over list of relations
        # for each unique resource item create a dict, and add parent_ids to it
        for relation in relations:
            r_item_id = relation['resource_id']
            if not r_item_id in r_items:
                r_item = {k:relation[k] for k in ('resource_id', 'resource_name')}
                r_item['parent_group_ids'] = []
                r_items[r_item_id] = r_item

            parent_id = relation['resource_group_parent_id']
            if parent_id != None and parent_id in rg_items:
                r_items[r_item_id]['parent_group_ids'].append(parent_id)
                rg_items[parent_id]['resource_ids'].append(r_item_id)

        result = {'groups': rg_items, 'resources': r_items}

        return result

    def getResourceClaimPropertyTypes(self):
        query = '''SELECT * from resource_allocation.resource_claim_property_type;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceClaimPropertyTypeNames(self):
        return [x['name'] for x in self.getResourceClaimPropertyTypes()]

    def getResourceClaimPropertyTypeId(self, type_name):
        query = '''SELECT id from resource_allocation.resource_claim_property_type
                   WHERE name = %s;'''
        result = self.executeQuery(query, [type_name], fetch=FETCH_ONE)

        if result:
            return result['id']

        raise KeyError('No such resource_claim_property_type: %s Valid values are: %s' % (type_name, ', '.join(self.getResourceClaimPropertyTypeNames())))

    def getResourceClaimPropertyIOTypes(self):
        query = '''SELECT * from resource_allocation.resource_claim_property_io_type;'''

        return list(self.executeQuery(query, fetch=FETCH_ALL))

    def getResourceClaimPropertyIOTypeNames(self):
        return [x['name'] for x in self.getResourceClaimPropertyIOTypes()]

    def getResourceClaimPropertyIOTypeId(self, io_type_name):
        query = '''SELECT id from resource_allocation.resource_claim_property_io_type
                   WHERE name = %s;'''
        result = self.executeQuery(query, [io_type_name], fetch=FETCH_ONE)

        if result:
            return result['id']

        raise KeyError('No such resource_claim_property_io_type: %s Valid values are: %s' % (io_type_name, ', '.join(self.getResourceClaimPropertyIOTypeNames())))

    def getResourceClaimProperties(self, claim_ids=None, task_id=None):
        query = '''SELECT rcpv.id, rcpv.resource_claim_id, rcpv.value, rcpv.type_id, rcpv.type_name, rcpv.io_type_id, rcpv.io_type_name, sap.number as sap_nr
                   FROM resource_allocation.resource_claim_property_view rcpv
                   LEFT JOIN resource_allocation.sap sap on rcpv.sap_id = sap.id'''

        conditions = []
        qargs = []

        if claim_ids is not None:
            if isinstance(claim_ids, int): # just a single id
                conditions.append('rcpv.resource_claim_id = %s')
                qargs.append(claim_ids)
            else: #assume a list/enumerable of id's
                conditions.append('rcpv.resource_claim_id in %s')
                qargs.append(tuple(claim_ids))

        if task_id is not None:
            query += ' JOIN resource_allocation.resource_claim rc on rc.id = rcpv.resource_claim_id'
            conditions.append('rc.task_id = %s')
            qargs.append(task_id)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        properties = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))
        for p in properties:
            if p['sap_nr'] is None:
                del p['sap_nr']

        return properties

    def insertResourceClaimProperty(self, claim_id, property_type, value, io_type, commit=True):
        return self.insertResourceClaimProperties([(claim_id, property_type, value, io_type)], commit)

    def insertResourceClaimProperties(self, props, commit=True):
        if not props:
            return []

        # props is a list of tuples
        # each tuple prop is encoded as: (claim_id, type, value, io_type, sap_nr)
        #                         index: (0       , 1   , 2    , 3      , 4     )

        # first insert unique sap numbers
        claim_sap_nrs = list(set([(p[0], p[4]) for p in props if p[4] is not None]))
        sap_ids = self.insertSAPNumbers(claim_sap_nrs, False)

        if sap_ids == None:
            return None

        # make sap_nr to sap_id mapping per claim_id
        claim_id2sap_nr2sap_id = {}
        for claim_sap_nr,sap_id in zip(claim_sap_nrs, sap_ids):
            claim_id = claim_sap_nr[0]
            sap_nr = claim_sap_nr[1]
            if claim_id not in claim_id2sap_nr2sap_id:
                claim_id2sap_nr2sap_id[claim_id] = {}
            claim_id2sap_nr2sap_id[claim_id][sap_nr] = sap_id

        logger.info('insertResourceClaimProperties inserting %d properties' % len(props))

        # convert all property type strings to id's
        type_strings = set([p[1] for p in props if isinstance(p[1], str)])
        type_string2id = {t:self.getResourceClaimPropertyTypeId(t) for t in type_strings}

        # convert all property io_type strings to id's
        io_type_strings = set([p[3] for p in props if isinstance(p[3], str)])
        io_type_string2id = {t:self.getResourceClaimPropertyIOTypeId(t) for t in io_type_strings}

        # finally we have all the info we need,
        # so we can build the bulk property insert query
        insert_values = ','.join(self._cursor.mogrify('(%s, %s, %s, %s, %s)',
                                                     (p[0],
                                                      type_string2id[p[1]] if
                                                      isinstance(p[1], str) else p[1],
                                                      p[2],
                                                      io_type_string2id[p[3]] if
                                                      isinstance(p[3], str) else p[3],
                                                      claim_id2sap_nr2sap_id[p[0]].get(p[4]) if
                                                      p[0] in claim_id2sap_nr2sap_id else None)).decode('utf-8')
                                                     for p in props)

        query = '''INSERT INTO resource_allocation.resource_claim_property
        (resource_claim_id, type_id, value, io_type_id, sap_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        ids = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in ids if x < 0]:
            logger.error("One or more properties could not be inserted. Rolling back.")
            self.rollback()
            return None

        if commit:
            self.commit()
        return ids

    def insertSAPNumbers(self, sap_numbers, commit=True):
        if not sap_numbers:
            return []

        logger.info('insertSAPNumbers inserting %d sap numbers' % len(sap_numbers))

        insert_values = ','.join(self._cursor.mogrify('(%s, %s)', rcid_sapnr).decode('utf-8') for rcid_sapnr in sap_numbers)

        query = '''INSERT INTO resource_allocation.sap
        (resource_claim_id, number)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        sap_ids = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in sap_ids if x < 0]:
            logger.error("One or more sap_nr's could not be inserted. Rolling back.")
            self.rollback()
            return None

        if commit:
            self.commit()

        return sap_ids

    def getResourceClaims(self, claim_ids=None, lower_bound=None, upper_bound=None, resource_ids=None, task_ids=None,
                          status=None, resource_type=None, extended=False, include_properties=False):
        extended |= resource_type is not None
        query = '''SELECT * from %s''' % ('resource_allocation.resource_claim_extended_view' if extended else 'resource_allocation.resource_claim_view')

        if lower_bound and not isinstance(lower_bound, datetime):
            lower_bound = None

        if upper_bound and not isinstance(upper_bound, datetime):
            upper_bound = None

        if resource_type is not None and isinstance(resource_type, str):
            #convert resource_type string to resource_type.id
            resource_type = self.getResourceTypeId(resource_type)

        conditions = []
        qargs = []

        if status is not None:
            def _claimStatusId(s):
                #convert status string to status.id, if it is a string
                return self.getResourceClaimStatusId(s) if isinstance(s, str) else s
            if isinstance(status, (int, str)): # just a single id
                conditions.append('status_id = %s')
                #convert status string to status.id, if it is a string
                qargs.append(_claimStatusId(status))
            else: #assume a list/enumerable of id's
                conditions.append('status_id in %s')
                #convert status string to status.id, if they are strings
                qargs.append(tuple([_claimStatusId(s) for s in status]))

        if claim_ids is not None:
            if isinstance(claim_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(claim_ids)
            else: #assume a list/enumerable of id's
                conditions.append('id in %s')
                qargs.append(tuple(claim_ids))

        if lower_bound:
            conditions.append('endtime >= %s')
            qargs.append(lower_bound)

        if upper_bound:
            conditions.append('starttime <= %s')
            qargs.append(upper_bound)

        if resource_ids is not None:
            if isinstance(resource_ids, int): # just a single id
                conditions.append('resource_id = %s')
                qargs.append(resource_ids)
            else: #assume a list/enumerable of id's
                conditions.append('resource_id in %s')
                qargs.append(tuple(resource_ids))

        if task_ids is not None:
            #if task_id is normal positive we do a normal inclusive filter
            #if task_id is negative we do an exclusive filter
            if isinstance(task_ids, int): # just a single id
                conditions.append('task_id = %s' if task_ids >= 0 else 'task_id != %s')
                qargs.append(abs(task_ids))
            else:
                inclusive_task_ids = [t for t in task_ids if t >= 0]
                exclusive_task_ids = [-t for t in task_ids if t < 0]

                if inclusive_task_ids:
                    conditions.append('task_id in %s')
                    qargs.append(tuple(inclusive_task_ids))

                if exclusive_task_ids:
                    conditions.append('task_id not in %s')
                    qargs.append(tuple(exclusive_task_ids))

        if resource_type is not None and extended:
            conditions.append('resource_type_id = %s')
            qargs.append(resource_type)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        claims = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))

        if include_properties and claims:
            claimDict = {c['id']: c for c in claims}
            claim_ids = list(claimDict.keys())
            properties = self.getResourceClaimProperties(claim_ids=claim_ids)
            for p in properties:
                try:
                    claim = claimDict[p['resource_claim_id']]
                    del p['resource_claim_id']
                    if 'sap_nr' in p:
                        if not 'saps' in claim:
                            claim['saps'] = {}
                        if not p['sap_nr'] in claim['saps']:
                            claim['saps'][p['sap_nr']] = []
                        claim['saps'][p['sap_nr']].append(p)
                        del p['sap_nr']
                    else:
                        if not 'properties' in claim:
                            claim['properties'] = []
                        claim['properties'].append(p)
                except KeyError:
                    pass

            for claim in claims:
                if 'saps' in claim:
                    claim['saps'] = [{'sap_nr':sap_nr, 'properties':props} for sap_nr, props in list(claim['saps'].items())]

        return claims

    def getResourceClaim(self, id):
        query = '''SELECT * from resource_allocation.resource_claim_view rcv
        where rcv.id = %s;
        '''
        result = self.executeQuery(query, [id], fetch=FETCH_ONE)

        return dict(result) if result else None

    def insertResourceClaim(self, resource_id, task_id, starttime, endtime, claim_size, username,
                            user_id, used_rcus=None, properties=None, commit=True):
        '''
        insert one resource claim for the given task
        :param resource_id: id of the resource which is claimed
        :param task_id: id of the task for which this claim is made
        :param starttime: when should this claim start? (can be different than the task's starttime)
        :param endtime: when should this claim end? (can be different than the task's endtime)
        :param claim_size: how much do you want to claim?
        :param username: the name of the user who inserts these claims (to link the this insert action to a user) (Not used yet, fill in any name)
        :param user_id: the id of the user who inserts these claims (to link the this insert action to a user) (Not used yet, fill in any name)
        :param used_rcus: ??
        :param properties: optional, <list of tuples> #see insertResourceClaimProperties
        :param commit: do commit, or keep transaction open.
        :return: id of the inserted claim.
        '''
        # for code re-use:
        # put the one claim in a list
        # and do a bulk insert of the one-item-list
        claim = {'resource_id': resource_id,
                 'starttime': starttime,
                 'endtime': endtime,
                 'claim_size': claim_size,
                 'used_rcus': used_rcus}

        if properties:
            claim['properties'] = properties

        result = self.insertResourceClaims(task_id, [claim], username, user_id, commit)
        if result:
            return result[0]
        return None

    def insertResourceClaims(self, task_id, claims, username, user_id, commit=True):
        '''bulk insert of a list of resource claims for a task(_id). All claims are inserted with status tentative.
        :param task_id: the task(_id) for which these claims are inserted. Each claim always belongs to one task, and one task only.
        :param claims: list of claims. each claim is defined by the following dict: {'resource_id': <int>,
                                                                                     'starttime': <datetime>,
                                                                                     'endtime': <datetime>,
                                                                                     'claim_size': <int>,
                                                                                     'used_rcus': <??>,
                                                                                     'properties': <list of tuples> #see insertResourceClaimProperties
                                                                                     }
        :param username: the name of the user who inserts these claims (to link the this insert action to a user) (Not used yet, fill in any name)
        :param userid: the id of the user who inserts these claims (to link the this insert action to a user) (Not used yet, fill in any int)
        :return: list of ints with the new claim id's

        claims is a list of dicts. Each dict is a claim for one resource containing the fields:
        starttime, endtime, status, claim_size
        '''
        logger.info('insertResourceClaims for task_id=%d with %d claim(s)' % (task_id, len(claims)))

        status_strings = set([c.get('status', 'tentative') for c in claims if isinstance(c.get('status', 'tentative'), str)])
        if status_strings:
            status_string2id = {s:self.getResourceClaimStatusId(s) for s in status_strings}
            for c in claims:
                if isinstance(c.get('status', 'tentative'), str):
                    c['status_id'] = status_string2id[c.get('status', 'tentative')]
                elif isinstance(c['status'], int):
                    c['status_id'] = c['status']

        try:
            claim_values = [(c['resource_id'], task_id, c['starttime'], c['endtime'],
                            c.get('status_id', 0), c['claim_size'], c.get('used_rcus'),
                            username, user_id) for c in claims]
        except Exception as e:
            logger.error("Invalid claim dict, rolling back. %s" % e)
            self.rollback()
            return []

        try:
            # use psycopg2 mogrify to parse and build the insert values
            # this way we can insert many values in one insert query, returning the id's of each inserted row.
            # this is much faster than psycopg2's executeMany method
            insert_values = ','.join(self._cursor.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s)", cv).decode("utf-8") for cv in claim_values)
        except Exception as e:
            logger.error("Invalid input, rolling back: %s\n%s" % (claim_values, e))
            self.rollback()
            return []

        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''INSERT INTO resource_allocation.resource_claim
        (resource_id, task_id, starttime, endtime, status_id, claim_size, used_rcus, username, user_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        claimIds = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if not claimIds or [x for x in claimIds if x < 0]:
            logger.error("One or more claims could not be inserted. Rolling back.")
            self.rollback()
            return []

        # gather all properties for all claims
        # store them as list of (claim_id, prop_type, prop_value, io_type, sap_nr) tuples
        properties = []
        for claim_id, claim in zip(claimIds, claims):
            if 'properties' in claim and len(claim['properties']) > 0:
                claim_props = [(claim_id, p['type'], p['value'], p.get('io_type', 0), p.get('sap_nr')) for p in claim['properties']]
                properties += claim_props

        if properties:
            property_ids = self.insertResourceClaimProperties(properties, False)
            if property_ids == None:
                return []

        if commit:
            self.commit()

        logger.info('inserted %d resource claim(s) for task_id=%d' % (len(claimIds), task_id))
        return claimIds

    def deleteResourceClaim(self, resource_claim_id, commit=True):
        self.deleteResourceClaims(resource_claim_ids=[resource_claim_id], commit=commit)

    def deleteResourceClaims(self, resource_claim_ids, commit=True):
        if resource_claim_ids:
            query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                    '''DELETE FROM resource_allocation.resource_claim
                       WHERE resource_allocation.resource_claim.id in %s;'''

            self.executeQuery(query, [tuple(resource_claim_ids)])
            if commit:
                self.commit()
            return self._cursor.rowcount > 0
        return True

    def deleteResourceClaimForTask(self, task_id, commit=True):
        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''DELETE FROM resource_allocation.resource_claim
                   WHERE resource_allocation.resource_claim.task_id = %s;'''

        self.executeQuery(query, (task_id,))
        if commit:
            self.commit()
        return self._cursor.rowcount > 0

    def updateResourceClaim(self, resource_claim_id, resource_id=None, task_id=None, starttime=None, endtime=None,
                            status=None, claim_size=None, username=None, used_rcus=None, user_id=None,
                            commit=True):
        return self.updateResourceClaims([resource_claim_id], None, None, resource_id, task_id, starttime, endtime, status,
                                         claim_size, username, used_rcus, user_id, commit)

    def updateResourceClaims(self, where_resource_claim_ids=None, where_task_ids=None, where_resource_types=None,
                             resource_id=None, task_id=None, starttime=None, endtime=None,
                             status=None, claim_size=None, username=None, used_rcus=None, user_id=None,
                             commit=True):
        '''Update the given paramenters on all resource claims given/delimited by where_resource_claim_ids and/or where_task_ids.
        Inside the database consistency checks are made. For example, in case you want to set a claim's status to 'claimed', but it does not fit in the free capacity of the claim's resource, then the claim goes to 'conflict'.

        A claim fits, (and hence can be claimed) only if the claim_size < resource.free_capacity within the claims time window.
        When a claim is released (claimed->tentative) then all overlapping conflicting claims are checked again if they fit because there is more capacity available.
        When a claim is claimed (tentative->claimed) then all overlapping tentative claims are checked again if they still fit because there is less capacity available.

        When one or more claims of a task are in conflict status, then its task is set to conflict as well, and hence cannot be scheduled.
        When all claims of a task are not in conflict status anymore, then the task is set to approved, and hence it is possible the schedule the task.
        '''
        status_id = status
        if status is not None and isinstance(status, str):
            #convert status string to status.id
            status_id = self.getResourceClaimStatusId(status)

        fields = []
        values = []

        if resource_id is not None:
            fields.append('resource_id')
            values.append(resource_id)

        if task_id is not None:
            fields.append('task_id')
            values.append(task_id)

        if starttime:
            fields.append('starttime')
            values.append(starttime)

        if endtime:
            fields.append('endtime')
            values.append(endtime)

        if status_id is not None:
            fields.append('status_id')
            values.append(status_id)

        if claim_size is not None:
            fields.append('claim_size')
            values.append(claim_size)

        if username is not None:
            fields.append('username')
            values.append(username)

        if used_rcus is not None:
            fields.append('used_rcus')
            values.append(used_rcus)

        if user_id is not None:
            fields.append('user_id')
            values.append(user_id)

        fields_str, value_placeholders_str = self._to_fields_and_value_placeholders_strings(fields)

        # updating the resource_claim table causes many trigger functions to do more updates/inserts/deletes on the
        # resource_claim
        query = '''LOCK TABLE resource_allocation.resource_claim, resource_allocation.resource_usage, resource_allocation.task IN EXCLUSIVE MODE; '''\
                '''UPDATE resource_allocation.resource_claim SET {fields} = {value_placeholders}'''.format(
            fields=fields_str, value_placeholders=value_placeholders_str)

        if where_resource_claim_ids is None and where_task_ids is None:
            raise ValueError('please provide either "where_resource_claim_ids" and/or "where_task_ids" argument for updateResourceClaims')

        conditions = []
        condition_values = []

        if where_resource_claim_ids is not None:
            if isinstance(where_resource_claim_ids, int): # just a single id
                conditions.append('id = %s')
                condition_values.append(where_resource_claim_ids)
            elif len(where_resource_claim_ids): #assume a list/enumerable of id's
                conditions.append('id in %s')
                condition_values.append(tuple(where_resource_claim_ids))

        if where_task_ids is not None:
            if isinstance(where_task_ids, int): # just a single id
                conditions.append('task_id = %s')
                condition_values.append(where_task_ids)
            elif isinstance(where_task_ids, collections.abc.Iterable): #assume a list/enumerable of id's
                if len(where_task_ids) == 1:
                    # faster
                    conditions.append('task_id = %s')
                    condition_values.append(where_task_ids[0])
                else:
                    conditions.append('task_id in %s')
                    condition_values.append(tuple(where_task_ids))
            else:
                raise RADBError("Invalid type for 'where_task_ids': %s %s" % (type(where_task_ids), where_task_ids))

        if where_resource_types is not None:
            if isinstance(where_resource_types, str) or isinstance(where_resource_types, int):
                where_resource_types = [where_resource_types]
            elif not isinstance(where_resource_types, collections.Iterable):
                where_resource_types = [where_resource_types]

            # convert any resource_type name to id
            resource_type_names = set([x for x in where_resource_types if isinstance(x, str)])
            if resource_type_names:
                resource_type_name_to_id = {x['name']:x['id'] for x in self.getResourceTypes()}
                where_resource_type_ids = [resource_type_name_to_id[x] if isinstance(x, str) else x
                                           for x in where_resource_types]
            else:
                where_resource_type_ids = [x for x in where_resource_types]

            conditions.append('resource_id in (SELECT r.id FROM virtual_instrument.resource r WHERE r.type_id in %s)')
            condition_values.append(tuple(where_resource_type_ids))

        query += ' WHERE ' + ' AND '.join(conditions)


        self.executeQuery(query, values + condition_values)

        if commit:
            self.commit()

        if self._cursor.rowcount == 0:
            # nothing updated, so let's check if there was nothing to update, or that the update failed
            query = 'SELECT count(id) FROM resource_allocation.resource_claim WHERE ' + ' AND '.join(conditions)
            return self.executeQuery(query, condition_values, fetch=FETCH_ONE).get('count', 0) == 0

        return self._cursor.rowcount > 0


    def updateTaskAndResourceClaims(self, task_id, starttime=None, endtime=None, task_status=None, claim_status=None, username=None, used_rcus=None, user_id=None, where_resource_types=None, commit=True):
        '''combination of updateResourceClaims and updateTask in one transaction'''
        updated = True

        if (starttime or endtime or claim_status is not None or
            username is not None or used_rcus is not None or user_id is not None):
            # update the claims as well
            updated &= self.updateResourceClaims(where_task_ids=task_id,
                                                 where_resource_types=where_resource_types,
                                                 starttime=starttime,
                                                 endtime=endtime,
                                                 status=claim_status,
                                                 username=username,
                                                 used_rcus=used_rcus,
                                                 user_id=user_id,
                                                 commit=False)

        if starttime or endtime:
            updated &= self.updateTaskStartEndTimes(task_id, starttime=starttime, endtime=endtime, commit=False)

        if task_status is not None :
            updated &= self.updateTask(task_id, task_status=task_status, commit=False)

        if commit:
            self.commit()

        return updated

    def get_overlapping_claims(self, claim_id, claim_status='claimed'):
        '''returns a list of claimed claims which overlap with given claim and which prevent the given claim to be claimed (cause it to be in conflict)'''
        if isinstance(claim_status, str):
            claim_status_id = self.getResourceClaimStatusId(claim_status)
        else:
            claim_status_id = claim_status

        query = '''SELECT * from resource_allocation.get_overlapping_claims(%s, %s)'''
        return list(self.executeQuery(query, (claim_id, claim_status_id), fetch=FETCH_ALL))

    def get_overlapping_tasks(self, claim_id, claim_status='claimed'):
        '''returns a list of tasks which overlap with given claim(s) and which prevent the given claim(s) to be claimed (cause it to be in conflict)'''
        conflicting_claims = self.get_overlapping_claims(claim_id, claim_status)
        task_ids = set([c['task_id'] for c in conflicting_claims])
        return self.getTasks(task_ids=task_ids)

    def get_max_resource_usage_between(self, resource_id, lower_bound, upper_bound, claim_status='claimed'):
        if isinstance(claim_status, str):
            claim_status_id = self.getResourceClaimStatusId(claim_status)
        else:
            claim_status_id = claim_status

        result = {'usage': 0, 'status_id': claim_status_id, 'as_of_timestamp': lower_bound, 'resource_id': resource_id}

        query = '''SELECT * from resource_allocation.get_max_resource_usage_between(%s, %s, %s, %s)'''
        qresult = self.executeQuery(query, (resource_id, claim_status_id, lower_bound, upper_bound), fetch=FETCH_ONE)

        if qresult and qresult.get('usage') is not None:
            result['usage'] = qresult.get('usage')
            result['as_of_timestamp'] = max(lower_bound, qresult.get('as_of_timestamp'))
        return result

    def get_resource_claimable_capacity(self, resource_id, lower_bound, upper_bound):
        '''get the claimable capacity for the given resource within the timewindow given by lower_bound and upper_bound.
        this is the resource's available capacity (total-used) minus the maximum allocated usage in that timewindow.'''
        if resource_id is None or lower_bound is None or upper_bound is None:
            raise ValueError('resource_id and/or lower_bound and/or upper_bound cannot be None')

        query = '''SELECT * from resource_allocation.get_resource_claimable_capacity_between(%s, %s, %s)'''
        qresult = self.executeQuery(query, (resource_id, lower_bound, upper_bound), fetch=FETCH_ONE)
        if qresult:
            return qresult.get('get_resource_claimable_capacity_between', 0)
        else:
            return 0

    def get_resource_claimable_capacities(self, resource_ids, lower_bound, upper_bound):
        '''get the claimable capacity for the given resource within the timewindow given by lower_bound and upper_bound.
        this is the resource's available capacity (total-used) minus the maximum allocated usage in that timewindow.'''
        if resource_ids is None or lower_bound is None or upper_bound is None:
            raise ValueError('resource_ids and/or lower_bound and/or upper_bound cannot be None')

        query = '''SELECT * from resource_allocation.get_resource_claimable_capacities_between(%s, %s, %s)'''
        qresult = self.executeQuery(query, (resource_ids, lower_bound, upper_bound), fetch=FETCH_ONE)
        if qresult:
            claimable_capacities = qresult.get('get_resource_claimable_capacities_between', [])
            assert len(resource_ids) == len(claimable_capacities)
            return {rid:cap for rid,cap in zip(resource_ids, claimable_capacities)}
        else:
            return {}

    def rebuild_resource_usages_from_claims(self, resource_id=None, claim_status=None):
        '''(re)builds the resource_usages table from all currently known resource_claims'''
        if isinstance(claim_status, str):
            claim_status_id = self.getResourceClaimStatusId(claim_status)
        else:
            claim_status_id = claim_status

        if resource_id is None and claim_status_id is None:
            self.executeQuery('SELECT * from resource_allocation.rebuild_resource_usages_from_claims()', fetch=FETCH_NONE)
        elif claim_status_id is None:
            self.executeQuery('SELECT * from resource_allocation.rebuild_resource_usages_from_claims_for_resource(%s)', (resource_id,), fetch=FETCH_NONE)
        else:
            self.executeQuery('SELECT * from resource_allocation.rebuild_resource_usages_from_claims_for_resource_of_status(%s, %s)', (resource_id, claim_status_id), fetch=FETCH_NONE)

    def insertOrUpdateSpecificationAndTask(self, mom_id, otdb_id, task_status, task_type, starttime, endtime, content, cluster, commit=True):
        '''
        Insert a new specification and task in one transaction.
        Removes resource_claims for existing task with same otdb_id if present in the same transaction.
        '''
        try:
            existing_task = self.getTask(otdb_id=otdb_id)
            if existing_task is None and mom_id is not None:
                existing_task = self.getTask(mom_id=mom_id)

            if existing_task is not None:
                # delete any existing resource_claims and update the properties of the spec and task
                logger.info("insertOrUpdateSpecificationAndTask: a task with the same mom/otdb id is already known: existing_task=%s. Clearing current resource claims (if any) and updating specification and task.", existing_task)
                specId = existing_task['specification_id']
                taskId = existing_task['id']
                self.deleteResourceClaimForTask(existing_task['id'], False)
                self.updateSpecification(specId, starttime=starttime, endtime=endtime, content=content, cluster=cluster, commit=False)
                self.updateTask(taskId, mom_id=mom_id, otdb_id=otdb_id, task_status=task_status, task_type=task_type, commit=False)
            else:
                specId = self.insertSpecification(starttime, endtime, content, cluster, False)
                taskId = self.insertTask(mom_id, otdb_id, task_status, task_type, specId, False)

            if commit:
                self.commit()
            return {'inserted': True, 'specification_id': specId, 'task_id': taskId}
        except Exception as e:
            logger.error(e)
            self.rollback()

        return {'inserted': False, 'specification_id': None, 'task_id': None}

    def getTaskConflictReasons(self, task_ids=None):
        query = '''SELECT * from resource_allocation.task_conflict_reason_view'''

        conditions = []
        qargs = []

        if task_ids is not None:
            if isinstance(task_ids, int): # just a single id
                conditions.append('task_id = %s')
                qargs.append(task_ids)
            else: #assume a list/enumerable of id's
                conditions.append('task_id in %s')
                qargs.append(tuple(task_ids))

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        conflict_reasons = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))
        return conflict_reasons

    def insertTaskConflicts(self, task_id, conflict_reason_ids, commit=True):
        if not self._cursor:
            self._connect()

        insert_values = ','.join(self._cursor.mogrify('(%s, %s)', (task_id, cr_id)).decode('utf-8') for cr_id in conflict_reason_ids)

        query = '''INSERT INTO resource_allocation.task_conflict_reason
        (task_id, conflict_reason_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        ids = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in ids if x < 0]:
            logger.error("One or more conflict reasons could not be inserted. Rolling back.")
            self.rollback()
            return None

        if commit:
            self.commit()
        return ids


    def getResourceClaimConflictReasons(self, claim_ids=None, resource_ids=None, task_ids=None):
        query = '''SELECT * from resource_allocation.resource_claim_conflict_reason_view'''

        conditions = []
        qargs = []

        if claim_ids is not None:
            if isinstance(claim_ids, int): # just a single id
                conditions.append('id = %s')
                qargs.append(claim_ids)
            else: #assume a list/enumerable of id's
                conditions.append('id in %s')
                qargs.append(tuple(claim_ids))

        if resource_ids is not None:
            if isinstance(resource_ids, int): # just a single id
                conditions.append('resource_id = %s')
                qargs.append(resource_ids)
            else: #assume a list/enumerable of id's
                conditions.append('resource_id in %s')
                qargs.append(tuple(resource_ids))

        if task_ids is not None:
            if isinstance(task_ids, int): # just a single id
                conditions.append('task_id = %s')
                qargs.append(task_ids)
            else: #assume a list/enumerable of id's
                conditions.append('task_id in %s')
                qargs.append(tuple(task_ids))

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        conflict_reasons = list(self.executeQuery(query, qargs, fetch=FETCH_ALL))
        return conflict_reasons

    def insertResourceClaimConflicts(self, claim_id, conflict_reason_ids, commit=True):
        if not self._cursor:
            self._connect()

        insert_values = ','.join(self._cursor.mogrify('(%s, %s)', (claim_id, cr_id)).decode('utf-8') for cr_id in conflict_reason_ids)

        query = '''INSERT INTO resource_allocation.resource_claim_conflict_reason
        (resource_claim_id, conflict_reason_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        ids = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in ids if x < 0]:
            logger.error("One or more conflict reasons could not be inserted. Rolling back.")
            self.rollback()
            return None

        if commit:
            self.commit()
        return ids

    def getResourceUsages(self, lower_bound=None, upper_bound=None, resource_ids=None, claim_statuses=None):
        """ Get the resource usages over time within the optionally given time window, resource_ids,
and/or claim_statuses.
        :param lower_bound: filter for usages newer than lower_bound
        :param upper_bound: filter for usages older than upper_bound
        :param resource_ids: filter for usages for the given resource id(s)
        :param claim_statuses: filter for usages for the given claim status(es)
        :return: a nested dict with resource_id at the first level, then claim_status(name) at the second level, and then a list of time ordered usages.
        """
        usages_per_resource = {}
        query = '''SELECT * from resource_allocation.resource_usage'''

        conditions = []
        qargs = []

        if lower_bound is not None:
            conditions.append('as_of_timestamp >= %s')
            qargs.append(lower_bound)

        if upper_bound is not None:
            conditions.append('as_of_timestamp <= %s')
            qargs.append(upper_bound)

        if resource_ids is not None:
            if isinstance(resource_ids, int): # just a single id
                conditions.append('resource_id = %s')
                qargs.append(resource_ids)
                usages_per_resource[resource_ids] = {} # append default empty result dict
            elif resource_ids: #assume a list/enumerable of id's
                conditions.append('resource_id in %s')
                qargs.append(tuple(resource_ids))
                for resource_id in resource_ids:
                    usages_per_resource[resource_id] = {} # append default empty result dict

        if claim_statuses is not None:
            if isinstance(claim_statuses, str):
                claim_statuses = [claim_statuses]
            elif not isinstance(claim_statuses, collections.Iterable):
                claim_statuses = [claim_statuses]

            # convert any claim_status name to id
            claim_status_names = set([x for x in claim_statuses if isinstance(x, str)])
            if claim_status_names:
                claim_status_name_to_id = {x['name']:x['id'] for x in self.getResourceClaimStatuses()}
                claim_status_ids = [claim_status_name_to_id[x] if isinstance(x, str) else x
                                    for x in claim_status_names]

            conditions.append('status_id in %s')
            qargs.append(tuple(claim_status_ids))

        for rcs in self.getResourceClaimStatuses():
            for resource_id, result_dict in usages_per_resource.items():
                result_dict[rcs['id']] = [] # add default empty list for each requested resource_id for each known status

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY as_of_timestamp'

        usages = self.executeQuery(query, qargs, fetch=FETCH_ALL)

        for usage in usages:
            resource_id = usage['resource_id']
            if resource_id not in usages_per_resource:
                usages_per_resource[resource_id] = {}

            status_id = usage['status_id']
            if status_id not in usages_per_resource[resource_id]:
                usages_per_resource[resource_id][status_id] = []

            usages_per_resource[resource_id][status_id].append({'as_of_timestamp':usage['as_of_timestamp'], 'usage':usage['usage']})

        # replace resource claim status id's by names
        for resource_id, resource_usages_per_status in list(usages_per_resource.items()):
            for status_id, usages in list(resource_usages_per_status.items()):
                resource_usages_per_status[self.getResourceClaimStatusName(status_id)] = usages
                del resource_usages_per_status[status_id]

        return usages_per_resource


    def getResourceAllocationConfig(self, sql_like_name_pattern=None):
        ''' The argument sql_like_name_pattern can be e.g. 'max_fill_ratio_%'
        '''
        query = "SELECT name, value FROM resource_allocation.config"
        if sql_like_name_pattern is not None:
            query += " WHERE name LIKE '%s'" % sql_like_name_pattern

        return list(self.executeQuery(query, fetch=FETCH_ALL))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='runs some test queries on the radb')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")
    (options, args) = parser.parse_args()

    dbcreds = dbcredentials.parse_options(options)

    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    db = RADatabase(dbcreds=dbcreds)

    def resultPrint(method):
        print('\n-- ' + str(method.__name__) + ' --')
        print('\n'.join([str(x) for x in method()]))

    resultPrint(db.getTaskStatuses)
    resultPrint(db.getTaskStatusNames)
    resultPrint(db.getTaskTypes)
    resultPrint(db.getTaskTypeNames)
    resultPrint(db.getResourceClaimStatuses)
    resultPrint(db.getResourceClaimStatusNames)
    resultPrint(db.getUnits)
    resultPrint(db.getUnitNames)
    resultPrint(db.getResourceTypes)
    resultPrint(db.getResourceTypeNames)
    resultPrint(db.getResourceGroupTypes)
    resultPrint(db.getResourceGroupTypeNames)
    resultPrint(db.getResources)
    resultPrint(db.getResourceGroups)
    resultPrint(db.getResourceGroupNames('cluster'))
    resultPrint(db.getResourceGroupMemberships)
    resultPrint(db.getTasks)
    resultPrint(db.getSpecifications)
    resultPrint(db.getResourceClaims)
    resultPrint(db.getResourceClaimProperties)
    resultPrint(db.getResourceAllocationConfig)

