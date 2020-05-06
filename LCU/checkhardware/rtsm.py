#!/usr/bin/env python3

check_version = '0714'

import sys
import os
import time
import traceback
from socket import gethostname
from threading import Thread
import numpy as np

os.umask(0o01)
os.nice(15)

conf_file = r'/localhome/stationtest/config/check_hardware.conf'

mainpath = r'/opt/stationtest'
maindatapath = r'/localhome/stationtest'
observationspath = r'/opt/lofar/var/run'
BEAMLETPATH = r'/localhome/data/Beamlets'

confpath = os.path.join(maindatapath, 'config')
logpath = os.path.join(maindatapath, 'log')
rtsmpath = os.path.join(maindatapath, 'rtsm_data')

# if not exists make path
if not os.access(logpath, os.F_OK):
    os.mkdir(logpath)
if not os.access(rtsmpath, os.F_OK):
    os.mkdir(rtsmpath)

hostname = gethostname().split('.')[0].upper()

# first start main logging before including checkhardware_lib
import logging

# backup log files
for nr in range(8, -1, -1):
    if nr == 0:
        full_filename = os.path.join(logpath, '%s_rtsm.log' % hostname)
    else:
        full_filename = os.path.join(logpath, '%s_rtsm.log.%d' % (hostname, nr))
    full_filename_new = os.path.join(logpath, '%s_rtsm.log.%d' % (hostname, (nr + 1)))
    if os.path.exists(full_filename):
        os.rename(full_filename, full_filename_new)

# make and setup logger
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
# create file handler
filename = '%s_rtsm.log' % hostname
full_filename = os.path.join(logpath, filename)
file_handler = logging.FileHandler(full_filename, mode='w')
formatter = logging.Formatter('%(asctime)s %(name)-14s %(levelname)-8s %(message)s')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
time.sleep(2.0)
logger.debug("logger is working")

# now include checkhardware library
from checkhardware_lib import *
from checkhardware_lib.spectrum_checks import *
from checkhardware_lib.data import AntennaData


def lba_mode(mode):
    return mode in (1, 2, 3, 4)


def lba_low_mode(mode):
    return mode in (1, 2)


def lba_high_mode(mode):
    return mode in (3, 4)


def hba_mode(mode):
    return mode in (5, 6, 7)


def abbr_to_str(key):
    checks = {'OSC': "Oscillation", 'HN': "High-noise", 'LN': "Low-noise", 'J': "Jitter", 'SN': "Summator-noise",
              'CR': "Cable-reflection", 'M': "Modem-failure", 'DOWN': "Antenna-fallen", 'SHIFT': "Shifted-band"}
    return checks.get(key, 'Unknown')


# get and unpack configuration file
class Configuration:
    def __init__(self):
        self.conf = dict()
        full_filename = os.path.join(confpath, 'checkHardware.conf')
        f = open(full_filename, 'r')
        data = f.readlines()
        f.close()
        for line in data:
            if line[0] in ('#', '\n', ' '):
                continue
            if line.find('#') > 0:
                line = line[:line.find('#')]
            try:
                key, value = line.strip().split('=')
                key = key.replace('_', '-')
                self.conf[key] = value
            except ValueError:
                print("Not a valid key, value pair: %s" % line)
            except:
                raise

    def get_int(self, key, default=0):
        return int(self.conf.get(key, str(default)))

    def get_float(self, key, default=0.0):
        return float(self.conf.get(key, str(default)))

    def get_str(self, key):
        return self.conf.get(key, '')


class CSV:
    def __init__(self, obsid):
        self.obsid = obsid
        self.station = hostname
        self.filename = "%s_%s_open.dat" %(self.station, self.obsid)
        self.rcumode = 0
        self.record_timestamp = 0
        self.write_header()

    def set_rcu_mode(self, rcumode):
        self.rcumode = rcumode
        return

    def set_record_timestamp(self, timestamp):
        self.record_timestamp = timestamp
        return

    def write_header(self):
        full_filename = os.path.join(rtsmpath, self.filename)
        # write only if new file
        if not os.path.exists(full_filename):
            f = open(full_filename, 'w')
            f.write('# SPECTRA-INFO=rcu,rcumode,obs-id,check,startfreq,stopfreq,rec-timestamp\n')
            f.write('#\n')
            f.flush()
            f.close()
        return

    def write_spectra(self, data, rcu, check):
        # dumpTime = time.gmtime(self.record_timestamp)
        # date_str = time.strftime("%Y%m%d", dumpTime)

        full_filename = os.path.join(rtsmpath, self.filename)

        logger.debug("start dumping data to %s" % full_filename)

        f = open(full_filename, 'a')

        freq = (0, 0)
        if self.rcumode in (1, 2, 3, 4):
            freq = (0 , 100)
        elif self.rcumode in (5,):
            freq = (100, 200)
        elif self.rcumode in (6,):
            freq = (160, 240)
        elif self.rcumode in (7,):
            freq = (200, 300)

        spectra_info = "SPECTRA-INFO=%d,%d,%s,%s,%d,%d,%f\n" % (
                        rcu, self.rcumode, self.obsid, check, freq[0], freq[1], self.record_timestamp)
        mean_spectra = "MEAN-SPECTRA=["
        for i in data.median_all_spectras(freq_band=mode_to_band(self.rcumode), polarity=data.polarity(rcu), masked=True):
            if np.ma.is_masked(i): i = 0 ## FIX numpy >= 1.13
            mean_spectra += "%3.1f " % np.nan_to_num(i)
        mean_spectra += "]\n"

        bad_spectra = "BAD-SPECTRA=["
        for i in data.rcu_mean_spectra(rcu=rcu, masked=True):
            #logger.debug("BAD-SPECTRA=%s" % str(i))
            if np.ma.is_masked(i): i = 0 ## FIX numpy >= 1.13
            bad_spectra += "%3.1f " % np.nan_to_num(i)
        bad_spectra += "]\n\n"

        f.write(spectra_info)
        f.write(mean_spectra)
        f.write(bad_spectra)

        f.close()
        return

    def write_info(self, start_time, stop_time, obsid_samples):
        full_filename = os.path.join(rtsmpath, self.filename)
        logger.debug("add obs_info to %s" % full_filename)
        f = open(full_filename, 'a')
        f.write('# OBS-ID-INFO=obsid,start_time,stop_time,obsid_samples\n')
        f.write('OBS-ID-INFO=%s,%5.3f,%5.3f,%d\n\n' % (self.obsid, start_time, stop_time, obsid_samples))
        f.flush()
        f.close()
        return

    def close_file(self):
        full_filename = os.path.join(rtsmpath, self.filename)
        filename_new = self.filename.replace('open', 'closed')
        full_filename_new = os.path.join(rtsmpath, filename_new)
        logger.debug("rename file from %s to %s" % (full_filename, full_filename_new))
        os.rename(full_filename, full_filename_new)
        self.obsid = ""
        self.filename = ""
        return


def check_oscillation(data, band, error_list, settings, cvs):
    logger.debug("start oscillation check")
    for pol in ('X', 'Y'):
        # test_data = data.getAll()[:,:1,:]
        result = check_for_oscillation(data, band, pol, settings)

        if len(result) > 1:
            # get mean values from all rcu's (rcu = -1)
            rcu, ref_max_sum, ref_n_peaks, ref_rcu_low = result[0]

            # rcu, max_sum, n_peaks, rcu_low = sorted(result[1:], reverse=True)[0]
            if len(result) == 2:
                rcu, max_sum, n_peaks, rcu_low = result[1]
            else:
                ref_low = result[0][3]
                max_low_rcu = (-1, -1)
                max_sum_rcu = (-1, -1)
                for i in result[1:]:
                    rcu, max_sum, n_peaks, rcu_low = i
                    if max_sum > max_sum_rcu[0]:
                        max_sum_rcu = (max_sum, rcu)
                    if (rcu_low - ref_low) > max_low_rcu[0]:
                        max_low_rcu = (rcu_low, rcu)

                rcu_low, rcu = max_low_rcu

            ant = data.antenna(rcu)
            mode = data.mode(rcu)

            if lba_mode(mode):
                logger.info("Mode-%d RCU-%03d Ant-%03d %c "
                            "Oscillation, sum=%3.1f(%3.1f) peaks=%d(%d) low=%3.1fdB(%3.1f) (=ref)" % (
                             mode, rcu, ant, pol, max_sum, ref_max_sum, n_peaks, ref_n_peaks, rcu_low, ref_rcu_low))
                if rcu not in error_list:
                    error_list.append(rcu)
                    cvs.set_rcu_mode(mode)
                    cvs.write_spectra(data, rcu, "OSC")

            if hba_mode(mode):
                if max_sum > 5000.0 or n_peaks > 40:
                    logger.info("Mode-%d RCU-%03d Tile-%02d %c "
                                "Oscillation, sum=%3.1f(%3.1f) peaks=%d(%d) low=%3.1fdB(%3.1f) ref=()" % (
                                 mode, rcu, ant, pol, max_sum, ref_max_sum, n_peaks, ref_n_peaks, rcu_low, ref_rcu_low))
                    if rcu not in error_list:
                        error_list.append(rcu)
                        cvs.set_rcu_mode(mode)
                        cvs.write_spectra(data, rcu, "OSC")
    return


def check_noise(data, band, error_list, settings, cvs):
    logger.debug("start noise check")
    for pol in ('X', 'Y'):
        low_noise, high_noise, jitter = check_for_noise(data, band, pol, settings)

        for err in high_noise:
            rcu, val, bad_secs, ref, diff = err

            ant = data.antenna(rcu)
            mode = data.mode(rcu)

            if lba_mode(mode):
                logger.info("Mode-%d RCU-%03d Ant-%03d %c "
                            "High-noise, value=%3.1fdB bad=%d(%d) limit=%3.1fdB diff=%3.1fdB" % (
                             mode, rcu, ant, pol, val, bad_secs, data.seconds(), ref, diff))

            if hba_mode(mode):
                logger.info("Mode-%d RCU-%03d Tile-%02d %c "
                            "High-noise, value=%3.1fdB bad=%d(%d) limit=%3.1fdB diff=%3.1fdB" % (
                             mode, rcu, ant, pol, val, bad_secs, data.seconds(), ref, diff))

            if rcu not in error_list:
                error_list.append(rcu)
                cvs.set_rcu_mode(mode)
                cvs.write_spectra(data, rcu, "HN")

        for err in low_noise:
            rcu, val, bad_secs, ref, diff = err

            ant = data.antenna(rcu)
            mode = data.mode(rcu)

            if lba_mode(mode):
                logger.info("Mode-%d RCU-%03d Ant-%03d %c "
                            "Low-noise, value=%3.1fdB bad=%d(%d) limit=%3.1fdB diff=%3.1fdB" % (
                             mode, rcu, ant, pol, val, bad_secs, data.seconds(), ref, diff))

            if hba_mode(mode):
                logger.info("Mode-%d RCU-%03d Tile-%02d %c "
                            "Low-noise, value=%3.1fdB bad=%d(%d) limit=%3.1fdB diff=%3.1fdB" % (
                             mode, rcu, ant, pol, val, bad_secs, data.seconds(), ref, diff))

            if rcu not in error_list:
                error_list.append(rcu)
                cvs.set_rcu_mode(mode)
                cvs.write_spectra(data, rcu, "LN")
    return


def check_summator_noise(data, band, error_list, settings, cvs):
    logger.debug("start summator-noise check")
    for pol in ('X', 'Y'):
        # sn=SummatorNoise  cr=CableReflections
        sn = check_for_summator_noise(data=data, band=band, pol=pol, parset=settings)
        cr = check_for_cable_reflection(data=data, band=band, pol=pol, parset=settings)
        for msg in sn:
            rcu, peaks, max_peaks = msg

            tile = data.antenna(rcu)
            mode = data.mode(rcu)

            logger.info("Mode-%d RCU-%03d Tile-%02d %c "
                        "Summator-noise, cnt=%d peaks=%d" % (
                         mode, rcu, tile, pol, peaks, max_peaks))

            if rcu not in error_list:
                error_list.append(rcu)
                cvs.set_rcu_mode(mode)
                cvs.write_spectra(data, rcu, "SN")

        for msg in cr:
            rcu, peaks, max_peaks = msg

            tile = data.antenna(rcu)
            mode = data.mode(rcu)

            logger.info("Mode-%d RCU-%03d Tile-%02d %c "
                        "Cable-reflections, cnt=%d peaks=%d" % (
                         mode, rcu, tile, pol, peaks, max_peaks))
            # if rcu not in error_list:
            #    error_list.append(rcu)
            #    cvs.set_rcu_mode(mode)
            #    cvs.write_spectra(data, rcu, "CR")
    return


def check_down(data, band, error_list, settings, cvs):
    logger.debug("start down check")
    down, shifted = check_for_down(data, band, settings)

    ref_max_sb = 0
    ref_max_val = 0.0
    ref_max_bw = 0
    ref_band_pwr = 0.0

    for msg in down:
        rcu, max_sb, max_val, max_bw, band_pwr = msg
        if rcu == 'Xref':
            logger.info("down test X rcus's median values: sb=%d, pwr=%3.1fdB, bw=%d, band-pwr=%3.1fdB" % (
                        max_sb, max_val, max_bw, band_pwr))
            continue
        if rcu == 'Yref':
            logger.info("down test Y rcu's median values: sb=%d, pwr=%3.1fdB, bw=%d, band-pwr=%3.1fdB" % (
                        max_sb, max_val, max_bw, band_pwr))
            continue

        max_offset = 292 - max_sb

        ant = data.antenna(rcu)
        mode = data.mode(rcu)
        pol = data.polarity(rcu)

        logger.info("Mode-%d RCU-%02d Ant-%02d %s Down: sb=%d, pwr=%3.1fdB, bw=%d, band-pwr=%3.1fdB" % (
                     mode, rcu, ant, pol, max_sb, max_val, max_bw, band_pwr))

        if rcu not in error_list:
            error_list.append(rcu)
            cvs.set_rcu_mode(mode)
            cvs.write_spectra(data, rcu, "DOWN")
    return


def check_flat(data, band, error_list, settings, cvs):
    logger.debug("start flat check")
    flat = check_for_flat(data, band, settings)
    for msg in flat:
        rcu, mean_val = msg

        ant = data.antenna(rcu)
        mode = data.mode(rcu)
        pol = data.polarity(rcu)

        logger.info("Mode-%d RCU-%02d Ant-%02d %s "
                    "Flat, value=%5.1fdB" % (
                     mode, rcu, ant, pol, mean_val))
        if rcu not in error_list:
            error_list.append(rcu)
            cvs.set_rcu_mode(mode)
            cvs.write_spectra(data, rcu, "FLAT")
    return


def check_short(data, band, error_list, settings, cvs):
    logger.debug("start short check")
    short = check_for_short(data, band, settings)
    for msg in short:
        rcu, mean_val = msg

        ant = data.antenna(rcu)
        mode = data.mode(rcu)
        pol = data.polarity(rcu)

        logger.info("Mode-%d RCU-%02d Ant-%02d %s "
                    "Short, value=%5.1fdB" % (
                     mode, rcu, ant, pol, mean_val))
        if rcu not in error_list:
            error_list.append(rcu)
            cvs.set_rcu_mode(mode)
            cvs.write_spectra(data, rcu, "SHORT")
    return


def close_all_open_files():
    files = os.listdir(rtsmpath)
    for filename in files:
        if filename.find('open') > -1:
            full_filename = os.path.join(rtsmpath, filename)
            filename_new = filename.replace('open', 'closed')
            full_filename_new = os.path.join(rtsmpath, filename_new)
            os.rename(full_filename, full_filename_new)
    return


class DayInfo:
    def __init__(self):
        self.date = time.strftime("%Y%m%d", time.gmtime(time.time()))
        self.filename = "%s_%s_dayinfo.dat" % (hostname, self.date)
        self.samples = [0, 0, 0, 0, 0, 0, 0]  # RCU-mode 1..7
        self.obs_info = list()
        self.delete_old_days()
        self.read_file()

    def add_sample(self, rcumode=-1):
        date = time.strftime("%Y%m%d", time.gmtime(time.time()))
        # new day reset data and set new filename
        if self.date != date:
            self.date = date
            self.reset()
        if rcumode in range(1, 8, 1):
            self.samples[rcumode - 1] += 1
            self.write_file()

    def add_obs_info(self, obs_id, start_time, stop_time, rcu_mode, samples):
        self.obs_info.append([obs_id, start_time, stop_time, rcu_mode, samples])

    def reset(self):
        self.filename = "%s_%s_dayinfo.dat" % (hostname, self.date)
        self.samples = [0, 0, 0, 0, 0, 0, 0]  # RCU-mode 1..7
        self.obs_info = list()
        self.delete_old_days()

    # after a restart, earlier data is imported
    def read_file(self):
        full_filename = os.path.join(rtsmpath, self.filename)
        if os.path.exists(full_filename):
            f = open(full_filename, 'r')
            lines = f.readlines()
            f.close()
            for line in lines:
                if len(line.strip()) == 0 or line.strip()[0] == '#':
                    continue
                key, data = line.split('=')
                if key == 'DAY-INFO':
                    self.samples = [int(i) for i in data.split(',')[1:]]
                if key == 'OBSID-INFO':
                    d = data.split(',')
                    self.obs_info.append([d[0], float(d[1]), float(d[2]), int(d[3]), int(d[4])])

    # rewrite file every sample
    def write_file(self):
        full_filename = os.path.join(rtsmpath, self.filename)
        f = open(full_filename, 'w')
        f.write('#DAY-INFO date,M1,M2,M3,M4,M5,M6,M7\n')
        f.write('DAY-INFO=%s,%d,%d,%d,%d,%d,%d,%d\n' % (
               self.date, self.samples[0], self.samples[1], self.samples[2], self.samples[3],
               self.samples[4], self.samples[5], self.samples[6]))
        f.write('\n#OBS-ID-INFO obs_id, start_time, stop_time, rcu_mode, samples\n')
        for i in self.obs_info:
            f.write('OBS-ID-INFO=%s,%5.3f,%5.3f,%d,%d\n' % (
                    i[0], i[1], i[2], i[3], i[4]))
        f.close()

    def delete_old_days(self):
        files = os.listdir(rtsmpath)
        backup = True
        for filename in files:
            if filename.find('closed') != -1:
                backup = False
        if backup:
            for filename in files:
                if filename.find('dayinfo') != -1:
                    if filename.split('.')[0].split('_')[1] != self.date:
                        full_filename = os.path.join(rtsmpath, filename)
                        os.remove(full_filename)


def get_obs_id():
    """ check swlevel for active obsid,
    return: list with active obsids
    """
    obsids = []
    answer = run_cmd('swlevel')
    if answer.find("ObsID") > -1:
        s1 = answer.find("ObsID:") + 6
        s2 = answer.find("]")
        obsids = answer[s1:s2].strip().split()
    return obsids


def get_obs_id_info(obsid):
    filename = "Observation%s" % obsid.strip()
    fullfilename = os.path.join(observationspath, filename)
    f = open(fullfilename, 'r')
    obsinfo = f.read()
    f.close()

    m1 = obsinfo.find("Observation.receiverList")
    m2 = obsinfo.find("\n", m1)
    obs_rcu_str = obsinfo[m1:m2].split("=")[1].strip()
    #print obs_rcu_str
    obs_rcu_list = extract_select_str(obs_rcu_str[1:-1])

    m1 = obsinfo.find("Observation.startTime")
    m2 = obsinfo.find("\n", m1)
    obs_start_str = obsinfo[m1:m2].split("=")[1].strip()
    #print obs_start_str
    obs_start_time = time.mktime(time.strptime(obs_start_str, "%Y-%m-%d %H:%M:%S"))

    m1 = obsinfo.find("Observation.stopTime")
    m2 = obsinfo.find("\n", m1)
    obs_stop_str = obsinfo[m1:m2].split("=")[1].strip()
    #print obs_stop_str
    obs_stop_time = time.mktime(time.strptime(obs_stop_str, "%Y-%m-%d %H:%M:%S"))

    logger.debug("obsid=%s  time=%s..%s  rcus=%s" % (obsid, obs_start_str, obs_stop_str, obs_rcu_str))
    #print obs_start_time, obs_stop_time, time.time()
    return obsid, obs_start_time, obs_stop_time, obs_rcu_list


class RecordBeamletStatistics(Thread):
    def __init__(self, obsid, starttime, duration):
        Thread.__init__(self)
        self.running = False
        self.obsid = obsid
        self.starttime = starttime
        self.duration = duration
        self.dump_dir = os.path.join(BEAMLETPATH, self.obsid)
        try:
            os.mkdir(self.dump_dir)
            self.ready = True
        except OSError:
            self.ready = False
        except:
            raise

    def is_running(self):
        return self.running

    def kill_recording(self):
        if self.running:
            logger.debug("kill recording beamlet statistics")
            run_cmd(cmd='killall rspctl')
            logger.debug("recording killed")

    def run(self):
        sleeptime = self.starttime - time.time()
        if sleeptime > 0.0:
            time.sleep(sleeptime)
        if self.duration:
            self.running = True
            logger.debug("start recording beamlet statistics for %d seconds" % self.duration)
            rspctl('--statistics=beamlet --duration=%d --integration=1 --directory=%s' % (self.duration, self.dump_dir))
            logger.debug("recording done")
            self.running = False

def main():
    obs_id = ""
    active_obs_id = ""
    rcumode = 0
    dayinfo = DayInfo()

    init_lofar_lib()

    # get test settings from configuration file
    conf = TestSettings(filename=conf_file)

    logger.info('== Start rtsm (Real Time Station Monitor) ==')

    # Read in RemoteStation.conf
    st_id, n_rsp, n_tbb, n_lbl, n_lbh, n_hba, hba_split = read_station_config()

    n_rcus = n_rsp * 8

    data = AntennaData({'n_rcus': n_rcus, 'data-dir': data_dir()})

    obs_info = {}
    obs_info_to_delete = []

    close_all_open_files()

    sleep_counter = 0
    while True:
        try:
            time_now = time.time()

            # get list with active obsids from swlevel, [] if none
            obsids = get_obs_id()

            # loop over obsids and start new proces for each obsid, asuming more than one observation can be run
            # get also used rcus from parameterset
            if obsids:
                for _obsid in obsids:
                    if not _obsid in obs_info:
                        # new obsid, setup and start recording beamlet statistics
                        obs_info[_obsid] = {}
                        obsid, start, stop, rcus = get_obs_id_info(_obsid)
                        obs_info[_obsid]['starttime'] = start
                        obs_info[_obsid]['stoptime'] = stop
                        obs_info[_obsid]['rcus'] = rcus
                        obs_info[_obsid]['state'] = 'new'
                        obs_info[_obsid]['csv'] = CSV(_obsid)
                        if time_now > (start + 60.0):
                            starttime = time_now
                        else:
                            starttime = start + 60.0
                        duration = stop - starttime - 10.0
                        #print starttime, duration
                        rbc = RecordBeamletStatistics(_obsid, starttime, duration)
                        obs_info[_obsid]['beamlet-recording'] = rbc
                        obs_info[_obsid]['beamlet-recording'].start()
                        obs_info[_obsid]['next-check-time'] = starttime
                        obs_info[_obsid]['last-check-time'] = stop - 15.0
                        obs_info[_obsid]['samples'] = 0
                        #print str(obs_info[_obsid])

            # close finished obsids
            for _obsid in obs_info_to_delete:
                if obs_info[_obsid]['state'] == 'finished':
                    del obs_info[_obsid]
            obs_info_to_delete = []

            # mark stopped obsids as stopped
            for _obsid in obs_info.keys():
                if not _obsid in obsids:
                    obs_info[_obsid]['state'] = 'stopped'
                    obs_info_to_delete.append(_obsid)

            check_now = False
            for _obsid in obs_info.keys():
                if time_now >= obs_info[_obsid]['next-check-time']:
                    check_now = True

            if check_now:
                # observing, so check mode now
                rec_timestamp = time.time() + 3.0
                data.collect(n_seconds=1, slow=True)
                # data.fetch()

                for _obsid in obs_info.keys():
                    conf = TestSettings(filename=conf_file)
                    # finish stopped obsid, and stop recording if needed
                    if obs_info[_obsid]['state'] == 'stopped':
                        # dayinfo.add_obs_info(obs_id, obs_start_time, obs_stop_time, rcumode, obsid_samples)
                        # dayinfo.write_file()
                        obs_info[_obsid]['csv'].write_info(obs_info[_obsid]['starttime'],
                                                           obs_info[_obsid]['stoptime'],
                                                           obs_info[_obsid]['samples'])
                        obs_info[_obsid]['csv'].close_file()
                        if obs_info[_obsid]['beamlet-recording'].is_running():
                            obs_info[_obsid]['beamlet-recording'].kill_recording()
                            time.sleep(0.2)
                        if not obs_info[_obsid]['beamlet-recording'].is_running():
                            obs_info[_obsid]['state'] = 'finished'
                        continue  # finished, next obsid

                    if time_now > obs_info[_obsid]['last-check-time']:
                        continue

                    if time_now < obs_info[_obsid]['next-check-time']:
                        continue

                    obs_info[_obsid]['csv'].set_record_timestamp(rec_timestamp)
                    obs_info[_obsid]['samples'] += 1
                    logger.debug("do tests")

                    error_list = []

                    for band in AntennaData.bands:
                        if data.band_active(band):
                            # TODO: DI.add_sample(rcumode)
                            # mask = extract_select_str(conf.get_str('mask-band-%d' % band))
                            # data.mask_sb(mask)
                            # if len(mask) > 0:
                            #     logger.debug("mask=%s" %(str(mask)))
                            data.reset_masked_rcus()
                            masked_rcus = []
                            for i in range(n_rcus):
                                if not i in obs_info[_obsid]['rcus']:
                                    masked_rcus.append(i)
                            data.mask_rcu(masked_rcus)
                            # check rcumode of first rcu
                            mode = data.mode(obs_info[_obsid]['rcus'][0])
                            # do LBA tests
                            logger.debug("band= %s, mode= %d" % (band, mode))
                            if mode in (1, 2, 3, 4) and band in ('10_90', '30_90'):
                                settings = conf.rcumode(mode)
                                check_down(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_short(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_flat(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_oscillation(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_noise(data, band, error_list, settings, obs_info[_obsid]['csv'])

                            # do HBA tests
                            if mode in (5, 6, 7) and band in ('110_190', '170_210', '210_250'):
                                settings = conf.group('rcumode.%d.tile' % mode)
                                check_oscillation(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_summator_noise(data, band, error_list, settings, obs_info[_obsid]['csv'])
                                check_noise(data, band, error_list, settings, obs_info[_obsid]['csv'])

                    next_check_time = obs_info[_obsid]['next-check-time']
                    obs_info[_obsid]['next-check-time'] = next_check_time + 60.0
                    logger.debug("next check obsid %s on %s" %(_obsid, time.ctime(next_check_time + 60.0)))
                    #print str(obs_info[_obsid])

            if len(obs_info) == 0:
                # if not observing check every 30 seconds for observation start
                if sleep_counter == 0:
                    logger.debug("no observation, sleep mode activated")
                sleep_counter += 1
                if (sleep_counter % 60) == 0:
                    logger.debug("no observation, still sleeping")
                time.sleep(10.0)
            else:
                # if observing do check every 1 seconds
                sleep_counter = 0
                time.sleep(1.0)

        except KeyboardInterrupt:
            logger.info("stopped by user")
            return 0
        except:
            logger.error('Caught %s', str(sys.exc_info()[0]))
            logger.error(str(sys.exc_info()[1]))
            logger.error('TRACEBACK:\n%s', traceback.format_exc())
            logger.error('Aborting NOW')
            return 1

    # do test and write result files to log directory
    log_dir = conf.get_str('log-dir-local')
    if os.path.exists(log_dir):
        logger.info("write result data")
        # write result
    else:
        logger.warning("not a valid log directory")
    logger.info("Test ready.")

    # if still running kill recording
    if beamlet_recording:
        if beamlet_recording.is_running():
            beamlet_recording.kill_recording()

    # delete files from data directory
    remove_all_data_files()
    return 0

if __name__ == '__main__':
    sys.exit(main())
