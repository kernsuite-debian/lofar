#!/usr/bin/env python

import unittest
import tempfile
from lofar.common.util import *

def setUpModule():
    pass

def tearDownModule():
    pass

class TestUtils(unittest.TestCase):
    def test_string_to_buffer_and_back(self):
        original = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit.'

        d = { 'test-key' : original }
        #print str(d)
        self.assertTrue(isinstance(d['test-key'], basestring))

        d2 = convertStringValuesToBuffer(d, 0)
        print d2
        self.assertTrue(isinstance(d2['test-key'], buffer))

        d3 = convertBufferValuesToString(d2)
        print d3
        self.assertTrue(isinstance(d3['test-key'], basestring))
        self.assertEqual(original, d3['test-key'])

        #try conversion again but only for long strings
        d2 = convertStringValuesToBuffer(d, 10000)
        print d2
        #type should still be basestring (so no conversion happened)
        self.assertTrue(isinstance(d2['test-key'], basestring))

        d3 = convertBufferValuesToString(d2)
        print d3
        #type should still be basestring (so no conversion back was needed)
        self.assertTrue(isinstance(d3['test-key'], basestring))
        self.assertEqual(original, d3['test-key'])

        #try with nested dict
        d4 = { 'outer': d }

        d2 = convertStringValuesToBuffer(d4, 0)
        print d2
        self.assertTrue(isinstance(d2['outer']['test-key'], buffer))

        d3 = convertBufferValuesToString(d2)
        print d3
        self.assertTrue(isinstance(d3['outer']['test-key'], basestring))
        self.assertEqual(original, d3['outer']['test-key'])

def main(argv):
    unittest.main()

if __name__ == "__main__":
    # run all tests
    import sys
    main(sys.argv[1:])
