#!/usr/bin/env python3

########################################################################
#
# Stop TBB recording on a bunch of stations
#
########################################################################

import argparse
import time
import subprocess
import logging
logger = logging.getLogger(__name__)

from lofar.mac.tbb.tbb_config import lcurun_command, tbb_command
from lofar.mac.tbb.tbb_util import split_stations_by_boardnumber
from lofar.common.lcu_utils import execute_in_parallel_over_stations, translate_user_station_string_into_station_list
from lofar.common.subprocess_utils import wrap_composite_command

def freeze_tbb(stations, dm, timesec, timensec):
    """
    :param stations: comma-separated list of stations
    :param dm: dispersion measure as float
    :param timesec: stop time in seconds (int)
    :param timensec: stop time offset in nanoseconds (int)
    :return:
    """

    stations = translate_user_station_string_into_station_list(stations)

    logger.info('Freezing TBB boards for stations: %s', ', '.join(stations))

    if dm is not None:
        logger.info('DM %s provided, performing timed stop on individual boards' % dm)

        # determine number of tbb boards per station:
        stationlists = split_stations_by_boardnumber(stations)

        # batch handle all stations with same number of boards through lcurun
        for num_boards in list(stationlists.keys()):
            stations_with_num_boards = stationlists[num_boards]
            logger.info('Handling stations with %s boards: %s', num_boards, stations_with_num_boards)
            station_str = ','.join(stationlists[num_boards])
            relay = lcurun_command + [station_str]

            slicenr = int(timensec // (5 * 1024))  # -> 5.12 microseconds per slice

            # string magic to create single cmdline ';' seperated tbbctl commands to set the dispersion measure and the stoptime
            set_dm_cmd = " ; ".join(['%s --dispmeas=%s,%s' % (tbb_command, board, dm) for board in range(num_boards)])
            set_stoptime_cmd = " ; ".join(['%s --stoptimed=%s,%s,%s' % (tbb_command, board, timesec, slicenr) for board in range(num_boards)])

            # apply all commands for each station
            for cmd in [set_dm_cmd, set_stoptime_cmd]:
                quoted_cmd = wrap_composite_command(cmd)
                execute_in_parallel_over_stations(quoted_cmd, stations_with_num_boards, timeout=60, max_parallel=10)

    # Note: Sander says it is still required to tbbctl --stop in subbands mode, although ICD seems to suggest otherwise,
    #       so we will issue that irrespective of mode in the following.
    # Note: This is not even close to nanosecond precision, but this is ridiculous outside the driver/firmware anyway...
    #       If we really have to be better than this, we could port the sleepuntil.sh that is apparently floating around
    #       lcuhead to the stations and chain it into the command, so that we are not delayed by lcurun/ssh.

    # wait for timestamp, then stop all boards on all stations.
    timestamp = float("%d.%09d" % (timesec, timensec))
    if dm is not None:
        timestamp += 0.32 * dm

    sleeptime = timestamp - time.time()
    if sleeptime > 0:
        logger.info('Waiting %s seconds before stopping TBB boards' % sleeptime)
        time.sleep(sleeptime)

    cmd = [tbb_command, '--stop']
    execute_in_parallel_over_stations(cmd, stations, timeout=60, max_parallel=10)

def parse_args():
    parser = argparse.ArgumentParser("This script will freeze TBB boards on a bunch of stations.")
    parser.add_argument('-s', '--stations', dest='stations', help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)", default=None)
    parser.add_argument('-d', '--dm', dest='dm', help="dispersion measure as float", type=float)
    parser.add_argument('-t', '--stoptime-seconds', dest='timesec', type=int, help="Freeze time since epoch in seconds")
    parser.add_argument('-n', '--stoptime-nanoseconds', dest='timensec', type=int, help="Freeze time offset in nanoseconds", default=0)
    args = parser.parse_args()

    if not args.timesec:
        logger.info('No timestamp provided, using current time instead.')
        stoptime = time.time()
        timesec_str, timensec_str = ("%.9f" % stoptime).split('.')
        args.timesec = int(timesec_str)
        args.timensec = int(timensec_str)

    if args.dm is None:
        logger.error("No dm provided")
        parser.print_help()
        exit(1)

    return args


def main():
    args = parse_args()
    freeze_tbb(args.stations, args.dm, args.timesec, args.timensec)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
