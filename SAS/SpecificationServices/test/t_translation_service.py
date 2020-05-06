#!/usr/bin/env python3

# t_translation_service.py
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

from lofar.specificationservices.translation_service import SpecificationTranslationHandler, FULL_TRANSLATION, MODEL_TRANSLATION
from lofar.common.test_utils import assertEqualXML
import os.path
from unittest import mock

GENERATE_GOLDEN_OUTPUT = False  # overwrite generic translation golden output


class TestSpecificationTranslationHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lofar_file_handler = open("t_translation_service.in_xml/type-1-lofar.xml", "r")
        cls.xml_type1 = lofar_file_handler.read()

        lofar_file_handler_minmax = open("t_translation_service.in_xml/type-1-lofar-minmax.xml", "r")
        cls.xml_type1_minmax = lofar_file_handler_minmax.read()

        lofar_file_handler = open("t_translation_service.in_xml/type-2-lofar.xml", "r")
        cls.xml_type2 = lofar_file_handler.read()

        lofar_file_handler = open("t_translation_service.in_xml/type-3-lofar.xml", "r")
        cls.xml_type3 = lofar_file_handler.read()

        # Note: We got MoM spec provided by the RO (I think) and we do not match that 100% with the generic translation
        # (different topologies and some obsolete items are missing). I would like to keep the provided templates for
        # reference and not adapt them to match the generic output for these tests. This means that we have two sets,
        # one based on the provided templates (for the model translation) and one with golden output of the generic
        # translation. Setting the GENERATE_GOLDEN_OUTPUT flag will overwrite this second set of expected output. This
        # can be used after changes to translation or the input, but the contents should always be thoroughly checked!

        # For model-based translation:

        mom_file_handler = open("t_translation_service.in_xml/telescope_model_xml_generator_type1.xml", "r")
        cls.expected_momxml_type1 = mom_file_handler.read()

        mom_file_handler = open("t_translation_service.in_xml/telescope_model_xml_generator_type1-minmax.xml", "r")
        cls.expected_momxml_type1_minmax = mom_file_handler.read()

        mom_file_handler = open("t_translation_service.in_xml/RTtemplateIMhba_type2.xml", "r")
        cls.expected_momxml_type2 = mom_file_handler.read()

        mom_file_handler = open("t_translation_service.in_xml/RTtemplateBF_type3.xml", "r")
        cls.expected_momxml_type3 = mom_file_handler.read()

        # For generic translation (file handlers are created in tests, since they are writing):

        testdir = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))
        cls.expected_momxml_direct_type1 = testdir + "/t_translation_service.in_xml/direct_xml_translation_type1.xml"
        cls.expected_momxml_direct_type1_minmax = testdir + "/t_translation_service.in_xml/direct_xml_translation_type1_minmax.xml"
        cls.expected_momxml_direct_type2 = testdir + "/t_translation_service.in_xml/direct_xml_translation_type2.xml"
        cls.expected_momxml_direct_type3 = testdir + "/t_translation_service.in_xml/direct_xml_translation_type3.xml"

    def setUp(self):
        validationrpc_patcher = mock.patch('lofar.specificationservices.translation_service.ValidationRPC.validate_mom_specification')
        self.addCleanup(validationrpc_patcher.stop)
        self.validationrpc_mock = validationrpc_patcher.start()
        self.validationrpc_mock.return_value = {"valid": True}

    def test_specification_to_momspecification_should_raise_exception_if_momspec_is_invalid(self):
        self.validationrpc_mock.return_value = {"valid": False}

        handler = SpecificationTranslationHandler()

        with self.assertRaises(Exception) as exception:
            handler.specification_to_momspecification(self.xml_type1, translation_mode=MODEL_TRANSLATION)

        self.assertEqual(str(exception.exception), "MoM specification validation after translation failed! -> {'valid': False}")

    def test_specification_to_momspecification_model_translation_should_return_expected_type1_mom_xml(self):
        handler = SpecificationTranslationHandler()

        momxml = handler.specification_to_momspecification(self.xml_type1, translation_mode=MODEL_TRANSLATION)

        assertEqualXML(momxml["mom-specification"], self.expected_momxml_type1)

    def test_specification_to_momspecification_model_translation_should_return_expected_type1_mom_xml_with_constraints(self):
        handler = SpecificationTranslationHandler()

        momxml = handler.specification_to_momspecification(self.xml_type1_minmax, translation_mode=MODEL_TRANSLATION)

        assertEqualXML(momxml["mom-specification"], self.expected_momxml_type1_minmax)

    #@unittest.skip("Skipping direct translation tests")
    def test_specification_to_momspecification_direct_translation_should_return_expected_type1_mom_xml(self):
        handler = SpecificationTranslationHandler()

        momxml = handler.specification_to_momspecification(self.xml_type1, translation_mode=FULL_TRANSLATION)

        with open(self.expected_momxml_direct_type1, "r+") as f:
            if GENERATE_GOLDEN_OUTPUT:
                f.write(momxml["mom-specification"])
            else:
                assertEqualXML(momxml["mom-specification"], f.read())

    #@unittest.skip("Skipping direct translation tests")
    def test_specification_to_momspecification_direct_translation_should_return_expected_type1_mom_xml_with_constraints(self):
        handler = SpecificationTranslationHandler()

        momxml_minmax = handler.specification_to_momspecification(self.xml_type1_minmax, translation_mode=FULL_TRANSLATION)

        with open(self.expected_momxml_direct_type1_minmax, "r+") as f:
            if GENERATE_GOLDEN_OUTPUT:
                f.write(momxml_minmax["mom-specification"])
            else:
                assertEqualXML(momxml_minmax["mom-specification"], f.read())

    #@unittest.skip("Skipping direct translation tests")
    def test_specification_to_momspecification_direct_translation_should_return_expected_type2_mom(self):
        handler = SpecificationTranslationHandler()

        momxml = handler.specification_to_momspecification(self.xml_type2, translation_mode=FULL_TRANSLATION)

        with open(self.expected_momxml_direct_type2, "r+") as f:
            if GENERATE_GOLDEN_OUTPUT:
                f.write(momxml["mom-specification"])
            else:
                assertEqualXML(momxml["mom-specification"], f.read())

    #@unittest.skip("Skipping direct translation tests")
    def test_specification_to_momspecification_direct_translation_should_return_expected_type3_mom(self):
        handler = SpecificationTranslationHandler()

        momxml = handler.specification_to_momspecification(self.xml_type3, translation_mode=FULL_TRANSLATION)

        with open(self.expected_momxml_direct_type3, "r+") as f:
            if GENERATE_GOLDEN_OUTPUT:
                f.write(momxml["mom-specification"])
            else:
                assertEqualXML(momxml["mom-specification"], f.read())


if __name__ == '__main__':
    unittest.main()

