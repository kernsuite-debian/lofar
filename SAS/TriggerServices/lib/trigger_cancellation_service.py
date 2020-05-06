#!/usr/bin/env python3
# $Id$

'''
This listens on OTDB updates and cancels triggers that are related to things falling apart.
'''
import logging
import time
from optparse import OptionParser
from lofar.common.util import waitForInterrupt
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

logger = logging.getLogger(__name__)

class TriggerCancellationService(OTDBBusListener):
    def __init__(self,
                 momqueryrpc = MoMQueryRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER),
                 exchange = DEFAULT_BUSNAME,
                 broker = DEFAULT_BROKER):
        super(TriggerCancellationService, self).__init__(
            handler_type=TriggerCancellationHandler, handler_kwargs={'momquery_rpc': momqueryrpc},
            exchange=exchange, broker=broker)


class TriggerCancellationHandler(OTDBEventMessageHandler):
    def __init__(self, momquery_rpc=MoMQueryRPC()):
        super().__init__()

        self.momqueryrpc = momquery_rpc

    def start_handling(self):
        self.momqueryrpc.open()
        super(TriggerCancellationHandler, self).start_handling()

    def stop_handling(self):
        self.momqueryrpc.close()
        super(TriggerCancellationHandler, self).stop_handling()

    def _cancel_trigger(self, trigger_id, cancellation_reason):
        self.momqueryrpc.cancel_trigger(trigger_id, cancellation_reason)

    def _if_trigger_cancel_trigger(self, otdb_id, cancellation_reason):
        mom_id = self._try_get_mom_id(otdb_id)

        if not mom_id:
            raise ValueError("Could not retrieve a mom_id for otdb_id: %s", otdb_id)

        trigger_id = self.momqueryrpc.get_trigger_id(mom_id)['trigger_id']

        if trigger_id:
            logger.info("Cancelling trigger w/ otdb_id: %s, mom_id: %s, trigger_id: %s, reason: %s",
                        otdb_id, mom_id, trigger_id, cancellation_reason)
            self._cancel_trigger(trigger_id, cancellation_reason)

    def _try_get_mom_id(self, otdb_id):
        # sometimes we are too fast for MoM so we need to retry
        mom_id = None
        for _ in range(10):
            mom_id = self.momqueryrpc.getMoMIdsForOTDBIds(otdb_id)[otdb_id]
            if mom_id:
                break
            time.sleep(3)
        return mom_id


    def onObservationError(self, otdb_id, modificationTime):
        self._if_trigger_cancel_trigger(otdb_id, "Observation error notification received for OTDB-Id %s" % otdb_id)

    def onObservationConflict(self, otdb_id, modificationTime):
        self._if_trigger_cancel_trigger(otdb_id, "Observation conflict notification received for OTDB-Id %s" % otdb_id)

    def onObservationAborted(self, otdb_id, modificationTime):
        self._if_trigger_cancel_trigger(otdb_id, "Observation aborted notification received for OTDB-Id %s" % otdb_id)

    # todo: Is this smart enough? How about cancelling triggers if triggered pipeline gets aborted?


def main():
    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the resourceassignment database service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the broker, default: %default')
    parser.add_option('-e', "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Exchange where the OTDB notifications are published. "
                           "[default: %default]")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    with TriggerCancellationService(exchange=options.exchange,
                                    broker=options.broker):
        waitForInterrupt()

if __name__ == '__main__':
    main()
