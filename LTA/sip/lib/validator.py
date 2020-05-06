
from lxml import etree
import os
from . import ltasip

d = os.path.dirname(os.path.realpath(__file__))
XSDPATH = d+"/LTA-SIP.xsd"

DEFAULT_SIP_XSD_PATH = os.path.join(os.environ.get('LOFARROOT', '/opt/lofar'), 'etc', 'lta', 'LTA-SIP.xsd')

def validate(xmlpath, xsdpath=DEFAULT_SIP_XSD_PATH):
    '''validates given xml file against given xsd file'''

    print("validating", xmlpath, "against", xsdpath)

    with open(xsdpath) as xsd:
        xmlschema_doc = etree.parse(xsd)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        with open(xmlpath) as xml:
            doc = etree.parse(xml)
            valid = xmlschema.validate(doc)

            if not valid:
                try:
                    xmlschema.assertValid(doc)
                except Exception as err:
                    print(err)

            print("SIP is valid according to schema definition!")
            return valid


def check_consistency(xmlpath):
    """
    Checks the general structure of the provided SIP XML. E.g.:
    Is/Are the processes/es present that created the described dataproduct / related dataproducts?
    Are the input dataproducts for these processes present?
    """

    print("Checking", xmlpath, "for structural consistency")

    with open(xmlpath) as f:
        xml = f.read()
        sip = ltasip.CreateFromDocument(xml)


        linkstodataproduct = {}
        linkstoprocess = {}

        # the dataproduct that is described by the sip
        data_out =  sip.dataProduct
        id_out = str(data_out.dataProductIdentifier.identifier)
        id_process = str(data_out.processIdentifier.identifier)
        linkstodataproduct.setdefault(id_out,[]).append(id_process)

        # the input / intermediate dataproducts
        for data_in in sip.relatedDataProduct:
            id_in = str(data_in.dataProductIdentifier.identifier)
            id_process = str(data_in.processIdentifier.identifier)
            linkstodataproduct.setdefault(id_in,[]).append(id_process)

        # the observations
        for obs in sip.observation:
            id_obs = str(obs.observationId.identifier)
            id_process = str(obs.processIdentifier.identifier)
            linkstoprocess.setdefault(id_process,[])

        # the data processing steps
        for pipe in sip.pipelineRun:
            id_pipe = str(pipe.processIdentifier.identifier)
            id_in = []
            for id in pipe.sourceData.content():
                id_in.append(str(id.identifier))
            linkstoprocess.setdefault(id_pipe,[]).append(id_in)

        # the data processing steps
        for unspec in sip.unspecifiedProcess:
            id_unspec = str(unspec.processIdentifier.identifier)
            linkstoprocess.setdefault(id_unspec,[])


        # todo: online processing
        # todo: parsets (?)

        for id in linkstodataproduct:
            for id_from in linkstodataproduct.get(id):
                if not id_from in linkstoprocess:
                    raise Exception("The pipeline or observation that created dataproduct '"+ id + "' seems to be missing! -> ", id_from)

        for id in linkstoprocess:
            for ids_from in linkstoprocess.get(id):
                for id_from in ids_from:
                    if not id_from in linkstodataproduct:
                        raise Exception("The input dataproduct for pipeline '"+ id +"' seems to be missing! -> ", id_from)

        print("General SIP structure seems ok!")
        return True # already raised Exception if there was a problem...


def main(xml):
    """
    validates given xml against the SIP XSD and does consistency check
    """

    try:
        xml = xml
        xsd = DEFAULT_SIP_XSD_PATH
        valid = validate(xml, xsd)
        consistent = check_consistency(xml)
        return valid and consistent
    except Exception as err:
        print("An error occurred:")
        print(err)
