#!/usr/bin/env python3


info = '''    ----------------------------------------------------------------------------
    Usage of arguments
    -cf=fullfilename  : full path and filename for the configurationfile to use.
    -l=2              : set level to 2 (default level is 0)
                      level 0    : manual checks, use keys listed below
                      level 1..n : see checkhardware.conf file for checks done

    To start a long check set number of runs or start and stop time, if start time
    is not given the first run is started immediately
    -r=1              : repeats, number of runs to do
    -start=[date_time]: start time of first run, format [YYYYMMDD_HH:MM:SS]
    -stop=[date_time] : stop time of last run, format [YYYYMMDD_HH:MM:SS]

    Set logging level, can be: debug|info|warning|error
    -ls=debug         : print all information on screen, default=info
    -lf=info          : print debug|warning|error information to log file, default=debug

    Select checks to do, can be combined with all levels
    -s(rcumode)       : signal check for rcumode
    -sh(rcumode)      : short test for rcumode 1..4
    -f(rcumode)       : flat test for rcumode 1..4
    -d(rcumode)       : down test for rcumode 1..4
    -o(rcumode)       : oscillation check for rcumode
    -sp(rcumode)      : spurious check for rcumode
    -n(rcumode)[=120] : noise check for rcumode, optional data time in seconds default = 120 sec.
    -e(rcumode)[=12]  : do all HBA element tests, optional data time in seconds default = 4 sec.
    -sn(rcumode)      : HBA summator noise check.
    -m(rcumode)       : HBA modem check.

    -rcu(mode)        : do all rcu(mode) tests

    -rv               : RSP version check, always done
    -tv               : TBB version check, always done

    -rbc              : RSP board check, voltage and temperature
    -tbc              : TBB board check, voltage and temperature
    -spu              : SPU voltage check
    -tm               : TBB memmory check

    example   : ./checkHardware.py -s5 -n5=180
    ----------------------------------------------------------------------------'''


import os
import sys
import traceback
from time import sleep
import time
import datetime
from socket import gethostname
import logging
from signal import SIGABRT, SIGINT, SIGTERM, signal
import atexit
from subprocess import Popen, check_call, CalledProcessError, STDOUT, check_output
from functools import partial

# FIXME: There is _way_ too much going on here outside a function, including things that might fail (like path checks)
# FIXME: emoving hard dependencies on station environment

os.umask(0o001)

conf_file = r'check_hardware.conf'

mainpath = r'/opt/stationtest'
maindatapath = r'/localhome/stationtest'

confpath = os.path.join(maindatapath, 'config')
logpath = os.path.join(maindatapath, 'log')

# if not exists make path
if not os.access(logpath, os.F_OK):
    os.mkdir(logpath)

hostname = gethostname().split('.')[0].upper()
station_name = hostname

# first start main logging before including checkhardware_lib
# backup log files
for nr in range(8, -1, -1):
    if nr == 0:
        full_filename = os.path.join(logpath, 'check_hardware.log')
    else:
        full_filename = os.path.join(logpath, 'check_hardware.log.%d' % nr)
    full_filename_new = os.path.join(logpath, 'check_hardware.log.%d' % (nr + 1))
    if os.path.exists(full_filename):
        os.rename(full_filename, full_filename_new)

# make and setup logger
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler
filename = 'check_hardware.log'
full_filename = os.path.join(logpath, filename)
file_handler = logging.FileHandler(full_filename, mode='w')
formatter = logging.Formatter('%(asctime)s %(name)-14s %(levelname)-8s %(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# create console handler
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-14s %(levelname)-7s %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)
logger.addHandler(stream_handler)

file_logger_handler = logger.handlers[0]
screen_logger_handler = logger.handlers[1]

sleep(2.0)
logger.debug("logger is working")

# now include checkhardware library
from checkhardware_lib import read_station_config
from checkhardware_lib import swlevel
from checkhardware_lib import rspctl
from checkhardware_lib import RSP
from checkhardware_lib import check_active_boards
from checkhardware_lib import check_active_tbbdriver
from checkhardware_lib import check_active_rspdriver
from checkhardware_lib import reset_rsp_settings
from checkhardware_lib import HBA
from checkhardware_lib import reset_48_volt
from checkhardware_lib import tbbctl
from checkhardware_lib import init_lofar_lib
from checkhardware_lib import TestSettings
from checkhardware_lib import lofar
from checkhardware_lib import DB
from checkhardware_lib import is_test_mode_active
from checkhardware_lib import write_message
from checkhardware_lib import make_report
from checkhardware_lib import CoreStations
from checkhardware_lib import RemoteStations
from checkhardware_lib import LBA
from checkhardware_lib import remove_all_data_files
from checkhardware_lib import SPU
from checkhardware_lib import TBB
from checkhardware_lib import activate_test_mode




check_version = '0516'

rcu_keys = ('RCU1', 'RCU2', 'RCU3', 'RCU4', 'RCU5', 'RCU6', 'RCU7')
rcu_m1_keys = ('O1', 'SP1', 'N1', 'S1', 'SH1', 'D1', 'F1')
rcu_m2_keys = ('O2', 'SP2', 'N2', 'S2', 'SH2', 'D2', 'F2')
rcu_m3_keys = ('O3', 'SP3', 'N3', 'S3', 'SH3', 'D3', 'F3')
rcu_m4_keys = ('O4', 'SP4', 'N4', 'S4', 'SH4', 'D4', 'F4')
rcu_m5_keys = ('M5', 'O5', 'SN5', 'SP5', 'N5', 'S5', 'E5')
rcu_m6_keys = ('M6', 'O6', 'SN6', 'SP6', 'N6', 'S6', 'E6')
rcu_m7_keys = ('M7', 'O7', 'SN7', 'SP7', 'N7', 'S7', 'E7')

rcu_m12_keys = rcu_m1_keys + rcu_m2_keys
rcu_m34_keys = rcu_m3_keys + rcu_m4_keys
rcu_m567_keys = rcu_m5_keys + rcu_m6_keys + rcu_m7_keys

rsp_keys = ('RV', 'SPU', 'RBC') + rcu_keys + rcu_m12_keys + rcu_m34_keys + rcu_m567_keys
tbb_keys = ('TV', 'TM', 'TBC')
control_keys = ('R', 'START', 'STOP', 'TST')
all_keys = control_keys + rsp_keys + tbb_keys
rsp_check = False
tbb_check = False

args = dict()

# version checks are always done
args['RV'] = '-'
args['TV'] = '-'

def print_help():
    print(info)


# return readable info for test
def get_test_info(key=''):
    if key[-1] in '1234567':
        test_name = ''
        test = key[:-1]
        mode = key[-1]

        if mode in '1234':
            ant_type = 'LBA'
        else:
            ant_type = 'HBA'

        if test in ('O',):
            test_name += 'Oscillation'
        if test in ('SP',):
            test_name += 'Spurious'
        if test in ('N',):
            test_name += 'Noise'
        if test in ('S',):
            test_name += 'RF'
        if test in ('SH',):
            test_name += 'Short'
        if test in ('D',):
            test_name += 'Down'
        if test in ('F',):
            test_name += 'Flat'
        if test in ('SN',):
            test_name += 'Summator noise'
        if test in ('E',):
            test_name += 'Element'
        if test in ('M',):
            test_name += 'Modem'
        if test in ('RCU',):
            test_name += 'All tests'

        return '%s mode-%c %s check' % (ant_type, mode, test_name)

    if key == 'RV':
        return 'RSP Version check'
    if key == 'SPU':
        return 'SPU check'
    if key == 'RBC':
        return 'RSP board checks'
    if key == 'TV':
        return 'TBB Version check'
    if key == 'TM':
        return 'TBB Memory check'
    if key == 'TBC':
        return 'TBB board checks'
    if key == 'START':
        return 'START checks'
    if key == 'STOP':
        return 'STOP checks'
    if key == 'R':
        return 'Number of test repeats set to'
    return ''


def add_to_args(key, value):
    if key == '':
        return
    global args, rsp_check, tbb_check
    if key in rsp_keys or key in tbb_keys or key in ('H', 'L', 'LS', 'LF', 'R', 'START', 'STOP', 'TST'):
        if value != '-':
            args[key] = value
        else:
            args[key] = '-'

        if key in rsp_keys:
            rsp_check = True
        if key in tbb_keys:
            tbb_check = True
    else:
        sys.exit('Unknown key %s' % key)
    return


def get_arguments():
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            opt = arg[1:].strip().upper()
            valpos = opt.find('=')
            if valpos != -1:
                key, value = opt.split('=')
            else:
                key, value = opt, '-'
            add_to_args(key=key.strip(), value=value.strip())
    return


# get checklevel and set tests to do
def set_tests(conf):
    level = args.get('L', '0')
    if level == '0':
        return
    tests = conf.as_string('always').split(',')
    tests += conf.as_string('list.%s' % level).split(',')
    logger.debug("test= %s" % tests)
    for tst in tests:
        opt = tst.strip().upper()
        valpos = opt.find('=')
        if valpos != -1:
            key, value = opt.split('=')
        else:
            key, value = opt, '-'
        add_to_args(key=key.strip(), value=value.strip())
    return

# setup default python logging system
# logstream for screen output
def init_logging():
    log_levels = {'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR}

    file_log_level = args.get('LF', 'DEBUG')
    if file_log_level not in log_levels:
        sys.exit('LF=%s, Not a legal log level, try again' % file_log_level)

    screen_log_level = args.get('LS', 'WARNING')
    if screen_log_level not in log_levels:
        sys.exit('LS=%s, not a legal log level, try again' % screen_log_level)

    if 'LF' in args:
        file_logger_handler.setLevel(log_levels[file_log_level])
    if 'LS' in args:
        screen_logger_handler.setLevel(log_levels[screen_log_level])
    return


def wait_for_start(start_datetime):
    start_time = time.mktime(start_datetime.timetuple())
    if start_time > time.time():
        logger.info('delayed start, sleep till %s' % (time.asctime(start_datetime.timetuple())))

    while start_time > time.time():
        wait_time = start_time - time.time()
        sleep_time = min(wait_time, 3600.0)
        sleep(sleep_time)
    return


def stop_test_signal(cmd):
    logger.info("Stopping test signal.")

    # try to execute command to stop test signal
    try:
        check_call(cmd, shell=True)
    except CalledProcessError as ex:
        logger.error(("Could not stop the test signal! Non-zero return code from start_cmd (%s)." % cmd), ex)
        raise

def stop_test_signal_and_exit(cmd, *optargs):
    """
    Signal handler that exits with the return code of a passed POSIX signal after executing the provided command.

    :param cmd: The command to stop the test signal
    :param optargs: The intercepted POSIX signal
    """
    stop_test_signal(cmd)
    exit_without_triggering_handler(cmd, *optargs)


def exit_without_triggering_handler(cmd, *optargs):
    """
    :param cmd: The command to stop the test signal
    :param optargs: The intercepted POSIX signal
    """

    # try to get correct return code
    logger.info('Now exiting.')
    try:
        ret_code = int(optargs[0])  # use POSIX signal code
        os._exit(ret_code)  # sys.exit() won't work here, we don't want to trigger our handler again
        # (hm, we could actually call sys.exit and just trigger the atexit handler, but this is more explicit and keeps
        # things operational independently.)
    except:
        os._exit(1)


def register_exit_handler(cmd):
    """
    execute stop_cmd when script exits normally or with Exception
    :param cmd: the command to execute
    """
    # execute stop_cmd when script exits normally
    atexit.register(stop_test_signal, cmd)


def register_signal_handlers(cmd):
    """
    execute stop_cmd when script is terminated externally
    :param cmd: the command to execute
    """
    # execute stop_cmd when script exits normally
    atexit.register(stop_test_signal, cmd)

    # handle POSIX signals
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, partial(stop_test_signal_and_exit, cmd))


def start_watchdog_daemon(pid, cmd):
    """
    Start a daemon that sits and waits for this script to terminate and then execute the provided command.
    We cannot handle SIGKILL / kill -9 from inside the script, so we have to handle that case this way. This may be
    a bit --wait for it-- overkill (hah!) and I don't see why this would be needed under normal circumstances, but
    nonetheless, since this was requested on the ticket, here we go.
    :param cmd: command as shell-executable string
    """
    daemon_cmd = 'while ps -p %s > /dev/null; do sleep 1; done; %s' % (pid, cmd)
    Popen(daemon_cmd, stdout=open('/dev/null', 'w'), stderr=STDOUT, shell=True, preexec_fn=os.setpgrp)


def safely_start_test_signal(start_cmd, stop_cmd):
    """
    This will start start_cmd and set things up in a way that stop_cmd is executed in case the check_hardware script
    either exits regularly or gets killed for some reason by a POSIX signal. stop_cmd might be executed repeatedly
    under circumstances.
    :param start_cmd: the command to start as shell-executable string
    :param stop_cmd: the command to stop on exit as shell-executable string
    """

    # set things up sp signal is stopped when check_hardware terminates
    register_signal_handlers(stop_cmd)
    register_exit_handler(stop_cmd)
    start_watchdog_daemon(os.getpid(), stop_cmd)  # this alone would actually be sufficient

    # start signal
    try:
        check_call(start_cmd, shell=True)
    except CalledProcessError as ex:
        logger.error("Could not start the test signal! Non-zero return code from start_cmd (%s)." % start_cmd, ex)
        raise


def safely_start_test_signal_from_ParameterSet(settings):
    '''
    :param settings: A settings.ParameterSet (e.g. obtained through TestSettings.group)
    '''
    try:
        start_cmd = settings.parset['testsignal']['start-cmd']
        stop_cmd = settings.parset['testsignal']['stop-cmd']
        logger.info('Test signal start/stop settings found. (%s // %s)' % (start_cmd, stop_cmd))

        # start signal:
        safely_start_test_signal(start_cmd, stop_cmd)

        try:
            status_cmd = settings.parset['testsignal']['status-cmd']
            ok_status = settings.parset['testsignal']['ok-status']
            logger.info('Test signal status settings found. (%s // %s)' % (status_cmd, ok_status))

            # wait for signal status to be ok:
            wait_for_test_signal_status(status_cmd, ok_status)

        except KeyError:
            logger.info('No test signal status settings found.')

    except KeyError:
        logger.info('No test signal settings found.')


def wait_for_test_signal_status(status_cmd, status, retry_limit=30):
    """
    :param status_cmd: command to get test signal status
    :param status: the command output to wait for
    :param retry_limit: raise RunTimeError after this many status_cmd that did not return status
    """
    logger.info("Waiting for '%s' to return '%s'" % (status_cmd, status))
    out = None
    for _ in range(retry_limit):
        out = check_output(status_cmd, shell=True)
        out = out.strip()
        if out == status:
            logger.info("Status ok.")
            return status
        else:
            logger.info('Wrong status: %s != %s. Try again...'% (out, status))
        sleep(1)

    raise RuntimeError("Timed out. Last response was '%s'" % out)


def main():
    global station_name
    get_arguments()
    # print args
    if len(args) == 0 or 'H' in args:
        print_help()
        sys.exit()

    init_logging()
    init_lofar_lib()

    full_filename = os.path.join(confpath, conf_file)
    conf = TestSettings(filename=full_filename)

    if 'TST' in args:
        lofar.testmode = True
        logger.info("**** NOW IN TESTMODE ****")

    set_tests(conf.group('check'))

    logger.info('== START HARDWARE CHECK ==')
    logger.info('== requested checks and settings ==')
    logger.info('-'*40)
    for i in all_keys:
        if i in args:
            if args.get(i) == '-':
                logger.info(' %s' % (get_test_info(i)))
            else:
                logger.info(' %s, time = %s' % (get_test_info(i), args.get(i)))
    logger.info('-'*40)

    # use format YYYYMMDD_HH:MM:SS
    stop_time = -1
    if 'STOP' in args:
        stop = args.get('STOP')
        if len(stop) != 17:
                return 'wrong stoptime format must be YYYYMMDD_HH:MM:SS'
        stop_datetime = datetime.datetime(int(stop[:4]), int(stop[4:6]), int(stop[6:8]),
                                          int(stop[9:11]), int(stop[12:14]), int(stop[15:]))
        stop_time = time.mktime(stop_datetime.timetuple())

        if 'START' in args:
            start = args.get('START')
            if len(start) != 17:
                return 'wrong starttime format must be YYYYMMDD_HH:MM:SS'
            start_datetime = datetime.datetime(int(start[:4]), int(start[4:6]), int(start[6:8]),
                                               int(start[9:11]), int(start[12:14]), int(start[15:]))
            if time.mktime(start_datetime.timetuple()) < time.time():
                # print time.mktime(start_datetime.timetuple()), time.time()
                logger.error('Stop program, StartTime in past')
                return 2
            if time.mktime(start_datetime.timetuple()) > stop_time:
                logger.error('Stop program, stop before start')
                return 2
            wait_for_start(start_datetime)

        logger.info('run checks till %s' % (time.asctime(stop_datetime.timetuple())))


    # Read in RemoteStation.conf
    st_id, n_rsp, n_tbb, n_lbl, n_lbh, n_hba, hba_split = read_station_config()
    logger.info("Station configuration %s:" % station_name)
    logger.info("   ID                   = %d" % st_id)
    logger.info("   nr RSP boards        = %d" % n_rsp)
    logger.info("   nr TB boards         = %d" % n_tbb)
    logger.info("   nr LBA low antennas  = %d" % n_lbl)
    logger.info("   nr LBA high antennas = %d" % n_lbh)
    logger.info("   nr HBA high antennas = %d" % n_hba)
    logger.info("   has HBA splitter     = %d" % hba_split)

    # setup intern database with station layout
    db = DB(station_name, n_rsp, n_tbb, n_lbl, n_lbh, n_hba, hba_split)
    # if in local testmode
    logger.debug("testmode= %s" % str(is_test_mode_active()))
    if st_id == 9999:
        station_name = 'CS001C'
        activate_test_mode()
    logger.debug("testmode= %s" % str(is_test_mode_active()))
    if stop_time > 0.0:
        db.set_test_end_time((stop_time - 120.0))

    # set manualy marked bad antennas
    full_filename = conf().get('files.bad-antenna-list')
    try:
        f = open(full_filename, 'r')
        data = f.readlines()
        f.close()
        logger.info('get bad_antenna_list data "%s"' % full_filename)
        for line in data:
            if line[0] == '#':
                continue
            ant_list = line.strip().split(' ')
            if ant_list[0].strip().upper() == station_name.upper():
                if len(ant_list) > 1:
                    for ant in ant_list[1:]:
                        ant_type = ant[:3].strip().upper()
                        if ant_type == 'LBA':
                            ant_nr = int(ant[3:].strip())
                            # print 'ant type=%s nr=%d' % (ant_type, ant_nr)
                            if ant_nr < n_lbh:
                                db.lbh.ant[ant_nr].on_bad_list = 1
                            else:
                                db.lbl.ant[ant_nr-n_lbh].on_bad_list = 1
                        elif ant_type == 'HBA':
                            ant_nr = int(ant[3:].strip())
                            # print 'ant type=%s nr=%d' % (ant_type, ant_nr)
                            db.hba.tile[ant_nr].on_bad_list = 1
                break
    except IOError:
        logger.warning('bad_antenna_list data from file "%s" not found' % full_filename)

    db.check_start_time = time.gmtime()

    write_message(
        '!!!  This station will be in use for a test! Please do not use the station!  (script version %s)  !!!'
        % check_version
    )
    start_level, board_errors = swlevel()
    if start_level < 0:
        sw_level, board_errors = swlevel(1)
        start_level = abs(start_level)
    sw_level, board_errors = swlevel(2)
    if start_level < 2:
        logger.info('Wait 30 seconds while startup RSPDriver')
        time.sleep(30.0)
    rsp_ready, tbb_ready = check_active_boards(db, n_rsp, n_tbb, 2)
    if rsp_ready:
        # do RSP tests if requested
        if rsp_check is True:
            if 'RV' in args:
                rsp = RSP(db)
                rsp.check_versions(conf.group('rsp'))

            reset_rsp_settings()

            repeats = int(args.get('R', '1'))
            repeat_cnt = 1

            runtime = 0
            db.tests = ''
            while repeat_cnt <= repeats or (stop_time > -1 and (time.time() + runtime) < stop_time):

                try:
                    runstart = time.time()
                    if stop_time > -1:
                        logger.info('\n=== Start testrun %d ===\n' % repeat_cnt)
                    else:
                        logger.info('\n=== Start testrun %d of %d ===\n' % (repeat_cnt, repeats))

                    if 'SPU' in args:
                        spu = SPU(db)
                        spu.check_status(conf.group('spu'))

                    if 'RBC' in args:
                        rsp = RSP(db)
                        rsp.check_board(conf.group('rsp'))

                    # check if mode 1,2 is available on this station
                    if station_name in CoreStations or station_name in RemoteStations:
                        for mode in (1, 2):
                            lbl = LBA(db, 'LBL')
                            settings = conf.rcumode(mode)
                            # do all rcumode 1,2 tests
                            if 'RCU%d' % mode in args or 'SH%d' % mode in args:
                                lbl.check_short(mode=mode, parset=settings)

                            if 'RCU%d' % mode in args or 'F%d' % mode in args:
                                lbl.check_flat(mode=mode, parset=settings)

                            if 'RCU%d' % mode in args or 'D%d' % mode in args:
                                lbl.check_down(mode=mode, parset=settings)

                            if 'RCU%d' % mode in args or 'O%d' % mode in args:
                                lbl.check_oscillation(mode=mode, parset=settings)

                            if 'RCU%d' % mode in args or 'SP%d' % mode in args:
                                lbl.check_spurious(mode=mode, parset=settings)

                            if 'RCU%d' % mode in args or 'N%d' % mode in args:
                                if 'RCU%d' % mode in args or args.get('N%d' % mode) == '-':
                                    recordtime = 60
                                else:
                                    recordtime = int(args.get('N%d' % mode))
                                lbl.check_noise(mode=mode, record_time=recordtime, parset=settings)

                            if 'RCU%d' % mode in args or 'S%d' % mode in args:
                                lbl.check_rf_power(mode=mode, parset=settings)

                    for mode in (3, 4):
                        lbh = LBA(db, 'LBH')
                        settings = conf.rcumode(mode)
                        # do all rcumode 3,4 tests
                        if 'RCU%d' % mode in args or 'SH%d' % mode in args:
                            lbh.check_short(mode=mode, parset=settings)

                        if 'RCU%d' % mode in args or 'F%d' % mode in args:
                            lbh.check_flat(mode=mode, parset=settings)

                        if 'RCU%d' % mode in args or 'D%d' % mode in args:
                            lbh.check_down(mode=mode, parset=settings)

                        if 'RCU%d' % mode in args or 'O%d' % mode in args:
                            lbh.check_oscillation(mode=mode, parset=settings)

                        if 'RCU%d' % mode in args or 'SP%d' % mode in args:
                            lbh.check_spurious(mode=mode, parset=settings)

                        if 'RCU%d' % mode in args or 'N%d' % mode in args:
                            if 'RCU%d' % mode in args or args.get('N%d' % mode) == '-':
                                recordtime = 60
                            else:
                                recordtime = int(args.get('N%d' % mode))
                            lbh.check_noise(mode=mode, record_time=recordtime, parset=settings)

                        if 'RCU%d' % mode in args or 'S%d' % mode in args:
                            lbh.check_rf_power(mode=mode, parset=settings)

                    for mode in (5, 6, 7):

                        # do all rcumode 5, 6, 7 tests
                        hba = HBA(db)
                        tile_settings = conf.group('rcumode.%d.tile' % mode)
                        elem_settings = conf.group('rcumode.%d.element' % mode)

                        if 'RCU%d' % mode in args or 'M%d' % mode in args:
                            hba.check_modem(mode=mode)
                            hba.turn_off_bad_tiles()

                        if 'RCU%d' % mode in args or 'O%d' % mode in args:
                            hba.check_oscillation(mode=mode, parset=tile_settings)

                        if 'RCU%d' % mode in args or 'SN%d' % mode in args:
                            hba.check_summator_noise(mode=mode, parset=tile_settings)

                        if 'RCU%d' % mode in args or 'SP%d' % mode in args:
                            hba.check_spurious(mode=mode, parset=tile_settings)

                        if 'RCU%d' % mode in args or 'N%d' % mode in args:
                            if 'RCU%d' % mode in args or args.get('N%d' % mode) == '-':
                                recordtime = 60
                            else:
                                recordtime = int(args.get('N%d' % mode))
                            hba.check_noise(mode=mode, record_time=recordtime, parset=tile_settings)

                        # if 'RCU%d' % mode in args or 'S%d' % mode in args:
                        if 'S%d' % mode in args:
                            safely_start_test_signal_from_ParameterSet(tile_settings)
                            hba.check_rf_power(mode=mode, parset=tile_settings)

                        runtime = (time.time() - runstart)

                        # All element test
                        if 'E%d' % mode in args:
                            if args.get('E%d' % mode) == '-':
                                recordtime = 4
                            else:
                                recordtime = int(args.get('E%d' % mode))
                            safely_start_test_signal_from_ParameterSet(elem_settings)
                            hba.check_elements(mode=mode, record_time=recordtime, parset=elem_settings)

                    # stop test if driver stopped
                    db.rsp_driver_down = not check_active_rspdriver()
                    if db.rsp_driver_down and (restarts > 0):          # FIXME 'restarts' is undefined at this point?!
                        restarts -= 1
                        reset_48_volt()
                        time.sleep(30.0)
                        level, board_errors = swlevel(2)
                        if len(board_errors) > 0:
                            db.board_errors = board_errors
                            break
                        else:
                            time.sleep(30.0)

                    # one run done
                    repeat_cnt += 1

                except:
                    logger.error('Caught %s', str(sys.exc_info()[0]))
                    logger.error(str(sys.exc_info()[1]))
                    logger.error('TRACEBACK:\n%s', traceback.format_exc())
                    logger.error('Aborting NOW')
                    break

            db.rsp_driver_down = not check_active_rspdriver()
            if not db.rsp_driver_down:
                reset_rsp_settings()


    # do TBB tests if requested
    if tbb_check is True:
        tbb = TBB(db)
        try:
            if 'TV' in args:
                tbb.check_versions(conf.group('tbb'))

            if 'TBC' in args:
                tbb.check_board(conf.group('tbb'))

            if 'TM' in args:
                tbb.check_memory()
        except:
            logger.error('Program fault, TBB test')
            logger.error('Caught %s', str(sys.exc_info()[0]))
            logger.error(str(sys.exc_info()[1]))
            logger.error('TRACEBACK:\n%s', traceback.format_exc())
            logger.error('Aborting NOW')

        db.tbb_driver_down = not check_active_tbbdriver()

    db.check_stop_time = time.gmtime()


    if len(sys.argv) > 1:
        try:
            # do db test and write result files to log directory
            report_dir = conf().as_string('paths.local-report-dir')
            if os.path.exists(report_dir):
                logger.info('write result data')
                db.test()
                make_report(db, report_dir)
            else:
                logger.warning('not a valid report directory')
            # delete files from data directory
            remove_all_data_files()
        except:
            logger.error('Program fault, reporting and cleanup')
            logger.error('Caught %s', str(sys.exc_info()[0]))
            logger.error(str(sys.exc_info()[1]))
            logger.error('TRACEBACK:\n%s', traceback.format_exc())
            logger.error('Aborting NOW')

        logger.info('Check if boards are still ok')
        check_active_boards(db, n_rsp, n_tbb, 1)

    if check_active_tbbdriver() == True:
        # set mode to transient (also needed to set the right ethernet header to cep),
        # free all memory allocations, reallocate again and start recording
        tbbctl('--mode=transient')
        tbbctl('--free')
        tbbctl('--alloc')
        tbbctl('--record')

    if check_active_rspdriver() == True:
        # activate datastream from rsp to tbb in transient mode
        rspctl('--tbbmode=transient')
        logger.info('Going back to swlevel %d' % start_level)
        swlevel(start_level)

    logger.info('Test ready.')
    write_message('!!!     The test is ready and the station can be used again!      !!!')

    return 0

if __name__ == '__main__':
    sys.exit(main())


