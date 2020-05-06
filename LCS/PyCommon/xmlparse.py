from lxml import etree
from io import BytesIO

from typing import Union

def parse_xml_string_or_bytestring(xml_content: Union[str, bytes], parser=None) -> etree:
    """
    Parse the given xml content and returns a Etree
    :param xml_content: content of the xml file
    :return: the parsed content in the form of an element tree
    """
    if isinstance(xml_content, str):
        bstr = xml_content.encode('utf8')
    else:
        bstr = xml_content

    return etree.parse(BytesIO(bstr), parser=parser)