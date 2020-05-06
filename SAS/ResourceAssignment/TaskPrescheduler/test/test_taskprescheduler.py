#!/usr/bin/env python3

# Copyright (C) 2012-2015    ASTRON (Netherlands Institute for Radio Astronomy)
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

# $Id:  $
import unittest, datetime
from unittest import mock

# you might need to install mock, mysql.connector(from Oracle), testing.mysqld, mock, coverage,
# lxml, xmljson, django, djangorestframework, djangorestframework_xml, python3-ldap, six, qpid, mllib
# using things like sudo pip install <package>

from lofar.sas.resourceassignment.taskprescheduler.taskprescheduler import TaskPreschedulerEventHandler
from lofar.sas.resourceassignment.taskprescheduler.taskprescheduler import calculateCobaltSettings
from lofar.sas.resourceassignment.taskprescheduler.taskprescheduler import cobaltOTDBsettings
from lofar.sas.resourceassignment.taskprescheduler.taskprescheduler import main as PreschedulerMain
from lofar.sas.resourceassignment.common.specification import Specification

class TestingTaskPreschedulerEventHandler(TaskPreschedulerEventHandler):
    def __init__(self, otdbrpc, momrpc, radb):
        # super gets not done to be able to insert mocks as early as possible otherwise the RPC block unittesting
        self.otdbrpc = otdbrpc
        self.momquery = momrpc
        self.radb = radb

class PreschedulerTest(unittest.TestCase):
    # No __init__ because that confuses unittest.main()

    def reset_specification_tree(self, otdb_id, mom_id, future_start_time, future_stop_time):
        self.pipeline_specification_tree = {
            'ObsSW.Observation.DataProducts.Output_InstrumentModel.enabled': False,
            'ObsSW.Observation.stopTime': future_stop_time,
            'ObsSW.Observation.VirtualInstrument.stationList': [],
            'ObsSW.Observation.DataProducts.Input_CoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Output_CoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Output_SkyImage.enabled': False,
            'ObsSW.Observation.DataProducts.Input_Correlated.skip': [0, 0, 0, 0],
            'ObsSW.Observation.antennaSet': 'LBA_INNER',
            'ObsSW.Observation.nrBitsPerSample': 16,
            'ObsSW.Observation.ObservationControl.PythonControl.LongBaseline.subbandgroups_per_ms': 1,
            'ObsSW.Observation.DataProducts.Output_IncoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Input_IncoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Input_Correlated.enabled': True,
            'ObsSW.Observation.DataProducts.Output_Pulsar.enabled': False,
            'ObsSW.Observation.DataProducts.Input_CoherentStokes.skip': [],
            'ObsSW.Observation.ObservationControl.PythonControl.DPPP.demixer.demixtimestep': 10,
            'Version.number': 33774,
            'ObsSW.Observation.momID': mom_id,
            'ObsSW.Observation.startTime': future_start_time,
            'ObsSW.Observation.ObservationControl.PythonControl.LongBaseline.subbands_per_subbandgroup': 1,
            'ObsSW.Observation.nrBeams': 0,
            'ObsSW.Observation.DataProducts.Input_IncoherentStokes.skip': [],
            'ObsSW.Observation.ObservationControl.PythonControl.DPPP.demixer.demixfreqstep': 64,
            'ObsSW.Observation.DataProducts.Output_Correlated.enabled': True,
            'ObsSW.Observation.DataProducts.Output_Correlated.storageClusterName': 'CEP4',
            'ObsSW.Observation.sampleClock': 200,
            'ObsSW.Observation.processType': 'Pipeline',
            'ObsSW.Observation.processSubtype': 'Averaging Pipeline',
            'ObsSW.Observation.Scheduler.predecessors': '[]',
        }

        self.observation_specification_tree = {
            'ObsSW.Observation.DataProducts.Output_InstrumentModel.enabled': False,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.nrChannelsPerSubband': 64,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor': 1,
            'ObsSW.Observation.stopTime': future_stop_time,
            'ObsSW.Observation.VirtualInstrument.stationList': ['RS205', 'RS503', 'CS013', 'RS508', 'RS106'],
            'ObsSW.Observation.DataProducts.Input_CoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Output_CoherentStokes.enabled': True,
            'ObsSW.Observation.DataProducts.Output_CoherentStokes.storageClusterName': 'CEP4',
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband': 64,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.which': 'I',
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.which': 'I',
            'ObsSW.Observation.Beam[0].subbandList': '[100, 101, 102, 103]',
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.subbandsPerFile': 512,
            'ObsSW.Observation.DataProducts.Input_Correlated.skip': [],
            'ObsSW.Observation.antennaSet': 'HBA_DUAL',
            'ObsSW.Observation.nrBitsPerSample': 8,
            'ObsSW.Observation.Beam[0].nrTabRings': 0,
            'ObsSW.Observation.Beam[0].nrTiedArrayBeams': 0,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.flysEye': False,
            'ObsSW.Observation.nrBeams': 1,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime': 1.0,
            'ObsSW.Observation.DataProducts.Output_IncoherentStokes.enabled': True,
            'ObsSW.Observation.DataProducts.Output_IncoherentStokes.storageClusterName': 'CEP4',
            'ObsSW.Observation.DataProducts.Input_IncoherentStokes.enabled': False,
            'ObsSW.Observation.DataProducts.Input_Correlated.enabled': False,
            'ObsSW.Observation.DataProducts.Output_Pulsar.enabled': False,
            'ObsSW.Observation.DataProducts.Input_CoherentStokes.skip': [],
            'ObsSW.Observation.DataProducts.Output_SkyImage.enabled': False,
            'Version.number': 33774,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.nrChannelsPerSubband': 64,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor': 1,
            'ObsSW.Observation.momID': mom_id,
            'ObsSW.Observation.startTime': future_start_time,
            'ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.subbandsPerFile': 512,
            'ObsSW.Observation.DataProducts.Input_IncoherentStokes.skip': [],
            'ObsSW.Observation.DataProducts.Output_Correlated.enabled': True,
            'ObsSW.Observation.DataProducts.Output_Correlated.storageClusterName': 'CEP4',
            'ObsSW.Observation.sampleClock': 200,
            'ObsSW.Observation.processType': 'Observation',
            'ObsSW.Observation.processSubtype': 'Beam Observation',
            'ObsSW.Observation.Scheduler.predecessors': '[]',
        }

        self.test_specification = {
            'Version.number': 33774,
            'Observation.momID': mom_id,
            'Observation.sampleClock': 200,
            'Observation.DataProducts.Output_Correlated.enabled': True,
            'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband': 64,
            'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime': 1.0,
            'Observation.DataProducts.Output_CoherentStokes.enabled': True,
            'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.nrChannelsPerSubband': 4,
            'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor': 1,
            'Observation.DataProducts.Output_IncoherentStokes.enabled': True,
            'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.nrChannelsPerSubband': 64,
            'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor': 1,
        }

        self.test_cobalt_settings = {
            'blockSize': 196608, 'nrBlocks': 1, 'integrationTime': 1.00663296, 'nrSubblocks': 1
        }

        self.otdb_info = {
            'LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrBlocksPerIntegration': 1,
            'LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.blockSize': 196608,
            'LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime': 1.00663296,
            'LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrIntegrationsPerBlock': 1
        }

    def setUp(self):
        # init
        self.mom_id = 351557
        self.otdb_id = 1290494
        self.trigger_id = 2323
        future_start_time = (datetime.datetime.utcnow() + datetime.timedelta(hours = 1)).strftime('%Y-%m-%d %H:%M:%S')
        future_stop_time = (datetime.datetime.utcnow() + datetime.timedelta(hours = 2)).strftime('%Y-%m-%d %H:%M:%S')

        self.reset_specification_tree(self.otdb_id, self.mom_id, future_start_time, future_stop_time)
        otdbrpc_patcher = mock.patch('lofar.sas.otdb.otdbrpc')
        self.addCleanup(otdbrpc_patcher.stop)
        self.otdbrpc_mock = otdbrpc_patcher.start()
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': self.otdb_id, 'specification': self.observation_specification_tree}
        self.otdbrpc_mock.setOTDBinfo.return_value = {}

        momrpc_patcher = mock.patch('lofar.mom.momqueryservice.momqueryrpc')
        self.addCleanup(momrpc_patcher.stop)
        self.momrpc_mock = momrpc_patcher.start()
        self.momrpc_mock.getMoMIdsForOTDBIds.return_value = {self.otdb_id: self.mom_id}
        # self.momrpc_mock.get_trigger_id.return_value = {'status': 'OK', 'trigger_id': self.trigger_id}
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"trigger_id": self.trigger_id}
        radb_patcher = mock.patch('lofar.sas.resourceassignment.database.radb.RADatabase')
        self.addCleanup(radb_patcher.stop)
        self.radb_mock = radb_patcher.start()
        task = {"id": 1, "mom_id": self.mom_id, "otdb_id": self.otdb_id, "status": "approved",
                "type": "observation", "duration": 3600, "cluster": "CEP4"}
        self.radb_mock.getTask.return_value = task
        self.radb_mock.getResourceGroupNames.return_value = [{'name':'CEP4'}]

        self.taskprescheduler = TestingTaskPreschedulerEventHandler(self.otdbrpc_mock, self.momrpc_mock, self.radb_mock)

    def assert_all_services_opened(self):
        self.assertTrue(self.otdbrpc_mock.open.called, "OTDBRPC.open was not called")
        self.assertTrue(self.momrpc_mock.open.called, "MOMRPC.open was not called")
        self.assertTrue(self.radb_mock.connect.called, "radb.connect was not called")

    def assert_all_services_closed(self):
        self.assertTrue(self.otdbrpc_mock.close.called, "OTDBRPC.close was not called")
        self.assertTrue(self.momrpc_mock.close.called, "MOMRPC.close was not called")
        self.assertTrue(self.radb_mock.disconnect.called, "radb.disconnect was not called")

    @mock.patch("lofar.messaging.messagebus.AbstractMessageHandler.start_handling")
    def test_open_opens_all_services(self, mock_super):
        self.taskprescheduler.start_handling()
        self.assert_all_services_opened()
        self.assertTrue(mock_super.called)

    @mock.patch("lofar.messaging.messagebus.AbstractMessageHandler.stop_handling")
    def test_close_closes_all_services(self, mock_super):
        self.taskprescheduler.stop_handling()
        self.assert_all_services_closed()
        self.assertTrue(mock_super.called)

    def test_onTaskApproved_GetSpecification(self):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskGetSpecification.assert_any_call(otdb_id = self.otdb_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    # def test_resourceIndicatorsFromParset(self):
    #     specification = resourceIndicatorsFromParset(self.observation_specification_tree)
    #     self.assertEqual(specification, self.test_specification)

    def test_CobaltOTDBsettings(self):
        otdb_info = cobaltOTDBsettings(self.test_cobalt_settings)

        # beware! assertEqual succeeds for a comparison between 42.0 and 42
        # but for lofar specs it is essential that some values are int
        # so, check specifically for those!
        self.assertEqual(otdb_info, self.otdb_info)
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrBlocksPerIntegration']))
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrIntegrationsPerBlock']))
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.blockSize']))

    @mock.patch('lofar.sas.resourceassignment.common.specification.logger')
    def test_onTaskApproved_log_mom_id_found(self, logger_mock):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.info.assert_any_call('Found mom_id %s for otdb_id %s', self.mom_id, self.otdb_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    @mock.patch('lofar.sas.resourceassignment.common.specification.logger')
    def test_onTaskApproved_log_mom_id_not_found(self, logger_mock):
        observation_specification_tree_no_momid = self.observation_specification_tree
        observation_specification_tree_no_momid['ObsSW.Observation.momID'] = ''
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': self.otdb_id,
                                                               'specification': observation_specification_tree_no_momid}
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.info.assert_any_call('Did not find a mom_id for task otdb_id=%s', self.otdb_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    @mock.patch('lofar.sas.resourceassignment.common.specification.logger')
    def test_onTaskApproved_otdb_specification_problem(self, logger_mock):
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': 0, 'specification': ''}
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.exception.assert_called()
        logger_mock.error.assert_called()
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()
        # TODO not sure how to fix self.radb_mock.updateTaskStatusForOtdbId.assert_any_call(self.otdb_id, 'error')

    @mock.patch('lofar.sas.resourceassignment.common.specification.logger')
    def test_onTaskApproved_log_trigger_found_0(self, logger_mock):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.info.assert_any_call('Found a task mom_id=%s with a trigger_id=%s', self.mom_id, self.trigger_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    @mock.patch('lofar.sas.resourceassignment.taskprescheduler.taskprescheduler.logger')
    def test_onTaskApproved_log_no_trigger(self, logger_mock):
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"trigger_id": None}
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.info.assert_any_call('Did not find a trigger for task mom_id=%s', self.mom_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_onTaskApproved_no_trigger(self):
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"trigger_id": None}
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskSetStatus.assert_not_called()
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    @mock.patch('lofar.sas.resourceassignment.taskprescheduler.taskprescheduler.logger')
    def test_onTaskApproved_log_trigger_found_1(self, logger_mock):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        logger_mock.info.assert_any_call('Setting status to prescheduled for otdb_id %s so the resourceassigner can schedule the observation', self.otdb_id)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_onTaskApproved_SetSpecification(self):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskSetSpecification.assert_any_call(self.otdb_id, self.otdb_info)
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_onTaskApproved_pipeline_not_SetSpecification(self):
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': self.otdb_id,
                                                               'specification': self.pipeline_specification_tree}
        task = {"id": 1, "mom_id": self.mom_id, "otdb_id": self.otdb_id, "status": "approved",
                "type": "pipeline", "duration": 3600, "cluster": "CEP4"}
        self.radb_mock.getTask.return_value = task
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskSetSpecification.assert_not_called()
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_onTaskApproved_taskSetStatus(self):
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskSetStatus.assert_any_call(self.otdb_id, 'prescheduled')
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_onTaskApproved_pipeline_not_taskSetStatus(self):
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': self.otdb_id,
                                                               'specification': self.pipeline_specification_tree}
        task = {"id": 1, "mom_id": self.mom_id, "otdb_id": self.otdb_id, "status": "approved",
                "type": "pipeline", "duration": 3600, "cluster": "CEP4"}
        self.radb_mock.getTask.return_value = task
        self.taskprescheduler.onTaskApproved({'otdb_id': self.otdb_id})
        self.otdbrpc_mock.taskSetStatus.assert_not_called()
        self.radb_mock.insertOrUpdateSpecificationAndTask.assert_not_called()

    def test_calculateCobaltSettings(self):
        spec = Specification(self.otdbrpc_mock, self.momrpc_mock, self.radb_mock)
        spec.internal_dict = self.test_specification
        cobalt_settings = calculateCobaltSettings(spec)

        # beware! assertEqual succeeds for a comparison between 42.0 and 42
        # but for lofar specs it is essential that some values are int
        # so, check specifically for those!
        self.assertEqual(cobalt_settings, self.test_cobalt_settings)
        self.assertEqual(int, type(cobalt_settings['blockSize']))
        self.assertEqual(int, type(cobalt_settings['nrBlocks']))
        self.assertEqual(int, type(cobalt_settings['nrSubblocks']))

    def test_calculateCobaltSettingsAndConvertToOTDBsettings(self):
        '''combination of test_CobaltOTDBsettings and test_calculateCobaltSettings
        Make sure that the values are calculated and converted correctly'''
        spec = Specification(self.otdbrpc_mock, self.momrpc_mock, self.radb_mock)
        spec.internal_dict = self.test_specification
        otdb_info = cobaltOTDBsettings(calculateCobaltSettings(spec))

        # beware! assertEqual succeeds for a comparison between 42.0 and 42
        # but for lofar specs it is essential that some values are int
        # so, check specifically for those!
        self.assertEqual(otdb_info, self.otdb_info)
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrBlocksPerIntegration']))
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrIntegrationsPerBlock']))
        self.assertEqual(int, type(otdb_info['LOFAR.ObsSW.Observation.ObservationControl.OnlineControl.Cobalt.blockSize']))

    @mock.patch("lofar.common.util.waitForInterrupt")
    @mock.patch("lofar.messaging.messagebus.BusListener.start_listening")
    def test_main(self, mock_wait, mock_otdbbuslistener):
        PreschedulerMain()
        mock_wait.assert_called()

if __name__ == "__main__":
    unittest.main()
