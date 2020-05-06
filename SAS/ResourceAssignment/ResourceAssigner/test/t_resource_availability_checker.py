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

import unittest
from unittest import mock
from unittest.mock import MagicMock
import datetime
import sys

from lofar.sas.resourceassignment.resourceassigner.resource_availability_checker import ResourceAvailabilityChecker
from lofar.sas.resourceassignment.resourceassigner.resource_availability_checker import CouldNotFindClaimException



class ResourceAvailabilityCheckerTest(unittest.TestCase):
    specification_id = 2323

    task_mom_id = 351543
    task_otdb_id = 1290472
    task_id = 2299
    task_end_time = datetime.datetime(2016, 3, 25, 22, 47, 31)
    task_start_time = datetime.datetime(2016, 3, 25, 21, 47, 31)

    non_existing_task_mom_id = -1

    predecessor_task_mom_id = 1
    predecessor_task_otdb_id = 2
    predecessor_task_id = 3
    predecessor_task = {
        "mom_id": predecessor_task_mom_id,
        "otdb_id": predecessor_task_otdb_id,
        "id": predecessor_task_id,
        "endtime": datetime.datetime(2016, 3, 25, 22, 47, 31),
        "name": "IS HBA_DUAL",
        "predecessor_ids": [],
        "project_mom_id": 2,
        "project_name": "test-lofar",
        "specification_id": 2323,
        "starttime": datetime.datetime(2016, 3, 25, 21, 47, 31),
        "status": "prescheduled",
        "status_id": 350,
        "successor_ids": [],
        "type": "pipeline",
        "type_id": 0
    }

    successor_task_mom_id = 4
    successor_task_otdb_id = 5
    successor_task_id = 6
    successor_task = {
        "mom_id": successor_task_mom_id,
        "otdb_id": successor_task_otdb_id,
        "id": successor_task_id,
        "endtime": datetime.datetime(2016, 3, 25, 22, 47, 31),
        "name": "IS HBA_DUAL",
        "predecessor_ids": [],
        "project_mom_id": 2,
        "project_name": "test-lofar",
        "specification_id": 2323,
        "starttime": datetime.datetime(2016, 3, 25, 21, 47, 31),
        "status": "prescheduled",
        "status_id": 350,
        "successor_ids": [],
        "type": "pipeline",
        "type_id": 0
    }

    resources_with_rcus_otdb_id = 1290495
    resources_with_errors_otdb_id = 1290496
    resource_error1 = "error 1"
    resource_error2 = "error 2"
    unknown_resource_type_name = "fuel"
    unknown_resource_type_otdb_id = 123489

    cep4bandwidth_resource_id = 116
    cep4storage_resource_id = 117

    storage_claim = {
        'resource_id': cep4storage_resource_id,
        'resource_type_id': 5,
        'starttime': task_start_time,
        'used_rcus': None,
        'endtime': task_end_time + datetime.timedelta(days=365),
        'status': 'tentative',
        'claim_size': 2,
        'properties': [
            {'io_type': 'output', 'type': 15, 'sap_nr': 0, 'value': 0},
            {'io_type': 'output', 'type': 2, 'sap_nr': 0, 'value': 1},
            {'io_type': 'output', 'type': 10, 'sap_nr': 0, 'value': 1073741824}
        ]
    }

    bandwidth_claim = {
        'resource_id': cep4bandwidth_resource_id,
        'resource_type_id': 3,
        'starttime': task_start_time,
        'used_rcus': None,
        'endtime': task_end_time,
        'status': 'tentative',
        'claim_size': 2,
        'properties': []
    }

    def reset_task(self):
        self.task = {
            "mom_id": self.task_mom_id,
            "otdb_id": self.task_otdb_id,
            "id": self.task_id,
            "endtime": self.task_end_time,
            "name": "IS HBA_DUAL",
            "predecessor_ids": [],
            "project_mom_id": 2,
            "project_name": "test-lofar",
            "specification_id": self.specification_id,
            "starttime": self.task_start_time,
            "status": "prescheduled",
            "status_id": 350,
            "successor_ids": [],
            "type": "pipeline",
            "type_id": 0
        }

    def setUp(self):
        self.reset_task()

        def get_task_side_effect(*args, **kwargs):
            if 'mom_id' in kwargs:
                if kwargs['mom_id'] == self.successor_task_mom_id:
                    return self.successor_task
                elif kwargs['mom_id'] == self.predecessor_task_mom_id:
                    return self.predecessor_task
                elif kwargs['mom_id'] == self.non_existing_task_mom_id:
                    return None
                else:
                    return self.task
            else:
                return self.task

        self.successor_task_mom_ids = [self.successor_task_mom_id]
        self.predecessor_task_mom_ids = [self.predecessor_task_mom_id]

        rarpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassignmentservice.rpc.RADBRPC')
        self.addCleanup(rarpc_patcher.stop)
        self.rarpc_mock = rarpc_patcher.start()
        self.rarpc_mock.getTask.side_effect = get_task_side_effect
        self.rarpc_mock.insertOrUpdateSpecificationAndTask.return_value = {
            'inserted': True,
            'specification_id': self.specification_id,
            'task_id': self.task_id
        }
        self.rarpc_mock.getResourceClaimPropertyTypes.return_value = [
            {'id': 0, 'name': 'nr_of_is_files'},
            {'id': 1, 'name': 'nr_of_cs_files'},
            {'id': 2, 'name': 'nr_of_uv_files'},
            {'id': 3, 'name': 'nr_of_im_files'},
            {'id': 4, 'name': 'nr_of_img_files'},
            {'id': 5, 'name': 'nr_of_pulp_files'},
            {'id': 6, 'name': 'nr_of_cs_stokes'},
            {'id': 7, 'name': 'nr_of_is_stokes'},
            {'id': 8, 'name': 'is_file_size'},
            {'id': 9, 'name': 'cs_file_size'},
            {'id': 10, 'name': 'uv_file_size'},
            {'id': 11, 'name': 'im_file_size'},
            {'id': 12, 'name': 'img_file_size'},
            {'id': 13, 'name': 'nr_of_pulp_files'},
            {'id': 14, 'name': 'nr_of_cs_parts'},
            {'id': 15, 'name': 'start_sb_nr'},
            {'id': 16, 'name': 'uv_otdb_id'},
            {'id': 17, 'name': 'cs_otdb_id'},
            {'id': 18, 'name': 'is_otdb_id'},
            {'id': 19, 'name': 'im_otdb_id'},
            {'id': 20, 'name': 'img_otdb_id'},
            {'id': 21, 'name': 'pulp_otdb_id'},
            {'id': 22, 'name': 'is_tab_nr'},
            {'id': 23, 'name': 'start_sbg_nr'},
            {'id': 24, 'name': 'pulp_file_size'}
        ]
        self.rarpc_mock.getResourceTypes.return_value = [
            {'id': 0, 'name': 'rsp', 'unit_id': 0, 'units': 'rsp_channel_bit'},
            {'id': 1, 'name': 'tbb', 'unit_id': 1, 'units': 'bytes'},
            {'id': 2, 'name': 'rcu', 'unit_id': 2, 'units': 'rcu_board'},
            {'id': 3, 'name': 'bandwidth', 'unit_id': 3, 'units': 'bits/second'},
            {'id': 4, 'name': 'processor', 'unit_id': 4, 'units': 'cores'},
            {'id': 5, 'name': 'storage', 'unit_id': 1, 'units': 'bytes'},
        ]
        self.rarpc_mock.insertResourceClaims.return_value = {'ids': [1, 2]}

        self.rarpc_mock.getResourceGroupNames.return_value = [{"name": "CEP4"}, {"name": "DRAGNET"}, {"name": "COBALT"}]

        self.rarpc_mock.getResourceGroupMemberships.return_value = {'groups': [
            {'resource_group_parent_id': None, 'resource_group_parent_name': None, 'resource_group_id': 0,
             'resource_group_name': 'CORE', 'child_ids': [1, 2], 'parent_ids': [], 'resource_ids': [0, 1]},
            {'resource_group_parent_id': None, 'resource_group_parent_name': None, 'resource_group_id': 3,
             'resource_group_name': 'CS001', 'child_ids': [], 'parent_ids': [0], 'resource_ids': [212]},
            {'resource_group_parent_id': None, 'resource_group_parent_name': None, 'resource_group_id': 1,
             'resource_group_name': 'CEP4', 'child_ids': [], 'parent_ids': [0], 'resource_ids': [116, 117]},
            # {'resource_group_parent_id': None, 'resource_group_parent_name': None, 'resource_group_id': 4,   # TODO: WHY DOES ORDER MATTER IN HERE???
            #  'resource_group_name': 'CS002', 'child_ids': [], 'parent_ids': [0], 'resource_ids': [214]},     # TODO: check what happens when this is moved after e.g. CS001; also comment in CS002 in RE response
            ],
            'resources': [{'resource_group_parent_id': 0,
                           'resource_group_parent_name': 'CORE',
                           'resource_id': 0,
                           'resource_name': 'CS001',
                           'parent_group_ids': []},
                          {'resource_group_parent_id': 0,
                           'resource_group_parent_name': 'CORE',
                           'resource_id': 1,
                           'resource_name': 'CS002',
                           'parent_group_ids': []},
                          {'resource_group_parent_id': 1,
                           'resource_group_parent_name': 'CEP4',
                           'resource_id': 2,
                           'resource_name': 'CEP4_storage:/data',
                           'parent_group_ids': []}]}

        # incomplete response but good enough for tests
        self.rarpc_mock.getResources.return_value = [
            {'id': 0, 'name': 'cpunode01_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 1, 'name': 'cpunode01_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 2, 'name': 'cpunode02_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 3, 'name': 'cpunode02_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 4, 'name': 'cpunode03_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 5, 'name': 'cpunode03_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 6, 'name': 'cpunode04_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 7, 'name': 'cpunode04_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 8, 'name': 'cpunode05_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 9, 'name': 'cpunode05_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 10, 'name': 'cpunode06_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 11, 'name': 'cpunode06_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 12, 'name': 'cpunode07_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 13, 'name': 'cpunode07_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 14, 'name': 'cpunode08_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 15, 'name': 'cpunode08_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 16, 'name': 'cpunode09_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 17, 'name': 'cpunode09_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 18, 'name': 'cpunode10_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 19, 'name': 'cpunode10_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 20, 'name': 'cpunode11_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 21, 'name': 'cpunode11_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 22, 'name': 'cpunode12_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 23, 'name': 'cpunode12_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 24, 'name': 'cpunode13_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 25, 'name': 'cpunode13_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 26, 'name': 'cpunode14_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 27, 'name': 'cpunode14_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 28, 'name': 'cpunode15_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 29, 'name': 'cpunode15_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 30, 'name': 'cpunode16_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 31, 'name': 'cpunode16_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 32, 'name': 'cpunode17_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 33, 'name': 'cpunode17_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 34, 'name': 'cpunode18_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 35, 'name': 'cpunode18_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 36, 'name': 'cpunode19_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 37, 'name': 'cpunode19_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 38, 'name': 'cpunode20_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 39, 'name': 'cpunode20_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 40, 'name': 'cpunode21_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 41, 'name': 'cpunode21_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 42, 'name': 'cpunode22_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 43, 'name': 'cpunode22_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 44, 'name': 'cpunode23_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 45, 'name': 'cpunode23_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 46, 'name': 'cpunode24_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 47, 'name': 'cpunode24_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 48, 'name': 'cpunode25_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 49, 'name': 'cpunode25_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 50, 'name': 'cpunode26_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 51, 'name': 'cpunode26_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 52, 'name': 'cpunode27_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 53, 'name': 'cpunode27_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 54, 'name': 'cpunode28_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 55, 'name': 'cpunode28_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 56, 'name': 'cpunode29_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 57, 'name': 'cpunode29_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 58, 'name': 'cpunode30_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 59, 'name': 'cpunode30_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 60, 'name': 'cpunode31_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 61, 'name': 'cpunode31_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 62, 'name': 'cpunode32_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 63, 'name': 'cpunode32_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 64, 'name': 'cpunode33_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 65, 'name': 'cpunode33_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 66, 'name': 'cpunode34_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 67, 'name': 'cpunode34_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 68, 'name': 'cpunode35_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 69, 'name': 'cpunode35_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 70, 'name': 'cpunode36_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 71, 'name': 'cpunode36_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 72, 'name': 'cpunode37_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 73, 'name': 'cpunode37_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 74, 'name': 'cpunode38_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 75, 'name': 'cpunode38_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 76, 'name': 'cpunode39_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 77, 'name': 'cpunode39_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 78, 'name': 'cpunode40_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 79, 'name': 'cpunode40_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 80, 'name': 'cpunode41_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 81, 'name': 'cpunode41_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 82, 'name': 'cpunode42_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 83, 'name': 'cpunode42_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 84, 'name': 'cpunode43_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 85, 'name': 'cpunode43_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 86, 'name': 'cpunode44_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 87, 'name': 'cpunode44_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 88, 'name': 'cpunode45_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 89, 'name': 'cpunode45_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 90, 'name': 'cpunode46_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 91, 'name': 'cpunode46_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 92, 'name': 'cpunode47_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 93, 'name': 'cpunode47_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 94, 'name': 'cpunode48_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 95, 'name': 'cpunode48_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 96, 'name': 'cpunode49_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 97, 'name': 'cpunode49_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 98, 'name': 'cpunode50_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 99, 'name': 'cpunode50_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 100, 'name': 'cbt001_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 101, 'name': 'cbt001_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 102, 'name': 'cbt002_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 103, 'name': 'cbt002_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 104, 'name': 'cbt003_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 105, 'name': 'cbt003_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 106, 'name': 'cbt004_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 107, 'name': 'cbt004_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 108, 'name': 'cbt005_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 109, 'name': 'cbt005_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 110, 'name': 'cbt006_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 111, 'name': 'cbt006_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 112, 'name': 'cbt007_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 113, 'name': 'cbt007_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 114, 'name': 'cbt008_bandwidth', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 115, 'name': 'cbt008_processors', 'type_id': 4, 'type_name': 'processor', 'unit_id': 4,
             'unit': 'cores', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 116, 'name': 'CEP4_bandwidth:/data', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 117, 'name': 'CEP4_storage:/data', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 118, 'name': 'dragproc_bandwidth:/data', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 119, 'name': 'dragproc_storage:/data', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 120, 'name': 'drg01_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 121, 'name': 'drg01_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 122, 'name': 'drg01_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 123, 'name': 'drg01_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 124, 'name': 'drg02_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 125, 'name': 'drg02_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 126, 'name': 'drg02_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 127, 'name': 'drg02_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 128, 'name': 'drg03_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 129, 'name': 'drg03_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 130, 'name': 'drg03_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 131, 'name': 'drg03_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 132, 'name': 'drg04_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 133, 'name': 'drg04_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 134, 'name': 'drg04_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 135, 'name': 'drg04_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 136, 'name': 'drg05_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 137, 'name': 'drg05_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 138, 'name': 'drg05_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 139, 'name': 'drg05_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 140, 'name': 'drg06_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 141, 'name': 'drg06_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 142, 'name': 'drg06_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 143, 'name': 'drg06_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 144, 'name': 'drg07_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 145, 'name': 'drg07_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 146, 'name': 'drg07_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 147, 'name': 'drg07_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 148, 'name': 'drg08_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 149, 'name': 'drg08_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 150, 'name': 'drg08_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 151, 'name': 'drg08_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 152, 'name': 'drg09_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 153, 'name': 'drg09_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 154, 'name': 'drg09_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 155, 'name': 'drg09_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 156, 'name': 'drg10_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 157, 'name': 'drg10_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 158, 'name': 'drg10_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 159, 'name': 'drg10_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 160, 'name': 'drg11_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 161, 'name': 'drg11_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 162, 'name': 'drg11_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 163, 'name': 'drg11_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 164, 'name': 'drg12_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 165, 'name': 'drg12_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 166, 'name': 'drg12_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 167, 'name': 'drg12_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 168, 'name': 'drg13_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 169, 'name': 'drg13_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 170, 'name': 'drg13_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 171, 'name': 'drg13_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 172, 'name': 'drg14_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 173, 'name': 'drg14_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 174, 'name': 'drg14_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 175, 'name': 'drg14_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 176, 'name': 'drg15_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 177, 'name': 'drg15_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 178, 'name': 'drg15_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 179, 'name': 'drg15_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 180, 'name': 'drg16_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 181, 'name': 'drg16_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 182, 'name': 'drg16_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 183, 'name': 'drg16_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 184, 'name': 'drg17_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 185, 'name': 'drg17_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 186, 'name': 'drg17_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 187, 'name': 'drg17_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 188, 'name': 'drg18_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 189, 'name': 'drg18_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 190, 'name': 'drg18_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 191, 'name': 'drg18_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 192, 'name': 'drg19_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 193, 'name': 'drg19_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 194, 'name': 'drg19_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 195, 'name': 'drg19_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 196, 'name': 'drg20_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 197, 'name': 'drg20_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 198, 'name': 'drg20_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 199, 'name': 'drg20_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 200, 'name': 'drg21_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 201, 'name': 'drg21_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 202, 'name': 'drg21_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 203, 'name': 'drg21_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 204, 'name': 'drg22_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 205, 'name': 'drg22_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 206, 'name': 'drg22_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 207, 'name': 'drg22_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 208, 'name': 'drg23_bandwidth:/data1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 209, 'name': 'drg23_bandwidth:/data2', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3,
             'unit': 'bits/second', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 210, 'name': 'drg23_storage:/data1', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 211, 'name': 'drg23_storage:/data2', 'type_id': 5, 'type_name': 'storage', 'unit_id': 1,
             'unit': 'bytes', 'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 212, 'name': 'CS001rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 213, 'name': 'CS001tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 214, 'name': 'CS002rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 215, 'name': 'CS002tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 216, 'name': 'CS003rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 217, 'name': 'CS003tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 218, 'name': 'CS004rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 219, 'name': 'CS004tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 220, 'name': 'CS005rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 221, 'name': 'CS005tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 222, 'name': 'CS006rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 223, 'name': 'CS006tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 224, 'name': 'CS007rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 225, 'name': 'CS007tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 226, 'name': 'CS011rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 227, 'name': 'CS011tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 228, 'name': 'CS013rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 229, 'name': 'CS013tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 230, 'name': 'CS017rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 231, 'name': 'CS017tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 232, 'name': 'CS021rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 233, 'name': 'CS021tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 234, 'name': 'CS024rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 235, 'name': 'CS024tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 236, 'name': 'CS026rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 237, 'name': 'CS026tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 238, 'name': 'CS028rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 239, 'name': 'CS028tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 240, 'name': 'CS030rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 241, 'name': 'CS030tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 242, 'name': 'CS031rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 243, 'name': 'CS031tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 244, 'name': 'CS032rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 245, 'name': 'CS032tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 246, 'name': 'CS101rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 247, 'name': 'CS101tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 248, 'name': 'CS103rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 249, 'name': 'CS103tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 250, 'name': 'CS201rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 251, 'name': 'CS201tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 252, 'name': 'CS301rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 253, 'name': 'CS301tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 254, 'name': 'CS302rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 255, 'name': 'CS302tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 256, 'name': 'CS401rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 257, 'name': 'CS401tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 258, 'name': 'CS501rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 259, 'name': 'CS501tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 260, 'name': 'RS106rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 261, 'name': 'RS106tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 262, 'name': 'RS205rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 263, 'name': 'RS205tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 264, 'name': 'RS208rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 265, 'name': 'RS208tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 266, 'name': 'RS210rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 267, 'name': 'RS210tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 268, 'name': 'RS305rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 269, 'name': 'RS305tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 270, 'name': 'RS306rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 271, 'name': 'RS306tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 272, 'name': 'RS307rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 273, 'name': 'RS307tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 274, 'name': 'RS310rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 275, 'name': 'RS310tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 276, 'name': 'RS406rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 277, 'name': 'RS406tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 278, 'name': 'RS407rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 279, 'name': 'RS407tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 280, 'name': 'RS408rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 281, 'name': 'RS408tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 282, 'name': 'RS409rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 283, 'name': 'RS409tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 284, 'name': 'RS503rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 285, 'name': 'RS503tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 286, 'name': 'RS508rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 287, 'name': 'RS508tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 288, 'name': 'RS509rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 289, 'name': 'RS509tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 290, 'name': 'DE601rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 291, 'name': 'DE601tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 292, 'name': 'DE602rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 293, 'name': 'DE602tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 294, 'name': 'DE603rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 295, 'name': 'DE603tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 296, 'name': 'DE604rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 297, 'name': 'DE604tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 298, 'name': 'DE605rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 299, 'name': 'DE605tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 300, 'name': 'FR606rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 301, 'name': 'FR606tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 302, 'name': 'SE607rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 303, 'name': 'SE607tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 304, 'name': 'UK608rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 305, 'name': 'UK608tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 306, 'name': 'DE609rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 307, 'name': 'DE609tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 308, 'name': 'PL610rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 309, 'name': 'PL610tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 310, 'name': 'PL611rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 311, 'name': 'PL611tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 312, 'name': 'PL612rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 313, 'name': 'PL612tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 314, 'name': 'IE613rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 315, 'name': 'IE613tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 316, 'name': 'IS614rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 317, 'name': 'IS614tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 318, 'name': 'TEST1rcu', 'type_id': 2, 'type_name': 'rcu', 'unit_id': 2, 'unit': 'rcu_board',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 319, 'name': 'TEST1tbb', 'type_id': 1, 'type_name': 'tbb', 'unit_id': 1, 'unit': 'bytes',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 320, 'name': 'CS001chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 321, 'name': 'CS001bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 322, 'name': 'CS001chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 323, 'name': 'CS001bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 324, 'name': 'CS002chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 325, 'name': 'CS002bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 326, 'name': 'CS002chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 327, 'name': 'CS002bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 328, 'name': 'CS003chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 329, 'name': 'CS003bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 330, 'name': 'CS003chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 331, 'name': 'CS003bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 332, 'name': 'CS004chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 333, 'name': 'CS004bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 334, 'name': 'CS004chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 335, 'name': 'CS004bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 336, 'name': 'CS005chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 337, 'name': 'CS005bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 338, 'name': 'CS005chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 339, 'name': 'CS005bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 340, 'name': 'CS006chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 341, 'name': 'CS006bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 342, 'name': 'CS006chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 343, 'name': 'CS006bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 344, 'name': 'CS007chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 345, 'name': 'CS007bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 346, 'name': 'CS007chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 347, 'name': 'CS007bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 348, 'name': 'CS011chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 349, 'name': 'CS011bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 350, 'name': 'CS011chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 351, 'name': 'CS011bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 352, 'name': 'CS013chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 353, 'name': 'CS013bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 354, 'name': 'CS013chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 355, 'name': 'CS013bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 356, 'name': 'CS017chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 357, 'name': 'CS017bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 358, 'name': 'CS017chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 359, 'name': 'CS017bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 360, 'name': 'CS021chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 361, 'name': 'CS021bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 362, 'name': 'CS021chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 363, 'name': 'CS021bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 364, 'name': 'CS024chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 365, 'name': 'CS024bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 366, 'name': 'CS024chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 367, 'name': 'CS024bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 368, 'name': 'CS026chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 369, 'name': 'CS026bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 370, 'name': 'CS026chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 371, 'name': 'CS026bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 372, 'name': 'CS028chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 373, 'name': 'CS028bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 374, 'name': 'CS028chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 375, 'name': 'CS028bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 376, 'name': 'CS030chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 377, 'name': 'CS030bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 378, 'name': 'CS030chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 379, 'name': 'CS030bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 380, 'name': 'CS031chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 381, 'name': 'CS031bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 382, 'name': 'CS031chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 383, 'name': 'CS031bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 384, 'name': 'CS032chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 385, 'name': 'CS032bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 386, 'name': 'CS032chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 387, 'name': 'CS032bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 388, 'name': 'CS101chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 389, 'name': 'CS101bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 390, 'name': 'CS101chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 391, 'name': 'CS101bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 392, 'name': 'CS103chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 393, 'name': 'CS103bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 394, 'name': 'CS103chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 395, 'name': 'CS103bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 396, 'name': 'CS201chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 397, 'name': 'CS201bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 398, 'name': 'CS201chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 399, 'name': 'CS201bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 400, 'name': 'CS301chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 401, 'name': 'CS301bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 402, 'name': 'CS301chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 403, 'name': 'CS301bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 404, 'name': 'CS302chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 405, 'name': 'CS302bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 406, 'name': 'CS302chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 407, 'name': 'CS302bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 408, 'name': 'CS401chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 409, 'name': 'CS401bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 410, 'name': 'CS401chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 411, 'name': 'CS401bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 412, 'name': 'CS501chan0', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 413, 'name': 'CS501bw0', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 414, 'name': 'CS501chan1', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 415, 'name': 'CS501bw1', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 416, 'name': 'RS106chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 417, 'name': 'RS106bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 418, 'name': 'RS205chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 419, 'name': 'RS205bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 420, 'name': 'RS208chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 421, 'name': 'RS208bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 422, 'name': 'RS210chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 423, 'name': 'RS210bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 424, 'name': 'RS305chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 425, 'name': 'RS305bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 426, 'name': 'RS306chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 427, 'name': 'RS306bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 428, 'name': 'RS307chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 429, 'name': 'RS307bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 430, 'name': 'RS310chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 431, 'name': 'RS310bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 432, 'name': 'RS406chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 433, 'name': 'RS406bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 434, 'name': 'RS407chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 435, 'name': 'RS407bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 436, 'name': 'RS408chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 437, 'name': 'RS408bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 438, 'name': 'RS409chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 439, 'name': 'RS409bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 440, 'name': 'RS503chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 441, 'name': 'RS503bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 442, 'name': 'RS508chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 443, 'name': 'RS508bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 444, 'name': 'RS509chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 445, 'name': 'RS509bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 446, 'name': 'DE601chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 447, 'name': 'DE601bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 448, 'name': 'DE602chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 449, 'name': 'DE602bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 450, 'name': 'DE603chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 451, 'name': 'DE603bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 452, 'name': 'DE604chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 453, 'name': 'DE604bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 454, 'name': 'DE605chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 455, 'name': 'DE605bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 456, 'name': 'FR606chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 457, 'name': 'FR606bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 458, 'name': 'SE607chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 459, 'name': 'SE607bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 460, 'name': 'UK608chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 461, 'name': 'UK608bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 462, 'name': 'DE609chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 463, 'name': 'DE609bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 464, 'name': 'PL610chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 465, 'name': 'PL610bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 466, 'name': 'PL611chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 467, 'name': 'PL611bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 468, 'name': 'PL612chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 469, 'name': 'PL612bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 470, 'name': 'IE613chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 471, 'name': 'IE613bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 472, 'name': 'IS614chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 473, 'name': 'IS614bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 474, 'name': 'TEST1chan', 'type_id': 0, 'type_name': 'rsp', 'unit_id': 0, 'unit': 'rsp_channel_bit',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1},
            {'id': 475, 'name': 'TEST1bw', 'type_id': 3, 'type_name': 'bandwidth', 'unit_id': 3, 'unit': 'bits/second',
             'available_capacity': 10, 'used_capacity': 0, 'total_capacity': 10, 'active': 1}
        ]

        self.rarpc_mock.getResourceClaims.return_value = []

        self.rarpc_mock.getResourceAllocationConfig.return_value = [
            {'name': 'max_fill_ratio_CEP4_storage', 'value': 0.85}, {'name': 'claim_timeout', 'value': 172800},
            {'name': 'min_inter_task_delay', 'value': 60}, {'name': 'max_fill_ratio_CEP4_bandwidth', 'value': 0.75}
        ]

        logger_patcher = mock.patch(
            'lofar.sas.resourceassignment.resourceassigner.resource_availability_checker.logger'
        )
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        # Select logger output to see
        def myprint(s, *args):
            print(s % args if args else s, file=sys.stderr)

        # self.logger_mock.debug.side_effect = myprint
        self.logger_mock.info.side_effect = myprint
        self.logger_mock.warn.side_effect = myprint
        self.logger_mock.error.side_effect = myprint

        self.uut = ResourceAvailabilityChecker(self.rarpc_mock)

    def test_disk_claim(self):
        files = \
            {
                'uv':
                [{
                    'identification': 'mom.G732487.B0.1.C.SAP000.uv.dps',
                    'sap_nr': 0,
                    'properties':
                    {
                        'nr_of_uv_files': 120,
                        'start_sb_nr': 0,
                        'uv_file_size': 3617984960,
                        'uv_otdb_id': 2
                    }
                }]
            }
        properties = self.uut._get_files_properties(files_dict = files,
                                                    io_type = 'input')
        self.assertIsNotNone(properties)

    def test_get_current_resource_usage(self):
        '''
        Check if the resource availability checker returns a proper
        resource list.
        '''
        db_resource_list = self.uut._get_current_resource_usage()
        self.assertIsNotNone(db_resource_list)

    def test_fit_single_resource_no_claimable_resources(self):
        """
        Given 1 needed resource, and 0 claimable resources, fit_single_resources should return
        failure.
        """
        needed_resources_by_type_id = {5: 500}
        claimable_resources_list = []

        with self.assertRaises(CouldNotFindClaimException):
            self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

    def test_fit_single_resources_fit_one_disk(self):
        """
        Given 1 needed resource, and 1 claimable resource that fits, fit_single_resources should return succesful.
        """

        needed_resources_by_type_id = { 5: 500 }
        claimable_resources_list = [ { 5: { 'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000 } } ]

        uut = ResourceAvailabilityChecker(self.rarpc_mock)

        claims = self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

        self.assertIsNotNone(claims)

    def test_fit_single_resources_not_fit_one_disk(self):
        """
        Given 1 needed resource, and 1 claimable resource that does NOT fits, fit_single_resources should return
        failure.
        """

        needed_resources_by_type_id = { 5: 500 }
        claimable_resources_list = [ { 5: { 'id': 1, 'claimable_capacity': 400, 'available_capacity': 400 } } ]

        with self.assertRaises(CouldNotFindClaimException):
            self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

    def test_fit_single_resources_fit_multiple_disks(self):
        """
        Given 1 needed resource, and 2 claimable resources, of which one fits, fit_single_resources should return
        succesful.
        """

        needed_resources_by_type_id = { 5: 500 }
        claimable_resources_list = [
            {5: {'id': 1, 'claimable_capacity': 400, 'available_capacity': 400}},
            {5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]

        claims = self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

        self.assertIsNotNone(claims)

    def test_fit_single_resources_not_fit_multiple_resources(self):
        """
        Given 2 needed resources, and 2 claimable resource sets, of which neither fit for a different resource,
        fit_single_resources should return failure.
        """

        needed_resources_by_type_id = { 3: 3000, 5: 500 }
        claimable_resources_list = [
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 400, 'available_capacity': 400}},   # type 5 does not fit
            {3: {'id': 0, 'claimable_capacity': 1000, 'available_capacity': 1000},
             5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]  # type 3 does not fit

        with self.assertRaises(CouldNotFindClaimException):
            self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

    def test_fit_single_resources_fit_multiple_resources(self):
        """
        Given 2 needed resources, and 2 claimable resource sets, of which only one fits, fit_single_resources() should
        return success.
        """

        needed_resources_by_type_id = { 3: 3000, 5: 500 }
        claimable_resources_list = [
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 400, 'available_capacity': 400}},   # type 5 does not fit
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]  # both fit

        claims = self.uut._get_tentative_claim_objects_for_single_resource(needed_resources_by_type_id, claimable_resources_list)

        self.assertIsNotNone(claims)

    def test_fit_multiple_resources_not_fit(self):
        """
        Given 2 needed resources (which we need 4 times), and 2 claimable resource sets, only 3 out of 4 fit,
        fit_multiple_resources() should return failure.
        """

        needed_resources_by_type_id = {3: 1000, 5: 100}
        claimable_resources_list = [
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 200, 'available_capacity': 200}},   # fits 2x
            {3: {'id': 0, 'claimable_capacity': 1000, 'available_capacity': 1000},
             5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]  # fits 1x

        with self.assertRaises(CouldNotFindClaimException):
            self.uut._get_tentative_claim_objects_for_multiple_resources(needed_resources_by_type_id, 4, claimable_resources_list)

    def test_fit_multiple_resources_fit(self):
        """
        Given 2 needed resources (which we need 4 times), and 2 claimable resource sets, all 4 out of 4 fit,
        fit_multiple_resources() should return success.
        """

        needed_resources_by_type_id = {3: 1000, 5: 100}
        claimable_resources_list = [
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 200, 'available_capacity': 200}},   # fits 2x
            {3: {'id': 0, 'claimable_capacity': 2000, 'available_capacity': 2000},
             5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]  # fits 2x

        claims = self.uut._get_tentative_claim_objects_for_multiple_resources(needed_resources_by_type_id, 4, claimable_resources_list)

        self.assertIsNotNone(claims)

    def test_fit_multiple_resources_logs_created_claim_per_needed_resource_type(self):
        """
        Given 2 needed resources (which we need 4 times), and 2 claimable resource sets, all 4 out of 4 fit, check if
        fit_multiple_resources() logs the expected created claim
        """

        needed_resources_by_type_id = {3: 1000, 5: 100}
        claimable_resources_list = [
            {3: {'id': 0, 'claimable_capacity': 3000, 'available_capacity': 3000},
             5: {'id': 1, 'claimable_capacity': 200, 'available_capacity': 200}},   # fits 2x
            {3: {'id': 0, 'claimable_capacity': 2000, 'available_capacity': 2000},
             5: {'id': 1, 'claimable_capacity': 1000, 'available_capacity': 1000}}]  # fits 2x

        self.uut._get_tentative_claim_objects_for_multiple_resources(needed_resources_by_type_id, 4, claimable_resources_list)

        resource_type_3_dict = {'status': 'tentative', 'resource_type_id': 3, 'resource_id': 0, 'claim_size': 1000,
                                'starttime': None, 'used_rcus': None, 'endtime': None, 'properties': []}
        resource_type_5_dict = {'status': 'tentative', 'resource_type_id': 5, 'resource_id': 1, 'claim_size': 100,
                                'starttime': None, 'used_rcus': None, 'endtime': None, 'properties': []}

        expected_claims = [resource_type_3_dict, resource_type_5_dict, resource_type_3_dict, resource_type_5_dict,
                           resource_type_3_dict, resource_type_5_dict, resource_type_3_dict, resource_type_5_dict]

        self.logger_mock.info.assert_any_call('fit_multiple_resources: created claims: %s', expected_claims)

    def test_get_is_claimable_invalid_resource_group(self):
        """ If we try to find claims with a non-existing root_resource_group, get_is_claimable should fail. """

        estimates = [{
            'root_resource_group': 'MIDDLE EARTH',
            'resource_count': 1,
            'resource_types': {
                'storage': 100
            }
        }]
        claimable_resources_list = [{
                'id': self.cep4storage_resource_id,
                'type_id': 5,
                'claimable_capacity': 400,
                'available_capacity': 400,
                'active': True
            }
        ]

        with self.assertRaises(ValueError):
            _, _ = self.uut.get_is_claimable(estimates, claimable_resources_list)

    def test_get_is_claimable_fit(self):
        """
        Given 2 needed resources (which we need 4 times), and 2 claimable resource sets, all 4 out of 4 fit,
        get_is_claimable should return success.
        """

        estimates = [{
            'root_resource_group': 'CEP4',
            'resource_count': 4,
            'resource_types': {
                'bandwidth': 1000,
                'storage': 100
            }
        }]
        claimable_resources_list = [{
                'id': self.cep4bandwidth_resource_id,
                'type_id': 3,
                'claimable_capacity': 4000,
                'available_capacity': 4000,
                'active': True
            },
            {
                'id': self.cep4storage_resource_id,
                'type_id': 5,
                'claimable_capacity': 400,
                'available_capacity': 400,
                'active': True
            }]

        claimable_resources = self.uut.get_is_claimable(estimates, claimable_resources_list)

        self.assertEqual(len(claimable_resources), len(claimable_resources_list))

    def test_get_is_claimable_not_fit(self):
        """ Given 2 needed resources (which we need 4 times), and 2 claimable resource sets, 3 out of 4 fit,
        get_is_claimable should return failure. """

        estimates = [{
            'root_resource_group': 'CEP4',
            'resource_count': 4,
            'resource_types': {
                'bandwidth': 1000,
                'storage': 100
            }
        }]
        claimable_resources_list = [{
                'id': self.cep4bandwidth_resource_id,
                'type_id': 3,
                'claimable_capacity': 4000,
                'available_capacity': 4000, 'active': True
            },
            {
                'id': self.cep4storage_resource_id,
                'type_id': 5,
                'claimable_capacity': 300,
                'available_capacity': 300,
                'active': True
            }
        ]

        with self.assertRaises(CouldNotFindClaimException):
            self.uut.get_is_claimable(estimates, claimable_resources_list)

    def test_get_is_claimable_partial_fit(self):
        """ Given 2 sets of 2 needed resources (which we need 4 times), and 2 claimable resource sets, only one set
        fits, get_is_claimable should return partial success. """

        estimates = [{
            'root_resource_group': 'CEP4',
            'resource_count': 4,
            'resource_types': {
                'bandwidth': 1000,
                'storage': 100
            }}, {
            'root_resource_group': 'CEP4',
            'resource_count': 4,
            'resource_types': {
                'bandwidth': 1000,
                'storage': 100
            }}]
        claimable_resources_list = [{
                'id': self.cep4bandwidth_resource_id,
                'type_id': 3,
                'claimable_capacity': 5000,
                'available_capacity': 5000,
                'active': True
            },
            {
                'id': self.cep4storage_resource_id,
                'type_id': 5,
                'claimable_capacity': 500,
                'available_capacity': 500,
                'active': True
            }]

        # TODO: verify with Jan David whether this test case (returning a partial fit) should still succeed or whether
        # an exception is expected to be raised
        with self.assertRaises(CouldNotFindClaimException):
            self.uut.get_is_claimable(estimates, claimable_resources_list)

        # TODO: remove if uut raising exception is what's expected
        # claimable_resources = self.uut.get_is_claimable(estimates, claimable_resources_list)
        # self.assertEqual(len(claimable_resources), 2)  # storage & bandwidth for estimates[0]

if __name__ == '__main__':
    unittest.main()
