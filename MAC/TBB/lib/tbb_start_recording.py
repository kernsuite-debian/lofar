#!/usr/bin/env python3

########################################################################
#
# Start TBB recording on a bunch of stations
#
########################################################################

import argparse
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import supported_modes, lcurun_command, tbb_command, rsp_command
from lofar.common.lcu_utils import translate_user_station_string_into_station_list, stationname2hostname

def start_tbb(stations, mode, subbands):

    logging.info('Starting TBB recording')

    if mode == 'subband':
        mode += 's'
        # tbbctl and rspctl expect the mode to be 'subbands'.
        rspctl_mode_cmd = [rsp_command, '--tbbmode=%s,%s' % (mode, subbands)]
    else:
        rspctl_mode_cmd = [rsp_command, '--tbbmode=%s' % (mode)]

    cmds = [
        rspctl_mode_cmd,
        [tbb_command, '--mode=%s' % mode],
        [tbb_command, '--free'],
        [tbb_command, '--alloc'],
        [tbb_command, '--record']
    ]

    stations = translate_user_station_string_into_station_list(stations)
    station_hostname_csv_string = ','.join(stationname2hostname(s) for s in stations)

    relay = lcurun_command + [station_hostname_csv_string]

    for cmd in cmds:
        cmd = relay + cmd
        logging.info('Executing %s' % ' '.join(cmd))
        subprocess.check_call(cmd)
        time.sleep(2)

def parse_args():
    parser = argparse.ArgumentParser("This script will start TBB recording on a bunch of stations.")
    parser.add_argument('-s', '--stations', dest='stations',
                        help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)",
                        default=None)
    parser.add_argument('-m', '--mode', dest='mode', help="supported tbb modes: %s" % supported_modes,
                        default='subband')
    parser.add_argument('-b', '--subbands', dest='subbands', help='Subband range, e.g. 10:496', default='10:496')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode not in supported_modes:
        raise ValueError('Mode must be one of %s' % supported_modes)

    start_tbb(args.stations, args.mode, args.subbands)
