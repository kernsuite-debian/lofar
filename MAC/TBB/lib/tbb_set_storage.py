#!/usr/bin/env python3

#######################################################################################
#
# Set storage nodes where the TBB boards will send their data to on a bunch of stations
#
#######################################################################################

import argparse
import time
import subprocess
import logging
from lofar.mac.tbb.tbb_config import lcurun_command, tbb_command
from lofar.common.lcu_utils import translate_user_station_string_into_station_list, stationname2hostname

def set_tbb_storage(map):
    logging.info('Setting TBB storage nodes')

    for stations, node in map.items():
        stations = translate_user_station_string_into_station_list(stations)
        station_hostname_csv_string = ','.join(stationname2hostname(s) for s in stations)
        relay = lcurun_command + [station_hostname_csv_string]

        cmds = [
            [tbb_command, '--storage=%s' % node],
            [tbb_command, '--udp']
        ]

        for cmd in cmds:
            cmd = relay + cmd
            logging.info('Executing %s' % ' '.join(cmd))
            subprocess.check_call(cmd)


def parse_mapping(mapping_str):
    """
    :param mapping_str: comma-separated list of single station to single storage node assignments, e.g. station1=node1,station2=node2
    :return: dict mapping stations on nodes, e.g. {station1: node1, station2: node2}
    """
    map = {}
    items = mapping_str.split(',')
    for item in items:
        subitems = item.split('=')
        if len(subitems) != 2 or "" in subitems:
            raise ValueError('Malformed item "%s"' % item)
        else:
            station, node = subitems
            map[station] = node

    return map

def create_mapping(stations, nodes):
    """
    Map m stations to n nodes. If m>n, some nodes remain unassigned, if n>m, some nodes get assigned multiple times.
    :param stations: list of station LCUs
    :param nodes: list of nodes
    :return: dict mapping stations to nodes, e.g. {station1: node1, station2: node2}
    """
    stations = translate_user_station_string_into_station_list(stations)

    # zip truncates to shortest list, so make sure there are enough nodes, then map each station to a node
    logging.info("Mapping stations %s on %s nodes " % (stations, nodes))
    nodes *= (len(stations) // len(nodes) + 1)
    map = dict(list(zip(stations, nodes)))
    logging.debug('Stations were mapped to nodes as follows: %s' % map)
    return map


def parse_args():
    parser = argparse.ArgumentParser("This script will set the target node for TBB data on a bunch of stations.")
    parser.add_argument('-s', '--stations', dest='stations',
                        help="comma-separated list of station LCUs (e.g. cs030c,cs031c; also accepts lcurun aliases like 'today', 'nl', ...)",
                        default=None)
    node_group = parser.add_mutually_exclusive_group(required=True)
    node_group.add_argument('-n', '--nodes', dest='nodes',
                            help="comma-separated list of target nodes to receive tbb data, stations will mapped automatically, use option -m instead to be specific")
    node_group.add_argument('-m', '--mapping', dest='mapping',
                            help="comma-separated list of single station to single storage node assignments, e.g. station1=node1,station2=node2")
    args = parser.parse_args()

    # we cannot have a shared item in two mutually exclusive groups
    if args.mapping and args.stations:
        raise ValueError('Options -s and -m are mutually exclusive')
    if not args.stations:
        args.stations = 'today'

    if args.mapping:
        args.map = parse_mapping(args.mapping)
    else:
        nodes = args.nodes.split(',')
        args.map = create_mapping(args.stations, nodes)

    return args

def main():
    args = parse_args()
    set_tbb_storage(args.map)

