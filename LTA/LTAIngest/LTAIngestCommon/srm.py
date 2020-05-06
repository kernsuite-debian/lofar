# Copyright (C) 2018 ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id:  $

from subprocess import Popen, PIPE
import socket
import os
import time
import re
from datetime import datetime, timedelta

from lofar.common.subprocess_utils import communicate_returning_strings

import logging

logger = logging.getLogger(__name__)

"""
This srm module provides python methods for the most used srm calls like srmls, srmrm, etc.
Furthermore, this module provides methods for surl (srm-url) and turl (transfer-url) manipulation.
"""


class SrmException(Exception):
    """ Generic exception for srm errors"""
    pass


def srmrm(surl, log_prefix='', timeout=-1):
    """ remove file from srm
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple with the results of the system call to srm.
    """
    logger.info('%s removing surl: %s', log_prefix, surl)
    return __execute(['/bin/bash', '-c', 'srmrm %s' % (surl,)], log_prefix, timeout)


def srmrmdir(surl, log_prefix='', timeout=-1):
    """ remove (empty) directory from srm
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple with the results of the system call to srm.
    """
    return __execute(['/bin/bash', '-c', 'srmrmdir %s' % (surl,)], log_prefix, timeout)


def srmmkdir(surl, log_prefix='', timeout=-1):
    """ create directory in srm
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple with the results of the system call to srm.
    """
    return __execute(['/bin/bash', '-c', 'srmmkdir -retry_num=0 %s' % (surl,)], log_prefix, timeout)


def srmls(surl, log_prefix='', timeout=-1):
    """ get listing in directory
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple with the results of the system call to srm.
    """
    return __execute(['/bin/bash', '-c', 'srmls %s' % (surl,)], log_prefix, timeout)


def srmll(surl, log_prefix='', timeout=-1):
    """ get detailed listing of a surl (directory or file)
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple with the results of the system call to srm.
    """
    return __execute(['/bin/bash', '-c', 'srmls -l %s' % (surl,)], log_prefix, timeout)


def __execute(cmd, log_prefix='', timeout=-1):
    """ helper method, wrapper around subprocess.
    execute command and return (stdout, stderr, returncode) tuple
    :param cmd: a subprocess Popen cmd like list
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (stdout, stderr, returncode) tuple
    """
    if log_prefix:
        if not isinstance(log_prefix, str):
            log_prefix = str(log_prefix)
        if log_prefix[-1] != ' ':
            log_prefix += ' '

    logger.info('%sexecuting: %s', log_prefix, ' '.join(cmd))
    p_cmd = Popen(cmd, stdout=PIPE, stderr=PIPE)

    if timeout > 0:
        timeout = timedelta(seconds=timeout)
        logger.debug('%swaiting at most %s for command to finish...', log_prefix, timeout)
        start_wait = datetime.now()
        while datetime.now() - start_wait < timeout:
            if p_cmd.poll() is not None:
                break
            time.sleep(1)

        if p_cmd.poll() is None:
            raise SrmException('%s%s did not finish within %s.' % (log_prefix, cmd, timeout))

    stdout, stderr = communicate_returning_strings(p_cmd)

    if p_cmd.returncode != 0:
        logger.error('%s: cmd=%s stdout=%s stderr=%s', log_prefix, ' '.join(cmd), stdout, stderr)

    return stdout, stderr, p_cmd.returncode


def get_srm_size_and_a32_checksum(surl, log_prefix='', timeout=-1):
    """ get file size and checksum from srm via srmll
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    :param log_prefix: an optional prefix for all log lines (can be used to provide a unique identifier to filter log lines in a file)
    :param timeout: optional timeout in seconds
    :return: (success, file_size, a32_checksum) tuple.
    """
    try:
        output, errors, code = srmll(surl, log_prefix, timeout)
        logger.debug(output)

        if code != 0:
            return False, None, None

        path_line = output.strip()
        path_line_items = [x.strip() for x in path_line.split()]

        if len(path_line_items) < 2:
            # path line shorter than expected
            return False, None, None

        file_size = int(path_line_items[0])

        if 'Checksum type:' not in output:
            return False, None, None

        if 'Checksum type:' in output:
            cstype = output.split('Checksum type:')[1].split()[0].strip()
            if cstype.lower() != 'adler32':
                return False, None, None

        if 'Checksum value:' in output:
            a32_value = output.split('Checksum value:')[1].lstrip().split()[0]
            return True, file_size, a32_value

    except Exception as e:
        logger.error(e)

    return False, None, None


def create_missing_directories(surl):
    """ recursively checks for presence of parent directory and created the missing part of a tree
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :return: exit-code of srmmkdir of final dir
    """
    parent, child = os.path.split(surl)
    missing = []

    # determine missing dirs
    while parent:
        logger.info('checking path: %s' % parent)
        o, e, code = srmls(parent)
        if code == 0:
            logger.info('srmls returned successfully, so this path apparently exists: %s' % parent)
            break
        else:
            parent, child = os.path.split(parent)
            missing.append(child)

    # recreate missing dirs
    while len(missing) > 0:
        parent = parent + '/' + missing.pop()
        code = srmmkdir(parent)[2]
        if code != 0:
            logger.info('failed to create missing directory: %s' % parent)
            return code

    logger.info('successfully created parent directory: %s' % parent)
    return 0


def convert_surl_to_turl(surl):
    """ converts given srm url of an LTA site into a transport url as needed by gridftp.
    """
    if 'grid.sara.nl' in surl:
        # sara provides dynamic hostnames via a round-robin dns. Get a random/dynamic host as provided by them.
        dyn_hostname = socket.getfqdn(socket.gethostbyname('gridftp.grid.sara.nl'))
        return re.sub('srm://srm\.grid\.sara\.nl:?\d*', 'gsiftp://%s:2811' % (dyn_hostname,), surl)

    if 'lta-head.lofar.psnc.pl' in surl:
        # poznan provides dynamic hostnames via a round-robin dns. Get a random/dynamic host as provided by them.
        dyn_hostname = socket.getfqdn(socket.gethostbyname('gridftp.lofar.psnc.pl'))
        return re.sub('srm://lta-head\.lofar\.psnc\.pl:?\d*', 'gsiftp://%s:2811' % (dyn_hostname,), surl)

    if 'lofar-srm.fz-juelich.de' in surl:
        # juelich provides dynamic hostnames via a round-robin dns. Get a random/dynamic host as provided by them.
        dyn_hostname = socket.getfqdn(socket.gethostbyname('lofar-gridftp.fz-juelich.de'))
        return re.sub('srm://lofar-srm\.fz-juelich\.de:?\d*', 'gsiftp://%s:2811' % (dyn_hostname,), surl)

    raise SrmException('Cannot convert surl to turl. Unknown destination in surl: \'%s\'.' % surl)


def get_site_surl(surl):
    """
    extract the site surl from a given surl.
    for example srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    becomes: srm://lofar-srm.fz-juelich.de:8443
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :return: the 'site-part' of the surl, like: srm://lofar-srm.fz-juelich.de:8443
    """
    if not surl.startswith('srm://'):
        raise SrmException('invalid srm_url: %s' % surl)

    return 'srm://' + surl[6:].split('/')[0]


def get_path_in_site(surl):
    """
    cut the site 'prefix' of the srm url and returns the path.
    for example srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    becomes: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    :return: the 'path-part' of the surl, like: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    """
    site_surl = get_site_surl(surl)
    return surl[len(site_surl):].rstrip('/')


def get_dir_path_in_site(surl):
    """
    cut the site 'prefix' of the srm url and cut an optional file 'postfix' and return the directory path.
    It is assumed that a filename contains a '.'
    for example (1) srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    becomes: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    for example (2) srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
    becomes: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :param surl: an srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    :return: the 'dir-path-part' of the surl, like: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
    """
    path = get_path_in_site(surl)
    parts = path.split('/')
    if '.' in parts[-1]:
        # last part is a filename, because it contains a '.'
        # return only dir-parts
        return '/'.join(parts[:-1])

    # path contains no filename, just return it
    return path
