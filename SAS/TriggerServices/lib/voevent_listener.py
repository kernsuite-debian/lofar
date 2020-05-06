#!/usr/bin/env python3

# trigger_handler.py
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

"""
This module contains functionality to register at a VO event broker and implement handlers to act on arriving events.
"""

import logging
import argparse
import gcn.notice_types
import time
import threading

logger = logging.getLogger(__name__)


def listen_for_voevents(handler_function, broker_host, broker_port, filter_for=None):
    """
    Connect to vo event broker and call the provided handler function on each new event.
    An optional filter can be applied to only accept certain event types.

    Note: Consider to implement VOEventListenerInterface instead!

    :param handler_function: a callback function that handles the voevents when received. Should accept args (xml_string, lxml_etree_root).
    :param broker_host: Host of the VO event broker
    :param broker_port: Port of the VO event broker
    :param filter_for: a list of integer values that define the Packet_Type of the VO events to accept
    """
    # Log filters with name:
    if filter_for is not None:
        for i in filter_for:
            try:
                eventtype = gcn.notice_types.NoticeType(i).name
            except:
                eventtype = 'unknown'
            logger.info('Will listen for Packet_Type %s (%s)' % (i, eventtype))

        # Apply filters on handler
        if filter_for:
            handler = gcn.include_notice_types(*filter_for)(handler_function)
    else:
        logger.info('Will listen for all Packet_Types')

    logger.info("Now starting to listen on %s:%s, passing events to %s" % (broker_host, broker_port, handler_function))
    gcn.listen(host=broker_host, port=broker_port, handler=handler_function)


class VOEventListenerInterface(object):
    """
    An interface that should be implemented to listen to particular events and handle them.
    See _SimpleVOEventListener for an example implementation.
    """
    def __init__(self, broker_host='127.0.0.1', broker_port=8099, filter_for=None):
        """
        :param broker_host: Host of the VO event broker
        :param broker_port: Port of the VO event broker
        :param filter_for: a list of integer values that define the Packet_Type of the VO events to accept
        """
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._filter_for = filter_for

    def handle_event(self, xml_string, lxml_etree_root):
        """
        This is called when the listener receives a new message.

        Note: Implement this in handler classes that deal with !

        :param xml_string: voevent as xml string
        :param lxml_etree_root: lxml etree root node of the parsed voevent
        """
        raise NotImplementedError("Override this function with your custom behavior to react to this event!")

    def __enter__(self):
        '''entering 'with' context, starts listening'''
        self.start_listening(blocking=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''exiting 'with' context, stops listening'''
        self.stop_listening()

    def start_listening(self, blocking=False):
        logger.info('start listening for VOEvents on %s:%s with filter: %s', self._broker_host, self._broker_port, self._filter_for)
        args = (self.handle_event, self._broker_host, self._broker_port, self._filter_for)
        if blocking:
            listen_for_voevents(*args)
        else:
            t = threading.Thread(target=listen_for_voevents, args=args)
            t.daemon = True
            t.start()

    def stop_listening(self):
        '''should stop listening, but we can't due to gcn's blocking listen_for_voevents method...'''
        logger.warning('Cannot stop listening for VOEvents on %s:%s because the gcn package only offers a blocking listener...',
                       self._broker_host, self._broker_port)

class _SimpleVOEventListener(VOEventListenerInterface):
    """
    A simple stand-alone vo-event handler
    Note: This is here for manual testing and demonstration purposes.
          You should usually write your own listener class by extending VOEventListenerInterface.
    """

    def __init__(self, write_to_file=False, file_path=None, *args, **kwargs):
        super(_SimpleVOEventListener, self).__init__(*args, **kwargs)
        self.write_to_file = write_to_file
        self.filename = file_path

    def handle_event(self, payload, root):
        logger.info('Handling new event...')
        try:
            logger.info('%s' % payload)
            if self.write_to_file:
                if self.filename is None:
                    self.filename = '%s_%f.xml' % ('event', time.time())
                logger.info('...writing to: %s' % self.filename)
                with open(self.filename, 'w') as f:
                    f.write(payload.decode('utf-8'))

        except Exception as ex:
            logger.exception("An error occurred while handling event: %s" % ex)

        logger.info('...done handling event.')


def main():
    # Check the invocation arguments
    parser = argparse.ArgumentParser("This script will listen to voevents and optionally write them to a file.")
    parser.add_argument('-b', '--broker-host', dest='host', help="Host of the VO event broker", required=False, default='localhost')
    parser.add_argument('-p', '--broker-port', dest='port', help="Port of the VO event broker", required=False, default=8099)
    parser.add_argument('-d', '--dump-file', dest='write_to_file', help="Write received VO events to files", action='store_true')
    parser.add_argument('-f', '--filter-for', dest='filter_for', help="Comma-separated list of Packet_Type values you want to receive", nargs='+', type=int)

    args = parser.parse_args()

    # register simple listener
    listener = _SimpleVOEventListener(broker_host=args.host,
                                      broker_port=args.port,
                                      filter_for=args.filter_for,
                                      write_to_file=args.write_to_file)

    # start listening
    listener.start_listening()

if __name__ == '__main__':
    logformat = "%(asctime)s %(levelname)8s %(funcName)25s:%(lineno)-5d | %(threadName)10s | %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO)
    main()
