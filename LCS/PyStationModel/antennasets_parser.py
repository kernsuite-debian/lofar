#!/usr/bin/env python3

# antennasets_parser.py
#
# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import re
import os

DEFAULT_ANTENNASETS_CONF_FILEPATH = os.path.expandvars("$LOFARROOT/etc/AntennaSets.conf")

class AntennaSetsParser(object):
    """ Parses an antenna sets configuration file and makes it available in various forms """

    def __init__(self, conf_filepath=DEFAULT_ANTENNASETS_CONF_FILEPATH):
        if not self.__file_exists(conf_filepath):
            raise Exception("Configuration file doesn't exist")

        self.antenna_sets = self.__parse_from_file(conf_filepath)

    def __file_exists(self, filepath):
        return os.path.isfile(filepath)

    def __parse_from_file(self, conf_filepath):
        """ Reads in an antennasets configuration file and converts it into a dictionary
        :param: conf_filepath: Path to the antennasets configuration file
        :return: a dictionary of the antennasets in the form:
            { <antennaset_macro_name> : { <location> : {
                                            "antenna_field" : <antenna_field>,
                                            "receiver_units" : <receiver_units>
            } } }

            For example:
            { "LBA_INNER" : {   "Europe" : {
                                            "antenna_field" : "LBA",
                                            "receiver_units" : "192h" },
                                "Remote" : {
                                            "antenna_field" : "LBA"
                                            "receiver_units" : "46hh2.." },
                                "Core" : {
                                            "antenna_field" : "LBA",
                                            "receiver_units" : 46hh2.. }
                            }
            }
        """
        lines = self.__get_lines_from_file_stripped(conf_filepath)
        lines = self.__remove_comments_and_empty_lines(lines)
        antenna_sets = self.__create_antennasets_dict_from_lines(lines)
        return antenna_sets

    def __get_lines_from_file_stripped(self, filepath):
        with open(filepath, mode='rU') as fd:
            lines = [line.strip() for line in fd.readlines()]
        return lines

    def __remove_comments_and_empty_lines(self, lines):
        return [line for line in lines if len(line) > 0 and line[0] != '#']

    def __create_antennasets_dict_from_lines(self, lines):
        antenna_sets_dict = {}
        for line in lines:
            antenna_set = self.__parse_single_antennaset_line(line)
            self.__store_antennaset(antenna_set, antenna_sets_dict)
        return antenna_sets_dict

    def __parse_single_antennaset_line(self, line):
        parsed_line = tuple(line.split())
        if len(parsed_line) != 4:
            raise Exception("Expected 4 text columns in line: %s" % line)
        return parsed_line

    def __store_antennaset(self, antennaset, antennasets_dict):
        macro_name, antenna_field, location, encoded_receiver_units = antennaset
        antennasets_dict.setdefault(macro_name, {})[location] = {
            "antenna_field": antenna_field,
            "receiver_units": encoded_receiver_units
        }

    def get_antennaset_configuration(self):
        """ Get the raw antenna set configurations with antenna field names and rcu encoding as they appear in the
        configuration file.

        Each receiver unit (RCU) has three inputs (HBA, LBL, and LBH), of which at most one can be selected at a time.
        Each station has an array of N RCUs (RCU_0 - RCU_N), where N is defined by the station type (Europe, Remote, or
        Core). For each combination of antenna set and station type the configuration if this RCU input selection array
        is encoded as [repetitions][input selection pattern], where:
        - repetitions               The amount of times to repeat the defined input selection pattern. This is a numeric
                                    value.
        - input selection pattern   The input selection pattern to apply. This can be one of:
                                    H : HBA input
                                    h : LBH input
                                    l : LBL input
                                    . : RCU not included

        Multiple such encodings can be grouped together (concatenated without spaces) to encode a whole RCU array. An
        example encoding would be '8lh', which translates to RCU_0 to RCU_15 with an alternating input selection:
        RCU_0 = l, RCU_1 = h, RCU_2 = l, RCU_3 = h, ..., RCU_14 = l, RCU_15 = h

        Note: the input selection pattern is often a string of sub-patterns of size 2 (e.g. 'hh' and '..' in '46hh2..',
        and 'lh' and 'l.' in '46lh2l.'). This is due to the fact that one antenna is made up of two dipoles, each of
        which is selected through an individual RCU. Hence RCUs {0,1}, {2,3}, {4,5} etc. form dipole couples (=antennas)

        :return raw antenna sets as they appeared in the configuration file
        """
        return self.antenna_sets

    def get_receiver_units_configuration_per_station(self, antenna_set_name, station_list):
        """ Get the RCU input selection for the given antenna set on a per station basis. The possible RCU inputs are:
        "LBH", "LBL", "HBA", and None (if an RCU is not selected at all).

        :param antenna_set_name: name of the antenna set (e.g.  LBA_INNER, LBA_SPARSE_EVEN, ...)
        :param station_list: list of station names (RSxxx, CSxxx, etc.)
        :return: a dict with station names as keys and the RCU setting for that station, or None if the antenna set name
        is not known. E.g. for LBA_INNER:
            {
                            # RCU0  RCU1   ... RCU189 RCU190 RCU191
                "DExxx":    ["LBH", "LBH", ... "LBH", "LBH", "LBH"],
                "RSxxx":    ["LBH", "LBH", ... "LBH", None,  None],
                "CSxxx":    ["LBH", "LBH", ... "LBH", None,  None]
            }
        """
        station_rcu_mapping = {}
        receiver_units = self.get_receiver_units_configuration(antenna_set_name)
        station_type_lookup = {"RS": "Remote", "CS": "Core"}
        for station_name in station_list:
            station_type = station_type_lookup.get(station_name[:2], "Europe")
            station_rcu_mapping[station_name] = receiver_units.get(station_type, None)
        return station_rcu_mapping

    def get_receiver_units_configuration(self, antenna_set_name):
        """ Get the RCU input selection for the given antenna set per station type. The possible RCU inputs are: "LBH",
        "LBL", "HBA", and None (if an RCU is not selected at all).

        :param antenna_set_name: name of the antenna set (e.g.  LBA_INNER, LBA_SPARSE_EVEN, ...)
        :return: a dict containing the RCU setting for the different types of stations, or None if the antenna set name
        is not known. E.g. for LBA_INNER:
            {
                                    # RCU0  RCU1   ... RCU189 RCU190 RCU191
                "International":    ["LBH", "LBH", ... "LBH", "LBH", "LBH"],
                "Remote":           ["LBH", "LBH", ... "LBH", None,  None],
                "Core":             ["LBH", "LBH", ... "LBH", None,  None]
            }
        """
        rcu_config = {}
        antenna_set = self.antenna_sets.get(antenna_set_name, None)
        if antenna_set is not None:
            for station_type in antenna_set.keys():
                rcus_encoded = antenna_set[station_type].get('receiver_units', None)
                if rcus_encoded is not None:
                    rcus_decoded = self.decode_rcu_selection(rcus_encoded)
                    rcu_config[station_type] = rcus_decoded
        return rcu_config

    @staticmethod
    def decode_rcu_selection(encoded_rcu_selection):
        receiver_units_array = []
        _encoded_receiver_units = re.findall('([0-9]+[Hhl.]+)', encoded_rcu_selection)
        for encoding in _encoded_receiver_units:
            n_repetitions = int(re.match('([0-9]+)', encoding).group(0))
            rcu_input_pattern = re.search('([Hhl.]+)', encoding).group(0)
            if n_repetitions is not None and rcu_input_pattern is not None:
                legend = {
                    'H': "HBA",
                    'h': "LBH",
                    'l': "LBL",
                    '.': None
                }
                receiver_units_array += n_repetitions * [legend.get(rcu_input, None) for rcu_input in rcu_input_pattern]
        return receiver_units_array

if __name__ == "__main__":
    from pprint import pprint
    with AntennaSetsParser() as parser:
        antennasets_dict = parser.__parse_from_file()
    pprint(repr(antennasets_dict).strip())
