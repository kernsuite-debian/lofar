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


from lofar.common.util import humanreadablesize
from lofar.messaging.messagebus import BusListener, AbstractMessageHandler, BusListenerJanitor
from lofar.lta.ingest.common.config import INGEST_NOTIFICATION_PREFIX
from lofar.messaging.messagebus import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.messaging.messages import EventMessage
from lofar.common.util import waitForInterrupt
from typing import Iterable

import time
import sys

import logging
logger = logging.getLogger()


class IngestEventMessageHandler(AbstractMessageHandler):
    def __init__(self, log_subject_filters: Iterable = None):
        """
        :param log_subject_filters: list/set of subjects (like 'JobStarted', 'TaskFinished', etc) to specify which messages you would like to be logged, or all if None given.
        """
        super().__init__()
        self._log_subject_filters = set(log_subject_filters) if log_subject_filters else set()

    def handle_message(self, msg: EventMessage):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % INGEST_NOTIFICATION_PREFIX, '')

        self._log_job_notification(stripped_subject, msg.content)

        # map msg subject onto callback method
        if stripped_subject == 'JobStarted':
            self.onJobStarted(msg.content)
        elif stripped_subject == 'JobFinished':
            self.onJobFinished(msg.content)
        elif stripped_subject == 'JobFailed':
            self.onJobFailed(msg.content)
        elif stripped_subject == 'JobProgress':
            self.onJobProgress(msg.content)
        elif stripped_subject == 'JobRemoved':
            self.onJobRemoved(msg.content)
        elif stripped_subject == 'JobTransferFailed':
            self.onJobTransferFailed(msg.content)
        elif stripped_subject == 'TaskProgress':
            self.onTaskProgress(msg.content)
        elif stripped_subject == 'TaskFinished':
            self.onTaskFinished(msg.content)
        elif stripped_subject == 'TransferServiceStatus':
            self.onTransferServiceStatus(msg.content)
        else:
            raise ValueError("IngestEventMessageHandler.handleMessage: unknown subject: %s" %  msg.subject)

    def onJobStarted(self, job_dict):
        '''onJobStarted is called upon receiving a JobStarted message.
        :param job_dict: dictionary with the started job'''
        pass

    def onJobFinished(self, job_dict):
        '''onJobFinished is called upon receiving a JobFinished message.
        :param job_dict: dictionary with the finised job'''
        pass

    def onJobFailed(self, job_dict):
        '''onJobFailed is called upon receiving a JobFailed message.
        :param job_dict: dictionary with the failed job'''
        pass

    def onJobProgress(self, job_dict):
        '''onJobProgress is called upon receiving a JobProgress message.
        :param job_dict: dictionary with the progressing job'''
        pass

    def onJobRemoved(self, job_dict):
        '''onJobRemoved is called upon receiving a JobRemoved message.
        :param job_dict: dictionary with the removed job'''
        pass

    def onJobTransferFailed(self, job_dict):
        '''onJobTransferFailed is called upon receiving a JobTransferFailedmessage.
        :param job_dict: dictionary with the failed job'''
        pass

    def onTaskProgress(self, task_dict):
        '''onTaskProgress is called upon receiving a TaskProgress message. (progress of all dataproducts of a observation/pipeline)
        :param task_dict: dictionary with the progressing task'''
        pass

    def onTaskFinished(self, task_dict):
        '''onTaskFinished is called upon receiving a TaskFinished message. (when all dataproducts of a observation/pipeline were ingested)
        :param task_dict: dictionary with the finished task'''
        pass

    def onTransferServiceStatus(self, status_dict):
        '''onTransferServiceStatus is called upon receiving a TransferServiceStatus message. (when the ingesttransferservice reports it's status at regular intervals)
        :param status_dict: dictionary with the status'''
        pass

    def _log_job_notification(self, subject: str, job_dict: dict):
        if self._log_subject_filters and subject not in self._log_subject_filters:
            return

        try:
            if subject in ['JobProgress', 'TransferServiceStatus', 'TaskProgress', 'TaskFinished']:
                msg = "ingest %s " % subject
            else:
                msg = 'ingest job status changed to %s. ' % (subject,)

            msg += 'project: %s export_id: %s type: %s server: %s' % (job_dict.get('project'),
                                                                      job_dict.get('export_id'),
                                                                      job_dict.get('type'),
                                                                      job_dict.get('ingest_server'))
            if job_dict.get('archive_id'):
                msg += ' archive_id: %s' % job_dict.get('archive_id')

            if job_dict.get('dataproduct'):
                msg += ' dp: %s' % job_dict.get('dataproduct')

            if job_dict.get('lta_site'):
                msg += ' lta_site: %s' % job_dict.get('lta_site')

            if job_dict.get('otdb_id'):
                msg += ' otdb_id: %s' % job_dict.get('otdb_id')

            if job_dict.get('percentage_done') != None:
                msg += ' progress: %s%%' % (round(10.0 * float(job_dict.get('percentage_done'))) / 10.0)

            if job_dict.get('total_bytes_transfered') != None:
                msg += ' transferred: %s' % humanreadablesize(job_dict.get('total_bytes_transfered'))

            if job_dict.get('average_speed') != None:
                msg += ' avg speed: %s' % humanreadablesize(job_dict.get('average_speed'), 'Bps')

            if job_dict.get('srm_url'):
                msg += ' srm_url: %s' % job_dict.get('srm_url')

            if job_dict.get('message'):
                msg += ' message: %s' % job_dict.get('message')

            logger.log(logging.WARNING if 'Failed' in subject else logging.INFO, msg)
        except Exception as e:
            logger.error(e)


class IngestEventMesssageBusListener(BusListener):
    def __init__(self,
                 handler_type: IngestEventMessageHandler.__class__ = IngestEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER,
                 num_threads: int=1):
        """
        IngestBusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from IngestBusListener and implement the specific on<SomeMessage> methods that you are interested in.
        :param busname: valid Qpid address
        :param broker: valid Qpid broker host
        """
        if not issubclass(handler_type, IngestEventMessageHandler):
            raise TypeError("handler_type should be a IngestEventMessageHandler subclass")

        super(IngestEventMesssageBusListener, self).__init__(handler_type=handler_type,
                                                             handler_kwargs=handler_kwargs,
                                                             exchange=exchange, routing_key="%s.#" % INGEST_NOTIFICATION_PREFIX,
                                                             broker=broker,
                                                             num_threads=num_threads)

def main():
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run the ingest job monitor')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the message broker, default: %default')
    parser.add_option('-e', '--exchange', dest='exchange', type='string', default=DEFAULT_BUSNAME, help='Name of the exchange on which the ingest notifications are published, default: %default')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)

    event_listener = IngestEventMesssageBusListener(exchange=options.exchange, broker=options.broker)

    # wrap event_listener in a janitor to auto cleanup the designed listening queue upon exit.
    # this tool is only meant for live listening, not for historic logs.
    with BusListenerJanitor(event_listener):
        waitForInterrupt()

if __name__ == '__main__':
    main()
