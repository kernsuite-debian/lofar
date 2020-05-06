#!/usr/bin/env python3
import logging
import time
import os, os.path
from lxml import etree
from io import StringIO, BytesIO

logger = logging.getLogger(__name__)

def validateSIPAgainstSchema(sip, log_prefix=''):
    try:
        if log_prefix:
            if not isinstance(log_prefix, str):
                log_prefix = str(log_prefix)
            if log_prefix[-1] != ' ':
                log_prefix += ' '

        logger.debug("%svalidateSIPAgainstSchema starting", log_prefix)
        start  = time.time()

        lofarrootdir = os.environ.get('LOFARROOT', '/opt/lofar')
        sip_xsd_path = os.path.join(lofarrootdir, 'etc', 'lta', 'LTA-SIP.xsd')

        if not os.path.exists(sip_xsd_path):
            logger.error('Could not find LTA-SIP.xsd at %s', sip_xsd_path)
            return False

        with open(sip_xsd_path) as xsd_file:
            xsd_contents = etree.parse(xsd_file)
            schema       = etree.XMLSchema(xsd_contents)
            sip_io       = BytesIO(sip if isinstance(sip, bytes) else sip.encode('utf-8'))
            sip_xml      = etree.parse(sip_io)
            result       = schema.validate(sip_xml)
            if time.time() - start > 1:
                logger.debug("%svalidateSIPAgainstSchema took %ds", log_prefix, time.time() - start)
            if not result:
                for error_log_line in schema.error_log:
                    logger.error("%svalidateSIPAgainstSchema: %s", log_prefix, error_log_line)
            return result
    except Exception as e:
        logger.error('%svalidateSIPAgainstSchema raised an exception: %s', log_prefix, e)
        return False

def checkSIPContent(sip, archive_id=None, filename=None, storage_ticket=None, filesize=None, md5_checksum=None, adler32_checksum=None, log_prefix=''):
    try:
        if log_prefix:
            if not isinstance(log_prefix, str):
                log_prefix = str(log_prefix)
            if log_prefix[-1] != ' ':
                log_prefix += ' '

        logger.debug("%scheckSIPContent starting", log_prefix)
        start  = time.time()

        sip_io       = BytesIO(sip if isinstance(sip, bytes) else sip.encode('utf-8'))
        xml_tree     = etree.parse(sip_io)
        xml_root     = xml_tree.getroot()

        dataProducts = xml_root.xpath('dataProduct')
        if len(dataProducts) != 1:
            logger.error("%scheckSIPContent could not find single dataProduct in SIP", log_prefix)
            return False

        dataProductIdentifierIDs = dataProducts[0].xpath('dataProductIdentifier/identifier')
        if len(dataProductIdentifierIDs) != 1:
            logger.error("%scheckSIPContent could not find single dataProductIdentifier/identifier in SIP dataProduct", log_prefix)
            return False
        if archive_id and dataProductIdentifierIDs[0].text != str(archive_id):
            logger.error("%scheckSIPContent dataProductIdentifier/identifier %s does not match expected %s", log_prefix, dataProductIdentifierIDs[0].text, archive_id)
            return False

        dataProductIdentifierNames = dataProducts[0].xpath('dataProductIdentifier/name')
        if len(dataProductIdentifierNames) >= 1 and filename and not dataProductIdentifierNames[0].text in filename:
            logger.error("%scheckSIPContent dataProductIdentifier/name %s does not match expected %s", log_prefix, dataProductIdentifierNames[0].text, filename)
            return False

        if storage_ticket:
            storageTickets = dataProducts[0].xpath('storageTicket')
            if len(storageTickets) != 1:
                logger.error("%scheckSIPContent could not find single storageTickets in SIP dataProduct", log_prefix)
                return False
            if storageTickets[0].text != storage_ticket:
                logger.error("%scheckSIPContent storageTicket %s does not match expected %s", log_prefix, storageTickets[0].text, storage_ticket)
                return False

        if filesize:
            sizes = dataProducts[0].xpath('size')
            if len(sizes) != 1:
                logger.error("%scheckSIPContent could not find single size in SIP dataProduct", log_prefix)
                return False
            if sizes[0].text != str(filesize):
                logger.error("%scheckSIPContent filesize %s does not match expected %s", log_prefix, sizes[0].text, filesize)
                return False

        if md5_checksum or adler32_checksum:
            checksums = dataProducts[0].xpath('checksum')
            if len(checksums) == 0:
                logger.error("%scheckSIPContent could not find checksum(s) in SIP dataProduct", log_prefix)
                return False

            if md5_checksum:
                md5_checksums = [x for x in checksums if x.xpath('algorithm') and x.xpath('algorithm')[0].text == 'MD5']

                if len(md5_checksums) != 1:
                    logger.error("%scheckSIPContent could not find single md5 checksum in SIP dataProduct", log_prefix)
                    return False

                if md5_checksums[0].xpath('value')[0].text != str(md5_checksum):
                    logger.error("%scheckSIPContent md5_checksum %s does not match expected %s", log_prefix, md5_checksums[0].xpath('value')[0].text, md5_checksum)
                    return False

            if adler32_checksum:
                adler32_checksums = [x for x in checksums if x.xpath('algorithm') and x.xpath('algorithm')[0].text == 'Adler32']

                if len(adler32_checksums) != 1:
                    logger.error("%scheckSIPContent could not find single adler32 checksum in SIP dataProduct", log_prefix)
                    return False

                if adler32_checksums[0].xpath('value')[0].text != str(adler32_checksum):
                    logger.error("%scheckSIPContent adler32_checksum %s does not match expected %s", log_prefix, adler32_checksums[0].xpath('value')[0].text, adler32_checksum)
                    return False

        if time.time() - start > 1:
            logger.debug("%sscheckSIPContent took %ds", log_prefix, time.time() - start)

        logger.debug("%scheckSIPContent OK", log_prefix)
        return True
    except Exception as e:
        logger.error('%scheckSIPContent raised an exception: %s', log_prefix, e)
        return False

def addIngestInfoToSIP(sip, storage_ticket, filesize, md5_checksum, adler32_checksum):
    # parse sip xml and add filesize, storageticket and checkums

    logger.info("addIngestInfoToSIP(storage_ticket=%s, filesize=%s, md5_checksum=%s, adler32_checksum=%s)",
                storage_ticket, filesize, md5_checksum, adler32_checksum)

    from xml.dom import minidom
    sip_dom = minidom.parseString(sip.decode('utf-8') if isinstance(sip, bytes) else sip)
    dp_node = sip_dom.getElementsByTagName('dataProduct')[0]

    for elem in dp_node.getElementsByTagName('storageTicket'):
            dp_node.removeChild(elem)

    for elem in dp_node.getElementsByTagName('size'):
            dp_node.removeChild(elem)

    for elem in dp_node.getElementsByTagName('checksum'):
            dp_node.removeChild(elem)

    sip_namespace = "http://www.astron.nl/SIP-Lofar"
    storageticket_node = sip_dom.createElementNS(sip_namespace, 'storageTicket')
    storageticket_node.appendChild(sip_dom.createTextNode(str(storage_ticket)))

    size_node = sip_dom.createElementNS(sip_namespace, 'size')
    size_node.appendChild(sip_dom.createTextNode(str(filesize)))

    checksum_md5_algo_node = sip_dom.createElementNS(sip_namespace, 'algorithm')
    checksum_md5_algo_node.appendChild(sip_dom.createTextNode('MD5'))
    checksum_md5_value_node = sip_dom.createElementNS(sip_namespace, 'value')
    checksum_md5_value_node.appendChild(sip_dom.createTextNode(str(md5_checksum)))
    checksum_md5_node = sip_dom.createElementNS(sip_namespace, 'checksum')
    checksum_md5_node.appendChild(checksum_md5_algo_node)
    checksum_md5_node.appendChild(checksum_md5_value_node)

    checksum_a32_algo_node = sip_dom.createElementNS(sip_namespace, 'algorithm')
    checksum_a32_algo_node.appendChild(sip_dom.createTextNode('Adler32'))
    checksum_a32_value_node = sip_dom.createElementNS(sip_namespace, 'value')
    checksum_a32_value_node.appendChild(sip_dom.createTextNode(str(adler32_checksum)))
    checksum_a32_node = sip_dom.createElementNS(sip_namespace, 'checksum')
    checksum_a32_node.appendChild(checksum_a32_algo_node)
    checksum_a32_node.appendChild(checksum_a32_value_node)

    dp_node.insertBefore(checksum_a32_node, dp_node.getElementsByTagName('fileName')[0])
    dp_node.insertBefore(checksum_md5_node, checksum_a32_node)
    dp_node.insertBefore(size_node, checksum_md5_node)
    dp_node.insertBefore(storageticket_node, size_node)

    return sip_dom.toxml("utf-8")

