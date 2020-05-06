##!/usr/bin/env python3

## Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
## P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
##
## This file is part of the LOFAR software suite.
## The LOFAR software suite is free software: you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## The LOFAR software suite is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along
## with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

#import unittest
#from unittest import mock
#import uuid
#from threading import Event
#import shutil
#import os
#from datetime import datetime

#import logging
#logger = logging.getLogger(__name__)

#from lofar.qa.service.qa_service import QAService
#from lofar.qa.service.QABusListener import *
#from lofar.qa.hdf5_io import *
#from lofar.messaging.messagebus import TemporaryExchange, BusListenerJanitor
#from lofar.messaging.messages import EventMessage
#from lofar.sas.otdb.config import DEFAULT_OTDB_NOTIFICATION_SUBJECT
#from lofar.common.test_utils import unit_test, integration_test

## the tests below test is multi threaded (even multi process)
## define a SynchronizationQABusListener-derivative to handle synchronization (set the *_events)
#class SynchronizationQABusListener(QABusListener):
    #class SynchronizationQAEventMessageHandler(QAEventMessageHandler):
        #def __init__(self, listener):
            #super().__init__()
            #self.listener = listener

        #def onConvertedMS2Hdf5(self, msg_content):
            #self.listener.converted_msg_content = msg_content
            #self.listener.converted_event.set()

        #def onCreatedInspectionPlots(self, msg_content):
            #self.listener.plotted_msg_content = msg_content
            #self.listener.plotted_event.set()

        #def onFinished(self, msg_content):
            #self.listener.finished_msg_content = msg_content
            #self.listener.finished_event.set()

        #def onClustered(self, msg_content):
            #self.listener.clustered_msg_content = msg_content
            #self.listener.clustered_event.set()

        #def onError(self, msg_content):
            #self.listener.error_msg_content = msg_content
            #self.listener.error_event.set()

    #'''
    #the tests below test are multi threaded (even multi process)
    #this QABusListener-derivative handles synchronization (set the *_events)
    #and stores the msg_content results for expected result checking
    #'''
    #def __init__(self, exchange):
        #super().__init__(handler_type=SynchronizationQABusListener.SynchronizationQAEventMessageHandler,
                         #handler_kwargs={'listener':self},
                         #exchange=exchange)
        #self.converted_event = Event()
        #self.clustered_event = Event()
        #self.plotted_event = Event()
        #self.finished_event = Event()
        #self.error_event = Event()


#@integration_test
#class TestQAService(unittest.TestCase):
    #'''
    #Tests for the QAService class
    #'''
    #def setUp(self):
        #'''
        #quite complicated setup to setup test message-exchanges/queues
        #and mock away ssh calls to cep4
        #and mock away dockerized commands
        #'''
        #self.TEST_UUID = uuid.uuid1()
        #self.TEST_OTDB_ID = 999999

        #self.tmp_exchange = TemporaryExchange("%s_%s" % (__class__.__name__, self.TEST_UUID))
        #self.tmp_exchange.open()
        #self.addCleanup(self.tmp_exchange.close)

        ## where to store the test results
        #self.TEST_DIR = '/tmp/qa_service_%s' % self.TEST_UUID
        #self.TEST_H5_FILE = 'L%s.MS_extract.h5' % (self.TEST_OTDB_ID,)
        #self.TEST_H5_PATH = os.path.join(self.TEST_DIR, 'ms_extract', self.TEST_H5_FILE)

        ## mock the calls to ssh cep4 and docker
        #def mocked_wrap_command_for_docker(cmd, image_name=None, image_label=None):
            #logger.info('mocked_wrap_command_for_docker returning original command: %s', ' '.join(cmd))
            #return cmd

        #def mocked_wrap_command_in_cep4_head_node_ssh_call(cmd):
            #logger.info('mocked_wrap_command_in_cep4_head_node_ssh_call returning original command: %s', ' '.join(cmd))
            #return cmd

        #def mocked_wrap_command_in_cep4_node_ssh_call(cmd, cpu_node_nr, partition, via_head):
            #logger.info('mocked_wrap_command_in_cep4_node_ssh_call for %s node nr %s via head=%s ' \
                        #'returning original command: %s', partition, cpu_node_nr, via_head, ' '.join(cmd))
            #return cmd

        #def mocked_get_cep4_available_nodes(partition):
            #logger.info('mocked_get_cep4_available_cpu_nodes for returning just node nr 1')
            #return [1]

        #def mocked_otdbrpc_taskGetSpecification(otdb_id):
            #logger.info('mocked_otdbrpc_taskGetSpecification')
            #return {'specification': {'ObsSW.Observation.processType': 'Observation',
                                      #'ObsSW.Observation.DataProducts.Output_Correlated.enabled': True }}

        ## we need to patch the wrap_command_in_cep4_head_node_ssh_call function from module lofar.qa.service.qa_service,
        ## because that's were it's imported and used.
        ## (and not the original lofar.common.cep4_utils.wrap_command_for_docker)
        #wrap_command_for_docker_patcher = mock.patch('lofar.qa.service.qa_service.wrap_command_for_docker')
        #self.addCleanup(wrap_command_for_docker_patcher.stop)
        #self.wrap_command_for_docker_mock = wrap_command_for_docker_patcher.start()
        #self.wrap_command_for_docker_mock.side_effect = mocked_wrap_command_for_docker

        #wrap_command_in_cep4_head_node_ssh_call_patcher = mock.patch('lofar.qa.service.qa_service.wrap_command_in_cep4_head_node_ssh_call')
        #self.addCleanup(wrap_command_in_cep4_head_node_ssh_call_patcher.stop)
        #self.wrap_command_in_cep4_head_node_ssh_call_mock = wrap_command_in_cep4_head_node_ssh_call_patcher.start()
        #self.wrap_command_in_cep4_head_node_ssh_call_mock.side_effect = mocked_wrap_command_in_cep4_head_node_ssh_call

        #wrap_command_in_cep4_node_ssh_call_patcher = mock.patch('lofar.common.cep4_utils.wrap_command_in_cep4_node_ssh_call')
        #self.addCleanup(wrap_command_in_cep4_node_ssh_call_patcher.stop)
        #self.wrap_command_in_cep4_node_ssh_call_mock = wrap_command_in_cep4_node_ssh_call_patcher.start()
        #self.wrap_command_in_cep4_node_ssh_call_mock.side_effect = mocked_wrap_command_in_cep4_node_ssh_call

        #get_cep4_available_cpu_nodes_patcher = mock.patch('lofar.common.cep4_utils.get_cep4_available_nodes')
        #self.addCleanup(get_cep4_available_cpu_nodes_patcher.stop)
        #self.get_cep4_available_cpu_nodes_mock = get_cep4_available_cpu_nodes_patcher.start()
        #self.get_cep4_available_cpu_nodes_mock.side_effect = mocked_get_cep4_available_nodes

        #otdbrpc_taskGetSpecification_patcher = mock.patch('lofar.sas.otdb.otdbrpc.OTDBRPC.taskGetSpecification')
        #self.addCleanup(otdbrpc_taskGetSpecification_patcher.stop)
        #self.otdbrpc_taskGetSpecification_mock = otdbrpc_taskGetSpecification_patcher.start()
        #self.otdbrpc_taskGetSpecification_mock.side_effect = mocked_otdbrpc_taskGetSpecification

        ## mock the ssh_cmd_list function, and check in each test if it was NOT called,
        ## because that is what we are trying to prevent by mocking the other methods.
        ## So, in principle it should not be needed to mock it,
        ## but when there is some error in the code/test/mock we would like to prevent
        ## an accidental ssh call to cep4
        #def mocked_ssh_cmd_list(host, user='lofarsys'):
            #raise AssertionError("ssh_cmd_list should not be called!")

        #ssh_cmd_list_patcher1 = mock.patch('lofar.common.ssh_utils.ssh_cmd_list')
        #self.addCleanup(ssh_cmd_list_patcher1.stop)
        #self.ssh_cmd_list_mock1 = ssh_cmd_list_patcher1.start()
        #self.ssh_cmd_list_mock1.side_effect = mocked_ssh_cmd_list

        #ssh_cmd_list_patcher2 = mock.patch('lofar.common.cep4_utils.ssh_cmd_list')
        #self.addCleanup(ssh_cmd_list_patcher2.stop)
        #self.ssh_cmd_list_mock2 = ssh_cmd_list_patcher2.start()
        #self.ssh_cmd_list_mock2.side_effect = mocked_ssh_cmd_list

    #def tearDown(self):
        #logger.info('removing test dir: %s', self.TEST_DIR)
        #shutil.rmtree(self.TEST_DIR, ignore_errors=True)

    #def send_otdb_task_completing_event(self):
        #'''helper method: create a ToBus and send a completing EventMessage'''
        #with self.tmp_exchange.create_tobus() as sender:
            #msg = EventMessage(subject=DEFAULT_OTDB_NOTIFICATION_SUBJECT,
                               #content={"treeID": self.TEST_OTDB_ID,
                                        #"state": 'completing',
                                        #"time_of_change": datetime.utcnow()})
            #sender.send(msg)

    #@integration_test
    #def test_01_qa_service_for_expected_behaviour(self):
        #'''
        #This test starts a QAService, triggers a test observation completing event,
        #and tests if the generated h5 file and plots are as expected.
        #It is an end-to-end test which does not check the intermediate results. It is assumed that
        #the intermediate steps are tested in other tests/modules.
        #'''

        #logger.info(' -- test_01_qa_service_for_expected_behaviour -- ')

        ## override the mock behaviour from setUp for this specific test
        #def mocked_wrap_command_for_docker(cmd, image_name=None, image_label=None):
            ## replace the ms2hdf5 command which runs normally in the docker container
            ## by a call to the create_test_hypercube which fakes the ms2hdf5 conversion for this test.
            #if 'ms2hdf5' in cmd:
                ## the create_test_hypercube executable should be available in the PATH environment
                #create_test_hypercube_path = 'create_test_hypercube'

                #mocked_cmd = [create_test_hypercube_path, '-s 4', '-S 8', '-t 16',
                              #'-o', str(self.TEST_OTDB_ID), self.TEST_H5_PATH]
                #logger.info('''mocked_wrap_command_for_docker returning mocked command to create test h5 file: '%s', instead of original command: '%s' ''',
                            #' '.join(mocked_cmd), ' '.join(cmd))
                #return mocked_cmd

            #if 'cluster_this.py' in cmd:
                ## replace the cluster command which runs normally in the docker container
                ## by a call to bash true, so the 'cluster_this' call returns 0 exit code
                #mocked_cmd = ['true']
                #logger.info('''mocked_wrap_command_for_docker returning mocked command: '%s', instead of original command: '%s' ''',
                            #' '.join(mocked_cmd), ' '.join(cmd))
                #return mocked_cmd

            ##TODO: merge adder branch into trunk so we can use plot_hdf5_dynamic_spectra on the test-h5 file to create plots
            #if 'plot_hdf5_dynamic_spectra' in cmd:
                ## replace the plot_hdf5_dynamic_spectra command which runs normally in the docker container
                ## by a call to bash true, so the 'plot_hdf5_dynamic_spectra' call returns 0 exit code
                #mocked_cmd = ['true']
                #logger.info('''mocked_wrap_command_for_docker returning mocked command: '%s', instead of original command: '%s' ''',
                            #' '.join(mocked_cmd), ' '.join(cmd))
                #return mocked_cmd

            #logger.info('''mocked_wrap_command_for_docker returning original command: '%s' ''', ' '.join(cmd))
            #return cmd

        #self.wrap_command_for_docker_mock.side_effect = mocked_wrap_command_for_docker

        ## start the QAService (the object under test)
        #qaservice = QAService(exchange=self.tmp_exchange.address, qa_base_dir=self.TEST_DIR)
        #with qaservice, BusListenerJanitor(qaservice.filtering_buslistener), BusListenerJanitor(qaservice.filtered_buslistener):

            ## start listening for QA event messages from the QAService
            #with BusListenerJanitor(SynchronizationQABusListener(exchange=self.tmp_exchange.address)) as qa_listener:
                ## trigger a qa process by sending otdb task completing event
                ## this will result in the QAService actually doing its magic
                #self.send_otdb_task_completing_event()

                ## start waiting until ConvertedMS2Hdf5 event message received (or timeout)
                #qa_listener.converted_event.wait(30)

                ## ConvertedMS2Hdf5 event message should have been sent, so converted_event should have been set
                #self.assertTrue(qa_listener.converted_event.is_set())

                ## check the converted_msg_content
                #self.assertTrue('otdb_id' in qa_listener.converted_msg_content)
                #self.assertTrue('hdf5_file_path' in qa_listener.converted_msg_content)


                ## start waiting until Clustered event message received (or timeout)
                #qa_listener.clustered_event.wait(30)


                ## Clustered event message should have been sent, so clustered_event should have been set
                #self.assertTrue(qa_listener.clustered_event.is_set())

                ## check the clustered_msg_content
                #self.assertTrue('otdb_id' in qa_listener.clustered_msg_content)
                #self.assertTrue('hdf5_file_path' in qa_listener.clustered_msg_content)


                ## start waiting until CreatedInspectionPlots event message received (or timeout)
                #qa_listener.plotted_event.wait(30)

                ## CreatedInspectionPlots event message should have been sent, so plotted_event should have been set
                #self.assertTrue(qa_listener.plotted_event.is_set())

                ## check the plotted_msg_content
                #self.assertTrue('otdb_id' in qa_listener.plotted_msg_content)
                #self.assertTrue('hdf5_file_path' in qa_listener.plotted_msg_content)
                #self.assertTrue('plot_dir_path' in qa_listener.plotted_msg_content)

                ## TODO: merge adder branch into trunk so we can use plot_hdf5_dynamic_spectra on the test-h5 file to create plots, then re-enable the checks on created plots
                ## # check if the output dirs/files exist
                ## self.assertTrue(os.path.exists(qa_listener.plotted_msg_content['hdf5_file_path']))
                ## logger.info(qa_listener.plotted_msg_content['plot_dir_path'])
                ## self.assertTrue(os.path.exists(qa_listener.plotted_msg_content['plot_dir_path']))
                ## plot_file_names = [f for f in os.listdir(qa_listener.plotted_msg_content['plot_dir_path'])
                ##                    if f.endswith('png')]
                ## self.assertEqual(10, len(plot_file_names))
                ##
                ## auto_correlation_plot_file_names = [f for f in plot_file_names
                ##                                     if 'auto' in f]
                ## self.assertEqual(4, len(auto_correlation_plot_file_names))
                ##
                ## complex_plot_file_names = [f for f in plot_file_names
                ##                            if 'complex' in f]
                ## self.assertEqual(6, len(complex_plot_file_names))

                ## start waiting until QAFinished event message received (or timeout)
                #qa_listener.finished_event.wait(30)

                ## QAFinished event message should have been sent, so finished_event should have been set
                #self.assertTrue(qa_listener.finished_event.is_set())

                ## check the result_msg_content
                #self.assertTrue('otdb_id' in qa_listener.finished_msg_content)
                #self.assertTrue('hdf5_file_path' in qa_listener.finished_msg_content)
                #self.assertTrue('plot_dir_path' in qa_listener.finished_msg_content)

                #self.wrap_command_for_docker_mock.assert_called()
                #self.wrap_command_in_cep4_node_ssh_call_mock.assert_called()
                #self.wrap_command_in_cep4_head_node_ssh_call_mock.assert_called()
                #self.get_cep4_available_cpu_nodes_mock.assert_called()
                #self.ssh_cmd_list_mock1.assert_not_called()
                #self.ssh_cmd_list_mock2.assert_not_called()

    #@integration_test
    #def test_02_qa_service_for_error_in_ms2hdf5(self):
        #'''
        #This test starts a QAService, triggers a test observation completing event,
        #and tests if the conversion from MS to hdf5 fails (by intention).
        #It is an end-to-end test which does not check the intermediate results. It is assumed that
        #the intermediate steps are tested in other tests/modules.
        #'''

        #logger.info(' -- test_02_qa_service_for_error_in_ms2hdf5 -- ')

        #def mocked_wrap_command_for_docker(cmd, image_name=None, image_label=None):
            #if 'ms2hdf5' in cmd:
                ## replace the ms2hdf5 command which runs normally in the docker container
                ## by a call to bash false, so the 'ms2hdf5' call returns non-0 exit code
                #mocked_cmd = ['false']
                #logger.info('mocked_wrap_command_for_docker returning mocked erroneous command: %s', mocked_cmd)
                #return mocked_cmd

            #logger.info('mocked_wrap_command_for_docker returning original command: %s', cmd)
            #return cmd

        #self.wrap_command_for_docker_mock.side_effect = mocked_wrap_command_for_docker

        ## start the QAService (the object under test)
        #qaservice = QAService(exchange=self.tmp_exchange.address, qa_base_dir=self.TEST_DIR)
        #with qaservice, BusListenerJanitor(qaservice.filtering_buslistener), BusListenerJanitor(qaservice.filtered_buslistener):

            ## start listening for QA event messages from the QAService
            #with BusListenerJanitor(SynchronizationQABusListener(exchange=self.tmp_exchange.address)) as qa_listener:
                ## trigger a qa process by sending otdb task completing event
                ## this will result in the QAService actually doing its magic
                #self.send_otdb_task_completing_event()

                ## start waiting until QAFinished event message received (or timeout)
                #qa_listener.error_event.wait(30)

                ## ------------
                ## Error event message should have been sent, so error_event should have been set
                #self.assertTrue(qa_listener.error_event.is_set())

                #self.assertTrue('otdb_id' in qa_listener.error_msg_content)
                #self.assertTrue('message' in qa_listener.error_msg_content)

                #self.wrap_command_for_docker_mock.assert_called()
                #self.wrap_command_in_cep4_node_ssh_call_mock.assert_called()
                #self.get_cep4_available_cpu_nodes_mock.assert_called()
                #self.ssh_cmd_list_mock1.assert_not_called()
                #self.ssh_cmd_list_mock2.assert_not_called()

    #@integration_test
    #def test_03_qa_service_for_error_in_creating_plots(self):
        #'''
        #This test starts a QAService, triggers a test observation completing event,
        #and tests if the conversion from MS to hdf5 works,
        #but the plot generation fails (by intention).
        #It is an end-to-end test which does not check the intermediate results. It is assumed that
        #the intermediate steps are tested in other tests/modules.
        #'''

        #logger.info(' -- test_03_qa_service_for_error_in_creating_plots -- ')

        ## mock the calls to ssh cep4 and docker
        #def mocked_wrap_command_for_docker(cmd, image_name=None, image_label=None):
            #if 'ms2hdf5' in cmd:
                ## replace the ms2hdf5 command which runs normally in the docker container
                ## by a call to the create_test_hypercube which fakes the ms2hdf5 conversion for this test.
                ## the create_test_hypercube executable should be available in the PATH environment
                #create_test_hypercube_path = 'create_test_hypercube'
                #mocked_cmd = [create_test_hypercube_path, '-s 4', '-S 8', '-t 16',
                              #'-o', str(self.TEST_OTDB_ID), self.TEST_H5_PATH]
                #logger.info('mocked_wrap_command_for_docker returning mocked command to create test h5 file: %s',
                            #' '.join(mocked_cmd))
                #return mocked_cmd

            #if 'cluster_this.py' in cmd:
                ## replace the cluster command which runs normally in the docker container
                ## by a call to bash true, so the 'cluster_this' call returns 0 exit code
                #mocked_cmd = ['true']
                #logger.info('mocked_wrap_command_for_docker returning mocked command: %s', mocked_cmd)
                #return mocked_cmd


            #if 'plot_hdf5_dynamic_spectra' in cmd:
                ## replace the ms2hdf5 command which runs normally in the docker container
                ## by a call to bash false, so the 'ms2hdf5' call returns non-0 exit code
                #mocked_cmd = ['false']
                #logger.info('mocked_wrap_command_for_docker returning mocked erroneous command: %s', mocked_cmd)
                #return mocked_cmd

            #logger.info('mocked_wrap_command_for_docker returning original command: %s', ' '.join(cmd))
            #return cmd

        #self.wrap_command_for_docker_mock.side_effect = mocked_wrap_command_for_docker

        ## start the QAService (the object under test)
        #qaservice = QAService(exchange=self.tmp_exchange.address, qa_base_dir=self.TEST_DIR)
        #with qaservice, BusListenerJanitor(qaservice.filtering_buslistener), BusListenerJanitor(qaservice.filtered_buslistener):

            ## start listening for QA event messages from the QAService
            #with BusListenerJanitor(SynchronizationQABusListener(exchange=self.tmp_exchange.address)) as qa_listener:
                ## trigger a qa process by sending otdb task completing event
                ## this will result in the QAService actually doing its magic
                #self.send_otdb_task_completing_event()

                ## start waiting until ConvertedMS2Hdf5 event message received (or timeout)
                #qa_listener.converted_event.wait(30)

                ## ConvertedMS2Hdf5 event message should have been sent, so converted_event should have been set
                #self.assertTrue(qa_listener.converted_event.is_set())

                ## check the result_msg_content
                #self.assertTrue('otdb_id' in qa_listener.converted_msg_content)
                #self.assertTrue('hdf5_file_path' in qa_listener.converted_msg_content)

                ## start waiting until Error event message received (or timeout)
                #qa_listener.error_event.wait(30)

                ## Error event message should have been sent, so error_event should have been set
                #self.assertTrue(qa_listener.error_event.is_set())

                ## check the result_msg_content
                #self.assertTrue('otdb_id' in qa_listener.error_msg_content)
                #self.assertTrue('message' in qa_listener.error_msg_content)

                #self.wrap_command_for_docker_mock.assert_called()
                #self.wrap_command_in_cep4_node_ssh_call_mock.assert_called()
                #self.get_cep4_available_cpu_nodes_mock.assert_called()
                #self.ssh_cmd_list_mock1.assert_not_called()
                #self.ssh_cmd_list_mock2.assert_not_called()

    #@integration_test
    #def test_04_qa_service_for_error_ssh(self):
        #'''
        #This test starts a QAService, triggers a test observation completing event,
        #and tests if conversion fails due to an intentionally failing (mocked) ssh call.
        #It is an end-to-end test which does not check the intermediate results. It is assumed that
        #the intermediate steps are tested in other tests/modules.
        #'''

        #logger.info(' -- test_04_qa_service_for_error_ssh -- ')

        #def mocked_wrap_command_in_cep4_node_ssh_call(cmd, cpu_node_nr, partition, via_head):
            #logger.info('mocked_wrap_command_in_cep4_node_ssh_call for cpu node nr %s via head=%s ' \
                        #'returning call to bash false', cpu_node_nr, via_head)
            #return ['false', ';']

        #self.wrap_command_in_cep4_node_ssh_call_mock.side_effect = mocked_wrap_command_in_cep4_node_ssh_call

        ## start the QAService (the object under test)
        #qaservice = QAService(exchange=self.tmp_exchange.address, qa_base_dir=self.TEST_DIR)
        #with qaservice, BusListenerJanitor(qaservice.filtering_buslistener), BusListenerJanitor(qaservice.filtered_buslistener):

            ## start listening for QA event messages from the QAService
            #with BusListenerJanitor(SynchronizationQABusListener(exchange=self.tmp_exchange.address)) as qa_listener:
                ## trigger a qa process by sending otdb task completing event
                ## this will result in the QAService actually doing its magic
                #self.send_otdb_task_completing_event()

                ## start waiting until Error event message received (or timeout)
                #qa_listener.error_event.wait(30)

                ## Error event message should have been sent, so error_event should have been set
                #self.assertTrue(qa_listener.error_event.is_set())

                ## check the result_msg_content
                #self.assertTrue('otdb_id' in qa_listener.error_msg_content)
                #self.assertTrue('message' in qa_listener.error_msg_content)

                #self.wrap_command_for_docker_mock.assert_called()
                #self.wrap_command_in_cep4_node_ssh_call_mock.assert_called()
                #self.get_cep4_available_cpu_nodes_mock.assert_called()
                #self.ssh_cmd_list_mock1.assert_not_called()
                #self.ssh_cmd_list_mock2.assert_not_called()


#logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

#if __name__ == '__main__':
    ##run the unit tests
    #unittest.main()
