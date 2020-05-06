#!/usr/bin/env python3

import unittest, unittest.mock
import logging
import os
import shutil
import sys
from threading import Thread
from lofar.messaging.messagebus import  TemporaryExchange
from lofar.sas.datamanagement.storagequery.service import createService
from lofar.sas.datamanagement.storagequery.rpc import StorageQueryRPC
from lofar.sas.datamanagement.storagequery.cache import CacheManager

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s %(threadName)s', level=logging.INFO, stream=sys.stdout)

class TestStorageQueryServiceAndRPC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        cls.stored_otdb_ids = set()

        DIR_BYTES = 4096 # each dir adds 4096 bytes to a du
        cls.total_bytes_stored = DIR_BYTES
        cls.projects_bytes_stored = {}
        cls.observation_bytes_stored = {}

        cls.DATA_DIR_PATH = os.path.join(os.getcwd(), "test_data")
        cls.PROJECTS_DIR_PATH = os.path.join(cls.DATA_DIR_PATH, "test-projects")
        cls.PROJECTS = ['LC100_001', 'LC100_002']
        cls.otdb_id2project_map = {}

        for i, project in enumerate(cls.PROJECTS):
            cls.projects_bytes_stored[project] = DIR_BYTES
            cls.total_bytes_stored += DIR_BYTES

            for j in range(10):
                otdb_id = 999000 + (10*i+j)

                cls.stored_otdb_ids.add(otdb_id)
                cls.otdb_id2project_map[otdb_id] = project

                obs_dir = 'L%d' % (otdb_id,)
                obs_dir_path = os.path.join(cls.PROJECTS_DIR_PATH, project, obs_dir)
                os.makedirs(obs_dir_path, exist_ok=True)

                cls.observation_bytes_stored[otdb_id] = DIR_BYTES
                cls.projects_bytes_stored[project] += DIR_BYTES
                cls.total_bytes_stored += DIR_BYTES

                obs_data_file_path = os.path.join(obs_dir_path, 'data.txt')

                with open(obs_data_file_path, 'wt') as file:
                    data = 1000*(i+1)*(j+1)*r'a'
                    file.write(data)
                    num_bytes = len(data)
                    cls.total_bytes_stored += num_bytes
                    cls.projects_bytes_stored[project] += num_bytes
                    cls.observation_bytes_stored[otdb_id] += num_bytes

        cls.ssh_cmd_list_patcher = unittest.mock.patch('lofar.common.cep4_utils.ssh_cmd_list', lambda host,user: [])
        cls.ssh_cmd_list_patcher.start()

        cls.updateCEP4CapacitiesInRADB_patcher = unittest.mock.patch('lofar.sas.datamanagement.storagequery.cache.CacheManager._updateCEP4CapacitiesInRADB')
        cls.updateCEP4CapacitiesInRADB_patcher.start()

        # patch RADBRPC.getTask call and return the given otdb_id for each radb/mom/otdb id
        cls.radbrpc_patcher = unittest.mock.patch('lofar.sas.datamanagement.common.path.RADBRPC.getTask')
        radbrpc_mock = cls.radbrpc_patcher.start()
        radbrpc_mock.side_effect = lambda id, mom_id, otdb_id: { 'id': otdb_id, 'mom_id': otdb_id, 'otdb_id': otdb_id,
                                                                 'type': 'observation' }

        cls.momrpc_patcher = unittest.mock.patch('lofar.sas.datamanagement.common.path.MoMQueryRPC.getObjectDetails')
        momrpc_mock = cls.momrpc_patcher.start()
        momrpc_mock.side_effect = lambda mom_id: { mom_id: {'project_name': cls.otdb_id2project_map[mom_id]} }

        cls.tmp_exchange = TemporaryExchange(cls.__class__.__name__)
        cls.tmp_exchange.open()

        cls.cache = CacheManager(mountpoint=cls.DATA_DIR_PATH, exchange=cls.tmp_exchange.address)
        cls.cache.open()

        cls.service = createService(cls.tmp_exchange.address, cache_manager=cls.cache)
        cls.service.start_listening()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.DATA_DIR_PATH)
        cls.cache.close()
        cls.service.stop_listening()
        cls.tmp_exchange.close()
        cls.ssh_cmd_list_patcher.stop()
        cls.updateCEP4CapacitiesInRADB_patcher.stop()
        cls.radbrpc_patcher.stop()
        cls.momrpc_patcher.stop()


    def test_getOtdbIdsFoundOnDisk(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            found_otdb_ids = set(rpc.getOtdbIdsFoundOnDisk())
            self.assertEqual(self.stored_otdb_ids, found_otdb_ids)

    def test_getDiskUsagesForAllOtdbIds(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            results = rpc.getDiskUsagesForAllOtdbIds(force_update=True)
            self.assertEqual(self.stored_otdb_ids, set(results.keys()))

            for otdb_id in self.stored_otdb_ids:
                self.assertEqual(self.observation_bytes_stored[otdb_id], results[otdb_id]['disk_usage'])

    def test_getDiskUsageForProjectsDirAndSubDirectories(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            result = rpc.getDiskUsageForProjectsDirAndSubDirectories(force_update=True)
            self.assertTrue(result['found'])

            self.assertEqual(self.PROJECTS_DIR_PATH, result['projectdir']['path'])
            self.assertEqual(self.total_bytes_stored, result['projectdir']['disk_usage'])

            for project in self.PROJECTS:
                project_path = os.path.join(self.PROJECTS_DIR_PATH, project)
                self.assertTrue(project_path in result['sub_directories'])
                self.assertEqual(self.projects_bytes_stored[project], result['sub_directories'][project_path]['disk_usage'])

    def test_getDiskUsageForProjectDirAndSubDirectories(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            for project in self.PROJECTS:
                result = rpc.getDiskUsageForProjectDirAndSubDirectories(project_name=project, force_update=True)
                self.assertEqual(self.projects_bytes_stored[project], result['projectdir']['disk_usage'])

    def test_getDiskUsageForTask(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            for otdb_id in self.stored_otdb_ids:
                results = rpc.getDiskUsageForTask(otdb_id=otdb_id, force_update=True)
                self.assertEqual(self.observation_bytes_stored[otdb_id], results['disk_usage'])

    def test_getDiskUsageForTasks(self):
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:
            results = rpc.getDiskUsageForTasks(otdb_ids=list(self.stored_otdb_ids), force_update=True)
            for otdb_id in self.stored_otdb_ids:
                self.assertTrue(otdb_id in results['otdb_ids'])
                self.assertEqual(self.observation_bytes_stored[otdb_id], results['otdb_ids'][otdb_id]['disk_usage'])

    def test_survive_ddos(self):
        '''spam the service. It should be able to handle that.
        It's interesting to analyze the logging, which reports on how all requests are handled in parallel.'''
        with StorageQueryRPC.create(self.tmp_exchange.address) as rpc:

            # spamming, spawn many large getDiskUsageForTasks calls in parallel
            threads = []
            for i in range(10):
                threads.append(Thread(target=rpc.getDiskUsageForTasks,
                                      kwargs={'otdb_ids': list(self.stored_otdb_ids), 'force_update': True}))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # and to a final check. Service should still be reachable and deliver proper results
            self.test_getDiskUsageForTasks()

if __name__ == '__main__':
    unittest.main()

