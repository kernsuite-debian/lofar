#!/usr/bin/env python3
#
# Copyright (C) 2016
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
import os
import logging
from optparse import OptionParser

# WARNING: This code only works with Fabric Version 2
from fabric import Connection

from lofar.messaging import RPCService
from lofar.common.util import waitForInterrupt
from lofar.messaging import ServiceMessageHandler
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
import lofar.mac.config as config

logger = logging.getLogger(__name__)


class ObservationControlHandler(ServiceMessageHandler):
    def __init__(self):
        super(ObservationControlHandler, self).__init__()
        self.register_service_method("AbortObservation", self.abort_observation)

        host = "localhost"

        if "LOFARENV" in os.environ:
            lofar_environment = os.environ['LOFARENV']

            if lofar_environment == "PRODUCTION":
                host = config.PRODUCTION_OBSERVATION_CONTROL_HOST
            elif lofar_environment == "TEST":
                host = config.TEST_OBSERVATION_CONTROL_HOST

        self.connection = Connection(host)

    def _abort_observation_task(self, sas_id):
        logger.info("trying to abort ObservationControl for SAS ID: %s", sas_id)

        killed = False

        pid_line = self.connection.run('/usr/sbin/pidof ObservationControl').stdout.strip('\n')
        pids = pid_line.split(' ')

        for pid in pids:
            logger.info("Running: ps -p %s --no-heading -o command | awk -F[{}] '{ printf $2; }'", pid)
            pid_sas_id = self.connection.run(
                "ps -p %s --no-heading -o command | awk -F[{}] '{ printf $2; }'" % pid).stdout
            if str(pid_sas_id) == str(sas_id):
                logger.info("Killing ObservationControl with PID: %s for SAS ID: %s",
                            pid, sas_id)
                self.connection.run('kill -SIGINT %s' % pid)
                killed = True

        return killed

    def abort_observation(self, sas_id):
        """ aborts an observation for a single sas_id """
        aborted = self._abort_observation_task(sas_id)

        return {'aborted': aborted}


def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the observationcontrol service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the qpid broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string",
                      default=DEFAULT_BUSNAME,
                      help="Name of the exchange on the qpid broker, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true',
                      help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with RPCService(service_name=config.DEFAULT_OBSERVATION_CONTROL_SERVICE_NAME,
                    handler_type=ObservationControlHandler,
                    broker=options.broker,
                    exchange=options.exchange):
        waitForInterrupt()


if __name__ == '__main__':
    main()
