# base_pipeline_estimator.py
#
# Copyright (C) 2016
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
from .base_resource_estimator import BaseResourceEstimator

logger = logging.getLogger(__name__)

DATAPRODUCTS = "Observation.DataProducts."
PIPELINE = "Observation.ObservationControl.PythonControl."

#Observation.DataProducts.Output_Correlated.storageClusterName=

class BasePipelineResourceEstimator(BaseResourceEstimator):
    """ base ResourceEstimator for all Pipelines
    """
    def __init__(self, name):
        logger.info("init BasePipelineResourceEstimator")
        super(BasePipelineResourceEstimator, self).__init__(name=name)

    def _getDuration(self, start, end):
        # pipelines could be prescheduled for the resource assigner
        # without a proper start/end time
        # just return a default duration in that case, because slurm will handle the start/end time
        try:
            return super(BasePipelineResourceEstimator, self)._getDuration(start, end)
        except Exception as e:
            logger.error(e)
            logger.info("Could not get duration from parset, returning default pipeline duration of 1 hour")
            return 3600.0

    def _getOutputIdentification(self, identifications):
        """ For pipeline output, there must be exactly 1 (non-duplicate) identification string per
            data product type. (How can you otherwise refer to it unambiguously?) (Observation output can have 1 per SAP.)
        """
        if len(set(identifications)) != 1:  # make set to filter any duplicates
            if not identifications:
                return ''  # allow, because irrelevant if no successor planned
            else:
                logger.error("Cannot have multiple pipeline output identifications. Dropping all but the first in: %s", identifications)  # see doc string
        return identifications[0]

    def _getStorageManagerSizeMultiplier(self, parset):
        """Tries to read the storagemanager set in MoM, or otherwise from the OTDB key from the 'parset'.
        The Specification class puts the right one in a generic storagemanager key.
         If the storagemanager is dysco, then return a special multiplier, otherwise return a default multiplier of 1.
        """
        storagemanager = parset.getString("storagemanager", "")
        if storagemanager == "dysco": #Needs to match with the XML Generator
            return 0.5
        return 1

    def verify(self, parset, predecessor_estimates):
        super(BasePipelineResourceEstimator, self).verify(parset, predecessor_estimates)

        # All pipelines need a predecessor
        if not predecessor_estimates:
            raise ValueError("Pipeline needs predecessors to derive resource estimates.")

