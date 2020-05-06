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
import unittest, os
from unittest import mock

from lofar.parameterset import parameterset
from datetime import datetime, timedelta

# you might need to install mock, mysql.connector(from Oracle), testing.mysqld, mock, coverage,
# lxml, xmljson, django, djangorestframework, djangorestframework_xml, python3-ldap, six, qpid, mllib
# using things like sudo pip3 install <package>

from lofar.sas.resourceassignment.common.specification import Specification
from lofar.sas.resourceassignment.common.specification import INPUT_PREFIX, OUTPUT_PREFIX

class General(unittest.TestCase):
    def setUp(self):
        _, filename = os.path.split(__file__)
        self.data_sets_filename_prefix, _ = os.path.splitext(filename)
        self.data_sets_dir = "test_specification.in_datasets"

        self.otdbrpc_mock = mock.MagicMock()
        self.momrpc_mock = mock.MagicMock()
        self.radbrpc_mock = mock.MagicMock()
        self.logger_mock = mock.MagicMock()

        self.specification = Specification(self.otdbrpc_mock,
                                           self.momrpc_mock, self.radbrpc_mock)

    # ----------------------------------------------------------------------------------------------
    # Tests of functions to read values from MoM

    def test_read_from_mom_with_misc_info(self):
        """ Verify that get_specification properly generates an RA parset subset for a preprocessing
            pipeline parset """
        # Arrange
        min_start_time = datetime(2017, 10, 2, 22, 43, 12)
        max_end_time = datetime(2017, 10, 3, 22, 43, 12)
        min_duration = timedelta(seconds = 200)
        max_duration = timedelta(seconds = 3600)
        storagemanager = "dysco"
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"minStartTime": min_start_time,
                                                                       "maxEndTime": max_end_time,
                                                                       "minDuration": min_duration,
                                                                       "maxDuration": max_duration}
        self.momrpc_mock.get_storagemanager.return_value = storagemanager
        self.specification.mom_id = 1

        # Act
        self.specification.read_from_mom()

        # Assert
        self.assertEqual(self.specification.min_starttime, min_start_time)
        self.assertEqual(self.specification.max_endtime, max_end_time)
        self.assertEqual(self.specification.min_duration, min_duration)
        self.assertEqual(self.specification.max_duration, max_duration)
        self.assertEqual(self.specification.storagemanager, storagemanager)

    def test_read_from_mom_without_misc_info(self):
        """ Verify that get_specification properly generates an RA parset subset for a preprocessing
            pipeline parset """
        # Arrange
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"minStartTime": None,
                                                                       "minDuration": None,
                                                                       "maxDuration": None,
                                                                       "maxEndTime": None,
                                                                       "trigger_id": None}
        self.momrpc_mock.get_storagemanager.side_effect = KeyError('No "storagemanager" key in misc')
        self.specification.mom_id = 1

        # Act
        with mock.patch.object(self.specification, 'set_status') as status_mock:
            self.specification.read_from_mom()

            # Assert
            # Note that whatever was set in specification will be overridden here because momrpc returns defaults
            # on an empty misc field
            self.assertEqual(self.specification.min_starttime, None)
            self.assertEqual(self.specification.max_endtime, None)
            self.assertEqual(self.specification.min_duration, timedelta(0))    # None is translated to timedelta(0)
            self.assertEqual(self.specification.max_duration, timedelta(0))    # None is translated to timedelta(0)
            self.assertEqual(self.specification.storagemanager, None)    # default
            status_mock.assert_not_called()

    def test_read_from_mom_without_mom_id(self):
        """ Verify that get_specification properly generates an RA parset subset for a preprocessing pipeline parset """
        # Arrange
        self.momrpc_mock.get_trigger_time_restrictions.return_value = {"minStartTime": None,
                                                                       "minDuration": None,
                                                                       "maxDuration": None,
                                                                       "maxEndTime": None,
                                                                       "trigger_id": None}
        self.momrpc_mock.get_storagemanager.side_effect = ValueError('No match for MoM id')
        self.specification.mom_id = 1

        # Act
        with mock.patch.object(self.specification, 'set_status') as status_mock:
            self.specification.read_from_mom()

            # Assert
            # Note that whatever was set in specification will be overridden here because momrpc returns defaults on
            # and empty misc field
            self.assertEqual(self.specification.min_starttime, None)
            self.assertEqual(self.specification.max_endtime, None)
            self.assertEqual(self.specification.min_duration, timedelta(0))    # None is translated to timedelta(0)
            self.assertEqual(self.specification.max_duration, timedelta(0))    # None is translated to timedelta(0)
            self.assertEqual(self.specification.storagemanager, None)
            status_mock.assert_called_with('error')

    # ------------------------------------------------------------------------------------------------------------------
    # Tests of resourceIndicatorsFromParset one for each type of input parset, might duplicate code in RATaskSpecified

    def test_preprocessing_pipeline(self):
        """ Verify that get_specification properly generates an RA parset subset for a preprocessing
            pipeline parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_preprocessing")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'pipeline')
        self.assertEqual(input_subtype, 'averaging pipeline')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.storageClusterName'],
                         'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.identifications'],
                         ['mom.G737227.B1.1.PT2.uv.dps'])
        self.assertEqual(result['Observation.DataProducts.Output_InstrumentModel.enabled'], False)
        self.assertEqual(
            result['Observation.DataProducts.Output_InstrumentModel.storageClusterName'], 'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_InstrumentModel.identifications'],
                         [])
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.identifications'],
                         ['mom.G737227.B1.1.T.SAP002.uv.dps'])
        self.assertEqual(result['Observation.DataProducts.Input_InstrumentModel.enabled'], False)
        self.assertEqual(result['Observation.DataProducts.Input_InstrumentModel.identifications'],
                         [])
        self.assertEqual(
            result['Observation.ObservationControl.PythonControl.DPPP.demixer.freqstep'], 4)
        self.assertEqual(
            result['Observation.ObservationControl.PythonControl.DPPP.demixer.timestep'], 1)
        # self.assertEqual(result['Observation.ObservationControl.PythonControl.DPPP.storagemanager.name'], "dysco")

    def test_beam_observation(self):
        """ Verify that get_specification properly generates an RA parset subset for a beam
            observation parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_beam_observation")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'observation')
        self.assertEqual(input_subtype, 'bfmeasurement')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.sampleClock'], 200)
        self.assertEqual(result['Observation.nrBitsPerSample'], 8)
        self.assertEqual(result['Observation.antennaSet'], 'HBA_DUAL')
        self.assertEqual(result['Observation.VirtualInstrument.stationList'],
                         ['CS004', 'CS005', 'CS003', 'CS002', 'CS007', 'CS006'])
        self.assertEqual(result['Observation.nrBeams'], 3)
        self.assertEqual(result['Observation.Beam[0].subbandList'], list(range(100, 262)))
        self.assertEqual(result['Observation.Beam[1].subbandList'], list(range(100, 262)))
        self.assertEqual(result['Observation.Beam[2].subbandList'], list(range(100, 262)))

        self.assertEqual(result['Observation.DataProducts.Output_Correlated.enabled'], False)

        self.assertEqual(result['Observation.DataProducts.Output_IncoherentStokes.enabled'], True)
        self.assertEqual(
            result['Observation.DataProducts.Output_IncoherentStokes.storageClusterName'], 'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_IncoherentStokes.identifications'],
                         ['mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2.obs.is'])
        self.assertEqual(result['Observation.DataProducts.Output_CoherentStokes.enabled'], True)
        self.assertEqual(
            result['Observation.DataProducts.Output_CoherentStokes.storageClusterName'], 'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_CoherentStokes.identifications'],
                         ['mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2.obs.cs'])
        self.assertEqual(
            result['Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.flysEye'], False)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.subbandsPerFile'],
                         512)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor'],
                         6)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.which'],
                         'I')
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.subbandsPerFile'],
                         512)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor'],
                         6)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.which'],
                         'I')

        self.assertEqual(result['Observation.Beam[0].nrTabRings'], 4)
        self.assertEqual(result['Observation.Beam[1].nrTabRings'], 4)
        self.assertEqual(result['Observation.Beam[2].nrTabRings'], 4)
        self.assertEqual(result['Observation.Beam[0].nrTiedArrayBeams'], 13)
        self.assertEqual(result['Observation.Beam[1].nrTiedArrayBeams'], 13)
        self.assertEqual(result['Observation.Beam[2].nrTiedArrayBeams'], 13)

        for sap in range(0, 3):
            for tab in range(0, 12):
                self.assertEqual(
                    result['Observation.Beam[%d].TiedArrayBeam[%d].coherent' % (sap, tab)],
                    True if tab < 12 else False)

    def test_calibration_pipeline(self):
        """ Verify that get_specification properly generates an RA parset subset for a calibration
            pipeline parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_calibration_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'pipeline')
        self.assertEqual(input_subtype, 'calibration pipeline')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.storageClusterName'],
                         'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.identifications'],
                         ['mom.G732487.B0.1.CPC.uv.dps'])
        self.assertEqual(result['Observation.DataProducts.Output_InstrumentModel.enabled'], True)
        self.assertEqual(
            result['Observation.DataProducts.Output_InstrumentModel.storageClusterName'], 'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_InstrumentModel.identifications'],
                         ['mom.G732487.B0.1.CPC.inst.dps'])
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.identifications'],
                         ['mom.G732487.B0.1.C.SAP000.uv.dps'])
        self.assertEqual(result['Observation.DataProducts.Input_InstrumentModel.enabled'], False)
        self.assertEqual(result['Observation.DataProducts.Input_InstrumentModel.identifications'],
                         [])
        self.assertEqual(
            result['Observation.ObservationControl.PythonControl.DPPP.demixer.freqstep'], 4)
        self.assertEqual(
            result['Observation.ObservationControl.PythonControl.DPPP.demixer.timestep'], 1)
        # self.assertEqual(result['Observation.ObservationControl.PythonControl.DPPP.storagemanager.name'], '')

    def test_long_baseline_pipeline(self):
        """ Verify that get_specification properly generates an RA parset subset for a long-baseline
            pipeline parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_long_baseline_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'pipeline')
        self.assertEqual(input_subtype, 'long baseline pipeline')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.storageClusterName'],
                         'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.identifications'],
                         ['mom.G724024.B0.1.LBP27.uv.dps'])
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Input_Correlated.identifications'],
                         ['mom.G724024.B0.1.PTLB27.uv.dps'])
        self.assertEqual(result[
                             'Observation.ObservationControl.PythonControl.LongBaseline.subbandgroups_per_ms'],
                         1)
        self.assertEqual(result[
                             'Observation.ObservationControl.PythonControl.LongBaseline.subbands_per_subbandgroup'],
                         8)

    def _test_pulsar_pipeline(self):
        """ Verify that get_specification properly generates an RA parset subset for a pulsar
            pipeline parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_pulsar_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'pipeline')
        self.assertEqual(input_subtype, 'pulsar pipeline')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.DataProducts.Output_Pulsar.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Output_Pulsar.storageClusterName'],
                         'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_Pulsar.identifications'],
                         ['mom.G735371.LOTAAS-P1296B.1296.pipe.dps'])
        self.assertEqual(result['Observation.DataProducts.Input_CoherentStokes.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Input_CoherentStokes.identifications'],
                         ['mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.cs',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2'])
        self.assertEqual(result['Observation.DataProducts.Input_IncoherentStokes.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Input_IncoherentStokes.identifications'],
                         ['mom.G735371.LOTAAS-P1296B-SAP0.1296.SAP0.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP1.1296.SAP1.obs.is',
                          'mom.G735371.LOTAAS-P1296B-SAP2.1296.SAP2'])

    def test_interferometer_observation(self):
        """ Verify that get_specification properly generates an RA parset subset for an
            interferometer observation parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_interferometer_observation")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'observation')
        self.assertEqual(input_subtype, 'bfmeasurement')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.sampleClock'], 200)
        self.assertEqual(result['Observation.nrBitsPerSample'], 8)
        self.assertEqual(result['Observation.antennaSet'], 'HBA_DUAL_INNER')
        self.assertEqual(result['Observation.VirtualInstrument.stationList'],
                         ['CS001', 'CS002', 'CS003', 'CS004', 'CS005', 'CS006', 'CS007', 'CS011',
                          'CS013', 'CS017', 'CS021', 'CS024', 'CS026', 'CS028', 'CS030', 'CS031',
                          'CS032', 'CS101', 'CS103', 'CS201', 'CS301', 'CS302', 'CS401', 'CS501',
                          'DE602', 'DE603', 'DE605', 'DE609', 'FR606', 'PL610', 'PL611', 'PL612',
                          'RS106', 'RS205', 'RS208', 'RS210', 'RS305', 'RS306', 'RS307', 'RS310',
                          'RS406', 'RS407', 'RS409', 'RS503', 'RS508', 'RS509', 'SE607', 'UK608'])
        self.assertEqual(result['Observation.nrBeams'], 3)
        self.assertEqual(result['Observation.Beam[0].subbandList'], [256])
        self.assertEqual(result['Observation.Beam[1].subbandList'],
                         [104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118,
                          119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                          134, 135, 136, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
                          150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 165,
                          166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180,
                          182, 183, 184, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198,
                          199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 212, 213, 215, 216,
                          217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
                          232, 233, 234, 235, 236, 237, 238, 239, 240, 242, 243, 244, 245, 246, 247,
                          248, 249, 250, 251, 252, 253, 254, 255, 257, 258, 259, 260, 261, 262, 263,
                          264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 275, 276, 277, 278, 279,
                          280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,
                          295, 296, 297, 298, 299, 300, 302, 303, 304, 305, 306, 307, 308, 309, 310,
                          311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325,
                          326, 327, 328, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341,
                          342, 343, 344, 345, 346, 347, 349, 364, 372, 380, 388, 396, 404, 413, 421,
                          430, 438, 447])
        self.assertEqual(result['Observation.Beam[2].subbandList'],
                         [104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118,
                          119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133,
                          134, 135, 136, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
                          150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 165,
                          166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180,
                          182, 183, 184, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198,
                          199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 212, 213, 215, 216,
                          217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
                          232, 233, 234, 235, 236, 237, 238, 239, 240, 242, 243, 244, 245, 246, 247,
                          248, 249, 250, 251, 252, 253, 254, 255, 257, 258, 259, 260, 261, 262, 263,
                          264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 275, 276, 277, 278, 279,
                          280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294,
                          295, 296, 297, 298, 299, 300, 302, 303, 304, 305, 306, 307, 308, 309, 310,
                          311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325,
                          326, 327, 328, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341,
                          342, 343, 344, 345, 346, 347, 349, 364, 372, 380, 388, 396, 404, 413, 421,
                          430, 438, 447])

        self.assertEqual(result['Observation.DataProducts.Output_Correlated.enabled'], True)
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.storageClusterName'],
                         'CEP4')
        self.assertEqual(result['Observation.DataProducts.Output_Correlated.identifications'],
                         ['mom.G737227.B1.1.T.SAP000.uv.dps', 'mom.G737227.B1.1.T.SAP001.uv.dps',
                          'mom.G737227.B1.1.T.SAP002.uv.dps'])
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime'],
                         1.00139)
        self.assertEqual(result[
                             'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband'],
                         64)

        self.assertEqual(result['Observation.DataProducts.Output_IncoherentStokes.enabled'], False)
        self.assertEqual(result['Observation.DataProducts.Output_CoherentStokes.enabled'], False)

    def test_maintenance(self):
        """ Verify that get_specification properly generates an RA parset subset for a maintenance
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_maintenance")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'reservation')
        self.assertEqual(input_subtype, 'maintenance')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.VirtualInstrument.stationList'], ['CS003'])

    def test_reservation(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_reservation")
        input_parset = parameterset(input_parset_file)

        # Act
        input_type, input_subtype = Specification._get_task_types_from_parset(input_parset,
                                                                              INPUT_PREFIX)
        result = Specification._resourceIndicatorsFromParset(input_type, input_subtype,
                                                             input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(input_type, 'reservation')
        self.assertEqual(input_subtype, 'project')

        self.assertEqual(result['Version.number'], 33385)
        self.assertEqual(result['Observation.VirtualInstrument.stationList'],
                         ['DE601', 'FR606', 'SE607', 'UK608'])

    # ----------------------------------------------------------------------------------------------
    # Tests of functions to read values from parsets

    def test_get_mom_id_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_interferometer_observation")
        input_parset = parameterset(input_parset_file)

        # Act
        mom_id = self.specification._get_mom_id_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(mom_id, 737228)

    def test_get_no_mom_id_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_reservation")
        input_parset = parameterset(input_parset_file)

        # Act
        mom_id = self.specification._get_mom_id_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(mom_id, None)

    def test_get_start_and_end_times_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_interferometer_observation")
        input_parset = parameterset(input_parset_file)

        # Act
        start_time, end_time = Specification._get_start_and_end_times_from_parset(input_parset,
                                                                                  INPUT_PREFIX)

        # Assert
        self.assertEqual(start_time, datetime(2016, 12, 8, 23, 20, 25))
        self.assertEqual(end_time, datetime(2016, 12, 9, 7, 20, 25))

    def test_get_no_start_and_end_times_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
         task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_averaging_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        start_time, end_time = Specification._get_start_and_end_times_from_parset(input_parset,
                                                                                  INPUT_PREFIX)

        # Assert
        self.assertEqual(start_time, None)
        self.assertEqual(end_time, None)

    def test_get_duration_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_interferometer_observation")
        input_parset = parameterset(input_parset_file)

        # Act
        duration = Specification._get_duration_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(duration, timedelta(seconds = 28800))

    def test_get_no_duration_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_averaging_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        duration = Specification._get_duration_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(duration, timedelta(0))

    def test_get_storagemanager_from_parset(self):
        """ Verify that storagemanager is read properly from parset """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_preprocessing")
        input_parset = parameterset(input_parset_file)

        # Act
        storagemanager = Specification._get_storagemanager_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(storagemanager, "dysco")

    def test_get_no_storagemanager_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_averaging_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        storagemanager = Specification._get_storagemanager_from_parset(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(storagemanager, None)

    def test_get_parset_from_OTDB(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a interferometer_observation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_interferometer_observation")
        parset_file = open(input_parset_file)
        observation_specification_tree = {}
        for line in parset_file.readlines():
            if '=' in line:
                key, value = line.split('=')
                observation_specification_tree[key.strip()] = value.strip()
        self.specification.otdb_id = 562059
        self.otdbrpc_mock.taskGetSpecification.return_value = {
            'otdb_id': 562059, 'specification': observation_specification_tree}

        # Act
        input_parset = self.specification._get_parset_from_OTDB()

        # Assert
        # TODO not sure what to assert here, no easy comparison for parsets?
        # self.assertEqual(input_parset, None)
        self.otdbrpc_mock.taskGetSpecification.assert_any_call(otdb_id = 562059)

    # TODO more tests for read_from_otdb?
    def test_read_from_otdb(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a interferometer_observation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_calibration_pipeline")
        parset_file = open(input_parset_file)
        pipeline_specification_tree = {}
        for line in parset_file.readlines():
            if '=' in line:
                key, value = line.split('=')
                pipeline_specification_tree[key.strip()] = value.strip()
        self.otdbrpc_mock.taskGetSpecification.return_value = {
            'otdb_id': 559779, 'specification': pipeline_specification_tree}
        self.radbrpc_mock.getResourceGroupNames.return_value = [{'name': 'CEP4'}]

        # Act
        predecessors = self.specification.read_from_otdb(559779)

        # Assert
        # TODO not sure what more to assert here
        self.assertEqual(predecessors, [{'source': 'mom', 'id': 732488}])
        self.assertEqual(self.specification.cluster, 'CEP4')
        self.otdbrpc_mock.taskGetSpecification.assert_any_call(otdb_id = 559779)

    def test_read_from_otdb_with_get_storagewriter_mocked(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a
        preprocessing pipeline task if get_storage_writer returns a storagemanager """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_preprocessing")
        pipeline_specification_tree = parameterset(input_parset_file).dict()
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': 562063, 'specification': pipeline_specification_tree}
        self.radbrpc_mock.getResourceGroupNames.return_value = [{'name': 'CEP4'}]

        with mock.patch.object(self.specification, "_get_storagemanager_from_parset", mock.MagicMock(return_value = "dysco")):

            # Act
            predecessors = self.specification.read_from_otdb(562063)

            # Assert
            # TODO not sure what more to assert here
            self.assertEqual(predecessors, [{'source': 'otdb', 'id': 562059}])
            self.assertEqual(self.specification.cluster, 'CEP4')
            self.otdbrpc_mock.taskGetSpecification.assert_any_call(otdb_id = 562063)
            self.specification._get_storagemanager_from_parset.assert_called_once()
            # Note: call args are a bit inconvenient to test because specification wraps the dict response in a
            #       parameterset object internally. So the following is not possible:
            #       self.specification._get_storagemanager_from_parset.assert_called_with(mocked_parset, 'ObsSW')
            (call_parset, call_prefix), kwargs = self.specification._get_storagemanager_from_parset.call_args
            self.assertEqual(call_parset.dict(), pipeline_specification_tree)
            self.assertEqual(call_prefix, 'ObsSW.')
            self.assertEqual(self.specification.storagemanager, "dysco")

    def test_read_from_otdb_with_storagewriter(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a for a
        preprocessing pipeline task with a storagemanager defined """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_preprocessing")
        parset_file = open(input_parset_file)
        pipeline_specification_tree = {}
        for line in parset_file.readlines():
            if '=' in line:
                key, value = line.split('=')
                pipeline_specification_tree[key.strip()] = value.strip()
        self.otdbrpc_mock.taskGetSpecification.return_value = {'otdb_id': 562063, 'specification': pipeline_specification_tree}
        self.radbrpc_mock.getResourceGroupNames.return_value = [{'name': 'CEP4'}]

        # Act
        predecessors = self.specification.read_from_otdb(562063)

        # Assert
        # TODO not sure what more to assert here
        self.assertEqual(predecessors, [{'source': 'otdb', 'id': 562059}])
        self.assertEqual(self.specification.cluster, 'CEP4')
        self.otdbrpc_mock.taskGetSpecification.assert_any_call(otdb_id = 562063)
        self.assertEqual(self.specification.storagemanager, "dysco")

    def test_convert_id_to_otdb_ids_other(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a interferometer_observation
            task """
        # Act
        otdb_id = self.specification.convert_id_to_otdb_ids(1, 'other')

        # Assert
        self.assertEqual(otdb_id, None)

    def test_convert_id_to_otdb_ids_otdb(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a interferometer_observation
            task """
        # Act
        otdb_id = self.specification.convert_id_to_otdb_ids(1, 'otdb')

        # Assert
        self.assertEqual(otdb_id, 1)

    def test_convert_id_to_otdb_ids_mom(self):
        """ Verify that _get_parset_from_OTDB gets the partset for a interferometer_observation
            task """
        # Arrange
        self.otdbrpc_mock.taskGetIDs.return_value = {'otdb_id': 2}

        # Act
        otdb_id = self.specification.convert_id_to_otdb_ids(1, 'mom')

        # Assert
        self.assertEqual(otdb_id, 2)

    def test_get_cluster_name(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_calibration_pipeline")
        input_parset = parameterset(input_parset_file)
        self.radbrpc_mock.getResourceGroupNames.return_value = [{'name': 'CEP4'}]

        # Act
        cluster = self.specification.get_cluster_name(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(cluster, 'CEP4')

    def test_get_no_cluster_name(self):
        """ Verify that get_specification properly generates an RA parset subset for a
            reservation task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir, "tSpecification.in_maintenance")
        input_parset = parameterset(input_parset_file)

        # Act
        cluster = self.specification.get_cluster_name(input_parset, INPUT_PREFIX)

        # Assert
        self.assertEqual(cluster, None)

    def test_get_storage_cluster_names_from_parset(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        input_parset_file = os.path.join(self.data_sets_dir,
                                         "tSpecification.in_calibration_pipeline")
        input_parset = parameterset(input_parset_file)

        # Act
        cluster_names = Specification._get_storage_cluster_names_from_parset(input_parset,
                                                                             INPUT_PREFIX)

        # Assert
        self.assertEqual(cluster_names.pop(), 'CEP4')    # TODO does with work with a list?

class UpdateStartEndTimesOnNonMoveableTasks(unittest.TestCase):
    """ Test update_start_end_times on non moveable tasks (Reservation and Maintenance)

        maintenance and reservation
        They only work properly is submitted with at least start and end time. Duration gets
        overwritten if given.

    """

    def setUp(self):
        _, filename = os.path.split(__file__)
        self.data_sets_filename_prefix, _ = os.path.splitext(filename)
        self.data_sets_dir = "test_specification.in_datasets"

        self.otdbrpc_mock = mock.MagicMock()
        self.momrpc_mock = mock.MagicMock()
        self.radbrpc_mock = mock.MagicMock()
        self.logger_mock = mock.MagicMock()

        self.specification = Specification(self.otdbrpc_mock,
                                           self.momrpc_mock, self.radbrpc_mock)

    def test_maintenance_tasks_raise_value_error_without_fixed_time(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.type = "maintenance"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_reservation_tasks_raise_value_error_without_fixed_time(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.type = "reservation"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_maintenance_tasks_raise_value_error_with_only_starttime(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.starttime = datetime.utcnow()
        self.specification.type = "maintenance"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_reservation_tasks_raise_value_error_with_only_starttime(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.starttime = datetime.utcnow()
        self.specification.type = "reservation"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_maintenance_tasks_raise_value_error_with_only_endtime(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.endtime = datetime.utcnow()
        self.specification.type = "maintenance"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_reservation_tasks_raise_value_error_with_only_endtime(self):
        # Arrange
        self.specification.otdb_id = 1
        self.specification.endtime = datetime.utcnow()
        self.specification.type = "reservation"

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.update_start_end_times()

    def test_duration_gets_filed_for_fixed_time_on_maintenance_task(self):
        # Arrange
        duration = timedelta(hours = 1)
        self.specification.otdb_id = 1
        self.specification.starttime = datetime.utcnow()
        self.specification.endtime = self.specification.starttime + duration
        self.specification.type = "maintenance"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.duration, duration)

    def test_duration_gets_filed_for_fixed_time_on_reservation_task(self):
        # Arrange
        duration = timedelta(hours = 1)
        self.specification.otdb_id = 1
        self.specification.starttime = datetime.utcnow()
        self.specification.endtime = self.specification.starttime + duration
        self.specification.type = "reservation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.duration, duration)

    def test_correct_reservation_get_submitted_to_otdb(self):
        # Arrange
        self.specification.starttime = datetime.utcnow()
        self.specification.endtime = self.specification.starttime + timedelta(hours = 1)
        self.specification.type = "reservation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.otdbrpc_mock.taskSetSpecification.assert_called()

    def test_correct_maintenance_get_submitted_to_otdb(self):
        # Arrange
        self.specification.starttime = datetime.utcnow()
        self.specification.endtime = self.specification.starttime + timedelta(hours = 1)
        self.specification.type = "maintenance"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.otdbrpc_mock.taskSetSpecification.assert_called()

    class UpdateStartEndTimesMoveableTasks(unittest.TestCase):
        """ Test update_start_end_times on Moveable tasks (Non Reservation and Maintenance)

        Currently the LOFAR Spec accepts Five types of time constraints

            #1 dwell time constraints
                minStartTime
                maxEndTime
                duration
            #2 fixed time
                startTime
                endTime
            #3 only duration
                duration
            #4 fixed time based on duration
                startTime
                duration
            #5 not time constraints at all

            MinDurations
        """

        def setUp(self):
            _, filename = os.path.split(__file__)
            self.data_sets_filename_prefix, _ = os.path.splitext(filename)
            self.data_sets_dir = "test_specification.in_datasets"

            self.otdbrpc_mock = mock.MagicMock()
            self.momrpc_mock = mock.MagicMock()
            self.radbrpc_mock = mock.MagicMock()
            self.logger_mock = mock.MagicMock()

            self.specification = Specification(self.otdbrpc_mock,
                                               self.momrpc_mock, self.radbrpc_mock)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_observation_with_no_time_gets_correct_starttime(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)
        self.specification.type = "observation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, now + timedelta(minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_observation_with_no_time_gets_correct_endtime(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)
        self.specification.type = "observation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.endtime, now + timedelta(hours = 1, minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_observation_with_no_time_gets_correct_duration(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)
        self.specification.type = "observation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.duration, timedelta(hours = 1))

    def test_observation_with_no_time_gets_submitted_to_otdb(self):
        # Arrange
        self.specification.type = "observation"

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.otdbrpc_mock.taskSetSpecification.assert_called()

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_with_starttime_in_the_past_gets_shifted_to_now_plus_3_min(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.starttime = now - timedelta(minutes = 10)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, now + timedelta(minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_with_starttime_less_then_3_minutes_in_the_future_gets_shifted(
            self,
            datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.starttime = now + timedelta(minutes = 2, seconds = 55)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, now + timedelta(minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_starttime_gets_shifted_endtime_gets_shifted_in_same_amount(
            self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        before_shift_starttime = now + timedelta(minutes = 2, seconds = 55)
        before_shift_endtime = now + timedelta(hours = 2)
        self.specification.type = "observation"
        self.specification.starttime = before_shift_starttime
        self.specification.endtime = before_shift_endtime

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime - before_shift_starttime,
                         self.specification.endtime - before_shift_endtime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_starttime_is_more_then_3_minutes_in_the_future_min_stattime_should_equal_startime(
            self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.starttime = now + timedelta(minutes = 4)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, self.specification.min_starttime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_starttime_is_more_then_3_minutes_in_the_future_max_endtime_should_equal_endtime(
            self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.starttime = now + timedelta(minutes = 4)
        self.specification.endtime = now + timedelta(minutes = 30)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.endtime, self.specification.max_endtime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_using_minStarttime_start_time_should_be_equal_to_minStarttime(self,
                                                                                datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.min_starttime = now + timedelta(minutes = 4)
        self.specification.max_endtime = now + timedelta(minutes = 60)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, self.specification.min_starttime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_using_max_endtime_the_endtime_should_be_equal_to_max_endtime(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.min_starttime = now + timedelta(minutes = 4)
        self.specification.max_endtime = now + timedelta(minutes = 60)
        self.specification.duration = timedelta(minutes = 13)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.endtime,
                         self.specification.min_starttime + self.specification.duration)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_using_minStarttime_thats_in_the_past_its_set_to_now_plus_3_minutes(self,
                                                                                     datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.min_starttime = now - timedelta(minutes = 5)
        self.specification.max_endtime = now + timedelta(minutes = 60)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.min_starttime, now + timedelta(minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_minStarttime_is_less_then_3_min_in_future_its_shifted_to_now_plus_3_min(
            self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.min_starttime = now + timedelta(minutes = 2, seconds = 56)
        self.specification.max_endtime = now + timedelta(minutes = 60)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.min_starttime, now + timedelta(minutes = 3))

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_min_starttime_gets_shifted_max_endtime_gets_shifted_in_same_amount(self,
                                                                                     datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        before_shift_min_starttime = now + timedelta(minutes = 2, seconds = 55)
        before_shift_max_endtime = now + timedelta(hours = 2)
        self.specification.type = "observation"
        self.specification.min_starttime = before_shift_min_starttime
        self.specification.max_endtime = before_shift_max_endtime

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.min_starttime - before_shift_min_starttime,
                         self.specification.max_endtime - before_shift_max_endtime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_when_starttime_is_more_then_3_min_in_future_min_starttime_should_still_be_equal(
            self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        self.specification.type = "observation"
        self.specification.starttime = now + timedelta(minutes = 6)
        self.specification.endtime = now + timedelta(minutes = 76)

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.min_starttime, self.specification.starttime)

    @mock.patch("lofar.sas.resourceassignment.common.specification.datetime")
    def test_observation_when_shift_time_behind_predecessor_with_3min_shift(self, datetime_mock):
        # Arrange
        now = datetime.utcnow()
        datetime_mock.utcnow = mock.Mock(return_value = now)

        predesessor = Specification(self.otdbrpc_mock,
                                    self.momrpc_mock, self.radbrpc_mock)
        predesessor.endtime = now + timedelta(minutes = 10)

        self.specification.type = "observation"
        self.specification.starttime = now
        self.specification.endtime = now + timedelta(minutes = 30)
        self.specification.predecessors = [predesessor]

        # Act
        self.specification.update_start_end_times()

        # Assert
        self.assertEqual(self.specification.starttime, predesessor.endtime + timedelta(minutes = 3))

class CalculateDwellValues(unittest.TestCase):
    def setUp(self):
        _, filename = os.path.split(__file__)
        self.data_sets_filename_prefix, _ = os.path.splitext(filename)
        self.data_sets_dir = "test_specification.in_datasets"

        self.otdbrpc_mock = mock.MagicMock()
        self.momrpc_mock = mock.MagicMock()
        self.radbrpc_mock = mock.MagicMock()
        self.logger_mock = mock.MagicMock()

        self.specification = Specification(self.otdbrpc_mock,
                                           self.momrpc_mock, self.radbrpc_mock)

    def test_raises_ValueError_on_missing_arguments(self):
        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.calculate_dwell_values(None, None, None, None)

    def test_raises_ValueError_when_max_end_time_is_less_than_min_starttime(self):
        # Arrange
        min_start_time = datetime(2018, 1, 1, 2, 0, 0)
        max_end_time = datetime(2018, 1, 1, 1, 0, 0)
        start_time = datetime(2018, 1, 1, 2, 0, 0)
        duration = timedelta(hours = 1)

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.calculate_dwell_values(start_time, duration,
                                                      min_start_time, max_end_time)

    def test_raises_ValueError_when_duration_is_longer_then_period_between_min_and_max_time(self):
        # Arrange
        min_start_time = datetime(2018, 1, 1, 1, 0, 0)
        max_end_time = datetime(2018, 1, 1, 2, 0, 0)
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        duration = timedelta(hours = 2)

        # Act and Assert
        with self.assertRaises(ValueError):
            self.specification.calculate_dwell_values(start_time, duration,
                                                      min_start_time, max_end_time)

    def test_returns_duration_that_is_given(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time
        max_end_time = start_time + timedelta(hours = 1)
        duration = timedelta(hours = 1)

        # Act
        _, _, result_duration = self.specification.calculate_dwell_values(start_time,
                                                                          duration,
                                                                          min_start_time,
                                                                          max_end_time)

        # Assert
        self.assertEqual(duration, result_duration)

    def test_returns_min_start_time_as_given_if_equal_to_starttime(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time
        max_end_time = start_time + timedelta(hours = 1)
        duration = timedelta(hours = 1)

        # Act
        result_min_start_time, _, _ = self.specification.calculate_dwell_values(start_time,
                                                                          duration,
                                                                          min_start_time,
                                                                          max_end_time)

        # Assert
        self.assertEqual(min_start_time, result_min_start_time)

    def test_returns_min_start_time_as_given_if_earlier_to_starttime(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time - timedelta(hours = 1)
        max_end_time = start_time + timedelta(hours = 1)
        duration = timedelta(hours = 1)

        # Act
        result_min_start_time, _, _ = self.specification.calculate_dwell_values(start_time,
                                                                          duration,
                                                                          min_start_time,
                                                                          max_end_time)

        # Assert
        self.assertEqual(min_start_time, result_min_start_time)

    def test_returns_value_of_start_time_as_min_start_time_if_min_start_time_later_to_starttime(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time + timedelta(minutes = 5)
        max_end_time = start_time + timedelta(hours = 2)
        duration = timedelta(hours = 1)

        # Act
        result_min_start_time, _, _ = self.specification.calculate_dwell_values(start_time,
                                                                          duration,
                                                                          min_start_time,
                                                                          max_end_time)

        # Assert
        self.assertEqual(start_time, result_min_start_time)

    def test_no_dwelling_if_period_between_min_start_time_max_end_time_is_equals_duration(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time
        max_end_time = start_time + timedelta(hours = 1)
        duration = timedelta(hours = 1)

        # Act
        result_min_start_time, restul_max_stat_time, _ = \
            self.specification.calculate_dwell_values(start_time, duration,
                                                      min_start_time, max_end_time)

        # Assert
        self.assertEqual(restul_max_stat_time, result_min_start_time)

    def test_dwelling_if_period_between_min_start_time_max_end_time_is_less_than_duration(self):
        # Arrange
        start_time = datetime(2018, 1, 1, 1, 0, 0)
        min_start_time = start_time
        duration = timedelta(hours = 1)
        dwelling = timedelta(minutes = 20)
        max_end_time = start_time + duration + dwelling

        # Act
        result_min_start_time, restul_max_stat_time, _ = \
            self.specification.calculate_dwell_values(start_time, duration,
                                                      min_start_time, max_end_time)

        # Assert
        self.assertEqual(dwelling, restul_max_stat_time - result_min_start_time)

class ReadFromRadb(unittest.TestCase):
    def setUp(self):
        _, filename = os.path.split(__file__)
        self.data_sets_filename_prefix, _ = os.path.splitext(filename)
        self.data_sets_dir = "test_specification.in_datasets"

        self.otdbrpc_mock = mock.MagicMock()
        self.momrpc_mock = mock.MagicMock()
        self.radbrpc_mock = mock.MagicMock()
        self.logger_mock = mock.MagicMock()

        self.specification = Specification(self.otdbrpc_mock, self.momrpc_mock,
                                           self.radbrpc_mock)

    def test_read_from_radb(self):
        """ Verify that get_specification properly generates an RA parset subset for a reservation
            task """
        # Arrange
        task = {"id": 1, "mom_id": 2, "otdb_id": 3, "status": "scheduled",
                "type": "observation", "duration": 100, "cluster": "CEP4"}
        self.radbrpc_mock.getTask.return_value = task

        # Act
        self.specification.read_from_radb(1)

        # Assert
        self.assertEqual(self.specification.radb_id, task["id"])
        self.assertEqual(self.specification.mom_id, task["mom_id"])
        self.assertEqual(self.specification.otdb_id, task["otdb_id"])
        self.assertEqual(self.specification.status, task["status"])
        self.assertEqual(self.specification.type, task["type"])
        self.assertEqual(self.specification.duration, timedelta(seconds = task["duration"]))
        self.assertEqual(self.specification.cluster, task["cluster"])

    def test_insert_into_radb_and_check_predecessors(self):
        # Arrange
        def mock_getTask(id=None, mom_id=None, otdb_id=None, specification_id=None):
            if id is None and mom_id is not None:
                id = mom_id
            return {"id": id, "mom_id": id, "otdb_id": id, "status": "approved", "type": "observation", "duration": 100, "predecessor_ids": []}

        self.radbrpc_mock.getTask.side_effect = mock_getTask
        self.radbrpc_mock.insertOrUpdateSpecificationAndTask.return_value = {'specification_id': 1, 'task_id': 1}
        self.momrpc_mock.getPredecessorIds.return_value = {'1': [42]}
        self.specification.read_from_radb(1)

        # Act
        self.specification.insert_into_radb()

        # Assert
        self.radbrpc_mock.insertTaskPredecessor.assert_called_with(1, 42)


        # Arrange
        # now adapt the mock_getTask, and let it return the inserted predecessor_ids as well
        def mock_getTask(id=None, mom_id=None, otdb_id=None, specification_id=None):
            if id is None and mom_id is not None:
                id = mom_id
            task = {"id": id, "mom_id": id, "otdb_id": id, "status": "approved", "type": "observation", "duration": 100, "predecessor_ids": []}
            if id == 1:
                task['predecessor_ids'] = [42]
            return task

        self.radbrpc_mock.getTask.side_effect = mock_getTask
        self.radbrpc_mock.insertTaskPredecessor.reset_mock()

        # Act
        self.specification.insert_into_radb()

        # Assert
        self.radbrpc_mock.insertTaskPredecessor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
