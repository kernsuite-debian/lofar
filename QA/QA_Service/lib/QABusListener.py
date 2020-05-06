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
QABusListener listens on the lofar qa message bus and calls (empty) on<SomeMessage> methods when such a message is received.
Typical usage is to derive your own subclass from QABusListener and implement the specific on<SomeMessage> methods that you are interested in.
"""

from lofar.messaging.messagebus import BusListener, AbstractMessageHandler, LofarMessage, EventMessage
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.qa.service.config import DEFAULT_QA_NOTIFICATION_SUBJECT_PREFIX
from lofar.common.util import single_line_with_single_spaces

import logging

logger = logging.getLogger(__name__)


class QAEventMessageHandler(AbstractMessageHandler):
    def __init__(self):
        """
        QABusListener listens on the lofar qa message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from QABusListener and implement the specific on<SomeMessage> methods that you are interested in.
        """
        super().__init__()

    def handle_message(self, msg: LofarMessage):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % DEFAULT_QA_NOTIFICATION_SUBJECT_PREFIX, '')

        logger.info("QAEventMessageHandler.handleMessage on%s: %s" % (stripped_subject, str(msg.content).replace('\n', ' ')))

        if stripped_subject == 'ConvertedMS2Hdf5':
            self.onConvertedMS2Hdf5(msg.content)
        elif stripped_subject == 'ConvertedBF2Hdf5':
            self.onConvertedBF2Hdf5(msg.content)
        elif stripped_subject == 'CreatedInspectionPlots':
            self.onCreatedInspectionPlots(msg.content)
        elif stripped_subject == 'Clustered':
            self.onClustered(msg.content)
        elif stripped_subject == 'Finished':
            self.onFinished(msg.content)
        elif stripped_subject == 'Error':
            self.onError(msg.content)
        else:
            raise ValueError("QAEventMessageHandler.handleMessage: unknown subject: %s" %  msg.subject)

    def onConvertedMS2Hdf5(self, msg_content):
        logger.info("%s.onConvertedMS2Hdf5(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

    def onConvertedBF2Hdf5(self, msg_content):
        logger.info("%s.onConvertedBF2Hdf5(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

    def onClustered(self, msg_content):
        logger.info("%s.onClustered(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

    def onCreatedInspectionPlots(self, msg_content):
        logger.info("%s.onCreatedInspectionPlots(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

    def onFinished(self, msg_content):
        logger.info("%s.onFinished(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

    def onError(self, msg_content):
        logger.info("%s.onError(%s)", self.__class__.__name__, single_line_with_single_spaces(msg_content))

class QABusListener(BusListener):
    def __init__(self,
                 handler_type: QAEventMessageHandler.__class__ = QAEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME,
                 routing_key: str = DEFAULT_QA_NOTIFICATION_SUBJECT_PREFIX+".#",
                 num_threads: int = 1,
                 broker: str = DEFAULT_BROKER):
        """
        QABusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from QABusListener and implement the specific on<SomeMessage> methods that you are interested in.
        """
        if not issubclass(handler_type, QAEventMessageHandler):
            raise TypeError("handler_type should be a QAEventMessageHandler subclass")

        super().__init__(handler_type, handler_kwargs, exchange, routing_key, num_threads, broker)


__all__ = ["QABusListener", "QAEventMessageHandler"]
