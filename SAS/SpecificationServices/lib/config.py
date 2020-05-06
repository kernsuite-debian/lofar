from lofar.common import isProductionEnvironment, isTestEnvironment

""" Config file for specification services. """

# Messaging

VALIDATION_SERVICENAME = "specificationvalidationservice"

SPECIFICATION_SERVICENAME = "specificationservice"

SPECIFICATIONTRANSLATION_SERVICENAME = "specificationtranslationservice"

# TODO: mom.importxml does not prepend "test." on the test system?
MOMIMPORTXML_BUSNAME = "mom.importxml"

MOMIMPORTXML_BROKER = "lcs023.control.lofar" if isProductionEnvironment() else \
                      "lcs028.control.lofar" if isTestEnvironment() else \
                      "localhost"

# XSD paths (for validation service)
TRIGGER_XSD = "$LOFARROOT/share/SAS/LofarTrigger.xsd"
LOFARSPEC_XSD = "$LOFARROOT/share/SAS/LofarSpecification.xsd"
MOMSPEC_XSD = "$LOFARROOT/share/MoM/LofarMoM2.xsd"

# Telescope Model XML paths (for xml generators used by translation service)
TELESCOPE_MODEL_TYPE1_XML = "$LOFARROOT/share/xml/telescope_model_type1_template.xml"
TELESCOPE_MODEL_TYPE2_XML = "$LOFARROOT/share/xml/telescope_model_type2_template.xml"
