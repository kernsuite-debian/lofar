# messagelogger: Simple buslistener logging each and every received message
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
Simple buslistener logging each and every received message
"""

import re
import logging

logger = logging.getLogger(__name__)

from lofar.messaging import LofarMessage, RequestMessage, BusListener, AbstractMessageHandler
from lofar.messaging.config import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import waitForInterrupt


class MessageLoggerHandler(AbstractMessageHandler):
    def __init__(self, remove_content_newlines: bool, max_content_size: int = -1):
        self._remove_content_newlines = remove_content_newlines
        self._max_content_size = max_content_size

    def handle_message(self, msg: LofarMessage):
        content = str(msg.content)

        if self._remove_content_newlines:
            linesep_whitespace = re.compile("\n\s\s")
            while linesep_whitespace.match(content):
                content = linesep_whitespace.sub("\n ")
            content = content.replace("\n", " ")

        if self._max_content_size > 0 and len(content) > self._max_content_size:
            content = content[:self._max_content_size] + "..."

        logger.info("%s subject='%s' %s%s%scontent: %s",
                    msg.__class__.__name__,
                    msg.subject,
                    ("priority=%s " % msg.priority if msg.priority != 4 else ""),  # only show non-default priorities
                    ("reply_to=%s " % msg.reply_to if isinstance(msg, RequestMessage) else ""),
                    (" %s" % msg.ttl) if msg.ttl else "",
                    content)
        return True


class MessageLogger(BusListener):
    def __init__(self, exchange:str=DEFAULT_BUSNAME, routing_key:str="#", broker:str=DEFAULT_BROKER,
                 remove_content_newlines: bool=False, max_content_size: int=-1):
        super(MessageLogger, self).__init__(handler_type=MessageLoggerHandler,
                                            handler_kwargs={'remove_content_newlines': remove_content_newlines,
                                                            'max_content_size': max_content_size},
                                            exchange=exchange,
                                            routing_key=routing_key,
                                            num_threads=1,
                                            broker=broker)

def main():
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]', description='run the messegelogger, which logs each received message')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus (exchange) to receive messages from. [default: %default]")
    parser.add_option("-r", "--routing_key", dest="routing_key", type="string", default="#",
                      help="filter messages on by subject using this routing_key. #=all. [default: %default]")
    parser.add_option("-n", "--no_newlines", dest="no_newlines", action='store_true',
                      help="remove newlines in message content, so we have single line log messages")
    parser.add_option("-m", "--max_content_size", dest="max_content_size", type="int", default=-1,
                      help="delimit the logged content to at most <max_content_size> characters (or all if -1). [default: %default]")
    options, args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    logger.info("**************************")
    logger.info("* starting messagelogger *")
    logger.info("**************************")

    with MessageLogger(exchange=options.exchange, routing_key=options.routing_key, broker=options.broker,
                       remove_content_newlines=bool(options.no_newlines), max_content_size=options.max_content_size):
        waitForInterrupt()

__all__ = ['MessageLogger', 'main']

if __name__ == '__main__':
    main()

