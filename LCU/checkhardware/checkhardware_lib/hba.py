import logging
from .data import AntennaData
from .spectrum_checks import *
from .lofar import *

logger = logging.getLogger('main.hba')
logger.debug("starting hba logger")

# class for testing HBA antennas
class HBA(object):
    def __init__(self, db):
        self.db = db
        self.hba = db.hba
        self.antenna_data = AntennaData({'n_rcus': self.hba.nr_tiles * 2, 'data-dir': data_dir()})
        self.rcumode = 0

    def reset(self):
        self.db.rcus_changed = False

    def turn_on_tiles(self):
        pass

    def turn_off_tile(self, tile_nr):
        tile = self.hba.tile[tile_nr]
        tile.x.rcu_off = 1
        tile.y.rcu_off = 1
        logger.info("turned off tile %d RCU(%d,%d)" % (tile.nr, tile.x.rcu, tile.y.rcu))
        rspctl("--rcumode=0 --select=%d,%d" % (tile.x.rcu, tile.y.rcu), wait=2.0)
        self.db.rcus_changed = True
        return

    def turn_off_bad_tiles(self):
        for tile in self.hba.tile:
            if tile.x.rcu_off and tile.y.rcu_off:
                continue
            no_modem = 0
            modem_error = 0
            for elem in tile.element:
                if elem.no_modem:
                    no_modem += 1
                if elem.modem_error:
                    modem_error += 1
            if tile.x.osc or tile.y.osc or (no_modem >= 8) or (modem_error >= 8):
                self.turn_off_tile(tile.nr)
        return

    def set_mode(self, mode):
        if self.db.rcumode != mode:
            self.db.rcumode = mode
            turn_off_rcus()
            turn_on_rcus(mode=mode, rcus=self.hba.select_list())
            self.hba.reset_rcu_state()

    def record_data(self, rec_time, new_data=False):
        if new_data or self.db.rcus_changed or self.antenna_data.seconds() < rec_time:
            logger.debug('record info changed')
            self.db.rcus_changed = False
            self.antenna_data.collect(n_seconds=rec_time)
            for tile in self.hba.tile:
                if tile.x.rcu_off or tile.y.rcu_off:
                    self.antenna_data.mask_rcu([tile.x.rcu, tile.y.rcu])


    def check_modem(self, mode):
        # setup internal test db
        n_elements = 16
        n_tests = 7
        modem_tst = list()
        for tile_nr in range(self.db.nr_hba):
            tile = list()
            for elem_nr in range(n_elements):
                test = list()
                for tst_nr in range(n_tests):
                    test.append([0, 0])
                tile.append(test)
            modem_tst.append(tile)
        # done

        logger.info("=== Start HBA modem test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=50.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        time.sleep(4.0)
        ctrlstr = list()
        ctrlstr.append(('129,' * 16)[:-1])  # 0ns
        ctrlstr.append(('133,' * 16)[:-1])  # 0.5ns
        ctrlstr.append(('137,' * 16)[:-1])  # 1ns
        ctrlstr.append(('145,' * 16)[:-1])  # 2ns
        ctrlstr.append(('161,' * 16)[:-1])  # 4ns
        ctrlstr.append(('193,' * 16)[:-1])  # 8ns
        ctrlstr.append(('253,' * 16)[:-1])  # 15.5ns
        # rsp_hba_delay(delay=ctrlstr[6], rcus=self.hba.selectList(), discharge=False)
        tst_nr = 0
        for ctrl in ctrlstr:

            rsp_hba_delay(delay=ctrl, rcus=self.hba.select_list(), discharge=False)
            #data = rspctl('--realdelays', wait=1.0).splitlines()
            data = rspctl('--realdelays', wait=0.0).splitlines()

            ctrllist = ctrl.split(',')
            for line in data:
                if line[:3] == 'HBA':
                    rcu = int(line[line.find('[') + 1:line.find(']')])
                    hba_nr = rcu // 2
                    if hba_nr >= self.hba.nr_tiles:
                        continue
                    if self.hba.tile[hba_nr].on_bad_list:
                        continue
                    realctrllist = line[line.find('=') + 1:].strip().split()
                    for elem in self.hba.tile[hba_nr].element:
                        if ctrllist[elem.nr - 1] != realctrllist[elem.nr - 1]:
                            logger.info("Modemtest Tile=%d RCU=%d Element=%d ctrlword=%s response=%s" % (
                                         hba_nr, rcu, elem.nr, ctrllist[elem.nr - 1], realctrllist[elem.nr - 1]))

                            if realctrllist[elem.nr - 1].count('?') == 3:
                                # elem.no_modem += 1
                                modem_tst[hba_nr][elem.nr - 1][tst_nr][0] = 1
                            else:
                                # elem.modem_error += 1
                                modem_tst[hba_nr][elem.nr - 1][tst_nr][1] = 1
            tst_nr += 1
        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        # analyse test results and add to DB
        no_modem = dict()
        modem_error = dict()
        for tile_nr in range(self.db.nr_hba):
            n_no_modem = dict()
            n_modem_error = dict()
            for elem_nr in range(n_elements):
                n_no_modem[elem_nr] = 0
                n_modem_error[elem_nr] = 0
                for tst_nr in range(n_tests):
                    if modem_tst[tile_nr][elem_nr][tst_nr][0]:
                        n_no_modem[elem_nr] += 1
                    if modem_tst[tile_nr][elem_nr][tst_nr][1]:
                        n_modem_error[elem_nr] += 1
                no_modem[tile_nr] = n_no_modem
                modem_error[tile_nr] = n_modem_error

        n_tile_err = 0
        for tile in no_modem:
            n_elem_err = 0
            for elem in no_modem[tile]:
                if no_modem[tile][elem] == n_tests:
                    n_elem_err += 1
            if n_elem_err == n_elements:
                n_tile_err += 1

        if n_tile_err < (self.db.nr_hba // 2):
            for tile_nr in range(self.db.nr_hba):
                for elem_nr in range(n_elements):
                    #if no_modem[tile_nr][elem_nr] >= 2:  # 2 or more ctrl values went wrong
                    if no_modem[tile_nr][elem_nr]:  # 1 or more ctrl values went wrong
                        self.db.hba.tile[tile_nr].element[elem_nr].no_modem = 1

        n_tile_err = 0
        for tile in modem_error:
            n_elem_err = 0
            for elem in modem_error[tile]:
                if modem_error[tile][elem] == n_tests:
                    n_elem_err += 1
            if n_elem_err == n_elements:
                n_tile_err += 1

        if n_tile_err < (self.db.nr_hba // 2):
            for tile_nr in range(self.db.nr_hba):
                for elem_nr in range(n_elements):
                    #if no_modem[tile_nr][elem_nr] >= 2:  # 2 or more ctrl values went wrong
                    if no_modem[tile_nr][elem_nr]:  # 1 or more ctrl values went wrong
                        self.db.hba.tile[tile_nr].element[elem_nr].modem_error = 1

        self.hba.modem_check_done = 1
        self.db.add_test_done('M%d' % mode)
        logger.info("=== Done HBA modem test ===")
        # self.db.rcumode = 0
        return

    # check for summator noise and turn off RCU
    def check_summator_noise(self, mode, parset):
        logger.info("=== Start HBA tile based summator-noise test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=25.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        for delay_val in ('2','253'):
            delay_str = ','.join([delay_val] * 16)
            rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())

            self.record_data(rec_time=12)

            for pol_nr, pol in enumerate(('X', 'Y')):
                sum_noise = check_for_summator_noise(data=self.antenna_data, band=mode_to_band(mode),
                                                     pol=pol, parset=parset)
                for n in sum_noise:
                    rcu, cnt, n_peaks = n
                    tile = rcu // 2
                    logger.info("RCU %d Tile %d Summator-Noise delay-val=%s cnt=%3.1f peaks=%3.1f" % (
                        rcu, tile, delay_val, cnt, n_peaks))
                    if pol == 'X':
                        self.hba.tile[tile].x.summator_noise = 1
                    else:
                        self.hba.tile[tile].y.summator_noise = 1
                    self.turn_off_tile(tile)

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.summatornoise_check_done = 1
        self.db.add_test_done('SN%d' % mode)
        logger.info("=== Done HBA tile based summator-noise test ===")
        return

    # check for oscillating tiles and turn off RCU
    # stop one RCU each run
    def check_oscillation(self, mode, parset):
        logger.info("=== Start HBA tile based oscillation test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=35.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        delay_str = ('253,' * 16)[:-1]
        get_new_data = rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())

        clean = False
        while not clean:
            if not self.db.check_end_time(duration=25.0):
                logger.warning("check stopped, end time reached")
                return

            clean = True

            self.record_data(rec_time=12, new_data=get_new_data)

            for pol_nr, pol in enumerate(('X', 'Y')):
                # result is a sorted list on maxvalue
                result = check_for_oscillation(data=self.antenna_data, band=mode_to_band(mode), pol=pol, parset=parset)
                max_sum = n_peaks = 0
                if len(result) > 1:
                    if len(result) == 2:
                        rcu, max_sum, n_peaks, rcu_low = result[1]
                    else:
                        ref_low = result[0][3]
                        max_low_tile = (-1, -1)
                        max_sum_tile = (-1, -1)
                        for i in result[1:]:
                            rcu, max_sum, n_peaks, tile_low = i
                            # rcu = (tile * 2) + pol_nr
                            if max_sum > max_sum_tile[0]:
                                max_sum_tile = (max_sum, rcu)
                            if (tile_low - ref_low) > max_low_tile[0]:
                                max_low_tile = (tile_low, rcu)

                        rcu_low, rcu = max_low_tile

                    clean = False
                    get_new_data = True
                    tile = rcu // 2
                    # tile_polarity  = rcu % 2
                    # rcu = (tile * 2) + pol_nr
                    logger.info("RCU %d Tile %d Oscillation sum=%3.1f peaks=%d low=%3.1f" % (
                                 rcu, tile, max_sum, n_peaks, rcu_low))
                    self.turn_off_tile(tile)
                    if pol_nr == 0:
                        self.hba.tile[tile].x.osc = 1
                    else:
                        self.hba.tile[tile].y.osc = 1

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.oscillation_check_done = 1
        self.db.add_test_done('O%d' % mode)
        logger.info("=== Done HBA tile based oscillation test ===")
        return

    def check_noise(self, mode, record_time, parset):
        logger.info("=== Start HBA tile based noise test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=(record_time + 60.0)):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        for tile in self.hba.tile:
            if tile.x.rcu_off or tile.y.rcu_off:
                logger.info("skip low-noise test for tile %d, RCUs turned off" % tile.nr)

        delay_str = ('253,' * 16)[:-1]
        get_new_data = rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())

        self.record_data(rec_time=record_time, new_data=get_new_data)

        for pol_nr, pol in enumerate(('X', 'Y')):
            # result is a sorted list on maxvalue
            low_noise, high_noise, jitter = check_for_noise(data=self.antenna_data, band=mode_to_band(mode), pol=pol,
                                                            parset=parset)

            for n in low_noise:
                rcu, val, bad_secs, ref, diff = n
                tile = rcu // 2
                if self.hba.tile[tile].x.rcu_off or self.hba.tile[tile].y.rcu_off:
                    continue
                logger.info("RCU %d Tile %d Low-Noise value=%3.1f bad=%d(%d) limit=%3.1f diff=%3.3f" % (
                    rcu, tile, val, bad_secs, self.antenna_data.seconds(), ref, diff))

                if pol == 'X':
                    tile_polarity = self.hba.tile[tile].x
                else:
                    tile_polarity = self.hba.tile[tile].y

                tile_polarity.low_seconds += self.antenna_data.seconds()
                tile_polarity.low_bad_seconds += bad_secs
                if val < tile_polarity.low_val:
                    tile_polarity.low_noise = 1
                    tile_polarity.low_val = val
                    tile_polarity.low_ref = ref
                    tile_polarity.low_diff = diff

            for n in high_noise:
                rcu, val, bad_secs, ref, diff = n
                tile = rcu // 2
                logger.info("RCU %d Tile %d High-Noise value=%3.1f bad=%d(%d) limit=%3.1f diff=%3.1f" % (
                    rcu, tile, val, bad_secs, self.antenna_data.seconds(), ref, diff))

                if pol == 'X':
                    tile_polarity = self.hba.tile[tile].x
                else:
                    tile_polarity = self.hba.tile[tile].y

                tile_polarity.high_seconds += self.antenna_data.seconds()
                tile_polarity.high_bad_seconds += bad_secs
                if val > tile_polarity.high_val:
                    tile_polarity.high_noise = 1
                    tile_polarity.high_val = val
                    tile_polarity.high_ref = ref
                    tile_polarity.high_diff = diff

            for n in jitter:
                rcu, val, ref, bad_secs = n
                tile = rcu // 2
                logger.info("RCU %d Tile %d Jitter, fluctuation=%3.1fdB  normal=%3.1fdB" % (rcu, tile, val, ref))

                if pol == 'X':
                    tile_polarity = self.hba.tile[tile].x
                else:
                    tile_polarity = self.hba.tile[tile].y

                tile_polarity.jitter_seconds += self.antenna_data.seconds()
                tile_polarity.jitter_bad_seconds += bad_secs
                if val > tile_polarity.jitter_val:
                    tile_polarity.jitter = 1
                    tile_polarity.jitter_val = val
                    tile_polarity.jitter_ref = ref

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.noise_check_done = 1
        self.db.add_test_done('NS%d=%d' % (mode, record_time))
        logger.info("=== Done HBA tile based noise test ===")
        return

    def check_spurious(self, mode, parset):
        logger.info("=== Start HBA tile based spurious test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=12.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        delay_str = ('253,' * 16)[:-1]
        get_new_data = rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())

        self.record_data(rec_time=12, new_data=get_new_data)

        for pol_nr, pol in enumerate(('X', 'Y')):
            # result is a sorted list on maxvalue
            result = check_for_spurious(data=self.antenna_data, band=mode_to_band(mode), pol=pol, parset=parset)
            for rcu in result:
                tile = rcu // 2
                logger.info("RCU %d Tile %d pol %c Spurious" % (rcu, tile, pol))
                if pol == 'X':
                    self.hba.tile[tile].x.spurious = 1
                else:
                    self.hba.tile[tile].y.spurious = 1

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.spurious_check_done = 1
        self.db.add_test_done('SP%d' % mode)
        logger.info("=== Done HBA spurious test ===")
        return

    def check_rf_power(self, mode, parset):
        logger.info("=== Start HBA tile based RF test ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        if not self.db.check_end_time(duration=37.0):
            logger.warning("check stopped, end time reached")
            return

        self.set_mode(mode)

        # check twice
        # 2   ... check if all elements are turned off, normal value between 60.0 and 62.0
        # 128 ...
        # 253 ...
        for tile in self.hba.tile:
            if tile.x.rcu_off or tile.y.rcu_off:
                logger.debug("skip signal test for tile %d, RCUs turned off" % tile.nr)

        ctrl_2_subband = None

        for ctrl in ('128,', '253,', '2,'):
            if not self.db.check_end_time(duration=80.0):
                logger.warning("check stopped, end time reached")
                return

            ctrl_nr = -1
            if ctrl == '128,':
                ctrl_nr = 0
            elif ctrl == '253,':
                ctrl_nr = 1

            logger.debug("HBA signal test, ctrl word %s" % (ctrl[:-1]))

            delay_str = (ctrl * 16)[:-1]
            rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())


            check_for_valid_retries = 3
            record_time = 2
            while check_for_valid_retries > 0:
                self.record_data(rec_time=record_time, new_data=True)
                if ctrl_nr == -1:
                    parset.parset['rf']['subbands'] = str(ctrl_2_subband)

                logger.debug("subband=%s" % parset.parset['rf']['subbands'])
                test_info_x, signal_info_x = check_rf_power(data=self.antenna_data, band=mode_to_band(mode),
                                                             pol='X', parset=parset)
                test_info_y, signal_info_y = check_rf_power(data=self.antenna_data, band=mode_to_band(mode),
                                                             pol='Y', parset=parset)
                if ctrl_nr > -1:
                    if test_info_x['valid'] and test_info_y['valid']:
                        check_for_valid_retries = 0
                    else:
                        logger.warning("HBA, No valid test signal, try again")
                        check_for_valid_retries -= 1
                        record_time = 30
                else:
                    check_for_valid_retries = 0

            logger.debug("X data: control-word=%s,  test subband=%d,  median val=%5.3f" % (
                         ctrl[:-1], test_info_x['subband'], test_info_x['test_val']))

            logger.debug("Y data: control-word=%s,  test subband=%d,  median val=%5.3f" % (
                         ctrl[:-1], test_info_y['subband'], test_info_y['test_val']))

            if ctrl_nr > -1:
                ctrl_2_subband = test_info_x['subband']
                self.hba.rf_ref_signal_x[ctrl_nr] = test_info_x['test_val']
                self.hba.rf_ref_signal_y[ctrl_nr] = test_info_y['test_val']
                self.hba.rf_test_subband_x[ctrl_nr] = test_info_x['subband']
                self.hba.rf_test_subband_y[ctrl_nr] = test_info_y['subband']

                if test_info_x['valid'] and test_info_y['valid']:
                    for tile in self.hba.tile:
                        if tile.x.rcu_off or tile.y.rcu_off:
                            continue

                        if str(tile.x.rcu) in signal_info_x:
                            tile.x.test_signal[ctrl_nr] = signal_info_x[str(tile.x.rcu)]['value']

                            if signal_info_x[str(tile.x.rcu)]['status'] == 'no_signal':
                                tile.x.no_signal = 1
                            elif signal_info_x[str(tile.x.rcu)]['status'] == 'no_power':
                                tile.no_power = 1
                            elif signal_info_x[str(tile.x.rcu)]['status'] == 'low':
                                tile.x.too_low = 1
                            elif signal_info_x[str(tile.x.rcu)]['status'] == 'high':
                                tile.x.too_high = 1

                        if str(tile.y.rcu) in signal_info_y:
                            tile.y.test_signal[ctrl_nr] = signal_info_y[str(tile.y.rcu)]['value']

                            if signal_info_y[str(tile.y.rcu)]['status'] == 'no_signal':
                                tile.y.no_signal = 1
                            elif signal_info_y[str(tile.y.rcu)]['status'] == 'no_power':
                                tile.no_power = 1
                            elif signal_info_y[str(tile.y.rcu)]['status'] == 'low':
                                tile.y.too_low = 1
                            elif signal_info_y[str(tile.y.rcu)]['status'] == 'high':
                                tile.y.too_high = 1

                        if str(tile.x.rcu) in signal_info_x and str(tile.y.rcu) in signal_info_y:
                            if signal_info_x[str(tile.x.rcu)]['status'] != 'normal' or \
                                    signal_info_y[str(tile.y.rcu)]['status'] != 'normal':
                                logger.info("HBA Tile=%d: control-word=%s   X=%3.1fdB(%s)   Y=%3.1fdB(%s)" % (
                                             tile.nr,
                                             ctrl[:-1],
                                             signal_info_x[str(tile.x.rcu)]['value'],
                                             signal_info_x[str(tile.x.rcu)]['status'],
                                             signal_info_y[str(tile.y.rcu)]['value'],
                                             signal_info_y[str(tile.y.rcu)]['status']))
                else:
                    logger.warning("HBA, No valid test signal")
                    self.hba.rf_signal_to_low = 1
            else:
                # TODO: not valid, so no values, change spectrum_checks.py
                for tile in self.hba.tile:
                    if tile.x.rcu_off or tile.y.rcu_off:
                        continue
                    if str(tile.x.rcu) in signal_info_x:
                        if signal_info_x[str(tile.x.rcu)]['status'] in ('high',):
                            logger.warning("Tile %d rcu %d not switched off" % (tile.nr, tile.x.rcu))
                    if str(tile.y.rcu) in signal_info_y:
                        if signal_info_y[str(tile.y.rcu)]['status'] in ('high',):
                            logger.warning("Tile %d rcu %d not switched off" % (tile.nr, tile.y.rcu))

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.signal_check_done = 1
        self.db.add_test_done('S%d' % mode)
        logger.info("=== Done HBA signal test ===")
        return

    # Next tests are element based
    #
    # 8bit control word
    #
    # bit-7  RF on/off   1 = on
    # bit-6  delay       1 = 8 ns
    # bit-5  delay       1 = 4 ns
    # bit-4  delay       1 = 2 ns
    # bit-3  delay       1 = 1 ns
    # bit-2  delay       1 = 0.5 ns
    # bit-1  LNA on/off  1 = off
    # bit-0  LED on/off  1 = on
    #
    # control word = 0 (signal - 30 db)
    # control word = 2 (signal - 40 db)
    #
    def check_elements(self, mode, record_time, parset):

        logger.info("=== Start HBA element based tests ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        self.set_mode(mode)

        n_rcus_off = 0
        for ctrl in ('128', '253'):
            ctrl_nr = -1
            if ctrl == '128':
                ctrl_nr = 0
            elif ctrl == '253':
                ctrl_nr = 1

            parset.parset['ctrl-word'] = ctrl

            #logger.info("    check elements with ctrlword %s" % (ctrl))
            for elem in range(self.hba.tile[0].nr_elements):
                logger.info("    check elements %d with control-word %s" % ((elem + 1), ctrl))

                if not self.db.check_end_time(duration=45.0):
                    logger.warning("check stopped, end time reached")
                    return

                if n_rcus_off > 0:
                    rsp_rcu_mode(mode=mode, rcus=self.hba.select_list())
                    n_rcus_off = 0
                for tile in self.hba.tile:
                    if tile.element[elem].no_modem or tile.element[elem].modem_error:
                        self.turn_off_tile(tile.nr)
                        n_rcus_off += 1
                        logger.debug("skip tile %d, modem error" % tile.nr)

                delay_str = ('2,' * elem + ctrl + ',' + '2,' * 15)[:33]
                rsp_hba_delay(delay=delay_str, rcus=self.hba.select_list())

                clean = False
                while not clean:
                    if not self.db.check_end_time(duration=(record_time + 45.0)):
                        logger.warning("check stopped, end time reached")
                        return

                    self.record_data(rec_time=record_time, new_data=True)

                    clean, n_off = self.check_oscillation_elements(elem, parset)
                    n_rcus_off += n_off
                    if n_off > 0:
                        continue
                    n_off = self.check_spurious_elements(elem, parset)
                    n_rcus_off += n_off
                    if n_off > 0:
                        continue
                    self.check_noise_elements(elem, parset)
                    self.check_rf_power_elements(elem, ctrl_nr, parset)

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return

        self.hba.element_check_done = 1
        self.db.add_test_done('E%d' % mode)
        logger.info("=== Done HBA element tests ===")
        return

    # check for oscillating tiles and turn off RCU
    # stop one RCU each run
    # elem counts from 0..15 (for user output use 1..16)
    def check_oscillation_elements(self, elem, parset):
        logger.info("--- oscillation test --")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return
        clean = True
        n_rcus_off = 0
        # result is a sorted list on maxvalue
        result = check_for_oscillation(data=self.antenna_data, band=mode_to_band(self.db.rcumode), pol='XY',
                                       parset=parset)
        if len(result) > 1:
            clean = False
            rcu, peaks_sum, n_peaks, rcu_low = sorted(result[1:], reverse=True)[0]  # result[1]
            tile = rcu // 2
            if self.hba.tile[tile].element[elem].no_modem or self.hba.tile[tile].element[elem].modem_error:
                return True, 0
            tile_polarity = rcu % 2
            logger.info("%s RCU %d Tile %d Element %d Oscillation sum=%3.1f peaks=%d, low=%3.1f" % (
                         parset.as_string('ctrl-word'), rcu, tile, elem + 1, peaks_sum, n_peaks, rcu_low))
            self.turn_off_tile(tile)
            n_rcus_off += 1
            if tile_polarity == 0:
                self.hba.tile[tile].element[elem].x.osc = 1
            else:
                self.hba.tile[tile].element[elem].y.osc = 1
        return clean, n_rcus_off

    def check_spurious_elements(self, elem, parset):
        logger.info("--- spurious test ---")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return
        n_rcus_off = 0
        # result is a sorted list on maxvalue
        result = check_for_spurious(data=self.antenna_data, band=mode_to_band(self.db.rcumode), pol='XY',
                                    parset=parset)
        for rcu in result:
            tile = rcu // 2
            tile_polarity = rcu % 2
            logger.info("%s RCU %d Tile %d Element %d pol %d Spurious" % (parset.as_string('ctrl-word'), rcu, tile, elem + 1, tile_polarity))
            self.turn_off_tile(tile)
            n_rcus_off += 1
            if tile_polarity == 0:
                self.hba.tile[tile].element[elem].x.spurious = 1
            else:
                self.hba.tile[tile].element[elem].y.spurious = 1
        return n_rcus_off

    def check_noise_elements(self, elem, parset):
        logger.info("--- noise test ---")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return
        # result is a sorted list on maxvalue
        low_noise, high_noise, jitter = check_for_noise(data=self.antenna_data, band=mode_to_band(self.db.rcumode),
                                                        pol='XY', parset=parset)

        for n in low_noise:
            rcu, val, bad_secs, ref, diff = n
            tile = rcu // 2
            logger.info("%s RCU %d Tile %d Element %d Low-Noise value=%3.1f bad=%d(%d) limit=%3.1f diff=%3.3f" % (
                         parset.as_string('ctrl-word'), rcu, tile, elem + 1, val, bad_secs, self.antenna_data.seconds(), ref, diff))

            if rcu % 2 == 0:
                elem_polarity = self.hba.tile[tile].element[elem].x
            else:
                elem_polarity = self.hba.tile[tile].element[elem].y

            elem_polarity.low_seconds += self.antenna_data.seconds()
            elem_polarity.low_bad_seconds += bad_secs
            if val < elem_polarity.low_val:
                elem_polarity.low_noise = 1
                elem_polarity.low_val = val
                elem_polarity.low_ref = ref
                elem_polarity.low_diff = diff

        for n in high_noise:
            rcu, val, bad_secs, ref, diff = n
            tile = rcu // 2
            logger.info("%s RCU %d Tile %d Element %d High-Noise value=%3.1f bad=%d(%d) ref=%3.1f diff=%3.1f" % (
                         parset.as_string('ctrl-word'), rcu, tile, elem + 1, val, bad_secs, self.antenna_data.seconds(), ref, diff))

            if rcu % 2 == 0:
                elem_polarity = self.hba.tile[tile].element[elem].x
            else:
                elem_polarity = self.hba.tile[tile].element[elem].y

            elem_polarity.high_seconds += self.antenna_data.seconds()
            elem_polarity.high_bad_seconds += bad_secs
            if val > elem_polarity.high_val:
                elem_polarity.high_noise = 1
                elem_polarity.high_val = val
                elem_polarity.high_ref = ref
                elem_polarity.high_diff = diff

        for n in jitter:
            rcu, val, ref, bad_secs = n
            tile = rcu // 2
            logger.info("%s RCU %d Tile %d Element %d Jitter, fluctuation=%3.1fdB  normal=%3.1fdB" % (
                         parset.as_string('ctrl-word'), rcu, tile, elem + 1, val, ref))

            if rcu % 2 == 0:
                elem_polarity = self.hba.tile[tile].element[elem].x
            else:
                elem_polarity = self.hba.tile[tile].element[elem].y

            elem_polarity.jitter_seconds += self.antenna_data.seconds()
            elem_polarity.jitter_bad_seconds += bad_secs
            if val > elem_polarity.jitter_val:
                elem_polarity.jitter = 1
                elem_polarity.jitter_val = val
                elem_polarity.jitter_ref = ref
        return

    def check_rf_power_elements(self, elem, ctrl_nr, parset):

        logger.info("--- RF test ---")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        test_info_x, signal_info_x = check_rf_power(data=self.antenna_data, band=mode_to_band(self.db.rcumode),
                                                     pol='X', parset=parset)
        logger.debug("X data:  test subband=%d,  median val=%5.3f" % (test_info_x['subband'],
                                                                      test_info_x['test_val']))

        test_info_y, signal_info_y = check_rf_power(data=self.antenna_data, band=mode_to_band(self.db.rcumode),
                                                     pol='Y', parset=parset)
        logger.debug("Y data:  test subband=%d,  median val=%5.3f" % (test_info_y['subband'],
                                                                      test_info_y['test_val']))

        if test_info_x['valid'] and test_info_y['valid']:
            for tile in self.hba.tile:
                if tile.x.rcu_off or tile.y.rcu_off:
                    continue

                tile.element[elem].x.rf_ref_signal[ctrl_nr] = test_info_x['test_val']
                tile.element[elem].y.rf_ref_signal[ctrl_nr] = test_info_y['test_val']
                tile.element[elem].x.rf_test_subband[ctrl_nr] = test_info_x['subband']
                tile.element[elem].y.rf_test_subband[ctrl_nr] = test_info_y['subband']

                if str(tile.x.rcu) in signal_info_x:
                    tile.element[elem].x.test_signal[ctrl_nr] = signal_info_x[str(tile.x.rcu)]['value']
                    if signal_info_x[str(tile.x.rcu)]['status'] == 'no_signal':
                        tile.element[elem].x.no_signal = 1
                    elif signal_info_x[str(tile.x.rcu)]['status'] == 'no_power':
                        tile.element[elem].no_power = 1
                    elif signal_info_x[str(tile.x.rcu)]['status'] == 'low':
                        tile.element[elem].x.too_low = 1
                    elif signal_info_x[str(tile.x.rcu)]['status'] == 'high':
                        tile.element[elem].x.too_high = 1

                if str(tile.y.rcu) in signal_info_y:
                    tile.element[elem].y.test_signal[ctrl_nr] = signal_info_y[str(tile.y.rcu)]['value']
                    if signal_info_y[str(tile.y.rcu)]['status'] == 'no_signal':
                        tile.element[elem].y.no_signal = 1
                    elif signal_info_y[str(tile.y.rcu)]['status'] == 'no_power':
                        tile.element[elem].no_power = 1
                    elif signal_info_y[str(tile.y.rcu)]['status'] == 'low':
                        tile.element[elem].y.too_low = 1
                    elif signal_info_y[str(tile.y.rcu)]['status'] == 'high':
                        tile.element[elem].y.too_high = 1

                if str(tile.x.rcu) in signal_info_x and str(tile.y.rcu) in signal_info_y:
                    if signal_info_x[str(tile.x.rcu)]['status'] != 'normal' or \
                       signal_info_y[str(tile.y.rcu)]['status'] != 'normal':
                        logger.info("%s HBA Tile=%d Elem=%d:  X=%3.1fdB(%s)   Y=%3.1fdB(%s)" % (
                                     parset.as_string('ctrl-word'),
                                     tile.nr,
                                     elem + 1,
                                     signal_info_x[str(tile.x.rcu)]['value'],
                                     signal_info_x[str(tile.x.rcu)]['status'],
                                     signal_info_y[str(tile.y.rcu)]['value'],
                                     signal_info_y[str(tile.y.rcu)]['status']))
        else:
            logger.warning("HBA Elem=%d, No valid test signal" % (elem + 1))
            # self.hba.rf_signal_to_low = 1

        return
