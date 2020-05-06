import xmlrpc.client
import logging
import time
from lofar.common import isProductionEnvironment
from lofar.lta.ingest.server.config import LTA_BASE_URL
from lofar.lta.ingest.server.sip import *
from lofar.common.util import humanreadablesize

logger = logging.getLogger()

#lta status codes
IngestStarted     = 10
IngestSIPComplete = 30
IngestSuccessful  = 40
IngestFailed      = -10
Removed           = -20

def ltaState2String(ltastate):
  if ltastate == IngestStarted:
    return "%d (IngestStarted)" % ltastate
  elif ltastate == IngestSIPComplete:
    return "%d (IngestSIPComplete)" % ltastate
  elif ltastate == IngestSuccessful:
    return "%d (IngestSuccessful)" % ltastate
  elif ltastate == IngestFailed:
    return "%d (IngestFailed)" % ltastate
  elif ltastate == Removed:
    return "%d (Removed)" % ltastate
  return str(ltastate)

class LTAClient:
    def __init__(self, user=None, password=None):
        if user == None or password==None:
            # (mis)use dbcredentials to read user/pass from disk
            from lofar.common import dbcredentials
            dbc = dbcredentials.DBCredentials()
            creds = dbc.get('LTA' if isProductionEnvironment() else 'LTA_test')
            user = creds.user
            password = creds.password

        url = LTA_BASE_URL % (user, password)
        self.__rpc = xmlrpc.client.ServerProxy(url)
        logger.info('LTAClient connected to: %s', self.__hidePassword(url))

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        pass

    def close(self):
        pass
        #self.__rpc.__close()

    def __hidePassword(self, message):
        ''' helper function which hides the password in the ltaClient url in the message
        '''
        try:
            url = str(self.__rpc._ServerProxy__host)
            password = url.split('@')[0].split(':')[-1].strip() #assume url is http://user:pass@host:port
            wrapped_password = ':%s@' % password
            return message.replace(wrapped_password, ':*****@')
        except Exception as e:
            return message

    def GetStorageTicket(self, project, filename, filesize, archive_id, job_id, obs_id, check_mom_id=True, id_source='MoM'):
        ''' get the storage ticket for the given project and filename.

        example result: {'error_nr': 0, 'primary_uri_rnd': 'srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc6_015/547859/L547859_SB463_uv.MS_7f3820e3.tar', 'previous_state': '', 'primary_uri': 'srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc6_015/547859', 'version': '@(#)$Revision$', 'result': 'ok', 'error': '', 'secondary_uri': '', 'ticket': '3E0A47ED860D6339E053B316A9C3BEE2', 'secondary_uri_rnd': ''}
        example result in case check_mom_id=True and ticket exists: {'existing_ticket_id': '3DFBBE6765776EF6E053B316A9C35F11', 'error_nr': 1000, 'primary_uri_rnd': '', 'previous_state': '', 'primary_uri': '', 'version': '@(#)$Revision$', 'result': '', 'error': 'StorageTicket with mom ID "20165895" and ID source "MoM" already exists !', 'secondary_uri': '', 'ticket': '', 'secondary_uri_rnd': '', 'existing_ticket_state': 40}
        '''
        try:
            logger.info("calling GetStorageTicket(%s, %s, %s, %s, %s, %s, %s, %s)", project, filename, filesize, archive_id, job_id, obs_id, check_mom_id, id_source)
            start = time.time()
            result = self.__rpc.GetStorageTicket(project, filename, filesize, archive_id, job_id, obs_id, check_mom_id, id_source)
            if time.time() - start > 2:
                logger.info("GetStorageTicket for %s took %ds" % (job_id, time.time() - start))
            if result.get('error'):
                logger.log(logging.WARNING if 'already exists' in result.get('error','') else logging.ERROR,
                           "LTAClient.GetStorageTicket for %s error: %s", job_id, self.__hidePassword(result.get('error')))
            else:
                logger.info("LTAClient.GetStorageTicket for %s received ticket: %s primary_uri: %s", job_id, result.get('ticket'), result.get('primary_uri_rnd'))

            return result
        except xmlrpc.client.Fault as err:
            logger.error('LTAClient.GetStorageTicket received XML-RPC fault: %s %s' % (err.faultCode, self.__hidePassword(err.faultString)))
            raise
        except Exception as err:
            logger.error('LTAClient.GetStorageTicket exception: %s' % (self.__hidePassword(str(err))))
            raise


    def SendChecksums(self, job_id, project, ticket, filesize, primary_uri=None,  secondary_uri=None, md5_checksum=None, adler32_checksum=None):
        try:
            start = time.time()

            uris = {}
            if primary_uri:
                uris['primary_uri'] = primary_uri
            if secondary_uri:
                uris['secondary_uri'] = secondary_uri

            checksums = {}
            if md5_checksum:
                checksums['MD5'] = md5_checksum
            if adler32_checksum:
                checksums['Adler32'] = adler32_checksum

            logger.info("LTAClient.SendChecksums for %s: project=%s ticket=%s size=%s checksums=%s uris=%s" % (job_id, project, ticket, filesize, checksums, uris))
            result = self.__rpc.SendChecksums(project, ticket, filesize, checksums, uris)
            if time.time() - start > 2:
                logger.info("LTAClient.SendChecksums for %s took %ds" % (job_id, time.time() - start))
        except xmlrpc.client.Fault as err:
            logger.error('LTAClient.SendChecksums received XML-RPC fault: %s %s' % (err.faultCode, self.__hidePassword(err.faultString)))
            raise

        if result.get('error'):
            msg = 'Got an error back in LTAClient.SendChecksums for %s: %s' % (job_id, self.__hidePassword(result.get('error')))
            logger.error(msg)
            raise Exception(msg)

        logger.info('LTAClient.SendChecksums succesful. final uris: primary: %s secondary: %s', result.get('primary_uri'), result.get('secondary_uri'))
        return result

    def UpdateUriState(self, job_id, project, ticket, primary_uri, state_id):
        try:
            start = time.time()
            result = self.__rpc.UpdateUriState(project, ticket, primary_uri, state_id)
            if time.time() - start > 2:
                logger.debug("LTAClient.UpdateUriState for %s took %ds" % (job_id, time.time() - start))
        except xmlrpc.client.Fault as err:
            logger.error('LTAClient.UpdateUriState Received XML-RPC Fault: %s %s' % (err.faultCode, self.__hidePassword(err.faultString)))
            raise
        except Exception as e:
            logger.error('Received unknown exception in SendStatus for %s: %s' % (job_id, self.__hidePassword(str(e))))
            raise

        if time.time() - start > 2:
            logger.info("LTAClient.UpdateUriState for %s took %ds", job_id, time.time() - start)

        if result['result'] == 'ok':
            logger.info('LTAClient.UpdateUriState updated status for %s to %s', job_id, ltaState2String(state_id))
        elif result.get('error'):
            msg = 'Got an error back in LTAClient.UpdateUriState for %s: %s' % (job_id, self.__hidePassword(result.get('error')))
            logger.error(msg)
            raise Exception(msg)

    def SendSIP(self, job_id, sip, storage_ticket):
        try:
            logger.info("LTAClient.SendSIP sending sip of %s for %s ...", humanreadablesize(len(sip)), job_id)
            start = time.time()
            #check sip before we upload it the the LTA
            if not validateSIPAgainstSchema(sip, log_prefix=str(job_id)):
                raise Exception('SIP for %s does not validate against schema' % job_id)

            if not checkSIPContent(sip,
                                    log_prefix=str(job_id),
                                    storage_ticket=storage_ticket):
                raise Exception('SIP for %s does has invalid content' % job_id)

            # sip ok, do upload
            result = self.__rpc.TransmitSIP(sip, storage_ticket)
            if time.time() - start > 2:
                logger.info("LTAClient.SendSIP for %s took %ds", job_id, time.time() - start)
        except xmlrpc.client.Fault as err:
            logger.error('LTAClient.SendSIP Received XML-RPC Fault: %s %s' % (err.faultCode, self.__hidePassword(err.faultString)))
            raise
        if result['result'] == 'ok':
            logger.info('LTAClient.SendSIP: Successfully sent SIP of %s for %s to the LTA', humanreadablesize(len(sip)), job_id)
        elif result.get('error'):
            if "could not use SIP" in result['error']:
                if 'is already in database with isValid 1 and Ticket state 40' in result['error']:
                    #sip is already in lta. issue warning, and continue, don't fail
                    logger.warning(result['error'])
                else:
                    msg = 'LTAClient.SendSIP: Invalid SIP according to LTA catalog for %s: %s' % (job_id, result['error'])
                    logger.error(msg)
                    raise Exception(msg)
            else:
                raise Exception('LTAClient.SendSIP: Got Tier 1 TransmitSIP error for %s: %s' % (job_id, result['error']))
