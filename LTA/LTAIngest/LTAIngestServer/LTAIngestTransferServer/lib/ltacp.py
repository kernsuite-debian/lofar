#!/usr/bin/env python3

# LTACP Python module for transferring data from a remote node to a remote SRM via localhost
#
# Remote data can be individual files or directories. Directories will be tar-ed.
#
# Between the remote and local host, md5 checksums are used to ensure integrity of the file,
# adler32  is used between localhost and the SRM.

import logging
from optparse import OptionParser
from subprocess import Popen, PIPE
import socket
import os, sys, getpass
import time
import re
import random
import math
import atexit
from datetime import datetime, timedelta
from lofar.common.util import humanreadablesize
from lofar.common.datetimeutils import totalSeconds
from lofar.common.subprocess_utils import PipeReader, communicate_returning_strings
from lofar.lta.ingest.common.config import hostnameToIp
from lofar.lta.ingest.server.config import GLOBUS_TIMEOUT
from lofar.lta.ingest.common.srm import *
from lofar.common.subprocess_utils import communicate_returning_strings

logger = logging.getLogger()

class LtacpException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return str(self.value)

class LtacpDestinationExistsException(LtacpException):
     def __init__(self, value):
         super(LtacpDestinationExistsException, self).__init__(value)

def getLocalIPAddress():
    return hostnameToIp(socket.gethostname())

def createNetCatCmd(listener, user=None, host=None):
    '''helper method to determine the proper call syntax for netcat on host'''

    # nc has no version option or other ways to check it's version
    # so, just try the variants and pick the first one that does not fail
    if listener:
        nc_variants = ['nc --recv-only', 'nc']
    else:
        nc_variants = ['nc -q 0', 'nc --send-only', 'nc']

    for nc_variant in nc_variants:
        cmd = nc_variant.split(' ')
        if user and host:
            cmd = ['ssh', '-n', '-x', '%s@%s' % (user, host)] + cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = communicate_returning_strings(p)
        if 'invalid option' not in err:
            return nc_variant

    raise LtacpException('could not determine remote netcat version')

class LtaCp:
    def __init__(self,
                 src_host,
                 src_path,
                 dst_surl,
                 src_user=None,
                 gzip=False,
                 globus_timeout=GLOBUS_TIMEOUT,
                 local_ip=None,
                 progress_callback=None):
        """
        Create an LtaCp instance so you can start transferring data from a given src_path at a given src_host to the
        given dst_url in the LTA.
        Simple Example:
          ltacp = LtaCp('localhost', '/data/projects/LC8_001/L654321', 'srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/test/test123.tar')
          md5, a32, num_bytes = ltacp.transfer()

        Example with progress:
          def print_progress(percentage_done, current_speed, total_bytes_transfered):
            print percentage_done, current_speed, total_bytes_transfered

          ltacp = LtaCp('localhost', '/data/projects/LC8_001/L654321', 'srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/test/test123.tar',
                        progress_callback=print_progress)
          md5, a32, num_bytes = ltacp.transfer()

        :param src_host: a string with the source hostname or ip (usually 'localhost')
        :param src_path: either a string with a path to a file or directory, or a list paths to multiple files.
                         All files (either the one file, all files in the directory, or all files in the list of file_paths) are tarred togheter
                         and transfered to the dst_surl
        :param dst_surl: a string with an srm url (like: 'srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/test/test123.tar')
        :param src_user: optional string with a user name to login on the src_host. If None, then the current user is used.
        :param gzip: bool, when True it zips the datastream (so the end result is a .tar.gz file)
        :param globus_timeout: timeout in seconds to wait for the destination host to finish
        :param local_ip: string with local ip address to use when this host has multiple network interfaces.
        :param progress_callback: function with parameters percentage_done, current_speed, total_bytes_transfered which is called during transfer to report on progress.
        """

        self.src_host = src_host
        self.src_path = src_path.rstrip('/') if isinstance(src_path, str) else [sp.rstrip('/') for sp in src_path]
        self.dst_surl = dst_surl
        self.src_user = src_user if src_user else getpass.getuser()
        self.gzip = gzip
        self.globus_timeout = globus_timeout
        self.progress_callback = progress_callback
        if isinstance(src_path, str):
            self.logId = os.path.basename(self.src_path)
        else:
            #src_path is a list of paths, pick filename of first as logId
            self.logId = os.path.basename(self.src_path[0])
        self.started_procs = {}
        self.fifos = []
        self.ssh_cmd = ['ssh', '-tt', '-n', '-x', '-q', '%s@%s' % (self.src_user, self.src_host)]

        self.localIPAddress = local_ip if local_ip else getLocalIPAddress()
        self.localNetCatCmd = createNetCatCmd(listener=True)
        self.remoteNetCatCmd = createNetCatCmd(listener=False, user=self.src_user, host=self.src_host)

    def can_logon_to_source_host(self):
        cmd_login_to_source_host = self.ssh_cmd + ['true']
        logger.info('ltacp %s: logging in to source host. executing: %s' % (self.logId, ' '.join(cmd_login_to_source_host)))
        proc = Popen(cmd_login_to_source_host, stdout=PIPE, stderr=PIPE)
        self.started_procs[proc] = cmd_login_to_source_host

        # block until find is finished
        out, err = communicate_returning_strings(proc)
        del self.started_procs[proc]

        if proc.returncode==0:
            logger.info('ltacp %s: can login to %s@%s', self.logId, self.src_user, self.src_host)
            return True

        logger.error('ltacp %s: cannot login to %s@%s error: %s', self.logId, self.src_user, self.src_host, err)
        return False

    def path_exists(self, path):
        cmd = self.ssh_cmd + ['ls %s' % (path)]
        logger.info('ltacp %s: checking if source exists. executing: %s' % (self.logId, ' '.join(cmd)))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.started_procs[proc] = cmd

        # block until find is finished
        communicate_returning_strings(proc)
        del self.started_procs[proc]

        logger.info('ltacp %s: source %s %s' % (self.logId, path, 'exists' if proc.returncode==0 else 'does not exist'))
        return proc.returncode==0

    def source_exists(self):
        if isinstance(self.src_path, str):
            return self.path_exists(self.src_path)
        else:
            #self.src_path is a list, check each item and combine
            return all([self.path_exists(p) for p in self.src_path])

    def path_mounted(self, path):
        logger.info(os.path.normpath(path))
        logger.info(os.path.normpath(path).strip().split(os.path.sep))
        root_dir = os.path.sep + [dir for dir in os.path.normpath(path).strip().split(os.path.sep) if dir][0]
        cmd = self.ssh_cmd + ['mount | grep %s' % (root_dir)]
        logger.info("ltacp %s: checking if '%s' of path '%s' is mounted. executing: %s" % (self.logId, root_dir, path, ' '.join(cmd)))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.started_procs[proc] = cmd

        # block until find is finished
        communicate_returning_strings(proc)
        del self.started_procs[proc]

        logger.info("ltacp %s: '%s' of path '%s' %s" % (self.logId, root_dir, path, 'is mounted' if proc.returncode==0 else 'is not mounted'))
        return proc.returncode==0

    def source_mounted(self):
        if isinstance(self.src_path, str):
            return self.path_mounted(self.src_path)
        else:
            #self.src_path is a list, check each item and combine
            return all([self.path_mounted(p) for p in self.src_path])

    def is_soure_single_file(self):
        if isinstance(self.src_path, str):
            src_dirname = os.path.dirname(self.src_path)
            src_basename = os.path.basename(self.src_path)

            # get input filetype
            cmd_remote_filetype = self.ssh_cmd + ['stat -L -c %%F %s' % (os.path.join(src_dirname, src_basename),)]
            logger.info('ltacp %s: determining source type. executing: %s' % (self.logId, ' '.join(cmd_remote_filetype)))
            p_remote_filetype = Popen(cmd_remote_filetype, stdout=PIPE, stderr=PIPE)
            self.started_procs[p_remote_filetype] = cmd_remote_filetype

            # block until find is finished
            output_remote_filetype = communicate_returning_strings(p_remote_filetype)
            del self.started_procs[p_remote_filetype]
            if p_remote_filetype.returncode != 0:
                raise LtacpException('ltacp %s: determining source type failed: \nstdout: %s\nstderr: %s' % (self.logId,
                                                                                                             output_remote_filetype[0],
                                                                                                             output_remote_filetype[1]))

            for line in output_remote_filetype[0].split('\n'):
                if 'regular file' in line.strip():
                    logger.info('ltacp %s: remote path is a file' % (self.logId,))
                    return True

            logger.info('ltacp %s: remote path is a directory' % (self.logId))
            return False
        else:
            #self.src_path is a list of files/dirs, so it is not a single file
            logger.info('ltacp %s: remote path is a list of files/dirs' % self.logId)
            return False

    # transfer file/directory from given src to SRM location with given turl
    def transfer(self, force=False, dereference=False):
        starttime = datetime.utcnow()

        # for cleanup
        self.started_procs = {}
        self.fifos = []

        try:
            if not self.source_exists():
                if self.can_logon_to_source_host():
                    if self.source_mounted():
                        raise LtacpException("ltacp %s: source path %s:%s does not exist" %
                                             (self.logId, self.src_host, self.src_path))
                    else:
                        raise LtacpException("ltacp %s: the disk of source path %s:%s does not seem to be mounted" %
                                             (self.logId, self.src_host, self.src_path))
                else:
                    raise LtacpException("ltacp %s: cannot login to %s@%s" % (self.logId, self.src_user, self.src_host))

            # determine if input is file
            input_is_file = self.is_soure_single_file()

            if not input_is_file:
                # make sure the file extension is .tar or .tar.gz
                missing_suffix = ""
                if self.gzip:
                    if not (self.dst_surl.endswith(".tar.gz") or self.dst_surl.endswith(".tgz")):
                        if self.dst_surl.endswith(".tar"):
                            missing_suffix = ".gz"
                        else:
                            missing_suffix = ".tar.gz"
                else:
                    if not self.dst_surl.endswith(".tar"):
                        missing_suffix = ".tar"

                if missing_suffix:
                    self.dst_surl += missing_suffix
                    logger.info("ltacp %s: appending missing suffix %s to surl: %s", self.logId, missing_suffix, self.dst_surl)

            dst_turl = convert_surl_to_turl(self.dst_surl)
            logger.info('ltacp %s: initiating transfer of %s:%s to surl=%s turl=%s' % (self.logId,
                                                                                       self.src_host,
                                                                                       self.src_path,
                                                                                       self.dst_surl,
                                                                                       dst_turl))

            # get input datasize
            du_items = self.src_path if input_is_file or isinstance(self.src_path, str) else ' '.join(self.src_path)
            cmd_remote_du = self.ssh_cmd + ['du -b %s --max-depth=0 %s' % ("--dereference" if dereference else "", du_items)]
            logger.info('ltacp %s: remote getting datasize. executing: %s' % (self.logId, ' '.join(cmd_remote_du)))
            p_remote_du = Popen(cmd_remote_du, stdout=PIPE, stderr=PIPE)
            self.started_procs[p_remote_du] = cmd_remote_du

            # block until du is finished
            output_remote_du = communicate_returning_strings(p_remote_du)
            del self.started_procs[p_remote_du]
            if p_remote_du.returncode != 0:
                raise LtacpException('ltacp %s: remote du failed: \nstdout: %s\nstderr: %s' % (self.logId,
                                                                                               output_remote_du[0],
                                                                                               output_remote_du[1]))

            # compute various parameters for progress logging
            if input_is_file:
                input_datasize = int(output_remote_du[0].split()[0])
            else:
                input_datasize = sum([int(line.strip().split()[0]) for line in output_remote_du[0].split('\n') if line.strip()])

            logger.info('ltacp %s: input datasize: %d bytes, %s' % (self.logId, input_datasize, humanreadablesize(input_datasize)))
            estimated_tar_size = 512*(input_datasize // 512) + 3*512 #512byte header, 2*512byte ending, 512byte modulo data
            logger.info('ltacp %s: estimated_tar_size: %d bytes, %s' % (self.logId, estimated_tar_size, humanreadablesize(estimated_tar_size)))

            #---
            # Server part
            #---

            # we'll randomize ports
            # to minimize initial collision, randomize based on path and time
            random.seed(hash(self.logId) ^ hash(time.time()))

            p_data_in, port_data = self._ncListen('data')


            self.local_data_fifo = '/tmp/ltacp_datapipe_%s_%s' % (self.src_host, self.logId)

            logger.info('ltacp %s: creating data fifo: %s' % (self.logId, self.local_data_fifo))
            if os.path.exists(self.local_data_fifo):
                os.remove(self.local_data_fifo)
            os.mkfifo(self.local_data_fifo)
            if not os.path.exists(self.local_data_fifo):
                raise LtacpException("ltacp %s: Could not create fifo: %s" % (self.logId, self.local_data_fifo))

            # transfer incomming data stream via md5a32bc to compute md5, adler32 and byte_count
            # data is written to fifo, which is then later fed into globus-url-copy
            # on stdout we can monitor progress
            # set progress message step 0f 0.5% of estimated_tar_size
            cmd_md5a32bc = ['md5a32bc', '-p', str(min(1000000, estimated_tar_size//200)), self.local_data_fifo]
            logger.info('ltacp %s: processing data stream for md5, adler32 and byte_count. executing: %s' % (self.logId, ' '.join(cmd_md5a32bc),))
            p_md5a32bc = Popen(cmd_md5a32bc, stdin=p_data_in.stdout, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            self.started_procs[p_md5a32bc] = cmd_md5a32bc

            # start copy fifo stream to globus-url-copy
            guc_options = ['-cd', #create remote directories if missing
                           '-p 4', #number of parallel ftp connections
                           '-bs 131072', #buffer size
                           '-b', # binary
                           '-nodcau', # turn off data channel authentication for ftp transfers
                           ]
            cmd_data_out = ['/bin/bash', '-c', 'globus-url-copy %s file://%s %s' % (' '.join(guc_options), self.local_data_fifo, dst_turl) ]
            logger.info('ltacp %s: copying data stream into globus-url-copy. executing: %s' % (self.logId, ' '.join(cmd_data_out)))
            p_data_out = Popen(cmd_data_out, stdout=PIPE, stderr=PIPE)
            self.started_procs[p_data_out] = cmd_data_out

            # Check if receiver side is set up correctly
            # and all processes are still waiting for input from client
            finished_procs = dict((p, cl) for (p, cl) in list(self.started_procs.items()) if p.poll() is not None)

            if len(finished_procs):
                msg = ''
                for p, cl in list(finished_procs.items()):
                    o, e = communicate_returning_strings(p)
                    msg += "  process pid:%d exited prematurely with exit code %d. cmdline: %s\nstdout: %s\nstderr: %s\n" % (p.pid,
                                                                                                                             p.returncode,
                                                                                                                             cl,
                                                                                                                             o,
                                                                                                                             e)
                raise LtacpException("ltacp %s: %d local process(es) exited prematurely\n%s" % (self.logId, len(finished_procs), msg))

            #---
            # Client part
            #---

            # start remote copy on src host:
            # 1) create fifo
            # 2) send tar stream of data/dir + tee to fifo for 3)
            # 3) simultaneously to 2), calculate checksum of fifo stream
            # 4) break fifo

            self.remote_data_fifo = '/tmp/ltacp_md5_pipe_%s' % (self.logId, )
            #make sure there is no old remote fifo
            self._removeRemoteFifo()
            cmd_remote_mkfifo = self.ssh_cmd + ['mkfifo %s' % (self.remote_data_fifo,)]
            logger.info('ltacp %s: remote creating fifo. executing: %s' % (self.logId, ' '.join(cmd_remote_mkfifo)))
            p_remote_mkfifo = Popen(cmd_remote_mkfifo, stdout=PIPE, stderr=PIPE)
            self.started_procs[p_remote_mkfifo] = cmd_remote_mkfifo

            # block until fifo is created
            output_remote_mkfifo = communicate_returning_strings(p_remote_mkfifo)
            del self.started_procs[p_remote_mkfifo]
            if p_remote_mkfifo.returncode != 0:
                raise LtacpException('ltacp %s: remote fifo creation failed: \nstdout: %s\nstderr: %s' % (self.logId, output_remote_mkfifo[0],output_remote_mkfifo[1]))

            with open(os.devnull, 'r') as devnull:
                # start sending remote data, tee to fifo
                if input_is_file:
                    cmd_remote_data = self.ssh_cmd + ['cat %s %s| tee %s | %s %s %s' % (self.src_path,
                        '| gzip --stdout --fast ' if self.gzip else '',
                        self.remote_data_fifo,
                        self.remoteNetCatCmd,
                        self.localIPAddress,
                        port_data)]
                else:
                    if isinstance(self.src_path, str):
                        #src_path is dir
                        src_path_parent, src_path_child = os.path.split(self.src_path)
                    else:
                        #src_path is list if paths
                        dirs = set([os.path.dirname(p) for p in self.src_path])

                        if len(dirs) > 1:
                            raise LtacpException('ltacp %s: cannot combine multiple files from different directories in one tarbal' % self.logId)

                        files = set([os.path.basename(p) for p in self.src_path])
                        src_path_parent = list(dirs)[0]
                        src_path_child = ' '.join(files)

                    cmd_remote_data = self.ssh_cmd + ['cd %s && tar c %s -O %s %s| tee %s | %s %s %s' % (src_path_parent,
                        src_path_child,
                        '--dereference' if dereference else '',
                        '| gzip --stdout --fast ' if self.gzip else '',
                        self.remote_data_fifo,
                        self.remoteNetCatCmd,
                        self.localIPAddress,
                        port_data)]
                logger.info('ltacp %s: remote starting transfer. executing: %s' % (self.logId, ' '.join(cmd_remote_data)))
                p_remote_data = Popen(cmd_remote_data, stdin=devnull, stdout=PIPE, stderr=PIPE)
                self.started_procs[p_remote_data] = cmd_remote_data

                # start computation of checksum on remote fifo stream
                cmd_remote_checksum = self.ssh_cmd + ['md5sum %s' % (self.remote_data_fifo,)]
                logger.info('ltacp %s: remote starting computation of md5 checksum. executing: %s' % (self.logId, ' '.join(cmd_remote_checksum)))
                p_remote_checksum = Popen(cmd_remote_checksum, stdin=devnull, stdout=PIPE, stderr=PIPE)
                self.started_procs[p_remote_checksum] = cmd_remote_checksum

                # waiting for output, comparing checksums, etc.
                logger.info('ltacp %s: transfering... waiting for progress...' % self.logId)
                transfer_start_time = datetime.utcnow()
                prev_progress_time = datetime.utcnow()
                prev_bytes_transfered = 0

                with PipeReader(p_md5a32bc.stdout, self.logId) as pipe_reader:
                    # wait and poll for progress while all processes are runnning
                    while len([p for p in list(self.started_procs.keys()) if p.poll() is not None]) == 0:
                        try:
                            current_progress_time = datetime.utcnow()
                            elapsed_secs_since_prev = totalSeconds(current_progress_time - prev_progress_time)

                            if elapsed_secs_since_prev > 900:
                                raise LtacpException('ltacp %s: transfer stalled for 15min.' % (self.logId))

                            # read and process md5a32bc stdout lines to create progress messages
                            lines = pipe_reader.readlines(1)
                            nextline = lines[-1].strip() if lines else ''

                            if len(nextline) > 0:
                                try:
                                    logger.debug('ltacp %s: transfering... %s', self.logId, nextline)
                                    total_bytes_transfered = int(nextline.split()[0].strip())
                                    percentage_done = (100.0*float(total_bytes_transfered))/float(estimated_tar_size)
                                    elapsed_secs_since_start = totalSeconds(current_progress_time - transfer_start_time)
                                    if percentage_done > 0 and elapsed_secs_since_start > 0 and elapsed_secs_since_prev > 0:
                                        avg_speed = total_bytes_transfered / elapsed_secs_since_start
                                        current_bytes_transfered = total_bytes_transfered - prev_bytes_transfered
                                        current_speed = current_bytes_transfered / elapsed_secs_since_prev
                                        if elapsed_secs_since_prev > 120 or current_bytes_transfered > 0.333*estimated_tar_size:
                                            prev_progress_time = current_progress_time
                                            prev_bytes_transfered = total_bytes_transfered
                                            percentage_to_go = 100.0 - percentage_done
                                            time_to_go = elapsed_secs_since_start * percentage_to_go / percentage_done

                                            try:
                                                if self.progress_callback:
                                                    self.progress_callback(percentage_done=percentage_done, current_speed=current_speed, total_bytes_transfered=total_bytes_transfered)
                                            except Exception as e:
                                                logger.error(e)

                                            logger.info('ltacp %s: transfered %s %.1f%% in %s at avgSpeed=%s (%s) curSpeed=%s (%s) to_go=%s to %s' % (self.logId,
                                                                                                                    humanreadablesize(total_bytes_transfered),
                                                                                                                    percentage_done,
                                                                                                                    timedelta(seconds=int(round(elapsed_secs_since_start))),
                                                                                                                    humanreadablesize(avg_speed, 'Bps'),
                                                                                                                    humanreadablesize(avg_speed*8, 'bps'),
                                                                                                                    humanreadablesize(current_speed, 'Bps'),
                                                                                                                    humanreadablesize(current_speed*8, 'bps'),
                                                                                                                    timedelta(seconds=int(round(time_to_go))),
                                                                                                                    dst_turl))
                                except Exception as e:
                                    msg = 'ltacp %s: error while parsing md5a32bc loglines: error=%s. line=%s' % (self.logId, e, nextline)
                                    logger.error(msg)
                                    self.cleanup()
                                    raise LtacpException(msg)
                            time.sleep(0.05)
                        except KeyboardInterrupt:
                            self.cleanup()
                        except LtacpException as e:
                            logger.error('ltacp %s: %s' % (self.logId, str(e)))
                            self.cleanup()
                            raise
                        except Exception as e:
                            logger.error('ltacp %s: %s' % (self.logId, str(e)))

                def waitForSubprocess(proc, timeout=timedelta(seconds=60), proc_log_name='', loglevel=logging.DEBUG):
                    logger.log(loglevel, 'ltacp %s: waiting at most %s for %s to finish...', self.logId, timeout, proc_log_name)
                    start_wait = datetime.now()
                    while datetime.now() - start_wait < timeout:
                        if proc.poll() is not None:
                            break;
                        time.sleep(1)

                    if proc.poll() is None:
                        raise LtacpException('ltacp %s: %s did not finish within %s.' % (self.logId, proc_log_name, timeout))

                waitForSubprocess(p_data_out, timedelta(seconds=self.globus_timeout), 'globus-url-copy', logging.INFO)
                output_data_out = communicate_returning_strings(p_data_out)
                if p_data_out.returncode != 0:
                    if 'file exist' in output_data_out[1].lower():
                        raise LtacpDestinationExistsException('ltacp %s: data transfer via globus-url-copy to LTA failed, file already exists. turl=%s.' % (self.logId, dst_turl))
                    raise LtacpException('ltacp %s: transfer via globus-url-copy to LTA failed. turl=%s error=%s' % (self.logId,
                                                                                                                     dst_turl,
                                                                                                                     output_data_out[0].strip()+output_data_out[1].strip()))
                logger.info('ltacp %s: data transfer via globus-url-copy to LTA complete.' % self.logId)

                waitForSubprocess(p_remote_data, timedelta(seconds=60), 'remote data transfer')
                output_remote_data = communicate_returning_strings(p_remote_data)
                if p_remote_data.returncode != 0:
                    raise LtacpException('ltacp %s: Error in remote data transfer: %s' % (self.logId, output_remote_data[1]))
                logger.debug('ltacp %s: remote data transfer finished...' % self.logId)

                waitForSubprocess(p_remote_checksum, timedelta(seconds=60), 'remote md5 checksum computation')
                output_remote_checksum = communicate_returning_strings(p_remote_checksum)
                if p_remote_checksum.returncode != 0:
                    raise LtacpException('ltacp %s: Error in remote md5 checksum computation: %s' % (self.logId, output_remote_checksum[1]))
                logger.debug('ltacp %s: remote md5 checksum computation finished.' % self.logId)

                waitForSubprocess(p_md5a32bc, timedelta(seconds=60), 'local computation of md5 adler32 and byte_count')
                output_md5a32bc_local = communicate_returning_strings(p_md5a32bc)
                if p_md5a32bc.returncode != 0:
                    raise LtacpException('ltacp %s: Error while computing md5 adler32 and byte_count: %s' % (self.logId, output_md5a32bc_local[1]))
                logger.debug('ltacp %s: computed local md5 adler32 and byte_count.' % self.logId)

                # process remote md5 checksums
                try:
                    md5_checksum_remote = output_remote_checksum[0].split(' ')[0]
                except Exception as e:
                    logger.error('ltacp %s: error while parsing remote md5: %s\n%s' % (self.logId, output_remote_checksum[0], output_remote_checksum[1]))
                    raise

                # process local md5 adler32 and byte_count
                try:
                    items = output_md5a32bc_local[1].splitlines()[-1].split(' ')
                    md5_checksum_local = items[0].strip()
                    a32_checksum_local = items[1].strip().zfill(8)
                    byte_count = int(items[2].strip())
                except Exception as e:
                    logger.error('ltacp %s: error while parsing md5 adler32 and byte_count outputs: %s' % (self.logId, output_md5a32bc_local[0]))
                    raise

                # check transfered number of bytes
                if(byte_count == 0 and input_datasize > 0):
                    raise LtacpException('ltacp %s: did not transfer any bytes of the expected %s. Something is wrong in the datastream setup.' % (self.logId, humanreadablesize(estimated_tar_size)))

                logger.info('ltacp %s: byte count of datastream is %d %s' % (self.logId, byte_count, humanreadablesize(byte_count)))

                # compare local and remote md5
                if(md5_checksum_remote != md5_checksum_local):
                    raise LtacpException('md5 checksum reported by client (%s) does not match local checksum of incoming data stream (%s)' % (self.logId, md5_checksum_remote, md5_checksum_local))
                logger.info('ltacp %s: remote and local md5 checksums are equal: %s' % (self.logId, md5_checksum_local,))

            logger.info('ltacp %s: fetching adler32 checksum from LTA...' % self.logId)
            srm_ok, srm_file_size, srm_a32_checksum = get_srm_size_and_a32_checksum(self.dst_surl, 'ltacp %s:' % self.logId)

            if not srm_ok:
                raise LtacpException('ltacp %s: Could not get srm adler32 checksum for: %s'  % (self.logId, self.dst_surl))

            if srm_a32_checksum != a32_checksum_local:
                raise LtacpException('ltacp %s: adler32 checksum reported by srm (%s) does not match original data checksum (%s)' % (self.logId,
                                                                                                                                     srm_a32_checksum,
                                                                                                                                     a32_checksum_local))

            logger.info('ltacp %s: adler32 checksums are equal: %s' % (self.logId, a32_checksum_local,))

            if int(srm_file_size) != int(byte_count):
                raise LtacpException('ltacp %s: file size reported by srm (%s) does not match datastream byte count (%s)' % (self.logId,
                                                                                                                             srm_file_size,
                                                                                                                             byte_count))

            logger.info('ltacp %s: srm file size and datastream byte count are equal: %s bytes (%s)' % (self.logId,
                                                                                                        srm_file_size,
                                                                                                        humanreadablesize(srm_file_size)))
            logger.info('ltacp %s: transfer to LTA completed successfully.' % (self.logId))

        except LtacpDestinationExistsException as e:
            logger.log(logging.WARN if force else logging.ERROR, str(e))
            if force:
                self.cleanup()
                srmrm(self.dst_surl, 'ltacp %s ' % self.logId)
                return self.transfer(force=False)
            else:
                # re-raise the exception to the caller
                raise
        except Exception as e:
            # Something went wrong
            logger.error('ltacp %s: Error in transfer: %s' % (self.logId, str(e)))
            # re-raise the exception to the caller
            raise
        finally:
            # cleanup
            self.cleanup()

        total_time = round(10*totalSeconds(datetime.utcnow() - starttime))/10
        logger.info('ltacp %s: successfully completed transfer of %s:%s to %s in %ssec for %s at avg speed of %s or %s', self.logId,
                                                                                                                         self.src_host,
                                                                                                                         self.src_path,
                                                                                                                         self.dst_surl,
                                                                                                                         total_time,
                                                                                                                         humanreadablesize(int(srm_file_size)),
                                                                                                                         humanreadablesize(int(srm_file_size)/total_time, 'Bps'),
                                                                                                                         humanreadablesize(8*int(srm_file_size)/total_time, 'bps'))

        return (md5_checksum_local, a32_checksum_local, str(byte_count))

    def _ncListen(self, log_name):
        # pick initial random port for data receiver
        port = str(random.randint(49152, 65535))
        while True:
            # start listen for data stream
            cmd_listen = self.localNetCatCmd.split(' ') + ['-l', port]

            logger.info('ltacp %s: listening for %s. executing: %s' % (self.logId, log_name, ' '.join(cmd_listen)))
            p_listen = Popen(cmd_listen, stdout=PIPE, stderr=PIPE)

            time.sleep(0.5)
            if p_listen.poll() is not None:
                # nc returned prematurely, pick another port to listen to
                o, e = communicate_returning_strings(p_listen)
                logger.info('ltacp %s: nc returned prematurely: %s' % (self.logId, e.strip()))
                port = str(random.randint(49152, 65535))
            else:
                self.started_procs[p_listen] = cmd_listen
                return (p_listen, port)


    def _removeRemoteFifo(self):
        if hasattr(self, 'remote_data_fifo') and self.remote_data_fifo:
            '''remove a file (or fifo) on a remote host. Test if file exists before deleting.'''
            cmd_remote_ls = self.ssh_cmd + ['ls %s' % (self.remote_data_fifo,)]
            p_remote_ls = Popen(cmd_remote_ls, stdout=PIPE, stderr=PIPE)
            communicate_returning_strings(p_remote_ls)

            if p_remote_ls.returncode == 0:
                cmd_remote_rm = self.ssh_cmd + ['rm %s' % (self.remote_data_fifo,)]
                logger.info('ltacp %s: removing remote fifo. executing: %s' % (self.logId, ' '.join(cmd_remote_rm)))
                p_remote_rm = Popen(cmd_remote_rm, stdout=PIPE, stderr=PIPE)
                communicate_returning_strings(p_remote_rm)
                if p_remote_rm.returncode != 0:
                    logger.error("Could not remove remote fifo %s@%s:%s\n%s" % (self.src_user, self.src_host, self.remote_data_fifo, p_remote_rm.stderr))

    def cleanup(self):
        logger.debug('ltacp %s: cleaning up' % (self.logId))

        self._removeRemoteFifo()

        # remove local fifos
        for fifo in self.fifos:
            if os.path.exists(fifo):
                logger.info('ltacp %s: removing local fifo: %s' % (self.logId, fifo))
                os.remove(fifo)
        self.fifos = []

        # cancel any started running process, as they should all be finished by now
        running_procs = dict((p, cl) for (p, cl) in list(self.started_procs.items()) if p.poll() == None)

        if len(running_procs):
            logger.warning('ltacp %s: terminating %d running subprocesses...' % (self.logId, len(running_procs)))
            for p,cl in list(running_procs.items()):
                if isinstance(cl, list):
                    cl = ' '.join(cl)
                logger.warning('ltacp %s: terminated running process pid=%d cmdline: %s' % (self.logId, p.pid, cl))
                p.terminate()
            logger.info('ltacp %s: terminated %d running subprocesses...' % (self.logId, len(running_procs)))
        self.started_procs = {}

        logger.debug('ltacp %s: finished cleaning up' % (self.logId))

# limited standalone mode for testing:
# usage: ltacp.py <remote-host> <remote-path> <surl>
def main():
    # Check the invocation arguments
    parser = OptionParser("%prog [options] <source_host> <source_path> <lta-detination-srm-url>",
                          description='copy a file/directory from <source_host>:<source_path> to the LTA <lta-detination-srm-url>')
    parser.add_option("-u", "--user", dest="user", type="string", default=getpass.getuser(), help="username for to login on <host>, default: %default")
    parser.add_option('-l', '--local_ip', dest='local_ip', type='string', default=getLocalIPAddress(), help='ip address of localhost to which the client side connects via netcat, default: %default')
    parser.add_option('-t', '--timeout', dest='globus_timeout', type='int', default=GLOBUS_TIMEOUT, help='number of seconds (default=%default) to wait for globus-url-copy to finish after the transer is done (while lta-site is computing checksums)')
    parser.add_option('-f', '--force', dest='force', action='store_true', help='force file transfer/copy, even if destination exists (overwrite destanation)')
    parser.add_option('-z', '--zip', dest='zip', action='store_true', help='''zip the source data stream with gzip --fast. This has quite a performance penalty on transfer speed and higher cpu load. In general gzip hardly compresses noisy radio data. We use this option to workaround a bug in the underlying gridftp transfer which sometimes stalles due to a certain byte pattern in the datastream. Gzip alters the datastream, so a stalled transfer is prevented.''')
    parser.add_option('-d', '--dereference', dest='dereference', action='store_true', help='''dereference (follow) all symlinks.''')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    if len(args) != 3:
        parser.print_help()
        sys.exit(1)

    try:
        cp = LtaCp(args[0], args[1], args[2], options.user, options.zip, options.globus_timeout, options.local_ip)

        # make sure that all subprocesses and fifo's are cleaned up when the program exits
        atexit.register(cp.cleanup)

        cp.transfer(options.force, options.dereference)
        sys.exit(0)
    except LtacpException as e:
        logger.error("ltacp transfer raised an exception: %s", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
