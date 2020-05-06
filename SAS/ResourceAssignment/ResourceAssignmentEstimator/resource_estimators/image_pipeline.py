# image_pipeline.py
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
#Observation.ObservationControl.PythonControl.AWimager

class ImagePipelineResourceEstimator(BasePipelineResourceEstimator):
    """ ResourceEstimator for Imaging Pipelines
    """
    def __init__(self):
        logger.info("init ImagePipelineResourceEstimator")
        BasePipelineResourceEstimator.__init__(self, name='imaging_pipeline')
        self.required_keys = ('Observation.startTime',
                              'Observation.stopTime',
                              DATAPRODUCTS + 'Input_Correlated.enabled',
                              DATAPRODUCTS + 'Input_Correlated.identifications',
                              #DATAPRODUCTS + 'Input_Correlated.storageClusterName',  # enable if input bandwidth is also estimated
                              DATAPRODUCTS + 'Output_SkyImage.enabled',
                              DATAPRODUCTS + 'Output_SkyImage.identifications',
                              DATAPRODUCTS + 'Output_SkyImage.storageClusterName',
                              PIPELINE + 'Imaging.slices_per_image',
                              PIPELINE + 'Imaging.subbands_per_image')

    def _calculate(self, parset, predecessor_estimates):
        """ Estimate for imaging pipeline step. Also used for MSSS imaging pipeline.
        calculates: datasize (number of files, file size), bandwidth

        For a predecessor_estimates example, see the calibration/averaging
        (and possibly the observation) estimator code.

        For a return value example, see the calibration/averaging estimator code,
        except that here we have instead of 'uv' and optionally 'im', e.g.:
          'img': {'identification': ...,
                  'properties': {'nr_of_img_files': 481, 'img_file_size': 148295}}
        """
        logger.debug("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)

        result = {'errors': [], 'estimates': []}

        slices_per_image = parset.getInt(PIPELINE + 'Imaging.slices_per_image', 0) #TODO, should these have defaults?
        subbands_per_image = parset.getInt(PIPELINE + 'Imaging.subbands_per_image', 0)
        if slices_per_image < 1 or subbands_per_image < 1:
            logger.error('slices_per_image or subbands_per_image is not valid')
            result['errors'].append('slices_per_image or subbands_per_image is not valid')
        if not parset.getBool(DATAPRODUCTS + 'Output_SkyImage.enabled'):
            logger.error('Output_SkyImage is not enabled')
            result['errors'].append('Output_SkyImage is not enabled')

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

        output_ident_img = self._getOutputIdentification( parset.getStringVector(DATAPRODUCTS + 'Output_SkyImage.identifications') )
        output_cluster_img = parset.getString(DATAPRODUCTS + 'Output_SkyImage.storageClusterName')

        # See the calibration pipeline estimator for why this is currently done this way.
        nr_input_subbands = sum([uv_dict['properties']['nr_of_uv_files'] for uv_dict in input_files['uv']])
        uv_file_size = input_files['uv'][0]['properties']['uv_file_size']
        if nr_input_subbands % (subbands_per_image * slices_per_image) > 0:
            logger.error('slices_per_image and subbands_per_image not a multiple of number of inputs')
            result['errors'].append('slices_per_image and subbands_per_image not a multiple of number of inputs')
        nr_images = nr_input_subbands / (subbands_per_image * slices_per_image)

        logger.debug("calculate sky image data size")
        # Not used as the current calculation is bogus any way
        # size_multiplier = self._getStorageManagerSizeMultiplier(parset)
        img_file_size = 1000  # TODO: 1 kB was hardcoded in the Scheduler

        logger.info("sky_images: {} files {} bytes each".format(nr_images, img_file_size))
        estimate['output_files'] = {'img': [{'identification': output_ident_img,
                                             'properties': {'nr_of_img_files': nr_images,
                                                            'img_file_size': img_file_size}}]}

        total_data_size = nr_images * img_file_size  # bytes
        if total_data_size:
            bandwidth = int(ceil(8 * total_data_size / duration))  # bits/second
            estimate['resource_types'] = {'bandwidth': bandwidth, 'storage': total_data_size}
            estimate['resource_count'] = 1
            estimate['root_resource_group'] = output_cluster_img
        else:
            logger.error('Estimated total data size is zero!')
            result['errors'].append('Estimated total data size is zero!')

        result['estimates'].append(estimate)

        return result

