#!/usr/bin/env python3

import os
import unittest
import logging
from lofar.sas.resourceassignment.resourceassignmentestimator.service import ResourceEstimatorHandler
from lofar.sas.resourceassignment.resourceassignmentestimator.resource_estimators import ObservationResourceEstimator
from unittest import mock

class TestObservationResourceEstimator(unittest.TestCase):
    def test_raises_ValueError_on_incomplete_parset(self):
        parset = {}

        estimator = ObservationResourceEstimator()

        with self.assertRaises(ValueError):
            estimator.verify_and_estimate(parset)

    def generate_complete_parset(self):
        parset = {'Observation.sampleClock': None,
                  'Observation.startTime': "2019-03-04 13:00:00",
                  'Observation.stopTime': "2019-03-04 14:00:00",
                  'Observation.antennaSet': "LBA_INNER",
                  'Observation.nrBeams': 1,
                  'Observation.Beam[0].subbandList': [40, 41],
                  'Observation.nrBitsPerSample': 16,
                  'Observation.VirtualInstrument.stationList': ["CS001"],
                  'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband': 64,
                  'Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime': 1,
                  'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.flysEye': None,
                  'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor': None,
                  'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor': None,
                  'Observation.DataProducts.Output_Correlated.enabled': True,
                  'Observation.DataProducts.Output_Correlated.identifications': None,
                  'Observation.DataProducts.Output_Correlated.storageClusterName': None,
                  'Observation.DataProducts.Output_CoherentStokes.enabled': False,
                  'Observation.DataProducts.Output_CoherentStokes.identifications': None,
                  'Observation.DataProducts.Output_CoherentStokes.storageClusterName': None,
                  'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.which': None,
                  'Observation.DataProducts.Output_IncoherentStokes.enabled': False,
                  'Observation.DataProducts.Output_IncoherentStokes.identifications': None,
                  'Observation.DataProducts.Output_IncoherentStokes.storageClusterName': None,
                  'Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.which': None,
                  }

        return parset

    def test_does_not_raise_ValueError_on_complete_parset(self):
        parset = self.generate_complete_parset()

        estimator = ObservationResourceEstimator()

        try:
            estimator.verify_and_estimate(parset)
        except ValueError:
            self.fail("estimator.verify_and_estimate(parset) raised ValueError unexpectedly!")

    def test_reports_error_when_no_output_was_enabled(self):
        parset = self.generate_complete_parset()

        parset['Observation.DataProducts.Output_Correlated.enabled'] = False
        parset['Observation.DataProducts.Output_CoherentStokes.enabled'] = False
        parset['Observation.DataProducts.Output_IncoherentStokes.enabled'] = False

        estimator = ObservationResourceEstimator()

        estimate = estimator.verify_and_estimate(parset)

        self.assertEqual(
            ['Produced observation resource estimate list has no data product estimates!'],
            estimate['errors'])

    def test_raise_reports_error_when_no_subbands_are_given(self):
        parset = self.generate_complete_parset()

        parset['Observation.DataProducts.Output_Correlated.enabled'] = True
        parset['Observation.Beam[0].subbandList'] = []

        estimator = ObservationResourceEstimator()

        estimate = estimator.verify_and_estimate(parset)

        self.assertTrue("Correlated data output enabled, but empty subband list for sap 0" in
            estimate['errors'])

    def test_reports_error_when_stationlist_is_empty(self):
        parset = self.generate_complete_parset()

        parset['Observation.DataProducts.Output_Correlated.enabled'] = True
        parset['Observation.VirtualInstrument.stationList'] = []

        estimator = ObservationResourceEstimator()

        estimate = estimator.verify_and_estimate(parset)

        self.assertTrue("Observation.VirtualInstrument.stationList is empty" in
            estimate['errors'])

    def test_reports_error_when_nrbeams_less_than_one(self):
        parset = self.generate_complete_parset()

        parset['Observation.DataProducts.Output_Correlated.enabled'] = True
        parset['Observation.nrBeams'] = 0

        estimator = ObservationResourceEstimator()

        estimate = estimator.verify_and_estimate(parset)

        self.assertTrue("Correlated data output enabled, but nrBeams < 1" in
            estimate['errors'])


class TestResourceEstimatorHandler(unittest.TestCase):
    def setUp(self):
        self.unique_otdb_id = 0
        self.data_sets_dir = os.path.join(os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__))),
                                          "data_sets")

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.ObservationResourceEstimator')
    def test_ObservationResourceEstimator_gets_called_on_observation_parset(self, ObservationResourceEstimator_mock):
        specification_tree = self.generate_observation_spec()

        resource_estimator_handler = ResourceEstimatorHandler()

        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        ObservationResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_observation_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_beam_observation')
        task_type = 'observation'
        task_subtype = 'bfmeasurement'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.ReservationResourceEstimator')
    def test_ReservationResourceEstimator_gets_called_on_reservation_maintenance_parset(self, ReservationResourceEstimator_mock):
        specification_tree = self.generate_maintenance_reservation_spec()

        resource_estimator_handler = ResourceEstimatorHandler()

        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        ReservationResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_maintenance_reservation_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_maintenance_reservation')
        task_type = 'reservation'
        task_subtype = 'maintenance'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.ReservationResourceEstimator')
    def test_ReservationResourceEstimator_gets_called_on_reservation_project_parset(self, ReservationResourceEstimator_mock):
        specification_tree = self.generate_project_reservation_spec()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        ReservationResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_project_reservation_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_project_reservation')
        task_type = 'reservation'
        task_subtype = 'project'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.CalibrationPipelineResourceEstimator')
    def test_CalibrationPipelineResourceEstimator_gets_called_on_calibrator_pipeline_parset(self, CalibrationPipelineResourceEstimator_mock):
        specification_tree = self.generate_calibration_pipeline_spec()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        CalibrationPipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_calibration_pipeline_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_calibration_pipeline')
        task_type = 'pipeline'
        task_subtype = 'calibration pipeline'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        self.add_predecessor_to_specification_tree(os.path.join(self.data_sets_dir,
                                                                't_resource_estimator.in_calibration_pipeline_predecessor_558022'),
                                                   # predecessor also used for imaging pipeline test
                                                   'observation',
                                                   'bfmeasurement',
                                                   specification_tree['predecessors'])
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.CalibrationPipelineResourceEstimator')
    def test_ImagePipelineResourceEstimator_gets_called_on_averaging_pipeline_parset(self, CalibrationPipelineResourceEstimator_mock):
        specification_tree = self.generate_averaging_pipeline_spec()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        CalibrationPipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_averaging_pipeline_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_preprocessing_pipeline')
        task_type = 'pipeline'
        task_subtype = 'averaging pipeline'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        # Pipelines need a predecessor so give it one
        predecessor_data_set_filepath = os.path.join(self.data_sets_dir,
                                                     't_resource_estimator.in_interferometer_observation')
        predecessor_task_type = 'observation'
        predecessor_task_subtype = 'interferometer'
        self.add_predecessor_to_specification_tree(predecessor_data_set_filepath,
                                                   predecessor_task_type,
                                                   predecessor_task_subtype,
                                                   specification_tree['predecessors'])
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.ImagePipelineResourceEstimator')
    def test_ImagePipelineResourceEstimator_gets_called_on_imaging_pipeline_parset(self, ImagePipelineResourceEstimator_mock):
        data_set_filepath = os.path.join(self.data_sets_dir, 't_resource_estimator.in_imaging_pipeline')
        task_type = 'pipeline'
        task_subtype = 'imaging pipeline'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)

        self.add_predecessor_to_specification_tree(os.path.join(self.data_sets_dir,
                                                   't_resource_estimator.in_calibration_pipeline_predecessor_558022'),  # predecessor also used for calibration pipeline test
                                                   'observation',
                                                   'bfmeasurements',
                                                   specification_tree['predecessors'])

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        ImagePipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.ImagePipelineResourceEstimator')
    def test_ImagePipelineResourceEstimator_gets_called_on_imaging_pipeline_msss_parset(self, ImagePipelineResourceEstimator_mock):
        specification_tree = self.generate_imageing_pipeline_mss()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        ImagePipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_imageing_pipeline_mss(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_imaging_pipeline')
        task_type = 'pipeline'
        task_subtype = 'imaging pipeline msss'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        self.add_predecessor_to_specification_tree(os.path.join(self.data_sets_dir,
                                                                't_resource_estimator.in_calibration_pipeline_predecessor_558022'),
                                                   # predecessor also used for calibration pipeline test
                                                   'observation',
                                                   'bfmeasurements',
                                                   specification_tree['predecessors'])
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.LongBaselinePipelineResourceEstimator')
    def test_LongBaselinePipelineResourceEstimator_get_called_on_long_baseline_pipeline_parset(self, LongBaselinePipelineResourceEstimator_mock):
        specification_tree = self.generate_long_baseline_pipeline_spec()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        LongBaselinePipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_long_baseline_pipeline_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_long_baseline_pipeline')
        golden_output_filepath = os.path.join(self.data_sets_dir,
                                              't_resource_estimator.out_long_baseline_pipeline')
        task_type = 'pipeline'
        task_subtype = 'long baseline pipeline'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        tree = specification_tree
        predecessor_tree = self.get_specification_tree(
            os.path.join(
                self.data_sets_dir,
                't_resource_estimator.in_long_baseline_pipeline_predecessor_556601'),
            'pipeline',
            'averaging pipeline')
        tree['predecessors'].append(predecessor_tree)
        tree = predecessor_tree
        predecessor_tree = self.get_specification_tree(
            os.path.join(
                self.data_sets_dir,
                't_resource_estimator.in_long_baseline_pipeline_predecessor_556601_556429'),
            'pipeline',
            'calibration pipeline')
        tree['predecessors'].append(predecessor_tree)
        tree = predecessor_tree
        predecessor_tree_branch_a = self.get_specification_tree(
            os.path.join(
                self.data_sets_dir,
                't_resource_estimator.in_long_baseline_pipeline_predecessor_556601_556429_556373'),
            'pipeline',
            'calibration pipeline')
        tree['predecessors'].append(predecessor_tree_branch_a)
        predecessor_tree_branch_b = self.get_specification_tree(
            os.path.join(
                self.data_sets_dir,
                't_resource_estimator.in_long_baseline_pipeline_predecessor_556601_556429_556375'),
            'observation',
            'bfmeasurement')
        tree['predecessors'].append(predecessor_tree_branch_b)
        predecessor_tree = self.get_specification_tree(
            os.path.join(
                self.data_sets_dir,
                't_resource_estimator.in_long_baseline_pipeline_predecessor_556601_556429_xxxxxx_556371'),
            'observation',
            'bfmeasurement')
        predecessor_tree_branch_a['predecessors'].append(predecessor_tree)
        predecessor_tree_branch_b['predecessors'].append(predecessor_tree)
        return specification_tree

    @mock.patch('lofar.sas.resourceassignment.resourceassignmentestimator.service.PulsarPipelineResourceEstimator')
    def test_PulsarPipelineResourceEstimator_get_called_on_a_pulsar_pipeline_parset(self, PulsarPipelineResourceEstimator_mock):
        specification_tree = self.generate_pulsar_pipeline_spec()

        resource_estimator_handler = ResourceEstimatorHandler()
        resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        PulsarPipelineResourceEstimator_mock().verify_and_estimate.assert_called()

    def generate_pulsar_pipeline_spec(self):
        data_set_filepath = os.path.join(self.data_sets_dir,
                                         't_resource_estimator.in_pulsar_pipeline')
        task_type = 'pipeline'
        task_subtype = 'pulsar pipeline'
        specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        # Pulsar pipelines need a beamformer observation as their predecessor
        predecessor_data_set_filepath = os.path.join(self.data_sets_dir,
                                                     't_resource_estimator.in_beam_observation')
        predecessor_task_type = 'observation'
        predecessor_task_subtype = 'bfmeasurement'
        self.add_predecessor_to_specification_tree(predecessor_data_set_filepath,
                                                   predecessor_task_type,
                                                   predecessor_task_subtype,
                                                   specification_tree['predecessors'])
        return specification_tree

    def test_add_otdb_id_to_output(self):
        specification_tree = self.generate_averaging_pipeline_spec()

        resource_estimator_handler = ResourceEstimatorHandler()

        estimate = resource_estimator_handler._get_estimated_resources(specification_tree=specification_tree)

        estimate_list = estimate['estimates']

        for est in estimate_list:
            output_files = est.get('output_files')
            for dptype in output_files:
                for dptype_dict in output_files[dptype]:
                    self.assertEqual(specification_tree['otdb_id'], dptype_dict['properties'][dptype + '_otdb_id'])


    def add_predecessor_to_specification_tree(self, data_set_filepath, task_type, task_subtype, predecessor_list):
        """ Adds a predecessor specification tree to an existing specification tree

        :param data_set_filepath: predecessor specification data set filepath
        :param task_type: predecessor task's type
        :param task_subtype: predecessor task's subtype
        :param predecessor_list: specification tree to with to add predecessor specification tree
        """
        predecessor_specification_tree = self.get_specification_tree(data_set_filepath, task_type, task_subtype)
        predecessor_list.append(predecessor_specification_tree)

    def get_specification_tree(self, data_set_filepath, task_type, task_subtype):
        """ Create a specification tree from a specification data set text file

        :param data_set_filepath: specification data set's filepath
        :param task_type: the task's type
        :param task_subtype: the task's subtype
        :return: specification tree
        """
        with open(data_set_filepath) as spec_file:
            parset = eval(spec_file.read().strip())
            return {
                'otdb_id': self.get_unique_otdb_id(),
                'task_type': task_type,
                'task_subtype': task_subtype,
                'predecessors': [],
                'specification': parset
            }

    def get_unique_otdb_id(self):
        """ Generates a unique OTDB ID (for use in parsets with predecessors)

        :return: unique OTDB ID
        """
        self.unique_otdb_id += 1
        return self.unique_otdb_id


    def get_golden_imate(self, golden_output_filepath, estimator_function=None, *estimator_args):
        """ Obtain the golden estimation from file (and create one if DO_GENERATE_GOLDEN_OUTPUTS is True)

        :param golden_output_filepath: the path to the golden estimate output file
        :param estimator_function: the estimator function to be called with estimator_args as it argument(S)
        :param estimator_args: the estimator function's arguments
        :return: the golden estimate
        """
        # Generate the golden output prior to fetching it if user requests so
        if DO_GENERATE_GOLDEN_OUTPUTS:
            estimation = estimator_function(*estimator_args)
            error_messages = self.get_uut_errors(estimation)
            # Make sure that there no errors are returned by uut
            if len(error_messages) == 0:
                self.store_datastructure(estimation, golden_output_filepath)
            else:
                raise Exception("\nThe uut reported errors:\n" + '\n- '.join(error_messages))

        # Fetch the golden output
        f = open(golden_output_filepath, "r")
        golden_output = f.read()
        f.close()

        # Remove trailing newline, and trailing and heading double-quotes
        stringified = golden_output.strip()
        stringified = stringified.strip('\n')
        stringified = stringified.strip('"')
        return stringified

    def store_datastructure(self, estimation={}, output_file=""):
        """ Stores the estimation data structure such that it can be used as golden output to verify against.

        :param estimation: resource estimator data structure
        :param output_file: file name to store the estimation to
        """
        output_filepath = os.path.join(self.data_sets_dir, output_file)
        f = open(output_filepath, 'w+')
        pprint(repr(estimation).strip(), stream=f)
        f.close()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    unittest.main()
