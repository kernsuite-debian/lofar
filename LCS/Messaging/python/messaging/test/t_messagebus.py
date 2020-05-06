# t_messagebus.py: Test program for the module lofar.messaging.messagebus
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
# $Id: t_messagebus.py 1580 2015-09-30 14:18:57Z loose $

"""
Test program for the module lofar.messaging.messagebus
"""

import uuid
import unittest
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(thread)d %(threadName)s %(levelname)s %(message)s', level=logging.DEBUG)

from datetime import datetime

from lofar.messaging.messages import *
from lofar.messaging.messagebus import *
from lofar.messaging.messagebus import _AbstractBus, can_connect_to_broker
from lofar.messaging.messagebus import create_queue, create_exchange, create_binding, create_bound_queue, delete_exchange, delete_queue, exchange_exists, queue_exists
from lofar.messaging.config import DEFAULT_USER, DEFAULT_PASSWORD
from lofar.messaging.rpc import RequestMessage
from lofar.messaging.exceptions import MessageBusError, MessagingRuntimeError, MessagingTimeoutError
from lofar.common.datetimeutils import round_to_millisecond_precision
from time import sleep
from threading import Lock, Event as ThreadingEvent

TIMEOUT = 1.0

class TestCreateDeleteFunctions(unittest.TestCase):
    """Test the various create/delete exchange/queue/binding funcions"""

    def test_create_delete_exchange(self):
        name = "test-exchange-%s" % (uuid.uuid4())

        self.assertFalse(exchange_exists(name))

        # creating this new unique test exchange should succeed, and return True cause it's a new exchange
        self.assertTrue(create_exchange(name, durable=False))

        self.assertTrue(exchange_exists(name))

        # creating it again should return False
        self.assertFalse(create_exchange(name, durable=False))

        # deleting it should succeed
        self.assertTrue(delete_exchange(name))

        self.assertFalse(exchange_exists(name))

        # deleting it again should return False as there is nothing to deleting
        self.assertFalse(delete_exchange(name))

    def test_create_delete_queue(self):
        name = "test-queue-%s" % (uuid.uuid4())

        self.assertFalse(queue_exists(name))

        # creating this new unique test queue should succeed, and return True cause it's a new queue
        self.assertTrue(create_queue(name, durable=False))

        self.assertTrue(queue_exists(name))

        # creating it again should return False
        self.assertFalse(create_queue(name, durable=False))

        # deleting it should succeed
        self.assertTrue(delete_queue(name))

        self.assertFalse(queue_exists(name))

        # deleting it again should return False as there is nothing to deleting
        self.assertFalse(delete_queue(name))

    def test_create_binding(self):
        exchange = "test-exchange-%s" % (uuid.uuid4())
        queue = "test-queue-%s" % (uuid.uuid4())

        # try to create the binding on non-existing exchange/queue
        with self.assertRaisesRegex(MessageBusError, ".*does not exist.*"):
            create_binding(exchange=exchange, queue=queue)

        try:
            # now, do make sure the exchange/queue exist
            create_exchange(exchange)
            create_queue(queue)

            # and do the actual binding test
            self.assertTrue(create_binding(exchange=exchange, queue=queue))
        finally:
            # and cleanup the exchange/queue
            delete_queue(queue)
            delete_exchange(exchange)




class TestTemporaryExchangeAndQueue(unittest.TestCase):
    """Test the TemporaryExchange and TemporaryQueue classes"""

    def test_temporary_exchange_is_really_temporary(self):
        """
        test if the temporary exchange is really removed after usage
        """
        tmp_exchange_address = None
        with TemporaryExchange("MyTestExchange") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            self.assertTrue("MyTestExchange" in tmp_exchange_address)

        self.assertFalse(exchange_exists(tmp_exchange_address))

        # test if the temporary exchange has been deleted when leaving scope
        # We should not be able to connect to it anymore
        with self.assertRaisesRegex(MessageBusError, '.*NOT_FOUND.*'):
            with FromBus(tmp_exchange_address):
                pass

    def test_temporary_queue_is_really_temporary(self):
        """
        test if the temporary queue is really removed after usage
        """
        tmp_queue_address = None
        with TemporaryQueue("MyTestQueue") as tmp_queue:
            tmp_queue_address = tmp_queue.address
            self.assertTrue("MyTestQueue" in tmp_queue_address)

        self.assertFalse(queue_exists(tmp_queue_address))

        # test if the temporary queue has been deleted when leaving scope
        # We should not be able to connect to it anymore
        with self.assertRaisesRegex(MessageBusError, '.*NOT_FOUND.*'):
            with FromBus(tmp_queue_address):
                pass

    def test_send_receive_over_temporary_exchange_and_queue(self):
        """
        test the usage of the TemporaryExchange and TemporaryQueue in conjunction with normal ToBus and Frombus usage
        """
        with TemporaryExchange("MyTestExchange") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            # create a normal ToBus on this tmp_exchange
            with tmp_exchange.create_tobus() as tobus_on_exchange:
                # create a TemporaryQueue, bound to the tmp_exchange
                with TemporaryQueue("MyTestQueue", exchange=tmp_exchange.address) as tmp_queue:
                    tmp_queue_address = tmp_queue.address
                    # create a normal FromBus on this tmp_queue
                    with tmp_queue.create_frombus() as frombus:
                        # and let's see if the tmp_queue can also create a tobus which then points to the bound_exchange
                        with tmp_queue.create_tobus() as tobus_on_tmp_queue:

                            self.assertEqual(tobus_on_exchange.exchange, tobus_on_tmp_queue.exchange)

                            # test sending a message to both "types" of tobuses.
                            for tobus in [tobus_on_exchange, tobus_on_tmp_queue]:
                                # send a message...
                                original_msg = EventMessage(content="foobar")
                                tobus.send(original_msg)

                                # ...receive the message...
                                received_msg = frombus.receive()
                                self.assertIsNotNone(received_msg)

                                # and test if they are equal
                                self.assertEqual(original_msg.id, received_msg.id)
                                self.assertEqual(original_msg.content, received_msg.content)

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(tmp_queue_address))

    def test_send_receive_over_temporary_queue_with_subject_filtering(self):
        """
        test the usage of the TemporaryQueue in conjunction with normal ToBus and Frombus usage with additional filtering on subject
        """
        SUBJECT = "FooBarSubject"
        SUBJECT2 = "FAKE_SUBJECT"

        with TemporaryQueue("MyTestQueue", routing_key=SUBJECT) as tmp_queue:
            tmp_queue_address = tmp_queue.address
            # create a normal To/FromBus on this tmp_queue
            NUM_MESSAGES_TO_SEND = 3
            with tmp_queue.create_tobus() as tobus:
                # create a FromBus, which listens for/receives only the messages with the given SUBJECT
                with tmp_queue.create_frombus() as frombus:
                    for i in range(NUM_MESSAGES_TO_SEND):
                        # send a message...
                        original_msg = EventMessage(subject=SUBJECT,
                                                    content="test message %d with subject='%s'" % (i, SUBJECT))
                        logger.info("Sending message: %s", original_msg)
                        tobus.send(original_msg)

                        # ...receive the message...
                        received_msg = frombus.receive(timeout=0.1)
                        logger.info("received message: %s", received_msg)

                        # and test if they are equal
                        self.assertEqual(original_msg.id, received_msg.id)
                        self.assertEqual(original_msg.content, received_msg.content)
                        self.assertEqual(original_msg.subject, received_msg.subject)

                        # now send a message with a different subject...
                        original_msg = EventMessage(subject=SUBJECT2, content="foobar")
                        logger.info("Sending message: %s", original_msg)
                        tobus.send(original_msg)

                        # ... and try to receive it (should yield None, because of the non-matching subject)
                        received_msg = frombus.receive(timeout=0.1)
                        logger.info("received message: %s", received_msg)
                        self.assertEqual(None, received_msg)

        self.assertFalse(queue_exists(tmp_queue_address))

    def test_send_receive_over_temporary_exchange_with_queue_with_subject_filtering(self):
        """
        test the usage of the TemporaryQueue in conjunction with normal ToBus and Frombus usage with additional filtering on subject
        """
        SUBJECT = "FooBarSubject"
        SUBJECT2 = "FAKE_SUBJECT"
        NUM_MESSAGES_TO_SEND = 3
        with TemporaryExchange("MyTestExchange") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            with tmp_exchange.create_tobus() as tobus:
                # create a TemporaryQueue, which listens for/receives only the messages with the given SUBJECT
                with TemporaryQueue("MyTestQueue", exchange=tmp_exchange.address, routing_key=SUBJECT) as tmp_queue:
                    tmp_queue_address = tmp_queue.address
                    with tmp_queue.create_frombus() as frombus:
                        for i in range(NUM_MESSAGES_TO_SEND):
                            # send a message...
                            original_msg = EventMessage(subject=SUBJECT,
                                                        content="test message %d with subject='%s'" % (
                                                        i, SUBJECT))
                            logger.info("Sending message: %s", original_msg)
                            tobus.send(original_msg)

                            # ...receive the message...
                            received_msg = frombus.receive(timeout=0.1)
                            logger.info("received message: %s", received_msg)

                            # and test if they are equal
                            self.assertEqual(original_msg.id, received_msg.id)
                            self.assertEqual(original_msg.content, received_msg.content)
                            self.assertEqual(original_msg.subject, received_msg.subject)

                            # now send a message with a different subject...
                            original_msg = EventMessage(subject=SUBJECT2, content="foobar")
                            logger.info("Sending message: %s", original_msg)
                            tobus.send(original_msg)

                            # ... and try to receive it (should yield None, because of the non-matching subject)
                            received_msg = frombus.receive(timeout=0.1)
                            logger.info("received message: %s", received_msg)
                            self.assertEqual(None, received_msg)

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(tmp_queue_address))

    def test_send_receive_over_temporary_exchange_with_multiple_bound_queues_with_subject_filtering(
            self):
        """
        test the usage of the TemporaryQueue in conjunction with normal ToBus and Frombus usage with additional filtering on subject
        """
        with TemporaryExchange("MyTestExchange") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            with tmp_exchange.create_tobus() as tobus:
                SUBJECT1 = "FooBarSubject"
                SUBJECT2 = "FAKE_SUBJECT"
                with TemporaryQueue("MyTestQueue", exchange=tmp_exchange.address, routing_key=SUBJECT1) as tmp_queue1, \
                     TemporaryQueue("MyTestQueue", exchange=tmp_exchange.address, routing_key=SUBJECT2) as tmp_queue2:
                    tmp_queue1_address = tmp_queue1.address
                    tmp_queue2_address = tmp_queue2.address
                    # create a normal To/FromBus on this tmp_queue
                    NUM_MESSAGES_TO_SEND = 3

                    # create two FromBus'es, which listen for/receive only the messages with their routing_key
                    with tmp_queue1.create_frombus() as frombus1, tmp_queue2.create_frombus() as frombus2:
                        for i in range(NUM_MESSAGES_TO_SEND):
                            # send a message...
                            original_msg = EventMessage(subject=SUBJECT1,
                                                        content="test message %d with subject='%s'" % (
                                                            i, SUBJECT1))
                            logger.info("Sending message: %s", original_msg)
                            tobus.send(original_msg)

                            # ...receive the message...
                            received_msg1 = frombus1.receive(timeout=0.1)
                            received_msg2 = frombus2.receive(timeout=0.1)
                            self.assertIsNotNone(received_msg1)
                            self.assertIsNone(received_msg2)
                            logger.info("received message: %s", received_msg1)

                            # and test if they are equal
                            self.assertEqual(original_msg.id, received_msg1.id)
                            self.assertEqual(original_msg.content, received_msg1.content)
                            self.assertEqual(original_msg.subject, received_msg1.subject)

                            # now send a message with a different subject...
                            original_msg = EventMessage(subject=SUBJECT2, content="foobar")
                            logger.info("Sending message: %s", original_msg)
                            tobus.send(original_msg)

                            # ... and try to receive it
                            received_msg1 = frombus1.receive(timeout=0.1)
                            received_msg2 = frombus2.receive(timeout=0.1)
                            self.assertIsNone(received_msg1)
                            self.assertIsNotNone(received_msg2)
                            logger.info("received message: %s", received_msg2)

                            # and test if they are equal
                            self.assertEqual(original_msg.id, received_msg2.id)
                            self.assertEqual(original_msg.content, received_msg2.content)
                            self.assertEqual(original_msg.subject, received_msg2.subject)

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(tmp_queue1_address))
        self.assertFalse(queue_exists(tmp_queue2_address))

# ========  FromBus unit tests  ======== #

class FromBusInitFailed(unittest.TestCase):
    """
    Class to test initialization failures of FromBus
    """

    def setUp(self):
        self.test_queue = TemporaryQueue(__class__.__name__)
        self.test_queue.open()

    def tearDown(self):
        tmp_queue_address = self.test_queue.address
        self.test_queue.close()
        self.assertFalse(queue_exists(tmp_queue_address))

    def test_no_broker_address(self):
        """
        Connecting to non-existent broker address must raise MessageBusError
        """
        with self.assertRaisesRegex(MessageBusError, ".*failed to resolve broker hostname"):
            with FromBus(self.test_queue.address, broker="foo.bar"):
                pass

    def test_connection_refused(self):
        """
        Connecting to broker on wrong port must raise MessageBusError
        """
        with self.assertRaisesRegex(MessageBusError, ".*failed to resolve broker hostname"):
            with FromBus("fake" + self.test_queue.address, broker="localhost:4"):
                pass


class FromBusInContext(unittest.TestCase):
    """
    Class to test FromBus when inside context.
    """

    def setUp(self):
        self.test_queue = TemporaryQueue(__class__.__name__)
        self.test_queue.open()

    def tearDown(self):
        tmp_queue_address = self.test_queue.address
        self.test_queue.close()
        self.assertFalse(queue_exists(tmp_queue_address))

    def test_receiver_exists(self):
        with FromBus(self.test_queue.address) as frombus:
            self.assertTrue(frombus._receiver is not None)

    def test_connect_fails(self):
        random_non_existing_address = str(uuid.uuid4())

        with self.assertRaisesRegex(MessageBusError, ".*failed*"):
            with FromBus(random_non_existing_address) as frombus:
                self.assertTrue(frombus._receiver is not None)

    def test_receive_timeout(self):
        """
        Getting a message when there's none must yield None after timeout.
        """
        with FromBus(self.test_queue.address) as frombus:
            self.assertIsNone(frombus.receive(timeout=TIMEOUT))


# ========  ToBus unit tests  ======== #

class ToBusInitFailed(unittest.TestCase):
    """
    Class to test initialization failures of ToBus
    """

    def setUp(self):
        self.test_exchange = TemporaryExchange(__class__.__name__)
        self.test_exchange.open()

    def tearDown(self):
        tmp_exchange_address = self.test_exchange.address
        self.test_exchange.close()
        self.assertFalse(exchange_exists(tmp_exchange_address))

    def test_no_broker_address(self):
        """
        Connecting to non-existent broker address must raise MessageBusError
        """
        with self.assertRaisesRegex(MessageBusError, ".*failed to resolve broker hostname"):
            with ToBus(self.test_exchange.address, broker="foo.bar"):
                pass

    def test_connection_refused(self):
        """
        Connecting to broker on wrong port must raise MessageBusError
        """
        with self.assertRaisesRegex(MessageBusError, ".*failed to resolve broker hostname"):
            with ToBus(self.test_exchange.address, broker="localhost:4"):
                pass


class SendReceiveMessage(unittest.TestCase):
    """
    Class to test sending and receiving a message.
    """

    def setUp(self):
        self.test_exchange = TemporaryExchange(__class__.__name__)
        self.test_exchange.open()

        self.test_queue = TemporaryQueue(__class__.__name__, exchange=self.test_exchange.address)
        self.test_queue.open()

        self.frombus = self.test_queue.create_frombus()
        self.tobus = self.test_exchange.create_tobus()

    def tearDown(self):
        tmp_queue_address = self.test_queue.address
        self.test_queue.close()
        self.assertFalse(queue_exists(tmp_queue_address))

        tmp_exchange_address = self.test_exchange.address
        self.test_exchange.close()
        self.assertFalse(exchange_exists(tmp_exchange_address))

    def _test_sendrecv(self, send_msg):
        """
        Helper class that implements the send/receive logic and message checks.
        :param send_msg: Message to send
        :return the received message
        """
        with self.tobus, self.frombus:
            self.tobus.send(send_msg)
            recv_msg = self.frombus.receive(timeout=TIMEOUT)

        self.assertEqual(type(send_msg), type(recv_msg))
        self.assertEqual(send_msg.id, recv_msg.id)
        self.assertEqual(send_msg.subject, recv_msg.subject)
        self.assertEqual(send_msg.content, recv_msg.content)
        return recv_msg

    def test_sendrecv_event_message(self):
        """
        Test send/receive of an EventMessage, containing a string.
        """
        content = "An event message"
        self._test_sendrecv(EventMessage(content))

    def test_sendrecv_request_message(self):
        """
        Test send/receive of an RequestMessage, containing a byte array.
        """
        self._test_sendrecv(RequestMessage(subject="my_request",  reply_to=self.test_queue.address).with_args_kwargs(
                                           request="Do Something", argument="Very Often"))

    def test_sendrecv_request_message_with_large_content_map(self):
        """
        Test send/receive of an RequestMessage, containing a dict with a large string value.
        Qpid, cannot (de)serialize strings > 64k in a dict
        We circumvent this in ToBus.send and FromBus.receive by converting long strings in a dict to a buffer and back.
        """
        self._test_sendrecv(RequestMessage(subject="my_request",  reply_to=self.test_queue.address).with_args_kwargs(
                                           key1="short message", key2="long message " + (2 ** 17) * 'a'))

    def test_sendrecv_request_message_with_datetime_in_dict(self):
        """
        Test send/receive of an RequestMessage, containing a datetime in the dict.
        """
        self._test_sendrecv(RequestMessage(subject="my_request", reply_to=self.test_queue.address).with_args_kwargs(
                                           starttime=round_to_millisecond_precision(datetime.utcnow())))

    def test_sendrecv_request_message_with_datetime_in_list(self):
        """
        Test send/receive of an RequestMessage, containing a datetime in the list.
        """
        my_list = [round_to_millisecond_precision(datetime.utcnow()),round_to_millisecond_precision(datetime.utcnow())]
        self._test_sendrecv(RequestMessage(subject="my_request", reply_to=self.test_queue.address).with_args_kwargs(
                                           my_list=my_list))

    def test_sendrecv_request_message_with_large_string(self):
        """
        Test send/receive of an RequestMessage, containing a large string
        """
        large = ((2**16)+1)*'a' # test if the messages can handle a string with more than 2^16 chars which is aparently a probly for some brokers of messaging libs.
                                  # so, we need a large enough string, but not too big to overload the broker buffers when running multiple tests at the same time

        self._test_sendrecv(RequestMessage(subject="my_request", reply_to=self.test_queue.address).with_args_kwargs(
                                           my_string=large))

    def test_sendrecv_request_message_with_nested_dicts_and_lists_with_special_types(self):
        """
        Test send/receive of an RequestMessage, containing a datetimes in nested dicts/lists.
        """
        content = {'foo': [ {'timestamp1': round_to_millisecond_precision(datetime.utcnow()),
                             'timestamp2': round_to_millisecond_precision(datetime.utcnow()),
                             'foo': 'bar'},
                            {},
                            {'abc':[round_to_millisecond_precision(datetime.utcnow()), round_to_millisecond_precision(datetime.utcnow())]},
                            {'a': 'b',
                             'c': { 'timestamp': round_to_millisecond_precision(datetime.utcnow())}}],
                   'bar': [],
                   'large_string': ((2**16)+1)*'a' # test if the messages can handle a string with more than 2^16 chars which is aparently a probly for some brokers of messaging libs.
                                                   # so, we need a large enough string, but not too big to overload the broker buffers when running multiple tests at the same time
                   }
        self._test_sendrecv(RequestMessage(subject="my_request", reply_to=self.test_queue.address).with_args_kwargs(**content))

    def test_sendrecv_request_message_with_int_keys(self):
        """
        Test send/receive of an RequestMessage, containing int's as keys
        """
        my_dict = { 0: 'foo',
                    1: 'bar' }
        recv_msg = self._test_sendrecv(RequestMessage(subject="my_request",  reply_to=self.test_queue.address).with_args_kwargs(
                                                      my_dict=my_dict))
        self.assertEqual(my_dict, recv_msg.content['kwargs']['my_dict'])

class PriorityTest(unittest.TestCase):
    def test_priority(self):
        with TemporaryExchange(self.__class__.__name__) as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            with tmp_exchange.create_temporary_queue() as tmp_queue:
                tmp_queue_address = tmp_queue.address
                msg1 = EventMessage(priority=4, subject="some.event", content=1)
                msg2 = EventMessage(priority=5, subject="some.event", content=2)

                with tmp_exchange.create_tobus() as tobus:
                    tobus.send(msg1)
                    tobus.send(msg2)

                with tmp_queue.create_frombus() as frombus:
                    result_msg1 = frombus.receive()
                    result_msg2 = frombus.receive()

                    # message with highest priority should arrive first
                    self.assertEqual(msg1.id, result_msg2.id)
                    self.assertEqual(msg2.id, result_msg1.id)

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(tmp_queue_address))

class Rejector(BusListener):
    handled_messages = 0

    class Handler(AbstractMessageHandler):
        def __init__(self, rejector):
            self.rejector = rejector


        def handle_message(self, msg: LofarMessage):
            self.rejector.handled_messages += 1
            raise Exception("Intentional exception to reject message")

    def __init__(self, exchange):
        super(Rejector, self).__init__(handler_type=Rejector.Handler,
                                       handler_kwargs={"rejector": self},
                                       exchange=exchange,
                                       routing_key="spam")


class RejectorTester(unittest.TestCase):
    def test_reject_should_result_in_empty_queue(self):
        number_of_messages = 1000

        with TemporaryExchange("Rejection") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            with BusListenerJanitor(Rejector(tmp_exchange.address)) as rejector:
                rejector_address = rejector.designated_queue_name()
                with tmp_exchange.create_tobus() as spammer:
                    for _ in range(number_of_messages):
                        msg = EventMessage(content="ping", subject="spam")
                        spammer.send(msg)

                while rejector.handled_messages < number_of_messages:
                    logger.info("Handled messages: {}".format(rejector.handled_messages))
                    sleep(1)

                with FromBus(rejector.address) as frombus:
                    logger.info("Number of messages on queue: {}".format(frombus.nr_of_messages_in_queue()))
                    self.assertEqual(0, frombus.nr_of_messages_in_queue())

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(rejector_address))



class PingPongPlayer(BusListener):
    """
    Helper class with a simple purpose:
        - listen on one queue,
        - when receiving a message, send answer on exchange, flipping message contents between ping and pong.

    This is NOT the intended way of using the BusListener and AbstractMessageHandler... This weird construct is
    used to test the multi-threaded BusListener's behaviour, and tests if the underlying messaging lib can cope with multithreading.
    """

    class Handler(AbstractMessageHandler):
        def __init__(self, player, opponent_name):
            self.player = player
            self.opponent_name = opponent_name

        def handle_message(self, msg):
            """Implementation of BusListener.handle_message
            log received message, and send a response message to the pingpong_table_exchange where it will be routed to the opponent's queue,
            flipping ping for pong and vice versa
            """
            logger.info("%s: received %s on %s", self.player.name, msg.content, self.player.address)

            response_msg = EventMessage(content="ping" if msg.content == "pong" else "pong",
                                        subject=self.opponent_name)

            logger.info("%s: sending %s to %s", self.player.name, response_msg.content, self.player.response_bus.exchange)

            # do not lock around the player's response_bus to test internal thread safety
            self.player.response_bus.send(response_msg)

            with self.player.lock: # do lock 'normal' assignement of variables
                self.player.num_turns += 1

            return True


    def __init__(self, name, opponent_name, pingpong_table_exchange, num_threads):
        self.name = name
        self.opponent_name = opponent_name
        self.num_turns = 0
        self.response_bus = ToBus(pingpong_table_exchange)
        self.lock = Lock() # a lock to keep track of self.num_turns in a multithreaded environment
        super(PingPongPlayer, self).__init__(handler_type=PingPongPlayer.Handler,
                                             handler_kwargs={'player': self, 'opponent_name': opponent_name},
                                             exchange=pingpong_table_exchange,
                                             routing_key=self.name,
                                             num_threads=num_threads)

    def start_listening(self):
        self.response_bus.open()
        super(PingPongPlayer, self).start_listening()

    def stop_listening(self):
        super(PingPongPlayer, self).stop_listening()
        self.response_bus.close()

    def get_num_turns(self):
        with self.lock:
            return self.num_turns

class PingPongTester(unittest.TestCase):
    """Test an event driven message ping/pong game, where two 'players' respond to each other.
    This test should work regardless of the number of threads the each 'player'/BusListener uses"""

    def test_single_thread_per_player(self):
        self._play(1)

    def test_two_threads_per_player(self):
        self._play(2)

    def test_ten_threads_per_player(self):
        self._play(10)

    def _play(self, num_threads_per_player):
        """simulate a ping/pong event driven loop until each player played a given amount of turns, or timeout"""

        # game parameters
        NUM_TURNS = 10
        GAME_TIMEOUT = 10

        # setup temporary exchange, on which the player can publish their messages (ping/pong balls)
        with TemporaryExchange("PingPongTable") as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address

            # create two players, on "both sides of the table"
            # i.e.: they each play on the tmp_exchange, but have the auto-generated designated listen queues for incoming balls
            with BusListenerJanitor(PingPongPlayer("Player1", "Player2", tmp_exchange.address, num_threads_per_player)) as player1:
                player1_address = player1.address
                with BusListenerJanitor(PingPongPlayer("Player2", "Player1", tmp_exchange.address, num_threads_per_player)) as player2:
                    player2_address = player2.address
                    start_timestamp = datetime.utcnow()

                    # first serve, referee throws a ping ball on the table in the direction of player1
                    with tmp_exchange.create_tobus() as referee:
                        first_msg = EventMessage(content="ping", subject="Player1")
                        logger.info("first message: sending %s to %s", first_msg.content, tmp_exchange.address)
                        referee.send(first_msg)

                    # play the game!
                    # run the "event loop". Actually there are multiple loops: num_threads per player
                    # this loop just tracks game progress.
                    while True:
                        player1_num_turns = player1.get_num_turns()
                        player2_num_turns = player2.get_num_turns()
                        time_remaining = GAME_TIMEOUT - (datetime.utcnow() - start_timestamp).total_seconds()

                        logger.info("PingPongTester STATUS: player1_num_turns=%d/%d player2_num_turns=%d/%d time_remaining=%.1fsec",
                                    player1_num_turns, NUM_TURNS, player2_num_turns, NUM_TURNS, time_remaining)

                        # assert on deadlocked game (should never happen!)
                        self.assertGreater(time_remaining, 0)

                        if player1_num_turns >= NUM_TURNS and player2_num_turns >= NUM_TURNS :
                            break

                        sleep(0.1)

                    # assert on players who did not finish the game
                    self.assertGreaterEqual(player1.get_num_turns(), NUM_TURNS)
                    self.assertGreaterEqual(player2.get_num_turns(), NUM_TURNS)

                    logger.info("SUCCESS! player1_num_turns=%d/%d player2_num_turns=%d/%d num_threads_per_player=%d #msg_per_sec=%.1f",
                                player1_num_turns, NUM_TURNS, player2_num_turns, NUM_TURNS,
                                num_threads_per_player, 2*NUM_TURNS/(datetime.utcnow() - start_timestamp).total_seconds())

        self.assertFalse(exchange_exists(tmp_exchange_address))
        self.assertFalse(queue_exists(player1_address))
        self.assertFalse(queue_exists(player2_address))

class BusListenerTests(unittest.TestCase):
    def test_designated_queue_name_contains_subclass_name(self):
        class MyListener(BusListener):
            pass

        with TemporaryExchange(self.__class__.__name__) as tmp_exchange:
            listener = MyListener(AbstractMessageHandler, exchange=tmp_exchange.address)
            queue_name = listener.designated_queue_name()

            self.assertTrue(".MyListener." in queue_name)
            self.assertFalse(".BusListener." in queue_name)


class MessageHandlerTester(unittest.TestCase):
    def test_handler_init_raises(self):
        # define a MessageHandler that raises on init
        class RaisingHandler(AbstractMessageHandler):
            def __init__(self):
                raise Exception("intentional test exception")

        # try to start a BusListener using this handler. Should fail and raise a MessagingRuntimeError
        with TemporaryExchange(self.__class__.__name__) as tmp_exchange:
            tmp_exchange_name = tmp_exchange.address
            listener = BusListener(handler_type=RaisingHandler, exchange=tmp_exchange_name)
            with self.assertRaises(MessagingRuntimeError):
                with BusListenerJanitor(listener):
                    pass

        self.assertFalse(exchange_exists(tmp_exchange_name))
        self.assertFalse(queue_exists(listener.designated_queue_name()))

    def test_empty_template_handler(self):
        # define a MessageHandler with a template for callback on<something> methods
        class BaseTemplateHandler(AbstractMessageHandler):
            def handle_message(self, msg: LofarMessage):
                if 'foo' in msg.subject:
                    self.on_foo()
                if 'bar' in msg.subject:
                    self.on_bar(msg.content)

            def on_foo(self):
                pass

            def on_bar(self, some_arg):
                pass

        self.assertTrue(BaseTemplateHandler().is_empty_template_handler())

        class ConcreteHandler1(BaseTemplateHandler):
            def on_foo(self):
                return 42

        self.assertFalse(ConcreteHandler1().is_empty_template_handler())

        class ConcreteHandler2(BaseTemplateHandler):
            def on_bar(self, some_arg):
                if some_arg:
                    return 3.14
                return 2.71

        self.assertFalse(ConcreteHandler2().is_empty_template_handler())

        class SimpleNonTemplateHandler(AbstractMessageHandler):
            def handle_message(self, msg: LofarMessage):
                if 'foo' in msg.subject:
                    return 42
                elif 'bar' in msg.subject:
                    if msg.content:
                        return 3.14
                    return 2.71

        self.assertFalse(SimpleNonTemplateHandler().is_empty_template_handler())


    def test_empty_template_handler_raises(self):
        # define a MessageHandler with a template for callback on<something> methods
        class BaseTemplateHandler(AbstractMessageHandler):
            def handle_message(self, msg: LofarMessage):
                if 'foo' in msg.subject:
                    self.on_foo()
                if 'bar' in msg.subject:
                    self.on_bar(msg.content)

            def on_foo(self):
                pass

            def on_bar(self, some_arg):
                pass

        # try to start a BusListener using a BaseTemplateHandler. Should fail and raise a TypeError
        with TemporaryExchange(self.__class__.__name__) as tmp_exchange:
            tmp_exchange_name = tmp_exchange.address
            listener = BusListener(handler_type=BaseTemplateHandler, exchange=tmp_exchange_name)
            with self.assertRaises(RuntimeError):
                with BusListenerJanitor(listener):
                    pass

        self.assertFalse(exchange_exists(tmp_exchange_name))
        self.assertFalse(queue_exists(listener.designated_queue_name()))


class ReconnectOnConnectionLossTests(unittest.TestCase):
    def setUp(self):
        self.tmp_exchange = TemporaryExchange()
        self.tmp_queue = self.tmp_exchange.create_temporary_queue()

        self.tmp_exchange.open()
        self.tmp_queue.open()

    def tearDown(self):
        tmp_queue_address = self.tmp_queue.address
        self.tmp_queue.close()
        self.assertFalse(queue_exists(tmp_queue_address))

        tmp_exchange_address = self.tmp_exchange.address
        self.tmp_exchange.close()
        self.assertFalse(exchange_exists(tmp_exchange_address))

    def _can_connect_to_rabbitmq_admin_site(self, hostname: str):
        try:
            url = 'http://%s:15672/api' % (hostname,)
            return requests.get(url, auth=(DEFAULT_USER, DEFAULT_PASSWORD)).status_code in [200, 202]
        except requests.ConnectionError:
            return False

    def _close_connection_of_bus_on_broker(self, bus: _AbstractBus):
        if not self._can_connect_to_rabbitmq_admin_site(bus.broker):
            raise unittest.SkipTest("Cannot connect tot RabbitMQ admin server to close connection %s" % (bus.connection_name))

        # use the http REST API using request to forcefully close the connection on the broker-side
        url = "http://%s:15672/api/connections/%s" % (bus.broker, bus.connection_name)

        # rabbitmq http api is sometimes lagging a bit behind...
        # wait until the connection url responds with 200-ok.
        while True:
            response = requests.get(url, auth=(DEFAULT_USER, DEFAULT_PASSWORD))
            if response.status_code == 200:
                break
            sleep(0.25)

        # now we can delete it.
        response = requests.delete(url, auth=(DEFAULT_USER, DEFAULT_PASSWORD))
        self.assertEqual(204, response.status_code)

    def test_tobus_send_handling_connection_loss(self):
        with ToBus(self.tmp_exchange.address) as tobus:
            tobus.send(EventMessage())

            # force server-side connection loss
            self._close_connection_of_bus_on_broker(tobus)

            # try to send with timeout of 0 (so there is no opportunity for reconnection) ->  MessagingTimeoutError
            with self.assertRaises(MessagingTimeoutError):
                tobus.send(EventMessage(), timeout=0)

            # send with normal timeout, should just succeed (and not raise)
            tobus.send(EventMessage(), timeout=5)

    def test_frombus_send_handling_connection_loss(self):
        with ToBus(self.tmp_exchange.address) as tobus:
            with self.tmp_exchange.create_temporary_queue(auto_delete_on_last_disconnect=False) as tmp_queue:
                with tmp_queue.create_frombus() as frombus:
                    # test normal send/receive -> should work
                    tobus.send(EventMessage())
                    self.assertIsNotNone(frombus.receive())

                    # force server-side connection loss for the receiving frombus connection
                    self._close_connection_of_bus_on_broker(frombus)

                    # test normal send/receive -> should work
                    tobus.send(EventMessage())
                    self.assertIsNotNone(frombus.receive())


    def test_buslistener_handling_connection_loss(self):
        msg_handled_event = ThreadingEvent()

        class SynchonizingHandler(AbstractMessageHandler):
            def handle_message(self, msg: LofarMessage):
                logger.info("handle_message(%s) ... setting msg_handled_event", msg)
                msg_handled_event.set()

        with BusListenerJanitor(BusListener(handler_type=SynchonizingHandler,
                                            exchange=self.tmp_exchange.address)) as listener:
            with ToBus(self.tmp_exchange.address) as tobus:
                # send test message
                tobus.send(EventMessage())

                # wait until mesage is handled...
                self.assertTrue(msg_handled_event.wait(2))
                msg_handled_event.clear()

                # magic lookup of the listeners receiver...
                frombus = list(listener._threads.values())[0]['receiver']
                # ... to force server-side connection loss
                self._close_connection_of_bus_on_broker(frombus)

                # send another test message...
                tobus.send(EventMessage())

                # listener should have handled the 2ns msg as well, even though the connection was broken
                # thanks to auto reconnect
                self.assertTrue(msg_handled_event.wait(2))


def load_tests(loader, tests, ignore):
    """add the doctests from lofar.messaging.messagebus to the unittest tests"""
    import doctest
    import lofar.messaging.messagebus
    tests.addTests(doctest.DocTestSuite(lofar.messaging.messagebus))
    return tests


if __name__ == '__main__':
    if not can_connect_to_broker():
        logger.error("Cannot connect to default rabbitmq broker. Skipping test.")
        exit(3)

    unittest.main()

