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
#
# $Id$

import datetime


class RADB_mock:
    def __init__(self):
        now = datetime.datetime.utcnow()
        now = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)  # strip milliseconds

        # 2 nodes:
        #   node1 has bandwidth and storage for mount points /d1-qzy, /d2-qzy
        #   node2 has bandwidth and (inactive) storage for mount point /d-qzy
        self.resources = [
            {'id': 0, 'name': 'node1_bandwidth:/d1-qzy',
             'active': True,
             'total_capacity': 1000,
             'available_capacity': 1000,
             'used_capacity': 0,
             'type_id': 3, 'type_name': 'bandwidth',
             'unit_id': 3, 'unit': 'bits/second'
            },
            {'id': 1, 'name': 'node1_storage:/d1-qzy',
             'active': True,
             'total_capacity': 100,
             'available_capacity': 90,
             'used_capacity': 10,
             'type_id': 5, 'type_name': 'storage',
             'unit_id': 5, 'unit': 'bytes'
            },
            {'id': 2, 'name': 'node1_bandwidth:/d2-qzy',
             'active': True,
             'total_capacity': 2000,
             'available_capacity': 2000,
             'used_capacity': 0,
             'type_id': 3, 'type_name': 'bandwidth',
             'unit_id': 3, 'unit': 'bits/second'
            },
            {'id': 3, 'name': 'node1_storage:/d2-qzy',
             'active': True,
             'total_capacity': 200,
             'available_capacity': 180,
             'used_capacity': 20,
             'type_id': 5, 'type_name': 'storage',
             'unit_id': 5, 'unit': 'bytes'
            },
            {'id': 4, 'name': 'node2_bandwidth:/d-qzy',
             'active': True,
             'total_capacity': 2000,
             'available_capacity': 2000,
             'used_capacity': 0,
             'type_id': 3, 'type_name': 'bandwidth',
             'unit_id': 3, 'unit': 'bits/second'
            },
            {'id': 5, 'name': 'node2_storage:/d-qzy',
             'active': False,  # i.e. inactive by default
             'total_capacity': 5000,
             'available_capacity': 5000,
             'used_capacity': 0,
             'type_id': 5, 'type_name': 'storage',
             'unit_id': 5, 'unit': 'bytes'
            },

        ]

        # The root node is INSTRUMENT. Under it 1 cluster named CLUSTER with 2 nodes and the 6 resources listed above.
        # Note that node1 has 2 resource groups under it (group type 'virtual' but not annotated here) to have
        # the data1 resources under another group than the data2 resources. This is similar to the real RADB.
        self.memberships = {'resources': {0: {'resource_name': 'node1_bandwidth:/d1-qzy', 'parent_group_ids': [4], 'resource_id': 0},
                                           1: {'resource_name': 'node1_storage:/d1-qzy'  , 'parent_group_ids': [4], 'resource_id': 1},
                                           2: {'resource_name': 'node1_bandwidth:/d2-qzy', 'parent_group_ids': [5], 'resource_id': 2},
                                           3: {'resource_name': 'node1_storage:/d2-qzy'  , 'parent_group_ids': [5], 'resource_id': 3},
                                           4: {'resource_name': 'node2_bandwidth:/d-qzy' , 'parent_group_ids': [3], 'resource_id': 4},
                                           5: {'resource_name': 'node2_storage:/d-qzy'   , 'parent_group_ids': [3], 'resource_id': 5},
                                          },
                            'groups':    {0: {'resource_group_id': 0, 'parent_ids': [] , 'resource_ids': [],     'child_ids': [1]   , 'resource_group_name': 'INSTRUMENT'},
                                           1: {'resource_group_id': 1, 'parent_ids': [0], 'resource_ids': [],     'child_ids': [2, 3], 'resource_group_name': 'CLUSTER'},
                                           2: {'resource_group_id': 2, 'parent_ids': [1], 'resource_ids': [],     'child_ids': [4, 5], 'resource_group_name': 'node1'},
                                           3: {'resource_group_id': 3, 'parent_ids': [1], 'resource_ids': [4, 5], 'child_ids': []    , 'resource_group_name': 'node2'},
                                           4: {'resource_group_id': 4, 'parent_ids': [2], 'resource_ids': [0, 1], 'child_ids': []    , 'resource_group_name': 'node1-1'},
                                           5: {'resource_group_id': 5, 'parent_ids': [2], 'resource_ids': [2, 3], 'child_ids': []    , 'resource_group_name': 'node1-2'},
                                          }
                           }

        # 2 tasks
        self.tasks = [
            {'id': 1,
             'mom_id': 10,
             'otdb_id': 100,
             'starttime': now - datetime.timedelta(minutes=15),
             'endtime':   now - datetime.timedelta(minutes=5),
             'duration': 600.0,
             'type': 'observation',
             'status_id': 1000,
             'status': 'finished',
             # and more; irrelevant for test
            },
            {'id': 2,
             'mom_id': 20,
             'otdb_id': 200,
             'starttime': now - datetime.timedelta(hours=2),
             'endtime':   now - datetime.timedelta(hours=1),
             'duration': 3600.0,
             'type': 'observation',
             'status_id': 1000,
             'status': 'finished',
            },
        ]
 
        # 3 claims: 1 on the 1st task and 2 on the 2nd task
        self.claims = [
            {'id': 1,
             'task_id': 1,
             'resource_id': 3, 'resource_name': 'node1_storage:/d2-qzy',
             'resource_type_id': 5, 'resource_type_name': 'storage',
             'starttime': self.tasks[0]['starttime'],
             'endtime':   self.tasks[0]['endtime'] + datetime.timedelta(days=365),  # storage claim end time typically set to task end + 1 yr by the system
             'claim_size': 80,
             'status_id': 1, 'status': 'claimed',
            },
            {'id': 2,
             'task_id': 2,
             'resource_id': 4, 'resource_name': 'node2_bandwidth:/d-qzy',
             'resource_type_id': 3, 'resource_type_name': 'bandwidth',
             'starttime': self.tasks[1]['starttime'],
             'endtime':   self.tasks[1]['endtime'],
             'claim_size': 8,
             'status_id': 1, 'status': 'claimed',
            },
            {'id': 3,
             'task_id': 2,
             'resource_id': 5, 'resource_name': 'node2_storage:/d-qzy',
             'resource_type_id': 5, 'resource_type_name': 'storage',
             'starttime': self.tasks[1]['starttime'],
             'endtime':   self.tasks[1]['endtime'] + datetime.timedelta(days=365),  # storage claim end time typically set to task end + 1 yr by the system
             'claim_size': 3600,
             'status_id': 1, 'status': 'claimed',
            },
        ]

    def get_resources(self):
        return self.resources

    def get_memberships(self):
        return self.memberships

    def get_tasks(self):
        return self.tasks

    def get_claims(self):
        return self.claims

# RADB changes stay persistent on purpose after a test program run.
# Different test program runs are not different tests, but make up a single test, e.g. 'show, modify, show' should display the change.
# To make different tests, reinitialize this object before each new test sequence.
radb_mock = RADB_mock()

class RADBRPC_mock:

    @staticmethod
    def create(**kwargs):
        return RADBRPC_mock()

    def __init__(self, busname=None, # don't care about any of these here
                 servicename=None,
                 broker=None,
                 timeout=0):
        global radb_mock
        self.radb_mock = radb_mock
        self.is_open = True

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Do approx what the rpc service does. This is sub-optimal, because the code may go out of sync.
    # Python mock can do autospec on patched functions (we could do similar with the inspect module),
    # but that doesn't apply to this sort of implementation logic.

    def updateResourceAvailability(self, resource_id, active=None, available_capacity=None,
                                   total_capacity=None, commit=True):
        # Only implement some of the function arguments that the system under test may use
        for res in self.radb_mock.get_resources():
            if res['id'] == resource_id:
                if active is not None:
                    res['active'] = active  # data type not checked here...
                if available_capacity is not None:
                    res['available_capacity'] = available_capacity  # idem
                if total_capacity is not None:
                    res['total_capacity'] = total_capacity  # idem

                if available_capacity is not None or total_capacity is not None:
                    res['used_capacity'] = res['total_capacity'] - res['available_capacity']  # idem

                return {'updated': True, 'resource_id': resource_id}

        raise KeyError(resource_id)

    def getResources(self, resource_ids=None, resource_types=None, include_availability=False,
                     claimable_capacity_lower_bound=None, claimable_capacity_upper_bound=None):
        # Only implement some of the function arguments that the system under test may use
        resources = []
        for res in self.radb_mock.get_resources():
            if resource_ids is not None:
                if isinstance(resource_ids, int):
                    if res['id'] != resource_ids:
                        continue
                elif res['id'] not in resource_ids:
                    continue

            if resource_types is not None:
                if isinstance(resource_types, str):
                    if res['type_name'] != resource_types:
                        continue
                elif res['type_id'] not in resource_types:
                    continue

            res2 = dict(res)  # shallow copy is enough
            if not include_availability:
                del res2['active']
                del res2['available_capacity']
                del res2['total_capacity']
                del res2['used_capacity']

            resources.append(res2)

        return resources

    def getResourceGroupMemberships(self):
        from copy import deepcopy
        return deepcopy(self.radb_mock.get_memberships())

    def getResourceClaims(self, claim_ids=None, lower_bound=None, upper_bound=None,
                          resource_ids=None, task_ids=None, status=None, resource_type=None,
                          extended=False, include_properties=False):
        # Only implement some of the function arguments that the system under test may use
        # shallow copy is enough
        return [dict(claim) for claim in self.radb_mock.get_claims() if (claim_ids is None or claim['id'] in claim_ids) and \
                                                                  (resource_ids is None or claim['resource_id'] in resource_ids) and \
                                                                  (task_ids is None or claim['task_ids'] in task_ids) and \
                                                                  (resource_type is None or claim['resource_type_id'] == resource_type) and \
                                                                  (lower_bound is None or claim['endtime'] >= lower_bound) and \
                                                                  (upper_bound is None or claim['starttime'] <= upper_bound)]

    def updateResourceClaims(self, where_resource_claim_ids=None, where_task_ids=None, where_resource_types=None,
                             resource_id=None, task_id=None, starttime=None, endtime=None,
                             status=None, claim_size=None, username=None, used_rcus=None, user_id=None,
                             commit=True):
        # This implementation is greatly simplified vs the real radb updateResourceClaims()! Only what the system under test may use.
        updated = False

        claims = self.radb_mock.get_claims()
        for claim in claims:
            if (where_resource_claim_ids is None or claim['id']               in where_resource_claim_ids) and \
               (where_task_ids           is None or claim['task_id']          in where_task_ids) and \
               (where_resource_types     is None or claim['resource_type_id'] in where_resource_types):
                # don't bother checking if it (still) fits, etc.
                if starttime is not None:
                    claim['starttime'] = starttime  # data type not checked here...
                if endtime is not None:
                    claim['endtime'] = endtime  # idem
                if claim_size is not None:
                    claim['claim_size'] = claim_size  # idem
                # <more potentially updated values here>
                updated = True

        return {'updated': updated}  # there's more in this dict (see ResourceAssignmentService/service.py), but don't bother

    def getTasks(self, lower_bound=None, upper_bound=None, task_ids=None, task_status=None,
                 task_type=None, mom_ids=None, otdb_ids=None, cluster=None):
        # Only implement some of the function arguments that the system under test may use
        if task_ids is not None:
            # shallow copy is enough
            return [dict(task) for task in self.radb_mock.get_tasks() if task['id'] in task_ids]
        return []

    def get_resource_claimable_capacity(self, resource_id, lower_bound, upper_bound):
        if resource_id is None or lower_bound is None or upper_bound is None:
            raise ValueError('resource_id and/or lower_bound and/or upper_bound cannot be None')

        # This inefficient implementation is good enough for this mock; the RADB does it better
        for res in self.radb_mock.get_resources():
            if res['id'] == resource_id:
                claimable_cap = res['available_capacity']
                for claim in self.radb_mock.get_claims():
                    if claim['resource_id'] == resource_id and \
                       claim['endtime'] >= lower_bound and claim['starttime'] <= upper_bound:
                        claimable_cap -= claim['claim_size']
                return claimable_cap
        return 0


from sys import exit

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Hook the mock class in place after import and before running the program
import lofar.sas.datamanagement.resourcetool.resourcetool as rt
rt.RADBRPC = RADBRPC_mock

# List all resources and claims (no time range bounds)
rv = rt.main(['-G', 'INSTRUMENT', '-T', 'None', '-S', 'None'])
if rv != 0:
    logger.error('1st listing failed with status {}'.format(rv))
    exit(1)

# Change a few resources
rv = rt.main(['-G', 'CLUSTER', 'node1_bandwidth:/d2-qzy=1999', 'node2_storage:/d-qzy=True,9000,10000'])
if rv != 0:
    logger.error('changing 2 resources failed with status {}'.format(rv))
    exit(1)

# Reset end times beyond *now* (if task ended) of some storage claims.
rv = rt.main(['-G', 'CLUSTER', '-E'])
if rv != 0:
    logger.error('adjusting storage claim end time(s) using -E failed with status {}'.format(rv))
    exit(1)

# List all CLUSTER resources (incl changes). Use timestamp bounds that include all claims.
ts1 = datetime.datetime.utcnow() - datetime.timedelta(minutes=90)
ts1_str = str(datetime.datetime(ts1.year, ts1.month, ts1.day, ts1.hour, ts1.minute, ts1.second))  # strip milliseconds
ts2 = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
ts2_str = str(datetime.datetime(ts2.year, ts2.month, ts2.day, ts2.hour, ts2.minute, ts2.second))  # strip milliseconds
logger.info('test ts1_str = {}, ts2_str = {}'.format(ts1_str, ts2_str))
rv = rt.main(['-G', 'CLUSTER', '-T', ts1_str, '-S', ts2_str])
if rv != 0:
    logger.error('2nd listing failed with status {}'.format(rv))
    exit(1)

# Try a few erroneous cases.
# We can't try errors detected by cmd-line arg parsing here, since the opt parser calls exit().
rv = 0
rv |= rt.main(['-G', 'NON_EXISTENT_GROUP'])
rv |= rt.main(['-G', 'node1', 'node2_bandwidth:/d-qzy=False'])  # resource N/A under group node1
rv |= rt.main(['-G', 'CLUSTER', 'node1_storage:/d1-qzy=101'])  # avail > total not allowed
if rv != 1:
    logger.error('some tests for erroneous cases incorrectly returned success')
    exit(1)

# Another overview (error cases should not have changed anything), this time show storage only, and raw values
rv = rt.main(['-G', 'INSTRUMENT', '-t', 'storage', '-T', 'None', '-S', 'None', '--no-scaled-units'])
if rv != 0:
    logger.error('final listing failed with status {}'.format(rv))
    exit(1)

