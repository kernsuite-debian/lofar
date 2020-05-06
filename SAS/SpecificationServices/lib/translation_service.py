#!/usr/bin/env python3

# translation_service.py
#
# Copyright (C) 2015
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


# This Service translates specifications. High level description:
#
# A) Trigger -> Lofar spec:
#
# Triggers contain a lofar spec element, so no further changes are needed than priority and identifier injection.
#
# B) From a generic LOFAR spec to MoM spec:
#
# Lofar specs are structured by relations that define how activities are connected, but Mom specs are structured as a
# tree, with nesting elements in a folder hiararchy. There are two approaches on how to translate between them:
#
# 1) We use a model-based translation that reads a few key values from the LofarSpec and places these in a well-defined template
#
# 2) We directly translate the Lofar XML to an equivalent MoM compatible version. See lofarxml_to_momxml_translator for the approach of the full translation


import logging

from lofar.specificationservices.lofarxml_to_momxmlmodel_translator import LofarXMLToMomXMLModelTranslator
from lofar.specificationservices.telescope_model_xml_generator_type1 import TelescopeModelXMLGeneratorType1

logger = logging.getLogger(__name__)
from lxml import etree
from io import BytesIO
from lofar.common.xmlparse import parse_xml_string_or_bytestring


from lofar.messaging import RPCService, ServiceMessageHandler, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import waitForInterrupt

from .config import SPECIFICATIONTRANSLATION_SERVICENAME

from .validation_service_rpc import ValidationRPC

from .lofarxml_to_momxml_translator import LofarXmlToMomXmlTranslator



# Translation modes:
FULL_TRANSLATION = "Full translation"
MODEL_TRANSLATION = "Model translation"

class SpecificationTranslationHandler(ServiceMessageHandler):
    def __init__(self):
        super().__init__()
        self.validationrpc = ValidationRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)

    def trigger_to_specification(self, trigger_spec, trigger_id, job_priority):

        logger.info("Translating Trigger spec to Lofar spec")
        logger.debug('trigger before translation ->' + trigger_spec)
        try:
            # pick the specification element
            parser = etree.XMLParser(remove_blank_text=True)
            doc = parse_xml_string_or_bytestring(trigger_spec, parser=parser)
            # spec = doc.getroot().find('{http://www.astron.nl/LofarSpecification}specification')
            root = doc.getroot()
            if not "trigger" in root.tag:
                raise Exception("XML doesn't seem to contain a trigger")
            spec = root.find('specification')
            logger.debug("root is " + str(spec.tag))

            # inject identifier and project priority
            for activity in spec.findall('activity'):
                priority = activity.find('priority')
                priority.text = str(int(priority.text) + int(job_priority))

                identifier = activity.find('triggerId')
                if identifier is not None:
                    activity.remove(identifier)  # remove any existing id (e.g. set by the user, the XSD allows this)
                identifier = etree.SubElement(activity, 'triggerId')
                etree.SubElement(identifier, 'source').text = 'MoM'
                etree.SubElement(identifier, 'identifier').text = str(trigger_id)

            # create xml string with correct namespace:
            lofarspec = etree.Element("{http://www.astron.nl/LofarSpecification}specification", nsmap=spec.nsmap)
            for child in spec.getchildren():
                lofarspec.append(child)
            specification_xml = etree.tostring(lofarspec, pretty_print=True).decode('utf8')
            logger.debug(specification_xml)
        except Exception as err:
            logger.error("Exception while translating trigger -> " + str(err))
            raise

        logger.debug("specification after translation from trigger -> " + specification_xml)
        with self.validationrpc:
            response = self.validationrpc.validate_specification(specification_xml)
        if response["valid"]:
            logger.info("Translation successful")
            return {"specification": specification_xml}
        else:
            raise Exception("Lofar specification validation after translation failed! -> " + str(response))

    def specification_to_momspecification(self, spec_xml, translation_mode=FULL_TRANSLATION):

        logger.info("Translating Lofar spec to MoM spec")
        logger.debug("Specification before translation -> " + spec_xml)
        momspec_xml = None

        # Template-based translation:

        if translation_mode == MODEL_TRANSLATION:
            lofar_translator = LofarXMLToMomXMLModelTranslator()
            telescope_model = lofar_translator.generate_model(spec_xml)

            type1_generator = TelescopeModelXMLGeneratorType1()
            momspec_xml_tree = type1_generator.get_xml_tree(telescope_model)
            momspec_xml = etree.tostring(momspec_xml_tree)

        elif translation_mode == FULL_TRANSLATION:
            try:
                lofar_translator = LofarXmlToMomXmlTranslator()
                momspec_xml = lofar_translator.translate_lofarspec_to_momspec(spec_xml)

            except Exception as err:
                logger.error("Exception while translating specification -> " + str(err))
                raise

        if isinstance(momspec_xml, bytes):
            momspec_xml = momspec_xml.decode("utf-8")

        logger.debug("MoM spec after translation -> " + momspec_xml)

        with self.validationrpc:
            response = self.validationrpc.validate_mom_specification(momspec_xml)
        if response["valid"]:
            logger.info("Translation successful")
            return {"mom-specification": momspec_xml}
        else:
            raise Exception("MoM specification validation after translation failed! -> " + str(response))


def create_service(busname=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
    return RPCService(SPECIFICATIONTRANSLATION_SERVICENAME,
                      SpecificationTranslationHandler,
                      exchange=busname,
                      broker=broker)


def main():
    with create_service():
        waitForInterrupt()
