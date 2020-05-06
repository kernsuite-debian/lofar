#!/usr/bin/env python3
#  t_validation_service.py
#
# Copyright (C) 2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import os
import unittest
from unittest.mock import patch

from lofar.specificationservices.validation_service import *

INPUT_XML_DIR = "t_validation_service.in_xml"
INPUT_TYPE1_LOFAR_XML = "type-1-lofar.xml"
INPUT_TYPE1_TRIGGER_XML = "type-1-trigger.xml"
INPUT_TYPE1_MOM_XML = "type-1-mom.xml"


class TestValidationService(unittest.TestCase):
    def setUp(self):
        input_xml_path = os.path.join(os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__))),
                                      INPUT_XML_DIR)

        self.sample_lofar_xml = self.get_xml_from_file(os.path.join(input_xml_path, INPUT_TYPE1_LOFAR_XML))
        self.sample_trigger_xml = self.get_xml_from_file(os.path.join(input_xml_path, INPUT_TYPE1_TRIGGER_XML))
        self.sample_mom_xml = self.get_xml_from_file(os.path.join(input_xml_path, INPUT_TYPE1_MOM_XML))

    def get_xml_from_file(self, filepath):
        f = open(filepath, "r")
        xmlcontent = f.read()
        f.close()
        return xmlcontent

    # todo: the service map is not around anymore. Do we have to test anything equivalent with new RabbitMQ setup?
    # def test_validation_service_method_map_should_be_correct(self):
    #     uut = ValidationHandler()
    #
    #     self.assertEqual(uut.service2MethodMap["validate_trigger_specification"], uut.validate_trigger_specification)
    #     self.assertEqual(uut.service2MethodMap["validate_specification"], uut.validate_specification)
    #     self.assertEqual(uut.service2MethodMap["validate_mom_specification"], uut.validate_mom_specification)

    def test_validate_specification_should_raise_exception_on_invalid_xsd(self):
        xml = self.sample_lofar_xml
        xsd = ""
        uut = ValidationHandler()

        with patch('lofar.specificationservices.validation_service.LOFARSPEC_XSD', new=xsd):
            self.assertRaises(Exception, uut.validate_specification, xml)

    def test_validate_specification_should_fail_on_invalid_xml(self):
        xml = ""
        uut = ValidationHandler()

        result = uut.validate_specification(xml)

        self.assertFalse(result["valid"])

    def test_validate_trigger_specification_should_fail_on_invalid_xml(self):
        xml = ""
        uut = ValidationHandler()

        result = uut.validate_trigger_specification(xml)

        self.assertFalse(result["valid"])

    def test_validate_mom_specification_should_fail_on_invalid_xml(self):
        xml = ""
        uut = ValidationHandler()

        result = uut.validate_mom_specification(xml)

        self.assertFalse(result["valid"])

    def test_validate_specification_should_fail_on_unsupported_xml(self):
        xml = "<test />"
        uut = ValidationHandler()

        result = uut.validate_specification(xml)

        self.assertFalse(result["valid"])

    def test_validate_specification_should_succeed_on_valid_lofar_xml(self):
        xml = self.sample_lofar_xml
        uut = ValidationHandler()

        result = uut.validate_specification(xml)

        self.assertTrue(result["valid"])

    def test_validate_specification_should_succeed_on_valid_trigger_xml(self):
        xml = self.sample_trigger_xml
        uut = ValidationHandler()

        result = uut.validate_trigger_specification(xml)

        self.assertTrue(result["valid"])

    def test_validate_specification_should_succeed_on_valid_mom_xml(self):
        xml = self.sample_mom_xml
        uut = ValidationHandler()

        result = uut.validate_mom_specification(xml)

        self.assertTrue(result["valid"])

if __name__ == '__main__':
    unittest.main()
