#!/usr/bin/env python3
# coding: iso-8859-15
#
# Copyright (C) 2015-2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
#
# $Id$
"""
Daemon that listens to specific OTDB status changes, requests the parset of such jobs including
their predecessors, and posts them on the bus.
"""

from lofar.messaging import ToBus, EventMessage, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.otdb.OTDBBusListener import OTDBEventMessageHandler, OTDBBusListener
from lofar.sas.resourceassignment.rataskspecified.config import \
    DEFAULT_RA_TASK_SPECIFIED_NOTIFICATION_SUBJECT
from lofar.sas.resourceassignment.common.specification import Specification
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

import logging
logger = logging.getLogger(__name__)


class RATaskSpecifiedOTDBEventMessageHandler(OTDBEventMessageHandler):
    def __init__(self, exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        """
        :param exchange: name of the exchange to listen on.
        :param broker: name of the broker to connect to.
        """
        super().__init__()
        self.otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker)
        self.radbrpc = RADBRPC.create(exchange=exchange, broker=broker)
        self.momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)
        self.send_bus = ToBus(exchange=exchange, broker=broker)

    def start_handling(self):
        self.otdbrpc.open()
        self.momrpc.open()
        self.radbrpc.open()
        self.send_bus.open()

    def stop_handling(self):
        self.otdbrpc.close()
        self.momrpc.close()
        self.radbrpc.close()
        self.send_bus.close()

    # This is mainly to trigger the propagation of misc field values through read_from_mom
    # and then sending them to the RA to OTDB Service in the resource assigner.
    # Might need to be a separate service if we take on more mom-otdb-adapter function.
    def onObservationApproved(self, main_id, modification_time):
        self.createAndSendSpecifiedTask(main_id, 'approved')

    def onObservationPrescheduled(self, main_id, modification_time):
        self.createAndSendSpecifiedTask(main_id, 'prescheduled')

    def createAndSendSpecifiedTask(self, main_id, status):
        spec = Specification(self.otdbrpc, self.momrpc, self.radbrpc)
        spec.status = status
        spec.read_from_OTDB_with_predecessors(main_id, "otdb", {})
        spec.read_from_mom()
        spec.update_start_end_times()
        # spec.insert_into_radb() is still done in resource_assigner for now.
        result_tree = spec.as_dict()
        if spec.status == status:
            logger.info("Sending result: %s" % result_tree)
            # Put result on bus
            msg = EventMessage(subject=DEFAULT_RA_TASK_SPECIFIED_NOTIFICATION_SUBJECT,
                               content=result_tree)
            with self.send_bus:
                self.send_bus.send(msg)
            logger.info("Result sent")
        else:
            logger.warning("Problem retrieving task %i" % main_id)


def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    import logging
    from optparse import OptionParser
    from lofar.common.util import waitForInterrupt

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description="run the rataskspecified service")
    parser.add_option("-e", "--exchange", dest="exchange", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Bus or queue to communicate on. [default: %default]")
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the broker, default: localhost')
    (options, args) = parser.parse_args()

    with OTDBBusListener(handler_type=RATaskSpecifiedOTDBEventMessageHandler,
                         exchange=options.exchange,
                         broker=options.broker):
        waitForInterrupt()


if __name__ == "__main__":
    main()
