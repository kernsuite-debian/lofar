#!/usr/bin/env python3
# Copyright (C) 2012-2013  ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
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

try:
  import proton
  import proton.utils
  MESSAGING_ENABLED = True
except ImportError:
  from . import noqpidfallback as proton
  MESSAGING_ENABLED = False

import os
import logging
import lofar.messagebus.message as message
from lofar.messagebus.environment import isProductionEnvironment, isTestEnvironment
import atexit

# Candidate for a config file
broker="127.0.0.1" 
options="create:never"

# which brokers to use to avoid routing
if isProductionEnvironment():
  broker_feedback="mcu001.control.lofar"
  broker_state="ccu001.control.lofar"
elif isTestEnvironment():
  broker_feedback="mcu199.control.lofar"
  broker_state="ccu199.control.lofar"
else:
  broker_feedback="localhost"
  broker_state="localhost"

logger=logging.getLogger("MessageBus")

# which brokers to use to avoid routing
if isProductionEnvironment():
  broker_feedback="mcu001.control.lofar"
  broker_state="ccu001.control.lofar"
elif isTestEnvironment():
  broker_feedback="mcu199.control.lofar"
  broker_state="ccu199.control.lofar"
else:
  broker_feedback="localhost"
  broker_state="localhost"

#TODO: replace this version of the messagebus by the version in LCS/Messaging/python/messaging
logger.warning("This version of the messagebus (lofar.messagebus.messagebus) is deprecated and will be replaced by lofar.messaging.messagebus")

# Set to True if the caller parses LOFARENV -- required for surface between MessageBus and Messaging libs
IGNORE_LOFARENV=False

class BusException(Exception):
    pass

class Session:
    def __init__(self, broker):
        self.closed = False

        logger.info("[Bus] Connecting to broker %s", broker)
        try:
            self.connection = proton.utils.BlockingConnection(broker)
            self.connection.reconnect = True
            logger.info("[Bus] Connected to broker %s", broker)
            #self.session = self.connection.session()
        except proton.ProtonException as m:
            raise BusException(m)

        # NOTE: We cannot use:
        #  __del__: its broken (does not always get called, destruction order is unpredictable)
        #  with:    not supported in python 2.4, does not work well on arrays of objects
        #  weakref: dpes not guarantee to be called (depends on gc)
        #
        # Note that this atexit call will prevent self from being destructed until the end of the program,
        # since a reference will be retained
        atexit.register(self.close)

    def close(self):
        if self.closed:
            return

        self.closed = True

        # NOTE: session.close() freezes under certain error conditions,
        # f.e. opening a receiver on a non-existing queue.
        # This seems to happen whenever a Python exception was thrown
        # by the qpid wrapper.
        #
        # This especially happens if we would put this code in __del__.
        # Note that we cannot use __enter__ and __exit__ either due to
        # ccu001/ccu099 still carrying python 2.4.
        #
        # See https://issues.apache.org/jira/browse/QPID-6402
        #
        # We set a timeout to prevent freezing, which obviously leads
        # to data loss if the stall was legit.
        try:
            self.connection.close()
        except proton.Timeout as t:
            logger.error("[Bus] Could not close connection: %s", t)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def address(self, queue, options):
        return "%s%s" % (self._queue_prefix(), queue) # + ' ; {%s}' % options

    def _queue_prefix(self):
        lofarenv = os.environ.get("LOFARENV", "")
        queueprefix = os.environ.get("QUEUE_PREFIX", "")

        if lofarenv == "PRODUCTION" or IGNORE_LOFARENV:
            pass
        elif lofarenv == "TEST":
            queueprefix += "test."
        else:
            queueprefix += "devel."

        return queueprefix

class ToBus(Session):
    def __init__(self, queue, options=options, broker=broker):
        Session.__init__(self, broker)
        self.queue = queue

        try:
            self.sender = self.connection.create_sender(self.address(queue, options))
        except proton.ProtonException as m:
            raise BusException(m)

    def send(self, msg):
        try:
            logger.info("[ToBus] Sending message to queue %s", self.queue)

            try:
              # Send Message or MessageContent object
              self.sender.send(msg.qpidMsg())
            except AttributeError:
              # Send string or messaging.Message object
              self.sender.send(msg)

            logger.info("[ToBus] Message sent to queue %s", self.queue)
        except proton.SessionError as m:
            raise BusException(m)

class FromBus(Session):
    def __init__(self, queue, options=options, broker=broker):
        Session.__init__(self, broker)

        self.add_queue(queue, options)

    def add_queue(self, queue, options=options):
        try:
            self.receiver = self.connection.create_receiver(self.address(queue, options))
        except proton.ProtonException as m:
            raise BusException(m)

        # Need capacity >=1 for 'self.session.next_receiver' to function across multiple queues
        self.receiver.capacity = 1

    def get(self, timeout=None):
        msg = None

        logger.debug("[FromBus] Waiting for message")
        try:
            msg = self.receiver.receive(timeout)
            if msg is None:
                logger.error("[FromBus] Could not retrieve available message on queue %s", self.receiver.source)
            else:
                logger.info("[FromBus] Message received on queue %s", self.receiver.source)
        except proton.Timeout as e:
            return None

        if msg is None:
          return None
        else:
          return message.Message(qpidMsg=msg)

    def ack(self, msg):
        self.receiver.accept()
        logging.info("[FromBus] Message ACK'ed")

