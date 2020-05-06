#!/usr/bin/env python3

import argparse
import logging
import glob
import h5py
import os
import os.path
from lofar.common.lcu_utils import get_station_cable_delays
import numpy as np

logger = logging.getLogger(__name__)

def add_dipole_cable_delays_h5_files_in_directory(directory):
    directory = os.path.expanduser(directory)
    logger.info("scanning %s for h5 files", directory)
    h5_paths = glob.glob('%s/*.h5' % (directory,))
    logger.info("found %d h5 files in %s", len(h5_paths), directory)
    return add_dipole_cable_delays_h5_files(h5_paths)

def add_dipole_cable_delays_h5_files(h5_paths):
    '''
    Fetch the calibration tables from given stations (or all current stations if None given), and add them to the tbb h5 files
    :param stations - string or list of strings with path(s) for tbb spectral h5 files
    '''

    # small cache for the fetched cable_delays from the stations
    cable_delays = {}

    # loop over all h5 files
    for h5_path in sorted(h5_paths):
        try:
            with h5py.File(h5_path, 'r+') as file:
                # check if this is a correct tbb spectral mode file
                if file.attrs.get('FILETYPE') != 'tbb':
                    logger.warning('skipping file %s which has incorrect FILETYPE=%s', h5_path, file.attrs.get('FILETYPE'))
                    continue

                if file.attrs.get('OPERATING_MODE') != 'spectral':
                    logger.warning('skipping file %s which has incorrect OPERATING_MODE=%s', h5_path, file.attrs.get('OPERATING_MODE'))
                    continue

                logger.info('add_dipole_cable_delays_h5_files: processing file %s', h5_path)

                # loop over all stations and dipoles in the file
                for root_key in list(file.keys()):
                    if root_key.startswith('STATION_'):
                        station_group = file[root_key]
                        station_name = station_group.attrs['STATION_NAME']

                        # check if we already have fetched the caltables for this station for this filter
                        # if not, fetch them once and cache them during this method's lifetime
                        if station_name not in cable_delays:
                            station_cable_delays = get_station_cable_delays(stations=station_name).get(station_name)
                            if station_cable_delays:
                                cable_delays[station_name] = station_cable_delays

                        # get the cached cable_delays for this station and filter
                        if station_name in cable_delays:
                            station_cable_delays = cable_delays[station_name]

                            for station_key in list(station_group.keys()):
                                if station_key.startswith('DIPOLE_'):
                                    dipole_group = station_group[station_key]

                                    try:
                                        rcu_id = dipole_group.attrs['RCU_ID']
                                        logger.debug('  adding cable delays for station=%s dipole=%s', station_name, rcu_id)
                                        #TODO: select by antenna type. We now use hard coded HBA.
                                        dipole_group.attrs['CABLE_DELAY'] = station_cable_delays['HBA']['delays'][rcu_id]
                                        dipole_group.attrs['CABLE_DELAY_UNIT'] = 'seconds'
                                    except Exception as e:
                                        # just continue
                                        logger.exception(e)
                        else:
                            logger.warning('  could not find station cable delays, so cannot add them for station=%s in file %s', station_name, h5_path)
        except Exception as e:
            # just continue
            logger.exception(e)

def parse_args():
    parser = argparse.ArgumentParser("add cable delays for each dipole in each station in the tbb spectral h5 files in the given directory",
                                     add_help=True)
    parser.add_argument("-d", "--directory", default=os.getcwd(), dest="directory",
                        help="directory to scan for tbb spectral h5 files. default: %(default)s")
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    add_dipole_cable_delays_h5_files_in_directory(args.directory)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main()