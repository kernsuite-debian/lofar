#!/usr/bin/env python3

import os
import os.path
import logging
import socket
import subprocess

from lofar.common import isProductionEnvironment
from lofar.common.subprocess_utils import communicate_returning_strings
from lofar.common.cep4_utils import wrap_command_in_cep4_head_node_ssh_call

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.datamanagement.common.config import CEP4_DATA_MOUNTPOINT

from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC

from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

logger = logging.getLogger(__name__)

class PathResolver:
    def __init__(self,
                 mountpoint=CEP4_DATA_MOUNTPOINT,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):

        self.mountpoint = mountpoint
        self.projects_path = os.path.join(self.mountpoint, 'projects' if isProductionEnvironment() else 'test-projects')
        self.scratch_path = os.path.join(self.mountpoint, 'scratch', 'pipeline')
        self.share_path = os.path.join(self.mountpoint, 'share', 'pipeline')

        self.radbrpc = RADBRPC.create(exchange=exchange, broker=broker)
        self.momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)

    def open(self):
        self.radbrpc.open()
        self.momrpc.open()

    def close(self):
        self.radbrpc.close()
        self.momrpc.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def getPathForRADBId(self, radb_id):
        logger.debug("Get path for radb_id %s" % (radb_id,))
        return self.getPathForTask(radb_id=radb_id)

    def getPathForMoMId(self, mom_id):
        logger.debug("Get path for mom_id %s" % (mom_id,))
        return self.getPathForTask(mom_id=mom_id)

    def getPathForOTDBId(self, otdb_id):
        logger.debug("Get path for otdb_id %s" % (otdb_id,))
        return self.getPathForTask(otdb_id=otdb_id)

    def getPathForTask(self, radb_id=None, mom_id=None, otdb_id=None, include_scratch_paths=True):
        logger.info("getPathForTask(radb_id=%s, mom_id=%s, otdb_id=%s)", radb_id, mom_id, otdb_id)
        '''get the path for a task for either the given radb_id, or for the given mom_id, or for the given otdb_id'''
        result = self._getProjectPathAndDetails(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)
        if result['found']:
            project_path = result['path']
            task = result['task']
            task_data_path = os.path.join(project_path, 'L%s' % task['otdb_id'])
            logger.info("constructed path '%s' for otdb_id=%s mom_id=%s radb_id=%s" % (task_data_path, task['otdb_id'], task['mom_id'], task['id']))

            path_result = {'found': True, 'message': '', 'path': task_data_path,
                           'radb_id': task.get('id'), 'mom_id': task.get('mom_id'), 'otdb_id': task.get('otdb_id')}

            if include_scratch_paths and task['type'] == 'pipeline':
                path_result['scratch_paths'] = []

                scratch_path = os.path.join(self.scratch_path, 'Observation%s' % task['otdb_id'])
                share_path = os.path.join(self.share_path, 'Observation%s' % task['otdb_id'])
                logger.info("Checking scratch paths %s %s for otdb_id=%s mom_id=%s radb_id=%s" % (scratch_path, share_path, task['otdb_id'], task['mom_id'], task['id']))

                if self.pathExists(scratch_path):
                    path_result['scratch_paths'].append(scratch_path)

                if self.pathExists(share_path):
                    path_result['scratch_paths'].append(share_path)

            logger.info("result for getPathForTask(radb_id=%s, mom_id=%s, otdb_id=%s): %s", radb_id, mom_id, otdb_id, path_result)
            return path_result

        result = {'found': False, 'message': result.get('message', ''), 'path': '',
                  'radb_id': radb_id, 'mom_id': mom_id, 'otdb_id': otdb_id}
        logger.warn("result for getPathForTask(radb_id=%s, mom_id=%s, otdb_id=%s): %s", radb_id, mom_id, otdb_id, result)
        return result

    def _getProjectPathAndDetails(self, radb_id=None, mom_id=None, otdb_id=None):
        '''get the project path and details of a task for either the given radb_id, or for the given mom_id, or for the given otdb_id'''
        ids = [radb_id, mom_id, otdb_id]
        validIds = [x for x in ids if x != None and isinstance(x, int)]

        if len(validIds) != 1:
            raise KeyError("Provide one and only one id: radb_id=%s, mom_id=%s, otdb_id=%s" % (radb_id, mom_id, otdb_id))

        task = self.radbrpc.getTask(id=radb_id, mom_id=mom_id, otdb_id=otdb_id)

        if not task:
            message = "Could not find task in RADB for radb_id=%s, mom_id=%s, otdb_id=%s" % (radb_id, mom_id, otdb_id)
            logger.error(message)
            return {'found': False, 'message': message, 'path': None}

        logger.info("found radb task with radb_id=%s mom_id=%s and otdb_id=%s" % (task['id'], task['mom_id'], task['otdb_id']))

        mom_details = self.momrpc.getObjectDetails(task['mom_id'])

        if not mom_details or int(task['mom_id']) not in mom_details:
            message = "Could not find mom project details for otdb_id=%s mom_id=%s radb_id=%s" % (task['otdb_id'], task['mom_id'], task['id'])
            logger.error(message)
            return {'found': False, 'message': message, 'path': None}

        project_name = mom_details[task['mom_id']]['project_name']
        logger.info("found project '%s' for otdb_id=%s mom_id=%s radb_id=%s" % (project_name, task['otdb_id'], task['mom_id'], task['id']))

        project_path = os.path.join(self.projects_path, "_".join(project_name.split()))
        return {'found': True, 'path': project_path, 'mom_details':mom_details, 'task':task}

    def getProjectPath(self, radb_id=None, mom_id=None, otdb_id=None):
        result = self._getProjectPathAndDetails(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)

        if result['found']:
            del result['mom_details']
            del result['task']

        return result

    def getProjectDirAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, project_name=None):
        '''get the project directory and its subdirectories of either the project_name, or the task's project for either the given radb_id, or for the given mom_id, or for the given otdb_id'''
        if project_name:
            project_path = os.path.join(self.projects_path, "_".join(project_name.split()))
            return self.getSubDirectories(project_path)

        result = self.getProjectPath(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)
        if result['found']:
            return self.getSubDirectories(result['path'])
        return result

    def getSubDirectoriesForOTDBId(self, otdb_id):
        return self.getSubDirectoriesForTask(otdb_id=otdb_id)

    def getSubDirectoriesForMoMId(self, mom_id):
        return self.getSubDirectoriesForTask(mom_id=mom_id)

    def getSubDirectoriesForRADBId(self, radb_id):
        return self.getSubDirectoriesForTask(radb_id=radb_id)

    def getSubDirectoriesForTask(self, radb_id=None, mom_id=None, otdb_id=None):
        result = self.getPathForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)
        if result['found']:
            return self.getSubDirectories(result['path'])
        return result

    def getSubDirectories(self, path):
        logger.debug('getSubDirectories(%s)', path)
        # get the subdirectories of the given path
        cmd = ['find', path.rstrip('/'), '-maxdepth', '1', '-type', 'd']
        cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
        logger.debug(' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = communicate_returning_strings(proc)

        if proc.returncode != 0:
            # lfs puts it's error message in stdout
            logger.error(out + err)
            return {'found': False, 'path': path, 'message': out + err}

        # parse out, clean lines and skip first line which is path itself.
        lines = [l.strip() for l in out.split('\n')][1:]
        subdir_names = [l.split('/')[-1].strip().strip('/') for l in lines if l]

        result = {'found': True, 'path': path, 'sub_directories': subdir_names}
        logger.debug('getSubDirectories(%s) result: %s', path, result)
        return result

    def pathExists(self, path):
        cmd = ['lfs', 'ls', path]
        cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
        logger.debug(' '.join(cmd))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = communicate_returning_strings(proc)

        if proc.returncode != 0 and 'No such file or directory' in err:
            return False

        return True

def wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd: []):
    """wrap the Popen cmd in a cep4 ssh call if not running on cep4 or lexar"""
    hostname = socket.gethostname()
    if not ('head' in hostname or 'lexar' in hostname):
        return wrap_command_in_cep4_head_node_ssh_call(cmd)
    return cmd

def main():
    import sys
    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='get path for otdb_id/mom_id/radb_id')
    parser.add_option('-p', '--path', dest='path', action='store_true', help='get the path for the given otdb_id/mom_id/radb_id')
    parser.add_option('-P', '--project', dest='project', action='store_true', help='get the project path and all its sub directories for the given otdb_id/mom_id/radb_id')
    parser.add_option('-s', '--subdirs', dest='subdirs', action='store_true', help='get the sub directories of the path for the given otdb_id/mom_id/radb_id')
    parser.add_option('-o', '--otdb_id', dest='otdb_id', type='int', default=None, help='otdb_id of task to get the path for')
    parser.add_option('-m', '--mom_id', dest='mom_id', type='int', default=None, help='mom_id of task to get the path for')
    parser.add_option('-r', '--radb_id', dest='radb_id', type='int', default=None, help='radb_id of task to get the path for')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the broker, default: localhost')
    parser.add_option("--mountpoint", dest="mountpoint", type="string", default=CEP4_DATA_MOUNTPOINT, help="path of local cep4 mount point, default: %default")
    parser.add_option("--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME, help="Name of the exchange on which the services listen, default: %default")
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    if not (options.otdb_id or options.mom_id or options.radb_id):
        parser.print_help()
        exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if options.verbose else logging.WARN)

    with PathResolver(exchange=options.exchange, broker=options.broker) as path_resolver:

        if options.path:
            result = path_resolver.getPathForTask(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id)
            if result['found']:
                print("path: %s" % (result['path']))
            else:
                print(result['message'])
                exit(1)

        if options.project:
            result = path_resolver.getProjectDirAndSubDirectories(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id)
            if result['found']:
                print("projectpath: %s" % (result['path']))
                print("subdirectories: %s" % (' '.join(result['sub_directories'])))
            else:
                print(result['message'])
                exit(1)

        if options.subdirs:
            result = path_resolver.getSubDirectoriesForTask(otdb_id=options.otdb_id, mom_id=options.mom_id, radb_id=options.radb_id)
            if result['found']:
                print("path: %s" % (result['path']))
                print("subdirectories: %s" % (' '.join(result['sub_directories'])))
            else:
                print(result['message'])
                exit(1)


if __name__ == '__main__':
    main()
