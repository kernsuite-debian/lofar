#!/usr/bin/env python3

from copy import deepcopy
from .general import *
from .lofar import *
import time
import logging
import string

db_version = '0415'

logger = logging.getLogger('main.db')
logger.debug("starting db logger")


class DB:
    def __init__(self, StID, nRSP, nTBB, nLBL, nLBH, nHBA, HBA_SPLIT):
        self.StID = StID
        self.nr_rsp = nRSP
        self.nr_spu = nRSP // 4
        self.nr_rcu = nRSP * 8
        self.nr_lbl = nLBL
        self.nr_lbh = nLBH
        self.nr_hba = nHBA
        self.hba_split = HBA_SPLIT
        self.nr_tbb = nTBB

        self.script_versions = ''

        self.board_errors = list()
        self.rcumode = -1
        self.tests_done = list()
        self.check_start_time = 0
        self.check_stop_time = 0
        self.rsp_driver_down = False
        self.tbb_driver_down = False

        self.station_error = 0

        self.test_end_time = -1
        self.rcus_changes = False

        self.spu = list()
        for i in range(self.nr_spu):
            self.spu.append(self.SPU(i))

        self.rsp = list()
        for i in range(nRSP):
            self.rsp.append(self.RSP(i))

        self.tbb = list()
        for i in range(nTBB):
            self.tbb.append(self.TBB(i))

        self.rcu_state = list()
        for i in range(self.nr_rcu):
            self.rcu_state.append(0)

        self.lbl = deepcopy(self.LBA(label='LBL', nr_antennas=nLBL, nr_offset=48))
        self.lbh = deepcopy(self.LBA(label='LBH', nr_antennas=nLBH, nr_offset=0))
        self.hba = deepcopy(self.HBA(nr_tiles=nHBA, split=self.hba_split))

    def set_test_end_time(self, end_time):
        if end_time > time.time():
            self.test_end_time = end_time
        else:
            logger.warning("end time in past")
        return

    # returns True if before end time
    def check_end_time(self, duration=0.0):
        if self.test_end_time == -1:
            return True
        if (time.time() + duration) < self.test_end_time:
            return True
        else:
            return False

    # add only ones
    def add_test_done(self, name):
        if name not in self.tests_done:
            self.tests_done.append(name)

    # check if already done
    def is_test_done(self, name):
        if name in self.tests_done:
            return False
        return True

    # test
    def test(self):
        for _spu in self.spu:
            ok = _spu.test()
            if not ok:
                self.station_error = 1

        for _rsp in self.rsp:
            ok = _rsp.test()
            if not ok:
                self.station_error = 1

        for _tbb in self.tbb:
            ok = _tbb.test()
            if not ok:
                self.station_error = 1

        # test rcu's first
        for _rcu in range(self.nr_rcu):
            error_count = 0

            ant_nr = _rcu // 2
            pol_nr = _rcu % 2  # 0=X, 1=Y

            if pol_nr == 0:
                if self.nr_lbl > 0 and ant_nr < self.nr_lbl and self.lbl.ant[ant_nr].x.error:
                    error_count += 1
                if ant_nr < self.nr_lbh and self.lbh.ant[ant_nr].x.error:
                    error_count += 1
                if ant_nr < self.nr_hba and self.hba.tile[ant_nr].x.rcu_error:
                    error_count += 1
            else:
                if self.nr_lbl > 0 and ant_nr < self.nr_lbl and self.lbl.ant[ant_nr].y.error:
                    error_count += 1
                if ant_nr < self.nr_lbh and self.lbh.ant[ant_nr].y.error:
                    error_count += 1
                if ant_nr < self.nr_hba and self.hba.tile[ant_nr].y.rcu_error:
                    error_count += 1

            if error_count >= 2:
                self.rcu_state[_rcu] = 1

        self.station_error = max(self.station_error, self.lbl.test(), self.lbh.test(), self.hba.test())

        return self.station_error


    # =======================================================================================================================
    # database from here
    class SPU:
        def __init__(self, nr):
            self.nr = nr
            self.rcu_5_0_volt = 0.0
            self.lba_8_0_volt = 0.0
            self.hba_48_volt = 0.0
            self.spu_3_3V = 0.0
            self.rcu_ok = 1
            self.lba_ok = 1
            self.hba_ok = 1
            self.spu_ok = 1
            self.voltage_ok = 1
            self.temp = 0.0
            self.temp_ok = 1

        def test(self):
            self.voltage_ok = 0
            if self.rcu_ok and self.lba_ok and self.hba_ok and self.spu_ok:
                self.voltage_ok = 1
            return self.voltage_ok

    class RSP:
        def __init__(self, nr):
            self.nr = nr

            self.test_done = 0
            self.board_ok = 1
            self.ap_version = 'ok'
            self.bp_version = 'ok'
            self.version_ok = 1
            self.voltage1_2 = 0.0
            self.voltage2_5 = 0.0
            self.voltage3_3 = 0.0
            self.voltage_ok = 1
            self.pcb_temp = 0.0
            self.bp_temp = 0.0
            self.ap0_temp = 0.0
            self.ap1_temp = 0.0
            self.ap2_temp = 0.0
            self.ap3_temp = 0.0
            self.temp_ok = 1

        def test(self):
            if self.ap_version != 'ok' or self.bp_version != 'ok':
                self.version_ok = 0
            return self.version_ok and self.voltage_ok and self.temp_ok

    # used by LBA and HBA antenna class
    class Polarity:
        def __init__(self, rcu=None):
            self.rcu = rcu
            self.rcu_off = 0  # 0 = RCU on, 1 = RCU off
            self.rcu_error = 0

            # status variables 0|1
            self.error = 0  #
            self.too_low = 0  #
            self.too_high = 0  #
            self.low_noise = 0  #
            self.high_noise = 0  #
            self.jitter = 0  #
            self.osc = 0  #
            self.no_signal = 0  # signal below 2dB
            self.summator_noise = 0  #
            self.spurious = 0  #
            self.flat = 0  #
            self.short = 0  #

            # test result of signal test,
            # only for HBA element test, first value ctrl=129 second value ctrl=253
            self.rf_test_subband = [0, 0]
            self.rf_ref_signal = [-1, -1]
            self.test_signal = [0.0, 0.0]

            # for down test
            self.down_pwr = 0.0
            self.down_offset = 0

            # measured values filled on error
            # proc : bad time in meausured time 0..100%
            # val  : max or min meausured value
            self.low_seconds = 0
            self.low_bad_seconds = 0
            self.low_val = 100.0  #
            self.low_diff = 0.0
            self.low_ref = 0.0  #

            self.high_seconds = 0
            self.high_bad_seconds = 0
            self.high_val = 0.0  #
            self.high_diff = 0.0
            self.high_ref = 0.0  #

            self.jitter_seconds = 0
            self.jitter_bad_seconds = 0
            self.jitter_val = 0.0
            self.jitter_ref = 0.0

            self.flat_val = 0.0
            self.short_val = 0.0

    class LBA:
        def __init__(self, label, nr_antennas, nr_offset=0):
            self.rsp_driver_down = False
            self.noise_check_done = 0
            self.signal_check_done = 0
            self.short_check_done = 0
            self.flat_check_done = 0
            self.down_check_done = 0
            self.spurious_check_done = 0
            self.oscillation_check_done = 0

            self.noise_low_deviation = 0.0
            self.noise_high_deviation = 0.0
            self.noise_max_fluctuation = 0.0

            self.rf_low_deviation = 0.0
            self.rf_high_deviation = 0.0
            self.rf_subband = 0

            self.check_time_noise = 0
            self.nr_antennas = nr_antennas
            self.nr_offset = nr_offset
            self.label = label
            self.error = 0
            self.rf_signal_to_low = 0
            self.avg_x = 0
            self.avg_y = 0
            self.rf_test_subband_x = 0
            self.rf_test_subband_y = 0
            self.rf_ref_signal_x = 0
            self.rf_ref_signal_y = 0
            self.nr_bad_antennas = -1
            self.ant = list()
            for i in range(self.nr_antennas):
                self.ant.append(self.Antenna(i, self.nr_offset))
            return

        def test(self):
            if self.rsp_driver_down:
                return self.error
            if self.noise_check_done or self.signal_check_done or self.short_check_done or \
                    self.flat_check_done or self.down_check_done or self.signal_check_done or \
                    self.spurious_check_done or self.oscillation_check_done:
                self.nr_bad_antennas = 0

            for ant in self.ant:
                ant.test()
                ant_error = max(ant.x.error, ant.y.error)
                self.error = max(self.error, ant_error)
                if ant_error:
                    self.nr_bad_antennas += 1
            return self.error

        # return select string for rspctl command
        def select_list(self):
            select = list()
            for ant in self.ant:
                if ant.on_bad_list == 0:
                    select.append(ant.x.rcu)
                    select.append(ant.y.rcu)
            return select

        def reset_rcu_state(self):
            for ant in self.ant:
                ant.x.rcu_off = 0
                ant.y.rcu_off = 0

        class Antenna:
            def __init__(self, nr, nr_offset):
                self.nr = nr
                self.nr_pvss = self.nr + nr_offset
                self.on_bad_list = 0
                if nr_offset == 0:
                    self.x = DB.Polarity(rcu=(self.nr * 2))
                    self.y = DB.Polarity(rcu=((self.nr * 2) + 1))
                else:
                    self.x = DB.Polarity(rcu=(self.nr * 2) + 1)
                    self.y = DB.Polarity(rcu=((self.nr * 2)))
                self.down = 0
                return

            def test(self):
                self.x.error = max(self.x.too_low, self.x.too_high, self.x.osc, self.x.high_noise, self.x.low_noise,
                                   self.x.jitter, self.x.spurious, self.down, self.x.flat, self.x.short)
                self.y.error = max(self.y.too_low, self.y.too_high, self.y.osc, self.y.high_noise, self.y.low_noise,
                                   self.y.jitter, self.y.spurious, self.down, self.y.flat, self.y.short)
                return

    class HBA:
        def __init__(self, nr_tiles, split):
            self.rsp_driver_down = False
            self.modem_check_done = 0
            self.noise_check_done = 0
            self.signal_check_done = 0
            self.spurious_check_done = 0
            self.oscillation_check_done = 0
            self.summatornoise_check_done = 0
            self.element_check_done = 0

            self.hba_split = split
            self.check_time_noise = 0
            self.check_time_noise_elements = 0
            self.nr_tiles = nr_tiles
            self.error = 0
            self.rf_signal_to_low = 0
            # only used for tile RF test
            # first value ctrl=129 second value ctrl=253
            self.rf_test_subband_x = [0, 0]
            self.rf_test_subband_y = [0, 0]
            self.rf_ref_signal_x = [0.0, 0.0]
            self.rf_ref_signal_y = [0.0, 0.0]
            self.tile = list()
            self.nr_bad_tiles = -1
            self.nr_bad_tiles_0 = -1
            self.nr_bad_tiles_1 = -1
            for i in range(self.nr_tiles):
                self.tile.append(self.Tile(i))
            return

        def test(self):
            if self.rsp_driver_down:
                return self.error
            if self.modem_check_done or self.noise_check_done or self.signal_check_done or self.spurious_check_done or\
                    self.oscillation_check_done or self.summatornoise_check_done or self.element_check_done:
                if self.hba_split == 1:
                    self.nr_bad_tiles_0 = 0
                    self.nr_bad_tiles_1 = 0
                else:
                    self.nr_bad_tiles = 0

            for tile in self.tile:
                tile.test(self.element_check_done or self.modem_check_done)
                tile_error = max(tile.x.error, tile.y.error)
                self.error = max(self.error, tile_error)

                if tile_error:
                    if self.hba_split == 1:
                        if tile.nr < 24:
                            self.nr_bad_tiles_0 += 1
                        else:
                            self.nr_bad_tiles_1 += 1
                    else:
                        self.nr_bad_tiles += 1
            return self.error

        # return select string for rspctl command
        def select_list(self):
            select = list()
            for tile in self.tile:
                if tile.on_bad_list == 0:
                    select.append(tile.x.rcu)
                    select.append(tile.y.rcu)
            return select

        def reset_rcu_state(self):
            for tile in self.tile:
                tile.x.rcu_off = 0
                tile.y.rcu_off = 0

        class Tile:
            def __init__(self, nr):
                self.nr = nr
                self.on_bad_list = 0
                self.x = DB.Polarity(rcu=(nr * 2))
                self.y = DB.Polarity(rcu=(nr * 2 + 1))

                self.noise_low_deviation = 0.0
                self.noise_high_deviation = 0.0
                self.noise_max_fluctuation = 0.0

                self.rf_low_deviation = 0.0
                self.rf_high_deviation = 0.0
                self.rf_subband = 0

                self.no_power = 0  # signal around 60dB
                self.p_summator_error = 0
                self.c_summator_error = 0
                self.nr_elements = 16
                self.element = list()
                for i in range(1, self.nr_elements + 1, 1):
                    self.element.append(self.Element(i))
                return

            def test(self, check_done):
                no_modem_cnt = 0
                modem_err_cnt = 0
                no_power_cnt = 0
                x_no_signal_cnt = 0
                y_no_signal_cnt = 0
                if check_done:
                    for elem in self.element:
                        elem.test()
                        if elem.x.no_signal:
                            x_no_signal_cnt += 1
                        if elem.y.no_signal:
                            y_no_signal_cnt += 1
                        if elem.no_power:
                            no_power_cnt += 1
                        if elem.no_modem:
                            no_modem_cnt += 1
                        if elem.modem_error:
                            modem_err_cnt += 1

                        self.x.error = max(self.x.error, elem.x.error)
                        self.y.error = max(self.y.error, elem.y.error)

                if (no_modem_cnt >= 8) or (modem_err_cnt >= 8):
                    self.c_summator_error = 1
                if no_power_cnt >= 15:
                    self.p_summator_error = 1
                if x_no_signal_cnt == 16:
                    self.x.rcu_error = 1
                if y_no_signal_cnt == 16:
                    self.y.rcu_error = 1

                self.x.error = max(self.x.error, self.x.too_low, self.x.too_high, self.x.low_noise, self.x.no_signal,
                                   self.x.high_noise, self.x.jitter, self.x.osc,
                                   self.x.summator_noise, self.x.spurious, self.p_summator_error, self.c_summator_error)

                self.y.error = max(self.y.error, self.y.too_low, self.y.too_high, self.y.low_noise, self.y.no_signal,
                                   self.y.high_noise, self.y.jitter, self.y.osc,
                                   self.y.summator_noise, self.y.spurious, self.p_summator_error, self.c_summator_error)
                return

            class Element:
                def __init__(self, nr):
                    self.nr = nr
                    self.x = DB.Polarity()
                    self.y = DB.Polarity()

                    self.noise_low_deviation = 0.0
                    self.noise_high_deviation = 0.0
                    self.noise_max_fluctuation = 0.0

                    self.rf_low_deviation = 0.0
                    self.rf_high_deviation = 0.0
                    self.rf_subband = 0

                    self.no_power = 0  # signal around 60dB
                    self.no_modem = 0  # modem reponse = ??
                    self.modem_error = 0  # wrong response from modem

                    return

                def test(self):
                    modem_err = 0
                    if self.no_modem or self.modem_error:
                        modem_err = 1

                    self.x.error = max(self.x.too_low, self.x.too_high, self.x.low_noise, self.x.high_noise,
                                       self.x.no_signal,
                                       self.x.jitter, self.no_power, self.x.spurious, self.x.osc, modem_err)

                    self.y.error = max(self.y.too_low, self.y.too_high, self.y.low_noise, self.y.high_noise,
                                       self.y.no_signal,
                                       self.y.jitter, self.no_power, self.y.spurious, self.y.osc, modem_err)
                    return

    class TDS:
        def __init__(self):
            self.test_done = 0
            self.ok = 1

    class TBB:
        def __init__(self, nr):
            self.nr = nr
            self.board_active = 1
            self.board_ok = 1
            self.test_done = 0
            self.tp_version = 'ok'
            self.mp_version = 'ok'
            self.memory_size = 0
            self.version_ok = 1
            self.memory_ok = 1
            self.voltage1_2 = 0.0
            self.voltage2_5 = 0.0
            self.voltage3_3 = 0.0
            self.voltage_ok = 1
            self.pcb_temp = 0.0
            self.tp_temp = 0.0
            self.mp0_temp = 0.0
            self.mp1_temp = 0.0
            self.mp2_temp = 0.0
            self.mp3_temp = 0.0
            self.temp_ok = 1

        def test(self):
            if self.tp_version != 'ok' or self.mp_version != 'ok':
                self.version_ok = 0
            if self.memory_size != 0:
                self.memory_ok = 0
            return self.version_ok and self.voltage_ok and self.temp_ok
