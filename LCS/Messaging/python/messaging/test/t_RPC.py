#!/usr/bin/env python3
"""
Program to test the RPCClient and RPCService class of the Messaging package.
"""

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(message)s', level=logging.DEBUG)

import unittest
import uuid
from time import sleep

from lofar.messaging.messagebus import TemporaryExchange, can_connect_to_broker, exchange_exists, queue_exists, BusListenerJanitor
from lofar.messaging.rpc import RPCClient, RPCService, RPCException, RPCTimeoutException, ServiceMessageHandler

TEST_SERVICE_NAME = "%s.%s" % (__name__, uuid.uuid4())

class MyServiceMessageHandler(ServiceMessageHandler):
    def __init__(self, my_arg1, my_arg2):
        super().__init__()
        self.my_arg1 = my_arg1
        self.my_arg2 = my_arg2

    def my_public_method1(self):
        return self.my_arg1

    def my_public_method2(self, parameter1):
        return (self.my_arg2, parameter1)

    def my_public_failing_method(self):
        raise Exception("intentional test exception")

    def my_public_slow_method(self):
        sleep(2)


class RPCServiceTests(unittest.TestCase):
    def test_designated_queue_name_contains_subclass_name(self):
        class MyService(RPCService):
            pass

        with TemporaryExchange(self.__class__.__name__) as tmp_exchange:
            service = MyService("my service", MyServiceMessageHandler, exchange=tmp_exchange.address)
            queue_name = service.designated_queue_name()

            self.assertTrue(".MyService." in queue_name)
            self.assertFalse(".BusListener." in queue_name)


class TestRPC(unittest.TestCase):
    def test_registered_service_methods(self):
        handler = MyServiceMessageHandler("foo", "bar")
        handler.register_public_handler_methods()
        self.assertEqual(4, len(handler._subject_to_method_map))
        self.assertTrue('my_public_method1' in handler._subject_to_method_map)
        self.assertTrue('my_public_method2' in handler._subject_to_method_map)
        self.assertTrue('my_public_failing_method' in handler._subject_to_method_map)
        self.assertTrue('my_public_slow_method' in handler._subject_to_method_map)

    def test_rpc_client_to_service_call(self):
        with TemporaryExchange(__name__) as tmp_exchange:
            tmp_exchange_address = tmp_exchange.address
            with BusListenerJanitor(RPCService(TEST_SERVICE_NAME,
                            handler_type=MyServiceMessageHandler,
                            handler_kwargs={'my_arg1': "foo",
                                            'my_arg2': "bar"},
                            exchange=tmp_exchange.address,
                            num_threads=1)) as service:
                service_queue_address = service.address
                self.assertTrue(service.is_listening())
                self.assertTrue(service.is_running())

                with RPCClient(service_name=TEST_SERVICE_NAME, exchange=tmp_exchange.address, timeout=1) as rpc_client:
                    self.assertEqual("foo", rpc_client.execute("my_public_method1"))
                    self.assertEqual(("bar", 42), rpc_client.execute("my_public_method2", 42))

                    with self.assertRaises(RPCException):
                        rpc_client.execute("my_public_failing_method")

                    with self.assertRaises(TimeoutError):
                        rpc_client.execute("my_public_slow_method")

                    with self.assertRaises(RPCTimeoutException):
                        rpc_client.execute("my_public_slow_method")

        self.assertFalse(queue_exists(service_queue_address))
        self.assertFalse(exchange_exists(tmp_exchange_address))

if __name__ == '__main__':
    if not can_connect_to_broker():
        logger.error("Cannot connect to default rabbitmq broker. Skipping test.")
        exit(3)

    unittest.main()
