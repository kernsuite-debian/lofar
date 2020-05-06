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
This module contains functionality to listen to UDP messages that are send by LOFAR stations
when the TBB boards triggers
"""

import logging
import argparse
import time
import datetime
import threading
import tempfile
import subprocess
import socket
from lofar.tbbalertvoeventpublisher.config import *
from lofar.common.util import waitForInterrupt


logger = logging.getLogger(__name__)

class VOEventPublisher(object):
    """
    Listens to particular events and handle them.
    """
    def __init__(self, port, broker_host, broker_port):
        """
        :param port: Port to receive UDP messages
        :param broker_host: Host of the VO event broker
        :param broker_port: Port of the VO event broker
        """
        self._port = port
        self._broker_host = broker_host
        self._broker_port = broker_port

    def __enter__(self):
        '''entering 'with' context, starts listening'''
        self.start_listening(blocking=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''exiting 'with' context, stops listening'''
        self.stop_listening()

    def send_voevent(self, voevent):
        with tempfile.NamedTemporaryFile(mode='wt') as temp:
            temp.write(voevent)
            temp.flush()
            subprocess.check_call("comet-sendvo --host=%s --port=%s < %s" % (self._broker_host, self._broker_port, temp.name), shell=True)

    def generate_voevent(self, payload):
        """
        :param payload: UDP message to convert into vo event
        :return: vo event xml carrying the info
        """
        template =  """<voe:VOEvent xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:voe="http://www.ivoa.net/xml/VOEvent/v2.0" xsi:schemaLocation="http://www.ivoa.net/xml/VOEvent/v2.0 http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd" version="2.0" role="test" ivorn="%(ivorn)s">
<Who>
  <Description>VOEvent for LOFAR TBB Alerts</Description>
  <AuthorIVORN>ivo://nl.astron</AuthorIVORN>
  <Date>2019-08-05T12:00:00</Date>
  <Author>
    <title>LOFAR TBB ALERT</title>
    <contactEmail>veen@astron.nl</contactEmail>
    <contactName>Sander ter Veen</contactName>
    <shortName>LOFAR_TBB_ALERT</shortName>
  </Author>
</Who>
<What>
  <Group name="event parameters">
    <Param name="raw_message" value="%(raw_message)s" />
  </Group>
</What>
<Why importance="0.0">
  <Name>TBB event detected</Name>
</Why>
</voe:VOEvent>"""
        values = {'date': datetime.datetime.utcnow().isoformat(), 'raw_message': payload.decode('utf-8'), 'ivorn': "ivo://nl.astron/LOFAR_TBB_ALERT#%.2f" % time.time()}
        return template % values

    def handle_udp_message(self, payload):
        """
        This is called when the listener receives a new message.

        :param xml_string: voevent as xml string
        :param lxml_etree_root: lxml etree root node of the parsed voevent
        """
        logger.info('Handling new message...')
        try:
            logger.info('%s' % payload)
            voevent = self.generate_voevent(payload)
            logger.info('%s' % voevent)
            self.send_voevent(voevent)

        except Exception as ex:
            logger.exception("An error occurred while handling message: %s" % ex)

        logger.info('...done handling message.')

    def start_listening(self, blocking=False):
        logger.info('start listening for UDP messages on port %s', self._port)
        args = (self.handle_udp_message, self._port)
        if blocking:
            self.listen_for_udp_messages(*args)
        else:
            t = threading.Thread(target=self.listen_for_udp_messages, args=args)
            t.daemon = True
            t.start()

    def stop_listening(self):
        '''should stop listening, but we can't due to gcn's blocking listen_for_voevents method...'''
        self.sock.close()

    def listen_for_udp_messages(self, handler_function, port):
        """
        Open a UDP port and listen for messages. Generate a vo event and send it to a broker on each new event.

        :param handler_function: a callback function that handles the voevents when received. Should accept args (xml_string, lxml_etree_root).
        :param broker_host: Host of the VO event broker
        :param broker_port: Port of the VO event broker
        """
        # Log filters with name:
        logger.info("Now starting to listen on %s, passing events to %s" % (port, handler_function))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', port))
        self.sock = sock
        while True:
            try:
                recv_msg, _ = sock.recvfrom(65565)
                handler_function(recv_msg)
            except socket.timeout:
                continue


def main():
    logger.warning("!!! This is unfinished work!") # todo: finish, if required: Create proper events that are accepted by the comet broker

    # Check the invocation arguments
    parser = argparse.ArgumentParser("This script will listen to TBB trigger messages via UDP, generate a VO event and send that to a specified VOevent broker.")
    parser.add_argument('-l', '--listening-port', dest='lport', help="Port to listen for UDP messages", required=False, default=DEFAULT_LISTENING_PORT)
    parser.add_argument('-b', '--broker-host', dest='host', help="Host of the VO event broker", required=False, default=DEFAULT_TBB_ALERT_BROKER_HOST)
    parser.add_argument('-p', '--broker-port', dest='port', help="Port of the VO event broker", required=False, default=DEFAULT_TBB_ALERT_BROKER_PORT)

    args = parser.parse_args()
    with VOEventPublisher(args.lport,
                          broker_host=args.host,
                          broker_port=args.port):
        waitForInterrupt()

if __name__ == '__main__':
    logformat = "%(asctime)s %(levelname)8s %(funcName)25s:%(lineno)-5d | %(threadName)10s | %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO)
    main()
