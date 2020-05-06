#!/usr/bin/env python3

import logging
import unittest
import uuid
import os, os.path
from lofar.lta.ingest.common.job import *

class TestJob(unittest.TestCase):
    def test_foo(self):
        path = os.path.join('/tmp', 'job_%s.xml' % uuid.uuid1())
        createJobXmlFile(path, 'test_project', 123456, 321654, 'my_dp', 789456, 'dev/null', priority=None)

        with open(path, 'r') as file:
            xml = file.read()
            self.assertFalse('priority' in xml)

        updatePriorityInJobFile(path, 7)

        with open(path, 'r') as file:
            xml = file.read()
            self.assertTrue('priority' in xml)

        job = parseJobXmlFile(path)
        self.assertEqual(job['priority'], 7)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    unittest.main()
