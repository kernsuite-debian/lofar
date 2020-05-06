# pulsar_pipeline.py
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

class PulsarPipelineResourceEstimator(BasePipelineResourceEstimator):
    """ ResourceEstimator for Pulsar Pipelines
    """
    def __init__(self):
        logger.info("init PulsarPipelineResourceEstimator")
        BasePipelineResourceEstimator.__init__(self, name='pipeline')  #FIXME name='pulsar_pipeline'
        self.required_keys = ('Observation.startTime',
                              'Observation.stopTime',
                              DATAPRODUCTS + 'Input_CoherentStokes.enabled',
                              DATAPRODUCTS + 'Input_CoherentStokes.identifications',
                              #DATAPRODUCTS + 'Input_CoherentStokes.storageClusterName',  # enable if input bandwidth is also estimated
                              DATAPRODUCTS + 'Input_IncoherentStokes.enabled',
                              DATAPRODUCTS + 'Input_IncoherentStokes.identifications',
                              #DATAPRODUCTS + 'Input_IncoherentStokes.storageClusterName',  # enable if input bandwidth is also estimated
                              DATAPRODUCTS + 'Output_Pulsar.enabled', 
                              DATAPRODUCTS + 'Output_Pulsar.identifications',
                              DATAPRODUCTS + 'Output_Pulsar.storageClusterName')

    def _calculate(self, parset, predecessor_estimates):
        """ Estimate for Pulsar Pipeline
        calculates: datasize (number of files, file size), bandwidth

        For a predecessor_estimates example, see the observation estimator code.

        For a return value example, see the calibration/averaging estimator code,
        except that here we have instead of 'cs' or 'is', e.g.:
          'pulp': {'identification': ...,
                   'properties': {'nr_of_pulp_files': 48, 'pulp_file_size': 185104}}
        """
        logger.debug("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)

        result = {'errors': [], 'estimates': []}

        if not parset.getBool(DATAPRODUCTS + 'Output_Pulsar.enabled'):
            logger.error('Output_Pulsar is not enabled')
            result['errors'].append('Output_Pulsar is not enabled')

        duration = self._getDuration(parset.getString('Observation.startTime'),
                                     parset.getString('Observation.stopTime'))

        # The current XML generator can produce a pulsar pipeline step that operates on 1 SAP,
        # however, pulsar astronomers produce an XML that works on all SAPs (CS+IS) of an obs.
        # This is regular and going on for years, so we need to support multi-SAP pulp input.
        # Note that when selecting obs SAP nr > 0 or a sparse SAP nr range, TAB nrs in pulp filenames do not
        # match TAB nrs in obs filenames, because there is no pulp equiv of start_sb[g]_nr. Nobody cares.
        # (Then there is the possibility of multi-obs pulp input. As-is that may turn out to work as well.)
        input_files = {}
        input_idents_cs = parset.getStringVector(DATAPRODUCTS + 'Input_CoherentStokes.identifications')
        input_files_cs = self.get_inputs_from_predecessors(predecessor_estimates, input_idents_cs, 'cs')
        if input_files_cs:
            input_files['cs'] = input_files_cs['cs']
        input_idents_is = parset.getStringVector(DATAPRODUCTS + 'Input_IncoherentStokes.identifications')
        input_files_is = self.get_inputs_from_predecessors(predecessor_estimates, input_idents_is, 'is')
        if input_files_is:
            input_files['is'] = input_files_is['is']
        if not input_files:
            logger.error('Missing \'cs\' or \'is\' dataproducts in predecessor output_files')
            result['errors'].append('Missing \'cs\' or \'is\' dataproducts in predecessor output_files')

        if result['errors']:
            return result

        estimate = {'input_files': input_files}

        # NOTE: input bandwidth is currently not included in the resulting estimate.
        # Proper input bandwidth est has limited use and is tricky, because of pipeline duration est, tmp files, multiple passes, nr nodes and caching, ...
        #input_cluster_cs = parset.getString(DATAPRODUCTS + 'Input_CoherentStokes.storageClusterName')
        #input_cluster_is = parset.getString(DATAPRODUCTS + 'Input_IncoherentStokes.storageClusterName')

        output_ident_pulp = self._getOutputIdentification( parset.getStringVector(DATAPRODUCTS + 'Output_Pulsar.identifications') )
        output_cluster_pulp = parset.getString(DATAPRODUCTS + 'Output_Pulsar.storageClusterName')

        # The pulsar pipeline ('pulp') produces 1 data product per tied-array beam, it seems also for complex voltages (XXYY) and stokes IQUV(?).
        # For XXYY it really needs all 4 components at once. For IQUV this is less important, but currently we treat it the same (1 obs output estimate).
        # Note that it also produces 1 additional "summary" data product per data product *type* (i.e. 1 for 'cs' and/or 1 for 'is'),
        # but the RA_Services sub-system does not know about it. Adding support may be a waste of time(?).
        # Currently, RO controlled pulp grabs all inputs given some project name/id(?) and obs id, not from rotspservice generated parset parts.
        nr_input_files = 0
        if 'cs' in input_files:
            nr_input_files += sum([cs_dict['properties']['nr_of_cs_files'] / \
                                   cs_dict['properties']['nr_of_cs_stokes'] for cs_dict in input_files['cs']])
        if 'is' in input_files:
            nr_input_files += sum([is_dict['properties']['nr_of_is_files'] / \
                                   is_dict['properties']['nr_of_is_stokes'] for is_dict in input_files['is']])

        logger.debug("calculate pulp data size")
        pulp_file_size = 1000  # TODO: 1 kB was hardcoded in the Scheduler

        logger.info("pulsar_pipeline pulp: {} files {} bytes each".format(nr_input_files, pulp_file_size))
        estimate['output_files'] = {'pulp': [{'identification': output_ident_pulp,
                                              'properties': {'nr_of_pulp_files': nr_input_files,
                                                             'pulp_file_size': pulp_file_size}}]}

        # count total data size
        total_data_size = nr_input_files * pulp_file_size
        if total_data_size > 0:
            bandwidth = int(ceil(8 * total_data_size / duration))  # bits/second
            estimate['resource_types'] = {'bandwidth': bandwidth, 'storage': total_data_size}
            estimate['resource_count'] = 1
            estimate['root_resource_group'] = output_cluster_pulp
        else:
            logger.error('Estimated total data size is zero!')
            result['errors'].append('Estimated total data size is zero!')

        result['estimates'].append(estimate)

        return result

