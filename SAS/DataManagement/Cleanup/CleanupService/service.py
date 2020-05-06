#!/usr/bin/env python3
# $Id$

'''
'''
import logging
import os.path
import socket
import time
import subprocess
from datetime import datetime
from optparse import OptionParser
from lofar.messaging import RPCService, ServiceMessageHandler
from lofar.messaging import EventMessage, ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.messaging.rpc import RPCTimeoutException
from lofar.common.util import waitForInterrupt, humanreadablesize
from lofar.common.subprocess_utils import communicate_returning_strings

from lofar.sas.datamanagement.common.config import CEP4_DATA_MOUNTPOINT
from lofar.sas.datamanagement.common.path import PathResolver, wrap_command_in_cep4_head_node_ssh_call_if_needed
from lofar.sas.datamanagement.cleanup.config import DEFAULT_CLEANUP_SERVICENAME
from lofar.sas.datamanagement.common.config import DEFAULT_DM_NOTIFICATION_PREFIX

from lofar.sas.datamanagement.storagequery.rpc import StorageQueryRPC


logger = logging.getLogger(__name__)

#TODO: this local pinfile is a temporary solution to store the pins in until it can be specified and stored for each task in mom/radb
pinfile = os.path.join(os.environ.get('LOFARROOT', '.'), 'var', 'run', 'auto_cleanup_pinned_tasks.py')

#TODO: this local method is a temporary solution to store the pins in until it can be specified and stored for each task in mom/radb
def _setTaskDataPinned(otdb_id, pinned=True):
    try:
        pins = {}

        if os.path.exists(pinfile):
            with open(pinfile) as f:
                pins = eval(f.read())

        pins[otdb_id] = pinned

        if not os.path.exists(os.path.dirname(pinfile)):
            os.makedirs(os.path.dirname(pinfile))

        with open(pinfile, 'w') as f:
            f.write(str(pins))
            return True
    except Exception as e:
        logger.error(str(e))
    return False

#TODO: this local method is a temporary solution to store the pins in until it can be specified and stored for each task in mom/radb
def _isTaskDataPinned(otdb_id):
    try:
        if os.path.exists(pinfile):
            with open(pinfile) as f:
                pins = eval(f.read())
                return pins.get(otdb_id)
    except Exception as e:
        logger.error(str(e))

    return False

#TODO: this local method is a temporary solution to store the pins in until it can be specified and stored for each task in mom/radb
def _getPinnedStatuses():
    try:
        if os.path.exists(pinfile):
            with open(pinfile) as f:
                pins = eval(f.read())
                return pins
    except Exception as e:
        logger.error(str(e))
        raise
    return {}


class CleanupHandler(ServiceMessageHandler):
    def __init__(self, mountpoint=CEP4_DATA_MOUNTPOINT):
        super().__init__()
        self.mountpoint = mountpoint
        self.path_resolver = None
        self._sqrpc = None

    def init_service_handler(self, service_name: str):
        super().init_service_handler(service_name)

        self.register_service_method('GetPathForOTDBId', self.path_resolver.getPathForOTDBId)
        self.register_service_method('RemovePath', self._removePath)
        self.register_service_method('RemoveTaskData', self._removeTaskData)
        self.register_service_method('SetTaskDataPinned', self._setTaskDataPinned)
        self.register_service_method('IsTaskDataPinned', self._isTaskDataPinned)
        self.register_service_method('GetPinnedStatuses', self._getPinnedStatuses)

    def init_tobus(self, exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER):
        super().init_tobus(exchange, broker)

        self.path_resolver = PathResolver(mountpoint=self.mountpoint, exchange=exchange, broker=broker)
        self._sqrpc = StorageQueryRPC.create(exchange=exchange, broker=broker)

    def start_handling(self):
        super().start_handling()
        self.path_resolver.open()
        self._sqrpc.open()
        logger.info("%s started with projects_path=%s", self, self.path_resolver.projects_path)

    def stop_handling(self):
        self.path_resolver.close()
        self._sqrpc.close()
        super().stop_handling()

    def _setTaskDataPinned(self, otdb_id, pinned=True):
        logger.info('setTaskDataPinned(otdb_id=%s, pinned=%s)', otdb_id, pinned)
        _setTaskDataPinned(otdb_id, pinned)
        self._sendNotification(subject='TaskDataPinned', content={ 'otdb_id':otdb_id, 'pinned': _isTaskDataPinned(otdb_id) })

    def _isTaskDataPinned(self, otdb_id):
        return { str(otdb_id): _isTaskDataPinned(otdb_id) }

    def _getPinnedStatuses(self):
        return _getPinnedStatuses()

    def _sendNotification(self, subject, content):
        try:
            msg = EventMessage(subject="%s.%s" % (DEFAULT_DM_NOTIFICATION_PREFIX, subject), content=content)
            logger.info('Sending notification with subject %s to %s: %s', msg.subject, self.exchange, msg.content)
            self.send(msg)
        except Exception as e:
            logger.error(str(e))

    def _removeTaskData(self, otdb_id, delete_is=True, delete_cs=True, delete_uv=True, delete_im=True, delete_img=True, delete_pulp=True, delete_scratch=True, force=False):
        logger.info("Remove task data for otdb_id %s, force=%s" % (otdb_id, force))

        if not isinstance(otdb_id, int):
            message = "Provided otdb_id is not an int"
            logger.error(message)
            return {'deleted': False, 'message': message}

        self._sendNotification(subject='TaskDeleting', content={ 'otdb_id': otdb_id })

        if _isTaskDataPinned(otdb_id):
            message = "Task otdb_id=%s is pinned. Not deleting data." % (otdb_id)
            logger.error(message)
            self._sendNotification(subject='TaskDeleted', content={'deleted': False,
                                                                   'otdb_id': otdb_id,
                                                                   'message': message})
            return {'deleted': False, 'message': message}

        radbrpc = self.path_resolver.radbrpc
        task = radbrpc.getTask(otdb_id=otdb_id)
        if task:
            suc_tasks = radbrpc.getTasks(task_ids=task['successor_ids'])
            unfinished_scu_tasks = [t for t in suc_tasks if not (t['status'] == 'finished' or t['status'] == 'obsolete')]
            if unfinished_scu_tasks:
                message = "Task otdb_id=%s has unfinished successor tasks (otdb_ids: %s). Not deleting data." % (task['otdb_id'], [t['otdb_id'] for t in unfinished_scu_tasks])
                logger.error(message)
                self._sendNotification(subject='TaskDeleted', content={'deleted': False,
                                                                       'otdb_id': otdb_id,
                                                                       'message': message})
                return {'deleted': False, 'message': message}

            momrpc = self.path_resolver.momrpc
            dataproducts = momrpc.getDataProducts(task['mom_id']).get(task['mom_id'])
            ingestable_dataproducts = [dp for dp in dataproducts if dp['status'] not in [None, 'has_data', 'no_data', 'populated'] ]
            ingested_dataproducts = [dp for dp in ingestable_dataproducts if dp['status'] == 'ingested']

            if not force:
                if len(ingestable_dataproducts) > 0 and len(ingested_dataproducts) < len(ingestable_dataproducts):
                    uningested_dataproducts = [dp for dp in ingestable_dataproducts if dp['status'] != 'ingested']
                    message = "Task otdb_id=%s has un-ingested dataproducts. Not deleting data." % (task['otdb_id'],)
                    logger.error(message)
                    self._sendNotification(subject='TaskDeleted', content={'deleted': False,
                                                                        'otdb_id': otdb_id,
                                                                        'message': message})
                    return {'deleted': False, 'message': message}

        path_result = self.path_resolver.getPathForOTDBId(otdb_id)
        if path_result['found']:
            rm_results = []
            if delete_is and delete_cs and delete_uv and  delete_im and delete_img and delete_pulp:
                rm_results.append(self._removePath(path_result['path']))
            else:
                if delete_is and self.path_resolver.pathExists(os.path.join(path_result['path'], 'is')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'is')))
                if delete_cs and self.path_resolver.pathExists(os.path.join(path_result['path'], 'cs')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'cs')))
                if delete_uv and self.path_resolver.pathExists(os.path.join(path_result['path'], 'uv')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'uv')))
                if delete_im and self.path_resolver.pathExists(os.path.join(path_result['path'], 'im')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'im')))
                if delete_img and self.path_resolver.pathExists(os.path.join(path_result['path'], 'img')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'img')))
                if delete_pulp and self.path_resolver.pathExists(os.path.join(path_result['path'], 'pulp')):
                    rm_results.append(self._removePath(os.path.join(path_result['path'], 'pulp')))

            if delete_scratch and 'scratch_paths' in path_result:
                for scratch_path in path_result['scratch_paths']:
                    rm_results.append(self._removePath(scratch_path))

            rm_result = {'deleted': all(x['deleted'] for x in rm_results),
                         'paths': [x.get('path') for x in rm_results],
                         'message': '',
                         'size': sum([x.get('size', 0) or 0 for x in rm_results])}

            combined_message = '\n'.join(x.get('message','') for x in rm_results)

            if rm_result['deleted'] and not 'does not exist' in combined_message:
                task_type = task.get('type', 'task') if task else 'task'
                rm_result['message'] = 'Deleted %s of data from disk for %s with otdb_id %s\n' % (humanreadablesize(rm_result['size']), task_type, otdb_id)

            rm_result['message'] += combined_message

            self._sendNotification(subject='TaskDeleted', content={'deleted':rm_result['deleted'],
                                                                   'otdb_id':otdb_id,
                                                                   'paths': rm_result['paths'],
                                                                   'message': rm_result['message'],
                                                                   'size': rm_result['size'],
                                                                   'size_readable': humanreadablesize(rm_result['size'])})

            self._endStorageResourceClaim(otdb_id)

            return rm_result

        return {'deleted': False, 'message': path_result['message']}

    def _endStorageResourceClaim(self, otdb_id):
        try:
            #check if all data has actually been removed,
            #and adjust end time of claim on storage
            path_result = self.path_resolver.getPathForOTDBId(otdb_id)
            if path_result['found']:
                path = path_result['path']

                if not self.path_resolver.pathExists(path):
                    # data was actually deleted
                    #update resource claim
                    radbrpc = self.path_resolver.radbrpc
                    storage_resources = radbrpc.getResources(resource_types='storage')
                    cep4_storage_resource = next(x for x in storage_resources if 'CEP4' in x['name'])
                    task = radbrpc.getTask(otdb_id=otdb_id)
                    if task:
                        claims = radbrpc.getResourceClaims(task_ids=task['id'], resource_type='storage')
                        cep4_storage_claim_ids = [c['id'] for c in claims if c['resource_id'] == cep4_storage_resource['id']]
                        for claim_id in cep4_storage_claim_ids:
                            logger.info("setting endtime for claim %s on resource %s %s to now", claim_id, cep4_storage_resource['id'], cep4_storage_resource['name'])
                            radbrpc.updateResourceClaim(claim_id, endtime=datetime.utcnow())
        except Exception as e:
            logger.error(str(e))

    def _removePath(self, path, do_recurse=False):
        logger.info("Remove path: %s" % (path,))

        # do various sanity checking to prevent accidental deletes
        if not isinstance(path, str):
            message = "Provided path is not a string"
            logger.error(message)
            return {'deleted': False, 'message': message, 'path': path}

        if not path:
            message = "Empty path provided"
            logger.error(message)
            return {'deleted': False, 'message': message, 'path': path}

        if '*' in path or '?' in path:
            message = "Invalid path '%s': No wildcards allowed" % (path,)
            logger.error(message)
            return {'deleted': False, 'message': message, 'path': path}

        # remove any trailing slashes
        if len(path) > 1:
            path = path.rstrip('/')

        required_base_paths = [self.path_resolver.projects_path, self.path_resolver.scratch_path, self.path_resolver.share_path]

        if not any(path.startswith(base_path) for base_path in required_base_paths):
            message = "Invalid path '%s': Path does not start with any of the base paths: '%s'" % (path, ' '.join(required_base_paths))
            logger.error(message)
            return {'deleted': False, 'message': message, 'path': path}

        for base_path in required_base_paths:
            if path.startswith(base_path) and path[len(base_path):].count('/') == 0:
                message = "Invalid path '%s': Path should be a subdir of '%s'" % (path, base_path)
                logger.error(message)
                return {'deleted': False, 'message': message, 'path': path}

        if not self.path_resolver.pathExists(path):
            message = "Nothing to delete, path '%s' does not exist." % (path)
            logger.warn(message)
            return {'deleted': True, 'message': message, 'path': path}

        try:
            du_result = self._sqrpc.getDiskUsageForPath(path) if do_recurse else {}
        except RPCTimeoutException:
            du_result = {}

        if du_result.get('found'):
            logger.info("Attempting to delete %s in %s", du_result.get('disk_usage_readable', '?B'), path)
        else:
            logger.info("Attempting to delete %s", path)

        if do_recurse:
            # LustreFS on CEP4 like many small deletes better than one large tree delete
            # so, recurse into the sub_directories,
            # and take a small sleep in between so other processes (like observation datawriters) can access LustreFS
            # (we've seen observation data loss when deleting large trees)
            subdirs_result = self.path_resolver.getSubDirectories(path)
            if subdirs_result.get('found') and subdirs_result.get('sub_directories'):
                sub_directories = subdirs_result['sub_directories']

                for subdir in sub_directories:
                    subdir_path = os.path.join(path, subdir)
                    self._removePath(subdir_path, do_recurse=False) #recurse only one level deep
                    time.sleep(0.01)
        else:
            self._sendNotification(subject='PathDeleting', content={'path': path, 'size': du_result.get('disk_usage', 0) })


        cmd = ['rm', '-rf', path]
        cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
        logger.info(' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = communicate_returning_strings(proc)

        if proc.returncode == 0:
            message = "Deleted %s in '%s'" % (du_result.get('disk_usage_readable', '?B'), path)
            logger.info(message)

            if do_recurse:
                #only send notification if not recursing
                self._sendNotification(subject='PathDeleted', content={'deleted': True, 'path': path, 'message':message, 'size': du_result.get('disk_usage', 0)})

            return {'deleted': True, 'message': message, 'path': path, 'size': du_result.get('disk_usage', 0)}

        if do_recurse:
            #only send notification if not recursing
            self._sendNotification(subject='PathDeleted', content={'deleted': False, 'path': path, 'message':'Failed to delete (part of) %s' % path})

        logger.error(err)

        return {'deleted': False,
                'message': 'Failed to delete (part of) %s' % path,
                'path': path }




def createService(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER,
                  mountpoint=CEP4_DATA_MOUNTPOINT):
    return RPCService(DEFAULT_CLEANUP_SERVICENAME,
                   handler_type=CleanupHandler,
                   handler_kwargs={'mountpoint': mountpoint},
                   exchange=exchange,
                   broker=broker,
                   num_threads=4)

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description='runs the cleanup service')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option("-e", "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus exchange on the broker, [default: %default]")
    parser.add_option("--mountpoint", dest="mountpoint", type="string", default=CEP4_DATA_MOUNTPOINT, help="path of local cep4 mount point, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    with createService(exchange=options.exchange,
                       broker=options.broker):
        waitForInterrupt()

if __name__ == '__main__':
    main()
