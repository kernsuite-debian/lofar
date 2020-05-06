#!/usr/bin/env python3

import logging
import unittest
from lofar.lta.ingest.server.sip import *
from lofar.lta.ingest.server.unspecifiedSIP import *

logger = logging.getLogger(__file__)

class TestSIP(unittest.TestCase):
    def test_valid_SIP(self):
        sip = makeSIP('project', 123456, 234567, 'abc-123', 'foo.txt', 0, '', '', 'TEST', 'LofarStorageManager', 'Unknown')
        logger.info(sip)
        self.assertTrue(validateSIPAgainstSchema(sip))

    def test_invalid_SIP_with_incorrect_storageWriter(self):
        sip = makeSIP('project', 123456, 234567, 'abc-123', 'foo.txt', 0, '', '', 'TEST', 'incorrect-storageWriter', 'Unknown')
        logger.info(sip)
        self.assertFalse(validateSIPAgainstSchema(sip))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    unittest.main()
