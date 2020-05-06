#!/usr/bin/env python3

import logging
from lofar.messaging import RPCClient, RPCClientContextManagerMixin
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.sas.datamanagement.cleanup.config import DEFAULT_CLEANUP_SERVICENAME
from lofar.common.util import convertStringDigitKeysToInt

logger = logging.getLogger(__name__)

DEFAULT_CLEANUPRPC_TIMEOUT = 900 # delete actions on disk can take a while, so allow more time (15min) until timeout by default.

class CleanupRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the CleanupRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_CLEANUP_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_CLEANUP_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_CLEANUPRPC_TIMEOUT):
        """Create a CleanupRPC connecting to the given exchange/broker on the default DEFAULT_CLEANUP_SERVICENAME service"""
        return CleanupRPC(RPCClient(service_name=DEFAULT_CLEANUP_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def getPathForOTDBId(self, otdb_id):
        return self._rpc_client.execute('GetPathForOTDBId', otdb_id=otdb_id)

    def removePath(self, path):
        return self._rpc_client.execute('RemovePath', path=path)

    def removeTaskData(self, otdb_id, delete_is=True, delete_cs=True, delete_uv=True, delete_im=True, delete_img=True, delete_pulp=True, delete_scratch=True, force=False):
        return self._rpc_client.execute('RemoveTaskData', otdb_id=otdb_id, delete_is=delete_is, delete_cs=delete_cs, delete_uv=delete_uv, delete_im=delete_im, delete_img=delete_img, delete_pulp=delete_pulp, delete_scratch=delete_scratch, force=force)

    def setTaskDataPinned(self, otdb_id, pinned=True):
        return self._rpc_client.execute('SetTaskDataPinned', otdb_id=otdb_id, pinned=pinned)

    def isTaskDataPinned(self, otdb_id):
        return convertStringDigitKeysToInt(self._rpc_client.execute('IsTaskDataPinned', otdb_id=otdb_id)).get(otdb_id, False)

    def getPinnedStatuses(self):
        return convertStringDigitKeysToInt(self._rpc_client.execute('GetPinnedStatuses'))

def main():
    import sys
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options] <otdb_id>',
                          description='do cleanup actions on cep4 from the commandline')
    parser.add_option('-d', '--delete', dest='delete', action='store_true', help='delete the data for the given otdb_id (see also --force option)')
    parser.add_option('-f', '--force', dest='force', action='store_true', help='in combination with --delete, always delete the data even when safety checks block deletion. (But pinned data is still kept, even when this force flag is supplied.)')
    parser.add_option('-p', '--pin', dest='pin', action='store_true', help='pin the data for the given otdb_id')
    parser.add_option('-u', '--unpin', dest='unpin', action='store_true', help='unpin the data for the given otdb_id')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the broker, default: localhost')
    parser.add_option('-e', '--exchange', dest='exchange', type='string', default=DEFAULT_BUSNAME,
                      help='Name of the bus exchange on the broker, default: [%default]')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if options.verbose else logging.WARN)

    with CleanupRPC.create(exchange=options.exchange, broker=options.broker) as rpc:
        otdb_id = int(args[0])

        if options.pin or options.unpin:
            rpc.setTaskDataPinned(otdb_id, bool(options.pin))
        elif not options.delete:
            print('data for otdb_id %s is %spinned' % (otdb_id, '' if rpc.isTaskDataPinned(otdb_id) else 'not '))

        if options.delete:
            if options.pin:
                print("You can't delete and pin data at the same time!")
                exit(1)

            path_result = rpc.getPathForOTDBId(otdb_id)
            if path_result['found']:
                path = path_result['path']
                scratch_paths = path_result.get('scratch_paths', [])
                paths = scratch_paths + [path]
                print("This will delete everything in '%s'." % ', '.join(paths))
                if input("Are you sure? (y/n) ") == 'y':
                    result = rpc.removeTaskData(otdb_id, force=options.force)
                    print()
                    if not result['deleted']:
                        print('Could not delete data for task with otdb_id=%s' % otdb_id)
                    print(result['message'])
                    exit(0 if result['deleted'] else 1)
                else:
                    print("Nothing deleted")
            else:
                print(path_result['message'])
                exit(1)

if __name__ == '__main__':
    main()
