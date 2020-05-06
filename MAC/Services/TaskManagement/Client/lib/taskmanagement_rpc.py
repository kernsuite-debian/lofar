#!/usr/bin/env python3

from lofar.messaging import RPCClientContextManagerMixin, RPCClient, DEFAULT_BUSNAME, DEFAULT_BROKER, DEFAULT_RPC_TIMEOUT
from lofar.mac.services.taskmanagement.common.config import DEFAULT_SERVICENAME


class TaskManagementRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        super(TaskManagementRPC, self).__init__()
        self._rpc_client = rpc_client or RPCClient(DEFAULT_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int = DEFAULT_RPC_TIMEOUT):
        return TaskManagementRPC(RPCClient(service_name=DEFAULT_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def abort_task(self, otdb_id):
        result = self._rpc_client.execute('AbortTask', otdb_id=otdb_id)
        return result
