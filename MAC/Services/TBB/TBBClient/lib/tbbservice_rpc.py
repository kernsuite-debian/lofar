#!/usr/bin/env python3

import logging
from lofar.messaging import RPCClientContextManagerMixin, RPCClient, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.mac.tbbservice.config import DEFAULT_TBB_SERVICENAME

logger = logging.getLogger(__name__)

class TBBRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        super(TBBRPC, self).__init__()
        self._rpc_client = rpc_client or RPCClient(DEFAULT_TBB_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int = DEFAULT_RPC_TIMEOUT):
        return TBBRPC(RPCClient(service_name=DEFAULT_TBB_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def start_datawriters(self, output_path, num_samples_per_subband, voevent_xml=""):
        logger.info("Requesting start of tbb data writers...")
        result = self._rpc_client.execute('start_datawriters', output_path, num_samples_per_subband, voevent_xml)
        logger.info("Received start datawriter request result %s" % result)
        return result

    def stop_datawriters(self):
        logger.info("Requesting stop of tbb data writers...")
        result = self._rpc_client.execute('stop_datawriters')
        logger.info("Received stop datawriter request result %s" % result)
        return result

    def switch_firmware(self, stations, mode):
        logger.info("Requesting switch of tbb firmware on stations '%s' to mode '%s' ..." % (stations, mode))
        result = self._rpc_client.execute('switch_firmware', stations, mode)
        logger.info("Received firmware request result %s" % result)
        return result

    def start_recording(self, stations, mode, subbands):
        logger.info("Requesting start of tbb recording on stations '%s' in mode '%s' with subbands '%s'..." % (stations, mode, subbands))
        result = self._rpc_client.execute('start_recording', stations, mode, subbands)
        logger.info("Received start recording request result %s" % result)
        return result

    def release_data(self, stations):
        logger.info("Requesting release of tbb data on stations '%s'..." % stations)
        result = self._rpc_client.execute('release_data', stations)
        logger.info("Received release data request result %s" % result)
        return result

    def restart_recording(self, stations):
        logger.info("Requesting restart of tbb recording on stations '%s'..." % (stations))
        result = self._rpc_client.execute('restart_recording', stations)
        logger.info("Received restart recording request result %s" % result)
        return result

    def upload_data(self, stations, dm, start_time, duration, sub_bands, wait_time, boards):
        logger.info("Requesting upload of tbb data from stations '%s', with dm '%s', start_time '%s', duration '%s', sub_bands '%s', wait_time '%s', from boards '%s'..." % (stations, dm, start_time, duration, sub_bands, wait_time, boards))
        result = self._rpc_client.execute('upload_data', stations, dm, start_time, duration, sub_bands, wait_time, boards)
        logger.info("Received upload data request result %s" % result)
        return result

    def freeze_data(self, stations, dm, timesec, timensec):
        logger.info("Requesting freezing of tbb data from stations '%s' at %s seconds %s nanoseconds since epoch, with source dm '%s'..." % (stations, timesec, timensec, dm))
        result = self._rpc_client.execute('freeze_data', stations, dm, timesec, timensec)
        logger.info("Received freeze data request result %s" % result)
        return result

    def set_storage(self, map):
        logger.info("Requesting storage nodes for tbb data according to the following mapping: %s" % map)
        result = self._rpc_client.execute('set_storage', map)
        logger.info("Received set storage request result %s" % result)
        return result

    def do_tbb_subband_dump(self, starttime, duration, dm, project, triggerid, stations, subbands, boards, nodes, voevent_xml, stoptime=None, rcus=None):
        logger.info("Requesting full tbb dump to CEP for trigger %s and project %s" % (triggerid, project))
        result = self._rpc_client.execute('do_tbb_subband_dump', starttime, duration, dm, project, triggerid, stations, subbands, boards, nodes, voevent_xml, stoptime=stoptime, rcus=rcus)
        logger.info("Received full dump to CEP result for trigger %s and project %s: %s" % (triggerid, project, result))
        return result

if __name__ == '__main__':
    '''little example usage'''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    import pprint
    with TBBRPC.create() as rpc:
        import time
        from lofar.mac.tbb.tbb_util import expand_list
        logger.info(rpc.start_datawriters(output_path=None, num_samples_per_subband=None))
        logger.info(rpc.switch_firmware("de601c", "subband"))
        logger.info(rpc.set_storage({"de601c": "somecepnode"}))
        logger.info(rpc.start_recording("de601c", "subband", "1:48"))
        logger.info(rpc.restart_recording("de601c"))
        sec, nsec = ("%.9f" % time.time()).split(".")
        sec = int(sec)
        nsec = int(nsec)
        logger.info(rpc.freeze_data("de601c", 4.2, sec, nsec))
        logger.info(rpc.upload_data("de601c", 4.2, time.time(), 1, "1:48", 1, expand_list("0,2-3,5")))
        logger.info(rpc.release_data("de601c"))



