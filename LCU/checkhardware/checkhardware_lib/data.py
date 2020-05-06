#!/usr/bin/env python3

"""
data library for reading in sample data
"""

# from general_lib import *
from .lofar import mode_to_band, is_test_mode_active, rspctl, select_str, run_cmd, get_rcu_info
import os
import numpy as np
import logging
from time import sleep

test_version = '0815'

logger = logging.getLogger('main.data')
logger.debug("starting data logger")


class AntennaData:
    bands = {'10_90'  : (1, 3),
             '30_90'  : (2, 4),
             '110_190': (5,),
             '170_210': (6,),
             '210_250': (7,)}

    XPOL = 'x'
    YPOL = 'y'
    XYPOL = 'xy'

    def __init__(self, args):
        self._args = args
        if 'data-dir' not in args or 'n_rcus' not in args:
            logger.error("missing arguments")
            return
        self._data_dir = self._args['data-dir']
        self._n_rcus = int(self._args.get('n_rcus', 96))
        self._sbdata = np.zeros((self._n_rcus, 1, 512), dtype=np.float64)
        self._rcu_info = {}
        for rcu in range(self._n_rcus):
            self._rcu_info[str(rcu)] = {'state': 'OFF', 'mode': '0'}
        self._rcu_mask = []
        self._sb_mask = {}
        self._rcus = {}
        self._requested_seconds = 0
        for band in list(self.bands.keys()):
            self._sb_mask[band] = []
            self._rcus[band] = {self.XPOL: [], self.YPOL: [], self.XYPOL: []}

    def _reset(self):
        self._n_rcus = int(self._args.get('n_rcus', 96))
        self._rcu_info = {}
        for rcu in range(self._n_rcus):
            self._rcu_info[str(rcu)] = {'state': 'OFF', 'mode': '0'}
        self._rcu_mask = []
        self._sb_mask = {}
        self._rcus = {}
        for band in list(self.bands.keys()):
            self._sb_mask[band] = []
            self._rcus[band] = {self.XPOL: [], self.YPOL: [], self.XYPOL: []}

    def seconds(self):
        return self._sbdata.shape[1]

    def max_rcus(self):
        return self._n_rcus

    def antenna(self, rcu):
        ant = rcu // 2
        if self._rcu_info[str(rcu)]['mode'] in ('1', '2'):
            ant += 48
        return ant

    def mode(self, rcu):
        return int(self._rcu_info[str(rcu)]['mode'])

    def polarity(self, rcu):
        """
        check polarity of signal
        :param rcu: rcu number
        :return: pol, 0=x, 1=y
        """
        pol = None
        if self._rcu_info[str(rcu)]['state'] == 'ON':
            if self._rcu_info[str(rcu)]['mode'] in ('1', '2'):
                if rcu % 2 == 0:
                    pol = self.YPOL
                else:
                    pol = self.XPOL
            else:
                if rcu % 2 == 0:
                    pol = self.XPOL
                else:
                    pol = self.YPOL
        return pol

    def rcus(self, band, polarity):
        # logger.debug("band='%s' polarity='%s'" % (band, polarity))
        pol = None
        if polarity in (0, 'X', 'x'):
            pol = self.XPOL
        if polarity in (1, 'Y', 'y'):
            pol = self.YPOL
        if polarity in (2, 'XY', 'xy'):
            pol = self.XYPOL
        if not pol:
            return []
        # if not filled, fill it now
        if len(self._rcus[band][pol]) == 0:
            for rcu in self._rcu_info:
                if self._rcu_info[rcu]['state'] == 'ON':
                    if int(self._rcu_info[rcu]['mode']) in self.bands[band]:
                        if pol is self.XYPOL:
                            self._rcus[band][pol].append(int(rcu))
                        elif self.polarity(int(rcu)) == pol:
                            self._rcus[band][pol].append(int(rcu))
        #logger.debug("pol=%s  selected rcus=%s" % (pol, ','.join([str(i) for i in sorted(self._rcus[band][pol])])))
        #logger.debug("pol=%s  selected rcus=%s" % (pol, str(sorted(self._rcus[band][pol])).replace(' ','') ))
        return sorted(self._rcus[band][pol])

    def mask_rcu(self, rcus):
        """
        mask rcu, this rcus will be ignored
        :param rcus: list with rcus to mask
        """
        if type(rcus) in (list, tuple):
            for rcu in rcus:
                if rcu not in self._rcu_mask:
                    self._rcu_mask.append(rcu)
        else:
            if rcus not in self._rcu_mask:
                self._rcu_mask.append(rcus)

    def reset_masked_rcus(self):
        self._rcu_mask = []

    def reset_masked_sb(self, band):
        self._sb_mask[band] = []

    def set_passband(self, band, subbands):
        """
        mask subbands, these subbands will be ignored
        :param band: band to add
        :param subbands: list with subbands to mask
        """
        for sb in range(1,512,1):
            if sb not in subbands:
                if sb not in self._sb_mask:
                    self._sb_mask[band].append(sb)

    def mask_sb(self, band, subbands):
        """
        mask subbands, these subbands will be ignored
        :param band: band to add
        :param subbands: list with subbands to mask
        """
        for sb in subbands:
            if sb not in self._sb_mask:
                self._sb_mask[band].append(sb)

    def band_active(self, band):
        """
        Checks if data available
        :param band: band to check
        :return: True if data available else False
        """
        if self.rcus(band, 'xy'):
            return True
        return False

    def collect(self, n_seconds=2, slow=False):
        """
        Collect new data
        :param n_seconds: seconds to record
        :param slow: get data i 2 steps
        :return: None
        """
        self._requested_seconds = n_seconds
        self._reset()
        self._rcu_info = get_rcu_info(list(range(self._n_rcus)))
        self._record_antenna_data(n_seconds, slow)
        self._sbdata = self._read_files()



    def _record_antenna_data(self, n_seconds, slow):
        """
        record antenna data using rspctl --statistics cmd, for all active rcus a file will be made
        :param n_seconds: number of seconds to sample data
        :param slow: slow down lcu disk usage
        :return:
        """
        self._remove_all_datafiles()  # cleanup data directory
        x_list = []
        y_list = []
        xy_list = []
        for rcu in self._rcu_info:
            if self._rcu_info[rcu]['state'] == 'ON':
                xy_list.append(int(rcu))
                if int(rcu) % 2 == 0:
                    x_list.append(int(rcu))
                else:
                    y_list.append(int(rcu))

        if slow is True:
            rcus = select_str(x_list)
            logger.debug("Wait %d seconds while recording X data" % n_seconds)
            rspctl('--statistics --duration=%d --integration=1 --directory=%s --select=%s' % (
                n_seconds, self._data_dir, rcus), wait=0.0)

            rcus = select_str(y_list)
            logger.debug("Wait %d seconds while recording Y data" % n_seconds)
            rspctl('--statistics --duration=%d --integration=1 --directory=%s --select=%s' % (
                n_seconds, self._data_dir, rcus), wait=0.0)
        else:
            rcus = select_str(xy_list)
            logger.debug("Wait %d seconds while recording XY data" % n_seconds)
            rspctl('--statistics --duration=%d --integration=1 --directory=%s --select=%s' % (
                n_seconds, self._data_dir, rcus), wait=0.0)

    def _remove_all_datafiles(self):
        """
        remove all *.dat files from data_dir
        """
        #logger.debug("testmode= %s" % str(is_test_mode_active()))
        if not is_test_mode_active():
            if os.access(self._data_dir, os.F_OK):
                cmd = 'rm -f %s/*' % self._data_dir
                logger.debug("remove test data, cmd= %s" % cmd)
                os.system(cmd)
                sleep(0.5)
                #files = os.listdir(self._data_dir)
                ## print files
                #for filename in files:
                #    if filename[-3:] == 'dat' or filename[-3:] == 'nfo':
                #        os.remove(os.path.join(self._data_dir, filename))

    def _read_file(self, full_filename):
        if not is_test_mode_active():
            sleep(0.02)
        data = np.fromfile(full_filename, dtype=np.float64)
        n_samples = len(data)
        if (n_samples % 512) > 0:
            logger.warning("data error: number of samples (%d) not multiple of 512 in '%f'" % (
                n_samples, full_filename))
        n_frames = n_samples // 512
        data = data.reshape(n_frames, 512)
        #logger.info("recorded data shape %s" %(str(data.shape)))
        return data[:self._requested_seconds,:]

    def _read_files(self):
        files_in_dir = os.listdir(self._data_dir)
        if len(files_in_dir) == 0:
            logger.warning('No data recorded !!')
            self._reset()
            return

        data_shape = self._read_file(os.path.join(self._data_dir, files_in_dir[0])).shape
        ssdata = np.zeros((self._n_rcus, data_shape[0], data_shape[1]), dtype=np.float64)
        for file_name in sorted(files_in_dir):
            # path, filename = os.split(file_name)
            # filename format: 20160228_174114_sst_rcu000.dat
            rcu = int(file_name.split('.')[0][-3:])
            ssdata[rcu, :, :] = self._read_file(os.path.join(self._data_dir, file_name))

            # logger.debug("%s  rcu=%d" %(file_name, rcu))

        # mask zero values and convert to dBm
        # logger.debug("rcu0=%s" % ssdata[:,0,301])
        ssdata_db = np.log10(np.ma.masked_less(ssdata, self._args.get('minvalue', 1.0))) * 10.0
        # do not use subband 0
        # logger.debug("rcu0=%s" % ssdata_db[:,0,301])
        ssdata_db[:, :, 0] = np.ma.masked
        # logger.debug("rcu0=%s" % ssdata_db[:,0,301])
        logger.debug("recorded data shape %s" %(str(ssdata_db.shape)))
        return ssdata_db

    # subbands is list to mask
    def get_masked_data(self, band='', mask_subbands=True, mask_rcus=True):
        data = self._sbdata.copy()
        if mask_subbands:
            data[:, :, self._sb_mask[band]] = np.ma.masked
        if mask_rcus:
            data[self._rcu_mask, :, :] = np.ma.masked
        return data

    # spectra(s) for one rcu
    def rcu_median_spectra(self, rcu, masked):
        spec = self.rcu_spectras(rcu, masked)
        if spec.shape[0] > 1:
            return np.median(spec, axis=0)
        return spec[0,:]


    def rcu_mean_spectra(self, rcu, masked):
        spec = self.rcu_spectras(rcu, masked)
        if spec.shape[0] > 1:
            return np.mean(spec, axis=0)
        return spec[0,:]


    def rcu_spectras(self, rcu, masked):
        if rcu in range(self._n_rcus):
            if masked:
                return self.get_masked_data(band=mode_to_band(self.mode(rcu)), mask_rcus=False)[rcu, :, :]
            else:
                return self._sbdata[rcu, :, :]

        logger.error("Not valid arguments %s" % (
            str(rcu)))
        return None

    # spectras for one band and polarity
    def mean_spectras(self, freq_band, polarity, masked):
        spec = self.spectras(freq_band, polarity, masked)
        if spec.shape[1] > 1:
            return np.mean(spec, axis=1)
        return spec[:,0,:]

    def mean_all_spectras(self, freq_band, polarity, masked):
        spec = self.mean_spectras(freq_band, polarity, masked)
        if spec.shape[0] > 1:
            return np.mean(spec, axis=0)
        return spec[0,:]

    def median_spectras(self, freq_band, polarity, masked):
        spec = self.spectras(freq_band, polarity, masked)
        if spec.shape[1] > 1:
            return np.median(spec, axis=1)
        return spec[:,0,:]

    def median_all_spectras(self, freq_band, polarity, masked):
        spec = self.median_spectras(freq_band, polarity, masked)
        if spec.shape[0] > 1:
            return np.median(spec, axis=0)
        return spec[0,:]

    def spectras(self, freq_band, polarity, masked):
        return self.subbands(freq_band, polarity, list(range(512)), masked)

    def subbands(self, freq_band, polarity, sb_set, masked):
        sb_range = list(range(512))
        pol = None
        band = None
        if polarity in (0, 'X', 'x'):
            pol = self.XPOL
        if polarity in (1, 'Y', 'y'):
            pol = self.YPOL
        if polarity in (2, 'XY', 'xy'):
            pol = self.XYPOL
        if freq_band in list(self.bands.keys()):
            band = freq_band

        if isinstance(sb_set, int) or isinstance(sb_set, np.integer):
            if sb_set in sb_range:
                sb = sb_set
            else:
                sb = None
        else:
            sb = list(sb_set)
            for i in sb:
                if i not in sb_range:
                    sb = None

        if pol and band and sb:
            rcu_list = self.rcus(band, pol)
            #logger.debug("rcu-list=%s" % str(rcu_list))
            # logger.debug("sb-list=%s" % str(sb))
            if masked:
                masked_data = self.get_masked_data(band=band)
                rcu_data = masked_data[rcu_list, :, :]
                sb_data = rcu_data[:, :, sb]
                # logger.debug("subbands():: sb_data.shape=%s" % str(sb_data.shape))
                # logger.debug("subbands():: sb_data= %s" % str(sb_data))
                return sb_data
            else:
                rcu_data = self._sbdata[rcu_list, :, :]
                sb_data = rcu_data[:, :, sb]
                # logger.debug("subbands():: sb_data.shape=%s" % str(sb_data.shape))
                # logger.debug("subbands():: sb_data= %s" % str(sb_data))
                return sb_data

        logger.error("Not valid arguments %s, %s, %s" % (str(band),
                                                         str(polarity),
                                                         str(sb_set)))
        return None
