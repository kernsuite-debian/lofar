#!/usr/bin/env python3

########################################################################
#
# Load a TBB firmware on a bunch of stations and the respective boards there
#
########################################################################

import argparse
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import supported_modes, lcurun_command, tbb_command
from lofar.common.lcu_utils import translate_user_station_string_into_station_list,stationname2hostname
from lofar.common.subprocess_utils import check_output_returning_strings

def load_tbb_firmware(stations, mode):
    logging.info('Loading TBB firmware for mode \"%s\"' % (mode))

    # This is hardcoded for now.  There is no reliable way to tell from the output
    # of tbbctl --imageinfo what a firmware can do.  Everything there is a string that
    # gets passed by the --writeimage command.  So even the image name can be wrong or
    # misleading.
    # So:  the ALERT firmware must be in slot #2!
    if mode == "subband":
        slot = 2
    else:
        slot = 1

    stations = translate_user_station_string_into_station_list(stations)
    station_hostname_csv_string = ','.join(stationname2hostname(s) for s in stations)

    logging.info("It is assumed that the firmware for mode \"%s\" is in slot %d!" % (mode, slot))

    relay = lcurun_command + [station_hostname_csv_string]
    cmd = [tbb_command, '--config=%s' % slot]
    cmd = relay + cmd
    logging.info('Executing %s' % ' '.join(cmd))
    subprocess.check_call(cmd)

    # Wait for 60s.  The TBBs will reset when a new firmware gets loaded
    # and that takes some time.
    wait_time = 60
    interval = 10
    for sleep_time in range(wait_time, 0, -interval):
        logging.info("Waited %ds of %ds for the TBB boards to load the firmware for mode \"%s\"..." % (wait_time - sleep_time, wait_time, mode))
        time.sleep(interval)
    logging.info("TBBs should now have the firmware for mode \"%s\" loaded.  Check the output of the following command!" % (mode))

    for board in range(6):
        cmd = [tbb_command, '--imageinfo=%s' % str(board)]
        cmd = relay + cmd
        logging.info('Executing %s' % ' '.join(cmd))
        logging.info(check_output_returning_strings(cmd))


def parse_args():
    parser = argparse.ArgumentParser(
        "This script will load a TBB firmware on a bunch of stations and the respective boards there.")
    parser.add_argument('-s', '--stations', dest='stations',
                        help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)",
                        default=None)
    parser.add_argument('-m', '--mode', dest='mode', help="supported tbb modes: %s" % supported_modes,
                        default='subband')
    args = parser.parse_args()

    if args.mode not in supported_modes:
        raise ValueError('Mode must be one of %s' % supported_modes)
    return args

def main():
    args = parse_args()
    load_tbb_firmware(args.stations, args.mode)
