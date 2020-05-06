
from lofar.messaging import RPCClientContextManagerMixin, RPCClient, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from .config import SPECIFICATIONTRANSLATION_SERVICENAME
import logging
logger = logging.getLogger(__file__)


class TranslationRPC(RPCClientContextManagerMixin):

    def __init__(self, rpc_client: RPCClient = None):
        super(TranslationRPC, self).__init__()
        self._rpc_client = rpc_client or RPCClient(SPECIFICATIONTRANSLATION_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int = DEFAULT_RPC_TIMEOUT):
        return TranslationRPC(RPCClient(service_name=SPECIFICATIONTRANSLATION_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def trigger_to_specification(self, trigger_spec, trigger_id, job_priority):
        logger.info("Requesting validation of trigger XML")
        result = self._rpc_client.execute('trigger_to_specification',
                          trigger_spec=trigger_spec,
                          trigger_id=trigger_id,
                          job_priority=job_priority)
        logger.info("Received validation result -> " +str(result))
        return result


    def specification_to_momspecification(self, spec):
        logger.info("Requesting validation of trigger XML")
        result = self._rpc_client.execute('specification_to_momspecification', spec_xml=spec)
        logger.info("Received validation result -> " +str(result))
        return result
