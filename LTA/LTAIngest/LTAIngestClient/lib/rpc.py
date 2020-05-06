#!/usr/bin/env python3

import logging
from lofar.messaging.rpc import RPCClient, RPCClientContextManagerMixin, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.lta.ingest.server.config import DEFAULT_INGEST_SERVICENAME

logger = logging.getLogger(__name__)


class IngestRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the IngestRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_INGEST_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_INGEST_SERVICENAME)

    @staticmethod
    def create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        """Create a IngestRPC connecting to the given exchange/broker on the default DEFAULT_INGEST_SERVICENAME service"""
        return IngestRPC(RPCClient(service_name=DEFAULT_INGEST_SERVICENAME,
                                   exchange=exchange, broker=broker, timeout=DEFAULT_RPC_TIMEOUT))

    def removeExportJob(self, export_group_id):
        return self._rpc_client.execute('RemoveExportJob', export_group_id=export_group_id)

    def setExportJobPriority(self, export_group_id, priority):
        return self._rpc_client.execute('SetExportJobPriority', export_id=export_group_id, priority=priority)

    def getStatusReport(self):
        return self._rpc_client.execute('GetStatusReport')

    def getJobStatus(self, job_id):
        return self._rpc_client.execute('GetJobStatus', job_id=job_id)[job_id]

    def getReport(self, export_group_id):
        return self._rpc_client.execute('GetReport', job_group_id=export_group_id)

    def getExportIds(self):
        return self._rpc_client.execute('GetExportIds')


if __name__ == '__main__':
    logging.basicConfig()
    import pprint
    with IngestRPC() as rpc:
        pprint.pprint(rpc.getStatusReport())
