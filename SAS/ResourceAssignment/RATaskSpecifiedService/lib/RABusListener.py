#!/usr/bin/env python3

# RABusListener.py: RABusListener listens on the lofar ra message bus and calls (empty) on<SomeMessage> methods when such a message is received.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id$

"""
RABusListener listens on the lofar otdb message bus and calls (empty) on<SomeMessage> methods when such a message is received.
Typical usage is to derive your own subclass from RABusListener and implement the specific on<SomeMessage> methods that you are interested in.
"""

from lofar.messaging import BusListener, AbstractMessageHandler, LofarMessage
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.rataskspecified.config import DEFAULT_RA_TASK_SPECIFIED_NOTIFICATION_SUBJECT

import logging

logger = logging.getLogger(__name__)


class RATaskSpecifiedEventMessageHandler(AbstractMessageHandler):
    def __init__(self):
        """
        RATaskSpecifiedEventMessageHandler listens on the lofar ra message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from RATaskSpecifiedEventMessageHandler and implement the specific on<SomeMessage> methods that you are interested in.
        """
        super().__init__()

    def handle_message(self, msg: LofarMessage):
        logger.debug("RABusListener.handle_message: %s" %str(msg))

        otdb_id = msg.content['otdb_id']
        specification_tree = msg.content

        self.onTaskSpecified(otdb_id, specification_tree)

    def onTaskSpecified(self, otdb_id, specification_tree):
        pass


class RATaskSpecifiedBusListener(BusListener):
    def __init__(self, handler_type: RATaskSpecifiedEventMessageHandler.__class__ = RATaskSpecifiedEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME,
                 routing_key: str = "%s.#" % DEFAULT_RA_TASK_SPECIFIED_NOTIFICATION_SUBJECT,
                 broker: str = DEFAULT_BROKER,
                 num_threads: int = 1,):
        super().__init__(handler_type=handler_type, handler_kwargs=handler_kwargs,
                         exchange=exchange, routing_key=routing_key,
                         num_threads=num_threads, broker=broker)

__all__ = ["RATaskSpecifiedBusListener", "RATaskSpecifiedEventMessageHandler"]
