
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, RPCClientContextManagerMixin, RPCClient, DEFAULT_RPC_TIMEOUT
from .config import SPECIFICATION_SERVICENAME
import logging
logger = logging.getLogger(__file__)


class SpecificationRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the SpecificationRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the SPECIFICATION_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=SPECIFICATION_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int = DEFAULT_RPC_TIMEOUT):
        """Create a SpecificationRPC connecting to the given exchange/broker on the default DEFAULT_MOMQUERY_SERVICENAME service"""
        return SpecificationRPC(RPCClient(service_name=SPECIFICATION_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def add_specification(self, user, lofar_xml):
        logger.info("Requesting addition of specification XML for user -> "+user)
        result = self._rpc_client.execute('add_specification', user, lofar_xml=lofar_xml)
        logger.info("Received addition result -> " + str(result))
        return result

    def get_specification(self, user, id):
        logger.info("Requesting specification XML for user, id -> "+user+","+id)
        result = self._rpc_client.execute('get_specification', user, id=id)
        logger.info("Received specification XML -> " + str(result))
        return result
