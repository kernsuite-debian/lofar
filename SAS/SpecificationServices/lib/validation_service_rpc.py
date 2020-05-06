
from lofar.messaging import RPCClientContextManagerMixin, RPCClient, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from .config import VALIDATION_SERVICENAME
import logging
logger = logging.getLogger(__file__)
from ast import literal_eval

class ValidationRPC(RPCClientContextManagerMixin):

    def __init__(self, rpc_client: RPCClient = None):
        super(ValidationRPC, self).__init__()
        self._rpc_client = rpc_client or RPCClient(VALIDATION_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int = DEFAULT_RPC_TIMEOUT):
        return ValidationRPC(RPCClient(service_name=VALIDATION_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def validate_trigger_specification(self, xml):
        logger.info("Requesting validation of trigger XML")
        result = self._rpc_client.execute('validate_trigger_specification', xml=xml)
        logger.info("Received validation result -> " +str(result))
        return result

    def validate_specification(self, xml):
        logger.info("Requesting validation of specification XML")
        result = self._rpc_client.execute('validate_specification', xml=xml)
        logger.info("Received validation result -> " +str(result))
        return result


    def validate_mom_specification(self, xml):
        logger.info("Requesting validation of MoM specification XML")
        result = self._rpc_client.execute('validate_mom_specification', xml=xml)
        logger.info("Received validation result -> " +str(result))
        return result


