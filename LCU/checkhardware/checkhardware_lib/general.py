r"""
general script
"""

from subprocess import (Popen, PIPE)
import traceback
import time
import os
import sys
import logging

general_version = '0913'
logger = logging.getLogger('main.general')
logger.debug("starting general logger")


def write_message(msg):
    run_cmd('wall %s' % str(msg))
    return


# Return date string in the following format YYYYMMDD
def get_short_date_str(tm=time.gmtime()):
    return time.strftime("%Y%m%d", tm)


# Return time string in the following format HH:MM:SS
def get_date_str(tm=time.gmtime()):
    return time.strftime("%d-%m-%Y", tm)


# Return time string in the following format HH:MM:SS
def get_time_str(tm=time.gmtime()):
    return time.strftime("%H:%M:%S", tm)


# Return time string in the following format HH:MM:SS
def get_date_time_str(tm=time.gmtime()):
    return time.strftime("%d-%m-%YT%H:%M:%S", tm)


# Run cmd with args and return response
def run_cmd(cmd=''):
    if cmd != '':
        try:
            _cmd = cmd.replace(' =', '=').replace('= ', '=')
            cmd_list = _cmd.split()
            #print cmd_list
            cmdline = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
            (so, se) = cmdline.communicate()
            if len(so) != 0:
                return so.decode('UTF-8')
            else:
                return 'Error, %s' % se.decode('UTF-8')
        except:
            logger.error('Caught %s', str(sys.exc_info()[0]))
            logger.error(str(sys.exc_info()[1]))
            logger.error('TRACEBACK:\n%s', traceback.format_exc())
            return 'Exception Error'

    return ''


# Get Host name
def get_hostname():
    retries = 0
    while retries < 3:
        try:
            host = run_cmd('hostname -s')
            if host == 'Exception Error':
                host = 'Unknown'
                retries += 1
            if host != 'Unknown':
                break
        except:
            host = 'Unknown'
            retries += 1

    return host.strip()


# file logger
class MyLogger:
    def __init__(self, logdir, filename, screen_prefix=''):
        self.fullFilename = os.path.join(logdir, filename)
        self.logfile = open(self.fullFilename, 'w')
        self.prefix = screen_prefix
        self.start_time = time.time()

    def __del__(self):
        self.logfile.close()

    def get_full_filename(self):
        return self.fullFilename

    def reset_start_time(self, screen=False):
        self.start_time = time.time()
        self.info("Start time %s" % (time.strftime("%H:%M:%S", time.gmtime(self.start_time))), screen=screen)

    def print_busy_time(self, screen=False):
        self.info("Time from start %s" % (time.strftime("%H:%M:%S", (time.gmtime(time.time() - self.start_time)))),
                  screen=screen)

    def print_time_now(self, screen=False):
        self.info("Time %s" % (time.strftime("%H:%M:%S", time.gmtime(time.time()))), screen=screen)

    def info(self, msg, no_end=False, screen=False):
        if len(msg) != 0:
            if screen:
                print(self.prefix + ' ' + msg)
            if not no_end:
                msg += '\n'
            self.logfile.write(msg)
            self.logfile.flush()


class MyTestLogger(MyLogger):
    def __init__(self, logdir, hostname):
        filename =  '%s_station_test.csv' % hostname.upper()
        MyLogger.__init__(self, logdir, filename)

    def add_line(self, info):
        MyLogger.info(self, info)


class MyStationLogger(MyLogger):
    def __init__(self, logdir, hostname, filetime=time.gmtime()):
        filename = "stationtest_%s.log" % hostname
        MyLogger.__init__(self, logdir, filename)
        MyLogger.info(self, "StID  >: %s" % hostname)
        MyLogger.info(self, "Lgfl  >: %s" % (os.path.join(logdir, filename)))
        testdate = time.strftime("%a, %d %b %Y %H:%M:%S", filetime)
        MyLogger.info(self, "Time  >: %s" % testdate)

    def add_line(self, info):
        MyLogger.info(self, info)


class MyPVSSLogger(MyLogger):
    def __init__(self, logdir, hostname):
        filename = '%s_station_test_pvss.log' % hostname
        MyLogger.__init__(self, logdir, filename)
        # cLogger.info(self, "# PVSS input file")

    def add_line(self, info):
        MyLogger.info(self, info)
