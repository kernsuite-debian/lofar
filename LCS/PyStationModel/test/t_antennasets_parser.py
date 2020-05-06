#!/usr/bin/env python3
import os
import unittest
from lofar.stationmodel.antennasets_parser import AntennaSetsParser

class TestAntennaSetsParser(unittest.TestCase):
    def setUp(self):
        self.working_dir = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))
        self.test_filepath = os.path.join(self.working_dir, "datasets",
                                          "t_antennasets_parser.antennaset_conf_test_sample")

    def test_default_config_path(self):
        """ Verify that an exception is raised by the AntennaSetsParser constructor if the configuration file doesn't 
        exist. """
        self.assertRaises(Exception, AntennaSetsParser, None)

    def test_bad_config_file_five_columns(self):
        """ Verify that an exception is raised by the AntennaSetsParser constructor when parsing a configuration file
        with a number of columns not equaling four. """
        test_filepath = os.path.join(self.working_dir, "datasets",
                                          "t_antennasets_parser.bad_antennaset_conf_test_sample_five_columns")
        self.assertRaises(Exception, AntennaSetsParser, test_filepath)

    def test_antennaset_names(self):
        """ Verify if the parsed antennaset names equal those in our sample configuration file """
        uut = AntennaSetsParser(self.test_filepath)
        antennaset_dict = uut.get_antennaset_configuration()

        expected_antenna_sets = ['LBA_INNER', 'LBA_OUTER', 'LBA_SPARSE_EVEN', 'LBA_SPARSE_ODD', 'LBA_X', 'LBA_Y',
                                 'HBA_ZERO', 'HBA_ONE', 'HBA_DUAL', 'HBA_JOINED', 'HBA_ZERO_INNER', 'HBA_ONE_INNER',
                                 'HBA_DUAL_INNER', 'HBA_JOINED_INNER']
        self.assertEqual(sorted(expected_antenna_sets), sorted(antennaset_dict.keys()))

    def test_antennaset_locations(self):
        """ Verify if the parsed antennaset locations equal those in our sample configuration file """

        uut = AntennaSetsParser(self.test_filepath)
        antennaset_dict = uut.get_antennaset_configuration()
        locations = []
        for macro in antennaset_dict.keys():
            locations += list(antennaset_dict[macro].keys())
        locations = list(set(locations))

        expected_locations = ['Europe', 'Remote', 'Core']
        self.assertEqual(sorted(expected_locations), sorted(locations))

    def test_antennaset_rcu_selection_LBA_INNER(self):
        """ Verify if the parsed antennaset contains the RCU selections for LBA_INNER equal to those in our sample
        configuration file
        """

        expected_rcu_config_int = "192h"
        expected_rcu_config_remote = "46hh2.."
        expected_rcu_config_core = "46hh2.."

        uut = AntennaSetsParser(self.test_filepath)
        antennaset_dict = uut.get_antennaset_configuration()
        rcu_config_int = antennaset_dict['LBA_INNER']['Europe']['receiver_units']
        rcu_config_remote = antennaset_dict['LBA_INNER']['Remote']['receiver_units']
        rcu_config_core = antennaset_dict['LBA_INNER']['Core']['receiver_units']

        self.assertEqual(rcu_config_int, expected_rcu_config_int)
        self.assertEqual(rcu_config_remote, expected_rcu_config_remote)
        self.assertEqual(rcu_config_core, expected_rcu_config_core)

    def test_receiver_unit_decoder_LBA_INNER_core_station(self):
        """ Verify that encoded RCU selections for LBA_INNER are properly decoded """
        encoded_rcu_config = "46hh2.."
        expected_decoded_rcu_config = 92*["LBH"] + 4*[None]

        decoded_rcu_config = AntennaSetsParser.decode_rcu_selection(encoded_rcu_config)

        self.assertEqual(expected_decoded_rcu_config, decoded_rcu_config)

    def test_receiver_unit_decoder_LBA_SPARSE_ODD_core_station(self):
        """ Verify that encoded RCU selections for LBA_SPARSE_ODD are properly decoded """
        encoded_rcu_config = "23llhh1ll.."
        expected_decoded_rcu_config = 23*(2*["LBL"]+2*["LBH"]) + (2*["LBL"] + 2*[None])

        decoded_rcu_config = AntennaSetsParser.decode_rcu_selection(encoded_rcu_config)

        self.assertEqual(expected_decoded_rcu_config, decoded_rcu_config)

    def test_receiver_units_configuration_LBA_INNER(self):
        """ Verify if the RCUs decoding for LBA_INNER is successful """
        expected_rcu_config = {
            "Europe": 192*["LBH"],
            "Remote": 92*["LBH"] + 4*[None],
            "Core": 92*["LBH"] + 4*[None]
        }

        uut = AntennaSetsParser(self.test_filepath)
        rcu_config = uut.get_receiver_units_configuration("LBA_INNER")

        self.assertEqual(expected_rcu_config, rcu_config)

    def test_receiver_units_configuration_LBA_SPARSE_ODD(self):
        """ Verify if the RCUs decoding for LBA_INNER is successful """
        expected_rcu_config = {
            "Europe": 192*["LBH"],
            "Remote": 23*(2*["LBL"]+2*["LBH"]) + (2*["LBL"] + 2*[None]),
            "Core": 23*(2*["LBL"]+2*["LBH"]) + (2*["LBL"] + 2*[None])
        }

        uut = AntennaSetsParser(self.test_filepath)
        rcu_config = uut.get_receiver_units_configuration("LBA_SPARSE_ODD")

        self.assertEqual(expected_rcu_config, rcu_config)

    def test_receiver_units_configuration_per_station_LBA_INNER(self):
        """ Verify if the RCUs decoding for LBA_INNER is successfully mapped to the given stations """
        station_list = ['DE001', 'CS001', 'RS001']
        expected_rcu_config = {
            "DE001": 192 * ["LBH"],
            "CS001": 23 * (2 * ["LBL"] + 2 * ["LBH"]) + (2 * ["LBL"] + 2 * [None]),
            "RS001": 23 * (2 * ["LBL"] + 2 * ["LBH"]) + (2 * ["LBL"] + 2 * [None])
        }

        uut = AntennaSetsParser(self.test_filepath)
        rcu_config = uut.get_receiver_units_configuration_per_station("LBA_SPARSE_ODD", station_list)

        self.assertEqual(expected_rcu_config, rcu_config)



if __name__ == '__main__':
    unittest.main()
