#!/usr/bin/env python

import unittest
import tempfile
from lofar.common.test_utils import *

def setUpModule():
    pass

def tearDownModule():
    pass

class TestTestUtils(unittest.TestCase):

    def test_assertEqualXML_passes_when_xml_equals(self):
        xml1 = '<xml><test att="1">testtext1</test></xml>'
        xml2 = xml1
        assertEqualXML(xml1, xml2)

    def test_assertEqualXML_passes_when_attribute_order_differs(self):
        xml1 = '<xml><test att1="1" att2="2">testtext1</test></xml>'
        xml2 = '<xml><test att2="2" att1="1">testtext1</test></xml>'
        assertEqualXML(xml1, xml2)

    def test_assertEqualXML_passes_with_irrelevant_whitespace(self):
        xml1 = '   <xml><test att1="1"    att2="2">testtext1</test>\t</xml>'
        xml2 = '<xml>   \n<test att2="2" att1="1">testtext1</test> </xml>'
        assertEqualXML(xml1, xml2)

    def test_assertEqualXML_raises_AssertionError_when_node_text_differs(self):
        xml1 = '<xml><test>testtext1</test></xml>'
        xml2 = '<xml><test>testtext2</test></xml>'
        with self.assertRaises(AssertionError):
            assertEqualXML(xml1, xml2)

    def test_assertEqualXML_raises_AssertionError_when_node_name_differs(self):
        xml1 = '<xml><test1>testtext</test1></xml>'
        xml2 = '<xml><test2>testtext</test2></xml>'
        with self.assertRaises(AssertionError):
            assertEqualXML(xml1, xml2)

    def test_assertEqualXML_raises_AssertionError_when_attribute_text_differs(self):
        xml1 = '<xml><test test="1">testtext</test></xml>'
        xml2 = '<xml><test test="2">testtext</test></xml>'
        with self.assertRaises(AssertionError):
            assertEqualXML(xml1, xml2)

    def test_assertEqualXML_raises_AssertionError_when_attribute_name_differs(self):
        xml1 = '<xml><test test1="1">testtext</test></xml>'
        xml2 = '<xml><test test2="1">testtext</test></xml>'
        with self.assertRaises(AssertionError):
            assertEqualXML(xml1, xml2)

    def test_assertEqualXML_raises_AssertionError(self):
        xml1 = '<xml><test att=" 1">testtext</test></xml>'
        xml2 = '<xml><test att="2">test text</test></xml>'
        with self.assertRaises(AssertionError):
            assertEqualXML(xml1, xml2)


def main(argv):
    unittest.main()

if __name__ == "__main__":
    # run all tests
    import sys
    main(sys.argv[1:])
