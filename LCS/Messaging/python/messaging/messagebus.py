# messagebus.py: Provide an easy way exchange messages on the message bus.
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
LOFAR's common and simple messaging API around AMQP messaging frameworks.

For more background information on messaging:
 - AMQP (the protocol): https://www.amqp.org and https://en.wikipedia.org/wiki/Advanced_Message_Queuing_Protocol
 - RabbitMQ (the broker): https://www.rabbitmq.com/
 - Kombu (the python client used in this package): https://kombu.readthedocs.io/en/stable/

Concepts (the quick common background summary):
Messaging is used to provide fast robust reliable communication between software programs.
Messages (containing your valuable information) are exchanged via a so-called broker. We use RabbitMQ for that.
Messages are 'published' on so called 'exchanges' on the broker.
If you're listening on that exchange, you receive the message. But if you're not listening, the message is lost for you forever.
That's why there are also 'queues' (on the broker). A queue can hold messages for you, even if you're not listening, and
you'll receive them as soon as you start listening.

The trick of a well used messaging system is to have single or a only few exchanges on which every program publishes his
messages with a proper 'subject' (also called 'routing_key'), and have the broker route the message to zero or more
queues which are interested in these particular messages. It makes sense to have one or more designated queue's for each program,
so each program receives only the messages which are interesting for him.

LOFAR's messaging way:
The two core classes are:
 - the ToBus to publish messages on an exchange
 - the FromBus to receive messages from a queue

RabbitMQ provides a nice webinterface and CLI to setup exchanges and queues, but we also provide some convenience methods,
Let's use them here in an example to setup a simple exchange, and bind a queue to it.
We're assuming you're running a RabbitMQ broker on localhost.

>>> create_bound_queue("my.exchange", "my.queue")

Now we have done three things:
1) create an exchange on the broker called "my.exchange"
2) create a queue on the broker called "my.queue"
3) create a binding between the two routing all messages from the exchange to the queue

Let's send a message to the bus:
>>> with ToBus("my.exchange") as tobus:
...     tobus.send(EventMessage(subject="some.event", content="foo"))

That's it, it's that simple. So, what just happened?
By constructing a ToBus instance in a python 'with' context we make sure that the connection to the broker is cleaned up.
Calling tobus.send can send any LofarMessage to the exchange, in this case an EventMessage.
The message has been sent (published), and we can now forget about it...

... or we can listen for interesting messages with a FromBus, like so:
>>> with FromBus("my.queue") as frombus:
...     msg = frombus.receive()
...     print(msg.content)
...
foo

Notice that we *did* receive the message, even after contructing a FromBus after the message was send!
That's because it was stored in the queue at the broker, ready to be delivered as soon as we started listening.

Let's be nice, and cleanup our exchange and queue at the broker, like so:
>>> delete_exchange("my.exchange")
True
>>> delete_queue("my.queue")
True


These are the basics, now let's move one to the more interesting usage,
for example working with dynamically created/deleted exchanges/queues.
This is a typical pattern used in many tests where we want unique short-lived exchanges and queues,
which are guaranteed to be deleted upon test completion.
Another use-case is for example in the RPCClient/RPCService usage, but that's a later example.

>>> # create a TemporaryExchange in a context, so it's automagically created and deleted
... with TemporaryExchange("my.exchange") as tmp_exchange:
...
...     # create a TemporaryQueue in a context, so it's automagically created and deleted
...     # connect/bind it to the tmp_exchange
...     with TemporaryQueue("my.queue", exchange=tmp_exchange.address) as tmp_queue:
...
...         # use the convenience factory method to create a ToBus instance on the exchange
...         # notice that it's also used in a context for automatic connect/disconnect.
...         with tmp_exchange.create_tobus() as tobus:
...             tobus.send(EventMessage(subject="some.event", content="foo"))
...
...         # and finally use the convenience factory method to create a FromBus instance on the queue
...         # notice that it's also used in a context for automatic connect/disconnect.
...         with tmp_queue.create_frombus() as frombus:
...             msg = frombus.receive()
...             print(msg.content)
...
foo

Ok, until now the examples were simple, and only sending/receiving a single message...
In practice most of our programs are event-driven, and act on received messages.
That means we should be able to continuously listen for messages, and handle them when we receive any.
That's what the BusListener is for. It's a core class used in many lofar programs.
Let's illustrate with an example...
 - Use the now familiar TemporaryExchange
 - Define a concrete implementation of an handler for the BusListener: MyMessageHandler
 - Show how the BusListener is used, and how the MyMessageHandler is injected.
 - an additional feature shown here is the use of the routing_key from the tmp_exchange to the tmp_queue:
   only messages with subject 'some.#' are routed to the queue, and hence received by the buslistener.

>>> with TemporaryExchange("my.exchange") as tmp_exchange:
...     with tmp_exchange.create_tobus() as tobus:
...         listener_queue_name = None
...         try:
...             # implement an example AbstractMessageHandler which just prints the received message subject and content
...             class MyMessageHandler(AbstractMessageHandler):
...                 def handle_message(self, lofar_msg):
...                     print(lofar_msg.subject, lofar_msg.content)
...                     # ... do some more fancy stuff with the msg...
...
...             # construct a BusListener instance in a context,
...             # so it starts/stops listening and and handling messages automagically
...             with BusListener(MyMessageHandler, exchange=tmp_exchange.address, routing_key="some.#") as listener:
...                 listener_queue_name = listener.address
...                 tobus.send(EventMessage(subject="some.event", content="foo"))
...                 tobus.send(EventMessage(subject="another.event", content="xyz"))
...                 tobus.send(EventMessage(subject="some.event", content="bar"))
...
...                 # ... do some work ... simulate this by sleeping a little...
...                 # ...in the mean time, BusListener receives and handles the messages (on its own thread)
...                 from time import sleep
...                 sleep(0.5)
...         finally:
...             delete_queue(listener_queue_name)
...
some.event foo
some.event bar
True

In practice you might find it a too big hassle to setup a designated queue for such a listener. It's also easy to make
a mess of queue names, routing keys, etc etc... So, isn't there a uniform and simple way to set up a designated queue
for each listener? Yes, there is: just provide the general exchange name and a routing_key to the listener, and the
designated queue is created automagically for you, with the following standard name: <exchange_name>.for.<program_name>.<routing_key>
Please note that this queue is not deleted upon exit, and that's by design! This way, all our lofar programs use the same
paradigm to create queues, and broker queue confiration is simplified and uniform.
Suppose that, as in the following example, or in unittests etc, you would like to leave the system as clean as you found it.
Then you want to get rid of the auto-generated queue for this listener. Use the BusListenerJanitor!
Let's illustrate this with a slight midification of the above example...
 - Use the now familiar TemporaryExchange (but no TemporaryQueue!)
 - Define again aconcrete implementation of an BusListener: BusListener
 - Show how the BusListener is used:
    - let it bind automagically to the exchange this time, via the standarized auto-generated queue (including filtering on subject 'some.#')
    - use the BusListenerJanitor to do the cleanup of the auto-generated queue for us.


>>> with TemporaryExchange("my.exchange") as tmp_exchange:
...     with tmp_exchange.create_tobus() as tobus:
...
...         # construct a BusListener instance in a BusListenerJanitor context,
...         # so it starts/stops listening and and handling messages automagically
...         # and have the auto-generated buslistener's queue be auto-deleted via the janitor.
...         with BusListenerJanitor(BusListener(MyMessageHandler, exchange=tmp_exchange.address, routing_key="some.#")):
...             tobus.send(EventMessage(subject="some.event", content="foo"))
...             tobus.send(EventMessage(subject="another.event", content="xyz"))
...             tobus.send(EventMessage(subject="some.event", content="bar"))
...
...             # ... do some work ... simulate this by sleeping a little...
...             # ...in the mean time, BusListener receives and handles the messages (on its own thread)
...             from time import sleep
...             sleep(0.25)
...
some.event foo
some.event bar



"""

import kombu, kombu.exceptions, amqp.exceptions
import inspect
import re
import uuid
import threading
from typing import Optional
from datetime import datetime, timedelta
from queue import Empty as EmptyQueueError
from socket import gaierror
import json
import requests

import logging
logger = logging.getLogger(__name__)

from lofar.messaging.exceptions import *
from lofar.messaging import adaptNameToEnvironment
from lofar.messaging.messages import *
from lofar.messaging.config import DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_PORT, DEFAULT_USER, DEFAULT_PASSWORD
from lofar.common.threading_utils import TimeoutLock
from lofar.common.util import program_name
from lofar.common.util import is_empty_function



# some serializers are considered 'insecure', but we know better ;)
# so enable the python pickle serializer
kombu.enable_insecure_serializers(['pickle'])

# default receive timeout in seconds
DEFAULT_BUS_TIMEOUT = 5

def can_connect_to_broker(broker: str=DEFAULT_BROKER, port: int=DEFAULT_PORT) -> bool:
    try:
        logger.debug("trying to connect to broker: hostname=%s port=%s userid=%s password=***",
                     broker, port, DEFAULT_USER)
        with kombu.Connection(hostname=broker, port=port, userid=DEFAULT_USER, password=DEFAULT_PASSWORD,
                              max_retries=0, connect_timeout=1) as connection:
            connection.connect()
            logger.debug("can connect to broker with hostname=%s port=%s userid=%s password=***",
                        broker, port, DEFAULT_USER)
            return True
    except Exception as e:
        logger.error("cannot connect to broker with hostname=%s port=%s userid=%s password=***, error: %s",
                     broker, port, DEFAULT_USER, e)
        return False

def create_exchange(name: str, durable: bool=True, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG) -> bool:
    """
    create a message exchange of type topic with the given name on the given broker if needed (not already existing)
    :param name: the name for the exchange
    :param durable: if True, then the exchange 'survives' broker restarts
    :param broker: a message broker address
    :param log_level: optional logging level (to add/reduce spamming)
    :raises: MessagingError if the exchange could not be created
    :return True if created, False if not-created (because it already exists)
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            exchange = kombu.Exchange(name, durable=durable, type='topic')
            try:
                exchange.declare(channel=connection.default_channel, passive=True)
            except amqp.exceptions.NotFound:
                exchange.declare(channel=connection.default_channel)
                logger.log(log_level, "Created exchange %s on broker %s", name, broker)
                return True
        return False
    except Exception as e:
        raise MessagingError("Could not create exchange %s on broker %s error=%s" % (name, broker, e))

def delete_exchange(name: str, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG) -> bool:
    """
    delete the exchange with the given name on the given broker
    :param name: the name for the exchange
    :param broker: a message broker address
    :param log_level: optional logging level (to add/reduce spamming)
    :raises: MessagingError if the exchange could not be deleted
    :return True if deleted, False if not-deleted (because it does not exist)
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            exchange = kombu.Exchange(name, channel=connection)
            try:
                exchange.declare(channel=connection.default_channel, passive=True)
                exchange.delete()
                logger.log(log_level, "Deleted exchange %s on broker %s", name, broker)
                return True
            except amqp.exceptions.NotFound:
                return False
    except Exception as e:
        raise MessagingError("Could not delete exchange %s on broker %s error=%s" % (name, broker, e))

def exchange_exists(name: str, broker: str=DEFAULT_BROKER) -> bool:
    """
    does the exchange with the given name exist on the given broker?
    :param name: the name for the exchange
    :param broker: a message broker address
    :return True if it exists, False if not.
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            exchange = kombu.Exchange(name, channel=connection)
            try:
                exchange.declare(channel=connection.default_channel, passive=True)
                return True
            except amqp.exceptions.NotFound:
                return False
    except Exception as e:
        raise MessagingError("Could not test if exchange %s exists on broker %s error=%s" % (name, broker, e))


def create_queue(name: str, durable: bool=True, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG, auto_delete: bool=False) -> bool:
    """
    create a message queue with the given name on the given broker
    :param name: the name for the queue
    :param durable: if True, then the queue 'survives' broker restarts
    :param broker: a message broker address
    :param log_level: optional logging level (to add/reduce spamming)
    :param auto_delete: if True, then the queue is automatically deleted when the last consumer disconnects.
    :raises: MessagingError if the queue could not be created
    :return True if created, False if not-created (because it already exists)
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            queue = kombu.Queue(name,
                                durable=durable,
                                auto_delete=auto_delete,
                                max_priority=9 # need to set max_priority to get a queue that respects priorities on messages.
                                )
            try:
                queue.queue_declare(channel=connection.default_channel, passive=True)
            except amqp.exceptions.NotFound:
                queue.queue_declare(channel=connection.default_channel)
                logger.log(log_level, "Created queue %s on broker %s", name, broker)
                return True
        return False
    except Exception as e:
        raise MessagingError("Could not create queue %s on broker %s error=%s" % (name, broker, e))

def delete_queue(name: str, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG) -> bool:
    """
    delete the message queue with the given name on the given broker (any messages in the queue are discarded)
    :param name: the name for the queue
    :param broker: a message broker address
    :param log_level: optional logging level (to add/reduce spamming)
    :raises: MessagingError if the queue could not be deleted
    :return True if deleted, False if not-deleted (because it does not exist)
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            queue = kombu.Queue(name, no_declare=True, channel=connection)
            try:
                queue.queue_declare(channel=connection.default_channel, passive=True)
                queue.delete(if_unused=False, if_empty=False)
                logger.log(log_level, "Deleted queue %s on broker %s", name, broker)
                return True
            except amqp.exceptions.NotFound:
                return False
    except Exception as e:
        raise MessagingError("Could not delete queue %s on broker %s error=%s" % (name, broker, e))

def queue_exists(name: str, broker: str=DEFAULT_BROKER) -> bool:
    """
    does the queue with the given name exist on the given broker?
    :param name: the name for the queue
    :param broker: a message broker address
    :return True if it exists, False if not.
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            queue = kombu.Queue(name, no_declare=True, channel=connection)
            try:
                queue.queue_declare(channel=connection.default_channel, passive=True)
                return True
            except amqp.exceptions.NotFound:
                return False
    except Exception as e:
        raise MessagingError("Could not test if queue %s exists on broker %s error=%s" % (name, broker, e))

def nr_of_messages_in_queue(queue_name: str, broker: str = DEFAULT_BROKER) -> int:
    """get the number of messages in the queue"""
    try:
        # the kombu way of getting the number of messages via a passice queue_declare is not reliable...
        # so, let's use the http REST API using request
        url = "http://%s:15672/api/queues/%%2F/%s" % (broker, queue_name)
        response = requests.get(url, auth=(DEFAULT_USER, DEFAULT_PASSWORD))
        queue_info = json.loads(response.text)
        return queue_info.get('messages', 0)
    except Exception as e:
        return 0

def create_binding(exchange: str, queue: str, routing_key: str='#', durable: bool=True, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG):
    """
    create a binding between the exchange and queue, possibly filtered by the routing_key, on the given broker.
    please note that this only creates the binding, not the exchange, nor the queue. See also create_bound_queue(...)
    :param exchange: the name for the exchange
    :param queue: the name for the queue
    :param routing_key: filter only messages with the given routing_key to the queue
    :param durable: if True, then the queue 'survives' broker restarts
    :param broker: a message broker address
    :param log_level: optional logging level (to add/reduce spamming)
    """
    try:
        with kombu.Connection(hostname=broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD) as connection:
            kombu_exchange = kombu.Exchange(exchange, durable=durable, type='topic', no_declare=True)
            kombu_queue = kombu.Queue(queue, exchange=kombu_exchange, routing_key=routing_key, durable=durable, no_declare=True)
            if not kombu_queue.is_bound:
                kombu_queue.queue_bind(channel=connection.default_channel)
                logger.log(log_level, "Added binding from exchange %s to queue %s with routing_key %s on broker %s",
                           exchange, queue, routing_key, broker)
            return True
    except amqp.exceptions.NotFound as e:
        raise MessageBusError("Could not create binding from exchange %s to queue %s with routing_key %s " \
                " on broker %s because either the exchange or queue does not exist. error=%s" % (exchange,
                                                                                                 queue,
                                                                                                 routing_key,
                                                                                                 broker,
                                                                                                 e))
    except Exception as e:
        raise MessageBusError("Could not create binding from exchange %s to queue %s with routing_key %s " \
                             " on broker %s error=%s" % (exchange, queue, routing_key, broker, e))

def create_bound_queue(exchange: str, queue: str, routing_key: str='#', durable: bool=True, broker: str=DEFAULT_BROKER, log_level=logging.DEBUG, auto_delete: bool=False):
    """
    create an exchange (if needed), queue (if needed), and the in-between binding, possibly filtered by the routing_key, on the given broker.
    :param exchange: the name for the exchange
    :param queue: the name for the queue
    :param routing_key: filter only messages with the given routing_key to the queue
    :param durable: if True, then the queue 'survives' broker restarts
    :param broker: a message broker address
    :param auto_delete: if True, then the queue is automatically deleted when the last consumer disconnects.
    :param log_level: optional logging level (to add/reduce spamming)
    """
    create_exchange(exchange, durable=durable, broker=broker, log_level=log_level)
    create_queue(queue, durable=durable, broker=broker, log_level=log_level, auto_delete=auto_delete)
    create_binding(exchange, queue, routing_key, durable=durable, broker=broker, log_level=log_level)



class _AbstractBus:
    """
    Common class for ToBus and FromBus, providing an common way to connect to the amqp message bus.
    """

    def __init__(self, broker: str=DEFAULT_BROKER, connection_log_level: int=logging.INFO):
        """
        Constructor, specifying the address of the queue or exchange to connect to on the given broker.
        :param broker: the valid broker url, like 'localhost'
        :param connection_log_level: optional logging level for opening/closing the connection (to add/reduce spamming)
        """
        self.broker = broker
        self._connection_log_level = connection_log_level
        self._connection = None
        self._lock = TimeoutLock()

    @property
    def is_connected(self) -> bool:
        """Is this instance connected to the bus? """
        with self._lock:
            return (self._connection is not None) and self._connection.connected

    @property
    def local_address(self) -> (str, int):
        """get a ip,port tuple for the local socket of the connection"""
        with self._lock:
            if not self.is_connected:
                raise MessageBusError("cannot get local socket address for an unconnected bus")
            return self._connection._connection.sock.getsockname()

    @property
    def remote_address(self) -> (str, int):
        """get a ip,port tuple for the remote socket of the connection"""
        with self._lock:
            if not self.is_connected:
                raise MessageBusError("cannot get remote socket address for an unconnected bus")
            parts = self._connection.host.partition(':')
            return (parts[0], int(parts[2]))

    @property
    def connection_name(self) -> str:
        """returns the connection name in rabbitmq format: local socket's ip:port -> remote socket's ip:port"""
        local = self.local_address
        remote = self.remote_address
        return "%s:%d -> %s:%d" % (local[0], local[1], remote[0], remote[1])

    def open(self):
        """
        Open a connection to the broker, and connect to the endpoint (a receiver for a FromBus, a sender for a ToBus)
        It is recommended to not use open() and close() directly, but in a 'with' context.
        :raise MessagingError: in case connecting to the broker or the address failed.
        """
        try:
            with self._lock:
                if self.is_connected:
                    return

                logger.debug("[%s] Connecting to broker: %s", self.__class__.__name__, self.broker)
                self._connection = kombu.Connection(hostname=self.broker, port=DEFAULT_PORT, userid=DEFAULT_USER, password=DEFAULT_PASSWORD)
                self._connection.connect()
                logger.debug("[%s] Connected to broker: %s (%s)", self.__class__.__name__, self.broker, self.connection_name)

                # let the subclass (FromBus or ToBus) create a receiver of sender
                self._connect_to_endpoint()
        except Exception as ex:
            error_msg = "[%s] Connecting to broker %s failed: %s" % (self.__class__.__name__, self.broker, ex)
            if isinstance(ex, gaierror) or isinstance(ex, OSError) or isinstance(ex, MessageBusError):
                # log "normal" known exceptions as error...
                logging.error(error_msg)
            else:
                # log other exceptions with stack trace...
                logging.exception(error_msg)

            # it is possible that a connection was established already
            # raising the MessageBusError below will not call the close method via the 'with' context manager
            # because the __enter__  was not finished yet
            # so, we have to close any connections here our selves.
            self.close()

            # ... and finally raise a MessageBusError ourselves with a nice error message
            raise MessageBusError(error_msg)

    def close(self):
        """
        Disconnect from the endpoint (a receiver for a FromBus, a sender for a ToBus), and close the  connection to the broker.
        It is recommended to not use open() and close() directly, but in a 'with' context.
        :raise MessagingError: in case disconnecting from the broker or the address failed.
        """
        with self._lock:
            if not self.is_connected:
                return

            try:
                self._disconnect_from_endpoint()
            except MessagingError as e:
                logger.error(e)

            try:
                logger.debug("[%s] Disconnecting from broker: %s", self.__class__.__name__, self.broker)
                self._connection.close()
                logger.debug("[%s] Disconnected from broker: %s", self.__class__.__name__, self.broker)
            except Exception as ex:
                if isinstance(ex, AttributeError) and 'drain_events' in str(ex):
                    # looks like a kombu bug, just continue
                    pass
                else:
                    error_msg = "[%s] Disconnecting from broker %s failed: %s" % (self.__class__.__name__, self.broker, ex)

                    logger.exception(error_msg)
                    raise MessagingError(error_msg)
            finally:
                self._connection = None

    def reconnect(self):
        """
        Reconnect by calling close and open.
        :raise MessagingError: in case connecting from the broker or the address failed.
        """
        with self._lock:
            logger.info("[%s] Reconnecting to broker: %s", self.__class__.__name__, self.broker)
            try:
                # close and catch any exceptions...
                self.close()
            except Exception as ex:
                logging.error(ex)
            # open and allow any open/connect exceptions to be raised and bubbled upwards.
            self.open()
            logger.info("[%s] Reconnected to broker: %s (%s)", self.__class__.__name__, self.broker, self.connection_name)

    def __enter__(self) -> '_AbstractBus':
        """Open the connection when entering a 'with' context."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the connection leaving the 'with' context."""
        self.close()

    def _connect_to_endpoint(self):
        # implement in subclass
        raise NotImplementedError()

    def _disconnect_from_endpoint(self):
        # implement in subclass
        raise NotImplementedError()

    def _is_connection_error(self, error: Exception) -> bool:
        if isinstance(error, amqp.exceptions.ConnectionError):
            return True
        if isinstance(error, kombu.exceptions.ConnectionError):
            return True
        if isinstance(error, OSError) or isinstance(error, IOError):
            msg = str(error).lower()
            if 'connection' in msg or 'socket' in msg:
                return True
        return False


class FromBus(_AbstractBus):
    """
    A FromBus provides an easy way to fetch messages from the message bus.
    The recommended way is to use a FromBus in a 'with' context, like so.

    >>> # use a TemporaryQueue where we can let the FromBus connect to
    ... with TemporaryQueue() as tmp_queue:
    ...     # create a new FromBus, use it in a context.
    ...     with FromBus(queue=tmp_queue.address) as frombus:
    ...         print("connected =", frombus.is_connected)
    ...
    ...         # try to receive a message (there is None, cause nobody sent any)
    ...         msg = frombus.receive(timeout=0.1)
    ...         print("msg =", msg)
    ...
    ...     # left context, so is_connected should be false now.
    ...     print("connected =", frombus.is_connected)
    ...
    connected = True
    msg = None
    connected = False
    """

    def __init__(self, queue: str, broker: str=DEFAULT_BROKER, connection_log_level=logging.DEBUG):
        """
        Constructor, specifying the address of the queue to connect to on the given broker.
        :param queue: the 'name' of the queue to connect to.
        :param broker: a valid broker url, like 'localhost'
        :param connection_log_level: optional logging level for opening/closing the connection (to add/reduce spamming)
        """
        self.queue = queue
        self._unacked_messages = {}
        self._receiver = None
        super(FromBus, self).__init__(broker=broker, connection_log_level=connection_log_level)

    def _connect_to_endpoint(self):
        """
        Implementation of abstract method. Connect a receiver to the broker queue specified by the queue address.
        Can raise kombu/amqp exceptions, which are handled in the _AbstractBus.
        """
        try:
            logger.debug("[FromBus] Connecting receiver to: %s on broker: %s", self.queue, self.broker)

            kombu_queue = kombu.Queue(self.queue, no_declare=True)

            # try to passivly declare the queue on the broker, raises if non existent
            kombu_queue.queue_declare(passive=True, channel=self._connection.default_channel)

            self._receiver = self._connection.SimpleQueue(kombu_queue)
            self._receiver.consumer.qos(prefetch_count=0) # do not prefetch any messages

            logger.log(self._connection_log_level, "[FromBus] Connected receiver to: %s on broker: %s", self.queue, self.broker)
        except Exception as ex:
            error_msg = "[FromBus] Connecting to %s at broker %s failed: %s" % (self.queue, self.broker, ex)
            if isinstance(ex, amqp.exceptions.NotFound) :
                # log "normal" known exceptions as error...
                logging.error(error_msg)
            else:
                # log other exceptions with stack trace...
                logging.exception(error_msg)

            # ... and finally raise a MessageBusError ourselves with a nice error message
            raise MessageBusError(error_msg)

    def _disconnect_from_endpoint(self):
        """
        Implementation of abstract method. Disconnect the receiver from the broker queue.
        Can raise kombu/amqp exceptions, which are handled in the _AbstractBus.
        """
        try:
            if self._receiver is not None:
                logger.debug("[FromBus] Disconnecting receiver from bus: %s on broker: %s", self.queue, self.broker)

                self._receiver.close()
                self._receiver = None

                logger.log(self._connection_log_level, "[FromBus] Disconnected receiver from bus: %s on broker: %s",
                             self.queue, self.broker)
        except Exception as ex:
            error_msg = "[FromBus] Disconnecting from queue %s at broker %s failed: %s" % (self.queue, self.broker, ex)
            logger.exception(error_msg)
            raise MessagingError(error_msg)

    def _is_connection_error(self, error: Exception) -> bool:
        if isinstance(error, TypeError):
            # special exception case for kombu not handling connection-loss very well...
            if str(error) == "'NoneType' object is not subscriptable":
                return True

        return super()._is_connection_error(error)

    def receive(self, timeout: float=DEFAULT_BUS_TIMEOUT, acknowledge: bool = True) -> Optional[LofarMessage]:
        """
        Receive the next message from the queue we're listening on.
        :param timeout: maximum time in seconds to wait for a message.
        :param acknowledge: if True, then automatically acknowledge the received message
        :return: received message, or None if timeout occurred.
        """
        if not self.is_connected:
            self.reconnect()

        kombu_msg = None
        start = datetime.utcnow()

        with self._lock.timeout_context(timeout=timeout) as have_lock:
            if not have_lock:
                return None

            while True:
                try:
                    elapsed_sec = (datetime.utcnow() - start).total_seconds()
                    if elapsed_sec > timeout:
                        raise MessagingTimeoutError("[FromBus] Timeout while trying to receive message from: %s" % (self.queue,))

                    kombu_msg = self._receiver.get(timeout=max(timeout-elapsed_sec, 0.001))
                    logger.debug("[FromBus] Message received on: %s mgs: %s" % (self.queue, kombu_msg))

                    # convert kombu msg to lofarmessage
                    lofar_msg = MessageFactory.create_lofar_message_from_kombu_message(kombu_msg)

                    # keep track of unacked messages
                    # the outside world only knows about lofar messages, so track them based on the lofar_message id.
                    # also keep track of thread id, because ack'ing/rejecting messages across threads is a bad idea!
                    self._unacked_messages[lofar_msg.id] = (kombu_msg, threading.current_thread().ident)

                    if acknowledge:
                        self.ack(lofar_msg)

                    return lofar_msg

                except kombu.exceptions.TimeoutError:
                    return None
                except EmptyQueueError:
                    return None
                except MessagingError:
                    # just reraise our own errors
                    raise
                except Exception as e:
                    if self._is_connection_error(e):
                        logger.warning("Could not receive message due to connection problems: %s", e)
                        self.reconnect()
                    else:
                        logger.exception(e)
                        if kombu_msg:
                            kombu_msg.reject()
                        raise MessagingError("[FromBus] unknown exception while receiving message on %s: %s" % (self.queue, e))

    def ack(self, lofar_msg: LofarMessage):
        """
        Acknowledge the message to the broker.
        :param lofar_msg: the message to be ack'ed
        """
        with self._lock:
            kombu_msg, thread_id = self._unacked_messages.get(lofar_msg.id, (None, None))

            if kombu_msg is None:
                raise KeyError("Cannot find kombu message to ack for lofar message_id %s. unacked_msg_ids=%s" % (lofar_msg.id,
                                                                                                                 list(self._unacked_messages.keys())))

            if threading.current_thread().ident != thread_id:
                raise MessagingRuntimeError("Cannot acknowledge messages across threads")

            try:
                kombu_msg.ack(multiple=False)
            except Exception as e:
                logger.exception(e)
                raise MessageBusError("Cannot ack msg with id=%s error:%s" % (lofar_msg.id, str(e)))
            else:
                logger.debug("%s acknowledged %s", self, lofar_msg)
                del self._unacked_messages[lofar_msg.id]

    def reject(self, lofar_msg: LofarMessage):
        """
        Reject the message to the broker.
        :param lofar_msg: the message to be rejected
        """
        with self._lock:
            kombu_msg, thread_id = self._unacked_messages.get(lofar_msg.id, (None, None))

            if kombu_msg is None:
                raise KeyError("Cannot find kombu message to reject for lofar message_id %s. unacked_msg_ids=%s" % (lofar_msg.id,
                                                                                                                    list(self._unacked_messages.keys())))

            if threading.current_thread().ident != thread_id:
                raise MessagingRuntimeError("Cannot reject messages across threads")

            try:
                kombu_msg.reject(requeue=False)
            except Exception as e:
                logger.exception(e)
                raise MessageBusError("Cannot reject msg with id=%s error:%s" % (lofar_msg.id, str(e)))
            else:
                logger.debug("%s rejected %s", self, lofar_msg)
                del self._unacked_messages[lofar_msg.id]

    def nr_of_messages_in_queue(self) -> int:
        """get the number of waiting messages in the queue"""
        return nr_of_messages_in_queue(self.queue, self.broker)

    def __str__(self):
        return "[FromBus] queue: %s on broker: %s (%s)" % (self.queue, self.broker, self.connection_name)


class ToBus(_AbstractBus):
    """
    A ToBus provides an easy way to send/publish messages to the message bus.
    The recommended way is to use a ToBus in a 'with' context, like so.

    >>> # use a TemporaryExchange where we can let the ToBus connect to
    ... with TemporaryExchange() as tmp_exchange:
    ...     # create a new ToBus, use it in a context.
    ...     with ToBus(exchange=tmp_exchange.address) as tobus:
    ...         print("connected =", tobus.is_connected)
    ...
    ...         # send a message to the exchange on the broker
    ...         tobus.send(EventMessage(content='foo'))
    ...
    ...     # left context, so is_connected should be false now.
    ...     print("connected =", tobus.is_connected)
    ...
    connected = True
    connected = False
    """

    def __init__(self, exchange: str=DEFAULT_BUSNAME, broker: str=DEFAULT_BROKER, connection_log_level=logging.DEBUG):
        """
        Constructor, specifying the address of the exchange to connect to on the given broker.
        :param exchange: the name of the exchange to connect to.
        :param broker: the valid broker url, like 'localhost'
        :param connection_log_level: optional logging level for opening/closing the connection (to add/reduce spamming)
        """
        self._sender = None
        self.exchange = exchange
        super(ToBus, self).__init__(broker=broker, connection_log_level=connection_log_level)

    def _connect_to_endpoint(self):
        """
        Implementation of abstract method. Connect a sender to the broker exchange specified by address.
        Can raise kombu/amqp exceptions, which are handled in the _AbstractBus.
        """
        try:
            logger.debug("[ToBus] Connecting sender to: %s on broker: %s", self.exchange, self.broker)

            # self._sender = self._connection.create_sender(address=self.address)
            self._sender = kombu.Producer(self._connection)

            logger.log(self._connection_log_level, "[ToBus] Connected sender to: %s on broker: %s", self.exchange, self.broker)
        except Exception as ex:
            error_msg = "[ToBus] Connecting to %s at broker %s failed: %s" % (self.exchange, self.broker, ex)
            if isinstance(ex, amqp.exceptions.NotFound) :
                # log "normal" known exceptions as error...
                logging.error(error_msg)
            else:
                # log other exceptions with stack trace...
                logging.exception(error_msg)

            # ... and finally raise a MessageBusError ourselves with a nice error message
            raise MessageBusError(error_msg)

    def _disconnect_from_endpoint(self):
        """
        Implementation of abstract method. Disconnect the sender from the broker exchange specified by address.
        Can raise kombu/amqp exceptions, which are handled in the _AbstractBus.
        """
        try:
            if self._sender is not None:
                logger.debug("[ToBus] Disconnecting sender from: %s on broker: %s" % (self.exchange, self.broker))
                self._sender.close()
                self._sender = None
                logger.log(self._connection_log_level, "[ToBus] Disconnected sender from: %s on broker: %s" % (self.exchange, self.broker))
        except Exception as ex:
            error_msg = "[FromBus] Disconnecting from queue %s at broker %s failed: %s" % (self.exchange, self.broker, ex)
            logger.exception(error_msg)
            raise MessagingError(error_msg)


    def send(self, message: LofarMessage, timeout: int=DEFAULT_BUS_TIMEOUT):
        """
        Send a message to the exchange we're connected to.
        :param message: message to be sent
        """
        start = datetime.utcnow()
        while True:
            try:
                logger.debug("[ToBus] Sending message to: %s (%s)", self.exchange, message)

                kwargs_dict = message.as_kombu_publish_kwargs()

                # every message is sent the connected exchange, and then routed to zero or more queues using the subject.
                kwargs_dict['exchange'] = self.exchange
                kwargs_dict['routing_key'] = message.subject

                with self._lock:
                    self._sender.publish(serializer='pickle', **kwargs_dict)

                logger.debug("[ToBus] Sent message to: %s", self.exchange)
                return
            except Exception as e:
                if self._is_connection_error(e):
                    logger.warning("Could not send message due to connection problems: %s", e)
                    self.reconnect()
                else:
                    raise MessagingError("[ToBus] Failed to send message to: %s error=%s" % (self.exchange, e))

            if datetime.utcnow() - start > timedelta(seconds=timeout):
                raise MessagingTimeoutError("[ToBus] Timeout while trying to send message to: %s" % (self.exchange,))

    def __str__(self):
        return "[ToBus] exchange: %s on broker: %s (%s)" % (self.exchange, self.broker, self.connection_name)

class TemporaryExchange:
    """
    A TemporaryExchange instance can be used to setup a dynamic temporary exchange which is closed and deleted automagically when leaving context.

    Particularly useful for testing, like so:
    >>> with TemporaryExchange("my.exchange") as tmp_exchange:
    ...     with tmp_exchange.create_tobus() as tobus:
    ...         tobus.send(EventMessage(subject="some.event", content="foo"))

    """
    def __init__(self, name_prefix: str=None, broker: str=DEFAULT_BROKER):
        """
        Create a TemporaryExchange instance with an optional name on the given broker.
        :param name_prefix: prefix for the final address which also includes a uuid.
        :param broker: the message broker to connect to.
        """
        self._name_prefix = name_prefix or ""
        self.broker = broker
        self._tmp_exchange = None
        self.address = None

    def __enter__(self):
        """
        Opens/creates the temporary exchange. It is automatically closed when leaving context in __exit__.
        :return: self.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close/remove the temporary exchange.
        """
        self.close()

    def open(self):
        """
        Open/create the temporary exchange.
        It is advised to use the TemporaryExchange instance in a 'with' context, which guarantees the close call.
        """
        # create an identifiable address based on the given name which is also (almost) unique, and readable.
        self.address = adaptNameToEnvironment("%stmp-exchange-%s" % (self._name_prefix+"-" if self._name_prefix else "",
                                                                     uuid.uuid4().hex[:8]))
        logger.debug("Creating TemporaryExchange at %s ...", self.address)
        create_exchange(name=self.address, broker=self.broker)
        logger.debug("Created TemporaryExchange at %s", self.address)

    def close(self):
        """
        Close/remove the temporary exchange.
        It is advised to use the TemporaryExchange instance in a 'with' context, which guarantees the close call.
        """
        logger.debug("Closing TemporaryExchange at %s", self.address)
        try:
            delete_exchange(self.address)
        except Exception as e:
            logger.error(e)
        logger.debug("Closed TemporaryExchange at %s", self.address)
        self.address = None

    def __str__(self):
        return "TemporaryExchange address=%s" % self.address

    def create_tobus(self) -> ToBus:
        """
        Factory method to create a ToBus instance which is connected to this TemporaryExchange
        :return: ToBus
        """
        return ToBus(broker=self.broker, exchange=self.address)

    def create_temporary_queue(self, auto_delete_on_last_disconnect: bool=True) -> 'TemporaryQueue':
        """
        Factory method to create a TemporaryQueue instance which is connected to this TemporaryExchange
        :param auto_delete_on_last_disconnect: If True auto-delete the queue on the broker when the last consumer disconnects.
        :return: TemporaryQueue
        """
        return TemporaryQueue(broker=self.broker, exchange=self.address, auto_delete_on_last_disconnect=auto_delete_on_last_disconnect)


class TemporaryQueue:
    """
    A TemporaryQueue instance can be used to setup a dynamic temporary queue which is closed and deleted automagically when leaving context.
    Together with the TemporaryExchange and factory methods create_frombus and/or create_tobus it gives us
    the following simple but often used use case:

    >>> with TemporaryExchange("my.exchange") as tmp_exchange:
    ...         with TemporaryQueue("my.queue", exchange=tmp_exchange.address, routing_key="some.#") as tmp_queue:
    ...             with tmp_queue.create_frombus() as frombus:
    ...                 msg = frombus.receive(0.1)
    ...                 print(msg)
    ...
    ...                 with tmp_exchange.create_tobus() as tobus:
    ...                     tobus.send(EventMessage(subject="some.event", content="foo"))
    ...                     tobus.send(EventMessage(subject="another.event", content="xyz"))
    ...                     tobus.send(EventMessage(subject="some.event", content="bar"))
    ...
    ...                 msg = frombus.receive(0.1)
    ...                 print(msg.content)
    ...                 msg = frombus.receive(0.1)
    ...                 print(msg.content)
    ...                 msg = frombus.receive(0.1)
    ...                 print(msg)
    None
    foo
    bar
    None

    Alternative use cases with only a tobus or only a frombus on the tmp_queue are also possible.
    Here's an example with two TemporaryQueues, each with their own address, and a ToBus sending messages to each queue directly.

    >>> with TemporaryExchange("my.exchange") as tmp_exchange:
    ...     with TemporaryQueue(exchange=tmp_exchange.address, addressed_to_me_only=True) as tmp_queue1, TemporaryQueue(exchange=tmp_exchange.address, addressed_to_me_only=True) as tmp_queue2:
    ...         with tmp_exchange.create_tobus() as tobus:
    ...             tobus.send(EventMessage(content='foo', subject=tmp_queue1.address))
    ...             tobus.send(EventMessage(content='bar', subject=tmp_queue2.address))
    ...
    ...         with tmp_queue1.create_frombus() as frombus:
    ...             msg = frombus.receive(0.1)
    ...             print(msg.content)
    ...
    ...         with tmp_queue2.create_frombus() as frombus:
    ...             msg = frombus.receive(0.1)
    ...             print(msg.content)
    foo
    bar

    """
    def __init__(self, name_prefix: str=None, exchange: str=None,
                 routing_key: str="#",
                 addressed_to_me_only: bool = False,
                 auto_delete_on_last_disconnect: bool=True,
                 broker=DEFAULT_BROKER):
        """
        Create a TemporaryQueue instance with an optional name on the given broker.
        :param name_prefix: Optional prefix for the final address which also includes a uuid.
        :param exchange: Optional exchange name to bind this queue to (with the given routing_key).
                              If the exchange does not exist it is created and deleted automagically.
        :param routing_key: Optional routing_key for binding this queue to the given exchange.
                            If "#" (the default), then route all messages to this queue.
                            This routing_key can be overruled by addressed_to_me_only.
        :param addressed_to_me_only: If True then apply the tmp-queue's address as binding routing key,
                                     so only messages for this queue are routed to this queue.
                                     This overrules the given routing_key parameter.
        :param auto_delete_on_last_disconnect: If True auto-delete the queue on the broker when the last consumer disconnects.
        :param broker: the messaging broker to connect to.
        """
        self._name_prefix = name_prefix
        self.broker = broker
        self._bound_exchange = exchange
        self._routing_key = routing_key
        self._addressed_to_me_only = addressed_to_me_only
        self._auto_delete_on_last_disconnect = auto_delete_on_last_disconnect
        self._created_exchange = False
        self.address = None

    def __enter__(self):
        """
        Opens/creates the temporary queue. It is automatically closed when leaving context in __exit__.
        :return: self.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close/remove the temporary queue.
        """
        self.close()

    def open(self):
        """
        Open/create the temporary queue.
        It is advised to use the TemporaryQueue instance in a 'with' context, which guarantees the close call.
        """
        # create an identifiable address based on the given name which is also (almost) unique, and readable.
        self.address = adaptNameToEnvironment("%stmp-queue-%s" % (self._name_prefix+"-" if self._name_prefix else "",
                                                                  uuid.uuid4().hex[:8]))
        logger.debug("Creating TemporaryQueue at %s ...", self.address)

        if not self._bound_exchange:
            # if there is no exhange to bind to,
            # then we create an exchange with the same name as the queue,
            # and route all messages from the exchange to the queue.
            # That's because messaging is designed to only publish messages to exchanges.
            self._bound_exchange = "exchange-for-" + self.address

        # create the tmp queue...
        create_queue(self.address, broker=self.broker, durable=False, auto_delete=self._auto_delete_on_last_disconnect)

        # create the exchange (if needed), and remember if we need to destroy it (if it was created)
        self._created_exchange = create_exchange(self._bound_exchange, broker=self.broker,
                                                 durable=False)

        # and finally create the binding
        # if no routing_key given, then use this tmp-queue's specific address as routing key
        create_binding(exchange=self._bound_exchange, queue=self.address,
                       routing_key=self.address if self._addressed_to_me_only else self._routing_key ,
                       broker=self.broker, durable=False)

        logger.debug("Created TemporaryQueue %s bound to exchange %s with routing_key %s",
                     self.address, self._bound_exchange, self._routing_key)


    def close(self):
        """
        Close/remove the temporary queue.
        It is advised to use the TemporaryQueue instance in a 'with' context, which guarantees the close call.
        """
        logger.debug("Closing TemporaryQueue at %s", self.address)
        try:
            delete_queue(self.address)
        except Exception as e:
            logger.error(e)
        try:
            if self._created_exchange:
                delete_exchange(self._bound_exchange)
        except Exception as e:
            logger.error(e)
        logger.debug("Closed TemporaryQueue at %s", self.address)
        self.address = None

    def __str__(self):
        return "TemporaryQueue address=%s bound to exchange=%s with routing_key=%s" % (
            self.address, self._bound_exchange, self._routing_key)

    def create_frombus(self) -> FromBus:
        """
        Convenience factory method to create a FromBus instance which is connected to this TemporaryQueue
        :return: FromBus
        """
        return FromBus(broker=self.broker, queue=self.address, connection_log_level=logging.DEBUG)

    def create_tobus(self) -> ToBus:
        """
        Convenience factory method to create a ToBus instance which is connected to the bound exchange of this TemporaryQueue if any.
        :return: ToBus
        """
        return ToBus(broker=self.broker, exchange=self._bound_exchange, connection_log_level=logging.DEBUG)

class AbstractMessageHandler:
    """
    The AbstractMessageHandler is the base class which defines the following message handling pattern:
        - the method start_handling is called at startup
        - in the loop, for each message these methods are called:
            - before_receive_message
            - handle_message
            - after_receive_message
       - finally the method stop_handling is called when the loop ends

    Only the handle_message method raises a NotImplementedError, and thus needs to be implemented in the subclass.
    The other four methods have empty bodies, so their default behaviour is no-op.

    Typical usage is to derive from this class and implement the handle_message method with concrete logic.
    """

    def before_receive_message(self):
        """Called in main processing loop just before a blocking receive for a message."""
        pass

    def handle_message(self, msg: LofarMessage):
        """Implement this method in your subclass to handle the received message
        Raise an exception if you want to reject the incoming message on the broker.
        :param msg: the received message to be handled
        """
        raise NotImplementedError("Please implement the handle_message method in your subclass to handle the received message")

    def after_receive_message(self):
        """Called in the main loop after the messages was handled.
        """
        pass

    def start_handling(self):
        """Called before main processing loop is entered.
        Typical usage for overriding this method is to create thread-bound connections to external resources like databases.
        """
        pass

    def stop_handling(self):
        """Called after main processing loop is finished."""
        pass

    def __enter__(self) -> 'AbstractMessageHandler':
        """enter the context, and start handling.
        :return self
        """
        try:
            self.start_handling()
        except Exception as e:
            logger.exception(e)
            self.stop_handling()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """leave the context, and stop handling."""
        self.stop_handling()

    def __str__(self):
        return self.__class__.__name__

    def is_empty_template_handler(self) -> bool:
        """
        Test method to introspect if this handler instance is a template handler with only empty bodies.
        Example: this is an empty template handler
        class BaseTemplateHandler(AbstractMessageHandler):
            def handle_message(self, msg: LofarMessage):
                if 'foo' in msg.subject:
                    self.on_foo()

            def on_foo(self):
                pass
        :return:
        """

        # introspection magic to get all methods called from within this handler's handle_message method.
        r1 = re.compile(r"self\.on(.)+\(.*\)")
        r2 = re.compile(r"\(.*")
        called_template_methods_from_handle_message = set([r2.sub("", l.strip().replace("self.","")) for l in inspect.getsource(self.handle_message).split('\n') if r1.search(l)])

        for method_name, member_func in inspect.getmembers(self, inspect.ismethod):
            if method_name in called_template_methods_from_handle_message:
                if not is_empty_function(member_func):
                    # this method is called from within the handler's handle_message method,
                    # but it's not empty, so return False.
                    # This means that we have at least one non-empty method being call from within this handler.
                    return False

        if len(called_template_methods_from_handle_message) == 0:
            # this handler does not call any methods from within handle_message, so it's not an empty-template-handler
            return False

        # There are methods being called from within the handler's handle_message method,
        # and they are all empty bodied, so return True
        return True


class UsingToBusMixin:
    """It is quite common to have a message handler which sends out messages itself. You would need a ToBus in your handler for that.
    For code re-use, we provide this mixin class with a self._tobus member, which is ready for use in your AbstractMessageHandler sub-class implementation.
    """
    def __init__(self):
        self._tobus = None

    def init_tobus(self, exchange: str=DEFAULT_BUSNAME, broker: str=DEFAULT_BROKER):
        """Init the self._tobus member and connect it to the given exchange on the given broker."""
        self._tobus = ToBus(exchange=exchange, broker=broker)

    @property
    def exchange(self):
        return self._tobus.exchange

    @property
    def broker(self):
        return self._tobus.broker

    def send(self, message: LofarMessage):
        """Send the given message via the internal ToBus"""
        self._tobus.send(message)

    def start_handling(self):
        """Start handling, and open the ToBus connection"""
        self._tobus.open()

    def stop_handling(self):
        """Stop handling, and close the ToBus connection"""
        self._tobus.close()

class BusListener:
    """
    The BusListener is the core class to connect to a given bus, listen for messages, and handle each messages upon arrival.
    The listening/handling is done on one or more background threads, so 'normal' program business logic can just go on in the foreground.
    The actual handling of the message is deferred to a conrete implementation of an AbstractMessageHandler, so typical usage
    is to derive from the AbstractMessageHandler class and implement the handle_message method with concrete logic, and
    inject that into the buslistener. (Dependency Injection or Inversion of Control design pattern)

    Here's a simple but concrete example:

    >>> # implement an example MyHandler which just prints the received message subject and content
    ... class MyHandler(AbstractMessageHandler):
    ...     def handle_message(self, lofar_msg):
    ...         print(lofar_msg.subject, lofar_msg.content)
    ...         # ... do some more fancy stuff with the msg...


    And here's how it's used (TemporaryExchange is used again to have an isolated test)
    >>> with TemporaryExchange("my.exchange") as tmp_exchange:
    ...     with tmp_exchange.create_tobus() as tobus:
    ...         listener_queue = None
    ...         try:
    ...             # construct a BusListener instance in a context,
    ...             # so it starts/stops listening and and handling messages automagically,
    ...             # and inject the MyHandler
    ...             with BusListener(handler_type=MyHandler, exchange=tmp_exchange.address, routing_key="some.#") as listener:
    ...                 listener_queue = listener.address
    ...                 tobus.send(EventMessage(subject="some.event", content="foo"))
    ...                 tobus.send(EventMessage(subject="another.event", content="xyz"))
    ...                 tobus.send(EventMessage(subject="some.event", content="bar"))
    ...
    ...                 # ... do some work ... simulate this by sleeping a little...
    ...                 # ...in the mean time, BusListener receives and handles the messages (on its own thread)
    ...                 from time import sleep
    ...                 sleep(0.25)
    ...         finally:
    ...             delete_queue(listener_queue)
    ...
    some.event foo
    some.event bar
    True

    There are 4 more methods to (possibly) override, which are all executed on the background thread(s)
    - start_handling and stop_handling which are typically used to setup connections to a database (one per thread, to make each connection thread-specific)
    - before_receive_message and after_receive_message which are called just before and after receiving a message.

    >>> # implement an example AbstractMessageHandler which just
    ... # collects message contents in a 'database' and
    ... # prints the all received message subject and content at the end.
    ... class MyDBConnectedHandler(AbstractMessageHandler):
    ...     def __init__(self, db_name, user, password):
    ...         self._db_name  = db_name
    ...         self._user     = user
    ...         self._password = password
    ...         print("Connecting to database %s with user %s" % (self._db_name, self._user))
    ...         self._db = {} # use dict as fake database for this example. You would normally connect to a real database here.
    ...
    ...     def stop_handling(self):
    ...         print(sorted(self._db.values())) # You would normally disconnect from a real database here.
    ...
    ...     def handle_message(self, lofar_msg):
    ...         # ... do some more fancy stuff with the msg, like storing it in the database
    ...         self._db[lofar_msg.id] = lofar_msg.content

    And here's how it's used (TemporaryExchange is used again to have an isolated test)
    >>> with TemporaryExchange("my.exchange") as tmp_exchange:
    ...     with tmp_exchange.create_tobus() as tobus:
    ...         listener_queue = None
    ...         try:
    ...             # construct a BusListener instance in a context,
    ...             # so it starts/stops listening and and handling messages automagically
    ...             with BusListener(handler_type=MyDBConnectedHandler,
    ...                              handler_kwargs={'db_name': 'my_db', 'user': 'my_user', 'password': 'my_password' },
    ...                              exchange=tmp_exchange.address, routing_key="some.#") as listener:
    ...                 listener_queue = listener.address
    ...                 tobus.send(EventMessage(subject="some.event", content="foo"))
    ...                 tobus.send(EventMessage(subject="another.event", content="xyz"))
    ...                 tobus.send(EventMessage(subject="some.event", content="bar"))
    ...
    ...                 # ... do some work ... simulate this by sleeping a little...
    ...                 # ...in the mean time, BusListener receives and handles the messages (on its own thread)
    ...                 from time import sleep
    ...                 sleep(0.25)
    ...         finally:
    ...             delete_queue(listener_queue)
    Connecting to database my_db with user my_user
    ['bar', 'foo']
    True
    """

    def __init__(self, handler_type: AbstractMessageHandler.__class__,
                 handler_kwargs: dict = None,
                 exchange: str = None, routing_key: str = "#",
                 num_threads: int = 1,
                 broker: str = DEFAULT_BROKER):
        """
        Create a buslistener instance.

        Specify an exchange and routing_key. Then this buslistener creates a designated queue on the broker,
        specifically for this listener with the following constructed name: <exchange>.for.<program_name>.<routing_key>
        The designated queue is bound to the given exchange with the given routing_key.

        The rational behind this is that:
         - this saves a lot of 'infrastructure' (queue/binding) configuration on the broker.
         - the designated queues are named in a consistent way.
         - the designated queues only receive messages this listener is interested in.
         - monitoring tools (like the RabbitMQ web interface) can see what programs (or services within programs) are consuming messages, and at what rate.

        We intentionally do not remove the queue and binding upon closing this listener,
        so messages are stored/kept on the broker in the queue for this listener for later processing once the program and this listener restarts.

        If you realy would like to have automatic cleanup of the created queue (for example in tests),
        then use this buslistener in a BusListenerJanitor's context.

        :param handler_type: TODO!!!!!!!!
        :param handler_kwargs: TODO!!!!!!!!
        :param exchange: Bind the listener to this given exchange with the given routing key via an auto-generated designated queue.
        :param routing_key: Bind the listener to this given exchange with the given routing key via an auto-generated designated queue.
        :param num_threads: the number of receiver/handler threads.
                            default=1, use higher number only if it makes sense, for example when you are
                            waiting for a slow database while handling the message.
        :param broker: a message broker address
        :raises: MessagingError if the exchange could not be created
        """

        if not isinstance(handler_type, type):
            raise TypeError("handler_type should be a AbstractMessageHandler subclass, not an instance!")

        if not issubclass(handler_type, AbstractMessageHandler):
            raise TypeError("handler_type should be a AbstractMessageHandler subclass")

        self._handler_type    = handler_type
        self._handler_kwargs  = dict(handler_kwargs) if handler_kwargs else {}
        self.exchange         = exchange
        self.broker           = broker
        self._num_threads     = num_threads
        self._threads         = {}
        self._lock            = threading.Lock()
        self._running         = threading.Event()
        self._listening       = False
        self.routing_key      = routing_key
        self.address          = self.designated_queue_name()

        # make sure the queue is bound to the exchange
        # any created queue or binding is not removed on exit. See rational above.
        create_bound_queue(exchange=exchange, queue=self.address, routing_key=routing_key,
                           broker=self.broker, log_level=logging.INFO)

    def designated_queue_name(self) -> str:
        """
        create a designated queue name based on this buslistener's exchange name, routing_key, and the current running program name.
        Like so: <exchange>.for.<program_name>.<listener_type_name>.on.<sanitzed_routing_key>
        In case the routing_key filters for wildcards only, then the routing key is replaced by 'all'
        :return: <exchange>.for.<program_name>.<listener_type_name>.on.<sanitzed_routing_key>
        """
        sanitized_routing_key = self.routing_key.replace(".#","").replace(".*","").replace("#","").replace("*","")
        if not sanitized_routing_key:
            sanitized_routing_key = "all"
        return "%s.queue.for.%s.%s.on.%s" % (self.exchange,
                                          program_name(include_extension=False),
                                          self.__class__.__name__,
                                          sanitized_routing_key)

    def is_running(self) -> bool:
        """Is this listener running its background listen/handle loops?"""
        return self._running.isSet()

    def is_listening(self) -> bool:
        """Is this listener listening?"""
        return self._listening

    def start_listening(self):
        """
        Start the background threads and process incoming messages.
        """
        if self._listening:
            return

        self._listening = True
        self._running.set()
        for i in range(self._num_threads):
            thread_name = "ListenerThread_%s_%d" % (self.address, i)
            thread_started_event = threading.Event()
            thread = threading.Thread(target=self._listen_loop,
                                      name=thread_name,
                                      kwargs={'thread_started_event':thread_started_event})
            with self._lock:
                self._threads[thread] = {} # bookkeeping dict per thread
            thread.start()

            # check if the _listen_loop was started successfully
            logger.debug("waiting for thread %s to be running...", thread_name)
            if not (thread_started_event.wait(timeout=10) and thread.is_alive()):
                msg = "Could not fully start listener thread: %s" % (thread_name,)
                logger.error(msg)
                raise MessagingRuntimeError(msg)
            logger.debug("thread %s is running", thread_name)

    def stop_listening(self):
        """
        Stop the background threads that listen to incoming messages.
        """
        # stop all running threads
        if not self._listening:
            return

        self._listening = False

        if self.is_running():
            self._running.clear()

            for thread in list(self._threads.keys()):
                try:
                    logger.debug("STOPPING %s on thread '%s'", self, thread.name)
                    thread.join()
                    with self._lock:
                        del self._threads[thread]
                    logger.info("STOPPED %s on thread '%s'", self, thread.name)
                except Exception as e:
                    logger.exception("Could not stop thread %s: %s", thread.name, e)

    def __enter__(self) -> 'BusListener':
        """enter the context, and make the bus_listener start listening.
        :return self
        """
        try:
            self.start_listening()
            return self
        except Exception as e:
            # __exit__ (and hence stop_listening) is not called when an exception is raised in __enter__
            # so, do our own cleanup (log, stop_listening and re-raise).
            logger.exception("%s error: %s",  self, e)
            self.stop_listening()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """leave the context, and make the bus_listener stop listening.
        :return self
        """
        self.stop_listening()

    def __str__(self):
        return "%s using handler '%s' listening on queue '%s' at broker '%s'" % (self.__class__.__name__,
                                                                                 self._handler_type.__name__,
                                                                                 self.address,
                                                                                 self.broker)

    def _create_handler(self):
        handler_instance = self._handler_type(**self._handler_kwargs)
        try:
            # try to silently init the tobus if this is an AbstractMessageHandlerWithToBus instance (ducktyping)
            handler_instance.init_tobus(self.exchange, self.broker)
        except AttributeError:
            pass

        if handler_instance.is_empty_template_handler():
            error_msg = "%s is an empty template handler, so no concrete handler methods will be called. Please provide a concrete implementation." % (self._handler_type.__name__,)
            logger.error(error_msg)
            raise TypeError(error_msg)

        return handler_instance

    def _listen_loop(self, thread_started_event: threading.Event):
        """
        Internal use only. Message listener loop that receives messages and starts the attached function with the message content as argument.
        """
        current_thread = threading.currentThread()
        # dict for thread specific bookkeeping
        thread_bookkeeping = self._threads[current_thread]

        logger.debug( "STARTING %s on thread '%s' ", self, current_thread.name)

        # create an instance of the given handler for this background thread
        # (to keep the internals of the handler thread agnostic)
        with self._create_handler() as thread_handler:
            with FromBus(self.address, broker=self.broker) as receiver:
                logger.info("STARTED %s on thread '%s' ", self, current_thread.name)

                with self._lock:
                    thread_bookkeeping['handler'] = thread_handler
                    thread_bookkeeping['receiver'] = receiver

                # notify the thread starter that we successfully started the listen loop
                thread_started_event.set()

                # keep running and handling ....
                while self.is_running():
                    try:
                        thread_handler.before_receive_message()
                    except Exception as e:
                        logger.exception("before_receive_message() failed: %s", e)
                        pass

                    try:
                        # get the next message
                        lofar_msg = receiver.receive(1, acknowledge=False)
                        # retry loop if timed-out
                        if lofar_msg is None:
                            continue

                        # Execute the handler function
                        try:
                            thread_handler.handle_message(lofar_msg)
                        except Exception as e:
                            logger.exception("Handling of %s failed. Rejecting message. Error: %s", lofar_msg, e)
                            receiver.reject(lofar_msg)
                        else:
                            # handle_message was successful, so ack the msg.
                            receiver.ack(lofar_msg)

                        try:
                            thread_handler.after_receive_message()
                        except Exception as e:
                            logger.exception("after_receive_message() failed: %s", e)

                    except MessagingError as me:
                        # just log any own MessagingError, and continue loop.
                        logger.error(me)

                        if not receiver.is_connected:
                            receiver.reconnect()

                    except Exception as e:
                        # Unknown problem in the library. Report this and continue.
                        logger.exception("[%s:] ERROR during processing of incoming message: %s", self.__class__.__name__, e)


class BusListenerJanitor:
    """The BusListenerJanitor cleans up auto-generated consumer queues.
       It is intended specifically for use in a 'with' context in a test, or short-lived use-case.

       Typical example:
        >>> # implement an example AbstractMessageHandler which just prints the received message subject and content
        ... class MyMessageHandler(AbstractMessageHandler):
        ...     def handle_message(self, lofar_msg):
        ...         print(lofar_msg.subject, lofar_msg.content)
        ...         # ... do some more fancy stuff with the msg...

        And here's how it's used together with the BusListenerJanitor.
        >>> with TemporaryExchange("my.exchange") as tmp_exchange:
        ...     with tmp_exchange.create_tobus() as tobus:
        ...         # construct a BusListener instance in a BusListenerJanitor's context,
        ...         # so it starts/stops listening and and handling messages automagically
        ...         # and the auto-generated queue is also cleaned up after leaving context
        ...         with BusListenerJanitor(BusListener(MyMessageHandler, exchange=tmp_exchange.address, routing_key="some.#")):
        ...             tobus.send(EventMessage(subject="some.event", content="foo"))
        ...             tobus.send(EventMessage(subject="another.event", content="xyz"))
        ...             tobus.send(EventMessage(subject="some.event", content="bar"))
        ...
        ...             # ... do some work ... simulate this by sleeping a little...
        ...             # ...in the mean time, BusListener receives and handles the messages (on its own thread)
        ...             from time import sleep
        ...             sleep(0.25)
        ...
        some.event foo
        some.event bar
       """
    def __init__(self, bus_listener: BusListener):
        """Create a janitor for the given bus_listener"""
        self._bus_listener = bus_listener

    def __enter__(self) -> BusListener:
        """enter the context, and make the bus_listener start listening.
        :return a reference to the buslistener, not to the janitor!"""
        try:
            self.open()
            return self._bus_listener
        except Exception as e:
            logger.exception(e)
            self.close()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """leave the context, make the bus_listener stop listening,
        and clean up the auto-generated queue"""
        self.close()

    def open(self):
        """make the bus_listener start listening."""
        self._bus_listener.start_listening()

    def close(self):
        """make the bus_listener stop listening, and delete listener queue"""
        try:
            bus_listener_address = self._bus_listener.address
            self._bus_listener.stop_listening()
        finally:
            logger.info("BusListenerJanitor deleting auto-generated queue: %s", bus_listener_address)
            delete_queue(bus_listener_address)


# do not expose create/delete_queue/exchange etc methods in all, it's not part of the public API
__all__ = ['DEFAULT_BUS_TIMEOUT', 'FromBus', 'ToBus', 'BusListener', 'BusListenerJanitor',
           'TemporaryQueue', 'TemporaryExchange', 'AbstractMessageHandler', 'UsingToBusMixin',
           'nr_of_messages_in_queue', 'can_connect_to_broker']

if __name__ == "__main__":
    # run the doctests in this module
    import doctest
    doctest.testmod(verbose=True, report=True)
