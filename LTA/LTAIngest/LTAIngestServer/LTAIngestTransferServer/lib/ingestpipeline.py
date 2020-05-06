#!/usr/bin/env python3
import logging
import os
import time
import subprocess
import random
import socket
import re
import getpass

from lofar.lta.ingest.common.job import *
from lofar.lta.ingest.server.sip import validateSIPAgainstSchema, addIngestInfoToSIP
from lofar.lta.ingest.server.ltacp import *
from lofar.lta.ingest.server.unspecifiedSIP import makeSIP
from lofar.lta.ingest.server.ltaclient import *
from lofar.lta.ingest.server.momclient import *
from lofar.common.util import humanreadablesize
from lofar.common import isProductionEnvironment
from lofar.common.subprocess_utils import communicate_returning_strings
from lofar.messaging import EventMessage, ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.lta.ingest.common.config import INGEST_NOTIFICATION_PREFIX
from lofar.lta.ingest.common.config import hostnameToIp
from lofar.lta.ingest.server.config import GLOBUS_TIMEOUT

logger = logging.getLogger()

#---------------------- Custom Exception ----------------------------------------

PipelineJobFailedError      = 1
PipelineNoSourceError       = 2
PipelineAlreadyInLTAError   = 3
PipelineNoProjectInLTAError = 4

class PipelineError(Exception):
    def __init__(self, message, type = PipelineJobFailedError):
        Exception.__init__(self, message)
        self.type         = type

#---------------------- IngestPipeline ------------------------------------------

class IngestPipeline():
    STATUS_INITIALIZING = 1
    STATUS_TRANSFERRING = 2
    STATUS_FINALIZING   = 3
    STATUS_FINISHED     = 4

    def __init__(self, job, momClient, ltaClient,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER,
                 user=getpass.getuser(),
                 globus_timeout=GLOBUS_TIMEOUT,
                 minimal_SIP=False):
        self.status              = IngestPipeline.STATUS_INITIALIZING

        self.hostname            = socket.gethostname()
        self.job                 = job
        self.momClient           = momClient
        self.ltaClient           = ltaClient
        self.user                = user

        if not self.user:
            self.user=getpass.getuser()

        self.globus_timeout      = globus_timeout

        self.minimal_SIP         = minimal_SIP

        self.event_bus           = ToBus(exchange, broker=broker, connection_log_level=logging.DEBUG)

        self.Project             = job['Project']
        self.DataProduct         = job['DataProduct']
        self.FileName            = job['FileName']
        self.JobId               = job['JobId']
        self.ArchiveId           = int(job['ArchiveId'])
        self.ObsId               = int(job['ObservationId'])
        self.ExportID            = job['ExportID']
        self.Type                = job["Type"]
        self.HostLocation        = job['Location'].partition(':')[0]
        self.Location            = job['Location'].partition(':')[2]
        self.ticket              = ''
        self.FileSize            = '0'
        self.MD5Checksum         = ''
        self.Adler32Checksum     = ''
        self.ChecksumResult      = False
        self.SIP                 = ''
        self.PrimaryUri          = ''
        self.SecondaryUri        = ''
        self.lta_site            = ''

    def GetStorageTicket(self):
        do_check_already_in_lta=isProductionEnvironment()
        result = self.ltaClient.GetStorageTicket(self.Project, self.FileName, self.FileSize, self.ArchiveId, self.JobId, self.ObsId, do_check_already_in_lta, self.Type)

        error = result.get('error')
        if error:
            if 'StorageTicket with mom ID "%i"' % (self.ArchiveId) in error:
                if 'existing_ticket_id' in result and 'existing_ticket_state' in result:
                    logger.warning("Got a Tier 1 GetStorageTicket error for an incomplete storage ticket %s with status %s" % (result['existing_ticket_id'],result['existing_ticket_state']))
                    if result['existing_ticket_state'] < IngestSuccessful:
                        try:
                            self.ticket                = result['existing_ticket_id']
                            logger.warning("trying to repair status of StorageTicket %s" % self.ticket)

                            self.SendStatusToLTA(IngestFailed)
                        except Exception as e:
                            logger.exception('ResettingStatus IngestFailed failed for %s' % self.ticket)
                        raise Exception ('Had to reset state for %s' % self.ticket)
                    else:
                        raise PipelineError('GetStorageTicket error: Dataproduct already in LTA for %s' % (self.JobId), PipelineAlreadyInLTAError)
                else:
                    raise Exception('GetStorageTicket error I can''t interpret: %s' % result)

            if 'no storage resources defined for project' in error or "project does not exists" in error:
                raise PipelineError('GetStorageTicket error for project not known in LTA: %s' % error, PipelineNoProjectInLTAError)

            raise Exception('GetStorageTicket error: %s' % error)
        else:
            self.ticket            = result.get('ticket')
            self.PrimaryUri        = result.get('primary_uri_rnd')
            self.SecondaryUri      = result.get('secondary_uri_rnd')

            if 'sara' in self.PrimaryUri:
                self.lta_site = 'sara'
            elif 'juelich' in self.PrimaryUri:
                self.lta_site = 'juelich'
            elif 'psnc' in self.PrimaryUri:
                self.lta_site = 'poznan'

    def TransferFile(self):
        try:
            logger.info('Starting file transfer for %s ' % self.JobId)
            start = time.time()
            self.status = IngestPipeline.STATUS_TRANSFERRING

            self.__sendNotification('JobProgress',
                                    message='transfer starting',
                                    percentage_done=0.0,
                                    total_bytes_transfered=0)

            local_ip = hostnameToIp(self.hostname)

            if 'cep4' in self.HostLocation.lower() or 'cpu' in self.HostLocation.lower():
                self.HostLocation = 'localhost'

            if 'locus' in self.HostLocation.lower() and not '.' in self.HostLocation.lower():
                self.HostLocation += '.cep2.lofar'

            def progress_callback(percentage_done, current_speed, total_bytes_transfered):
                self.__sendNotification('JobProgress',
                                        percentage_done=min(100.0, round(10.0*percentage_done)/10.0),
                                        current_speed=current_speed,
                                        total_bytes_transfered=total_bytes_transfered)

            if (os.path.splitext(self.Location)[-1] == '.h5' and
                os.path.splitext(os.path.basename(self.Location))[0].endswith('_bf')):
                logger.info('dataproduct is a beamformed h5 file. adding raw file to the transfer')
                self.Location = [self.Location, self.Location.replace('.h5', '.raw')]

            if self.DataProduct not in self.Location and 'Source' in self.job:
                # old hack, is needed to support dynspec / pulsar archiving scripts
                self.Location = os.path.join(self.Location, self.job['Source'])

            cp = LtaCp(self.HostLocation,
                       self.Location,
                       self.PrimaryUri,
                       self.user,
                       local_ip=local_ip,
                       globus_timeout=self.globus_timeout,
                       progress_callback=progress_callback)

            transfer_result = cp.transfer(force=True)

            self.status = IngestPipeline.STATUS_FINALIZING

            if not transfer_result:
                msg = 'error while transferring %s with ltacp' % (self.JobId)
                logger.error(msg)
                raise Exception(msg)

            self.MD5Checksum = transfer_result[0]
            self.Adler32Checksum = transfer_result[1]
            self.FileSize = transfer_result[2]

            if self.MD5Checksum and self.Adler32Checksum and self.FileSize:
                logger.debug('valid checksums found for %s with filesize %sB (%s). md5: %s adler32: %s', self.JobId,
                                                                                                         self.FileSize,
                                                                                                         humanreadablesize(int(self.FileSize), 'B'),
                                                                                                         self.MD5Checksum,
                                                                                                         self.Adler32Checksum)
            else:
                msg = 'no valid checksums found for %s with filesize %sB (%s). md5: %s adler32: %s' % (self.JobId,
                                                                                                       self.FileSize,
                                                                                                       humanreadablesize(int(self.FileSize), 'B'),
                                                                                                       self.MD5Checksum,
                                                                                                       self.Adler32Checksum)
                logger.error(msg)
                raise Exception(msg)

            try:
                self.__sendNotification('JobProgress',
                                        message='transfer finished',
                                        percentage_done=100.0,
                                        total_bytes_transfered=int(self.FileSize))
            except ValueError:
                pass
            elapsed = time.time() - start

            try:
                if int(self.FileSize) > 0:
                    avgSpeed = float(self.FileSize) / elapsed
                logger.info("Finished file transfer for %s in %d sec with an average speed of %s for %s including ltacp overhead" % (self.JobId, elapsed, humanreadablesize(avgSpeed, 'Bps'), humanreadablesize(float(self.FileSize), 'B')))
            except Exception:
                logger.info('Finished file transfer of %s in %s' % (self.JobId, elapsed))

        except Exception as exp:
            if isinstance(exp, LtacpException):
                if '550 File not found' in exp.value:
                    logger.error('Destination directory does not exist. Creating %s in LTA for %s' % (self.PrimaryUri, self.JobId))

                    if create_missing_directories(self.PrimaryUri) == 0:
                        logger.info('Created path %s in LTA for %s' % (self.PrimaryUri, self.JobId))
                elif 'source path' in exp.value and 'does not exist' in exp.value:
                    raise PipelineError(exp.value, PipelineNoSourceError)

            raise Exception('transfer failed for %s: %s' % (self.JobId, str(exp)))

    def SendChecksumsToLTA(self):
        result = self.ltaClient.SendChecksums(self.JobId, self.Project, self.ticket, self.FileSize, self.PrimaryUri, self.SecondaryUri, self.MD5Checksum, self.Adler32Checksum)
        if not result.get('error'):
            #store final uri's
            self.PrimaryUri   = result['primary_uri']
            self.SecondaryUri = result.get('secondary_uri')

    def SendStatusToLTA(self, lta_state_id):
        if self.ticket:
            self.ltaClient.UpdateUriState(self.JobId, self.Project, self.ticket, self.PrimaryUri, lta_state_id)

    def CheckForValidSIP(self):
        if self.Type == "MoM":
            try:
                with self.momClient:
                    self.momClient.getSIP(self.ArchiveId, validate=True, log_prefix=self.JobId)

            except Exception as e:
                logger.log(logging.WARNING if self.minimal_SIP else logging.ERROR,
                           'CheckForValidSIP: Getting SIP from MoM failed for %s: %s', self.JobId, e)
                if not self.minimal_SIP:
                    raise

        elif 'SIPLocation' in self.job: # job file might know where the sip is when it is not a MoM job
            try:
                sip_host = self.job['SIPLocation'].split(':')[0]
                sip_path = self.job['SIPLocation'].split(':')[1]

                cmd = ['ssh', '-tt', '-n', '-x', '-q', '%s@%s' % (self.user, sip_host), 'cat %s' % sip_path]
                logger.info("GetSIP for %s at SIPLocation %s - cmd %s" % (self.JobId, self.job['SIPLocation'], ' ' .join(cmd)))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = communicate_returning_strings(p)
                if p.returncode != 0:
                    raise PipelineError('GetSIP error getting EoR SIP for %s: %s' % (self.JobId, out + err))

                tmp_SIP = out

                tmp_SIP = addIngestInfoToSIP(tmp_SIP, self.ticket, self.FileSize, self.MD5Checksum, self.Adler32Checksum)

                tmp_SIP = tmp_SIP.replace('<stationType>Europe</stationType>','<stationType>International</stationType>')

                #make sure the source in the SIP is the same as the type of the storageticket
                tmp_SIP = re.compile('<source>eor</source>', re.IGNORECASE).sub('<source>%s</source>' % (self.Type,), tmp_SIP)

                if not validateSIPAgainstSchema(tmp_SIP):
                    logger.error('CheckForValidSIP: Invalid SIP:\n%s', tmp_SIP)
                    raise Exception('SIP for %s does not validate against schema' % self.JobId)

            except:
                logger.exception('CheckForValidSIP: Getting SIP from SIPLocation %s failed', self.job['SIPLocation'])
                raise

        logger.info('SIP for %s is valid, can proceed with transfer' % (self.JobId,))

    def GetSIP(self):
        try:
            if self.Type == "MoM":
                with self.momClient:
                    self.SIP = self.momClient.uploadDataAndGetSIP(self.ArchiveId,
                                                                self.ticket,
                                                                self.FileName,
                                                                self.PrimaryUri,
                                                                self.FileSize,
                                                                self.MD5Checksum,
                                                                self.Adler32Checksum,
                                                                validate=True)
            elif 'SIPLocation' in self.job: # job file might know where the sip is when it is not a MoM job
                try:
                    sip_host = self.job['SIPLocation'].split(':')[0]
                    sip_path = self.job['SIPLocation'].split(':')[1]

                    cmd = ['ssh', '-tt', '-n', '-x', '-q', '%s@%s' % (self.user, sip_host), 'cat %s' % sip_path]
                    logger.info("GetSIP for %s at SIPLocation %s - cmd %s" % (self.JobId, self.job['SIPLocation'], ' ' .join(cmd)))
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = communicate_returning_strings(p)
                    if p.returncode != 0:
                        raise PipelineError('GetSIP error getting EoR SIP for %s: %s' % (self.JobId, out + err))

                    self.SIP = out

                    self.SIP = addIngestInfoToSIP(self.SIP, self.ticket, self.FileSize, self.MD5Checksum, self.Adler32Checksum)

                    self.SIP = self.SIP.replace('<stationType>Europe</stationType>','<stationType>International</stationType>')

                    #make sure the source in the SIP is the same as the type of the storageticket
                    self.SIP = re.compile('<source>eor</source>', re.IGNORECASE).sub('<source>%s</source>' % (self.Type,), self.SIP)

                    if not validateSIPAgainstSchema(self.SIP):
                        logger.error('Invalid SIP:\n%s', self.SIP)
                        raise Exception('SIP for %s does not validate against schema' % self.JobId)

                except:
                    logger.exception('Getting SIP from SIPLocation %s failed', self.job['SIPLocation'])
                    raise

                logger.info('SIP received for %s from SIPLocation %s with size %d (%s): \n%s' % (self.JobId,
                                                                                                self.job['SIPLocation'],
                                                                                                len(self.SIP),
                                                                                                humanreadablesize(len(self.SIP)),
                                                                                                self.SIP[0:1024]))
            else:
                self.SIP = makeSIP(self.Project, self.ObsId, self.ArchiveId, self.ticket, self.FileName, self.FileSize, self.MD5Checksum, self.Adler32Checksum, self.Type)
                self.FileType = FILE_TYPE_UNSPECIFIED
        except Exception as e:
            if self.minimal_SIP:
                logger.info('making minimal SIP for %s', self.JobId)
                self.SIP = makeSIP(self.Project, self.ObsId, self.ArchiveId, self.ticket, self.FileName, self.FileSize, self.MD5Checksum, self.Adler32Checksum, self.Type)
                logger.info('minimal SIP for %s: \n%s', self.JobId, self.SIP)
                self.FileType = FILE_TYPE_UNSPECIFIED
            else:
                raise

    def SendSIPToLTA(self):
        try:
            self.ltaClient.SendSIP(self.JobId, self.SIP, self.ticket)
        except Exception as e:
            logger.error('SendSIPToLTA exception: %s', e)
            raise PipelineError(str(e), PipelineJobFailedError)

    def RollBack(self):
        try:
            logger.info('rolling back file transfer for %s', self.JobId)
            start     = time.time()

            if self.PrimaryUri:
                srmrm(self.PrimaryUri, log_prefix=self.JobId, timeout=300)

            if self.SecondaryUri:
                srmrm(self.SecondaryUri, log_prefix=self.JobId, timeout=300)

            logger.debug("rollBack for %s took %ds", self.JobId, time.time() - start)
        except Exception as e:
            logger.exception('rollback failed for %s: %s', self.JobId, e)

    def __sendNotification(self, subject, message='', **kwargs):
        try:
            contentDict = { 'job_id': self.JobId,
                            'export_id': self.job.get('job_group_id'),
                            'archive_id': self.ArchiveId,
                            'project': self.Project,
                            'type': self.Type,
                            'ingest_server': self.hostname,
                            'dataproduct': self.DataProduct,
                            'srm_url': self.PrimaryUri }
            if 'ObservationId' in self.job:
                contentDict['otdb_id'] = self.job['ObservationId']

            if self.lta_site:
                contentDict['lta_site'] = self.lta_site

            if message:
                contentDict['message'] = message

            for k,v in list(kwargs.items()):
                contentDict[k] = v

            msg = EventMessage(subject="%s.%s" % (INGEST_NOTIFICATION_PREFIX, subject), content=contentDict)
            msg.ttl = 48*3600 #remove message from queue's when not picked up within 48 hours
            logger.info('Sending notification %s: %s' % (subject, str(contentDict).replace('\n', ' ')))
            self.event_bus.send(msg)
        except Exception as e:
            logger.error(str(e))

    def run(self):
        with self.event_bus:
            try:
                logger.info("starting ingestpipeline for %s" % self.JobId)
                start = time.time()
                self.__sendNotification('JobStarted')

                self.GetStorageTicket()
                self.CheckForValidSIP()
                self.TransferFile()
                self.SendChecksumsToLTA()
                self.GetSIP()
                self.SendSIPToLTA()
                self.SendStatusToLTA(IngestSuccessful)

                avgSpeed = 0
                elapsed = time.time() - start
                try:
                    avgSpeed = float(self.FileSize) / elapsed
                    logger.info("Ingest Pipeline finished for %s in %d sec with average speed of %s for %s including all overhead",
                                self.JobId, elapsed, humanreadablesize(avgSpeed, 'Bps'), humanreadablesize(float(self.FileSize), 'B'))
                except Exception:
                    logger.info("Ingest Pipeline finished for %s in %d sec", self.JobId, elapsed)

                self.__sendNotification('JobFinished',
                                        average_speed=avgSpeed,
                                        total_bytes_transfered=int(self.FileSize))

            except PipelineError as pe:
                logger.log(logging.WARNING if pe.type == PipelineAlreadyInLTAError else logging.ERROR,
                           'Encountered PipelineError for %s : %s', self.JobId, str(pe))
                if pe.type == PipelineNoSourceError:
                    self.__sendNotification('JobTransferFailed', 'data not transfered because it was not on disk')
                elif pe.type == PipelineAlreadyInLTAError:
                    self.__sendNotification('JobFinished', 'data was already in the LTA',
                                            average_speed=0,
                                            total_bytes_transfered=0)
                else:
                    self.RollBack()

                    # by default the error_message for the notification is the exception
                    error_message = str(pe)
                    # for known messsages in the exception, make a nice readable error_message
                    if 'MoM returned login screen instead of SIP' in error_message:
                        error_message = 'MoM returned login screen instead of SIP'

                    self.__sendNotification('JobTransferFailed', error_message)

                try:
                    if pe.type != PipelineAlreadyInLTAError:
                        self.SendStatusToLTA(IngestFailed)
                except Exception as e:
                    logger.error('SendStatusToLTA failed for %s: %s', self.JobId, e)

            except Exception as e:
                logger.error('Encountered unexpected error for %s: %s', self.JobId, e)

                # by default the error_message for the notification is the exception
                error_message = str(e)
                # for known messsages in the exception, make a nice readable error_message
                if 'ltacp' in error_message and ('file listing failed' in error_message or 'du failed' in error_message):
                    error_message = 'dataproduct %s not found at location %s:%s' % (self.DataProduct, self.HostLocation, self.Location)
                elif 'does not validate against schema' in error_message:
                    error_message = 'invalid SIP does not validate against schema'

                try:
                    self.RollBack()
                except Exception as rbe:
                    logger.error('RollBack failed for %s: %s', self.JobId, rbe)
                try:
                    self.SendStatusToLTA(IngestFailed)
                except Exception as sse:
                    logger.error('SendStatusToLTA failed for %s: %s', self.JobId, sse)
                try:
                    self.__sendNotification('JobTransferFailed', error_message)
                except Exception as sne:
                    logger.error('sendNotification failed for %s: %s', self.JobId, sne)
            finally:
                self.status = IngestPipeline.STATUS_FINISHED

def main():
    import os.path
    from optparse import OptionParser
    from lofar.common import dbcredentials

    # Check the invocation arguments
    parser = OptionParser("%prog [options] <path_to_jobfile.xml>",
                          description='Run the ingestpipeline on a single jobfile.')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('--busname', dest='busname', type='string', default=DEFAULT_BUSNAME, help='Name of the bus exchange on the qpid broker on which the ingest notifications are published, default: %default')
    parser.add_option("-u", "--user", dest="user", type="string", default=getpass.getuser(), help="username for to login on <host>, [default: %default]")
    parser.add_option('-s', '--minimal-SIP', dest='minimal_SIP', action='store_true', help='create and upload a minimal SIP to the LTA catalogue when the normal SIP is not accepted.')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_option('-t', '--timeout', dest='globus_timeout', type='int', default=GLOBUS_TIMEOUT, help='number of seconds (default=%default) to wait for globus-url-copy to finish after the transfer is done (while lta-site is computing checksums)')
    parser.add_option("-l", "--lta_credentials", dest="lta_credentials", type="string",
                      default='LTA' if isProductionEnvironment() else 'LTA_test',
                      help="Name of lofar credentials for lta user/pass (see ~/.lofar/dbcredentials) [default=%default]")
    parser.add_option("-m", "--mom_credentials", dest="mom_credentials", type="string",
                      default='MoM_site' if isProductionEnvironment() else 'MoM_site_test',
                      help="Name of credentials for MoM user/pass (see ~/.lofar/dbcredentials) [default=%default]")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    try:
        path = args[0]

        if os.path.isfile(path):
            job = parseJobXmlFile(path)
            job['filename'] = path
            logger.info("Parsed jobfile %s: %s", path, job)

            ltacreds = dbcredentials.DBCredentials().get(options.lta_credentials)
            ltaClient = LTAClient(ltacreds.user, ltacreds.password)

            momcreds = dbcredentials.DBCredentials().get(options.mom_credentials)
            momClient = MoMClient(momcreds.user, momcreds.password)

            jobPipeline = IngestPipeline(job, momClient, ltaClient,
                                         busname=options.busname,
                                         broker=options.broker,
                                         user=options.user,
                                         globus_timeout=options.globus_timeout,
                                         minimal_SIP=options.minimal_SIP)
            jobPipeline.run()
            exit(0)
        else:
            logger.info("No such file %s", path)
            exit(1)
    except Exception as e:
        logger.error(e)
        exit(1)

if __name__ == '__main__':
    main()
