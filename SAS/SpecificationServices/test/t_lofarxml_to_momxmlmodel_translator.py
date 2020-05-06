#!/usr/bin/env python3

# t_lofarxml_to_momxmlmodel_translator.py
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

import unittest

from lofar.specificationservices.lofarxml_to_momxmlmodel_translator import LofarXMLToMomXMLModelTranslator
from lxml.etree import XMLSyntaxError


class TestLofarXMLToMomXMLModelTranslator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lofar_spec = _read_lofar_spec()

    def test_generateModel_should_raise_exception_on_empty_xml_string(self):
        translator = LofarXMLToMomXMLModelTranslator()

        with self.assertRaises(XMLSyntaxError):
            translator.generate_model("")

    def test_generateModel_should_not_raise_exception_on_correct_project_code_LC7_030(self):
        translator = LofarXMLToMomXMLModelTranslator()

        translator.generate_model(self.lofar_spec)

    def test_generateModel_should_not_raise_exception_on_correct_project_code_test_lofar(self):
        test_lofar_project_spec = _read_lofar_spec()

        test_lofar_project_spec = test_lofar_project_spec.replace("LC7_030", "test-lofar")

        translator = LofarXMLToMomXMLModelTranslator()

        translator.generate_model(test_lofar_project_spec)

    def test_generateModel_should_raise_exception_on_incorrect_project_code(self):
        lofar__wrong_project_spec = _read_lofar_spec()

        lofar__wrong_project_spec = lofar__wrong_project_spec.replace("LC7_030", "WRONG")

        translator = LofarXMLToMomXMLModelTranslator()

        with self.assertRaises(NotImplementedError):
            translator.generate_model(lofar__wrong_project_spec)

    def test_generateModel_should_return_model_filled_with_start_time(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.start_time, "2016-11-23T15:21:44")

    def test_generateModel_should_return_model_filled_with_duration(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.duration, "PT3600S")

    def test_generateModel_should_return_model_filled_with_target_ra(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.target_ra, "204.648425")

    def test_generateModel_should_return_model_filled_with_target_dec(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.target_dec, "-0.172222222222")

    def test_generateModel_should_return_model_filled_with_calibrator_ra(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.calibrator_ra, "123.400291667")

    def test_generateModel_should_return_model_filled_with_calibrator_dec(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.calibrator_dec, "48.2173833333")

    def test_generateModel_should_return_modele_filled_with_trigger_id(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEqual(model.trigger_id, 1)

    def test_generateModel_should_return_model_filled_with_station_selection(self):
        translator = LofarXMLToMomXMLModelTranslator()
        model = translator.generate_model(self.lofar_spec)
        expected = {"CS001": 1, "CS002": 1, "CS003": 1, "CS004": 1, "CS005": 1, "CS006": 1, "CS007": 1, "CS011": 1,
                    "CS013": 1, "CS017": 1, "CS021": 1, "CS024": 1, "CS026": 1, "CS028": 1, "CS030": 1, "CS031": 1,
                    "CS032": 1, "CS101": 1, "CS103": 1, "CS201": 1, "CS301": 1, "CS302": 1, "CS401": 1, "CS501": 1,
                    "RS106": 1, "RS205": 1, "RS208": 1, "RS210": 1, "RS305": 1, "RS306": 1, "RS307": 1, "RS310": 1,
                    "RS406": 1, "RS407": 1, "RS409": 1, "RS503": 1, "RS508": 1, "RS509": 1, 'INTERNATIONAL': '3'}
        self.assertEqual(model.station_selection, expected)

    def test_generate_model_should_return_model_filled_with_correct_foldernames(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEqual(model.inner_foldername, "AARTFAAC-TRIGGERED")
        self.assertEqual(model.outer_foldername, "TARGET_A")

    def test_generateModel_should_return_model_filled_with_project_code(self):
        translator = LofarXMLToMomXMLModelTranslator()

        model = translator.generate_model(self.lofar_spec)

        self.assertEquals(model.projectname, "LC7_030")


def _read_lofar_spec():
    f = open("t_lofarxml_to_momxmlmodel_translator.in_xml/type-1-lofar.xml", "r")

    lofar_xml = f.read()

    return lofar_xml


if __name__ == '__main__':
    unittest.main()
