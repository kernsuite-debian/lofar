#!/usr/bin/env python3

########################################################################
#
# Release TBB recording on a bunch of stations
#
########################################################################

import argparse
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import lcurun_command, tbb_command
from lofar.common.lcu_utils import translate_user_station_string_into_station_list, stationname2hostname

def release_tbb(stations):
    logging.info('Releasing TBB recording')

    stations = translate_user_station_string_into_station_list(stations)
    station_hostname_csv_string = ','.join(stationname2hostname(s) for s in stations)
    relay = lcurun_command + [station_hostname_csv_string]

    cmd = relay + [tbb_command, '--free']
    logging.info('Executing %s' % ' '.join(cmd))
    subprocess.check_call(cmd)


def parse_args():
    parser = argparse.ArgumentParser("This script will release TBB recording on a bunch of stations.")
    parser.add_argument('-s', '--stations', dest='stations',
                        help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)",
                        default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    release_tbb(args.stations)

