#!/usr/bin/env python3

# RADBBusListener.py
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
# $Id: RADBBusListener.py 1580 2015-09-30 14:18:57Z loose $

"""
RADBBusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
Typical usage is to derive your own subclass from RADBBusListener and implement the specific on<SomeMessage> methods that you are interested in.
"""

from lofar.messaging import BusListener, AbstractMessageHandler, DEFAULT_BROKER, DEFAULT_BUSNAME, EventMessage
from lofar.sas.resourceassignment.database.config import DEFAULT_RADB_NOTIFICATION_PREFIX
from lofar.common.util import waitForInterrupt

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RADBEventMessageHandler(AbstractMessageHandler):
    def handle_message(self, msg: EventMessage):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % DEFAULT_RADB_NOTIFICATION_PREFIX, '')

        if stripped_subject == 'TaskUpdated':
            self.onTaskUpdated(msg.content)
        elif stripped_subject == 'TaskInserted':
            self.onTaskInserted(msg.content)
        elif stripped_subject == 'TaskDeleted':
            self.onTaskDeleted(msg.content)
        elif stripped_subject == 'ResourceClaimUpdated':
            self.onResourceClaimUpdated(msg.content)
        elif stripped_subject == 'ResourceClaimInserted':
            self.onResourceClaimInserted(msg.content)
        elif stripped_subject == 'ResourceClaimDeleted':
            self.onResourceClaimDeleted(msg.content)
        elif stripped_subject == 'ResourceAvailabilityUpdated':
            self.onResourceAvailabilityUpdated(msg.content)
        elif stripped_subject == 'ResourceCapacityUpdated':
            self.onResourceCapacityUpdated(msg.content)
        else:
            raise ValueError("RADBBusListener.handleMessage: unknown subject: %s" %  msg.subject)

    def onTaskUpdated(self, updated_task):
        '''onTaskUpdated is called upon receiving a TaskUpdated message.
        :param updated_task: dictionary with the updated task'''
        pass

    def onTaskInserted(self, new_task):
        '''onTaskInserted is called upon receiving a TaskInserted message.
        :param new_task: dictionary with the inserted task'''
        pass

    def onTaskDeleted(self, old_task_id):
        '''onTaskDeleted is called upon receiving a TaskDeleted message.
        :param old_task_id: id of the deleted task'''
        pass

    def onResourceClaimUpdated(self, updated_claim):
        '''onResourceClaimUpdated is called upon receiving a ResourceClaimUpdated message.
        :param updated_claim: dictionary with the updated claim'''
        pass

    def onResourceClaimInserted(self, new_claim):
        '''onResourceClaimInserted is called upon receiving a ResourceClaimInserted message.
        :param new_claim: dictionary with the inserted claim'''
        pass

    def onResourceClaimDeleted(self, old_claim_id):
        '''onResourceClaimDeleted is called upon receiving a ResourceClaimDeleted message.
        :param old_claim_id: id of the deleted claim'''
        pass

    def onResourceAvailabilityUpdated(self, updated_availability):
        '''onResourceAvailabilityUpdated is called upon receiving a ResourceAvailabilityUpdated message.
        :param updated_availability: dictionary with the updated availability'''
        pass

    def onResourceCapacityUpdated(self, updated_capacity):
        '''onResourceCapacityUpdated is called upon receiving a ResourceCapacityUpdated message.
        :param updated_capacity: dictionary with the updated capacity'''
        pass

class RADBEventMessageBusListener(BusListener):
    def __init__(self,
                 handler_type: RADBEventMessageHandler.__class__ = RADBEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER,
                 num_threads: int=1):
        """
        RADBEventMessageBusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        """
        if not issubclass(handler_type, RADBEventMessageHandler):
            raise TypeError("handler_type should be a RADBEventMessageHandler subclass")

        super().__init__(handler_type=handler_type, handler_kwargs=handler_kwargs,
                         exchange=exchange, routing_key="%s.#" % DEFAULT_RADB_NOTIFICATION_PREFIX,
                         broker=broker, num_threads=num_threads)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    from lofar.messaging import BusListenerJanitor
    with BusListenerJanitor(RADBEventMessageBusListener()):
        waitForInterrupt()

__all__ = ["RADBEventMessageBusListener", "RADBEventMessageHandler"]
