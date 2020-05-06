#!/usr/bin/env python3
#  t_telescope_model_xml_generator_type1.py
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
from lxml import etree
from io import BytesIO

from lofar.specificationservices.telescope_model import TelescopeModel
from lofar.specificationservices.telescope_model_xml_generator_type1 import TelescopeModelXMLGeneratorType1
from lofar.specificationservices.telescope_model_xml_generator_type1 import TelescopeModelException
from lofar.common.test_utils import assertEqualXML


GOLDEN_OUTPUT_DIR = "t_telescope_model_xml_generator_type1.in_xml"
GOLDEN_OUTPUT_FILENAME = "telescope_model_xml_generator_type1.xml"


class TestTelescopeModelXMLGeneratorType1(unittest.TestCase):
    def setUp(self):
        self.xmldoc = None
        self.generate_golden_output = False
        self.golden_output_file = os.path.join(
            os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__))),
            GOLDEN_OUTPUT_DIR, GOLDEN_OUTPUT_FILENAME)
        self.model = TelescopeModel()
        self.model.target_ra = "204.648425"
        self.model.target_dec = "-0.172222222222"
        self.model.calibrator_ra = "123.400291667"
        self.model.calibrator_dec = "48.2173833333"
        self.model.start_time = "2016-11-23T15:21:44"
        self.model.duration = "PT3600S"
        self.model.trigger_id = 333
        self.model.min_start_time = "2016-10-23T15:21:44"
        self.model.max_end_time = "2017-11-23T15:21:44"
        self.model.min_duration = "PT3600S"
        self.model.max_duration = "PT7200S"
        self.model.station_selection = {"INTERNATIONAL": 4, "CS001": 1, "CS002":1, "RS210": 1}
        self.model.custom_station_list = ["CS001", "CS002", "RS210"]
        self.model.inner_foldername = 'myinnerfolder'
        self.model.outer_foldername = 'myouterfolder'
        self.model.projectname = 'myproject'

    def tearDown(self):
        if self.generate_golden_output and self.xmldoc is not None:
            self.store_golden_output(self.xmldoc)

    def store_golden_output(self, xmldoc):
        with open(self.golden_output_file, 'w+') as f:
            f.write(etree.tostring(self.xmldoc, pretty_print=True).decode('utf-8'))

    def test_get_xml_tree_should_raise_exception_on_empty_model(self):
        generator = TelescopeModelXMLGeneratorType1()

        with self.assertRaises(TelescopeModelException):
            generator.get_xml_tree(None)

    def test_get_xml_tree_should_not_raise_exception_on_valid_model(self):
        generator = TelescopeModelXMLGeneratorType1()
        # Store to self.xmldoc, so that a golden output can be made form it in self.tearDown()
        self.xmldoc = generator.get_xml_tree(self.model)

    def test_get_xml_tree_result_should_equal_golden_output(self):
        golden_xmldoc = self.get_xmldoc_of_golden_output_as_string()

        generator = TelescopeModelXMLGeneratorType1()
        xmldoc = generator.get_xml_tree(self.model)
        result = str(etree.tostring(xmldoc), "UTF-8")

        assertEqualXML(result, golden_xmldoc)

    def get_xmldoc_of_golden_output_as_string(self):
        with open(self.golden_output_file, "r") as f:
            xmlcontent = f.read()

        xmldoc = etree.parse(BytesIO(xmlcontent.encode('UTF-8')))
        return str(etree.tostring(xmldoc), "UTF-8")


if __name__ == '__main__':
    unittest.main()
