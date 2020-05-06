#!/usr/bin/env python3
# service.py
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

'''
Simple Service listening
'''

import logging
import pprint
from lofar.messaging import RPCService, ServiceMessageHandler

from lofar.sas.resourceassignment.resourceassignmentestimator.resource_estimators import \
    ObservationResourceEstimator, \
    LongBaselinePipelineResourceEstimator, \
    CalibrationPipelineResourceEstimator, \
    PulsarPipelineResourceEstimator, \
    ImagePipelineResourceEstimator, \
    ReservationResourceEstimator

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.resourceassignmentestimator.config import DEFAULT_RESOURCEESTIMATOR_SERVICENAME

logger = logging.getLogger(__name__)


class ResourceEstimatorHandler(ServiceMessageHandler):
    def __init__(self):
        super().__init__()
        self.observation = ObservationResourceEstimator()
        self.longbaseline_pipeline = LongBaselinePipelineResourceEstimator()
        self.calibration_pipeline = CalibrationPipelineResourceEstimator()
        self.pulsar_pipeline = PulsarPipelineResourceEstimator()
        self.imaging_pipeline = ImagePipelineResourceEstimator()
        self.reservation = ReservationResourceEstimator()

        self.register_service_method("get_estimated_resources", self._get_estimated_resources)

    ##FIXME dirty hack
    def add_id(self, task_estimate, otdb_id):
        estimate_list = task_estimate['estimates']
        for est in estimate_list:
            if 'storage' in est['resource_types']:
                # We only need to do output files, it will be someone else's input
                output_files = est.get('output_files')
                if output_files is None:
                    continue
                for dptype in output_files:
                    for dptype_dict in output_files[dptype]:
                        dptype_dict['properties'][dptype + '_otdb_id'] = otdb_id
                        logger.info('add_id: added %s to properties of data type %s' % (otdb_id, dptype))

        return task_estimate

    #TODO use something else than .values()[0]['estimates'] ??
    def get_subtree_estimate(self, specification_tree):
        ''' Returns a dict { 'estimates': estimates, 'errors': [errors] }. '''
        otdb_id = specification_tree['otdb_id']
        parset = specification_tree['specification']
        predecessors = specification_tree['predecessors']

        # Recursively get estimates for predecessors, which are needed to determine the requested estimates.
        branch_estimates = {}
        for branch in predecessors:
            branch_otdb_id = branch['otdb_id']

            subtree_estimate = self.get_subtree_estimate(branch)
            if subtree_estimate['errors']:
                logger.warning("Could not estimate %s because predecessor %s has errors" % (otdb_id, branch))
                return {'errors': ["Could not estimate %s because predecessor %s has errors" % (otdb_id, branch)]}

            branch_estimates[branch_otdb_id] = subtree_estimate

        logger.info(("Branch estimates for %s\n" % otdb_id) + pprint.pformat(branch_estimates))

        # Construct the requested estimates
        if specification_tree['task_type'] == 'observation':
            return self.add_id(self.observation.verify_and_estimate(parset), otdb_id)
        elif specification_tree['task_type'] == 'reservation':
            return self.add_id(self.reservation.verify_and_estimate(parset), otdb_id)
        elif specification_tree['task_type'] == 'pipeline':
            # Averaging pipeline   
            if specification_tree['task_subtype'] in ['averaging pipeline', 'calibration pipeline']:
                predecessor_estimates = []
                for branch_otdb_id, branch_estimate in list(branch_estimates.items()):
                    logger.info('Looking at predecessor %s' % branch_otdb_id)

                    estimates = branch_estimate['estimates']
                    for est in estimates:
                        if 'output_files' not in est:
                            continue
                        has_uv = 'uv' in est['output_files']
                        has_im = 'im' in est['output_files']
                        if has_uv and not has_im:  # Not a calibrator pipeline
                            logger.info('found %s as the target of pipeline %s' % (branch_otdb_id, otdb_id))
                            predecessor_estimates.extend(estimates)
                            break
                        elif has_im:
                            logger.info('found %s as the calibrator of pipeline %s' % (branch_otdb_id, otdb_id))
                            predecessor_estimates.extend(estimates)
                            break

                return self.add_id(self.calibration_pipeline.verify_and_estimate(parset, predecessor_estimates), otdb_id)

            if len(predecessors) > 1:
                predecessor_otdb_ids = [t['otdb_id'] for t in predecessors]
                logger.warning('Pipeline %d should not have multiple predecessors: %s' % (otdb_id, predecessor_otdb_ids))
                return {'errors': ['Pipeline %d should not have multiple predecessors: %s' % (otdb_id, predecessor_otdb_ids)]}

            predecessor_estimates = list(branch_estimates.values())[0]['estimates']

            if specification_tree['task_subtype'] in ['imaging pipeline', 'imaging pipeline msss']:
                return self.add_id(self.imaging_pipeline.verify_and_estimate(parset, predecessor_estimates), otdb_id)

            if specification_tree['task_subtype'] in ['long baseline pipeline']:
                return self.add_id(self.longbaseline_pipeline.verify_and_estimate(parset, predecessor_estimates), otdb_id)

            if specification_tree['task_subtype'] in ['pulsar pipeline']:
                return self.add_id(self.pulsar_pipeline.verify_and_estimate(parset, predecessor_estimates), otdb_id)
        else: # system tasks?
            logger.warning("ID %s is not a pipeline, observation or reservation." % otdb_id)
            return {'errors': ["ID %s is not a pipeline, observation or reservation." % otdb_id]}

    def _get_estimated_resources(self, specification_tree: dict) -> dict:
        """ Input is like:
            {"otdb_id": otdb_id, "state": 'prescheduled', 'specification': ...,
             'task_type': "pipeline", 'task_subtype': "long baseline pipeline",
            'predecessors': [...]}
        
            reply is something along the lines of:
            {
              '452648': {  # otdb_id
                <see observation and calibration pipeline .py files for example estimator outputs>
              }
            }
        """
        logger.info('get_estimated_resources on: %s' % specification_tree)
        return self.get_subtree_estimate(specification_tree)


def createService(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
    return RPCService(service_name=DEFAULT_RESOURCEESTIMATOR_SERVICENAME,
                      handler_type=ResourceEstimatorHandler,
                      exchange=exchange,
                      broker=broker,
                      num_threads=1)


def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    from optparse import OptionParser
    from lofar.common.util import waitForInterrupt

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the resourceassigner service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the qpid broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the qpid broker, default: %s" % DEFAULT_BUSNAME)
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true',
                      help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with createService(exchange=options.exchange, broker=options.broker):
        waitForInterrupt()


if __name__ == '__main__':
    main()
