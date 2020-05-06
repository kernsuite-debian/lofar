#!/usr/bin/env python3

from unittest import mock
# test if netcat is available
try:
    from subprocess import call
    if call("which nc", shell=True) != 0:
        print('Cannot run test without netcat')
        print('Please install netcat.')
        exit(3)
except Exception as e:
    print(e)
    exit(3)

import logging
import unittest
import uuid
import os, os.path

with mock.patch('lofar.lta.ingest.common.srm.convert_surl_to_turl',
                new=lambda surl: surl.replace('srm', 'gsiftp')):

    import lofar.lta.ingest.server.ltacp as ltacp
    import ltastubs

    logger = logging.getLogger()

    class TestLtaCp(unittest.TestCase):
        def setUp(self):
            ltastubs.stub()

        def tearDown(self):
            ltastubs.un_stub()

        def test_path_exists(self):
            test_file_path = os.path.join(os.getcwd(), str(uuid.uuid1()), 'testfile.txt')
            os.makedirs(os.path.dirname(test_file_path))
            with open(test_file_path, 'w') as file:
                file.write(1000*'a')

            try:
                cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')
                self.assertTrue(cp.source_exists())
            except Exception as e:
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)
            finally:
                os.remove(test_file_path)

        def test_path_mounted(self):
            #first test with a valid path, the current working dir + some random dir + file
            test_file_path = os.path.join(os.getcwd(), str(uuid.uuid1()), 'testfile.txt')
            cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')

            #the path should not exists, but it should be mounted
            self.assertFalse(cp.source_exists())
            self.assertTrue(cp.source_mounted())

            #let's try to transfer this file, should not succeed, but raise an exception
            try:
                cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')
                cp.transfer()
            except ltacp.LtacpException as e:
                logger.info('caught expected LtacpException: %s', e.value)
                self.assertTrue('source path' in e.value and 'does not exist' in e.value)
            except Exception as e:
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)


            #repeat same test, but now with a non-mounted disk
            test_file_path = '/non-existing-root-dir/dir1/dir2/file.txt'
            cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')
            self.assertFalse(cp.source_mounted())

            #let's try to transfer this file, should not succeed, but raise an exception
            try:
                cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')
                cp.transfer()
            except ltacp.LtacpException as e:
                logger.info('caught expected LtacpException: %s', e.value)
                self.assertTrue('the disk of source path' in e.value and 'does not seem to be mounted' in e.value)
            except Exception as e:
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)

        def test_single_file(self):
            test_file_path = os.path.join(os.getcwd(), str(uuid.uuid1()), 'testfile.txt')
            os.makedirs(os.path.dirname(test_file_path))
            with open(test_file_path, 'w') as file:
                file.write(1000*'a')

            try:
                cp = ltacp.LtaCp('localhost', test_file_path, 'srm://fake_surl')
                md5cs, a32cs, fs = cp.transfer()
                #it suffices to check only the filesize as transfer result
                #if the checksums whould have been different between source, local, and/or 'lta'
                #then an exception would have been raised, and that is asserted below
                self.assertEqual(1000, int(fs))
            except Exception as e:
                logger.exception(e)
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)
            finally:
                os.remove(test_file_path)

        def test_multiple_files(self):
            test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1())
            os.makedirs(test_dir_path)
            test_file_paths = []
            for i in range(10):
                test_file_path = os.path.join(test_dir_path, 'testfile_%s.txt' % i)
                with open(test_file_path, 'w') as file:
                    file.write(1000*'a')

                if i%2==0: #only transfer half the files in the directory
                    test_file_paths.append(test_file_path)

            try:
                cp = ltacp.LtaCp('localhost', test_file_paths, 'srm://fake_surl')
                md5cs, a32cs, fs = cp.transfer()
            except Exception as e:
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)
            finally:
                for f in os.listdir(test_dir_path):
                    os.remove(os.path.join(test_dir_path, f))
                os.removedirs(test_dir_path)

        def test_directory(self):
            test_dir_path = os.path.join(os.getcwd(), 'testdir_%s' % uuid.uuid1())
            os.makedirs(test_dir_path)
            for i in range(10):
                test_file_path = os.path.join(test_dir_path, 'testfile_%s.txt' % i)
                with open(test_file_path, 'w') as file:
                    file.write(1000*'a')

            try:
                cp = ltacp.LtaCp('localhost', test_dir_path, 'srm://fake_surl')
                md5cs, a32cs, fs = cp.transfer()
            except Exception as e:
                self.assertTrue(False, 'Unexpected exception in transfer: %s' % e)
            finally:
                for f in os.listdir(test_dir_path):
                    os.remove(os.path.join(test_dir_path, f))
                os.removedirs(test_dir_path)


    if __name__ == '__main__':
        from subprocess import call
        if call(['ssh', '-o', 'PasswordAuthentication=no', '-o', 'PubkeyAuthentication=yes', '-o', 'ConnectTimeout=1', 'localhost', 'true']) != 0:
            print('this test depends on keybased ssh login to localhost, which is not setup correctly. skipping test...')
            exit(3)
        
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            level=logging.DEBUG)
        unittest.main()
