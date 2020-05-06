#!/usr/bin/env python3

import unittest
import tempfile
from lofar.common.util import *

def setUpModule():
    pass

def tearDownModule():
    pass

class TestUtils(unittest.TestCase):
    def test_is_iterable(self):
        #list
        self.assertTrue(is_iterable([]))
        self.assertTrue(is_iterable([1, 2, 3]))

        #dict
        self.assertTrue(is_iterable({}))
        self.assertTrue(is_iterable({1:2, 3:4}))

        #tuple
        self.assertTrue(is_iterable((1,2,4)))

        #string
        self.assertTrue(is_iterable("abc"))

        # non-iterale types
        self.assertFalse(is_iterable(1))
        self.assertFalse(is_iterable(None))


def main(argv):
    unittest.main()

if __name__ == "__main__":
    # run all tests
    import sys
    main(sys.argv[1:])
