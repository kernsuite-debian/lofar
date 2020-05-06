# calibration_pipeline.py
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

class CalibrationPipelineResourceEstimator(BasePipelineResourceEstimator):
    """ ResourceEstimator for Calibration Pipelines
    """
    def __init__(self):
        logger.info("init CalibrationPipelineResourceEstimator")
        BasePipelineResourceEstimator.__init__(self, name='calibration_pipeline')
        self.required_keys = ('Observation.startTime',
                              'Observation.stopTime',
                              DATAPRODUCTS + 'Input_Correlated.enabled',
                              DATAPRODUCTS + 'Input_Correlated.identifications',
                              #DATAPRODUCTS + 'Input_Correlated.storageClusterName',  # enable if input bandwidth is also estimated
                              DATAPRODUCTS + 'Input_InstrumentModel.enabled',
                              DATAPRODUCTS + 'Input_InstrumentModel.identifications',
                              DATAPRODUCTS + 'Output_InstrumentModel.enabled',
                              DATAPRODUCTS + 'Output_InstrumentModel.identifications',
                              DATAPRODUCTS + 'Output_InstrumentModel.storageClusterName',
                              DATAPRODUCTS + 'Output_Correlated.enabled',
                              DATAPRODUCTS + 'Output_Correlated.identifications',
                              DATAPRODUCTS + 'Output_Correlated.storageClusterName',
                              PIPELINE + 'DPPP.demixer.freqstep',
                              PIPELINE + 'DPPP.demixer.timestep')

    def _calculate(self, parset, predecessor_estimates):
        """ Estimator for calibration pipeline step. Also used for averaging pipeline step.
        calculates: datasize (number of files, file size), bandwidth

        predecessor_estimates looks something like (see also output format in observation.py and (other) pipelines):
        [{
           'resource_types': {'bandwidth': 286331153, 'storage': 1073741824},  # per 'uv' dict
           'resource_count': 20, 'root_resource_group': 'CEP4',
           'output_files': {
             'uv': [{'sap_nr': 2, 'identification': 'mom.G777955.B2.1.C.SAP002.uv.dps',
                     'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 0}}
                   ]
           }
         },
         {
           'resource_types': {'bandwidth': 286331153, 'storage': 1073741824},  # per 'uv' dict
           'resource_count': 20, 'root_resource_group': 'CEP4',
           'output_files': {
             'uv': [{'sap_nr': 3, 'identification': 'mom.G777955.B2.1.C.SAP003.uv.dps',
                     'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 20}}
                   ]
           }
         },
           <optionally more estimates>
        ]

        The reply is something along the lines of the example below
        (assumes task duration of 30 s, and typically 'im' is not in both input_files and output_files)
      {
        'errors': [],
        'estimates': [
        {
          'resource_types': {'bandwidth': 2236995 * 20, 'storage': 67109864 * 20},
          'resource_count': 1, 'root_resource_group': 'CEP4',

          # Note that the 2 predecessor estimates have been converted into an input 'uv' list. This works,
          # as long as input resources are not (yet) scheduled. Currently, resource_* values apply to output_files only.
          'input_files': {
            'uv': [{'sap_nr': 2, 'identification': 'mom.G777955.B2.1.C.SAP002.uv.dps',  # w/ sap only if predecessor is an observation
                    'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 20, 'start_sb_nr': 0}},
                   {'sap_nr': 3, 'identification': 'mom.G777955.B2.1.C.SAP003.uv.dps',  # idem, >1 input SAP possible for e.g. the pulsar pipeline
                    'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 20, 'start_sb_nr': 20}}
                  ]
            'im': [{'identification': ...,  # 'im' example; no 'im' input if predecessor is an observation as above
                    'properties': {'im_file_size': 1000, 'nr_of_im_files': 20, 'start_sb_nr': 0}}]
          },
          'output_files': {
            'uv': [{'identification': 'mom.G777956.B2.1.CPC.uv.dps',
                    'properties': {'uv_file_size': 67108864, 'nr_of_uv_files': 40, 'start_sb_nr': 0}}],
            'im': [{'identification': 'mom.G777956.B2.1.CPC.inst.dps',
                    'properties': {'im_file_size': 1000, 'nr_of_im_files': 20, 'start_sb_nr': 0}}]
          }
        },
          <optionally more estimates>
        ]
      }

        The estimates key has a list to support observations with >1 data product type that can have
        different properties (typically CS/IS (per SAP), but always used for observations w/ >1 SAP).
        This is the reason that observations have an estimate per SAP and per data product type:
        their resource_types values may be different. This is needed to employ resource_count > 1.
        See the observation estimator for an extensive observation data product type example.

        For each estimate, the total output_files resources to be claimed is resource_count * resources_types.
        Thus resource_types is a total across all output_files content. The idea is to keep this
        singular per data product type (inner list size 1), but for pipelines this is currently not possible.

        Note that input_files resources are currently not included or claimed.
        However, input_files properties must be added to resource claims to later generate parset values.
        This caveat must be fixed at some point, but until then, we cannot have input_files-only estimates.
        (After it is fixed, we should not have input_files-only estimates either; it makes no sense.)

        For pipelines we currently do not support output to multiple storage areas, so resource_count is 1.
        We still have to deal with input_files from an observation with >1 SAP (used for the pulsar pipeline).
        For this case, we generate 1 estimate, but use a list per data product type (e.g. 'uv': [...]).
        Also, we may need multiple data product types in one pipeline estimate, but there the reason
        is that e.g. 'uv' and 'im' files belong together, so we produce one estimate per pair,
        (but again, it is a pipeline so currently it is collapsed to a single estimate, thus resource_count 1).
        The inner data product type list can be removed once pipelines also use resource_count > 1.

        Some RA_Services design aspects work well. Others fail to capture the underlying concepts close enough, hence inelegance.
        """
        logger.debug("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)

        result = {'errors': [], 'estimates': []}

        freq_step = parset.getInt(PIPELINE + 'DPPP.demixer.freqstep', 1) #TODO, should these have defaults?
        time_step = parset.getInt(PIPELINE + 'DPPP.demixer.timestep', 1)
        reduction_factor = freq_step * time_step
        if reduction_factor < 1:
            logger.error('freqstep * timestep is not positive: %d' % reduction_factor)
            result['errors'].append('freqstep * timestep is not positive: %d' % reduction_factor)
        if not parset.getBool(DATAPRODUCTS + 'Input_Correlated.enabled') or \
           not parset.getBool(DATAPRODUCTS + 'Output_Correlated.enabled'):
            logger.error('Input_Correlated or Output_Correlated is not enabled')
            result['errors'].append('Input_Correlated or Output_Correlated is not enabled')

        duration = self._getDuration(parset.getString('Observation.startTime'),
                                     parset.getString('Observation.stopTime'))

        input_idents_uv = parset.getStringVector(DATAPRODUCTS + 'Input_Correlated.identifications')
        input_files_uv = self.get_inputs_from_predecessors(predecessor_estimates, input_idents_uv, 'uv')
        if not input_files_uv:
            logger.error('Missing uv dataproducts in predecessor output_files')
            result['errors'].append('Missing uv dataproducts in predecessor output_files')
        input_files = input_files_uv

        have_im_input = parset.getBool(DATAPRODUCTS + 'Input_InstrumentModel.enabled')
        if have_im_input:
            input_idents_im = parset.getStringVector(DATAPRODUCTS + 'Input_InstrumentModel.identifications')
            input_files_im = self.get_inputs_from_predecessors(predecessor_estimates, input_idents_im, 'im')
            if not input_files_im:
                logger.error('Input_InstrumentModel enabled, but missing \'im\' dataproducts in predecessor output_files')
                result['errors'].append('Input_InstrumentModel enabled, but missing \'im\' dataproducts in predecessor output_files')
            input_files['im'] = input_files_im['im']

        if result['errors']:
            return result

        estimate = {'input_files': input_files}

        # NOTE: input bandwidth is currently not included in the resulting estimate.
        # Proper input bandwidth estimation has limited use currently and is tricky, because of pipeline duration estimation, tmp files,
        # multiple passes, nr nodes and caching, but for sure also because bandwidth must be tied to *predecessor* storage!
        #input_cluster_uv = parset.getString(DATAPRODUCTS + 'Input_Correlated.storageClusterName')

        output_ident_uv = self._getOutputIdentification( parset.getStringVector(DATAPRODUCTS + 'Output_Correlated.identifications') )
        output_cluster_uv = parset.getString(DATAPRODUCTS + 'Output_Correlated.storageClusterName')
        have_im_output = parset.getBool(DATAPRODUCTS + 'Output_InstrumentModel.enabled')
        if have_im_output:
            output_ident_im = self._getOutputIdentification( parset.getStringVector(DATAPRODUCTS + 'Output_InstrumentModel.identifications') )

            output_cluster_im = parset.getString(DATAPRODUCTS + 'Output_InstrumentModel.storageClusterName')
            if output_cluster_uv != output_cluster_im:
                logger.error('Output_InstrumentModel is enabled, but its storageClusterName \'%s\' differs from Output_Correlated.storageClusterName \'%s\'',
                             output_cluster_uv, output_cluster_im)
                result['errors'].append('Output_InstrumentModel is enabled, but its storageClusterName \'%s\' differs from Output_Correlated.storageClusterName \'%s\'' % (output_cluster_im, output_cluster_uv))

        # Observations can have multiple output estimates, but currently pipelines do not.
        # (Reason: incomplete info available and effective assigner claim merging is harder)
        # As long as this is the case, try to do a best effort to map any predecessor (observation or pipeline) to single estimate output.
        nr_input_files = sum([uv_dict['properties']['nr_of_uv_files'] for uv_dict in input_files['uv']])

        # Assume all uv file sizes are the same size as in dict 0. For uv data, we never had pipelines with >1 dict,
        # but this could be meaningful when averaging multiple SAPs in 1 go (and no further processing steps).
        # (Never done, since subsequent pipeline steps must then also work on all SAPs. But averaging could be the last step.)
        # The potential other case is >1 dict from different observations with different file sizes.
        # In general, this requires >1 output estimate dict, which the estimate format allows, but is currently only used for observations.
        uv_input_file_size = input_files['uv'][0]['properties']['uv_file_size']

        # For start_sb_nr, take the minimum of all start_sb_nr values.
        # This fails when the input identifications has a sparse SAP list, but that was never supported either.
        # A likely setup where this could happen is LOTAAS+pulp, but pulp has no equivalent to start_sb[g]_nr,
        # so solve here and in the pulsar pipeline pragmatically each.
        start_sb_nr = min([uv_dict['properties']['start_sb_nr'] for uv_dict in input_files['uv']])

        # TODO: This output file size calculation comes from the (old) Scheduler without explaining comments.
        # The reason why it isn't a simple division, is that parts of the metadata are not reduced in size (and casacore storage managers).
        # With reduction_factor 1, computed output size increases by 53%... Casacore storage managers may change size, but that much?!?
        # If you can figure out what/how, please fix this calculation. Avoid unnamed magic values and document why!
        logger.debug("calculate correlated data size")
        size_multiplier = self._getStorageManagerSizeMultiplier(parset)
        new_size = uv_input_file_size / float(reduction_factor) * size_multiplier
        uv_output_file_size = int(new_size + new_size / 64.0 * (1.0 + reduction_factor) + new_size / 2.0)

        nr_output_files = nr_input_files  # pure 'map' (bijective) operation, no split or reduce
        logger.info("correlated_uv: {} files of {} bytes each".format(nr_output_files, uv_output_file_size))
        estimate['output_files'] = {'uv': [{'identification': output_ident_uv,
                'properties': {'nr_of_uv_files': nr_output_files, 'uv_file_size': uv_output_file_size, 'start_sb_nr': start_sb_nr}}]}
        data_size = uv_output_file_size

        # If instrument model output is needed, add it to the same estimate,
        # since it must be written to the same storage as the uv output (same nr_output_files).
        if have_im_output:
            logger.info("calculate instrument-model data size")
            im_file_size = 1000  # TODO: 1 kB was hardcoded in the Scheduler

            logger.info("correlated_im: {} files {} bytes each".format(nr_output_files, im_file_size))
            estimate['output_files']['im'] = [{'identification': output_ident_im,
                    'properties': {'nr_of_im_files': nr_output_files, 'im_file_size': im_file_size, 'start_sb_nr': start_sb_nr}}]
            # FIXME I don't think this is technically correct, as the IM files are sometimes created and used, just not a required export?
            # Need to split averaging pipeline and calibration pipeline
            data_size += im_file_size

        total_data_size = data_size * nr_output_files  # bytes
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

