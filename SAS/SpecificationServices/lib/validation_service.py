#!/usr/bin/env python3

# validation_service.py
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


# This service validates specifications provided as XML against according XSD definitions.


import logging
from io import BytesIO
from lxml import etree
import os
from lofar.messaging import ServiceMessageHandler, DEFAULT_BROKER, DEFAULT_BUSNAME, RPCService
from lofar.common.util import waitForInterrupt
from lofar.common.xmlparse import parse_xml_string_or_bytestring

from .config import TRIGGER_XSD, LOFARSPEC_XSD, MOMSPEC_XSD, VALIDATION_SERVICENAME

logger = logging.getLogger(__name__)

def _validateXSD(xml, xsdpath):
    '''validates given xml against given xsd file'''

    logger.info("Validating against " + str(xsdpath))
    logger.debug("XML: %s", xml)

    xsdpath = os.path.expandvars(xsdpath)

    with open(xsdpath) as xsd:
        # Construct XSD Schema
        xmlschema_doc = etree.parse(xsd)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # Try to parse the XML
        try:
            doc = parse_xml_string_or_bytestring(xml)
        except etree.LxmlError as err:
            logger.error(err)
            return {"valid": False, "error": "XML could not be parsed: %s" % (err,)}

        # Validate the XML against the XSD Schema
        valid = xmlschema.validate(doc)
        logger.info("xmlschema.validate: "+str(valid))

        if not valid:
            try:
                xmlschema.assertValid(doc) # this creates an exception with some details
            except etree.DocumentInvalid as err:
                logger.error(err)
                return {"valid": False, "error": "XML does not validate against schema: %s" % (err,)}

    return {"valid": True}


class ValidationHandler(ServiceMessageHandler):
    def __init__(self, **kwargs):
        super(ValidationHandler, self).__init__()

    def validate_trigger_specification(self, xml):
        return _validateXSD(xml, TRIGGER_XSD)

    def validate_specification(self, xml):
        # todo: further checks -> build relation graph, check for consistency!
        return _validateXSD(xml, LOFARSPEC_XSD)

    def validate_mom_specification(self, xml):
        # todo: further checks
        return _validateXSD(xml, MOMSPEC_XSD)



def create_service(busname=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
    return RPCService(VALIDATION_SERVICENAME,
                      ValidationHandler,
                      exchange=busname,
                      broker=broker)


def main():
    with create_service():
        waitForInterrupt()
