#!/usr/bin/env python3

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

from lofar.messaging.messagebus import AbstractMessageHandler, BusListener, LofarMessage, EventMessage
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.mac.tbbservice.config import DEFAULT_TBB_NOTIFICATION_PREFIX
from lofar.common.util import single_line_with_single_spaces

import logging
logger = logging.getLogger()


class TBBEventMessageHandler(AbstractMessageHandler):
    def __init__(self):
        super().__init__()

    def handle_message(self, msg: LofarMessage):
        # try to handle an incoming message, and call the associated on<SomeMessage> method
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % DEFAULT_TBB_NOTIFICATION_PREFIX, '')

        logger.debug("TBBEventMessageHandler.handle_message: on%s content=%s", stripped_subject, single_line_with_single_spaces(str(msg.content)))

        if stripped_subject == 'DataWritersStarting':
            self.onDataWritersStarting(msg.content)
        elif stripped_subject == 'DataWritersStarted':
            self.onDataWritersStarted(msg.content)
        elif stripped_subject == 'DataWritersFinished':
            self.onDataWritersFinished(msg.content)
        elif stripped_subject == 'DataWritersStopping':
            self.onDataWritersStopping(msg.content)
        elif stripped_subject == 'DataWritersStopped':
            self.onDataWritersStopped(msg.content)
        else:
            raise ValueError("TBBEventMessageHandler.handleMessage: unknown subject: %s" % msg.subject)

    def onDataWritersStarting(self, msg_content):
        '''onDataWritersStarting is called upon receiving a DataWritersStarting message.
        :param msg_content: '''
        pass

    def onDataWritersStarted(self, msg_content):
        '''onDataWritersStarted is called upon receiving a DataWritersStarted message.
        :param msg_content: dictionary with the info on which datawrited started on which host/port'''
        pass

    def onDataWritersFinished(self, msg_content):
        '''onDataWritersFinished is called upon receiving a DataWritersFinished message.
        :param msg_content: dictionary with the info on which datawrited started on which host/port'''
        pass

    def onDataWritersStopping(self, msg_content):
        '''onDataWritersStopping is called upon receiving a DataWritersStopping message.
        :param msg_content: '''
        pass

    def onDataWritersStopped(self, msg_content):
        '''onDataWritersStopped is called upon receiving a DataWritersStopped message.
        :param msg_content: dictionary with the info on which datawrited Stopped on which host/port'''
        pass


class TBBBusListener(BusListener):
    """The TBBBusListener is a normal BusListener listening specifically to EventMessages with TBB notification subjects.
    It uses by default the TBBEventMessageHandler to handle the EventMessages.
    """
    def __init__(self, handler_type: TBBEventMessageHandler.__class__ = TBBEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, num_threads: int = 1):
        if not issubclass(handler_type, TBBEventMessageHandler):
            raise TypeError("handler_type should be a TBBBusMessagehandler subclass")

        super(TBBBusListener, self).__init__(handler_type=handler_type,
                                             handler_kwargs=handler_kwargs,
                                             exchange=exchange,
                                             routing_key="%s.#" % (DEFAULT_TBB_NOTIFICATION_PREFIX),
                                             num_threads=num_threads, broker=broker)


def main():
    from lofar.common.util import waitForInterrupt
    from optparse import OptionParser
    import os, sys

    # make sure we run in UTC timezone
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run the ingest job monitor')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option("-n", "--busname", dest="busname", type="string",
                      default=DEFAULT_BUSNAME,
                      help='Name of the notification exchange where to listen for the published tbb notifications, default: %default')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)

    with TBBBusListener(exchange=options.busname,
                        broker=options.broker):
        waitForInterrupt()

if __name__ == '__main__':
    main()
