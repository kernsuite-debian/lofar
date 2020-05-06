#!/usr/bin/env python3

import unittest
from unittest import mock
from random import randint
from pysimplesoap.client import SoapClient
from time import sleep

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

from lofar.messaging.messagebus import TemporaryExchange, TemporaryQueue, BusListenerJanitor
from lofar.messaging.messages import EventMessage
from lofar.lta.ingest.common.job import createJobXml
from lofar.lta.ingest.common.config import INGEST_NOTIFICATION_PREFIX

from lofar.common.dbcredentials import Credentials

class TestIngestMoMAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp_exchange = TemporaryExchange("t_ingestmomadapter")
        self.tmp_exchange.open()
        self.addCleanup(self.tmp_exchange.close)


    def test_onXmlRPCJobReceived_no_soap(self):
        """test the handler routine onXmlRPCJobReceived to check if a job_xml is converted to a message and send on the correct bus"""
        from lofar.lta.ingest.server.ingestmomadapter import MoMXMLRPCHandler

        with MoMXMLRPCHandler(exchange=self.tmp_exchange.address,
                              mom_xmlrpc_host='localhost',
                              mom_xmlrpc_port=randint(2345, 4567)) as handler:

            # create a tmp job receiver queue
            with TemporaryQueue(exchange=self.tmp_exchange.address) as tmp_job_queue:
                with tmp_job_queue.create_frombus() as job_receiver:

                    # create a job...
                    job_xml = createJobXml('project', 0, 1, 'dp_id', 2, '/tmp/path/to/dataproduct')

                    # and let it be handled by the handler (as if it was received via xml-rpc)
                    handler.onXmlRPCJobReceived('my_job_file.xml', job_xml)

                    # there should now be a job on the tmp_job_queue
                    # receive and check it.
                    job_msg = job_receiver.receive()
                    self.assertEqual(job_xml, job_msg.content)

    def test_mom_soap_to_job_queue(self):
        """assuming test_onXmlRPCJobReceived_no_soap passes, test the correct behaviour when called via soap xml-rpc"""

        from lofar.lta.ingest.server.ingestmomadapter import MoMXMLRPCHandler
        with MoMXMLRPCHandler(exchange=self.tmp_exchange.address,
                              mom_xmlrpc_host='localhost',
                              mom_xmlrpc_port=randint(2345, 4567)) as handler:
            # create a tmp job receiver queue
            with TemporaryQueue(exchange=self.tmp_exchange.address) as tmp_job_queue:
                with tmp_job_queue.create_frombus() as job_receiver:
                    # create a job...
                    job_xml = createJobXml('project', 0, 1, 'dp_id', 2, '/tmp/path/to/dataproduct')

                    # submit the job like MoM would via xml-rpc
                    soap_client = SoapClient(location=handler.server_url(), namespace="urn:pipeline.export")
                    soap_client.new_job(fileName='my_job_file.xml', fileContent=job_xml)

                    # there should now be a job on the tmp_job_queue
                    # receive and check it.
                    job_msg = job_receiver.receive()
                    self.assertEqual(job_xml, job_msg.content)

    @unittest.skip("TODO: fix test, and make it more usefull.")
    def test_ingest_bus_listener_for_mom_adapter(self):
        with mock.patch('lofar.lta.ingest.server.momclient.MoMClient', autospec=True) as momclient_patcher:

            # import IngestBusListenerForMomAdapter here, because otherwise the MoMClient won't be mocked
            from lofar.lta.ingest.server.ingestmomadapter import IngestBusListenerForMomAdapter

            # start the IngestBusListenerForMomAdapter in a BusListenerJanitor so the auto-generated queues are auto deleted.
            with BusListenerJanitor(IngestBusListenerForMomAdapter(Credentials(), self.tmp_exchange.address)) as listener:
                with self.tmp_exchange.create_tobus() as tobus:
                    tobus.send(EventMessage(subject="%s.JobStarted" % INGEST_NOTIFICATION_PREFIX,
                                            content={'type': 'MoM',
                                                     'job_id': 9876543321,
                                                     'message': "The job started!"}))
                    sleep(1)
                    momclient_patcher.login.assert_called()
                    momclient_patcher.logout.assert_called()


if __name__ == '__main__':
    unittest.main()
