#!/usr/bin/env python3
# $Id$

import logging
import subprocess
import socket
import os.path
from optparse import OptionParser
from lofar.messaging import RPCService, DEFAULT_BROKER, DEFAULT_BUSNAME, ServiceMessageHandler
from lofar.common.util import waitForInterrupt

from lofar.sas.datamanagement.storagequery.config import DEFAULT_STORAGEQUERY_SERVICENAME
from lofar.sas.datamanagement.storagequery.cache import CacheManager

logger = logging.getLogger(__name__)

class StorageQueryHandler(ServiceMessageHandler):
    def __init__(self, cache_manager: CacheManager):
        super(StorageQueryHandler, self).__init__()
        self.cache = cache_manager

    def init_service_handler(self, service_name: str):
        super().init_service_handler(service_name)
        self.register_service_method('GetPathForOTDBId', self.cache.disk_usage.path_resolver.getPathForOTDBId)
        self.register_service_method('GetDiskUsageForOTDBId', self.cache.getDiskUsageForOTDBId)
        self.register_service_method('GetDiskUsageForMoMId', self.cache.getDiskUsageForMoMId)
        self.register_service_method('GetDiskUsageForRADBId', self.cache.getDiskUsageForRADBId)
        self.register_service_method('GetDiskUsageForTask', self.cache.getDiskUsageForTask)
        self.register_service_method('GetDiskUsageForTasks', self.cache.getDiskUsageForTasks)
        self.register_service_method('GetDiskUsageForTaskAndSubDirectories', self.cache.getDiskUsageForTaskAndSubDirectories)
        self.register_service_method('GetDiskUsageForProjectDirAndSubDirectories', self.cache.getDiskUsageForProjectDirAndSubDirectories)
        self.register_service_method('GetDiskUsageForProjectsDirAndSubDirectories', self.cache.getDiskUsageForProjectsDirAndSubDirectories)
        self.register_service_method('GetDiskUsageForPath', self.cache.getDiskUsageForPath)
        self.register_service_method('GetDiskUsagesForAllOtdbIds', self.cache.getDiskUsagesForAllOtdbIds)
        self.register_service_method('GetOtdbIdsFoundOnDisk', self.cache.getOtdbIdsFoundOnDisk)

def createService(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER, cache_manager=None):
    return RPCService(service_name=DEFAULT_STORAGEQUERY_SERVICENAME,
                      handler_type=StorageQueryHandler,
                      handler_kwargs={'cache_manager':cache_manager},
                      exchange=exchange,
                      broker=broker,
                      num_threads=12)

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the storagequery service')
    parser.add_option('-c', '--cache_path', dest='cache_path', type='string',
                      default=os.path.expandvars('$LOFARROOT/etc/storagequery_cache.py'),
                      help='path of the cache file, default: %default')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the broker, [default: %default]")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with CacheManager(exchange=options.exchange, broker=options.broker, cache_path=options.cache_path) as cache_manager:
        with createService(exchange=options.exchange,
                           broker=options.broker,
                           cache_manager=cache_manager):
            waitForInterrupt()

if __name__ == '__main__':
    main()
