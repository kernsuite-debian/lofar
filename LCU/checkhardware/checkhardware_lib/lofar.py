# lofar_lib

import os
import sys
import time
import logging
import socket
import struct
import string
from .general import *

os.umask(0o01)
lofar_version = '0514'
testmode = False
#testmode = True


CoreStations = ('CS001C', 'CS002C', 'CS003C', 'CS004C', 'CS005C', 'CS006C', 'CS007C', 'CS011C', 'CS013C', 'CS017C',
                'CS021C', 'CS024C', 'CS026C', 'CS028C', 'CS030C', 'CS031C', 'CS032C', 'CS101C', 'CS103C', 'CS201C',
                'CS301C', 'CS302C', 'CS401C', 'CS501C')

RemoteStations = ('RS106C', 'RS205C', 'RS208C', 'RS210C', 'RS305C', 'RS306C', 'RS307C', 'RS310C', 'RS406C', 'RS407C',
                  'RS409C', 'RS503C', 'RS508C', 'RS509C')

InternationalStations = ('DE601C', 'DE602C', 'DE603C', 'DE604C', 'DE605C', 'DE609C', 'FR606C', 'SE607C',
                         'UK608C', 'PL610C', 'PL611C', 'PL612C')

StationType = {'CS': 1, 'RS': 2, 'IS': 3}

logger = logging.getLogger('main.lofar')
logger.debug("starting lofar logger")

active_delay_str = ('555,' * 16)[:-1]


def activate_test_mode():
    global testmode
    testmode = True


def is_test_mode_active():
    return testmode


def init_lofar_lib():
    if not os.access(data_dir(), os.F_OK):
        os.mkdir(data_dir())


def data_dir():
    return r'/localhome/stationtest/sb_data'


# remove all *.dat
def remove_all_data_files():
    if not testmode:
        if os.access(data_dir(), os.F_OK):
            files = os.listdir(data_dir())
            # print files
            for f in files:
                if f[-3:] == 'dat' or f[-3:] == 'nfo':
                    os.remove(os.path.join(data_dir(), f))


# return station type
def get_station_type(StID):
    if StID in CoreStations:
        return StationType['CS']
    if StID in RemoteStations:
        return StationType['RS']
    if StID in InternationalStations:
        return StationType['IS']


# read from RemoteStation.conf file number of RSP and TB Boards
"""
#
# THIS FILE IS GENERATED, DO NOT MODIFY IT.
#
# RemoteStation.conf for CS002
#
# Describes the amount of available hardware on the station.
#

RS.STATION_ID  = 2
RS.N_RSPBOARDS = 12
RS.N_TBBOARDS  = 6
RS.N_LBAS      = 96
RS.N_HBAS      = 48
RS.HBA_SPLIT   = Yes
RS.WIDE_LBAS   = Yes
"""


def read_station_config():
    f = open('/opt/lofar/etc/RemoteStation.conf', 'r')
    lines = f.readlines()
    f.close()

    st_id = nrsp = ntbb = nlba = nlbl = nlbh = nhba = hba_split = 0

    for line in lines:
        if (line[0] == '#') or (len(line) < 2):
            continue
        key, val = line.split('=')
        key = key.strip()
        val = val.strip()
        if key == "RS.STATION_ID":
            st_id = int(val)
            continue
        if key == "RS.N_RSPBOARDS":
            nrsp = int(val)
            continue
        if key == "RS.N_TBBOARDS":
            ntbb = int(val)
            continue
        if key == "RS.N_LBAS":
            nlba = int(val)
            if nlba == nrsp * 8:
                nlbl = nlba // 2
                nlbh = nlba // 2
            else:
                nlbl = 0
                nlbh = nlba
            continue
        if key == "RS.N_HBAS":
            nhba = int(val)
            continue
        if key == "RS.HBA_SPLIT":
            if str.upper(val) == "YES":
                hba_split = 1
                continue
    return st_id, nrsp, ntbb, nlbl, nlbh, nhba, hba_split


# [lofarsys@RS306C stationtest]$ swlevel 2
# Going to level 2
# Starting RSPDriver
# Loading image 4 on RSPboard 0 ...
# Loading image 4 on RSPboard 1 ...
# Loading image 4 on RSPboard 2 ...
# Loading image 4 on RSPboard 3 ...
# Loading image 4 on RSPboard 4 ...
# Loading image 4 on RSPboard 5 ...
# Loading image 4 on RSPboard 6 ...
# Loading image 4 on RSPboard 7 ...
# RSPboard 8: Error requesting active firmware version (communication error)
# Loading image 4 on RSPboard 9 ...
# Loading image 4 on RSPboard 10 ...
# Loading image 4 on RSPboard 11 ...
# One or more boards have a communication problem; try reset the 48V
# root     21470     1  1 10:41 pts/2    00:00:00 /opt/lofar/bin/RSPDriver
# Starting TBBDriver
# root     21492     1  0 10:41 pts/2    00:00:00 /opt/lofar/bin/TBBDriver
#
# Status of all software level:
# 1 : PVSS00pmon                16177
# 1 : SoftwareMonitor           16227
# 1 : LogProcessor              16248
# 1 : ServiceBroker             16278
# 1 : SASGateway                16299
# ---
# 2 : RSPDriver                 21470
# 2 : TBBDriver                 21492
# ---
# 3 : CalServer                 DOWN
# 3 : BeamServer                DOWN
# ---
# 4 : HardwareMonitor           DOWN
# ---
# 5 : SHMInfoServer             DOWN
# ---
# 6 : CTStartDaemon             DOWN
# 6 : StationControl            DOWN
# 6 : ClockControl              DOWN
# 6 : CalibrationControl        DOWN
# 6 : BeamControl               DOWN
# 6 : TBBControl                DOWN
# ---

def swlevel(level=None):
    # level = None
    _level = level
    board_errors = list()
    if level is not None:
        if _level < 0:
            _level *= -1
        answer = run_cmd('swlevel %d' % _level)
    else:
        answer = run_cmd('swlevel')

    #print answer
    current_level = 0
    for line in answer.splitlines():
        if line.find("Going to level") > -1:
            current_level = int(line.split()[-1])

        elif line.find("Currently set level") > -1:
            current_level = int(line.strip().split()[-1])
            if current_level < 0:
                logger.warning("Current swlevel is %d" % current_level)
        if line.find("Error requesting active firmware version") > -1:
            endpos = line.find(":")
            board_errors.append(int(line[:endpos].split()[1]))
            logger.warning(line)
    logger.info("current swlevel = %s" % current_level)
    return current_level, board_errors


def reset_48_volt():
    logger.info("Try to reset 48V power")
    ec_name = socket.gethostname()[:-1] + "ec"
    ec_ip = socket.gethostbyname(ec_name)
    logger.debug("EC to connect = %s" % ec_ip)

    try:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        # sck.close()
        return
    except:
        raise

    try:
        sck.settimeout(4.0)
        sck.connect((ec_ip, 10000))
        time.sleep(0.5)
        cmd = struct.pack('hhh', 22, 0, 0)
        logger.debug("send cmd")
        sck.send(cmd)
        sck.settimeout(4.0)
        logger.debug("recv cmd")
        data = sck.recv(6)
        sck.close()
        logger.debug("reset done")
    except socket.error:
        logger.error("ec socket connect error")
        sck.close()
    except:
        raise




# Run rspctl command with given args and return response
def rspctl(args='', wait=0.0):
    if str(args) != '':
        logger.debug("rspctl %s" % str(args))
        response = run_cmd('rspctl %s' % str(args))
        if not testmode and wait > 0.0:
            time.sleep(wait)
        return response
    return 'No args given'


# Run tbbctl command with given args and return response
def tbbctl(args=''):
    if str(args) != '':
        logger.debug("tbbctl %s" % str(args))
        return run_cmd('tbbctl %s' % str(args))
    return 'No args given'


def check_active_tbbdriver():
    answer = run_cmd('swlevel').strip().splitlines()
    for line in answer:
        if line.find('TBBDriver') > -1:
            if line.find('DOWN') != -1:
                return False
    return True


# wait until all boards have a working image loaded
# returns 1 if ready or 0 if timed_out
def wait_tbb_ready(n_boards=6):
    board_active = [True] * n_boards
    timeout = 30
    logger.info("wait for working TBB boards ")
    while timeout > 0:
        answer = tbbctl('--version')
        # print answer
        if answer.find('TBBDriver is NOT responding') > 0:
            if timeout < 10:
                logger.warning("TBBDriver is NOT responding, try again in every 5 seconds")
            time.sleep(5.0)
            timeout -= 5
            continue

        # check if image_nr > 0 for all boards
        if answer.count('V') == (n_boards * 4):
            logger.debug("All boards in working image")
            return True, board_active

        reset_list = []
        board_not_ready = False
        for line in answer.splitlines():
            if line.count('V') == 4:
                board_nr = int(line.split()[0])
                board_active[board_nr] = True
            if 'boards not active' in line:
                board_nr = int(line.split()[0])
                board_active[board_nr] = False
            if 'mpi time-out' in line:
                board_nr = line.split()[0]
                reset_list.append(board_nr)
            if 'board not ready' in line:
                board_not_ready = True

        if board_not_ready:
            timeout += 5.0

        if len(reset_list) > 0:
            tbbctl('--reset --select=%s' % ','.join(reset_list))
            reset_list = []
            timeout += 35.0
            time.sleep(35.0)

        time.sleep(1.0)
        timeout -= 1

    logger.warning("Not all TB boards in working image")
    return False, board_active


def check_active_rspdriver():
    answer = run_cmd('swlevel').strip().splitlines()
    for line in answer:
        if line.find('RSPDriver') > -1:
            if line.find('DOWN') != -1:
                return False
    return True


# wait until all boards have a working image loaded
# returns 1 if ready or 0 if timed_out
#
# [lofarsys@RS306C ~]$ rspctl --version
# RSP[ 0] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 1] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 2] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 3] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 4] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 5] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 6] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 7] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 8] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[ 9] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[10] RSP version = 0, BP version = 0.0, AP version = 0.0
# RSP[11] RSP version = 0, BP version = 0.0, AP version = 0.0

def wait_rsp_ready():
    timeout = 60
    logger.info("wait for working RSP boards ")
    sys.stdout.flush()
    while timeout > 0:
        answer = rspctl('--version')
        # print answer
        if answer.count('No Response') > 0:
            time.sleep(5.0)
            timeout -= 5
            if timeout < 60:
                return 0
            continue
        # check if image_nr > 0 for all boards
        if answer.count('0.0') == 0:
            logger.debug("All boards in working image")
            return 1
        else:
            logger.warning("Not all RSP boards in working image")
            logger.debug(answer)
        if not testmode:
            time.sleep(5.0)
        timeout -= 1
    return 0


def check_active_boards(db, n_rsp_boards, n_tbb_boards, n_retries):
    # check if RSPDriver is running
    rsp_ready = False
    tbb_ready = False
    restarts  = n_retries

    # wait for RSP boards ready, and reset 48V if needed, max 2x if no board errors after 48V reset
    while (not rsp_ready or not tbb_ready) and restarts > 0:
        if not check_active_rspdriver() or not check_active_tbbdriver():
            logger.warning('RSPDriver and/or TBBDriver not running')
            swlevel(1)
            swlevel(2)
            #time.sleep(30.0)

        rsp_ready = wait_rsp_ready()
        tbb_ready, tbbs_active = wait_tbb_ready(n_tbb_boards)
        if not tbb_ready:
            active_tbbs_changed = False
            for tbb_nr, active in enumerate(tbbs_active):
                if active != db.tbb[tbb_nr].board_active:
                    active_tbbs_changed = True
            if not active_tbbs_changed:
                tbb_ready = True

        if rsp_ready and tbb_ready :
            break

        if not rsp_ready:
            logger.warning('Not all RSP boards ready, reset 48V to recover')
        if not rsp_ready:
            logger.warning('Not all TBB boards ready, reset 48V to recover')
        swlevel(1)
        reset_48_volt()
        restarts -= 1
        time.sleep(10.0)
        level, board_errors = swlevel(2)
        if len(board_errors) > 0:
            db.board_errors = board_errors

    if not rsp_ready:
        logger.warning('RSP not all boards ready')
    if not tbb_ready:
        logger.warning('TBB not all boards ready')
    # put tbbs active information in the db
    for tbb_nr, active in enumerate(tbbs_active):
        if active in (False, None):
            db.tbb[tbb_nr].board_active = 0
        else:
            db.tbb[tbb_nr].board_active = 1
    return rsp_ready, tbb_ready


def mode_to_band(mode):
    bands = {'10_90'  : (1, 3),
             '30_90'  : (2, 4),
             '110_190': (5,),
             '170_210': (6,),
             '210_250': (7,)}
    for band, modes in bands.items():
        if mode in modes:
            return band
    return '0'


# convert select-list to select-string
def select_str(sel_list):
    last_sel = -2
    is_set = False
    select = ""
    for sel in sorted(sel_list):
        if sel == last_sel + 1:
            is_set = True
        else:
            if is_set:
                is_set = False
                select += ':%d' % last_sel
            select += ",%d" % sel
        last_sel = sel
    if is_set:
        select += ':%d' % last_sel
    return select[1:]


# convert select-string to sel_list
def extract_select_str(select_string):
    select_string = select_string.strip()
    if not select_string:
        return []
    select_list = list()
    str_number = ''
    int_number = None
    first_set_number = None
    is_set = False
    #for ch in sel_str:
    select_string_size = len(select_string)
    last_i = select_string_size - 1
    for i in range(select_string_size):
        ch = select_string[i]
        if is_set and ch in '.':
            continue

        if ch.isalnum():
            str_number += ch
            if i < last_i:
                continue

        if str_number:
            int_number = int(str_number.strip())
            str_number = ''

        if int_number and (ch in ',' or i == last_i):
            if is_set:
                for nr in range(first_set_number, int_number+1, 1):
                    select_list.append(nr)
                is_set = False
            else:
                select_list.append(int_number)
            int_number = None

        if ch in ':.':
            first_set_number = int_number
            is_set = True

    return sorted(select_list)


def get_clock():
    answer = rspctl("--clock")
    # print answer[-6:-3]
    clock = float(answer[-7:-4])
    return clock


# function used for antenna testing
def swap_xy(state):
    if state in (0, 1):
        if state == 1:
            logger.debug("XY-output swapped")
        else:
            logger.debug("XY-output normal")
        rspctl('--swapxy=%d' % state)


def reset_rsp_settings():
    if rspctl('--clock').find('200MHz') < 0:
        rspctl('--clock=200')
        logger.debug("Changed Clock to 200MHz")
        if not testmode:
            time.sleep(2.0)
    rspctl('--wg=0', wait=0.0)
    rspctl('--rcuprsg=0', wait=0.0)
    rspctl('--datastream=0', wait=0.0)
    rspctl('--splitter=0', wait=0.0)
    rspctl('--specinv=0', wait=0.0)
    rspctl('--bitmode=16', wait=0.0)
    rspctl('--rcumode=0', wait=0.0)
    rspctl('--rcuenable=0', wait=0.0)
    rspctl('--swapxy=0', wait=0.0)  # 0=normal, 1=swapped
    # rspctl         ('--hbadelays=%s' %(('128,'*16)[:-1]), wait=8.0)


# TODO: change turn_on_rcus and readback rcu status, and return status
# retry if not set.
def turn_on_rcus(mode, rcus):
    retries = 3
    while retries:
        select = select_str(rcus)
        logger.debug("turn RCU's on, mode %d" % mode)
        rspctl('--mode=%d --select=%s' % (mode, select), wait=8.0)
        """
        logger.debug("enable rcus")
        rspctl('--rcuenable=1 --select=%s' % select, wait=0.0)
        logger.debug("setweights")
        rspctl('--aweights=8000,0', wait=0.0)

        if mode == 5:
            rspctl('--specinv=1', wait=0.0)
        else:
            rspctl('--specinv=0', wait=0.0)

        logger.debug("set rcu mode")
        rsp_rcu_mode(mode, rcus)
        """
        # check if rcus are turned on in right mode
        rcu_info = get_rcu_info(rcus)
        valid = True
        for rcu in rcus:
            if rcu_info[str(rcu)]['state'] != 'ON' or rcu_info[str(rcu)]['mode'] != str(mode):
                valid = False
        if valid:
            return 0

        logger.debug("Not all rcus in right mode, retry")
        retries -= 1
    return 1


def turn_off_rcus():
    logger.debug("RCU's off, mode 0")
    rspctl('--mode=0', wait=8.0)
    #rspctl('--rcumode=0', wait=0.0)
    #rspctl('--rcuenable=0', wait=0.0)
    #rspctl('--aweights=0,0', wait=1.0)


# set rcu mode
def rsp_rcu_mode(mode, rcus):
    if mode in range(1, 8, 1):  # all modes
        select = select_str(rcus)
        rspctl('--rcumode=%d --select=%s' % (mode, select), wait=6.0)
        return 0
    return -1


# set hba_delays, and discharge if needed
def rsp_hba_delay(delay, rcus, discharge=True):
    global active_delay_str

    if delay == active_delay_str:
        logger.debug("requested delay already active, skip hbadelay command")
        return 1

    select = select_str(rcus)
    if discharge:
        # count number of elements off in last command
        n_hba_off = 0
        for i in active_delay_str.split(','):
            if int(i, 10) & 0x02:
                n_hba_off += 1

        # count number of elements on in new command, and make discharge string
        n_hba_on = 0
        discharge_str = ''
        if n_hba_off > 0:
            for i in delay.split(','):
                if int(i, 10) & 0x02:
                    discharge_str += "2,"
                else:
                    discharge_str += "0,"
                    n_hba_on += 1

        # discharge if needed
        if n_hba_off > 0 and n_hba_on > 0:
            logger.debug("set hbadelays to 0 for 1 second")
            rspctl('--hbadelay=%s --select=%s' % (discharge_str[:-1], select), wait=8.0)

    logger.debug("send hbadelay command")
    rspctl('--hbadelay=%s --select=%s' % (delay, select), wait=8.0)

    active_delay_str = delay
    return 0


def get_rcu_info(rcus):
    """
    get rcu information, state, mode and swapped
    :return:
    """
    ack = {}
    for rcu in rcus:
        ack[str(rcu)] = {'state': 'OFF', 'mode': '0'}

    # RCU[ 0].control=0x10337a9c =>  ON, mode:3, delay=28, att=06
    answer = rspctl("--rcu")
    if answer.count('mode:') > 0: #== len(rcus):
        for line in answer.splitlines():
            if line.find('mode:') == -1:
                continue
            rcu = line[line.find('[') + 1: line.find(']')].strip()
            if not int(rcu) in rcus:
                continue
            state = line[line.find('=>') + 2: line.find(',')].strip()
            mode = line[line.find('mode:') + 5]
            if rcu.isdigit() and state in ("OFF", "ON") and mode.isdigit():
                ack[rcu]['state'] = state
                ack[rcu]['mode'] = mode
    #logger.debug("rcu-info = %s" % str(ack))
    return ack
