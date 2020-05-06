#!/usr/bin/env python3

# DataManagementBusListener.py
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

from lofar.messaging import AbstractMessageHandler, BusListener, LofarMessage, EventMessage
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.datamanagement.common.config import DEFAULT_DM_NOTIFICATION_PREFIX
from lofar.common.util import waitForInterrupt

import logging

logger = logging.getLogger(__name__)

class DataManagementEventMessageHandler(AbstractMessageHandler):
    def handle_message(self, msg: LofarMessage):
        if not isinstance(msg, EventMessage):
            raise ValueError("%s: Ignoring non-EventMessage: %s" % (self.__class__.__name__, msg))

        stripped_subject = msg.subject.replace("%s." % DEFAULT_DM_NOTIFICATION_PREFIX, '')
        logger.info("on%s: %s" % (stripped_subject, str(msg.content).replace('\n', ' ')))

        if stripped_subject == 'TaskDeleting':
            self.onTaskDeleting(msg.content.get('otdb_id'))
        elif stripped_subject == 'TaskDeleted':
            self.onTaskDeleted(msg.content.get('otdb_id'), msg.content.get('deleted'), msg.content.get('paths'), msg.content.get('message', ''))
        elif stripped_subject == 'TaskDataPinned':
            self.onTaskDataPinned(msg.content.get('otdb_id'), msg.content.get('pinned'))
        elif stripped_subject == 'PathDeleting':
            self.onPathDeleting(msg.content.get('path'))
        elif stripped_subject == 'PathDeleted':
            self.onPathDeleted(msg.content.get('path'), msg.content.get('deleted'), msg.content.get('message', ''))
        elif stripped_subject == 'DiskUsageChanged':
            self.onDiskUsageChanged(msg.content.get('path'), msg.content.get('disk_usage'), msg.content.get('otdb_id'))
        else:
            raise ValueError("DataManagementBusListener.handleMessage: unknown subject: %s" %  msg.subject)

    def onTaskDeleting(self, otdb_id):
        '''onTaskDeleting is called upon receiving a TaskDeleting message.
        :param otdb_id: otdb_id of the about to be deleted task'''
        pass

    def onTaskDeleted(self, otdb_id, deleted, paths, message=''):
        '''onTaskDeleted is called upon receiving a TaskDeleted message.
        :param otdb_id: otdb_id of the deleted task
        :param deleted: boolean indicating if delete action was successful
        :param paths: list of paths of the deleted task
        :param message: some remarks about the delete action'''
        pass

    def onTaskDataPinned(self, otdb_id, pinned):
        '''onTaskDataPinned is called upon receiving a TaskDataPinned message.
        :param otdb_id: otdb_id of the (un)pinned task
        :param pinned: boolean indicating if the data is pinned or not'''
        pass

    def onPathDeleting(self, path):
        '''onPathDeleting is called upon receiving a PathDeleting message.
        :param path: path of the about to be deleted task'''
        pass

    def onPathDeleted(self, path, deleted, message=''):
        '''onPathDeleted is called upon receiving a PathDeleted message.
        :param path: path of the deleted task
        :param deleted: boolean indicating if delete action was successful
        :param message: some remarks about the delete action'''
        pass

    def onDiskUsageChanged(self, path, disk_usage, otdb_id=None):
        '''onDiskUsageChanged is called upon receiving a DiskUsageChanged message.
        :param path: path for which the disk_usage changed
        :param path: the disk_usage of the path'''
        pass


class DataManagementBusListener(BusListener):
    def __init__(self,
                 handler_type: DataManagementEventMessageHandler.__class__ = DataManagementEventMessageHandler,
                 handler_kwargs: dict = None,
                 exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER,
                 num_threads: int=1):
        """
        DataManagementBusListener listens on the lofar notification message bus and calls (empty) on<SomeMessage> methods when such a message is received.
        Typical usage is to derive your own subclass from DataManagementBusListener and implement the specific on<SomeMessage> methods that you are interested in.
        :param busname: valid Qpid address
        :param broker: valid Qpid broker host
        """
        if not issubclass(handler_type, DataManagementEventMessageHandler):
            raise TypeError("handler_type should be a DataManagementEventMessageHandler subclass")

        super().__init__(handler_type=handler_type, handler_kwargs=handler_kwargs,
                         exchange=exchange, broker=broker,
                         routing_key="%s.#" % DEFAULT_DM_NOTIFICATION_PREFIX,
                         num_threads=num_threads)


if __name__ == '__main__':
    with DataManagementBusListener() as listener:
        waitForInterrupt()

__all__ = ["DataManagementBusListener"]
