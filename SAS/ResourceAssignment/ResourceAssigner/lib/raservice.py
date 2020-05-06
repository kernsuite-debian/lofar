#!/usr/bin/env python3

# ResourceAssigner.py: ResourceAssigner listens on the lofar ?? bus and calls onTaskSpecified
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
# $Id: raservice.py 1580 2015-09-30 14:18:57Z loose $

"""
TaskSpecifiedListener listens to a bus on which specified tasks get published. It will then try
to assign resources to these tasks.
"""

import logging

from lofar.common import dbcredentials
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.rataskspecified.RABusListener import RATaskSpecifiedEventMessageHandler, RATaskSpecifiedBusListener
from lofar.sas.resourceassignment.resourceassigner.resource_assigner import ResourceAssigner
from lofar.sas.resourceassignment.resourceassigner.schedulechecker import ScheduleChecker

logger = logging.getLogger(__name__)


class SpecifiedTaskEventMessageHandler(RATaskSpecifiedEventMessageHandler):
    def __init__(self, assigner=None):
        """
        SpecifiedTaskEventMessageHandler listens on the lofar ?? bus and calls onTaskSpecified
        """
        super().__init__()

        self.assigner = assigner
        if not self.assigner:
            self.assigner = ResourceAssigner()

    def onTaskSpecified(self, otdb_id, specification_tree):
        logger.info('onTaskSpecified: otdb_id=%s status=%s', otdb_id, specification_tree.get('status', '').lower())

        try:
            self.assigner.do_assignment(otdb_id, specification_tree)
        except Exception as e:
            logger.error(str(e))

__all__ = ["SpecifiedTaskEventMessageHandler"]


def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    from optparse import OptionParser
    from lofar.common.util import waitForInterrupt

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the resourceassigner service')
    parser.add_option('-b', '--broker', dest='broker', type='string',
                      default=DEFAULT_BROKER,
                      help='Address of the broker, default: localhost')
    parser.add_option('-e', "--exchange", dest="exchange", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Name of the bus on which communication occurs [default: %default]")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')

    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")

    (options, args) = parser.parse_args()

    radb_dbcreds = dbcredentials.parse_options(options)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with ResourceAssigner(exchange=options.exchange,
                          broker=options.broker,
                          radb_dbcreds=radb_dbcreds) as assigner:
        with RATaskSpecifiedBusListener(handler_type=SpecifiedTaskEventMessageHandler,
                                        handler_kwargs={"assigner": assigner},
                                        exchange=options.exchange,
                                        broker=options.broker):
            with ScheduleChecker(exchange=options.exchange,
                                 broker=options.broker):
                waitForInterrupt()

if __name__ == '__main__':
    main()
