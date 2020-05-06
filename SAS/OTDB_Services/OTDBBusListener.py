#!/usr/bin/env python3

# OTDBEventMessageHandler.py: OTDBEventMessageHandler listens on the lofar otdb message bus and calls (empty) on<SomeMessage> methods when such a message is received.
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
# $Id: messagebus.py 1580 2015-09-30 14:18:57Z loose $

"""
OTDBEventMessageHandler listens on the lofar message bus and calls (empty) on<SomeMessage> methods when such a message is received.
Typical usage is to derive your own subclass from OTDBEventMessageHandler and implement the specific on<SomeMessage> methods that you are interested in.

Here's a concrete example.
First implement your own MyOTDBMessageHandler which implements behaviour in onObservationStarted
>>> class MyOTDBMessageHandler(OTDBEventMessageHandler):
...     def onObservationStarted(self, treeId, modificationTime):
...         print("The observation with treeId %s started!" % treeId)
...         # implement some more business logic here if you want to.

# and then use the MyOTDBMessageHandler in the OTDBBusListener.
# See TemporaryExchange documentation why we use that here in the example.
>>> with TemporaryExchange() as tmp_exchange:
...     with OTDBBusListener(MyOTDBMessageHandler, exchange=tmp_exchange.address):
...         # that's it, now the OTDBBusListener is listening,
...         # and calling MyOTDBMessageHandler.onObservationStarted when a EventMessage for the OTDB ObservationStarted event comes in.
...         # for this example, let's create such an event, so we see something happening.
...         with tmp_exchange.create_tobus() as event_sender:
...             event_sender.send(EventMessage(subject=DEFAULT_OTDB_NOTIFICATION_SUBJECT,
...                                            content={'state': 'active', 'treeID': 123}))
...
...             # ... do some work ... simulate this by sleeping a little...
...             # ...in the mean time, BusListener receives and handles the messages (on its own thread)
...             from time import sleep
...             sleep(0.25)
The observation with treeId 123 started!
"""

from lofar.messaging import BusListener, AbstractMessageHandler, EventMessage, TemporaryExchange
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.otdb.config import DEFAULT_OTDB_NOTIFICATION_SUBJECT

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OTDBEventMessageHandler(AbstractMessageHandler):
    """Concrete implementation of an AbstractMessageHandler for handling OTDB EventMessage's,
    mapping the events to onObservation<Event> methods.
    Typical usage is to derive from this OTDBEventMessageHandler class
    and implement one or more onObservation<Event> methods with your desired behaviour code.

    See example at the top of this file.
    """
    def handle_message(self, msg):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        logger.debug("OTDBEventMessageHandler.handleMessage: %s" %str(msg))

        treeId =  msg.content['treeID']
        modificationTime = datetime.utcnow()
        if 'time_of_change' in msg.content:
            try:
                if msg.content['time_of_change'][-7] == '.':
                    modificationTime = datetime.strptime(msg.content['time_of_change'], '%Y-%m-%dT%H:%M:%S.%f')
                else:
                    modificationTime = datetime.strptime(msg.content['time_of_change'], '%Y-%m-%dT%H:%M:%S')
            except:
                pass

        logger.info("%s otdb task status changed: otdb_id=%s status=%s" % (self, treeId, msg.content['state']))

        if msg.content['state'] == 'described':
            self.onObservationDescribed(treeId, modificationTime)
        elif msg.content['state'] == 'prepared':
            self.onObservationPrepared(treeId, modificationTime)
        elif msg.content['state'] == 'approved':
            self.onObservationApproved(treeId, modificationTime)
        elif msg.content['state'] == 'on_hold':
            self.onObservationOnHold(treeId, modificationTime)
        elif msg.content['state'] == 'conflict':
            self.onObservationConflict(treeId, modificationTime)
        elif msg.content['state'] == 'prescheduled':
            self.onObservationPrescheduled(treeId, modificationTime)
        elif msg.content['state'] == 'scheduled':
            self.onObservationScheduled(treeId, modificationTime)
        elif msg.content['state'] == 'queued':
            self.onObservationQueued(treeId, modificationTime)
        elif msg.content['state'] == 'active':
            self.onObservationStarted(treeId, modificationTime)
        elif msg.content['state'] == 'completing':
            self.onObservationCompleting(treeId, modificationTime)
        elif msg.content['state'] == 'finished':
            self.onObservationFinished(treeId, modificationTime)
        elif msg.content['state'] == 'aborted':
            self.onObservationAborted(treeId, modificationTime)
        elif msg.content['state'] == 'obsolete':
            self.onObservationObsolete(treeId, modificationTime)
        elif msg.content['state'] == 'error':
            self.onObservationError(treeId, modificationTime)
        else:
            logger.info("OTDBEventMessageHandler.handleMessage - handled unknown state: %s", msg.content['state'])

        # apart from calling the above methods for known predefined states,
        # also always call plain onObservationStatusChanged
        # so subclasses can act on any status in this generic method.
        self.onObservationStatusChanged(treeId, msg.content['state'], modificationTime)

    def onObservationStatusChanged(self, treeId, new_status, modificationTime):
        """this method is called upon any OTDB status change event. Override it if you want to act on each status change."""
        pass

    def onObservationDescribed(self, treeId, modificationTime):
        """this method is called upon the ObservationDescribed status change event. Override it if you want to act on this status change."""
        pass

    def onObservationPrepared(self, treeId, modificationTime):
        """this method is called upon the ObservationPrepared status change event. Override it if you want to act on this status change."""
        pass

    def onObservationApproved(self, treeId, modificationTime):
        """this method is called upon the ObservationApproved status change event. Override it if you want to act on this status change."""
        pass

    def onObservationOnHold(self, treeId, modificationTime):
        """this method is called upon the ObservationOnHold status change event. Override it if you want to act on this status change."""
        pass

    def onObservationConflict(self, treeId, modificationTime):
        """this method is called upon the ObservationConflict status change event. Override it if you want to act on this status change."""
        pass

    def onObservationPrescheduled(self, treeId, modificationTime):
        """this method is called upon the ObservationPrescheduled status change event. Override it if you want to act on this status change."""
        pass

    def onObservationScheduled(self, treeId, modificationTime):
        """this method is called upon the ObservationScheduled status change event. Override it if you want to act on this status change."""
        pass

    def onObservationQueued(self, treeId, modificationTime):
        """this method is called upon the ObservationQueued status change event. Override it if you want to act on this status change."""
        pass

    def onObservationStarted(self, treeId, modificationTime):
        """this method is called upon the ObservationStarted status change event. Override it if you want to act on this status change."""
        pass

    def onObservationCompleting(self, treeId, modificationTime):
        """this method is called upon the ObservationCompleting status change event. Override it if you want to act on this status change."""
        pass

    def onObservationFinished(self, treeId, modificationTime):
        """this method is called upon the ObservationFinished status change event. Override it if you want to act on this status change."""
        pass

    def onObservationAborted(self, treeId, modificationTime):
        """this method is called upon the ObservationAborted status change event. Override it if you want to act on this status change."""
        pass

    def onObservationObsolete(self, treeId, modificationTime):
        """this method is called upon the ObservationObsolete status change event. Override it if you want to act on this status change."""
        pass

    def onObservationError(self, treeId, modificationTime):
        """this method is called upon the ObservationError status change event. Override it if you want to act on this status change."""
        pass


class OTDBBusListener(BusListener):
    """The OTDBBusListener is a normal BusListener listening specifically to EventMessages with OTDB notification subjects.
    You have to implement your own concrete subclass of the OTDBEventMessageHandler, and inject that in this OTDBBusListener.
    See example at the top of this file.
    """
    def __init__(self, handler_type: OTDBEventMessageHandler.__class__, handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, num_threads: int = 1):
        if not issubclass(handler_type, OTDBEventMessageHandler):
            raise TypeError("handler_type should be a OTDBEventMessageHandler subclass")

        super(OTDBBusListener, self).__init__(handler_type=handler_type, handler_kwargs=handler_kwargs,
                                              exchange=exchange, routing_key="%s.#" % (DEFAULT_OTDB_NOTIFICATION_SUBJECT),
                                              num_threads=num_threads, broker=broker)

__all__ = ["OTDBEventMessageHandler", "OTDBBusListener"]
