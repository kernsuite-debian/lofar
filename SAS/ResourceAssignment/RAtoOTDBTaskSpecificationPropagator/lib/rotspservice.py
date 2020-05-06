#!/usr/bin/env python3

# rotspservice.py: RAtoOTDBTaskSpecificationPropagator listens on the lofar ?? bus and calls onTaskScheduled
#
# Copyright (C) 2015
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: rotspservice.py 1580 2015-09-30 14:18:57Z loose $

"""
RATaskStatusChangedHandler listens to a bus on which tasks handled by the ResourceAssigner get published.
It will then try to propagate the changes to OTDB as Scheduled or Conflict.
"""

import logging
from datetime import datetime
import time

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.resourceassignment.resourceassigner.rabuslistener import RABusListener, RAEventMessageHandler
from lofar.sas.resourceassignment.ratootdbtaskspecificationpropagator.propagator import RAtoOTDBPropagator

logger = logging.getLogger(__name__)

class RATaskStatusChangedHandler(RAEventMessageHandler):
    def __init__(self, propagator=None):
        super().__init__()

        self.propagator = propagator
        if not self.propagator:
            self.propagator =  RAtoOTDBPropagator()

    def onTaskApproved(self, task_ids):
        radb_id = task_ids.get('radb_id')
        otdb_id = task_ids.get('otdb_id')
        mom_id = task_ids.get('mom_id')
        logger.info('onTaskApproved: radb_id=%s otdb_id=%s mom_id=%s', radb_id, otdb_id, mom_id)

        self.propagator.doTaskApproved(otdb_id, mom_id)

    def onTaskScheduled(self, task_ids):
        radb_id = task_ids.get('radb_id')
        otdb_id = task_ids.get('otdb_id')
        mom_id = task_ids.get('mom_id')
        logger.info('onTaskScheduled: radb_id=%s otdb_id=%s mom_id=%s', radb_id, otdb_id, mom_id)

        self.propagator.doTaskScheduled(radb_id, otdb_id, mom_id)

    def onTaskConflict(self, task_ids):
        radb_id = task_ids.get('radb_id')
        otdb_id = task_ids.get('otdb_id') #Does this work if one of the Id's is not set?
        mom_id = task_ids.get('mom_id')
        logger.info('onTaskConflict: radb_id=%s otdb_id=%s mom_id=%s', radb_id, otdb_id, mom_id)

        self.propagator.doTaskConflict(otdb_id)

    def onTaskError(self, task_ids):
        radb_id = task_ids.get('radb_id')
        otdb_id = task_ids.get('otdb_id') #Does this work if one of the Id's is not set?
        mom_id = task_ids.get('mom_id')
        logger.info('onTaskError: radb_id=%s otdb_id=%s mom_id=%s', radb_id, otdb_id, mom_id)

        self.propagator.doTaskError(otdb_id)


__all__ = ["RATaskStatusChangedHandler"]

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    from optparse import OptionParser
    from lofar.common.util import waitForInterrupt

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the RAtoOTDBTaskSpecificationPropagator service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('-e', "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME, help="Name of the bus on which messages are published, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    logging.getLogger('lofar.sas.resourceassignment.database.radbbuslistener').level = logging.WARN
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with RAtoOTDBPropagator(exchange=options.exchange,
                            broker=options.broker) as propagator:
        with RABusListener(handler_type=RATaskStatusChangedHandler,
                           handler_kwargs={'propagator': propagator},
                           exchange=options.exchange, broker=options.broker):
            waitForInterrupt()

if __name__ == '__main__':
    main()
