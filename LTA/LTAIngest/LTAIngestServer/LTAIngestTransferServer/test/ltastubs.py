#!/usr/bin/env python3

import logging
import uuid
import os, os.path
import subprocess
import lofar.lta.ingest.server.ltacp

logger = logging.getLogger(__name__)

#helper var to pass filename between different stubbed Popen calls
_local_globus_file_path = None

def stub():
    logger.info('stubbing globus-url-copy Popen command')
    #replace original Popen with a stub
    #this stub calls the normal Popen, except for when globus-url-copy is in the args
    #then the globus-url-copy command is replaced by a fake 'transfer'
    #saving the data not to the lta, but to /tmp on the local disk
    def stub_Popen_init(self, args, bufsize=0, executable=None,
                        stdin=None, stdout=None, stderr=None,
                        preexec_fn=None, close_fds=False, shell=False,
                        cwd=None, env=None, universal_newlines=False,
                        startupinfo=None, creationflags=0):

        if 'globus-url-copy' in ' '.join(args):
            dppath = [x for x in args[2].split() if 'file://' in x][0]
            dest_path = [x for x in args[2].split() if 'gsiftp://' in x][0]
            dest_filename = os.path.basename(dest_path)
            global _local_globus_file_path
            _local_globus_file_path = '/tmp/globus_output_%s/%s' % (uuid.uuid1(), dest_filename)
            os.makedirs(os.path.dirname(_local_globus_file_path))
            args = ['cat', dppath.replace('file://', '')]
            stdout = open(_local_globus_file_path, 'w')
            logger.info('replaced globus-url-copy Popen args with: %s, writing stdout into %s', args, _local_globus_file_path)
        self._args = args
        self.__init__org(args, bufsize, executable,
                            stdin, stdout, stderr,
                            preexec_fn, close_fds, shell,
                            cwd, env, universal_newlines,
                            startupinfo, creationflags)

    subprocess.Popen.__init__org = subprocess.Popen.__init__
    subprocess.Popen.__init__ = stub_Popen_init

    logger.info('stubbing srmll command')
    #replace srmll with a stub
    #return a precooked answer
    def stub_srmll(surl, log_prefix='', timeout=-1):
        logger.debug('calling stub_srmll instead on surl: %s, using stubbed _local_globus_file_path: %s', surl, _local_globus_file_path)
        #determine filesize and a32 checksum from localy stored 'globus' file
        with open(_local_globus_file_path) as file:
            p = subprocess.Popen(['md5a32bc', '/dev/null'], stdin=file, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o, e = tuple(x.decode('ascii') for x in p.communicate())

            items = e.strip().split()
            a32cs = items[1].strip().zfill(8)
            fs = items[2].strip()

            #precook fake srmll answer
            lines = ['  %s %s' % (fs, _local_globus_file_path),
                    ' some extra line',
                    ' another line',
                    '  - Checksum value:  %s' % a32cs,
                    '  - Checksum type:  adler32',
                    ' another tail line',
                    ' final line']

            return '\n'.join(lines), '', 0

    lofar.lta.ingest.common.srm.srmll_org = lofar.lta.ingest.common.srm.srmll
    lofar.lta.ingest.common.srm.srmll = stub_srmll

def un_stub():
    global _local_globus_file_path
    #undo stubbing of Popen and srmll
    logger.info('un-stubbing globus-url-copy Popen command')
    subprocess.Popen.__init__ = subprocess.Popen.__init__org

    logger.info('un-stubbing srmll command')
    lofar.lta.ingest.common.srm.srmll = lofar.lta.ingest.common.srm.srmll_org

    if _local_globus_file_path and os.path.exists(_local_globus_file_path):
        logger.info('removing _local_globus_file_path: %s', _local_globus_file_path)
        os.remove(_local_globus_file_path)

        if os.path.isdir(os.path.dirname(_local_globus_file_path)) and 'globus_output_' in os.path.dirname(_local_globus_file_path):
            os.removedirs(os.path.dirname(_local_globus_file_path))

        _local_globus_file_path= None

