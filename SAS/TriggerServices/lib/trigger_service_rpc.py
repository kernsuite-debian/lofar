
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from .config import TRIGGER_SERVICENAME
import logging
logger = logging.getLogger(__file__)


class TriggerRPC(RPCClientContextManagerMixin):

    def __init__(self, rpc_client: RPCClient = None):
        super(TriggerRPC, self).__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=TRIGGER_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_RPC_TIMEOUT):
        """Create a TriggerRPC connecting to the given exchange/broker on the default TRIGGER_SERVICENAME service"""
        return TriggerRPC(RPCClient(service_name=TRIGGER_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))


    def handle_trigger(self, user, host, trigger_xml):
        logger.info("Requesting handling of trigger")
        result = self._rpc_client.execute('handle_trigger', user=user, host=host, trigger_xml=trigger_xml)
        logger.info("Received trigger handling result -> " + str(result))
        return result
