#!/usr/bin/env python3

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
#

from lofar.lta.ingest.client.ingestbuslistener import IngestEventMessageHandler, IngestEventMesssageBusListener
from lofar.lta.ingest.client.rpc import IngestRPC
from lofar.lta.ingest.common.job import *
from lofar.lta.ingest.server.config import DEFAULT_INGEST_INCOMING_JOB_SUBJECT, INGEST_NOTIFICATION_PREFIX
from lofar.lta.ingest.server.config import DEFAULT_MOM_XMLRPC_HOST, DEFAULT_MOM_XMLRPC_PORT
from lofar.lta.ingest.server.config import MAX_NR_OF_RETRIES
from lofar.lta.ingest.server.momclient import *
from lofar.messaging.messagebus import ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME, UsingToBusMixin
from lofar.messaging.messages import CommandMessage, EventMessage
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.common.datetimeutils import totalSeconds
from lofar.common.dbcredentials import DBCredentials
from lofar.common.util import waitForInterrupt

from threading import Thread
import time
from datetime import datetime
from typing import Union

from http.server import HTTPServer
import pysimplesoap as soap

import logging
logger = logging.getLogger()

class IngestEventMessageHandlerForMomAdapter(UsingToBusMixin, IngestEventMessageHandler):
    def __init__(self, mom_creds: DBCredentials):
        self._otdb_id2mom_id = {}
        self._momrpc = None
        self._mom_client = MoMClient(mom_creds.user, mom_creds.password)
        self._removed_export_ids = set() # keep track of which export_id's were removed, so we don't have to remove them again

        IngestEventMessageHandler.__init__(self, ['JobStarted', 'JobFinished', 'JobTransferFailed', 'JobRemoved'])
        UsingToBusMixin.__init__(self)

    def init_tobus(self, exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER):
        super().init_tobus(exchange, broker)
        self._momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)

    def start_handling(self):
        logger.info("IngestEventMessageHandlerForMomAdapter.start_handling...")
        super().start_handling()
        self._momrpc.open()
        self._mom_client.login()
        logger.info("IngestEventMessageHandlerForMomAdapter.start_handling opened all connections and logged in to mom")

    def stop_handling(self):
        self._momrpc.close()
        self._mom_client.logout()
        super().stop_handling()

    def handle_message(self, msg: EventMessage) -> bool:
        try:
            # try 'normal' handling of msg, should result in normal calls to onJob* methods
            # but MoM (via the momrpc) is notorious in properly handling the messages....
            super().handle_message(msg)
        except Exception as e:
            # ... so handle the exceptions...
            logger.warning(e)

            # ... and try to deal with MoM's quirks.
            if self._remove_unknown_export_job_if_needed(msg):
                return True

            if self._resubmit_message_if_applicable(msg):
                return True

    def onJobStarted(self, job_dict):
        self._update_mom_status_if_applicable(job_dict, JobProducing)

    def onJobFinished(self, job_dict):
        self._update_mom_status_if_applicable(job_dict, JobProduced)
        self._checkTaskFullyIngested(job_dict)

    def onJobFailed(self, job_dict):
        self._update_mom_status_if_applicable(job_dict, JobFailed)

    def onJobRemoved(self, job_dict):
        job_dict['message'] = 'removed from ingest queue before transfer'
        self._update_mom_status_if_applicable(job_dict, JobFailed)

    def _update_mom_status_if_applicable(self, job_dict, status):
        if job_dict.get('type','').lower() == 'mom':
            if not self._mom_client.setStatus(job_dict.get('job_id'), status, job_dict.get('message')):
                raise Exception('Could not update status in MoM to %s for %s' % (jobState2String(status), job_dict.get('job_id')))

    def _get_mom_id(self, otdb_id):
        if otdb_id in self._otdb_id2mom_id:
            return self._otdb_id2mom_id[otdb_id]

        mom_id = self._momrpc.getMoMIdsForOTDBIds(otdb_id).get(otdb_id)
        if mom_id is not None:
            self._otdb_id2mom_id[otdb_id] = mom_id
            return mom_id

    def _checkTaskFullyIngested(self, job_dict):
        try:
            if job_dict.get('type','').lower() != 'mom':
                return
            if 'otdb_id' not in job_dict:
                return

            otdb_id = int(job_dict['otdb_id'])
            mom2id = self._get_mom_id(otdb_id)

            if mom2id is None:
                return

            job_dict['mom2id'] = mom2id

            dps = self._momrpc.getDataProducts(mom2id).get(mom2id)

            if dps is None or len(dps) <= 0:
                return

            ingested_dps = [dp for dp in dps if dp['status'] == 'ingested']

            #reuse part of job_dict contents for new notification message
            job_dict2 = {}
            for key in ['job_id', 'export_id', 'project', 'type', 'ingest_server', 'otdb_id', 'lta_site']:
                if key in job_dict:
                    job_dict2[key] = job_dict[key]

            if 'srm_url' in job_dict:
                try:
                    # try to parse the srm_url and get the observation dir name from the dataproduct srmurl
                    # example url: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
                    # should become: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
                    srm_url = job_dict['srm_url']
                    srm_dir_url = '/'.join(srm_url.split('/')[:-2])
                    job_dict2['srm_url'] = srm_dir_url
                except Exception as e:
                    logger.error("could not derive srm_dir_url from %s. error=%s", srm_url, e)

            message = 'Ingested %s/%s (%.1f%%) dataproducts for otdb_id %s mom2id %s' % (len(ingested_dps),
                                                                                        len(dps),
                                                                                        100.0*len(ingested_dps)/len(dps),
                                                                                        otdb_id,
                                                                                        mom2id)
            logger.info(message)

            job_dict2['message'] = message
            job_dict2['percentage_done'] = 100.0*len(ingested_dps)/len(dps)

            self._send_notification('TaskProgress', job_dict2)

            if len(dps) == len(ingested_dps):
                job_dict2['message'] = 'All dataproducts of task with otdb_id=%s mom2id=%s were ingested' % (otdb_id, mom2id)
                self._send_notification('TaskFinished', job_dict2)
        except Exception as e:
            logger.error(str(e))
            return False

        return True

    def _send_notification(self, subject, content_dict):
        try:
            msg = EventMessage(subject="%s.%s" % (INGEST_NOTIFICATION_PREFIX, subject), content=content_dict)
            msg.ttl = 48*3600 #remove message from queue's when not picked up within 48 hours
            logger.info('Sending notification %s to %s: %s' % (msg.subject, self.exchange, str(content_dict).replace('\n', ' ')))
            self.send(msg)
        except Exception as e:
            logger.error(str(e))

    def _remove_unknown_export_job_if_needed(self, msg: EventMessage) -> bool:
        if msg and msg.content:
            if self._momrpc and isinstance(msg.content, dict):
                if msg.content.get('type', '').lower() == 'mom':
                    export_id = msg.content.get('export_id')

                    if export_id is None:
                        job_id = msg.content.get('job_id')
                        export_id = int(job_id.split('_')[1])

                    if export_id and export_id not in self._momrpc.getObjectDetails(export_id):
                        if export_id not in self._removed_export_ids:
                            logger.warning(
                                'Export job %s cannot be found (anymore) in mom. Removing export job from ingest queue',
                                export_id)

                            # keep track of which export_id's were removed, so we don't have to remove them again
                            # this keeps stuff flowing faster
                            self._removed_export_ids.add(export_id)

                            with IngestRPC.create(exchange=self.exchange, broker=self.broker) as ingest_rpc:
                                ingest_rpc.removeExportJob(export_id)
                                return True
        return False

    def _resubmit_message_if_applicable(self, msg: EventMessage) -> bool:
        if msg and msg.content:
            retry_count = msg.content.get('retry_count', 0)

            if retry_count < min(MAX_NR_OF_RETRIES, 127):  # mom can't handle more than 127 status updates...
                retry_count += 1
                try:
                    retry_timestamp = msg.content.get('retry_timestamp', datetime.utcnow())
                    ago = totalSeconds(datetime.utcnow() - retry_timestamp)
                    time.sleep(max(0,
                                    2 * retry_count - ago))  # wait longer between each retry, other messages can be processed in between
                except Exception as e:
                    # just continue
                    logger.warning(e)

                # set/update retry values
                msg.content['retry_count'] = retry_count
                msg.content['retry_timestamp'] = datetime.utcnow()

                # resubmit
                new_msg = EventMessage(subject=msg.subject, content=msg.content)
                new_msg.ttl = 48 * 3600  # remove message from queue's when not picked up within 48 hours
                logger.info('resubmitting unhandled message to back of queue %s: %s %s', self.exchange, new_msg.subject,
                            str(new_msg.content).replace('\n', ' '))
                self.send(new_msg)
                return True

        return False

class IngestBusListenerForMomAdapter(IngestEventMesssageBusListener):
    def __init__(self, mom_creds: DBCredentials, exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        super(IngestBusListenerForMomAdapter, self).__init__(handler_type=IngestEventMessageHandlerForMomAdapter,
                                                             handler_kwargs={'mom_creds': mom_creds},
                                                             exchange=exchange, broker=broker)

class MoMXMLRPCHandler:
    def __init__(self,
                 exchange: str = DEFAULT_BUSNAME,
                 broker: str =DEFAULT_BROKER,
                 mom_xmlrpc_host: str =DEFAULT_MOM_XMLRPC_HOST,
                 mom_xmlrpc_port: Union[str, int] =DEFAULT_MOM_XMLRPC_PORT):
        self._tobus = ToBus(exchange=exchange, broker=broker)

        url = 'http://%s:%s' % (mom_xmlrpc_host, mom_xmlrpc_port)
        logger.info('Setting up MoM SOAP server on %s', url)
        dispatcher = soap.server.SoapDispatcher(name="mom_xmlrpc",
                                                location=url,
                                                action=url,
                                                namespace="urn:pipeline.export")
        dispatcher.register_function('new_job',
                                     self.onXmlRPCJobReceived,
                                     args={'fileName':str , 'fileContent': str},
                                     returns={'new_job_result': bool})

        self._server = HTTPServer((mom_xmlrpc_host, mom_xmlrpc_port), soap.server.SOAPHandler)
        self._server.dispatcher = dispatcher


    def server_address(self):
        """get the xml-rpc server address as host,port tuple"""
        return self._server.server_address

    def server_url(self):
        """get the xml-rpc server address as url"""
        return "http://%s:%s" % self._server.server_address

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        self._tobus.open()

        #run the soap server in a seperate thread
        logger.info('Starting MoM SOAP server on %s', self.server_url())
        self._server_thread = Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()
        logger.info('Started MoM SOAP server on %s', self.server_url())

    def close(self):
        # shutdown soap server and wait for its thread to complete
        logger.info('Shutting down MoM SOAP server on %s', self.server_url())
        self._server.shutdown()
        self._server_thread.join()
        logger.info('MoM SOAP server stopped')

        self._tobus.close()

    def onXmlRPCJobReceived(self, fileName, fileContent):
        try:
            logger.info("Received message on MoM SOAP server: %s", fileName)
            job = parseJobXml(fileContent)

            if job:
                logger.info("Received job on MoM SOAP server: %s", job)

                msg = CommandMessage(content=fileContent, subject=DEFAULT_INGEST_INCOMING_JOB_SUBJECT)
                logger.debug('submitting job %s to exchange %s with subject %s at broker %s',
                             job['JobId'], self._tobus.exchange, msg.subject, self._tobus.broker)
                try:
                    msg.priority = int(job.get('priority', 4))
                except Exception as e:
                    logger.error("Cannot set priority in job message: %s", e)

                self._tobus.send(msg)
                logger.info('submitted job %s with subject=%s to %s at %s',
                            job['JobId'], msg.subject,
                            self._tobus.exchange, self._tobus.broker)
            else:
                logger.info("Could not parse message as job: %s", fileContent)
        except Exception as e:
            logger.error(e)
            return False

        return True

class IngestMomAdapter:
    def __init__(self, mom_creds: DBCredentials,
                 exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER,
                 mom_xmlrpc_host: str = DEFAULT_MOM_XMLRPC_HOST,
                 mom_xmlrpc_port: Union[str, int] = DEFAULT_MOM_XMLRPC_PORT):
        self.ingest2mom_adapter = IngestBusListenerForMomAdapter(mom_creds, exchange, broker)
        self.mom2ingest_adapter = MoMXMLRPCHandler(exchange, broker, mom_xmlrpc_host, mom_xmlrpc_port)

    def open(self):
        self.ingest2mom_adapter.start_listening()
        self.mom2ingest_adapter.open()

    def close(self):
        self.ingest2mom_adapter.stop_listening()
        self.mom2ingest_adapter.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run ingest mom adapter, which receives jobs from MoM, and updates ingest statuses to MoM')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('--exchange', dest='exchange', type='string',
                      default=DEFAULT_BUSNAME,
                      help='Name of the bus on which the services listen, default: %default')
    parser.add_option("-m", "--mom_credentials", dest="mom_credentials",
                      type="string",
                      default='MoM_site' if isProductionEnvironment() else 'MoM_site_test',
                      help="Name of website credentials for MoM user/pass (see ~/.lofar/dbcredentials) [default=%default]")
    parser.add_option("--host", dest="host",
                      type="string",
                      default=DEFAULT_MOM_XMLRPC_HOST,
                      help="address on which the xmlrpc server listens for (mom) jobs [default=%default]")
    parser.add_option("-p", "--port", dest="port",
                      type="int",
                      default=DEFAULT_MOM_XMLRPC_PORT,
                      help="port on which the xmlrpc server listens for (mom) jobs [default=%default]")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    mom_creds = DBCredentials().get(options.mom_credentials)
    logger.info("Using username \'%s\' for MoM web client" % mom_creds.user)


    logger.info('*****************************************')
    logger.info('Starting IngestMomAdapter...')
    logger.info('*****************************************')

    with IngestMomAdapter(mom_creds, options.exchange, options.broker, options.host, options.port) as adapter:
        waitForInterrupt()

    logger.info('Stopped IngestMomAdapter')

if __name__ == '__main__':
    main()


