# messages.py: Message classes used by the package lofar.messaging.
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
# $Id: messages.py 1580 2015-09-30 14:18:57Z loose $

"""
Message classes used by the package lofar.messaging.
"""

import uuid
from typing import Optional

from lofar.messaging.exceptions import MessageFactoryError

class LofarMessage:
    """
    Describes the content of a message, which can be constructed from either a
    set of fields, or from an existing QPID message.

    We want to provide a uniform interface to the user so that any message
    property or field, either defined by Qpid of by us, can be accessed as an
    object attribute. To do so, we needed to implement the `__getattr__` and
    `__setattr` methods; they "extract" our message properties from the Qpid
    message properties and provide direct access to them.
    """

    def __init__(self, content=None, subject:str=None, priority:int=4, ttl:float=None, id=None):
        """Constructor.

        :param content: Content can either be a qpid.messaging.Message object,
        or an object that is valid content for a qpid.messaging.Message. In the
        first case, `content` must contain all the message properties that are
        required by LOFAR.
        :raise InvalidMessage if `content` cannot be used to initialize an
        LofarMessage object.

        note:: Because every access to attributes will be caught by
        `__getattr__` and `__setattr__`, we need to use `self.__dict__` to
        initialize our attributes; otherwise a `KeyError` exception will be
        raised.
        """
        self.content = content
        self.subject = subject
        self.priority = priority
        self.ttl = ttl
        self.id = uuid.uuid4() if id is None else uuid.UUID(id)

    def as_kombu_publish_kwargs(self):
        """Convert this message into a kwargs-dict, ready for use with kombu.Producer.publish"""
        publish_kwargs = {'body':self.content,
                          'priority': self.priority,
                          'routing_key': self.subject,
                          'delivery_mode': 2, # survives broker restarts
                          'headers': {'SystemName': 'LOFAR',
                                      'MessageId': str(self.id),
                                      'MessageType': self.__class__.__name__,
                                      'Subject': self.subject}
                          }

        if self.ttl:
           publish_kwargs['expiration'] = self.ttl

        return publish_kwargs

    def __str__(self):
        content_str = str(self.content)
        delimited_content_str = content_str if len(content_str) <= 128 else (content_str[:128] + "...")
        return "%s subject=%s id=%s content=%s" % (self.__class__.__name__,
                                                   self.subject,
                                                   self.id,
                                                   delimited_content_str)


class MessageFactory:
    """
    A simple factory for registering conversion-methods to create the proper LofarMessage-sub-class from a given kombu_msg.
    """
    _registry = {}

    @staticmethod
    def register(message_type: LofarMessage.__class__, kombu2lofar_convert_method):
        if not isinstance(message_type, type):
            raise TypeError("message_type should be a LofarMessage subclass, not an instance!")

        if not issubclass(message_type, LofarMessage):
            raise TypeError("handler_type should be a LofarMessage subclass")

        MessageFactory._registry[message_type.__name__] = kombu2lofar_convert_method

    @staticmethod
    def create_lofar_message_from_kombu_message(kombu_msg):
        try:
            message_type_name = kombu_msg.headers['MessageType']

            if message_type_name in MessageFactory._registry:
                kombu2lofar_convert_method = MessageFactory._registry[message_type_name]
                return kombu2lofar_convert_method(kombu_msg)

            raise MessageFactoryError("Unable to create LofarMessage of type %s for kombu-msg: %s" % (message_type_name, kombu_msg))
        except Exception as e:
            raise MessageFactoryError("Unable to create LofarMessage for kombu-msg: %s. error=%s" % (kombu_msg, str(e)))

class EventMessage(LofarMessage):
    """
    Message class used for event messages. Events are messages that *must*
    be delivered. If the message cannot be delivered to the recipient, it
    will be stored in a persistent queue for later delivery.
    """

    def __init__(self, content=None, subject:str=None, priority:int=4, ttl:float=None, id=None):
        super(EventMessage, self).__init__(content, subject=subject, priority=priority, ttl=ttl, id=id)


# register the EventMessage with a conversion function to create it from a kombu_msg
MessageFactory.register(EventMessage,
                        lambda kombu_msg : EventMessage(content=kombu_msg.payload,
                                                        subject=kombu_msg.headers.get('Subject'),
                                                        id=kombu_msg.headers.get('MessageId'),
                                                        priority=kombu_msg.properties.get('priority',4)))

class CommandMessage(LofarMessage):
    """
    Message class used for command messages. Commands will typically be sent
    to a controller. Command messages are messages that *must* be delivered.
    If the message cannot be delivered to the recipient, it will be stored in
    a persistent queue for later delivery.
    """

    def __init__(self, content=None, subject:str=None, priority:int=4, ttl:float=None, id=None):
        super(CommandMessage, self).__init__(content=content, subject=subject, priority=priority, ttl=ttl, id=id)


# register the CommandMessage with a conversion function to create it from a kombu_msg
MessageFactory.register(CommandMessage,
                        lambda kombu_msg : CommandMessage(content=kombu_msg.payload,
                                                        subject=kombu_msg.headers.get('Subject'),
                                                        id=kombu_msg.headers.get('MessageId'),
                                                        priority=kombu_msg.properties.get('priority',4)))

__all__ = ['LofarMessage', 'EventMessage', 'CommandMessage', 'MessageFactory']