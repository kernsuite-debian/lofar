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

import numpy as np
from datetime import datetime, timedelta

from lofar.qa.geoconversions import *

import logging
import math
logger = logging.getLogger(__name__)

def create_hypercube(num_saps=3, num_stations=5, num_timestamps=11, num_subbands_per_sap=None, snr=0.9,
                     max_signal_amplitude=1e5, parallel_to_cross_polarization_ratio=20.0,
                     num_phase_wraps=1.0,
                     num_time_sawtooth_periods=1, num_subband_sawtooth_periods=0,
                     num_time_cos_periods=0, num_subband_cos_periods=0):
    data = {}
    assert max_signal_amplitude > 1.0
    logger.info('create_hypercube: num_saps=%s num_stations=%s num_timestamps=%s num_subbands_per_sap=%s snr=%s max_amplitude=%s pol_ratio=%s' \
                'num_phase_wraps=%s num_time_sawtooth_periods=%s num_subband_sawtooth_periods=%s num_time_cos_periods=%s num_subband_cos_periods=%s',
                num_saps, num_stations, num_timestamps, num_subbands_per_sap, snr, max_signal_amplitude, parallel_to_cross_polarization_ratio,
                num_phase_wraps, num_time_sawtooth_periods, num_subband_sawtooth_periods, num_time_cos_periods, num_subband_cos_periods)

    if num_subbands_per_sap is None:
        num_subbands_per_sap = {}
        for sap_nr in range(num_saps):
            num_subbands_per_sap[sap_nr] = 13*(sap_nr+1)

    stations = ['CS%03d' % (i + 1) for i in range(num_stations)]
    baselines = []
    for idx, station1 in enumerate(stations):
        for station2 in stations[idx:]:
            baselines.append((station1, station2))

    num_baselines = len(baselines)

    for sap_nr in range(num_saps):
        #generate nice test visibilities
        num_subbands = num_subbands_per_sap[sap_nr]

        #generate 'ticks' along the polarization-axes
        polarizations = ['xx', 'xy', 'yx', 'yy']
        parallel_pol_idxs = [0,3]
        cross_pol_idxs = [1,2]

        # create synthetic visibilities signal
        baseline_visibilities_signal = np.zeros((num_timestamps, num_subbands, len(polarizations)), dtype=np.complex64)

        for subband_idx in range(num_subbands):
            # subband_ratio ranges from 0 to-but-not-including 1.0
            # this ensures the phases start at 0rad, and sweep up to but not including 2PIrad
            subband_ratio = ((subband_idx+1) / float(num_subbands)) if num_subbands > 1 else 1.0
            sawtooth_subband_amplitude = math.fmod(subband_ratio * num_subband_sawtooth_periods, 1)
            if sawtooth_subband_amplitude == 0.0:
                sawtooth_subband_amplitude = 1.0
            cos_subband_amplitude = 0.5 * (1.0 + np.cos(num_subband_cos_periods * subband_ratio * 2 * np.pi))

            for timestamp_idx in range(num_timestamps):
                # timestamp_ratio ranges from-and-including 1.0 to 'small'-but-not-zero
                # this prevents the visibility_value from becoming 0 (from which we cannot take the log)
                timestamp_ratio = ((timestamp_idx+1) / float(num_timestamps)) if num_timestamps > 1 else 1.0
                sawtooth_time_amplitude = math.fmod(timestamp_ratio * num_time_sawtooth_periods, 1)
                if sawtooth_time_amplitude == 0.0:
                    sawtooth_time_amplitude = 1.0
                cos_time_amplitude = 0.5*(1.0+np.cos(num_time_cos_periods*timestamp_ratio * 2 * np.pi))

                # create synthetic visibility_value
                # amplitude varies in time. make sure the smallest amplitude is >= 1.0,
                # because otherwise we cannot store them with enough bits in dB's
                #amplitude = max(1.0, max_signal_amplitude * (sawtooth_time + sawtooth_subband + cos_subband + cos_time)/4.0)
                amplitude = max(1.0, max_signal_amplitude * (sawtooth_time_amplitude * sawtooth_subband_amplitude *
                                                             cos_subband_amplitude * cos_time_amplitude))
                # phase varies in subband direction
                phase = np.exp(1j * subband_ratio * 2.0 * np.pi * num_phase_wraps)
                visibility_value_parallel = amplitude * phase
                visibility_value_cross = max(1.0, amplitude/parallel_to_cross_polarization_ratio) * phase
                baseline_visibilities_signal[timestamp_idx, subband_idx,parallel_pol_idxs] = visibility_value_parallel
                baseline_visibilities_signal[timestamp_idx, subband_idx, cross_pol_idxs] = visibility_value_cross

        # use/apply the same visibilities for each baseline
        visibilities_signal = np.zeros((num_baselines, num_timestamps, num_subbands, len(polarizations)), dtype=np.complex64)
        for i in range(num_baselines):
            visibilities_signal[i,:,:,:] = baseline_visibilities_signal

        # create some noise
        visibilities_noise = np.zeros((num_baselines, num_timestamps, num_subbands, len(polarizations)), dtype=np.complex64)
        visibilities_noise.real = np.random.normal(size=visibilities_noise.shape)
        visibilities_noise.imag = np.random.normal(size=visibilities_noise.shape)
        visibilities_noise *= max_signal_amplitude/np.max(np.abs(visibilities_noise))

        # add signal and noise according to given ratio
        visibilities = snr*visibilities_signal + (1.0-snr)*visibilities_noise

        # and some empty flagging
        flagging = np.zeros(visibilities.shape, dtype=np.bool)

        # generate 'ticks' along the timestamp-axis
        now = datetime.utcnow()
        timestamps = [now+timedelta(minutes=i) for i in range(num_timestamps)]

        # generate 'ticks' along the central_frequencies-axes
        # fill the HBA frequency range of 120-240MHz
        central_frequencies = [120e6+i*120e6/max(1,num_subbands-1) for i in range(num_subbands)]
        sb_offset = sum([len(sap['subbands']) for sap in data.values()])
        subbands = [i for i in range(sb_offset, sb_offset+num_subbands)]

        # create some synthetic antenna locations
        antenna_locations = {'XYZ': {}, 'PQR': {}, 'WGS84' : {}}
        for i, station in enumerate(stations):
            ratio = float(i)/len(stations)
            xyz_pos = (np.cos(ratio*2*np.pi),np.sin(ratio*2*np.pi),0)
            antenna_locations['XYZ'][station] = xyz_pos
            antenna_locations['PQR'][station] = pqr_cs002_from_xyz(xyz_pos)
            antenna_locations['WGS84'][station] = geographic_from_xyz(xyz_pos)

        # combine all data in the dict
        data[sap_nr] = { 'baselines':baselines,
                         'timestamps':timestamps,
                         'central_frequencies':central_frequencies,
                         'subbands':subbands,
                         'polarizations':polarizations,
                         'visibilities':visibilities,
                         'flagging':flagging,
                         'antenna_locations': antenna_locations}
    return data

