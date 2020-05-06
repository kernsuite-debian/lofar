# longbaseline_pipeline.py
#
# Copyright (C) 2016, 2017
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id$

import logging
from math import ceil
from .base_pipeline_estimator import BasePipelineResourceEstimator

logger = logging.getLogger(__name__)

DATAPRODUCTS = "Observation.DataProducts."
PIPELINE = "Observation.ObservationControl.PythonControl."

#Observation.DataProducts.Output_Correlated.storageClusterName=

class LongBaselinePipelineResourceEstimator(BasePipelineResourceEstimator):
    """ ResourceEstimator for Long Baseline Pipelines
    """
    def __init__(self):
        logger.info("init LongBaselinePipelineResourceEstimator")
        BasePipelineResourceEstimator.__init__(self, name='longbaseline_pipeline')
        self.required_keys = ('Observation.startTime',
                              'Observation.stopTime',
                              DATAPRODUCTS + 'Input_Correlated.enabled',
                              DATAPRODUCTS + 'Input_Correlated.identifications',
                              #DATAPRODUCTS + 'Input_Correlated.storageClusterName',  # enable if input bandwidth is also estimated
                              DATAPRODUCTS + 'Output_Correlated.enabled',
                              DATAPRODUCTS + 'Output_Correlated.identifications',
                              DATAPRODUCTS + 'Output_Correlated.storageClusterName',
                              PIPELINE + 'LongBaseline.subbandgroups_per_ms',
                              PIPELINE + 'LongBaseline.subbands_per_subbandgroup')



    def _calculate(self, parset, predecessor_estimates):
        """ Estimator for long baseline pipeline step.
        calculates: datasize (number of files, file size), bandwidth

        For a predecessor_estimates example, see the calibration/averaging
        (and possibly the observation) estimator code.

        For a return value example, see the calibration/averaging estimator code,
        except that there is no 'im' input or output, and instead of a 'start_sb_nr',
        we have a 'start_sbg_nr' property.
        """
        logger.debug("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)

        result = {'errors': [], 'estimates': []}

        subbandgroups_per_ms = parset.getInt(PIPELINE + 'LongBaseline.subbandgroups_per_ms', 0) #TODO, should these have defaults?
        subbands_per_subbandgroup = parset.getInt(PIPELINE + 'LongBaseline.subbands_per_subbandgroup', 0)
        if subbandgroups_per_ms < 1 or subbands_per_subbandgroup < 1:
            logger.error('subbandgroups_per_ms or subbands_per_subbandgroup is not valid')
            result['errors'].append('subbandgroups_per_ms or subbands_per_subbandgroup is not valid')
        if not parset.getBool(DATAPRODUCTS + 'Output_Correlated.enabled'):
            logger.error('Output_Correlated is not enabled')
            result['errors'].append('Output_Correlated is not enabled')

        duration = self._getDuration(parset.getString('Observation.startTime'),
                                     parset.getString('Observation.stopTime'))

        input_idents_uv = parset.getStringVector(DATAPRODUCTS + 'Input_Correlated.identifications')
        input_files = self.get_inputs_from_predecessors(predecessor_estimates, input_idents_uv, 'uv')
        if not input_files:
            logger.error('Missing uv dataproducts in predecessor output_files')
            result['errors'].append('Missing uv dataproducts in predecessor output_files')

        if result['errors']:
            return result

        estimate = {'input_files': input_files}

        # NOTE: input bandwidth is currently not included in the resulting estimate.
        # Proper input bandwidth est has limited use and is tricky, because of pipeline duration est, tmp files, multiple passes, nr nodes and caching, ...
        #input_cluster_uv = parset.getString(DATAPRODUCTS + 'Input_Correlated.storageClusterName')

        output_ident_uv = self._getOutputIdentification( parset.getStringVector(DATAPRODUCTS + 'Output_Correlated.identifications') )
        output_cluster_uv = parset.getString(DATAPRODUCTS + 'Output_Correlated.storageClusterName')

        # See the calibration pipeline estimator for why this is currently done this way.
        nr_input_files = sum([uv_dict['properties']['nr_of_uv_files'] for uv_dict in input_files['uv']])
        uv_input_file_size = input_files['uv'][0]['properties']['uv_file_size']
        start_sb_nr = min([uv_dict['properties']['start_sb_nr'] for uv_dict in input_files['uv']])

        if nr_input_files % (subbands_per_subbandgroup * subbandgroups_per_ms) > 0:
            logger.error('subbandgroups_per_ms and subbands_per_subbandgroup not a multiple of number of inputs')
            result['errors'].append('subbandgroups_per_ms and subbands_per_subbandgroup not a multiple of number of inputs')
        nr_output_files = nr_input_files / (subbands_per_subbandgroup * subbandgroups_per_ms)

        logger.debug("calculate correlated data size")
        # Not used as the current calculation is bogus any way
        # size_multiplier = self._getStorageManagerSizeMultiplier(parset)
        uv_output_file_size = 1000  # TODO: 1 kB was hardcoded in the Scheduler

        # Computing start_sbg_nr in the same way as nr_output_files may not always work out as perhaps originally intended,
        # e.g. if this is SAP 1, while SAP 0 had a different nr of subbands, but for filenames it doesn't really matter and we cannot easily do a lot better.
        start_sbg_nr = start_sb_nr / (subbands_per_subbandgroup * subbandgroups_per_ms)

        logger.info("correlated_uv: {} files {} bytes each".format(nr_output_files, uv_output_file_size))
        estimate['output_files'] = {'uv': [{'identification': output_ident_uv,
                                            'properties': {'nr_of_uv_files': nr_output_files,
                                                           'uv_file_size': uv_output_file_size,
                                                           'start_sbg_nr': start_sbg_nr}}]}

        total_data_size = nr_output_files * uv_output_file_size  # bytes
        if total_data_size:
            bandwidth = int(ceil(8 * total_data_size / duration))  # bits/second
            estimate['resource_types'] = {'bandwidth': bandwidth, 'storage': total_data_size}
            estimate['resource_count'] = 1
            estimate['root_resource_group'] = output_cluster_uv
        else:
            logger.error('Estimated total data size is zero!')
            result['errors'].append('Estimated total data size is zero!')

        result['estimates'].append(estimate)

        return result

