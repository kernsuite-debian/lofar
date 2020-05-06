#!/usr/bin/env python3
# RPCService.py: RPCService definition for the lofar.messaging module.
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

"""
A ServiceMessageHandler is a special type of AbstractMessageHandler to be used in conjunction with
the specialized RPCService implementation of the BusListener.
The two additions on top of AbstractMessageHandler/BusListener for the ServiceMessageHandler/RPCService are:
1) A ServiceMessageHandler can call methods based on the RequestMessage's subject
2) The RPCService then responds the result with a ReplyMessage


Here's an example:
>>> # implement your own ServiceMessageHandler, add some nice methods that do work
... class MyServiceMessageHandler(ServiceMessageHandler):
...     def foo(self, my_param):
...         print("foo was called. my_param =", my_param)
...         # ... do some work ...
...
...     def bar(self):
...         print("bar was called.")
...         # ... do some work ...

Use your handler in a RPCService instance
We assume you know that the TemporaryExchange is only needed here to have a working example.
>>> from lofar.messaging.messagebus import TemporaryExchange
>>> with TemporaryExchange() as tmp_exchange:
...     with RPCService(service_name="MyService",
...                  handler_type=MyServiceMessageHandler,
...                  exchange=tmp_exchange.address):
...
...         # That's it, now you have a running RPCService, waiting for incoming RequestMessages...
...         with RPCClient("MyService", exchange=tmp_exchange.address) as rpc:
...             rpc.execute("foo", my_param="whatever")
...             rpc.execute("bar")
...
...             # ... do some work ... simulate this by sleeping a little...
...             # ...in the mean time, the RPCService receives and handles the messages (on its own thread)
...             from time import sleep
...             sleep(0.25)
foo was called. my_param = whatever
bar was called.
"""

from lofar.messaging.config import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.messaging.messagebus import ToBus, BusListener, AbstractMessageHandler, UsingToBusMixin, TemporaryQueue
from lofar.messaging.messages import LofarMessage, MessageFactory
from lofar.messaging.exceptions import MessagingError
from lofar.common.util import program_name
from typing import Optional
from datetime import datetime, timedelta
import logging
import inspect

DEFAULT_RPC_TIMEOUT = 60

logger = logging.getLogger(__name__)

class RequestMessage(LofarMessage):
    """
    Message class used for service messages. RPCService messages are
    request-reply type of messages. They are typically used to query a
    subsystem. A service message must contain a valid ``ReplyTo`` property.
    """

    def __init__(self, subject:str, reply_to:str, priority:int=4, ttl:float=None, id=None):
        """create a new RequestMessage. Use method with_args_kwargs to specify request args and kwargs"""
        self.reply_to = reply_to
        content = { 'args': (), 'kwargs': {} }
        super(RequestMessage, self).__init__(content=content, subject=subject, priority=priority, ttl=ttl, id=id)

    def with_args_kwargs(self, *args, **kwargs):
        """set the args and kwargs for this request, which are passed along to the ServiceMessageHandler in the RPCService."""
        self.content = { 'args': args, 'kwargs': kwargs }
        return self

    def as_kombu_publish_kwargs(self):
        publish_kwargs = super(RequestMessage, self).as_kombu_publish_kwargs()
        publish_kwargs['reply_to'] = self.reply_to
        return publish_kwargs

    def __str__(self):
        return "%s reply_to=%s" % (super(RequestMessage, self).__str__(), self.reply_to)


# register the RequestMessage with a conversion function to create it from a kombu_msg
MessageFactory.register(RequestMessage,
                        lambda kombu_msg : RequestMessage(reply_to=kombu_msg.properties.get('reply_to'),
                                                          subject=kombu_msg.headers.get('Subject'),
                                                          id=kombu_msg.headers.get('MessageId'),
                                                          priority=kombu_msg.properties.get('priority',4)).with_args_kwargs(
                                                          *kombu_msg.payload.get('args', []),
                                                          **kombu_msg.payload.get('kwargs', {})))


class ReplyMessage(LofarMessage):
    """
    Message class used for reply messages. Reply messages are part of the
    request-reply type of messages. They are typically used as a reply on a service
    message. These use topic exchanges and thus are routed by the 'subject' property
    """

    def __init__(self, content, handled_successfully: bool, subject:str=None, priority:int=4, ttl:float=None, id=None, error_message: Optional[str]= ""):
        super(ReplyMessage, self).__init__(content=content, subject=subject, priority=priority, ttl=ttl, id=id)
        self.handled_successfully = handled_successfully
        self.error_message = error_message

    def as_kombu_publish_kwargs(self):
        publish_kwargs = super(ReplyMessage, self).as_kombu_publish_kwargs()
        publish_kwargs['headers']['handled_successfully'] = self.handled_successfully
        publish_kwargs['headers']['error_message'] = self.error_message
        return publish_kwargs

    def __str__(self):
        return "%s handled_successfully=%s%s" % (
            super(ReplyMessage, self).__str__(),
            self.handled_successfully,
            " error=%s" % self.error_message if self.error_message else "")

# register the ReplyMessage with a conversion function to create it from a kombu_msg
MessageFactory.register(ReplyMessage,
                        lambda kombu_msg : ReplyMessage(handled_successfully=kombu_msg.headers.get('handled_successfully'),
                                                        content=kombu_msg.payload,
                                                        subject=kombu_msg.headers.get('Subject'),
                                                        id=kombu_msg.headers.get('MessageId'),
                                                        priority=kombu_msg.properties.get('priority',4),
                                                        error_message=kombu_msg.headers.get('error_message')))

class ServiceMessageHandler(UsingToBusMixin, AbstractMessageHandler):
    def __init__(self):
        self.service_name = None
        self._subject_to_method_map = {}
        super(ServiceMessageHandler, self).__init__()

    def init_service_handler(self, service_name: str):
        """set the given parameters and automatically register all public handler methods"""
        self.service_name = service_name
        self.register_public_handler_methods()

    def register_public_handler_methods(self) -> None:
        excluded_class_names = (ServiceMessageHandler.__name__,) + tuple(x.__name__ for x in ServiceMessageHandler.__bases__)

        # predicate function for inspect.getmembers to filter only for public methods in subclasses
        def is_public_method_of_subclass(member):
            # should be member method
            if not inspect.ismethod(member):
                return False

            # should be "public"
            if member.__name__.startswith('_'):
                return False

            # should be method of the actual ServiceMessageHandler implementation
            if not issubclass(member.__self__.__class__, self.__class__):
                return False

            # should not be method of the excluded super classes
            super_class_name = member.__qualname__.partition(".")[0]
            return super_class_name not in excluded_class_names

        # register all public methods of subclasses
        for m in inspect.getmembers(self, is_public_method_of_subclass):
            self.register_service_method(m[0], m[1])

    def register_service_method(self, method_name: str, method: classmethod) -> None:
        """ register a service method.
        This allows this handler to map a RequestMessage's subject to one of its methods.
        The RPCService automatically registers all this handler's public methods, so there is usually no need to
        register any additinal methods.
        """
        logger.debug("%s registering method %s", self.service_name or "<unknown-service>", method_name)
        self._subject_to_method_map[method_name] = method

    def handle_message(self, msg: LofarMessage):
        if not isinstance(msg, RequestMessage):
            raise ValueError("%s: Ignoring non-RequestMessage: %s" % (self.__class__.__name__, msg))

        # handle the RequestMessage via the _service_handle_message
        # create a ReplyMessage based on the success (exception or not)
        # use the reply_msg.handled_successfully as state variable for error handling below...
        try:
            result = self._service_handle_message(msg)
            reply_msg = ReplyMessage(content=result,
                                     handled_successfully=True,
                                     subject=msg.reply_to,
                                     error_message=None)
        except Exception as e:
            logger.warning(e)
            reply_msg = ReplyMessage(content=None,
                                     handled_successfully=False,
                                     subject=msg.reply_to,
                                     error_message=str(e))

        # try to send back the reply, might raise on itself, which is ok, it's handled by the buslistener.
        self.send(reply_msg)

        # send was ok, no exception
        # now check reply_msg.handled_successfully state variable,
        # and raise if False. The exception is then handled by the buslistener.
        if not reply_msg.handled_successfully:
            raise Exception(reply_msg.error_message)


    def _service_handle_message(self, request_msg: RequestMessage) -> Optional[object]:
        """do a lookup in the registered service handler methods based on the subject of the request_msg,
        and call it, returning the service handler method's result."""
        subject_prefix = "%s." % self.service_name

        if not request_msg.subject.startswith(subject_prefix):
            # thanks to proper routing, this should never occur
            raise ValueError("%s: unexpected subject for service_name=%s RequestMessage with subject %s" % (
                             self.__class__.__name__,
                             self.service_name,
                             request_msg.subject))

        # do lookup based on subject without the service_name prefix
        stripped_subject = request_msg.subject.replace(subject_prefix, "", 1)

        if stripped_subject not in self._subject_to_method_map:
            raise KeyError("%s: No known handler method for a RequestMessage with subject %s" % (
                self.__class__.__name__, request_msg.subject))

        service_handler_method = self._subject_to_method_map[stripped_subject]

        try:
            rpc_args = request_msg.content.get('args', [])
            rpc_kwargs = request_msg.content.get('kwargs', {})

            logger.info("%s.%s calling service method %s(%s%s%s)", self.service_name or "<unknown-service>",
                                                           self.__class__.__name__,
                                                           service_handler_method.__name__,
                                                           ', '.join(str(arg) for arg in rpc_args),
                                                           ', ' if len(rpc_args) else '',
                                                           ', '.join("%s=%s" % (k,v) for k,v in rpc_kwargs.items()))
            return service_handler_method(*rpc_args, **rpc_kwargs)

        except Exception as e:
            logger.exception(str(e))
            raise Exception("%s: Error while handling msg with subject %s in service %s in method %s: %s" % (
                         self.__class__.__name__,
                         request_msg.subject,
                         self.service_name,
                         service_handler_method.__name__,
                         e))

    def __str__(self):
        return "%s for service '%s'" % (self.__class__.__name__, self.service_name)


class RPCService(BusListener):
    def __init__(self, service_name: str,
                 handler_type: ServiceMessageHandler.__class__,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME,
                 num_threads: int = 1,
                 broker: str = DEFAULT_BROKER):

        if not issubclass(handler_type, ServiceMessageHandler):
            raise TypeError("handler_type should be a ServiceMessageHandler subclass")

        self.service_name = service_name
        self.exchange = exchange

        # call the BusListener's contructor
        # and make sure it connects to the exchange via a designated queue using the service's name as routing_key filter.
        super(RPCService, self).__init__(exchange=exchange, routing_key="%s.#" % service_name,
                                         handler_type = handler_type,
                                         handler_kwargs = handler_kwargs,
                                         num_threads=num_threads, broker=broker)

    def _create_handler(self):
        """override of super-class. Create the service message handler, and initialize it."""
        service_handler = super()._create_handler()
        service_handler.init_service_handler(self.service_name)
        return service_handler

class RPCException(MessagingError):
    pass

class RPCTimeoutException(RPCException, TimeoutError):
    pass

class RPCClient():
    """
    An RPCClient instance enables the execution of remote procedure calls on a remotely running RPCService.
    It is assumed/expected that a RPCService is running and listening on the given, otherwise nobody will answer.
    See example usage at the top of this module file.
    """

    def __init__(self, service_name: str,
                 exchange: str = DEFAULT_BUSNAME,
                 broker: str = DEFAULT_BROKER,
                 timeout: int = DEFAULT_RPC_TIMEOUT):
        """
        Create an RPCClient instance, enabling the execution of remote procedure calls on the given <service_name>
        via the given <exchange> and <broker>.
        """
        self._service_name = service_name
        self.exchange = exchange
        self._timeout = timeout
        self._request_sender = ToBus(exchange=exchange, broker=broker, connection_log_level=logging.DEBUG)

    def open(self):
        """Open the rcp request sender connection to the broker. Recommended to be used in a 'with' context."""
        self._request_sender.open()

    def close(self):
        """Close the rcp request sender connection to the broker. Recommended to be used in a 'with' context."""
        self._request_sender.close()

    def __enter__(self):
        """enter a 'with' context, open the request sender"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """leave the 'with' context, close the request sender"""
        self.close()

    def execute(self, method_name, *args, **kwargs):
        """execute the given <method_name> procedure remotely on the service"""
        start_time = datetime.utcnow()

        # use the same exchange/broker as the request sender
        exchange = self._request_sender.exchange
        broker = self._request_sender.broker

        # setup a temporary queue on which we can receive the answer from the service
        with TemporaryQueue(name_prefix="rpc-reply-for-%s-%s" % (program_name(include_extension=False), self._service_name),
                            exchange=exchange,
                            broker=broker,
                            addressed_to_me_only=True) as tmp_reply_queue:
            with tmp_reply_queue.create_frombus() as reply_receiver:
                elapsed = (datetime.utcnow() - start_time).total_seconds()

                # by convention, the service listens for any message starting with the service_name,
                # and then calls the method given after the '.'
                service_method = "%s.%s" % (self._service_name, method_name)

                # create a request message, make sure it's routed to the service using the <service_method>
                # specify where to send the reply to (to our tmp queue)
                # and set a ttl (time-to-live), so the broker will automatically purge messages which are not handled in time.
                # pass along the given args and kwargs as arguments for the remote service method.
                request_msg = RequestMessage(subject=service_method,
                                             reply_to=tmp_reply_queue.address,
                                             ttl=max(0, self._timeout - elapsed),
                                             priority=4).with_args_kwargs(*args, **kwargs)

                logger.debug("executing rpc call to service.method=%s via exchange=%s args=%s kwargs=%s waiting for answer on %s",
                             service_method,
                             exchange,
                             args, kwargs,
                             tmp_reply_queue.address)

                self._request_sender.send(request_msg)

                elapsed = (datetime.utcnow() - start_time).total_seconds()
                wait_time = max(0.001, self._timeout - elapsed)

                logger.debug("executed rpc call to service.method=%s via exchange=%s waiting %.1fsec for answer on %s",
                             service_method,
                             exchange,
                             wait_time,
                             tmp_reply_queue.address)

                answer = reply_receiver.receive(wait_time)

                if answer is None:
                    raise RPCTimeoutException("rpc call to service.method=%s via exchange=%s timed out after %.1fsec" % (
                                               service_method, exchange, self._timeout))

                if not isinstance(answer, ReplyMessage):
                    raise ValueError("rpc call to service.method=%s via exchange=%s received an unexpected non-ReplyMessage of type %s" % (
                                     service_method, exchange, answer.__class__.__name__))

                logger.debug("executed rpc call to service.method=%s via exchange=%s received valid answer on %s",
                             service_method,
                             exchange,
                             tmp_reply_queue.address)

                if answer.handled_successfully:
                    return answer.content

                raise RPCException(answer.error_message)


class RPCClientContextManagerMixin:
    """Simple Mixin class which provides an your class using an RPCClient to be used in a 'with' context,
    automatically opening/closing the rpc"""
    def __init__(self):
        self._rpc_client = None

    def open(self):
        """Opens the RPCClient"""
        self._rpc_client.open()

    def close(self):
        """Closes the RPCClient"""
        self._rpc_client.close()

    def __enter__(self):
        """Opens the RPCClient upon entering the 'with' context"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the RPCClient upon exiting the 'with' context"""
        self.close()


__all__ = ['DEFAULT_RPC_TIMEOUT', 'ServiceMessageHandler', 'RPCService', 'RPCClient', 'RPCClientContextManagerMixin',
           'RequestMessage', 'ReplyMessage', 'RPCException', 'RPCTimeoutException']

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s %(threadName)s %(message)s', level=logging.DEBUG)
    logging.getLogger('lofar.messaging.messagebus').level = logging.INFO

    # run the doctests in this module
    import doctest
    doctest.testmod(verbose=True, report=True)
