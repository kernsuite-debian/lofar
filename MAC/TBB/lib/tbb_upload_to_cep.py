#!/usr/bin/env python3

#######################################################################################
#
# Upload the TBB data to CEP on a bunch of stations
#
#######################################################################################

import argparse
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import *
from lofar.mac.tbb.tbb_util import split_stations_by_boardnumber, expand_list, calculate_adjusted_start_time, wrap_remote_composite_command
from lofar.common.lcu_utils import execute_in_parallel_over_stations
from lofar.common.lcu_utils import translate_user_station_string_into_station_list

def upload_tbb_data(stations, dm, start_time, duration, sub_bands, wait_time, boards):
    """
    Set-up and execute tbbctl READBAND commands that will command TBBs in ALERT mode to upload part of their memory to CEP.
    :param stations:  Only TBBs of these stations will upload their data to CEP.
    :param dm:  The dispersion measure that was set during data recording.
    :param start_time:  Designates the start of the recorded data in the TBB memory which will be uploaded to CEP.  Earlier data in TBB memory will not be uploaded.
    :param duration:  The time span for which the data will be uploaded in seconds.
    :param sub_bands:  The list of sub-bands that will be uploaded.
    :param wait_time:  The time that has to be waited before another sub-band upload can be commanded.
    :param boards:  Only these boards will be commanded to upload the spectral data to CEP.
    """
    logging.info("Uploadind TBB data...")

    stations = translate_user_station_string_into_station_list(stations)

    # determine number of tbb boards per station:
    stationlists = split_stations_by_boardnumber(stations)

    tbb_cmd = tbb_command + " --readband=${board},${channel},%s,%s,%s,%s"
    # I have to wait until a sub-band has been uploaded.  But I can
    # upload multiple boards/channels in parallel.  Hence this can
    # parallelised down to the sub-bands.
    for sub_band in sub_bands:
        (adjusted_start_time, slice_nr) = calculate_adjusted_start_time(dm, start_time, int(sub_band))

        # batch handle all stations with same number of boards through lcurun
        for num_boards in list(stationlists.keys()):
            logging.debug("Creating TBB commands for stations with %s boards..." % num_boards)
            #relay = lcurun_command + [",".join(stationlists[num_boards])]
            stations_with_num_boards = stationlists[num_boards]

            # iterate over tbb boards
            board_list = []
            for board in boards:
                if int(board) <= num_boards:
                    board_list.append(board)
                else:
                    logging.error("Stations \"%s\" do not have a board #%s!  The stations have only %s boards.  Continuing without this board." % (stationlists[num_boards], board, num_boards))
                    continue

            cmd_list = []
            for channel in range(15):
                for board in board_list:
                    tbb_cmd = "tbbctl --readband=%s,%s,%s,%s,%s,%s" % (board, channel, sub_band, adjusted_start_time, slice_nr, duration*1000) # milliseconds
                    cmd_list.append(tbb_cmd)
                cmd_list.append("sleep %s" % (wait_time,))

            full_cmd = '\"%s\"' % (' ; '.join(cmd_list),)

            execute_in_parallel_over_stations(full_cmd, stations_with_num_boards,
                                              timeout=24*60*60) # tbb dumps can take a long time.... timeout of 24 hours is ok
        time.sleep(wait_time)
    logging.info("Uploading TBB data done.")


def parse_args():
    parser = argparse.ArgumentParser("This script will upload TBB data from a bunch of stations to CEP.")
    parser.add_argument("-s", "--stations", required=True, dest="stations",
                        help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like \"today\", \"nl\", ...)",
                        default=None)
    parser.add_argument('-d', '--dm', required=True, type=float, dest='dm', help="dispersion measure as float")
    parser.add_argument("-t", "--start_time", required=True, type=float, dest="start_time",
                        help="The start time of the data dump in fractional seconds since 1970-01-01T00.00.00.")
    parser.add_argument("-b", "--boards", required=True, dest="boards",
                        help="A list of boards or ranges of boards that will upload their data.  A range can be specified with \"-\" between the first and the last sub-band of the range, list items are separated with \",\".  Example:  --boards=0,2-3,5")
    parser.add_argument("-u", "--subbands", required=True, dest="sub_bands",
                        help="A list of sub-bands or ranges of sub-bands.  A range can be specified with \"-\" between the first and the last sub-band of the range, list items are separated with \",\".  Example:  --subbands=17-22,38,211-319,321,323")
    parser.add_argument("-p", "--duration", required=True, type=float, dest="duration",
                        help="Duration of data dump (upload) in seconds.")
    parser.add_argument("-w", "--wait_time", type=float, dest="wait_time_between_sub_bands",
                        help="Time in seconds that will be waited between uploading a sub-band.  The default is:  t = duration * 0.00012")
    args = parser.parse_args()

    args.boards = expand_list(args.boards)
    args.sub_bands = expand_list(args.sub_bands)

    if args.wait_time_between_sub_bands is not None and args.wait_time_between_sub_bands > 0.0:
        args.wait_time = float(args.wait_time_between_sub_bands)
    else:
        args.wait_time = args.duration * 0.00012

    return args


def main():

    args = parse_args()
    logging.info("Will upload data from these boards:  %s" % (args.boards))
    logging.info("Dispersion measure is %f." % (args.dm))
    logging.info("The start time is %fs." % (args.start_time))
    logging.info("Will upload these sub-bands:  %s" % (args.sub_bands))
    logging.info("Will wait %fs between uploads of sub-bands." % (args.wait_time))

    upload_tbb_data(args.stations, args.dm, args.start_time, args.duration, args.sub_bands, args.wait_time, args.boards)
