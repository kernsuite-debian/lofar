import logging
from .data import AntennaData
from .spectrum_checks import *
from .lofar import *

logger = logging.getLogger('main.lba')
logger.debug("starting lba logger")

# class for testing LBA antennas
class LBA(object):
    def __init__(self, db, lba):
        self.db = db
        self.lba = None
        if lba.upper() == 'LBL':
            self.lba = db.lbl
        if lba.upper() == 'LBH':
            self.lba = db.lbh

        self.antenna_data = AntennaData({'n_rcus': self.lba.nr_antennas * 2, 'data-dir': data_dir()})
        self.db.rcus_changed = False

        # Average normal value = 150.000.000 (81.76 dBm) -3dB +3dB
        # LOW/HIGH LIMIT is used for calculating mean value
        self.lowLimit = -3.0  # dB
        self.highLimit = 3.0  # dB

        # MEAN LIMIT is used to check if mean of all antennas is ok
        self.meanLimit = 66.0  # dB

    def reset(self):
        self.db.rcus_changed = False

    def turn_off_ant(self, ant_nr):
        ant = self.lba.ant[ant_nr]
        ant.x.rcu_off = 1
        ant.y.rcu_off = 1
        logger.info("turned off antenna %d RCU(%d,%d)" % (ant.nr_pvss, ant.x.rcu, ant.y.rcu))
        rspctl("--rcumode=0 --select=%d,%d" % (ant.x.rcu, ant.y.rcu), wait=2.0)
        rspctl("--rcuenable=0 --select=%d,%d" % (ant.x.rcu, ant.y.rcu), wait=2.0)
        self.db.rcus_changed = True
        return

    def set_mode(self, mode):
        if self.db.rcumode != mode:
            self.db.rcumode = mode
            turn_off_rcus()
            turn_on_rcus(mode=mode, rcus=self.lba.select_list())
            self.lba.reset_rcu_state()

    def record_data(self, rec_time, new_data=False):
        if new_data or self.db.rcus_changed or self.antenna_data.seconds() < rec_time:
            self.db.rcus_changed = False
            logger.debug('record info changed')
            self.antenna_data.collect(n_seconds=rec_time)
            for ant in self.lba.ant:
                if ant.x.rcu_off or ant.y.rcu_off:
                    self.antenna_data.mask_rcu([ant.x.rcu, ant.y.rcu])

    # check for oscillating tiles and turn off RCU
    # stop one RCU each run
    def check_oscillation(self, mode, parset):
        logger.info("=== Start %s oscillation test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=28.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        band = mode_to_band(mode)

        clean = False
        while not clean:
            if not self.db.check_end_time(duration=18.0):
                logger.warning("check stopped, end time reached")
                return

            clean = True
            self.record_data(rec_time=3, new_data=True)


            for pol in ('X', 'Y'):
                # result is a sorted list on maxvalue
                result = check_for_oscillation(data=self.antenna_data, band=band, pol=pol, parset=parset)
                if len(result) > 1:
                    clean = False
                    rcu, peaks_sum, n_peaks, ant_low = sorted(result[1:], reverse=True)[0]  # result[1]
                    ant = rcu // 2
                    logger.info("RCU %d LBA %d Oscillation sum=%3.1f peaks=%d low=%3.1fdB" % (
                        rcu, self.lba.ant[ant].nr_pvss, peaks_sum, n_peaks, ant_low))
                    self.turn_off_ant(ant)
                    if pol == 'X':
                        self.lba.ant[ant].x.osc = 1
                    else:
                        self.lba.ant[ant].y.osc = 1

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.oscillation_check_done = 1
        self.db.add_test_done('O%d' % mode)
        logger.info("=== Done %s oscillation test ===" % self.lba.label)
        return

    def check_noise(self, mode, record_time, parset):
        logger.info("=== Start %s noise test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=(record_time + 100.0)):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        band = mode_to_band(mode)

        for ant in self.lba.ant:
            if ant.x.rcu_off or ant.y.rcu_off:
                logger.info("skip low-noise test for antenna %d, RCUs turned off" % ant.nr)

        self.record_data(rec_time=record_time)

        # result is a sorted list on maxvalue
        low_noise, high_noise, jitter = check_for_noise(data=self.antenna_data, band=band, pol='XY', parset=parset)

        for n in low_noise:
            rcu, val, bad_secs, ref, diff = n
            ant = rcu // 2
            if self.lba.ant[ant].x.rcu_off or self.lba.ant[ant].y.rcu_off:
                continue
            # self.turnOffAnt(ant)
            logger.info("RCU %d Ant %d Low-Noise value=%3.1f bad=%d(%d) limit=%3.1f diff=%3.3f" % (
                rcu, self.lba.ant[ant].nr_pvss, val, bad_secs, self.antenna_data.seconds(), ref, diff))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                antenna = self.lba.ant[ant].x
            else:
                antenna = self.lba.ant[ant].y

            antenna.low_seconds += self.antenna_data.seconds()
            antenna.low_bad_seconds += bad_secs
            if val < self.lba.ant[ant].x.low_val:
                antenna.low_noise = 1
                antenna.low_val = val
                antenna.low_ref = ref
                antenna.low_diff = diff

        for n in high_noise:
            rcu, val, bad_secs, ref, diff = n
            ant = rcu // 2
            # self.turnOffAnt(ant)
            logger.info("RCU %d Ant %d High-Noise value=%3.1f bad=%d(%d) ref=%3.1f diff=%3.1f" % (
                rcu, self.lba.ant[ant].nr_pvss, val, bad_secs, self.antenna_data.seconds(), ref, diff))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                antenna = self.lba.ant[ant].x
            else:
                antenna = self.lba.ant[ant].y

            antenna.high_seconds += self.antenna_data.seconds()
            antenna.high_bad_seconds += bad_secs
            if val > self.lba.ant[ant].x.high_val:
                antenna.high_noise = 1
                antenna.high_val = val
                antenna.high_ref = ref
                antenna.high_diff = diff

        for n in jitter:
            rcu, val, ref, bad_secs = n
            ant = rcu // 2
            logger.info("RCU %d Ant %d Jitter, fluctuation=%3.1fdB  normal=%3.1fdB" % (
                rcu, self.lba.ant[ant].nr_pvss, val, ref))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                antenna = self.lba.ant[ant].x
            else:
                antenna = self.lba.ant[ant].y

            antenna.jitter_seconds += self.antenna_data.seconds()
            antenna.jitter_bad_seconds += bad_secs
            if val > antenna.jitter_val:
                antenna.jitter = 1
                antenna.jitter_val = val
                antenna.jitter_ref = ref

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.noise_check_done = 1
        self.db.add_test_done('NS%d=%d' % (mode, record_time))
        logger.info("=== Done %s noise test ===" % self.lba.label)
        return

    def check_spurious(self, mode, parset):
        logger.info("=== Start %s spurious test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=12.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        self.record_data(rec_time=3)

        # result is a sorted list on maxvalue
        result = check_for_spurious(data=self.antenna_data, band=mode_to_band(mode), pol='XY', parset=parset)
        for rcu in result:
            ant = rcu // 2
            # self. turnOffAnt(ant)
            logger.info("RCU %d Ant %d pol %s Spurious" % (
                rcu, self.lba.ant[ant].nr_pvss, self.antenna_data.polarity(rcu)))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                self.lba.ant[ant].x.spurious = 1
            else:
                self.lba.ant[ant].y.spurious = 1

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.spurious_check_done = 1
        self.db.add_test_done('SP%d' % mode)
        logger.info("=== Done %s spurious test ===" % self.lba.label)
        return

    def check_short(self, mode, parset):
        logger.info("=== Start %s Short test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=15.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        band = mode_to_band(mode)
        self.record_data(rec_time=3)

        # search for shorted cable (input), mean signal all subbands between 55 and 61 dB
        logger.debug("Check Short")
        short = check_for_short(data=self.antenna_data, band=band, parset=parset)
        for i in short:
            rcu, mean_val = i
            ant = rcu // 2

            logger.info("%s %2d RCU %3d Short, mean value band=%5.1fdB" % (
                self.lba.label, self.lba.ant[ant].nr_pvss, rcu, mean_val))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                self.lba.ant[ant].x.short = 1
                self.lba.ant[ant].x.short_val = mean_val
            else:
                self.lba.ant[ant].y.short = 1
                self.lba.ant[ant].y.short_val = mean_val

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.short_check_done = 1
        self.db.add_test_done('SH%d' % mode)
        logger.info("=== Done %s Short test ===" % self.lba.label)
        return

    def check_flat(self, mode, parset):
        logger.info("=== Start %s Flat test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=15.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        band = mode_to_band(mode)

        self.record_data(rec_time=3)

        # search for flatliners, mean signal all subbands between 63 and 65 dB
        logger.debug("Check Flat")
        flat = check_for_flat(data=self.antenna_data, band=band, parset=parset)
        for i in flat:
            rcu, mean_val = i
            ant = rcu // 2

            logger.info("%s %2d RCU %3d Flat, mean value band=%5.1fdB" % (
                self.lba.label,
                self.lba.ant[ant].nr_pvss,
                rcu,
                mean_val))

            self.antenna_data.mask_rcu(rcu)
            if self.antenna_data.polarity(rcu) == self.antenna_data.XYPOL:
                self.lba.ant[ant].x.flat = 1
                self.lba.ant[ant].x.flat_val = mean_val
            else:
                self.lba.ant[ant].y.flat = 1
                self.lba.ant[ant].y.flat_val = mean_val

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.flat_check_done = 1
        self.db.add_test_done('F%d' % mode)
        logger.info("=== Done %s Flat test ===" % self.lba.label)
        return

    def check_down(self, mode, parset):
        logger.info("=== Start %s Down test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=15.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        self.record_data(rec_time=3)

        # mark lba as down if top of band is lower than normal and top is shifted more than 10 subbands to left or right
        logger.debug("Check Down")
        down, shifted = check_for_down(data=self.antenna_data, band=mode_to_band(mode), parset=parset)
        #logger.debug("down_info=%s" % str(down))

        for rcu, max_sb, max_val, max_bw, band_pwr in down:
            if rcu == 'Xref':
                x_ref_max_sb = max_sb
                x_ref_max_val = max_val
                x_ref_max_bw = max_bw
                x_ref_band_pwr = band_pwr
                logger.info("down test X rcus's median values: sb=%d, pwr=%3.1fdB, bw=%d, band-pwr=%3.1fdB" % (
                            x_ref_max_sb, x_ref_max_val, x_ref_max_bw, x_ref_band_pwr))
                continue
            if rcu == 'Yref':
                y_ref_max_sb = max_sb
                y_ref_max_val = max_val
                y_ref_max_bw = max_bw
                y_ref_band_pwr = band_pwr
                logger.info("down test Y rcu's median values: sb=%d, pwr=%3.1fdB, bw=%d, band-pwr=%3.1fdB" % (
                            y_ref_max_sb, y_ref_max_val, y_ref_max_bw, y_ref_band_pwr))
                continue

            max_offset = 292 - max_sb
            ant = rcu // 2

            if self.lba.ant[ant].x.flat or self.lba.ant[ant].x.short or \
                    self.lba.ant[ant].y.flat or self.lba.ant[ant].y.short:
                continue
            if self.antenna_data.polarity(rcu) == self.antenna_data.XPOL:
                self.lba.ant[ant].x.down_pwr    = max_val
                self.lba.ant[ant].x.down_offset = max_offset
                self.lba.ant[ant].down = 1
            else:
                self.lba.ant[ant].y.down_pwr    = max_val
                self.lba.ant[ant].y.down_offset = max_offset
                self.lba.ant[ant].down = 1

            self.antenna_data.mask_rcu([self.lba.ant[ant].x.rcu, self.lba.ant[ant].y.rcu])

        for a in range(self.lba.nr_antennas):
            if self.lba.ant[a].down:
                logger.info("%s %2d RCU %3d/%3d Down, Xoffset=%d Yoffset=%d" % (
                    self.lba.label, self.lba.ant[a].nr_pvss,
                    self.lba.ant[a].x.rcu, self.lba.ant[a].y.rcu,
                    self.lba.ant[a].x.down_offset, self.lba.ant[a].y.down_offset))

        for i in shifted:
            rcu, max_sb, mean_max_sb = i
            ant = rcu // 2
            logger.info("%s %2d RCU %3d shifted top on sb=%d, normal=sb%d" % (
                self.lba.label, self.lba.ant[ant].nr_pvss, rcu, max_sb, mean_max_sb))

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.down_check_done = 1
        self.db.add_test_done('D%d' % mode)
        logger.info("=== Done %s Down test ===" % self.lba.label)
        return

    def check_rf_power(self, mode, parset):
        logger.info("=== Start %s RF test ===" % self.lba.label)
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=15.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)
        self.record_data(rec_time=2)

        test_info_x, signal_info_x = check_rf_power(data=self.antenna_data, band=mode_to_band(mode),
                                                     pol='X', parset=parset)
        logger.debug("X data:  test subband=%d,  median val=%5.3f" % (test_info_x['subband'], test_info_x['test_val']))

        test_info_y, signal_info_y = check_rf_power(data=self.antenna_data, band=mode_to_band(mode),
                                                     pol='Y', parset=parset)
        logger.debug("Y data:  test subband=%d,  median val=%5.3f" % (test_info_y['subband'], test_info_y['test_val']))

        # logger.debug("signal_info_x=%s" % str(signal_info_x))
        # logger.debug("signal_info_y=%s" % str(signal_info_y))

        self.lba.rf_ref_signal_y = test_info_y['test_val']
        self.lba.rf_ref_signal_x = test_info_x['test_val']
        self.lba.rf_test_subband_x = test_info_x['subband']
        self.lba.rf_test_subband_y = test_info_y['subband']

        rcu_list = self.antenna_data.rcus(mode_to_band(mode), 'XY')
        if test_info_x['valid'] and test_info_y['valid']:
            for ant in self.lba.ant:
                if ant.x.rcu_off or ant.y.rcu_off:
                    continue

                if str(ant.x.rcu) in signal_info_x:
                    ant.x.test_signal = signal_info_x[str(ant.x.rcu)]['value']
                    if signal_info_x[str(ant.x.rcu)]['status'] == 'no_signal':
                        ant.x.no_signal = 1
                    elif signal_info_x[str(ant.x.rcu)]['status'] == 'no_power':
                        ant.no_power = 1
                    elif signal_info_x[str(ant.x.rcu)]['status'] == 'low':
                        ant.x.too_low = 1
                    elif signal_info_x[str(ant.x.rcu)]['status'] == 'high':
                        ant.x.too_high = 1

                if str(ant.y.rcu) in signal_info_y:
                    ant.y.test_signal = signal_info_y[str(ant.y.rcu)]['value']
                    if signal_info_y[str(ant.y.rcu)]['status'] == 'no_signal':
                        ant.y.no_signal = 1
                    elif signal_info_y[str(ant.y.rcu)]['status'] == 'no_power':
                        ant.no_power = 1
                    elif signal_info_y[str(ant.y.rcu)]['status'] == 'low':
                        ant.y.too_low = 1
                    elif signal_info_y[str(ant.y.rcu)]['status'] == 'high':
                        ant.y.too_high = 1

                if str(ant.x.rcu) in signal_info_x and str(ant.y.rcu) in signal_info_y:
                    if signal_info_x[str(ant.x.rcu)]['status'] != 'normal' or \
                            signal_info_y[str(ant.y.rcu)]['status'] != 'normal':
                        logger.info("LBA Ant=%d:  X=%3.1fdB(%s)  Y=%3.1fdB(%s)" % (
                                     ant.nr,
                                     signal_info_x[str(ant.x.rcu)]['value'],
                                     signal_info_x[str(ant.x.rcu)]['status'],
                                     signal_info_y[str(ant.y.rcu)]['value'],
                                     signal_info_y[str(ant.y.rcu)]['status']))
        else:
            logger.warning("LBA, No valid test signal")
            self.lba.rf_signal_to_low = 1

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.lba.signal_check_done = 1
        self.db.add_test_done('S%d' % mode)
        logger.info("=== Done %s RF test ===" % self.lba.label)
        return

        # end of cLBA class
