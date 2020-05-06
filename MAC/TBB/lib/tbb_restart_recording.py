#!/usr/bin/env python3

########################################################################
#
# Restart TBB recording on a bunch of stations
#
########################################################################

import argparse
import logging
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import supported_modes, lcurun_command, tbb_command
from lofar.common.lcu_utils import translate_user_station_string_into_station_list, stationname2hostname


def restart_tbb_recording(stations):
    stations = translate_user_station_string_into_station_list(stations)
    station_hostname_csv_string = ','.join(stationname2hostname(s) for s in stations)

    logging.info("Restarting TBB recording on stations %s", stations)

    relay = lcurun_command + [station_hostname_csv_string]
    cmd = relay + [tbb_command, "--record"]
    logging.info("Executing %s" % " ".join(cmd))
    subprocess.check_call(cmd)
    time.sleep(2)

def parse_args():
    parser = argparse.ArgumentParser("This script will restart TBB recording on a bunch of stations.")
    parser.add_argument("-s", "--stations", dest="stations", help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    restart_tbb_recording(args.stations)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main()