#!/usr/bin/env python3

import sys
import argparse
import time
import datetime
import re
import numpy

import matplotlib
# On Mac OSX set this to whatever.  :-)
matplotlib.use("qt4agg")

import pylab
# Set some sane defaults for pylab/matplotlib.
pylab.rcParams["axes.formatter.limits"] = -18, 18
pylab.rcParams["figure.autolayout"] = True
#pylab.rcParams["figure.dpi"] = 300
pylab.rcParams["image.interpolation"] = "bicubic"
pylab.rcParams["pdf.fonttype"] = 42
pylab.rcParams["pdf.use14corefonts"] = False
pylab.rcParams["ps.fonttype"] = 42
pylab.rcParams["ps.papersize"] = "a4"
pylab.rcParams["ps.useafm"] = False
pylab.rcParams["ps.usedistiller"] = False
pylab.rcParams["savefig.dpi"] = 600
pylab.rcParams["savefig.orientation"] = "landscape"
pylab.rcParams["text.usetex"] = True
pylab.rcParams["timezone"] = "UTC"

import matplotlib.pyplot


def _setup_command_line_arguments():
    """
    Setup the command line argument parser and return it.
    :return: the parser for the command line arguments
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description = "")
    parser.add_argument(
        "cobalt_log_file", help = "The Cobalt log file which contains the flagging information.")
    parser.add_argument(
        "--station_list", help = "Run the tool at least once.  Then choose from the station list - which is printed during the execution of the script - the ones you want to be in the plot.", nargs = "+")
    parser.add_argument(
        "--ignore_zero_values", help = "Ignore data points when stations logged a 0.0%% value for flagged data.", action = "store_true")
    return parser


def read_file(input_file):
    '''
    Open and read a file in. 
    :param input_file:  The file that will be read and then split into lines.
    :return:  The file neatly split up into a list of lines. 
    '''
    with open(input_file, "r") as file_stream:
        file_lines = file_stream.read().splitlines()
    return file_lines


def build_regexp_format():
    '''
    Create a regular expression that triggers on Cobalt log lines which contain
    flagging information.
    The relevant log lines look like this:
    rtcp:07@cbt004 2018-10-09 13:30:06.676 WARN  RTCP.Cobalt.GPUProc - [block 57] Flagging:    CS004LBA: 0.0%, CS006LBA: 0.0%, CS021LBA: 0.0%, CS030LBA: 0.0%, CS501LBA: 0.5%,  [Pipeline.cc:449]
    :return: A regular expression strnig that allows to filter out non-matching
    log lines.
    '''
    # Time stamp = YYYY-MM-DD HH:mm:SS.mmm
    time_stamp_regex = "\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.\d{3}"
    # block # = n 
    block_regex = "\d+"
    # Staion flagging = CS004LBA: 0.0%, CS006LBA: 0.0%,
    stations_flagging_regex = "\w+:\s+\d+\.\d+%,\s*"
    format = r"^.*" \
        "(?P<time_stamp>{time_stamp_regex})" \
        "\s+WARN\s+.*\[block\s+" \
        "(?P<block>{block_regex})" \
        "\]\s+Flagging:\s+" \
        "(?P<stations_flagging>(?:{stations_flagging_regex})+)".format(
            time_stamp_regex=time_stamp_regex,
            block_regex=block_regex,
            stations_flagging_regex=stations_flagging_regex)
    return format


def split_log_line(regexp_format, log_line):
    """
    Identify and split Cobalt log lines that contain flagging information.  Then
    gather that information in a dict that has this structure:
        {'time_stamp': datetime.datetime(2018, 10, 9, 13, 29, 9, 590000), 'block': 0, 'stations_flagging': [{'CS004LBA': 0.0}, {'CS006LBA': 0.0}]}
    :param match:  A regexp match the matches the time stamp, the block number and the stations with their flagging percentage value.
    :param log_line: A Cobalt log line.  Example:
        rtcp:07@cbt004 2018-10-09 13:30:06.676 WARN  RTCP.Cobalt.GPUProc - [block 57] Flagging:    CS004LBA: 0.0%, CS006LBA: 0.0%, CS021LBA: 0.0%, CS030LBA: 0.0%, CS501LBA: 0.5%,  [Pipeline.cc:449]
    :return: a dict of dicts that contain the time stamp and the  
     the end_date, the rcu_mode, and the beam_switch_delay.
    :rtype: dict
    """
    match = re.match(regexp_format, log_line)

    stations_flagging = dict()
    if match is not None:
        stations_flagging = match.groupdict()
        # Massage the content in the dict returned by match a bit.
        stations_flagging_string = stations_flagging["stations_flagging"]
        # I need to extract the name of each of the stations.
        stations_flagging_list = stations_flagging_string.rstrip().rstrip("%,").split("%, ")
        beautified_stations_flagging_list = list()
        for station in stations_flagging_list:
            # Split the station name off from its flagging value.
            station_name, flagging = station.split(": ")
            # Store both.
            beautified_stations_flagging_list.append(
                {station_name: float(flagging)})
        # Keep everything nice and tidy.  Store the data in a new dict.
        stations_flagging["stations_flagging"] = beautified_stations_flagging_list
        stations_flagging["block"] = int(stations_flagging["block"])
        stations_flagging["time_stamp"] = datetime.datetime.strptime(
            stations_flagging["time_stamp"], "%Y-%m-%d %H:%M:%S.%f")

    return dict(stations_flagging)


def identify_cobalt_flagging_lines(log_lines):
    '''
    Apply a regexp to the Cobalt log lines and filter out the lines that do not
    contain flagging information.  The return the remaining log lines for
    further processing.
    :param log_lines:  The log lines of the Cobalt log file in a list.
    :return: A list of Cobalt log lines that contains only flagging information.
    '''
    regexp_format = build_regexp_format()
    flagging_lines = list()
    for log_line in log_lines:
        flagging_line = split_log_line(regexp_format, log_line)
        if flagging_line is not None and isinstance(flagging_line, dict) and len(flagging_line) > 0:
            flagging_lines.append(flagging_line)
    return flagging_lines


def reorder_flagging_information(flagging_dict, ignore_zero_values):
    '''
    Reshuffle the data into some numpy arrays that are compatible with matplot.
    :param flagging_dict:  a dict that contains the flagging data.  Example:
        {'time_stamp': datetime.datetime(2018, 10, 9, 13, 29, 9, 590000), 'block': 0, 'stations_flagging': [{'CS004LBA': 0.0}, {'CS006LBA': 0.0}]}
    :return: dict[station name]
                ["time_stamps"]:  time stamps when data was given
                ["block"]:  block #
                ["flagging_percentage"]:  percentage of flagged data
    '''
    time_stamps = list()
    blocks = list()
    stations = list()
    station_flagging_dict = dict()

    for item in flagging_dict:
        stations_flagging = item["stations_flagging"]
        time_stamp = item["time_stamp"]
        block = item["block"]

        for single_station in stations_flagging:
            (station, flagging_percentage) = single_station.popitem()
            if flagging_percentage > 0.0 or ignore_zero_values is False:
                if station in station_flagging_dict:
                    station_flagging_dict[station]["time_stamps"].append(time_stamp)
                    station_flagging_dict[station]["blocks"].append(block)
                    station_flagging_dict[station]["flagging_percentage"].append(flagging_percentage)
                else:
                    station_flagging_dict[station] = dict()
                    station_flagging_dict[station]["time_stamps"] = list()
                    station_flagging_dict[station]["time_stamps"].append(time_stamp)
                    station_flagging_dict[station]["blocks"] = list()
                    station_flagging_dict[station]["blocks"].append(block)
                    station_flagging_dict[station]["flagging_percentage"] = list()
                    station_flagging_dict[station]["flagging_percentage"].append(flagging_percentage)
    return station_flagging_dict


def closeEvent(event):
    '''
    When the close window button is clicked this function gets called.  It
    simply exits.
    '''
    sys.exit(0)


def keyPressEvent(event):
    '''
    Handle key-press events.
    Save the plot to disk if "S" or "s" is pressed.
    Leave the plotting hell if ESC, "Q" or "q" is pressed.
    '''
    if event.key == "escape" or event.key.lower() == "q":
        sys.exit(0)
    elif event.key.lower() == "s":
        # Save the current plot.
        fileName = time.strftime("%Y-%m-%dT%H.%M.%S-Cobalt_data_flagging.png", time.gmtime())
        matplotlib.pyplot.savefig(fileName, dpi = 600, orientation = "landscape", papertype = "a4", format = "png")



def main():
    cla_parser = _setup_command_line_arguments()
    arguments = cla_parser.parse_args()
    print(("Reading the Cobalt log file \"%s\"..." % (arguments.cobalt_log_file)))
    cobalt_log_lines = read_file(arguments.cobalt_log_file)
    print("Identifying the flagging log lines...")
    cobalt_flags = identify_cobalt_flagging_lines(cobalt_log_lines)
    # Convert the data to numpy arrays for plotting.
    print("Preparing the data for plotting...")
    stations_dict = reorder_flagging_information(cobalt_flags, arguments.ignore_zero_values)

    station_list = list(stations_dict.keys())
    print(("\nThe following stations flagged data:\n%s\n" % (" ".join(station_list))))

    # Set-up of the matplotlib stuff.
    print("Set up the matplotlib canvas...")
    figure, axes = matplotlib.pyplot.subplots()
    # Erase everything.
    axes.cla()
    # Set up the x-axis to display time and date.
#    axes.xaxis.set_major_locator(matplotlib.dates.MinuteLocator())
    axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
#    axes.xaxis.set_minor_locator(matplotlib.dates.SecondLocator())
    axes.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%H:%M:%S'))
    axes.fmt_xdata = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    figure.autofmt_xdate()
    # Display a grid.
    matplotlib.pyplot.grid(True)
    # Set the plot title.
    matplotlib.pyplot.title("Cobalt station flagging")
    # Label the axes.
    matplotlib.pyplot.xlabel("Time (YYYY-MM-DD HH:MM:SS)")
    matplotlib.pyplot.ylabel("Flagged data (\%)")

    plots = list()
    print("Plot everything...")
    if arguments.station_list is not None:
        station_list = arguments.station_list
        print(("The following stations will be plotted:\n%s\n" % (arguments.station_list)))
    for station in station_list:
        station_flagging = stations_dict[station]
        print(("Adding station %s to the plot..." % (station)))
        plots.append(axes.plot(station_flagging["time_stamps"], station_flagging["flagging_percentage"], marker = "+", label = station, alpha = 0.2))
    # Update the figure and add a legend,
    matplotlib.pyplot.legend()
    figure.canvas.draw()

    # Create an event handler for the close_event.
    figure.canvas.mpl_connect("close_event", closeEvent)

    # Create an event handler for the key_press_event.
    figure.canvas.mpl_connect("key_press_event", keyPressEvent)

    # Start everything.  This call blocks until the window close button is clicked.
    matplotlib.pyplot.show()
    # That's it.  Thanks and goodbye!
    matplotlib.pyplot.close(figure)
    print("Goodbye!")


if __name__ == "__main__":
    main()
