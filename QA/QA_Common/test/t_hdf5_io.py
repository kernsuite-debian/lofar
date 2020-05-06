#!/usr/bin/env python

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

import unittest
import logging
import tempfile
import os
import random
import numpy as np
from datetime import datetime, timedelta

from lofar.qa.hdf5_io import *
from lofar.parameterset import *
from lofar.common.datetimeutils import to_modified_julian_date_in_seconds
from lofar.common.test_utils import unit_test
from lofar.qa.utils import *

np.set_printoptions(precision=2)

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(process)s %(message)s', level=logging.INFO)

class TestHdf5_IO(unittest.TestCase):
    @unit_test
    def test_write_and_read_again(self):
        '''tests writing and reading an hdf5 file, and checks all parameters except for the visibility data.
        See test_write_and_read_and_verify_data for elaborate data verification.'''
        logger.info('test_write_and_read_again')

        path = tempfile.mkstemp()[1]
        try:
            logger.info('generating test data')
            num_saps=3
            num_stations=7
            num_timestamps=11
            saps_in = create_hypercube(num_saps=num_saps, num_stations=num_stations, num_timestamps=num_timestamps)

            parset=parameterset()
            parset.adoptArgv(['foo=bar'])

            write_hypercube(path, saps_in, parset)

            parset2 = read_hypercube_parset(path)
            self.assertEqual(str(parset), str(parset2))

            result = read_hypercube(path, visibilities_in_dB=False, python_datetimes=True)

            self.assertTrue(result['saps'])
            self.assertEqual(num_saps, len(result['saps']))

            for sap_nr, sap_out in result['saps'].items():
                sap_in = saps_in[sap_nr]

                self.assertTrue('timestamps' in sap_out)
                self.assertEqual(len(sap_in['timestamps']), len(sap_out['timestamps']))
                for t_in, t_out in zip(sap_in['timestamps'], sap_out['timestamps']):
                    self.assertEqual(t_in, t_out)

                self.assertFalse(sap_out['visibilities_in_dB'])
                self.assertEqual(sap_in['visibilities'].shape, sap_out['visibilities'].shape)

                self.assertTrue('antenna_locations' in sap_out)
                for coords_type in ['XYZ', 'PQR', 'WGS84']:
                    self.assertTrue(coords_type in sap_out['antenna_locations'])
                    self.assertEqual(7, len(sap_out['antenna_locations'][coords_type]))

            #test the file annotations
            annotate_file(path, 'This file was recorded in front of a live audience ;-)', 'test_user')
            file_annotations = read_file_annotations(path)

            self.assertEqual(1, len(file_annotations))
            self.assertEqual('This file was recorded in front of a live audience ;-)', file_annotations[0]['annotation'])
            self.assertEqual('test_user', file_annotations[0]['user'])

        finally:
            logger.info('removing test file: %s', path)
            os.remove(path)

    @unit_test
    def test_get_and_filter_baselines(self):
        logger.info('test_get_and_filter_baselines')

        path = tempfile.mkstemp()[1]
        try:
            logger.info('generating test data')
            num_stations=7
            write_hypercube(path, create_hypercube(num_stations=num_stations, num_saps=1, num_timestamps=1))

            expected_stations = ['CS%03d' % (i + 1) for i in range(num_stations)]

            stations = get_stations(path)
            self.assertEqual(expected_stations, stations)

            expected_baselines = []
            for i, s1 in enumerate(expected_stations):
                for s2 in expected_stations[i:]:
                    expected_baselines.append((s1, s2))

            baselines = get_baselines(path)
            self.assertEqual(expected_baselines, baselines)

            filtered_baselines = filter_baselines(baselines, keep_autocorrelations=True, keep_crosscorrelations=False)
            self.assertEqual(num_stations, len(filtered_baselines))
            for bl in filtered_baselines:
                self.assertEqual(bl[0], bl[1])

            filtered_baselines = filter_baselines(baselines, keep_autocorrelations=False, keep_crosscorrelations=True)
            self.assertEqual(len(expected_baselines)-num_stations, len(filtered_baselines))
            for bl in filtered_baselines:
                self.assertNotEqual(bl[0], bl[1])

            filtered_baselines = filter_baselines(baselines, antenna1_filter='CS')
            self.assertEqual(filtered_baselines, baselines)

            for i, station in enumerate(expected_stations):
                filtered_baselines = filter_baselines(baselines, antenna1_filter=station, antenna2_filter=station)
                self.assertEqual(1, len(filtered_baselines))
                self.assertEqual(filtered_baselines, [(station, station)])

                filtered_baselines = filter_baselines(baselines, antenna1_filter=station)
                self.assertEqual(num_stations-i, len(filtered_baselines))
                for bl in filtered_baselines:
                    self.assertEqual(station, bl[0])

                filtered_baselines = filter_baselines(baselines, antenna2_filter=station)
                self.assertEqual(i+1, len(filtered_baselines))
                for bl in filtered_baselines:
                    self.assertEqual(station, bl[1])
        finally:
            logger.info('removing test file: %s', path)
            os.remove(path)


    @unit_test
    def test_read_subsets(self):
        '''Assumes test_write_and_read_again and test_write_and_read_and_verify_data are working.
        This test focuses reading a subset of the stations/baselines.'''
        logger.info('test_read_subsets')

        path = tempfile.mkstemp()[1]
        try:
            logger.info('generating test data')
            num_saps=2
            num_stations=7
            num_timestamps=5
            saps_in = create_hypercube(num_saps=num_saps, num_stations=num_stations, num_timestamps=num_timestamps)
            stations = sorted(set(bl[0] for bl in saps_in[0]['baselines']))

            # test if the test-data has the full list of expected stations
            self.assertEqual(['CS%03d' % (i + 1) for i in range(num_stations)], stations)

            def baseline_to_value(station1, station2):
                # encode station into visibility value
                # so we can assert later on expected visibility values for a given station
                # real = index+1 of station1 of the baseline
                # imag = index+1 of station2 of the baseline
                return complex(stations.index(station1) + 1, stations.index(station2) + 1)

            for sap_nr, sap_in in saps_in.items():
                for bl_idx, bl in enumerate(sap_in['baselines']):
                    station1 = bl[0]
                    station2 = bl[1]
                    sap_in['visibilities'][bl_idx,:,:,:] = baseline_to_value(station1, station2)

            # just write the whole hypercube...
            write_hypercube(path, saps_in)

            # ... but read it back with station subselection
            for station in stations:
                result = read_hypercube(path, visibilities_in_dB=False, baselines_to_read=[(station, station)])

                for sap_nr, sap_out in result['saps'].items():
                    sap_in = saps_in[sap_nr]

                    # test expected dimensions
                    self.assertEqual(1, sap_out['visibilities'].shape[0])
                    self.assertEqual(sap_in['visibilities'].shape[1:], sap_out['visibilities'].shape[1:])
                    self.assertEqual(sap_out['visibilities'].shape, sap_out['flagging'].shape)

                    # test expected visibility values
                    for bl_idx, bl in enumerate(sap_out['baselines']):
                        self.assertTrue(station in bl)
                        expected_value = baseline_to_value(bl[0], bl[1])
                        expected_array = np.full(sap_out['visibilities'].shape[1:], expected_value)
                        vis_out = sap_out['visibilities'][bl_idx,:,:,:]
                        self.assertTrue(np.allclose(expected_array, vis_out, 0.1*abs(expected_value)))

            # ... and read it back with baseline subselection
            for bl_idx, bl in enumerate(sap_in['baselines']):
                result = read_hypercube(path, visibilities_in_dB=False, baselines_to_read=[bl])

                for sap_nr, sap_out in result['saps'].items():
                    sap_in = saps_in[sap_nr]

                    # test expected dimensions
                    self.assertEqual(1, sap_out['visibilities'].shape[0])
                    self.assertEqual(sap_in['visibilities'].shape[1:], sap_out['visibilities'].shape[1:])
                    self.assertEqual(sap_out['visibilities'].shape, sap_out['flagging'].shape)

                    # test expected visibility values
                    for bl_out_idx, bl_out in enumerate(sap_out['baselines']):
                        self.assertEqual(bl, bl_out)
                        expected_value = baseline_to_value(bl_out[0], bl_out[1])
                        expected_array = np.full(sap_out['visibilities'].shape[1:], expected_value)
                        vis_out = sap_out['visibilities'][bl_out_idx,:,:,:]
                        self.assertTrue(np.allclose(expected_array, vis_out, 0.1*abs(expected_value)))

        finally:
            logger.info('removing test file: %s', path)
            os.remove(path)


    @unit_test
    def test_write_and_read_and_verify_data(self):
        '''extensive test to verify to correctness of all visibility amplitudes and phases
        after it has been written and read back again, bot in raw and dB.'''
        logger.info('test_write_and_read_and_verify_data')

        path = tempfile.mkstemp()[1]

        try:
            # test over a wide range of possible number of saps, stations, timestamps, subbands, max_amplitude
            # because these parameters can influence the applied data reduction in writing, and reconstruction in reading
            for num_saps in [1, 2]:
                for num_stations in [1, 3, 10]:
                    for num_timestamps in [1, 2, 10]:
                        for num_subbands_per_sap in [1, 2, 10]:
                            for max_amplitude in [100, 1000, 10000]:
                                for pol_ratio in [1, 10, 50]:
                                    # create a synthetic hypercube with known data which we can verify
                                    # amplitude varies with time
                                    # phase varies with subband
                                    saps_in = create_hypercube(num_saps=num_saps,
                                                               num_stations=num_stations, num_timestamps=num_timestamps,
                                                               num_subbands_per_sap={sap_nr:num_subbands_per_sap for sap_nr in range(num_saps)},
                                                               snr=1.0, max_signal_amplitude=max_amplitude,
                                                               parallel_to_cross_polarization_ratio=pol_ratio)

                                    for sap_nr, sap_in_raw in saps_in.items():
                                        # test for correct input test data
                                        max_amplitude_in = np.max(np.abs(sap_in_raw['visibilities']))
                                        self.assertTrue(np.abs(max_amplitude - max_amplitude_in) < 1e-3*max_amplitude)

                                    # write the hypercube and parset into an h5 file....
                                    write_hypercube(path, saps_in)

                                    # ...and read the data back from file and compare it
                                    # input visibilities are not in dB, so request the output visibilities not to be in dB either
                                    # (side note, visibilities are stored in the h5 file in dB's for better compression)
                                    result_raw = read_hypercube(path, visibilities_in_dB=False, python_datetimes=True)
                                    # but because we usually plot the visibilities in dB, read and check those as well
                                    result_dB = read_hypercube(path, visibilities_in_dB=True, python_datetimes=True)

                                    self.assertTrue('saps' in result_raw)
                                    self.assertTrue('saps' in result_dB)
                                    saps_out_raw = result_raw['saps']
                                    saps_out_dB = result_dB['saps']
                                    self.assertEqual(num_saps, len(saps_out_raw))
                                    self.assertEqual(num_saps, len(saps_out_dB))

                                    for sap_nr, sap_out_raw in saps_out_raw.items():
                                        sap_in_raw = saps_in[sap_nr]
                                        sap_out_dB = saps_out_dB[sap_nr]

                                        # compare all in/out timestamps
                                        self.assertTrue('timestamps' in sap_out_raw)
                                        for t_in, t_out in zip(sap_in_raw['timestamps'], sap_out_raw['timestamps']):
                                            self.assertEqual(t_in, t_out)

                                        # compare all in/out subbands
                                        self.assertTrue('subbands' in sap_out_raw)
                                        for sb_in, sb_out in zip(sap_in_raw['subbands'], sap_out_raw['subbands']):
                                            self.assertEqual(sb_in, sb_out)

                                        # compare all in/out central_frequencies
                                        self.assertTrue('central_frequencies' in sap_out_raw)
                                        for freq_in, freq_out in zip(sap_in_raw['central_frequencies'], sap_out_raw['central_frequencies']):
                                            self.assertEqual(freq_in, freq_out)

                                        self.assertFalse(sap_out_raw['visibilities_in_dB'])
                                        self.assertEqual(sap_in_raw['visibilities'].shape, sap_out_raw['visibilities'].shape)

                                        # compare all in/out visibilities
                                        vis_in_raw = sap_in_raw['visibilities']
                                        vis_out_raw = sap_out_raw['visibilities']
                                        vis_out_dB = sap_out_dB['visibilities']

                                        # for the raw visibilities, comparison is easy...
                                        # just check the differences in amplitude and in phase
                                        abs_diff_raw = np.abs(vis_in_raw) - np.abs(vis_out_raw)
                                        abs_phase_diff_raw = np.abs(np.unwrap(np.angle(vis_in_raw) - np.angle(vis_out_raw), axis=2))
                                        # phase has no 'meaning' for small (insignificant) amplitudes,
                                        # so just set the phase difference to zero there
                                        abs_phase_diff_raw[np.abs(vis_in_raw) <= max(1.0, 1e-3*max_amplitude)] = 0
                                        abs_phase_diff_raw[np.abs(vis_out_raw) <= max(1.0, 1e-3*max_amplitude)] = 0

                                        # for the visibilities in dB, the phases should be equal to the input phases,
                                        # no matter whether the visibilities are in dB or raw.
                                        # but the amplitudes need conversion from dB back to raw first.
                                        abs_vis_out_raw_from_dB = np.power(10, 0.1*np.abs(vis_out_dB))
                                        abs_diff_raw_dB = np.abs(vis_in_raw) - abs_vis_out_raw_from_dB
                                        abs_phase_diff_raw_dB = np.abs(np.unwrap(np.angle(vis_in_raw) - np.angle(vis_out_dB), axis=2))
                                        # phase has no 'meaning' for small (insignificant) amplitudes, so just set it to zero there
                                        abs_phase_diff_raw_dB[np.abs(vis_in_raw) <= max(1.0, 1e-3*max_amplitude)] = 0
                                        abs_phase_diff_raw_dB[abs_vis_out_raw_from_dB <= max(1.0, 1e-3*max_amplitude)] = 0

                                        amplitude_threshold = 0.10 * max_amplitude
                                        phase_threshold = 0.025 * 2 * np.pi

                                        for i in range(vis_in_raw.shape[0]):
                                            for j in range(vis_in_raw.shape[1]):
                                                for k in range(vis_in_raw.shape[2]):
                                                    for l in range(vis_in_raw.shape[3]):
                                                        self.assertLess(abs_diff_raw[i,j,k,l],    amplitude_threshold)
                                                        self.assertLess(abs_diff_raw_dB[i,j,k,l], amplitude_threshold)
                                                        try:
                                                            self.assertLess(abs_phase_diff_raw[i,j,k,l],    phase_threshold)
                                                        except AssertionError:
                                                            # phase is just below 2pi (close to 0)
                                                            self.assertLess(2*np.pi-abs_phase_diff_raw[i,j,k,l], phase_threshold)

                                                        try:
                                                            self.assertLess(abs_phase_diff_raw_dB[i, j, k, l], phase_threshold)
                                                        except AssertionError:
                                                            # phase is just below 2pi (close to 0)
                                                            self.assertLess(2*np.pi-abs_phase_diff_raw_dB[i, j, k, l], phase_threshold)

        finally:
            logger.info('removing test file: %s', path)
            os.remove(path)

    @unit_test
    def test_12_to_13_to_14_conversion(self):
        path = tempfile.mkstemp()[1]

        try:
            max_amplitude = 1000
            saps_in = create_hypercube(num_saps=1,
                                       num_stations=2, num_timestamps=32,
                                       num_subbands_per_sap={0: 32},
                                       snr=1.0, max_signal_amplitude=max_amplitude,
                                       parallel_to_cross_polarization_ratio=1.0)

            # write the hypercube and parset into an h5 file....
            # this currently results in a v1.4 file
            write_hypercube(path, saps_in, sas_id=123456)

            # check if version is 1.4
            with h5py.File(path, "r") as file:
                version_str = file['version'][0]
                self.assertEqual('1.4', version_str)

            # change version back to 1.2
            # and modify visibility data to have the 1.2 incorrect phases
            with h5py.File(path, "r+") as file:
                # revert version...
                file['version'][0] = '1.2'

                # revert visibilities.
                # Use saps_in's visibilities and the old hdf5_io code to compute and store the incorrect phases.
                for sap_nr in sorted(saps_in.keys()):
                    visibilities_in = saps_in[sap_nr]['visibilities']
                    subbands = saps_in[sap_nr]['subbands']

                    # this is v1.2's incorrect dB conversion messing up the phases
                    visibilities_dB = 10.0 * np.log10(visibilities_in)
                    abs_vis_dB = np.absolute(visibilities_dB)

                    # this is v1.2's way of computing the scale factors per subband only
                    # compute scale factor per subband to map the visibilities_dB per subband from complex64 to 2xint8
                    scale_factors = np.empty((len(subbands),), dtype=np.float32)
                    for sb_nr in range(len(subbands)):
                        # use 99.9 percentile instead if max to get rid of spikes
                        max_abs_vis_sb = np.percentile(abs_vis_dB[:, :, sb_nr, :], 99.9)
                        scale_factor = 127.0 / max_abs_vis_sb
                        scale_factors[sb_nr] = 1.0 / scale_factor

                    # overwrite the visibility_scale_factors in the file with the v1.2 values
                    sap_group = file['measurement/saps/%s'%(sap_nr,)]
                    del sap_group['visibility_scale_factors']
                    sap_group.create_dataset('visibility_scale_factors', data=scale_factors)

                    extended_shape = visibilities_dB.shape[:] + (2,)
                    scaled_visibilities = np.empty(extended_shape, dtype=np.int8)
                    for sb_nr in range(len(subbands)):
                        scale_factor = 1.0 / scale_factors[sb_nr]
                        scaled_visibilities[:, :, sb_nr, :, 0] = scale_factor * visibilities_dB[:, :, sb_nr, :].real
                        scaled_visibilities[:, :, sb_nr, :, 1] = scale_factor * visibilities_dB[:, :, sb_nr, :].imag

                    # overwrite the visibilities in the file with the v1.2 values
                    del sap_group['visibilities']
                    sap_group.create_dataset('visibilities', data=scaled_visibilities)

            # check if version is 1.2
            with h5py.File(path, "r") as file:
                version_str = file['version'][0]
                self.assertEqual('1.2', version_str)

            # reading the 1.2 file should result in automatic conversion via 1.3 to 1.4 and correction of phases
            result_raw = read_hypercube(path, visibilities_in_dB=False, python_datetimes=True)

            # check if version is now 1.3
            with h5py.File(path, "r") as file:
                version_str = file['version'][0]
                self.assertEqual('1.4', version_str)

            # read in dB as well because we usually plot the visibilities in dB
            result_dB = read_hypercube(path, visibilities_in_dB=True, python_datetimes=True)

            saps_out_raw = result_raw['saps']
            saps_out_dB = result_dB['saps']

            for sap_nr, sap_in_raw in saps_in.items():
                sap_out_raw = saps_out_raw[sap_nr]
                sap_out_dB = saps_out_dB[sap_nr]

                # compare all in/out visibilities
                vis_in_raw = sap_in_raw['visibilities']
                vis_out_raw = sap_out_raw['visibilities']
                vis_out_dB = sap_out_dB['visibilities']

                # for the raw visibilities, comparison is easy...
                # just check the differences in amplitude and in phase
                abs_diff_raw = np.abs(vis_in_raw) - np.abs(vis_out_raw)
                abs_phase_diff_raw = np.abs(np.unwrap(np.angle(vis_in_raw) - np.angle(vis_out_raw), axis=2))
                # phase has no 'meaning' for small (insignificant) amplitudes,
                # so just set the phase difference to zero there
                abs_phase_diff_raw[np.abs(vis_in_raw) <= max(1.0, 1e-3 * max_amplitude)] = 0
                abs_phase_diff_raw[np.abs(vis_out_raw) <= max(1.0, 1e-3 * max_amplitude)] = 0

                # for the visibilities in dB, the phases should be equal to the input phases,
                # no matter whether the visibilities are in dB or raw.
                # but the amplitudes need conversion from dB back to raw first.
                abs_vis_out_raw_from_dB = np.power(10, 0.1 * np.abs(vis_out_dB))
                abs_diff_raw_dB = np.abs(vis_in_raw) - abs_vis_out_raw_from_dB
                abs_phase_diff_raw_dB = np.abs(np.unwrap(np.angle(vis_in_raw) - np.angle(vis_out_dB), axis=2))
                # phase has no 'meaning' for small (insignificant) amplitudes, so just set it to zero there
                abs_phase_diff_raw_dB[np.abs(vis_in_raw) <= max(1.0, 1e-3 * max_amplitude)] = 0
                abs_phase_diff_raw_dB[abs_vis_out_raw_from_dB <= max(1.0, 1e-3 * max_amplitude)] = 0

                amplitude_threshold = 0.10 * max_amplitude
                phase_threshold = 0.025 * 2 * np.pi

                for i in range(vis_in_raw.shape[0]):
                    for j in range(vis_in_raw.shape[1]):
                        for k in range(vis_in_raw.shape[2]):
                            for l in range(vis_in_raw.shape[3]):
                                self.assertLess(abs_diff_raw[i, j, k, l], amplitude_threshold)
                                self.assertLess(abs_diff_raw_dB[i, j, k, l], amplitude_threshold)
                                self.assertLess(abs_phase_diff_raw[i, j, k, l], phase_threshold)
                                self.assertLess(abs_phase_diff_raw_dB[i, j, k, l], phase_threshold)
        finally:
            logger.info('removing test file: %s', path)
            os.remove(path)


    @unit_test
    def test_combine_hypercubes(self):
        logger.info('test_combine_hypercubes')

        paths = []
        try:
            logger.info('generating test data')
            num_saps=2
            num_stations=2
            num_timestamps=2
            MAX_AMPLITUDE = 100
            saps_in = create_hypercube(num_saps=num_saps, num_stations=num_stations,
                                       num_timestamps=num_timestamps, num_subbands_per_sap={0:1,1:1},
                                       snr=1.0, max_signal_amplitude=MAX_AMPLITUDE)

            #write each sap to a seperate file
            for sap_nr, sap_in in saps_in.items():
                path = tempfile.mkstemp()[1]
                paths.append(path)
                logger.info('writing sap %d to %s', sap_nr, path)
                write_hypercube(path, {sap_nr:sap_in}, sas_id=999999, parset="key1=value1\nkey2=value2")

            combined_filepath = combine_hypercubes(paths, output_dir='/tmp', output_filename=os.path.basename(tempfile.mkstemp()[1]))
            self.assertIsNotNone(combined_filepath)

            paths.append(combined_filepath)

            result = read_hypercube(combined_filepath, visibilities_in_dB=False, python_datetimes=True)

            self.assertTrue(result['saps'])
            self.assertEqual(num_saps, len(result['saps']))

            for sap_nr, sap_out in result['saps'].items():
                sap_in = saps_in[sap_nr]

                self.assertTrue(sap_out['timestamps'])
                for t_in, t_out in zip(sap_in['timestamps'], sap_out['timestamps']):
                    self.assertEqual(t_in, t_out)

                self.assertFalse(sap_out['visibilities_in_dB'])
                self.assertEqual(sap_in['visibilities'].shape, sap_out['visibilities'].shape)

                diff = sap_in['visibilities'] - sap_out['visibilities']
                error = np.absolute(diff/sap_in['visibilities'])

                median_error = np.median(error)
                logger.info('median error %s < threshold %s', median_error, 0.05)
                self.assertTrue(median_error < 0.05)

        finally:
            for path in paths:
                logger.info('removing test file: %s', path)
                os.remove(path)

    @unit_test
    def test_common_info_from_parset(self):
        logger.info('test_common_info_from_parset')

        logger.info('generating test data')
        num_saps=1
        num_stations=2
        num_timestamps=3
        saps_in = create_hypercube(num_saps=num_saps, num_stations=num_stations, num_timestamps=num_timestamps)

        parset = parameterset.fromString("""ObsSW.Observation.Campaign.PI="my_PI"
                                            ObsSW.Observation.Campaign.name="my_project_name"
                                            ObsSW.Observation.Campaign.title="my_project_description"
                                            ObsSW.Observation.processType="my_process_type"
                                            ObsSW.Observation.processSubtype="my_process_subtype"
                                            ObsSW.Observation.Campaign.otdbID="my_id"
                                            ObsSW.Observation.antennaArray="LBA"
                                            ObsSW.Observation.Scheduler.taskName="my_task_name"
                                            ObsSW.Observation.startTime="2018-06-11 11:00:00"
                                            ObsSW.Observation.stopTime="2018-06-11 12:00:00"
                                            foo="bar" """)

        path = tempfile.mkstemp()[1]
        try:
            write_hypercube(path, saps_in, parset)

            # make sure the info folder is in the file,
            # and delete it so we can test fill_info_folder_from_parset later on
            with h5py.File(path, "r+") as file:
                self.assertTrue('measurement/info' in file)
                del file['measurement/info']

            with h5py.File(path, "r") as file:
                self.assertFalse('measurement/info' in file)

            # call the actual method under test, fill_info_folder_from_parset
            fill_info_folder_from_parset(path)

            with h5py.File(path, "r") as file:
                self.assertTrue('measurement/info' in file)

            info = read_info_dict(path)
            self.assertEqual('my_PI', info['PI'])
            self.assertEqual('my_id', info['SAS_id'])
            self.assertEqual('my_task_name', info['name'])
            self.assertEqual('my_project_name', info['project'])
            self.assertEqual('my_project_description', info['project_description'])
            self.assertEqual('my_process_type', info['type'])
            self.assertEqual('my_process_subtype', info['subtype'])
            self.assertEqual('LBA', info['antenna_array'])
            self.assertEqual(datetime(2018, 6, 11, 11, 0), info['start_time'])
            self.assertEqual(datetime(2018, 6, 11, 12, 0), info['stop_time'])
            self.assertEqual(timedelta(0, 3600), info['duration'])
        finally:
            os.remove(path)

if __name__ == '__main__':
    unittest.main()
