#!/usr/bin/env python3

import argparse
import logging
import glob
import h5py
import os
import os.path
from lofar.common.lcu_utils import get_station_calibration_tables
import numpy as np

logger = logging.getLogger(__name__)

def add_station_calibration_tables_h5_files_in_directory(directory):
    directory = os.path.expanduser(directory)
    logger.info("scanning %s for h5 files", directory)
    h5_paths = glob.glob('%s/*.h5' % (directory,))
    logger.info("found %d h5 files in %s", len(h5_paths), directory)
    return add_station_calibration_tables_h5_files(h5_paths)

def add_station_calibration_tables_h5_files(h5_paths):
    '''
    Fetch the calibration tables from given stations (or all current stations if None given), and add them to the tbb h5 files
    :param h5_paths - string or list of strings with path(s) for tbb spectral h5 files
    '''

    # small cache for the fetched caltables from the stations
    caltables = {}

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

                if 'FILTER_SELECTION' not in file.attrs:
                    logger.warning('skipping file %s which has no defined FILTER_SELECTION', h5_path)
                    continue

                logger.info('add_station_calibration_tables_h5_files: processing file %s', h5_path)

                # string magic... FILTER_SELECTION in the h5 file contains the antennaset and filter seperated by a '_'
                # the caltable files names on the lcu's expect a '-' seperator
                # so tweak the string
                # example: HBA_110_190 -> HBA-110_190
                items = file.attrs['FILTER_SELECTION'].partition('_')
                antenna_set_and_filter = '%s-%s' % (items[0], items[2])

                if antenna_set_and_filter not in caltables:
                    # add entry for antenna_set_and_filter if not available yet
                    caltables[antenna_set_and_filter] = {}

                # use caltables for the given antenna_set_and_filter
                caltables_for_antenna_set_and_filter = caltables[antenna_set_and_filter]

                # loop over all stations and dipoles in the file
                for root_key in list(file.keys()):
                    if root_key.startswith('STATION_'):
                        station_group = file[root_key]
                        station_name = station_group.attrs['STATION_NAME']

                        # check if we already have fetched the caltables for this station for this filter
                        # if not, fetch them once and cache them during this method's lifetime
                        if station_name not in caltables_for_antenna_set_and_filter:
                            station_caltable = get_station_calibration_tables(stations=station_name,
                                                                              antenna_set_and_filter=antenna_set_and_filter).get(station_name)
                            caltables_for_antenna_set_and_filter[station_name] = station_caltable

                        # get the cached caltables for this station and filter
                        if caltables_for_antenna_set_and_filter.get(station_name):
                            caltable = caltables_for_antenna_set_and_filter[station_name][1]
                            delays = _calcDipoleCalibrationDelays(caltable)

                            for station_key in list(station_group.keys()):
                                if station_key.startswith('DIPOLE_'):
                                    dipole_group = station_group[station_key]

                                    try:
                                        rcu_id = dipole_group.attrs['RCU_ID']
                                        logger.debug('  adding calibration delays and gains station=%s dipole=%s',
                                                      station_name, rcu_id)
                                        dipole_group.attrs['DIPOLE_CALIBRATION_DELAY'] = delays[rcu_id]
                                        dipole_group.attrs['DIPOLE_CALIBRATION_DELAY_UNIT'] = 'seconds'
                                        dipole_group.attrs['DIPOLE_CALIBRATION_GAIN_CURVE'] = caltable[rcu_id,:]
                                    except Exception as e:
                                        # just continue
                                        logger.exception(e)
                        else:
                            logger.warning('  could not find station calibration, so cannot add calibration delays and gains for station=%s', station_name)
        except Exception as e:
            # just continue
            logger.exception(e)

def _calcDipoleCalibrationDelays(cal_table):
    """Calculate the remaining delay to be applied to calibrate the dipole up to station level
    :param cal_table: a numpy array of complex double from the station calibration files. Size=(#dipoles,#subbands)
    :return: numpy array of doubles with a delay in (fractional) seconds for each dipole (practical values are in the order of 1e-9 which are thus nanoseconds)
    """
    #magic formula from Sander
    return np.median(np.diff(np.angle(cal_table[:]), axis=1) / 195312.5 / 2 / np.pi, axis=1)

def parse_args():
    parser = argparse.ArgumentParser("add calibration delays and gains for each dipole in each station in the tbb spectral h5 files in the given directory",
                                     add_help=True)
    parser.add_argument("-d", "--directory", default=os.getcwd(), dest="directory",
                        help="directory to scan for tbb spectral h5 files. default: %(default)s")
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    add_station_calibration_tables_h5_files_in_directory(args.directory)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main()