#!/usr/bin/env python3

import logging
import unittest
import uuid
import os.path
import shutil
from unittest.mock import patch

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from subprocess import call
if call(['ssh', '-o', 'PasswordAuthentication=no', '-o', 'PubkeyAuthentication=yes', '-o', 'ConnectTimeout=1', 'localhost', 'true']) != 0:
    print('this test depends on keybased ssh login to localhost, which is not setup correctly. skipping test...')
    exit(3)

from lofar.messaging import TemporaryExchange
from lofar.messaging.messagelogger import MessageLogger

testname = 't_ingestpipeline_%s' % uuid.uuid1()


# patch (mock) the LTAClient class during these tests.
# when the ingestpipeline instantiates an LTAClient it will get the mocked class.
with patch('lofar.lta.ingest.server.ltaclient.LTAClient', autospec=True) as MockLTAClient:
    ltamock = MockLTAClient.return_value

    # patch (mock) the MoMClient class during these tests.
    # when the ingestpipeline instantiates an MoMClient it will get the mocked class.
    with patch('lofar.lta.ingest.server.momclient.MoMClient', autospec=True) as MockMoMClient:
        mommock = MockMoMClient.return_value
        # modify the return values of the various MoMClient methods with pre-cooked answers
        mommock.setStatus.return_value = True

        # patch (mock) the convert_surl_to_turl method during these tests.
        with patch('lofar.lta.ingest.common.srm.convert_surl_to_turl') as mock_convert_surl_to_turl:
            mock_convert_surl_to_turl.side_effect = lambda surl: surl.replace('srm', 'gsiftp')

            from lofar.lta.ingest.common.job import createJobXml, parseJobXml
            from lofar.lta.ingest.server.ltaclient import LTAClient # <-- thanks to magick mock, we get the mocked ltaclient
            from lofar.lta.ingest.server.momclient import MoMClient # <-- thanks to magick mock, we get the mocked momclient
            from lofar.lta.ingest.server.ingestpipeline import *
            import ltastubs

            class TestIngestPipeline(unittest.TestCase):
                def setUp(self):
                    self.test_dir_path = None

                    self.tmp_exchange = TemporaryExchange(testname)
                    self.tmp_exchange.open()

                    # hook a MessageLogger to the bus, so we can read in the logs what's send around
                    self.message_logger = MessageLogger(exchange=self.tmp_exchange.address)
                    self.message_logger.start_listening()

                    ltastubs.stub()
                    self.ltaclient = LTAClient()
                    self.momclient = MoMClient()

                def tearDown(self):
                    ltastubs.un_stub()
                    self.message_logger.stop_listening()
                    self.tmp_exchange.close()

                    if self.test_dir_path and os.path.exists(self.test_dir_path):
                        logger.info("removing test dir: %s", self.test_dir_path)
                        shutil.rmtree(self.test_dir_path, True)

                def test_single_file(self):
                    try:
                        project_name = 'test-project'
                        obs_id = 987654321
                        dpname = 'L%s_SAP000_SB000_im.h5' % obs_id
                        self.test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1())

                        def stub_GetStorageTicket(project, filename, filesize, archive_id, job_id, obs_id, check_mom_id=True, id_source='MoM'):
                            return { 'primary_uri_rnd': 'srm://some.site.name:8443/some/path/data/lofar/ops/projects/%s/%s/%s' % (project, obs_id, dpname),
                                     'result': 'ok',
                                     'error': '',
                                     'ticket': '3E0A47ED860D6339E053B316A9C3BEE2'}
                        ltamock.GetStorageTicket.side_effect = stub_GetStorageTicket

                        def stub_uploadDataAndGetSIP(archive_id, storage_ticket, filename, uri, filesize, md5_checksum, adler32_checksum, validate=True):
                            #return unpecified sip with proper details
                            from lofar.lta.ingest.server.unspecifiedSIP import makeSIP
                            return makeSIP(project_name, obs_id, archive_id, storage_ticket, filename, filesize, md5_checksum, adler32_checksum, 'TEST')
                        mommock.uploadDataAndGetSIP.side_effect = stub_uploadDataAndGetSIP

                        os.makedirs(self.test_dir_path)
                        test_file_path = os.path.join(self.test_dir_path, dpname)
                        with open(test_file_path, 'w') as file:
                            file.write(4096*'a')

                        job_xml = createJobXml(testname, 123456789, obs_id, dpname, 918273645, 'localhost:%s' % test_file_path)
                        logger.info('job xml: %s', job_xml)
                        job = parseJobXml(job_xml)

                        pl = IngestPipeline(job, self.momclient, self.ltaclient,
                                            exchange=self.tmp_exchange.address)
                        pl.run()

                    except Exception as e:
                        self.assertTrue(False, 'Unexpected exception in pipeline: %s' % e)
                    finally:
                        # the 'stub-transfered' file ended up in out local stub lta
                        # with the path: ltastubs._local_globus_file_path
                        #check extension
                        self.assertEqual(os.path.splitext(test_file_path)[-1],
                                         os.path.splitext(ltastubs._local_globus_file_path)[-1])

                        #compare with original
                        with open(test_file_path) as input, open(ltastubs._local_globus_file_path) as output:
                            self.assertEqual(input.read(), output.read())

                        for f in os.listdir(self.test_dir_path):
                            os.remove(os.path.join(self.test_dir_path, f))
                        os.removedirs(self.test_dir_path)

                def test_h5_plus_raw_file(self):
                    #beam formed h5 files are always accompanied by a raw file
                    #these should be tarred togheter
                    try:
                        project_name = 'test-project'
                        obs_id = 987654321
                        dpname = 'L%s_SAP000_SB000_bf.h5' % obs_id
                        rawname = dpname.replace('.h5', '.raw')
                        self.test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1())

                        def stub_GetStorageTicket(project, filename, filesize, archive_id, job_id, obs_id, check_mom_id=True, id_source='MoM'):
                            return { 'primary_uri_rnd': 'srm://some.site.name:8443/some/path/data/lofar/ops/projects/%s/%s/%s.tar' % (project, obs_id, dpname),
                                     'result': 'ok',
                                     'error': '',
                                     'ticket': '3E0A47ED860D6339E053B316A9C3BEE2'}
                        ltamock.GetStorageTicket.side_effect = stub_GetStorageTicket

                        def stub_uploadDataAndGetSIP(archive_id, storage_ticket, filename, uri, filesize, md5_checksum, adler32_checksum, validate=True):
                            #return unpecified sip with proper details
                            from lofar.lta.ingest.server.unspecifiedSIP import makeSIP
                            return makeSIP(project_name, obs_id, archive_id, storage_ticket, filename, filesize, md5_checksum, adler32_checksum, 'TEST')
                        mommock.uploadDataAndGetSIP.side_effect = stub_uploadDataAndGetSIP

                        os.makedirs(self.test_dir_path)
                        test_file_path = os.path.join(self.test_dir_path, dpname)
                        with open(test_file_path, 'w') as file:
                            file.write(4096*'a')
                        raw_test_file_path = os.path.join(self.test_dir_path, dpname.replace('.h5', '.raw'))
                        with open(raw_test_file_path, 'w') as file:
                            file.write(4096*'b')

                        job_xml = createJobXml(testname, 123456789, obs_id, dpname, 918273645, 'localhost:%s' % test_file_path)
                        logger.info('job xml: %s', job_xml)
                        job = parseJobXml(job_xml)

                        pl = IngestPipeline(job, self.momclient, self.ltaclient,
                                            exchange=self.tmp_exchange.address)
                        pl.run()

                    except Exception as e:
                        self.assertTrue(False, 'Unexpected exception in pipeline: %s' % e)
                    finally:
                        # the 'stub-transfered' file ended up in out local stub lta
                        # with the path: ltastubs._local_globus_file_path
                        #check extension
                        self.assertEqual('.tar', os.path.splitext(ltastubs._local_globus_file_path)[-1])

                        #check tar contents
                        tar = subprocess.Popen(['tar', '--list', '-f', ltastubs._local_globus_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        tar_file_list, err = tuple(x.decode('ascii') for x in tar.communicate())
                        self.assertEqual(tar.returncode, 0)
                        logger.info('file list in tar:\n%s', tar_file_list)

                        self.assertTrue(os.path.basename(test_file_path) in tar_file_list)
                        self.assertTrue(os.path.basename(raw_test_file_path) in tar_file_list)
                        logger.info('all expected source files are in tar!')

                        os.remove(test_file_path)
                        os.remove(raw_test_file_path)
                        os.removedirs(self.test_dir_path)


                def test_directory(self):
                    try:
                        project_name = 'test-project'
                        obs_id = 987654321
                        dpname = 'L%s_SAP000_SB000_uv.MS' % obs_id
                        self.test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1(), dpname)

                        def stub_GetStorageTicket(project, filename, filesize, archive_id, job_id, obs_id, check_mom_id=True, id_source='MoM'):
                            return { 'primary_uri_rnd': 'srm://some.site.name:8443/some/path/data/lofar/ops/projects/%s/%s/%s.tar' % (project, obs_id, dpname),
                                     'result': 'ok',
                                     'error': '',
                                     'ticket': '3E0A47ED860D6339E053B316A9C3BEE2'}
                        ltamock.GetStorageTicket.side_effect = stub_GetStorageTicket

                        def stub_uploadDataAndGetSIP(archive_id, storage_ticket, filename, uri, filesize, md5_checksum, adler32_checksum, validate=True):
                            #return unpecified sip with proper details
                            from lofar.lta.ingest.server.unspecifiedSIP import makeSIP
                            return makeSIP(project_name, obs_id, archive_id, storage_ticket, filename, filesize, md5_checksum, adler32_checksum, 'TEST')
                        mommock.uploadDataAndGetSIP.side_effect = stub_uploadDataAndGetSIP

                        os.makedirs(self.test_dir_path)
                        test_file_paths = []
                        for i in range(10):
                            test_file_path = os.path.join(self.test_dir_path, 'testfile_%s.txt' % i)
                            test_file_paths.append(test_file_path)
                            with open(test_file_path, 'w') as file:
                                file.write(1000*'a')

                        job_xml = createJobXml(testname, 123456789, obs_id, dpname, 918273645, 'localhost:%s' % self.test_dir_path)
                        logger.info('job xml: %s', job_xml)
                        job = parseJobXml(job_xml)

                        pl = IngestPipeline(job, self.momclient, self.ltaclient,
                                            exchange=self.tmp_exchange.address)
                        pl.run()
                    except Exception as e:
                        self.assertTrue(False, 'Unexpected exception in pipeline: %s' % e)
                    finally:
                        # the 'stub-transfered' file ended up in out local stub lta
                        # with the path: ltastubs._local_globus_file_path
                        #check extension
                        self.assertTrue('.tar' == os.path.splitext(ltastubs._local_globus_file_path)[-1])

                        #check tar contents
                        tar = subprocess.Popen(['tar', '--list', '-f', ltastubs._local_globus_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        tar_file_list, err = tuple(x.decode('ascii') for x in tar.communicate())
                        self.assertEqual(tar.returncode, 0)
                        logger.info('file list in tar:\n%s', tar_file_list)

                        for test_file_path in test_file_paths:
                            self.assertTrue(os.path.basename(test_file_path) in tar_file_list)
                        logger.info('all expected source files are in tar!')

                        for f in os.listdir(self.test_dir_path):
                            os.remove(os.path.join(self.test_dir_path, f))
                        os.removedirs(self.test_dir_path)

                def test_directory_with_odd_dataproduct_name(self):
                    #sometimes somebody has data in a odd directory
                    #and gives the dataproduct a different name than it's directory
                    try:
                        project_name = 'test-project'
                        obs_id = 987654321
                        dpname = 'my_funky_dp_name'
                        self.test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1(), 'my_data_dir')

                        def stub_uploadDataAndGetSIP(archive_id, storage_ticket, filename, uri, filesize, md5_checksum, adler32_checksum, validate=True):
                            #return unpecified sip with proper details
                            from lofar.lta.ingest.server.unspecifiedSIP import makeSIP
                            return makeSIP(project_name, obs_id, archive_id, storage_ticket, filename, filesize, md5_checksum, adler32_checksum, 'TEST')
                        mommock.uploadDataAndGetSIP.side_effect = stub_uploadDataAndGetSIP

                        os.makedirs(self.test_dir_path)
                        test_file_paths = []
                        for i in range(10):
                            test_file_path = os.path.join(self.test_dir_path, 'testfile_%s.txt' % i)
                            test_file_paths.append(test_file_path)
                            with open(test_file_path, 'w') as file:
                                file.write(1000*'a')

                        job_xml = createJobXml(testname, 123456789, obs_id, dpname, 918273645, 'localhost:%s' % self.test_dir_path)
                        logger.info('job xml: %s', job_xml)
                        job = parseJobXml(job_xml)

                        pl = IngestPipeline(job, self.momclient, self.ltaclient,
                                            exchange=self.tmp_exchange.address)
                        pl.run()
                    except Exception as e:
                        self.assertTrue(False, 'Unexpected exception in pipeline: %s' % e)
                    finally:
                        # the 'stub-transfered' file ended up in out local stub lta
                        # with the path: ltastubs._local_globus_file_path
                        #check extension
                        self.assertTrue('.tar' == os.path.splitext(ltastubs._local_globus_file_path)[-1])

                        #check tar contents
                        tar = subprocess.Popen(['tar', '--list', '-f', ltastubs._local_globus_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        tar_file_list, err = tuple(x.decode('ascii') for x in tar.communicate())
                        self.assertEqual(tar.returncode, 0)
                        logger.info('file list in tar:\n%s', tar_file_list)

                        for test_file_path in test_file_paths:
                            self.assertTrue(os.path.basename(test_file_path) in tar_file_list)
                        logger.info('all expected source files are in tar!')

                        for f in os.listdir(self.test_dir_path):
                            os.remove(os.path.join(self.test_dir_path, f))
                        os.removedirs(self.test_dir_path)


            if __name__ == '__main__':
                logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                                    level=logging.DEBUG)
                unittest.main()

