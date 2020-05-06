#!/usr/bin/env python3

import unittest
import uuid
import datetime
import logging
from lofar.messaging.messagebus import TemporaryQueue

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with TemporaryQueue(__name__) as tmp_queue:
    busname = tmp_queue.address

    logger.warning("Fix and re-enable test_cleanup_service_and_rpc!")
    exit(3)

    # TODO: the cleanup service does not use shutil.rmtree under the hood anymore,
    # so we cannot mock that
    # and we do not want to delete actual data
    # so I disabled this test for now.

    ## the cleanup service uses shutil.rmtree under the hood
    ## so, mock/patch shutil.rmtree and fake the delete action
    ## because we do not want to delete any real data in this test
    #with patch('shutil.rmtree', autospec=True) as patch_rmtree:
        #mock_rmtree = patch_rmtree.return_value
        #mock_rmtree.return_value = True

        #with patch('lofar.sas.resourceassignment.resourceassignmentservice.rpc.RARPC', autospec=True) as patch_rarpc:
            #mock_rarpc = patch_rarpc.return_value
            #mock_rarpc.getTask.side_effect = lambda otdb_id: {'id': 42, 'mom_id': 1000042} if otdb_id == 13 else {'id': 43, 'mom_id': 1000043} if otdb_id == 14 else None

            #with patch('lofar.mom.momqueryservice.momqueryrpc.MoMQueryRPC', autospec=True) as patch_momrpc:
                #mock_momrpc = patch_momrpc.return_value
                #mock_momrpc.getObjectDetails.return_value = {'1000042': {'project_name': 'my_project'}}

                ## now that we have a mocked the external dependencies, import cleanupservice
                #from lofar.sas.datamanagement.cleanup.service import createService
                #from lofar.sas.datamanagement.cleanup.rpc import CleanupRPC

                #class TestCleanupServiceAndRPC(unittest.TestCase):
                    #def testRemovePath(self):
                        #with CleanupRPC(busname=busname) as rpc:
                            ##try some invalid input
                            #self.assertFalse(rpc.removePath(None)['deleted'])
                            #self.assertFalse(rpc.removePath(True)['deleted'])
                            #self.assertFalse(rpc.removePath({'foo':'bar'})['deleted'])
                            #self.assertFalse(rpc.removePath(['foo', 'bar'])['deleted'])

                            ##try some dangerous paths
                            ##these should not be deleted
                            #result = rpc.removePath('/')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Path does not start with' in result['message'])

                            #result = rpc.removePath('/foo/*/bar')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('No wildcards allowed' in result['message'])

                            #result = rpc.removePath('/foo/ba?r')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('No wildcards allowed' in result['message'])

                            #result = rpc.removePath('/data')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Path does not start with' in result['message'])

                            #result = rpc.removePath('/data/test-projects/')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Path should be a subdir of' in result['message'])

                            #result = rpc.removePath('/data/test-projects/foo')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Path should be a subdir of' in result['message'])

                            #result = rpc.removePath('/data/test-projects/foo/')
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Path should be a subdir of' in result['message'])

                            ##try an actual delete, should work with mocked shutil.rmtree
                            #self.assertTrue(rpc.removePath('/data/test-projects/foo/bar')['deleted'])

                    #def testRemoveTaskData(self):
                        #with CleanupRPC(busname=busname) as rpc:
                            ##try existing otdb_id=13
                            #self.assertTrue(rpc.removeTaskData(13)['deleted'])

                            ##try non_existing mom_project for otdb_id=14
                            #result = rpc.removeTaskData(14)
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Could not find mom project details' in result['message'])

                            ##try non_existing otdb_id=15
                            #result = rpc.removeTaskData(15)
                            #self.assertFalse(result['deleted'])
                            #self.assertTrue('Could not find task' in result['message'])

                ## create and run the service
                #with createService(busname=busname):
                    ## and run all tests
                    #unittest.main()
