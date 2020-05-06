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
import datetime
import sys
from copy import deepcopy

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(process)s %(message)s', level=logging.INFO)

from lofar.sas.resourceassignment.resourceassigner.config import DEFAULT_RA_NOTIFICATION_PREFIX
from lofar.sas.resourceassignment.resourceassigner.resource_assigner import ResourceAssigner
from lofar.messaging.messagebus import TemporaryExchange
from lofar.sas.resourceassignment.common.specification import Specification
from lofar.common.util import single_line_with_single_spaces
from lofar.messaging.messages import EventMessage

from lofar.sas.resourceassignment.database.testing.radb_common_testing import RADBCommonTestMixin

class ResourceAssignerTest(RADBCommonTestMixin, unittest.TestCase):
    mom_id = 351557
    otdb_id = 1290494
    specification_id = 2323
    task_type = 'pipeline'

    specification_tree = {}

    non_approved_or_prescheduled_status = 'opened'
    non_approved_or_prescheduled_otdb_id = 1

    future_start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    future_stop_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    task_duration = 3600

    non_approved_or_prescheduled_specification_tree = {
        'otdb_id': non_approved_or_prescheduled_otdb_id,
        'task_type': 'pipeline',
        'state': non_approved_or_prescheduled_status,
        'specification': {
            'Observation.startTime': future_start_time,
            'Observation.stopTime': future_stop_time
        }
    }

    mom_bug_processing_cluster_name = 'CEP2'
    mom_bug_otdb_id = 1234
    mom_bug_specification_tree = {
        'otdb_id': mom_bug_otdb_id,
        'mom_id': None,
        'task_id': None,
        'task_type': 'pipeline',
        'state': 'prescheduled',
        'starttime': datetime.datetime.utcnow(),
        'endtime': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
        'specification': {
            'Observation.startTime': future_start_time,
            'Observation.stopTime': future_stop_time,
            'Observation.DataProducts.Output_Pulsar.enabled': True,
            'Observation.DataProducts.Output_Pulsar.storageClusterName': 'CEP4',
            'Observation.Cluster.ProcessingCluster.clusterName': mom_bug_processing_cluster_name
        }
    }

    task_mom_id = 351543
    task_otdb_id = 1290472
    task_id = 2299
    task_end_time = datetime.datetime(2016, 3, 25, 22, 47, 31)
    task_start_time = datetime.datetime(2016, 3, 25, 21, 47, 31)

    task_minstarttime = task_start_time
    task_maxendtime = task_start_time   #  + datetime.timedelta(hours=1)
    task_minduration = 0
    task_maxduration = 0

    non_existing_task_mom_id = -1

    predecessor_task_mom_id = 1
    predecessor_task_otdb_id = 2
    predecessor_task_id = 3

    successor_task_mom_id = 4
    successor_task_otdb_id = 5
    successor_task_id = 6

    resources_with_no_resource_types_otdb_id = 1290497
    resources_with_negative_estimates_otdb_id = 1290488
    resources_with_errors_otdb_id = 1290496
    no_resources_otdb_id = 1290498
    resource_error1 = "error 1"
    resource_error2 = "error 2"

    rerpc_status = 0
    rerpc_needed_claim_for_bandwidth_size = 2
    rerpc_needed_claim_for_bandwidth = {
        'total_size': rerpc_needed_claim_for_bandwidth_size
    }

    rerpc_needed_claim_for_storage_output_files = {
        'uv': {
            'nr_of_uv_files': 481,
            'uv_file_size': 1482951104
        },
        'saps': [
            {
                'sap_nr': 0,
                'properties': {
                    'nr_of_uv_files': 319
                }
            },
            {
                'sap_nr': 1,
                'properties': {
                    'nr_of_uv_files': 81,
                }
            },
            {
                'sap_nr': 2,
                'properties': {
                    'nr_of_uv_files': 81
                }
            }
        ]
    }
    rerpc_needed_claim_for_storage_size = 2
    rerpc_needed_claim_for_storage = {
        'total_size': rerpc_needed_claim_for_storage_size,
        'output_files': rerpc_needed_claim_for_storage_output_files
    }
    rerpc_replymessage = {
        str(otdb_id): {
                'errors': [],
                'estimates': [{
                    'resource_types': {'bandwidth': 2, 'storage': 2},
                    'resource_count': 2, 'root_resource_group': 'CEP4',
                    'output_files': {
                        'uv': [{'sap_nr': 0, 'identifications': [],
                                'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 0}
                               }]
                    }
                }]
        },
        str(resources_with_negative_estimates_otdb_id):{
            'errors': [],
            'estimates': [{
                'resource_types': {'bandwidth': -2, 'storage': -2},
                'resource_count': 2, 'root_resource_group': 'CEP4',
                'output_files': {
                    'uv': [{'sap_nr': 0, 'identifications': [],
                              'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 0}
                            }]
                }
            }]
        },
        str(no_resources_otdb_id): {
            'errors': [],
            'estimates': []
        },
        str(resources_with_errors_otdb_id): {
                'estimates': [{
                    'resource_types': {'bandwidth': 19021319494, 'storage': 713299481024},
                    'output_files': {
                        'uv': [{'sap_nr': 0,
                                'properties': {'nr_of_uv_files': 319, 'uv_file_size': 1482951104}
                               },
                               {'sap_nr': 1,
                                'properties': {'nr_of_uv_files': 81, 'uv_file_size': 1482951104}
                               },
                               {'sap_nr': 2,
                                'properties': {'nr_of_uv_files': 81, 'uv_file_size': 1482951104}
                               }]
                     }
                }],
                'errors': [resource_error1, resource_error2]
        },
        str(resources_with_no_resource_types_otdb_id): {
            'errors': [],
            'estimates': [{
                'output_files': {
                    'uv': [{'sap_nr': 0,
                            'properties': {'nr_of_uv_files': 319, 'uv_file_size': 1482951104}
                            },
                           {'sap_nr': 1,
                            'properties': {'nr_of_uv_files': 81, 'uv_file_size': 1482951104}
                            },
                           {'sap_nr': 2,
                            'properties': {'nr_of_uv_files': 81, 'uv_file_size': 1482951104}
                            }]
                }
            }],
        }
    }

    def reset_specification_tree(self):
        self.specification_tree = {
            'otdb_id': self.otdb_id,
            'mom_id': self.mom_id,
            'task_id': self.task_id,
            'trigger_id': None,
            'status': 'approved',
            'task_type': self.task_type,
            'min_starttime': '2016-03-26 00:31:31',
            'endtime': '2016-03-26 01:31:31',
            'min_duration': 0,
            'max_duration': 0,
            'duration': 60,
            'cluster': "CEP4",
            'task_subtype': 'long baseline pipeline',
            'starttime': self.future_start_time,
            'endtime': self.future_stop_time,
            'storagemanager': None,
            'specification': {
                'Observation.momID': str(self.mom_id),
                'Observation.startTime': self.future_start_time,
                'Observation.stopTime': self.future_stop_time,
                'Observation.DataProducts.Output_InstrumentModel.enabled': False,
                'Observation.VirtualInstrument.stationList': [],
                'Observation.DataProducts.Input_CoherentStokes.enabled': False,
                'Observation.DataProducts.Output_CoherentStokes.enabled': False,
                'Observation.DataProducts.Input_Correlated.skip': [0, 0, 0, 0],
                'Observation.antennaSet': 'LBA_INNER',
                'Observation.nrBitsPerSample': '16',
                'Observation.ObservationControl.PythonControl.LongBaseline.subbandgroups_per_ms': '2',
                'Observation.DataProducts.Output_IncoherentStokes.enabled': False,
                'Observation.DataProducts.Input_IncoherentStokes.enabled': False,
                'Observation.DataProducts.Input_Correlated.enabled': True,
                'Observation.DataProducts.Output_Pulsar.enabled': False,
                'Observation.DataProducts.Input_CoherentStokes.skip': [],
                'Observation.DataProducts.Output_SkyImage.enabled': False,
                'Version.number': '33774',
                'Observation.ObservationControl.PythonControl.LongBaseline.subbands_per_subbandgroup': '2',
                'Observation.nrBeams': '0',
                'Observation.DataProducts.Input_IncoherentStokes.skip': [],
                'Observation.DataProducts.Output_Correlated.enabled': True,
                'Observation.DataProducts.Output_Correlated.storageClusterName': 'CEP4',
                'Observation.sampleClock': '200',
                'Observation.Cluster.ProcessingCluster.clusterName': 'CEP4'
            },
            'predecessors': [{
                'mom_id': self.predecessor_task_mom_id,
                'task_id': self.predecessor_task_id,
                'trigger_id': None,
                'status': None,
                'min_starttime': '2016-03-25 00:31:31',
                'endtime': '2016-03-25 01:31:31',
                'duration': 60,
                'min_duration': 60,
                'max_duration': 60,
                'cluster': "CEP4",
                'task_subtype': 'averaging pipeline',
                'specification': {
                    'Observation.DataProducts.Output_InstrumentModel.enabled': False,
                    'Observation.stopTime': '2016-03-25 13:51:05',
                    'Observation.VirtualInstrument.stationList': [],
                    'Observation.DataProducts.Input_CoherentStokes.enabled': False,
                    'Observation.DataProducts.Output_CoherentStokes.enabled': False,
                    'Observation.DataProducts.Output_SkyImage.enabled': False,
                    'Observation.DataProducts.Input_Correlated.skip': [0, 0, 0, 0],
                    'Observation.antennaSet': 'LBA_INNER',
                    'Observation.nrBitsPerSample': '16',
                    'Observation.ObservationControl.PythonControl.LongBaseline.subbandgroups_per_ms': '1',
                    'Observation.DataProducts.Output_IncoherentStokes.enabled': False,
                    'Observation.DataProducts.Input_IncoherentStokes.enabled': False,
                    'Observation.DataProducts.Input_Correlated.enabled': True,
                    'Observation.DataProducts.Output_Pulsar.enabled': False,
                    'Observation.DataProducts.Input_CoherentStokes.skip': [],
                    'Observation.ObservationControl.PythonControl.DPPP.demixer.demixtimestep': '10',
                    'Version.number': '33774',
                    'Observation.momID': '351556',
                    'Observation.startTime': '2016-03-25 13:49:55',
                    'Observation.ObservationControl.PythonControl.LongBaseline.subbands_per_subbandgroup': '1',
                    'Observation.nrBeams': '0',
                    'Observation.DataProducts.Input_IncoherentStokes.skip': [],
                    'Observation.ObservationControl.PythonControl.DPPP.demixer.demixfreqstep': '64',
                    'Observation.DataProducts.Output_Correlated.enabled': True,
                    'Observation.sampleClock': '200'
                },
                'task_type': 'pipeline',
                'otdb_id': 1290496,
                'predecessors': [{
                    'task_subtype': 'bfmeasurement',
                    'mom_id': 351539,
                    'task_id': 323,
                    'trigger_id': None,
                    'status': None,
                    'min_starttime': '2016-03-24 00:31:31',
                    'endtime': '2016-03-24 01:31:31',
                    'duration': 60,
                    'min_duration': 60,
                    'max_duration': 60,
                    'cluster': "CEP4",

                    'specification': {
                        'Observation.DataProducts.Output_InstrumentModel.enabled': False,
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor': '1',
                        'Observation.stopTime': '2016-03-26 00:33:31',
                        'Observation.VirtualInstrument.stationList': ['RS205', 'RS503', 'CS013', 'RS508',
                                                                       'RS106'],
                        'Observation.DataProducts.Input_CoherentStokes.enabled': False,
                        'Observation.DataProducts.Output_CoherentStokes.enabled': False,
                        'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband': '64',
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.which': 'I',
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.which': 'I',
                        'Observation.Beam[0].subbandList': [100, 101, 102, 103],
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.subbandsPerFile': '512',
                        'Observation.DataProducts.Input_Correlated.skip': [],
                        'Observation.antennaSet': 'HBA_DUAL',
                        'Observation.nrBitsPerSample': '8',
                        'Observation.Beam[0].nrTabRings': '0',
                        'Observation.Beam[0].nrTiedArrayBeams': '0',
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.flysEye': False,
                        'Observation.nrBeams': '1',
                        'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime': '1.0',
                        'Observation.DataProducts.Output_IncoherentStokes.enabled': False,
                        'Observation.DataProducts.Input_IncoherentStokes.enabled': False,
                        'Observation.DataProducts.Input_Correlated.enabled': False,
                        'Observation.DataProducts.Output_Pulsar.enabled': False,
                        'Observation.DataProducts.Input_CoherentStokes.skip': [],
                        'Observation.DataProducts.Output_SkyImage.enabled': False,
                        'Version.number': '33774',
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor': '1',
                        'Observation.momID': '351539',
                        'Observation.startTime': '2016-03-26 00:31:31',
                        'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.subbandsPerFile': '512',
                        'Observation.DataProducts.Input_IncoherentStokes.skip': [],
                        'Observation.DataProducts.Output_Correlated.enabled': True,
                        'Observation.sampleClock': '200'
                    },
                    'task_type': 'observation',
                    'otdb_id': 1290476,
                    'predecessors': [],
                    'successors': []
                }],
                'successors': []
            }],
            'successors': []
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
            "type_id": 0,
            "duration": 60,
            "cluster": "CEP4"
        }

    def setUp(self):
        super().setUp()
        self.reset_task()

        self.tmp_exchange = TemporaryExchange(__package__)
        self.tmp_exchange.open()
        self.addCleanup(self.tmp_exchange.close)

        def rerpc_mock_get_estimated_resources(specification_tree):
            otdb_id = specification_tree['otdb_id']
            return self.rerpc_replymessage[str(otdb_id)]

        rerpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.ResourceEstimatorRPC')
        self.addCleanup(rerpc_patcher.stop)
        self.rerpc_mock = rerpc_patcher.start()
        self.rerpc_mock.create.side_effect = lambda **kwargs: self.rerpc_mock # make factory method 'create' return the mock instance
        self.rerpc_mock.get_estimated_resources.side_effect = rerpc_mock_get_estimated_resources

        otdbrpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.OTDBRPC')
        self.addCleanup(otdbrpc_patcher.stop)
        self.otdbrpc_mock = otdbrpc_patcher.start()
        self.otdbrpc_mock.create.side_effect = lambda **kwargs: self.otdbrpc_mock # make factory method 'create' return the mock instance

        momrpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.MoMQueryRPC')
        self.addCleanup(momrpc_patcher.stop)
        self.momrpc_mock = momrpc_patcher.start()
        self.momrpc_mock.create.side_effect = lambda **kwargs: self.momrpc_mock # make factory method 'create' return the mock instance
        self.momrpc_mock.getPredecessorIds.return_value = {str(self.task_mom_id): [self.predecessor_task_mom_id]}
        self.momrpc_mock.getSuccessorIds.return_value = {str(self.task_mom_id): [self.successor_task_mom_id]}
        self.momrpc_mock.get_time_restrictions.return_value = {
            "minStartTime": self.task_minstarttime.strftime('%Y-%m-%dT%H:%M:%S'),
            "maxEndTime": self.task_maxendtime.strftime('%Y-%m-%dT%H:%M:%S'),
            "minDuration": str(self.task_minduration),
            "maxDuration": str(self.task_maxduration)
        }

        curpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.CleanupRPC')
        self.addCleanup(curpc_patcher.stop)
        self.curpc_mock = curpc_patcher.start()
        self.curpc_mock.create.side_effect = lambda **kwargs: self.curpc_mock # make factory method 'create' return the mock instance
        self.curpc_mock.removeTaskData.return_value = {'deleted': True, 'message': ""}

        sqrpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.StorageQueryRPC')
        self.addCleanup(sqrpc_patcher.stop)
        self.sqrpc_mock = sqrpc_patcher.start()
        self.sqrpc_mock.create.side_effect = lambda **kwargs: self.sqrpc_mock # make factory method 'create' return the mock instance
        self.sqrpc_mock.getDiskUsageForOTDBId.return_value = {'found': True, 'disk_usage': 10}

        obscontrol_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.ObservationControlRPCClient')
        self.addCleanup(obscontrol_patcher.stop)
        self.obscontrol_mock = obscontrol_patcher.start()
        self.obscontrol_mock.create.side_effect = lambda **kwargs: self.obscontrol_mock # make factory method 'create' return the mock instance

        ra_notification_bus_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.ToBus')
        self.addCleanup(ra_notification_bus_patcher.stop)
        self.ra_notification_bus_mock = ra_notification_bus_patcher.start()

        # Select logger output to see
        def myprint(s, *args):
            print(s % args if args else s, file=sys.stderr)

        logger_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()
        self.logger_mock.info.side_effect = myprint
        self.logger_mock.warn.side_effect = myprint
        self.logger_mock.error.side_effect = myprint

        self.resource_assigner = ResourceAssigner(exchange=self.tmp_exchange.address, radb_dbcreds=self.dbcreds)
        self.addCleanup(self.resource_assigner.close)

        self.reset_specification_tree()

    def assert_all_services_opened(self):
        self.assertTrue(self.rerpc_mock.open.called, "ResourceEstimatorRPC.open was not called")
        self.assertTrue(self.otdbrpc_mock.open.called, "OTDBRPC.open was not called")
        self.assertTrue(self.momrpc_mock.open.called, "MOMRPC.open was not called")
        self.assertTrue(self.curpc_mock.open.called, "CURPC.open was not called")
        self.assertTrue(any(mc for mc in self.ra_notification_bus_mock.mock_calls if 'open()' in str(mc)), "ra_notification_bus.open was not called")

    def assert_all_services_closed(self):
        self.assertTrue(self.rerpc_mock.close.called, "ResourceEstimatorRPC.close was not called")
        self.assertTrue(self.otdbrpc_mock.close.called, "OTDBRPC.close was not called")
        self.assertTrue(self.momrpc_mock.close.called, "MOMRPC.close was not called")
        self.assertTrue(self.curpc_mock.close.called, "CURPC.close was not called")
        self.assertTrue(any(mc for mc in self.ra_notification_bus_mock.mock_calls if 'close()' in str(mc)), "ra_notification_bus.close was not called")

    def test_open_opens_all_services(self):
        self.resource_assigner.open()

        self.assert_all_services_opened()

    def test_close_closes_all_services(self):
        self.resource_assigner.close()

        self.assert_all_services_closed()

    def test_contextManager_opens_and_closes_all_services(self):
        with self.resource_assigner:
            self.assert_all_services_opened()

        self.assert_all_services_closed()

    def test_do_assignment_logs_specification(self):
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        self.logger_mock.info.assert_any_call('do_assignment: otdb_id=%s specification_tree=%s',
                                              self.specification_tree['otdb_id'], self.specification_tree)

    def test_do_assignment_log_non_approved_or_prescheduled_states(self):
        otdb_id = self.non_approved_or_prescheduled_otdb_id
        status = self.non_approved_or_prescheduled_status
        spec_tree = self.non_approved_or_prescheduled_specification_tree

        with self.assertRaises(Exception):
            self.resource_assigner.do_assignment(otdb_id, spec_tree)

            assignable_task_states_str = "approved, prescheduled"
            self.logger_mock.warn.assert_any_call(
                'Task otdb_id=%s with status \'%s\' is not assignable. Allowed statuses are %s' %
                (otdb_id, status, assignable_task_states_str))

    def test_do_assignment_approved_task_should_not_be_rescheduled(self):
        otdb_id = self.specification_tree['otdb_id']
        # assure task is not known yet
        self.assertIsNone(self.radb.getTask(otdb_id=otdb_id))

        self.specification_tree['status'] = 'approved'
        self.resource_assigner.do_assignment(otdb_id, self.specification_tree)

        # assure task is known now, and scheduled
        self.assertIsNotNone(self.radb.getTask(otdb_id=otdb_id))
        self.assertEqual('approved', self.radb.getTask(otdb_id=otdb_id)['status'])

        self.logger_mock.info.assert_any_call('Task otdb_id=%s is only approved, no resource assignment needed yet' % otdb_id)

    def freeze_time_one_day_in_the_future(self, datetime_mock):
        now = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        now = self._strip_ms(now)
        datetime_mock.utcnow.return_value = now
        datetime_mock.strptime.side_effect = \
            lambda date_string, format_string: datetime.datetime.strptime(date_string, format_string)
        return now

    def _strip_ms(self, now):
        return datetime.datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

    def test_get_resource_estimates_should_request_needed_resources(self):
        self.resource_assigner._get_resource_estimates(self.specification_tree)

        self.rerpc_mock.get_estimated_resources.any_calls_with(self.specification_tree)

    def test_do_assignment_puts_spec_to_error_when_resource_estimation_gives_an_error(self):
        with mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.PriorityScheduler') as scheduler_mock:
            scheduler_mock.allocate_resources.return_value = False

            self.specification_tree["otdb_id"] = self.otdb_id + 11
            self.specification_tree['status'] = 'prescheduled'
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            task = self.radb.getTask(otdb_id=self.specification_tree["otdb_id"])
            self.assertEqual('error', task['status'])

    def test_do_assignment_should_not_claim_resouces_when_otdb_id_not_needed_resources(self):
        self.specification_tree["otdb_id"] = self.no_resources_otdb_id

        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        task = self.radb.getTask(otdb_id=self.specification_tree["otdb_id"])
        self.assertEqual([], self.radb.getResourceClaims(task_ids=task['id']))

    def test_do_assignment_should_not_claim_resources_when_task_type_not_in_needed_resources(self):
        wrong_task_type = "observation"
        self.specification_tree["task_type"] = wrong_task_type
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        task = self.radb.getTask(otdb_id=self.specification_tree["otdb_id"])
        self.assertEqual('error', task['status'])
        self.assertEqual([], self.radb.getResourceClaims(task_ids=task['id']))

    def test_do_assignment_should_log_single_errors_in_needed_resources(self):
        self.specification_tree["otdb_id"] = self.resources_with_errors_otdb_id

        with self.assertRaises(ValueError):
            self.resource_assigner._get_resource_estimates(self.specification_tree)

            self.logger_mock.error.assert_any_call("Error from Resource Estimator: %s", self.resource_error1)
            self.logger_mock.error.assert_any_call("Error from Resource Estimator: %s", self.resource_error2)

    def test_do_assignment_should_log_missing_resource_types_in_estimates(self):
        exception_string = "missing 'resource_types' in 'estimates' in estimator results: %s" % self.rerpc_replymessage[str(self.resources_with_no_resource_types_otdb_id)]
        self.specification_tree["otdb_id"] = self.resources_with_no_resource_types_otdb_id

        with self.assertRaises(ValueError) as e:
            self.resource_assigner._get_resource_estimates(self.specification_tree)

        self.assertEqual(str(e.exception), exception_string)

    def test_do_assignment_should_log_if_estimates_are_negative(self):
        self.specification_tree["otdb_id"] = self.resources_with_negative_estimates_otdb_id

        with self.assertRaisesRegexp(ValueError, "at least one of the estimates is not a positive number"):
            self.resource_assigner._get_resource_estimates(self.specification_tree)

    def ra_notification_bus_send_called_with(self, content, subject):
        for call in self.ra_notification_bus_mock().send.call_args_list:
            if isinstance(call[0][0], EventMessage):
                msg = call[0][0]
                if msg.subject == subject and msg.content == content:
                    return True
        return False

    def test_do_assignment_notifies_bus_when_it_was_unable_to_schedule_Conflict(self):
        # prepare: insert a blocking task with a huge claim on storage (directly via the radb, not via the resource_assigner)
        task_id = self.radb.insertOrUpdateSpecificationAndTask(9876, 9876, 'prescheduled', 'observation',
                                                       datetime.datetime.utcnow()-datetime.timedelta(days=1),
                                                       datetime.datetime.utcnow()+datetime.timedelta(days=1),
                                                       "", "CEP4")['task_id']
        task = self.radb.getTask(task_id)
        cep_storage_resource = next(r for r in self.radb.getResources(resource_types='storage', include_availability=True) if 'CEP4' in r['name'])
        self.radb.insertResourceClaim(cep_storage_resource['id'], task_id, task['starttime'], task['endtime'],
                                      0.75*cep_storage_resource['total_capacity'], "", 0)
        self.radb.updateTaskAndResourceClaims(task_id, claim_status='claimed', task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # make sure the estimater mock asks for too much storage which wont fit during scheduling
        def rerpc_mock_get_estimated_resources(specification_tree):
            otdb_id = specification_tree['otdb_id']
            estimates = deepcopy(self.rerpc_replymessage[str(otdb_id)])
            estimates['estimates'][0]['resource_types']['storage'] = 0.75*cep_storage_resource['total_capacity']
            return estimates
        self.rerpc_mock.get_estimated_resources.side_effect = rerpc_mock_get_estimated_resources

        # now test the resource_assigner.do_assignment. Should not succeed. Task and claims should go to conflict status.
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        # check if task is in the radb, and if status is in conflict
        resulting_task = self.radb.getTask(otdb_id=self.specification_tree['otdb_id'])
        self.assertIsNotNone(resulting_task)
        self.assertEqual('conflict', resulting_task['status'])

        # check if TaskConflict notification was logged and send
        content = {'radb_id': resulting_task['id'], 'otdb_id': resulting_task['otdb_id'], 'mom_id': resulting_task['mom_id']}
        subject = 'TaskConflict'
        self.assertBusNotificationAndLogging(content, subject)

    def test_do_assignment_notifies_bus_when_it_was_unable_to_schedule_Error(self):
        # make sure the estimater mock asks for more storage than available resulting in TaskError
        def rerpc_mock_get_estimated_resources(specification_tree):
            otdb_id = specification_tree['otdb_id']
            estimates = deepcopy(self.rerpc_replymessage[str(otdb_id)])
            cep_storage_resource = next(r for r in
                                        self.radb.getResources(resource_types='storage', include_availability=True)
                                        if 'CEP4' in r['name'])
            estimates['estimates'][0]['resource_types']['storage'] = 1+cep_storage_resource['total_capacity']
            return estimates
        self.rerpc_mock.get_estimated_resources.side_effect = rerpc_mock_get_estimated_resources

        # now test the resource_assigner.do_assignment. Should not succeed. Task should go to error status.
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        # check if task is in the radb, and if status is in error
        resulting_task = self.radb.getTask(otdb_id=self.specification_tree['otdb_id'])
        self.assertIsNotNone(resulting_task)
        self.assertEqual('error', resulting_task['status'])

        # check if TaskError notification was logged and send
        content = {'radb_id': resulting_task['id'], 'otdb_id': resulting_task['otdb_id'], 'mom_id': resulting_task['mom_id']}
        subject = 'TaskError'
        self.assertBusNotificationAndLogging(content, subject)

    def test_do_assignment_should_set_status_to_error_again_when_cant_schedule_and_not_in_conflict(self):
        # make sure the estimater mock asks for more storage than available resulting in TaskError
        def rerpc_mock_get_estimated_resources(specification_tree):
            otdb_id = specification_tree['otdb_id']
            estimates = deepcopy(self.rerpc_replymessage[str(otdb_id)])
            cep_storage_resource = next(r for r in
                                        self.radb.getResources(resource_types='storage', include_availability=True)
                                        if 'CEP4' in r['name'])
            estimates['estimates'][0]['resource_types']['storage'] = 1+cep_storage_resource['total_capacity']
            return estimates
        self.rerpc_mock.get_estimated_resources.side_effect = rerpc_mock_get_estimated_resources

        # check if the task assignment results in an error twice (apparently it didn't someday for whatever reason)
        for i in range(2):
            self.specification_tree['status'] = 'prescheduled'
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            # check if task is in the radb, and if status is in error
            resulting_task = self.radb.getTask(otdb_id=self.specification_tree['otdb_id'])
            self.assertIsNotNone(resulting_task)
            self.assertEqual('error', resulting_task['status'])

            # check if TaskError notification was logged and send
            content = {'radb_id': resulting_task['id'], 'otdb_id': resulting_task['otdb_id'], 'mom_id': resulting_task['mom_id']}
            subject = 'TaskError'
            self.assertBusNotificationAndLogging(content, subject)

            # reset the mock calls for next round
            self.ra_notification_bus_mock().send.reset_mock()
            self.logger_mock.info.send.reset_mock()

    def test_do_assignment_logs_task_data_removal_if_task_is_pipeline(self):
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        self.logger_mock.info.assert_any_call("removing data on disk from previous run for otdb_id %s", self.otdb_id)

    def test_do_assignment_removes_task_data_if_task_is_pipeline(self):
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        self.curpc_mock.removeTaskData.assert_any_call(self.specification_tree['otdb_id'])

    def test_do_assignment_logs_when_taks_data_could_not_be_deleted(self):
        message = "file was locked"
        self.curpc_mock.removeTaskData.return_value = {'deleted': False, 'message': message}

        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        self.logger_mock.warning.assert_any_call(
            "could not remove all data on disk from previous run for otdb_id %s: %s", self.otdb_id, message)

    def test_do_assignment_logs_exception_from_curcp_removeTaskData(self):
        exception_str = "Error something went wrong"
        self.curpc_mock.removeTaskData.side_effect = Exception(exception_str)

        otdb_id = self.specification_tree['otdb_id']
        # assure task is not known yet
        self.assertIsNone(self.radb.getTask(otdb_id=otdb_id))

        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(otdb_id, self.specification_tree)

        self.logger_mock.error.assert_any_call("Exception in cleaning up earlier data: %s", exception_str)

    def test_do_assignment_notifies_bus_when_task_is_scheduled(self):
        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

        # check if task is in the radb, and if status is scheduled
        resulting_task = self.radb.getTask(otdb_id=self.specification_tree['otdb_id'])
        self.assertIsNotNone(resulting_task)
        self.assertEqual('scheduled', resulting_task['status'])

        # check if TaskScheduled notification was logged and send
        content = {'radb_id': resulting_task['id'], 'otdb_id': resulting_task['otdb_id'], 'mom_id': resulting_task['mom_id']}
        subject = 'TaskScheduled'
        self.assertBusNotificationAndLogging(content, subject)

    def test_do_assignement_set_status_on_spec_when_scheduleable(self):
        otdb_id = self.specification_tree['otdb_id']
        # assure task is not known yet
        self.assertIsNone(self.radb.getTask(otdb_id=otdb_id))

        self.specification_tree['status'] = 'prescheduled'
        self.resource_assigner.do_assignment(otdb_id, self.specification_tree)

        # assure task is known now, and scheduled
        self.assertIsNotNone(self.radb.getTask(otdb_id=otdb_id))
        self.assertEqual('scheduled', self.radb.getTask(otdb_id=otdb_id)['status'])

    def assertBusNotificationAndLogging(self, content, subject):
        self.assertTrue(self.ra_notification_bus_send_called_with(content, "%s.%s" %(DEFAULT_RA_NOTIFICATION_PREFIX, subject)))
        self.logger_mock.info.assert_any_call('Sending notification %s: %s' %
                                              (subject, single_line_with_single_spaces(content)))

    def test_do_assignment_logs_exception_from_otdbrpc_taskSetSpecification_with_mom_bug(self):
        exception_str = "Error something went wrong"
        self.otdbrpc_mock.taskSetSpecification.side_effect = Exception(exception_str)

        with self.assertRaisesRegexp(Exception, exception_str):
            self.mom_bug_specification_tree['status'] = 'prescheduled'
            self.resource_assigner.do_assignment(self.mom_bug_specification_tree['otdb_id'],
                                                 self.mom_bug_specification_tree)

            self.logger_mock.error.assert_any_call(exception_str)

    def test_do_assignment_logs_exception_from_rerpc(self):
        exception_msg = "Error something went wrong"
        self.rerpc_mock.side_effect = Exception(exception_msg)

        with self.assertRaisesRegexp(Exception, exception_msg):
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            self.logger_mock.error.assert_any_call(exception_msg)

    def test_do_assignment_logs_when_notifies_bus_thows_exception(self):
        exception_msg = "Error something went wrong"
        self.ra_notification_bus_mock.send.side_effect = Exception(exception_msg)

        with self.assertRaisesRegexp(Exception, exception_msg):
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            self.logger_mock.error.assert_any_call(exception_msg)

    def test_do_assignment_logs_when_momrpc_getPredecessorIds_throws_exception(self):
        exception_msg = "Error something went wrong"
        self.momrpc_mock.getPredecessorIds.side_effect = Exception(exception_msg)

        with self.assertRaisesRegexp(Exception, exception_msg):
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            self.logger_mock.error.assert_any_call(exception_msg)

    def test_do_assignment_logs_when_momrpc_getSuccessorIds_throws_exception(self):
        exception_msg = "Error something went wrong"
        self.momrpc_mock.getSuccessorIds.side_effect = Exception(exception_msg)

        with self.assertRaisesRegexp(Exception, exception_msg):
            self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

            self.logger_mock.error.assert_any_call(exception_msg)

    def test_kill_task(self):
        spec = Specification(None, None, None)  # Easier than creating a custom object instance
        spec.radb_id = 1
        spec.mom_id = 2
        spec.otdb_id = 3
        spec.status = "aborted"
        spec.type = "observation"
        self.resource_assigner._kill_task(spec)
        self.obscontrol_mock.abort_observation.assert_called_with(spec.otdb_id)

    # SW-800 The schedulers need open and close called (using context manager)
    def test_do_assignement_uses_context_manager_on_schedulers(self):
        with mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.BasicScheduler') as basic_scheduler_mock:
            with mock.patch('lofar.sas.resourceassignment.resourceassigner.resource_assigner.PriorityScheduler') as prio_scheduler_mock:
                basic_scheduler_mock().allocate_resources.return_value = (False, None)
                prio_scheduler_mock().allocate_resources.return_value = (False, None)

                self.specification_tree['status'] = 'prescheduled'
                self.resource_assigner.do_assignment(self.specification_tree['otdb_id'], self.specification_tree)

                basic_scheduler_mock().__enter__.assert_called()
                basic_scheduler_mock().__exit__.assert_called()

                prio_scheduler_mock().__enter__.assert_called()
                prio_scheduler_mock().__exit__.assert_called()

    #This class is currently missing any tests of interaction between tasks already scheduled and new tasks,
    # e.g. triggered ones. It would require a totally different way to set up the tests to be able to test this.

    def test_do_assignment_does_not_raise_on_inserting_predecessors(self):
        '''SW-816: When scheduling a successor task, it failed on 'duplicate key value violates unique constraint "task_predecessor_unique"' error in the radb.
        This test proves correct/expected behaviour.'''
        predecessor_spec = deepcopy(self.specification_tree)
        predecessor_otdb_id = predecessor_spec['otdb_id']
        predecessor_spec['status'] = 'prescheduled'
        predecessor_spec['predecessors'] = []
        self.resource_assigner.do_assignment(predecessor_otdb_id, predecessor_spec)

        # check if task is in the radb, and if status is scheduled
        predecessor_task = self.radb.getTask(otdb_id=predecessor_otdb_id)
        self.assertIsNotNone(predecessor_task)
        self.assertEqual('scheduled', predecessor_task['status'])


        successor_spec = deepcopy(self.specification_tree)
        successor_spec['otdb_id'] += 1000
        successor_spec['mom_id'] += 1000
        successor_otdb_id = successor_spec['otdb_id']
        successor_spec['status'] = 'prescheduled'
        successor_spec['predecessors'] = [predecessor_spec]

        # let the mocked resource estimator return the same estimates for this new otdb_id+1000
        def rerpc_mock_get_estimated_resources(specification_tree):
            otdb_id = specification_tree['otdb_id']-1000
            return self.rerpc_replymessage[str(otdb_id)]
        self.rerpc_mock.get_estimated_resources.side_effect = rerpc_mock_get_estimated_resources

        # let the momrpc_mock provide the proper linkage between the tasks
        self.momrpc_mock.getPredecessorIds.return_value = {str(successor_spec['mom_id']): [predecessor_spec['mom_id']]}
        self.momrpc_mock.getSuccessorIds.return_value = {str(predecessor_spec['mom_id']): [successor_spec['mom_id']]}

        # it should be possible to scheduled the successor twice and link it twice to the predecessor.
        # the second time, it should just be 'cleaned-up' and rescheduled/relinked.
        for i in range(2):
            self.resource_assigner.do_assignment(successor_otdb_id, successor_spec)

            # check if task is in the radb, and if status is scheduled
            successor_task = self.radb.getTask(otdb_id=successor_otdb_id)
            self.assertIsNotNone(successor_task)
            self.assertEqual('scheduled', successor_task['status'])
            self.assertEqual([predecessor_task['id']], successor_task['predecessor_ids'], )

            # check if predecessor_task is also linked to its successor
            predecessor_task = self.radb.getTask(otdb_id=predecessor_otdb_id)
            self.assertEqual([successor_task['id']], predecessor_task['successor_ids'], )

    def test_scheduling_of_trigger_observation_when_running_observation_is_killed(self):
        '''SW-907: Trigger observation cannot be scheduled when it needs to abort a running observation.
        When a Trigger observation is set to prescheduled, and enters the whole do-schedule logic in the resourceassigner,
        and it has to kill a running observation, then the (stupidly implemented conflict-resolution) causes the trigger observation
        to be set to approved.
        The resource assigner should be able to handle that, or prevent that.'''

        # prepare: insert a blocking task with a huge claim on storage (directly via the radb, not via the resource_assigner)
        task_id = self.radb.insertOrUpdateSpecificationAndTask(9876, 9876, 'approved', 'observation',
                                                       datetime.datetime.utcnow()-datetime.timedelta(days=1),
                                                       datetime.datetime.utcnow()+datetime.timedelta(days=1),
                                                       "", "CEP4")['task_id']
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])
        cep_storage_resource = next(r for r in self.radb.getResources(resource_types='storage', include_availability=True) if 'CEP4' in r['name'])
        claim_id = self.radb.insertResourceClaim(cep_storage_resource['id'], task_id, task['starttime'], task['endtime'],
                                                 0.75*cep_storage_resource['total_capacity'], "", 0)
        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTaskAndResourceClaims(task_id, claim_status='claimed', task_status='prescheduled')
        self.assertEqual('prescheduled', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # simulate that the task is running...
        self.radb.updateTask(task_id, task_status='queued')
        self.radb.updateTask(task_id, task_status='active')
        self.assertEqual('active', self.radb.getTask(task_id)['status'])

        # create a second task (caused by a trigger)
        task2_id = self.radb.insertOrUpdateSpecificationAndTask(8765, 8765, 'approved', 'observation',
                                                       datetime.datetime.utcnow(),
                                                       datetime.datetime.utcnow()+datetime.timedelta(hours=1),
                                                       "", "CEP4")['task_id']
        task2 = self.radb.getTask(task2_id)
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

        # mimic that a trigger comes in and sets the observation to prescheduled...
        self.radb.updateTaskAndResourceClaims(task2_id, task_status='prescheduled')
        self.assertEqual('prescheduled', self.radb.getTask(task2_id)['status'])

        # try to claim some resources (more than available, causing a conflict)
        claim2_id = self.radb.insertResourceClaim(cep_storage_resource['id'], task2_id, task2['starttime'], task2['endtime'],
                                                  0.75*cep_storage_resource['total_capacity'], "", 0)

        # this 2nd (trigger) task should not be schedulable (because the running task is in the way)
        self.assertEqual('conflict', self.radb.getResourceClaims(claim2_id)[0]['status'])
        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

        # now mimic the PriorityScheduler's behaviour, and kill task1, ending it now.
        self.radb.updateTaskAndResourceClaims(task_id, task_status='aborted', endtime=task2['starttime'])

        # as a result task2 should now be schedulable with tentative claim, and in prescheduler state.
        self.assertEqual('tentative', self.radb.getResourceClaims(claim2_id)[0]['status'])

        # THE ROOT-CAUSE OF BUG SW-907 is that task2 used to get the approved state in via an RADB trigger function.
        # That has unforeseen sideeffects in the resourceassigner.
        # SO, let's test here if the status of task2 is now the expected 'prescheduled' as it was before it went to conflict.
        self.assertEqual('prescheduled', self.radb.getTask(task2_id)['status'])




if __name__ == '__main__':
    unittest.main()
