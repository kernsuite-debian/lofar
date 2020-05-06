#!/usr/bin/env python3

# RABusListener.py
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
# $Id: RABusListener.py 1580 2015-09-30 14:18:57Z loose $

"""
RABusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
Typical usage is to derive your own subclass from RABusListener and implement the specific on<SomeMessage> methods that you are interested in.
"""

from lofar.messaging.messagebus import BusListener, AbstractMessageHandler
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, LofarMessage, EventMessage
from lofar.sas.resourceassignment.resourceassigner.config import DEFAULT_RA_NOTIFICATION_PREFIX
from lofar.common.util import waitForInterrupt

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RAEventMessageHandler(AbstractMessageHandler):

    def handle_message(self, msg: EventMessage):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % DEFAULT_RA_NOTIFICATION_PREFIX, '')

        logger.info("on%s: %s" % (stripped_subject, str(msg.content).replace('\n', ' ')))

        if stripped_subject == 'TaskScheduled':
            self.onTaskScheduled(msg.content)
        elif stripped_subject == 'TaskConflict':
            self.onTaskConflict(msg.content)
        elif stripped_subject == 'TaskApproved':
            self.onTaskApproved(msg.content)
        elif stripped_subject == 'TaskError':
            self.onTaskError(msg.content)
        else:
            raise ValueError("RABusListener.handleMessage: unknown subject: %s" %  msg.subject)

    def onTaskApproved(self, task_ids):
        '''onTaskApproved is called upon receiving a TaskApproved message.
        :param task_ids: a dict containing radb_id, mom_id and otdb_id'''
        pass

    def onTaskScheduled(self, task_ids):
        '''onTaskScheduled is called upon receiving a TaskScheduled message.
        :param task_ids: a dict containing radb_id, mom_id and otdb_id'''
        pass

    def onTaskConflict(self, task_ids):
        '''onTaskConflict is called upon receiving a TaskConflict message.
        :param task_ids: a dict containing radb_id, mom_id and otdb_id'''
        pass

    def onTaskError(self, task_ids):
        '''onTaskError is called upon receiving a TaskError message.
        :param task_ids: a dict containing radb_id, mom_id and otdb_id'''
        pass

class RABusListener(BusListener):
    def __init__(self,
                 handler_type: RAEventMessageHandler.__class__ = RAEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME,
                 routing_key: str = DEFAULT_RA_NOTIFICATION_PREFIX+".#",
                 num_threads: int = 1,
                 broker: str = DEFAULT_BROKER):
        """
        RABusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from RABusListener and implement the specific on<SomeMessage> methods that you are interested in.
        """
        super().__init__(handler_type, handler_kwargs, exchange, routing_key, num_threads, broker)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    with RABusListener():
        waitForInterrupt()

__all__ = ["RABusListener"]
