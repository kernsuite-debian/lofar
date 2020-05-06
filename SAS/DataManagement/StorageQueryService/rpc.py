#!/usr/bin/env python3

import logging
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_RPC_TIMEOUT
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.datamanagement.storagequery.config import DEFAULT_STORAGEQUERY_SERVICENAME

logger = logging.getLogger(__name__)

class StorageQueryRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the StorageQueryRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_STORAGEQUERY_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_STORAGEQUERY_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_RPC_TIMEOUT):
        """Create a StorageQueryRPC connecting to the given exchange/broker on the default DEFAULT_STORAGEQUERY_SERVICENAME service"""
        return StorageQueryRPC(RPCClient(service_name=DEFAULT_STORAGEQUERY_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def getPathForOTDBId(self, otdb_id):
        return self._rpc_client.execute('GetPathForOTDBId', otdb_id=otdb_id)

    def getDiskUsageForOTDBId(self, otdb_id, include_scratch_paths=True, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForOTDBId', otdb_id=otdb_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForMoMId(self, mom_id, include_scratch_paths=True, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForMoMId', mom_id=mom_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForRADBId(self, radb_id, include_scratch_paths=True, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForRADBId', radb_id=radb_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForTask(self, radb_id=None, mom_id=None, otdb_id=None, include_scratch_paths=True, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForTask', radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForTasks(self, radb_ids=None, mom_ids=None, otdb_ids=None, include_scratch_paths=True, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForTasks', radb_ids=radb_ids, mom_ids=mom_ids, otdb_ids=otdb_ids, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForTaskAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForTaskAndSubDirectories', radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, force_update=force_update)

    def getDiskUsageForProjectDirAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, project_name=None, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForProjectDirAndSubDirectories', radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, project_name=project_name, force_update=force_update)

    def getDiskUsageForProjectsDirAndSubDirectories(self, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForProjectsDirAndSubDirectories', force_update=force_update)

    def getDiskUsageForPath(self, path, force_update=False):
        return self._rpc_client.execute('GetDiskUsageForPath', path=path, force_update=force_update)

    def getDiskUsagesForAllOtdbIds(self, force_update=False):
        return self._rpc_client.execute('GetDiskUsagesForAllOtdbIds', force_update=force_update)

    def getOtdbIdsFoundOnDisk(self):
        return self._rpc_client.execute('GetOtdbIdsFoundOnDisk')

def main():
    from pprint import pprint
    import sys
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='do storage queries (on cep4) from the commandline')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the broker, default: localhost')
    parser.add_option('-e', '--exchange', dest='exchange', type='string', default=DEFAULT_BUSNAME,
                      help='Name of the bus exchange on the broker, default: [%default]')
    parser.add_option('-o', '--otdb_id', dest='otdb_id', type='int', default=None, help='otdb_id of task to get the disk usage for')
    parser.add_option('-m', '--mom_id', dest='mom_id', type='int', default=None, help='mom_id of task to get the disk usage for')
    parser.add_option('-r', '--radb_id', dest='radb_id', type='int', default=None, help='radb_id of task to get the disk usage for')
    parser.add_option('-s', '--subdirs', dest='subdirs', action='store_true', help='get the disk usage of the task and its sub directories for the given otdb_id/mom_id/radb_id')
    parser.add_option('-p', '--project', dest='project', type='string', default=None, help='get the disk usage of the project path and all its sub directories for the given project name')
    parser.add_option('-P', '--projects', dest='projects', action='store_true', help='get the disk usage of the projects path and all its projects sub directories')
    parser.add_option('-d', '--dir', dest='dir_path', type='string', default=None, help='get the disk usage of the given directory path')
    parser.add_option('-a', '--all', dest='all', action='store_true', help='get disk usage for all otdb ids currently on disk')
    parser.add_option('-f', '--force_update', dest='force_update', action='store_true', help='force an update of the cache with a new du call')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    if not (options.otdb_id or options.mom_id or options.radb_id or options.project or options.projects or options.dir_path or options.all):
        parser.print_help()
        exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if options.verbose else logging.WARN)

    with StorageQueryRPC.create(exchange=options.exchange, broker=options.broker) as rpc:
        if options.projects:
            result = rpc.getDiskUsageForProjectsDirAndSubDirectories(force_update=bool(options.force_update))
            if result['found']:
                pprint(result)
            else:
                print(result['message'])
                exit(1)
        elif options.project:
            result = rpc.getDiskUsageForProjectDirAndSubDirectories(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id, project_name=options.project, force_update=bool(options.force_update))
            if result['found']:
                pprint(result)
            else:
                print(result['message'])
                exit(1)
        elif options.subdirs:
            result = rpc.getDiskUsageForTaskAndSubDirectories(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id, force_update=bool(options.force_update))
            if result['found']:
                pprint(result)
            else:
                print(result['message'])
                exit(1)
        elif options.dir_path:
            result = rpc.getDiskUsageForPath(path=options.dir_path, force_update=bool(options.force_update))
            if result['found']:
                pprint(result)
            else:
                print(result['message'])
                exit(1)
        elif options.all:
            result = rpc.getDiskUsagesForAllOtdbIds(force_update=bool(options.force_update))
            pprint(result)
        else:
            result = rpc.getDiskUsageForTask(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id, force_update=bool(options.force_update))
            if result['found']:
                print('path %s' % result['path'])
                print('disk_usage %s %s' % (result.get('disk_usage'), result.get('disk_usage_readable')))
                print('nr_of_files %s' % result.get('nr_of_files'))
            else:
                print(result['message'])
                exit(1)

if __name__ == '__main__':
    main()
