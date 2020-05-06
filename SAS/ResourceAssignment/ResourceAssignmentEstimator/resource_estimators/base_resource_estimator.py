# base_resource_estimator.py
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

""" Base class for Resource Estimators
"""
import logging
import copy
import pprint
from datetime import datetime
from lofar.common.datetimeutils import totalSeconds, parseDatetime
from datetime import datetime, timedelta
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)


class BaseResourceEstimator(object):
    """ Base class for all other resource estimator classes
    """
    def __init__(self, name):
        self.name = name
        self.required_keys = ()

    def _checkParsetForRequiredKeys(self, parset):
        """ Check if all required keys needed are available """
        logger.debug("required keys: %s" % ', '.join(self.required_keys))
        logger.debug("parset   keys: %s" % ', '.join(list(parset.keys())))
        missing_keys = set(self.required_keys) - set(parset.keys())
        if missing_keys:
            logger.error("missing keys: %s" % ', '.join(missing_keys))
            return False
        return True

    def _getDuration(self, start, end):
        """ Returns number of fractional seconds as a float(!) (as totalSeconds())
            between start and end.
        """
        startTime = parseDatetime(start)
        endTime = parseDatetime(end)
        if startTime >= endTime:
            logger.warning("startTime is not before endTime")
            return 1.0 ##TODO To prevent divide by zero later
        return totalSeconds(endTime - startTime)
        # TODO check if this makes duration = int(parset.get('duration', 0)) as a key reduntant?
        # TODO Should probably be refactored to use the Specification, maybe when RA needs to change for OTDB replacement

    def _calculate(self, parset, predecessor_estimates=[]):
        raise NotImplementedError('calculate() in base class is called. Please implement calculate() in your subclass')

    def _add_predecessor_output(self, input_files, predecessor_estimate, identification, dptype):
        """ Add copy of an element under the dptype key in predecessor_estimate
            to input_files if it matches identification, or else return False.
            But see comment below on resource_count collapsing to convert resource_count > 1 to pipelines.
        """
        if 'output_files' not in predecessor_estimate or \
           dptype not in predecessor_estimate['output_files']:
            return False

        for dt_values in predecessor_estimate['output_files'][dptype]:
            if dt_values['identification'] != identification:
                continue

            logger.info('Found predecessor output identification matching %s', identification)
            if dptype not in input_files:
                input_files[dptype] = []
            input_files[dptype].append(copy.deepcopy(dt_values))

            # Observation estimates have resource_count > 1 to be able to assign each output to another resource,
            # but that is currently not supported for pipelines. We only use input parameters to produce parset filenames etc,
            # but not to reserve resources (not covered by resource count). Collapse to implied resource_count of 1.
            input_files[dptype][-1]['properties']['nr_of_' + dptype + '_files'] *= predecessor_estimate['resource_count']
            return True

        return False

    def get_inputs_from_predecessors(self, predecessor_estimates, identifications, dptype):
        """ Return copy of parts with dptype in predecessor_estimates matching identifications
            If any of identifications could not be found, the empty dict is returned.
            dptype is one of the observation/pipeline data product types, e.g. 'uv', 'cs', 'pulp', ...
            No duplicates in the identifications iterable!

            See the calibration and observation pipeline estimators for parameter value examples.
        """
        input_files = {}
        logger.info('get_inputs_from_predecessors: parsing predecessor output for identifications: %s', identifications)

        for identification in identifications:
            found = False
            for estimate in predecessor_estimates:
                if self._add_predecessor_output(input_files, estimate, identification, dptype):
                    found = True
                    break
            if not found:
                logger.warn('get_inputs_from_predecessors: failed to find predecessor output matching %s', identification)
                return {}

        logger.info('get_inputs_from_predecessors: filtered predecessor output for dptype=' + dptype +
                    ' down to: \n' + pprint.pformat(input_files))
        return input_files

    def verify(self, parset, predecessor_estimates):
        if not self._checkParsetForRequiredKeys(parset):
            raise ValueError('The parset is incomplete')

    def verify_and_estimate(self, parset, predecessor_estimates=[]):
        """ Create estimates for an observation or pipeline step based on its parset and,
            in case of a pipeline step, all estimates of its direct predecessor(s).
        """

        self.verify(parset, predecessor_estimates)

        result = self._calculate(parameterset(parset), predecessor_estimates)

        logger.info('Estimates for %s:' % self.name)
        logger.info(pprint.pformat(result))

        return result
