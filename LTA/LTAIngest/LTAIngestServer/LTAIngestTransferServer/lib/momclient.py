#!/usr/bin/env python3

import requests

import logging
logger = logging.getLogger()

from lofar.lta.ingest.common.job import jobState2String
from lofar.lta.ingest.server.config import MOM_BASE_URL
from lofar.common import isProductionEnvironment
from lofar.lta.ingest.server.sip import *
from lofar.common.util import humanreadablesize
from lofar.mom.simpleapis.momhttpclient import BaseMoMClient

class MoMClient(BaseMoMClient):

    """This is an HTTP client that knows how to use the Single Sign On of Mom2.
    It is used instead of a SOAP client, because SOAPpy doesn't support
    form handling and cookies."""
    def __init__(self, user = None, password = None):
        super().__init__(MOM_BASE_URL, user, password)
        self.__momURLgetSIP = self.mom_base_url + 'mom3/interface/importXML2.do'
        self.__momURLsetStatus = self.mom_base_url + 'mom3/interface/service/setStatusDataProduct.do'

        self.MAX_MOM_RETRIES = 3

    def setStatus(self, export_id, status_id, message = None):
        try:
            # mom is quite reluctant in updating the status
            # often it returns a login page, even when you're logged in
            # so, upon error, retry a couple of times with a pause, else just return
            for mom_retry in range(self.MAX_MOM_RETRIES):
                self.login()

                params = {"exportId" : export_id, "status" : status_id}
                logger.info("updating MoM on url: %s with params: %s", self.__momURLsetStatus, params)
                response = self.session.get(self.__momURLsetStatus, params=params)
                reply = response.text.strip()

                if reply == 'ok':
                    logger.info('MoMClient.setStatus updated status of %s to %s', export_id, jobState2String(int(status_id)))

                    if message:
                        # even though the mom api suggests that one could update the status and message at the same time
                        # this does not work. If the status changes, and there is a message, then the status is ignored.
                        # So, let's fool mom, and update the status again, this time including the message
                        # In this second call, the status won't change, because we already just changed it.
                        if len(message) > 100:
                            logger.info('truncating message to 100 characters because MoM cannot store more')
                            message = message[:97] + '...'

                        params['message'] = message
                        logger.info("updating MoM (again to set the message) on url: %s with params: %s", self.__momURLsetStatus, params)
                        response = self.session.get(self.__momURLsetStatus, params=params)
                        reply = response.text.strip()

                        if reply == 'ok':
                            logger.info('MoMClient.setStatus updated status of %s to %s with message: %s',
                                        export_id,
                                        jobState2String(int(status_id)),
                                        message)
                        # if the message update did not succeed, we don't really care
                        # the status update already succeeded, and that's important.
                    return True
                else:
                    logger.error('MoMClient.setStatus could not update status of %s to %s using url: %s  reply: %s',
                                export_id,
                                jobState2String(int(status_id)),
                                response.url,
                                reply)
                    self.logout()

                    if 'DOCTYPE HTML PUBLIC' in reply:
                        logger.error('MoM returned login screen instead of SIP for export_id: %s on url %s', export_id, response.url)

                        wait_secs = (mom_retry + 1) * (mom_retry + 1) * 10
                        logger.info('Retrying to setStatus for export_id %s in %s seconds', export_id, wait_secs)
                        time.sleep(wait_secs)
                        continue    # jump back to for mom_retry in range(self.MAX_MOM_RETRIES)

        except Exception as e:
            logger.error('MoMClient.setStatus could not update status of %s to %s: %s', export_id,
                                                                                        jobState2String(int(status_id)),
                                                                                        e)
            self.logout()
        return False

    def uploadDataAndGetSIP(self, archive_id, storage_ticket, filename, uri, filesize, md5_checksum, adler32_checksum, validate = True):
        try:
            # mom is very reluctant in providing sips
            # often it returns a login page, even when you're logged in
            # so, upon error, retry a couple of times with a pause, else just return
            for mom_retry in range(self.MAX_MOM_RETRIES):
                start = time.time()
                logger.info("MoMClient.uploadDataAndGetSIP with archiveId %s - StorageTicket %s - FileName %s - Uri %s", archive_id, storage_ticket, filename, uri)

                self.login()

                xmlcontent = """<?xml version="1.0" encoding="UTF-8"?>
                <lofar:DataProduct archiveId="%s" xmlns:lofar="http://www.astron.nl/MoM2-Lofar">
                    <locations>
                        <location>
                            <uri>lta://%s/%s/%s</uri>
                        </location>
                    </locations>
                    <storageTicket>%s</storageTicket>
                    <fileSize>%s</fileSize>
                    <checksums>
                        <checksum>
                            <algorithm>MD5</algorithm>
                            <value>%s</value>
                        </checksum>
                        <checksum>
                            <algorithm>Adler32</algorithm>
                            <value>%s</value>
                        </checksum>
                    </checksums>
                </lofar:DataProduct>""" % (archive_id, storage_ticket, filename, uri, storage_ticket, filesize, md5_checksum, adler32_checksum)

                # sanitize, make compact
                xmlcontent = xmlcontent.replace('\n', ' ')
                while '  ' in xmlcontent:
                    xmlcontent = xmlcontent.replace('  ', ' ')

                params = {"command": "get-sip-with-input", "xmlcontent" : xmlcontent}
                response = self.session.get(self.__momURLgetSIP, params=params)
                result = response.text
                result = result.replace('<stationType>Europe</stationType>', '<stationType>International</stationType>')

                if 'DOCTYPE HTML PUBLIC' in result:
                    logger.error('MoM returned login screen instead of SIP for %s %s using url %s and params %s, full url=%s',
                                 archive_id, filename, self.__momURLgetSIP, params, response.url)

                    # logout, even though we think we should be logged in properly
                    # it's mom who thinks we should login again, even though we have a proper session.
                    # next retry, we'll login automatically again
                    self.logout()

                    if mom_retry == (self.MAX_MOM_RETRIES - 1):
                        # for some reason mom cannot handle the uploadDataAndGetSIP
                        # let's give it a final try with just GetSip
                        # we'll miss some data in the SIP, which we can add ourselves, so the LTA catalogue is up-to-date
                        # but MoM will miss these parameters. tough luck.
                        logger.warning("MoMClient.uploadDataAndGetSIP with archiveId %s - StorageTicket %s - FileName %s - Uri %s failed %s times. Trying normal GetSip without uploading data to MoM.", archive_id, storage_ticket, filename, uri, mom_retry)
                        result = self.getSIP(archive_id, validate = False)
                        # add ingest info to sip
                        result = addIngestInfoToSIP(result, storage_ticket, filesize, md5_checksum, adler32_checksum)
                    else:
                        wait_secs = (mom_retry + 1) * (mom_retry + 1) * 10
                        logger.info('Retrying to uploadDataAndGetSIP for archiveId %s in %s seconds', archive_id, wait_secs)
                        time.sleep(wait_secs)
                        continue    # jump back to for mom_retry in range(self.MAX_MOM_RETRIES)

                if validate:
                    if not validateSIPAgainstSchema(result, log_prefix = str(filename)):
                        logger.error('Invalid SIP:\n%s', result)
                        raise Exception('SIP for %s does not validate against schema' % filename)

                    # MoM sometimes provides SIPs which validate against the schema
                    # but which has incorrect content, e.g. an incorrect archive_id.
                    # check it!
                    if not checkSIPContent(result,
                                           log_prefix = str(filename),
                                           archive_id = archive_id,
                                           filename = filename,
                                           filesize = filesize,
                                           storage_ticket = storage_ticket,
                                           md5_checksum = md5_checksum,
                                           adler32_checksum = adler32_checksum):
                        raise Exception('SIP for %s does has invalid content' % filename)

                if time.time() - start > 2:
                    logger.debug("MoMClient.uploadDataAndGetSIP for %s took %ds", filename, time.time() - start)

                logger.info("MoMClient.uploadDataAndGetSIP for %s retreived SIP of %s: %s...",
                            filename,
                            humanreadablesize(len(result)), result[:512].replace('\n', ''))
                return result
        except Exception as e:
            self.logout()
            raise Exception("getting SIP from MoM failed: " + str(e))
        return ''

    def getSIP(self, archive_id, validate = True, log_prefix = ''):
        if not log_prefix:
            log_prefix = str(archive_id)

        # mom is very reluctant in providing sips
        # often it returns a login page, even when you're logged in
        # so, upon error, retry a couple of times with a pause, else just return
        for mom_retry in range(self.MAX_MOM_RETRIES):
            try:
                self.login()

                mom_id = archive_id - 1000000    # stupid mom one million archive_id offset

                # logger.info('%s: GetSip call: %s %s', log_prefix, self.__momURLgetSIP, data)
                params={"command" : "GETSIP", "id" : mom_id}
                response = self.session.get(self.__momURLgetSIP, params=params)
                result = response.text

                if 'DOCTYPE HTML PUBLIC' in result:
                    logger.error('%s: MoM returned login screen instead of SIP for archive_id=%s mom_id=%s using url %s and params %s',
                                 log_prefix, archive_id, mom_id, self.__momURLgetSIP, params)

                    wait_secs = (mom_retry + 1) * (mom_retry + 1) * 10
                    logger.info('%s: Retrying to getSIP for archiveId %s in %s seconds', log_prefix, archive_id, wait_secs)
                    time.sleep(wait_secs)
                    continue    # jump back to for mom_retry in range(self.MAX_MOM_RETRIES)

                logger.info('%s: GetSip for archive_id=%s result: %s ....', log_prefix, archive_id, result[:512])
                result = result.replace('<stationType>Europe</stationType>', '<stationType>International</stationType>')

                if validate:
                    if not validateSIPAgainstSchema(result, log_prefix = log_prefix):
                        raise Exception('%s: SIP for archive_id=%s does not validate against schema' % (log_prefix, archive_id))

                return result
            except Exception as e:
                self.logout()
                raise Exception("getting SIP from MoM failed: " + str(e))
        return ''
