#!/usr/bin/env python3
# $Id$

import logging
import subprocess
import socket
import os.path
from optparse import OptionParser
from lofar.common.util import humanreadablesize
from lofar.common.subprocess_utils import communicate_returning_strings

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.datamanagement.common.config import CEP4_DATA_MOUNTPOINT
from lofar.sas.datamanagement.common.path import PathResolver, wrap_command_in_cep4_head_node_ssh_call_if_needed

logger = logging.getLogger(__name__)

def getDiskUsageForPath(path):
    # 20180829: until lustre has been updated and robinhood has been switched back on (in october) use normal du
    return getDiskUsageForPath_du(path)

    result = getDiskUsageForPath_rbh_du(path)

    if not result.get('found') or result.get('nr_of_files', None) is None:
        logger.info('getDiskUsageForPath(\'%s\') could not obtain valid robinhood result, trying normal du.', path)
        result = getDiskUsageForPath_du(path)

    return result

def getDiskUsageForPath_rbh_du(path):
    logger.info('getDiskUsageForPath_rbh_du(\'%s\')', path)

    result = {'found': False, 'path': path, 'disk_usage': None, 'name': path.split('/')[-1] }

    cmd = ['rbh-du', '-bd', path]
    cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
    logger.info(' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = communicate_returning_strings(proc)

    if proc.returncode == 0:
        # example of out
        # Using config file '/etc/robinhood.d/tmpfs/tmp_fs_mgr_basic.conf'.
        # /data/projects/2016LOFAROBS/L522380
        # dir count:3906, size:16048128, spc_used:16052224
        # file count:17568, size:42274164368, spc_used:42327519232

        #parse out
        lines = [l.strip() for l in out.split('\n')]
        file_lines = [l for l in lines if 'file count' in l]
        if file_lines:
            parts = [p.strip() for p in file_lines[0].split(',')]
            partsDict = {p.split(':')[0].strip():p.split(':')[1].strip() for p in parts}

            result['found'] = True

            if 'size' in partsDict:
                result['disk_usage'] = int(partsDict['size'])

            if 'file count' in partsDict:
                result['nr_of_files'] = int(partsDict['file count'])
        else:
            dir_lines = [l for l in lines if 'dir count' in l]
            if dir_lines:
                result['found'] = True
                result['disk_usage'] = 0
                result['nr_of_files'] = None
    else:
        logger.error(out + err)
        result['message'] = out

    result['disk_usage_readable'] = humanreadablesize(result['disk_usage'])

    otdb_id = getOTDBIdFromPath(path)
    if otdb_id:
        result['otdb_id'] = otdb_id

    logger.info('getDiskUsageForPath_rbh_du(\'%s\') returning: %s', path, result)
    return result

def getDiskUsageForPath_du(path):
    logger.info('getDiskUsageForPath_du(\'%s\')', path)

    result = {'found': False, 'path': path, 'disk_usage': None, 'name': path.split('/')[-1] }

    cmd = ['du', '-bcs', path]
    cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
    logger.info(' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = communicate_returning_strings(proc)

    if proc.returncode == 0:
        # example of out
        # 7025510839      /data/projects/HOLOG_WINDMILL_TESTS/L662734/uv/
        # 7025510839      total

        #parse out
        lines = [l.strip() for l in out.split('\n')]
        total_lines = [l for l in lines if 'total' in l]
        if total_lines:
            parts = [p.strip() for p in total_lines[0].split()]
            if len(parts) == 2:
                result['found'] = True
                result['disk_usage'] = int(parts[0])
                result['nr_of_files'] = None
    else:
        result['message'] = out + err
        result['found'] = False

        if 'No such file or directory' in err:
            logger.warning('No such file or directory: %s', path)
            result['disk_usage'] = 0
        else:
            logger.error(out + err)

    result['disk_usage_readable'] = humanreadablesize(result['disk_usage'])

    otdb_id = getOTDBIdFromPath(path)
    if otdb_id:
        result['otdb_id'] = otdb_id

    logger.info('getDiskUsageForPath_du(\'%s\') returning: %s', path, result)
    return result

def getOTDBIdFromPath(path):
    try:
        path_items = path.rstrip('/').split('/')
        if len(path_items) >=3 and path_items[-1].startswith('L') and path_items[-1][1:].isdigit() and 'projects' in path_items[-3]:
            logger.info('found path for otdb_id %s %s', path_items[-1][1:], path)
            return int(path_items[-1][1:])
    except Exception as e:
        logger.error('Could not parse otdb_id from path %s %s', path, e)
    return None

def getDiskFreeSpaceForMountpoint(mountpoint=CEP4_DATA_MOUNTPOINT):
    logger.info('getDiskFreeSpaceForMountpoint(\'%s\')', mountpoint)

    result = {'found': False, 'mountpoint': mountpoint }

    cmd = ['df', mountpoint]
    cmd = wrap_command_in_cep4_head_node_ssh_call_if_needed(cmd)
    logger.info(' '.join(cmd) + ' ...waiting for result...')

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = communicate_returning_strings(proc)

    if proc.returncode != 0:
        logger.error(out + err)
        result['message'] = out
        return result

    # example of out
    # Filesystem                                         1K-blocks          Used     Available Use% Mounted on
    # 10.134.233.65@o2ib:10.134.233.66@o2ib:/cep4-fs 3369564904320 1460036416928 1737591103048  46% /data

    #parse out
    lines = [l.strip() for l in out.split('\n')]
    data_line = next(l for l in lines if mountpoint in l)
    if data_line:
        parts = [p.strip() for p in data_line.split(' ')]

        result['found'] = True
        result['disk_size'] = 1024*int(parts[1])
        result['disk_usage'] = 1024*int(parts[2])
        result['disk_free'] = 1024*int(parts[3])

        result['disk_size_readable'] = humanreadablesize(result['disk_size'])
        result['disk_usage_readable'] = humanreadablesize(result['disk_usage'])
        result['disk_free_readable'] = humanreadablesize(result['disk_free'])

    logger.info('getDiskFreeSpaceForMountpoint(\'%s\') returning: %s', mountpoint, result)
    return result

class DiskUsage:
    def __init__(self,
                 mountpoint=CEP4_DATA_MOUNTPOINT,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):
        self.path_resolver = PathResolver(mountpoint=mountpoint,
                                          exchange=exchange,
                                          broker=broker)

    def open(self):
        self.path_resolver.open()

    def close(self):
        self.path_resolver.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def getDiskUsageForOTDBId(self, otdb_id):
        return self.getDiskUsageForTask(otdb_id=otdb_id)

    def getDiskUsageForMoMId(self, mom_id):
        return self.getDiskUsageForTask(mom_id=mom_id)

    def getDiskUsageForRADBId(self, radb_id):
        return self.getDiskUsageForTask(radb_id=radb_id)

    def getDiskUsageForTask(self, radb_id=None, mom_id=None, otdb_id=None):
        logger.info("getDiskUsageForTask(radb_id=%s, mom_id=%s, otdb_id=%s)" % (radb_id, mom_id, otdb_id))
        result = self.path_resolver.getPathForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)
        if result['found']:
            return getDiskUsageForPath(result['path'])

        return {'found': False, 'path': result['path']}

    def getDiskUsageForTaskAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None):
        logger.info("getDiskUsageForTaskAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s)" % (radb_id, mom_id, otdb_id))
        task_du_result = self.getDiskUsageForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)
        if task_du_result['found']:
            task_sd_result = self.path_resolver.getSubDirectoriesForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id)

            if task_sd_result['found']:
                subdir_paths = [os.path.join(task_du_result['path'],sd) for sd in task_sd_result['sub_directories']]

                #TODO: potential for parallelization
                subdirs_du_result = { sd: getDiskUsageForPath(sd) for sd in subdir_paths }
                result = {'found':True, 'task_direcory': task_du_result, 'sub_directories': subdirs_du_result }
                logger.info('result: %s' % result)
                return result

        return task_du_result

    def getDiskUsageForProjectDirAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, project_name=None):
        logger.info("getDiskUsageForProjectDirAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s)" % (radb_id, mom_id, otdb_id))
        path_result = self.path_resolver.getProjectDirAndSubDirectories(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, project_name=project_name)
        if path_result['found']:
            projectdir_du_result = getDiskUsageForPath(path_result['path'])
            subdir_paths = [os.path.join(path_result['path'],sd) for sd in path_result['sub_directories']]

            #TODO: potential for parallelization
            subdirs_du_result = { sd: getDiskUsageForPath(sd) for sd in subdir_paths }
            result = {'found':True, 'projectdir': projectdir_du_result, 'sub_directories': subdirs_du_result }
            logger.info('result: %s' % result)
            return result

        return path_result

    def getDiskFreeSpace(self):
        return getDiskFreeSpaceForMountpoint(self.path_resolver.mountpoint)

def main():
    # Check the invocation arguments
    parser = OptionParser("%prog [options] <path>",
                          description='get disk usage for (cep4) path')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO if options.verbose else logging.WARN)

    if len(args) == 0:
        parser.print_help()
        exit(1)

    result = getDiskUsageForPath(args[0])

    if result['found']:
        print('path %s' % result['path'])
        print('disk_usage %s %s' % (result['disk_usage'], result['disk_usage_readbale']))
        print('nr_of_files %s' % result['nr_of_files'])
    else:
        print(result['message'])
        exit(1)

if __name__ == '__main__':
    main()
