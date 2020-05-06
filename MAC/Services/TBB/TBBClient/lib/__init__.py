#!/usr/bin/env python3

from threading import Event
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, BusListenerJanitor
from lofar.mac.tbbservice.client.tbbservice_rpc import TBBRPC
from lofar.mac.tbbservice.client.tbbbuslistener import TBBBusListener, TBBEventMessageHandler
from lofar.common.util import single_line_with_single_spaces

class Waiter(TBBBusListener):
    '''Helper class waiting for the DataWritersFinished event'''

    class WaiterTBBEventMessageHandler(TBBEventMessageHandler):
        '''concrete implementation of the TBBEventMessageHandler,
        setting the waiter's wait_event (threading.Event) to signal the waiter that waiting is over.'''
        def __init__(self, waiter):
            super().__init__()
            self._waiter = waiter

        def onDataWritersStarting(self, msg_content):
            logger.info("received DataWritersStarting event: %s", single_line_with_single_spaces(str(msg_content)))

        def onDataWritersStarted(self, msg_content):
            logger.info("received DataWritersStarted event: %s", single_line_with_single_spaces(str(msg_content)))

        def onDataWritersStopping(self, msg_content):
            logger.info("received DataWritersStopping event: %s", single_line_with_single_spaces(str(msg_content)))

        def onDataWritersStopped(self, msg_content):
            logger.info("received DataWritersStopped event: %s", single_line_with_single_spaces(str(msg_content)))

        def onDataWritersFinished(self, msg_content):
            logger.info("received DataWritersFinished event: %s", single_line_with_single_spaces(str(msg_content)))
            # signal that we're done waiting
            self._waiter.wait_event.set()

    def __init__(self, exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
       self.wait_event = Event()
       super(Waiter, self).__init__(handler_type=Waiter.WaiterTBBEventMessageHandler,
                                    handler_kwargs={'waiter': self},
                                    exchange=exchange, broker=broker)

    def wait(self, timeout: int=24*3600, log_interval: int=60):
        '''wait until the DataWritersFinished event is received.
        :param timeout: timeout in seconds
        :param log_interval: interval in seconds to log a message that we are still waiting.
        :raises TimeoutError after timeout seconds
        '''
        start = datetime.utcnow()
        while datetime.utcnow() - start <= timedelta(seconds=timeout):
            logger.info("waiting for DataWritersFinished event... timout in %s", timedelta(seconds=timeout)-(datetime.utcnow() - start))
            if self.wait_event.wait(max(1, min(timeout, log_interval))):
                return

        raise TimeoutError("Did not receive a DataWritersFinished event within %s seconds" %(timeout,))

def start_datawriters_and_wait_until_finished(output_path,
                                              num_samples_per_subband,
                                              timeout: int = 24 * 3600, log_interval: int = 60,
                                              exchange=DEFAULT_BUSNAME,
                                              broker=DEFAULT_BROKER):
    '''
    convenience method which issues a start_datawriters command to the tbbservice, and waits until all writers are done
    '''
    with BusListenerJanitor(Waiter(exchange=exchange, broker=broker)) as waiter:
        with TBBRPC.create(exchange=exchange, broker=broker) as rpc:
            rpc.start_datawriters(output_path=output_path, num_samples_per_subband=num_samples_per_subband)
        logger.info("it's ok to cancel this program. datawriters will continue in the background.")
        waiter.wait(timeout, log_interval)

    logger.info("Datawriters finished")

def stop_datawriters_and_wait_until_finished(timeout: int = 24 * 3600, log_interval: int = 60,
                                             exchange=DEFAULT_BUSNAME,
                                             broker=DEFAULT_BROKER):
    '''
    convenience method which issues a stop_datawriters command to the tbbservice, and waits until all writers are done
    '''
    with BusListenerJanitor(Waiter(exchange=exchange, broker=broker)) as waiter:
        with TBBRPC.create(exchange=exchange, broker=broker) as rpc:
            rpc.stop_datawriters()
        logger.info("it's ok to cancel this program. datawriters will stop in the background.")
        waiter.wait(timeout, log_interval)

    logger.info("Datawriters stopped")
