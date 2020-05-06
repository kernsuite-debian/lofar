#!/usr/bin/env python3
"""
Make report from measurement, using information in test_db
"""
import logging
from .general import get_date_time_str, get_short_date_str, get_hostname, MyTestLogger

logger = logging.getLogger('main.reporting')
logger.debug("starting reporting logger")


def make_report(db, logdir):
    # print logdir
    date = get_short_date_str(db.check_start_time)
    log = MyTestLogger(logdir, db.StID)

    log.add_line("%s,NFO,---,VERSIONS,%s" % (date, db.script_versions))

    log.add_line("%s,NFO,---,STATION,NAME=%s" % (date, db.StID))

    log.add_line("%s,NFO,---,RUNTIME,START=%s,STOP=%s" % (
        date, get_date_time_str(db.check_start_time), get_date_time_str(db.check_stop_time)))

    info = ""
    bad = ""
    for ant in db.lbl.ant:
        if ant.on_bad_list == 1:
            bad += "%d " % ant.nr_pvss
    if len(bad) > 0:
        info += "LBL=%s," % (bad[:-1])

    bad = ""
    for ant in db.lbh.ant:
        if ant.on_bad_list == 1:
            bad += "%d " % ant.nr_pvss
    if len(bad) > 0:
        info += "LBH=%s," % (bad[:-1])

    bad = ""
    for tile in db.hba.tile:
        if tile.on_bad_list == 1:
            bad += "%d " % tile.nr
    if len(bad) > 0:
        info += "HBA=%s," % (bad[:-1])
    if len(info) > 0:
        log.add_line("%s,NFO,---,BADLIST,%s" % (date, info[:-1]))

    if db.rsp_driver_down:
        log.add_line("%s,NFO,---,DRIVER,RSPDRIVER=DOWN" % date)

    if db.tbb_driver_down:
        log.add_line("%s,NFO,---,DRIVER,TBBDRIVER=DOWN" % date)

    if len(db.board_errors):
        boardstr = ''
        for board in db.board_errors:
            boardstr += "RSP-%d=DOWN," % board
        log.add_line("%s,NFO,---,BOARD,%s" % (date, boardstr[:-1]))

    log.add_line("%s,NFO,---,CHECKS,%s" % (date, ",".join(db.tests_done)))

    log.add_line("%s,NFO,---,STATISTICS,BAD_LBL=%d,BAD_LBH=%d,BAD_HBA=%d,BAD_HBA0=%d,BAD_HBA1=%d" % (
        date, db.lbl.nr_bad_antennas, db.lbh.nr_bad_antennas, db.hba.nr_bad_tiles,
        db.hba.nr_bad_tiles_0, db.hba.nr_bad_tiles_1))

    spu_report(db, date, log)
    rsp_report(db, date, log)
    tbb_report(db, date, log)

    for lba in (db.lbl, db.lbh):
        lba_report(lba, date, log)

    hba_tile_report(db, date, log)
    hba_element_report(db, date, log)

    return


def spu_report(db, date, log):
    logger.debug("generate spu report")
    for spu in db.spu:
        spu.test()
        if not spu.voltage_ok:
            valstr = ''
            if not spu.rcu_ok:
                valstr += ",RCU-5.0V=%3.1f" % spu.rcu_5_0_volt
            if not spu.lba_ok:
                valstr += ",LBA-8.0V=%3.1f" % spu.lba_8_0_volt
            if not spu.hba_ok:
                valstr += ",HBA-48V=%3.1f" % spu.hba_48_volt
            if not spu.spu_ok:
                valstr += ",SPU-3.3V=%3.1f" % spu.spu_3_3_volt
            if len(valstr):
                log.add_line("%s,SPU,%03d,VOLTAGE%s" % (date, spu.nr, valstr))

    if not spu.temp_ok:
        log.add_line("%s,SPU,%03d,TEMPERATURE,PCB=%2.0f" % (
            date, spu.nr, spu.temp))


def rsp_report(db, date, log):
    logger.debug("generate rsp report")
    for rsp in db.rsp:
        rsp.test()
        if not rsp.version_ok:
            log.add_line("%s,RSP,%03d,VERSION,BP=%s,AP=%s" % (
                date, rsp.nr, rsp.bp_version, rsp.ap_version))
        if not rsp.voltage_ok:
            log.add_line("%s,RSP,%03d,VOLTAGE,1.2V=%3.2f,2.5V=%3.2f,3.3V=%3.2f" % (
                date, rsp.nr, rsp.voltage1_2, rsp.voltage2_5, rsp.voltage3_3))
        if not rsp.temp_ok:
            log.add_line("%s,RSP,%03d,TEMPERATURE,PCB=%2.0f,BP=%2.0f,AP0=%2.0f,AP1=%2.0f,AP2=%2.0f,AP3=%2.0f" % (
                date, rsp.nr, rsp.pcb_temp, rsp.bp_temp, rsp.ap0_temp, rsp.ap1_temp, rsp.ap2_temp,
                rsp.ap3_temp))


def tbb_report(db, date, log):
    logger.debug("generate tbb report")
    for tbb in db.tbb:
        tbb.test()
        if not tbb.version_ok:
            log.add_line("%s,TBB,%03d,VERSION,TP=%s,MP=%s" % (
                date, tbb.nr, tbb.tp_version, tbb.mp_version))
        if not tbb.memory_ok:
            log.add_line("%s,TBB,%03d,MEMORY" % (date, tbb.nr))

        if not tbb.voltage_ok:
            log.add_line("%s,TBB,%03d,VOLTAGE,1.2V=%3.2f,2.5V=%3.2f,3.3V=%3.2f" % (
                date, tbb.nr, tbb.voltage1_2, tbb.voltage2_5, tbb.voltage3_3))
        if not tbb.temp_ok:
            log.add_line("%s,TBB,%03d,TEMPERATURE,PCB=%2.0f,TP=%2.0f,MP0=%2.0f,MP1=%2.0f,MP2=%2.0f,MP3=%2.0f" % (
                date, tbb.nr, tbb.pcb_temp, tbb.tp_temp, tbb.mp0_temp, tbb.mp1_temp, tbb.mp2_temp,
                tbb.mp3_temp))


def rcu_report(db, date, log):
    logger.debug("generate rcu rapport")
    for rcu in range(db.nr_rcu):
        if db.rcu_state[rcu]:
            log.add_line("%s,RCU,%03d,BROKEN" % (date, rcu))


def lba_report(db, date, log):
    logger.debug("generate %s report" % db.label.lower())
    if db.signal_check_done:
        if db.rf_signal_to_low:
            log.add_line("%s,%s,---,TOOLOW,MEDIANX=%3.1f,MEDIANY=%3.1f" % (
                date, db.label, db.rf_ref_signal_x, db.rf_ref_signal_y))
        else:
            if db.error:
                log.add_line("%s,%s,---,TESTSIGNAL,SUBBANDX=%d,SIGNALX=%3.1f,SUBBANDY=%d,SIGNALY=%3.1f" % (
                    date, db.label, db.rf_test_subband_x, db.rf_ref_signal_x,
                    db.rf_test_subband_y, db.rf_ref_signal_y))

    if db.noise_check_done or db.oscillation_check_done or db.spurious_check_done or \
            db.signal_check_done or db.short_check_done or db.flat_check_done or db.down_check_done:
        for ant in db.ant:
            if ant.down:
                log.add_line("%s,%s,%03d,DOWN,X=%3.1f,Y=%3.1f,Xoff=%d,Yoff=%d" % (
                    date, db.label, ant.nr_pvss, ant.x.down_pwr, ant.y.down_pwr, ant.x.down_offset, ant.y.down_offset))
            else:
                if db.signal_check_done:
                    valstr = ''
                    if ant.x.too_low or ant.x.too_high:
                        valstr += ",X=%3.1f" % ant.x.test_signal
                    if ant.y.too_low or ant.y.too_high:
                        valstr += ",Y=%3.1f" % ant.y.test_signal
                    if len(valstr):
                        log.add_line("%s,%s,%03d,RF_FAIL%s" % (date, db.label, ant.nr_pvss, valstr))

                if db.flat_check_done:
                    valstr = ''
                    if ant.x.flat:
                        valstr += ",Xmean=%3.1f" % ant.x.flat_val
                    if ant.y.flat:
                        valstr += ",Ymean=%3.1f" % ant.y.flat_val
                    if len(valstr):
                        log.add_line("%s,%s,%03d,FLAT%s" % (date, db.label, ant.nr_pvss, valstr))

                if db.short_check_done:
                    valstr = ''
                    if ant.x.short:
                        valstr += ",Xmean=%3.1f" % ant.x.short_val
                    if ant.y.short:
                        valstr += ",Ymean=%3.1f" % ant.y.short_val
                    if len(valstr):
                        log.add_line("%s,%s,%03d,SHORT%s" % (date, db.label, ant.nr_pvss, valstr))

                if db.oscillation_check_done:
                    valstr = ''
                    if ant.x.osc:
                        valstr += ',X=1'
                    if ant.y.osc:
                        valstr += ',Y=1'
                    if len(valstr):
                        log.add_line("%s,%s,%03d,OSCILLATION%s" % (date, db.label, ant.nr_pvss, valstr))

                if db.spurious_check_done:
                    valstr = ''
                    if ant.x.spurious:
                        valstr += ',X=1'
                    if ant.y.spurious:
                        valstr += ',Y=1'
                    if len(valstr):
                        log.add_line("%s,%s,%03d,SPURIOUS%s" % (date, db.label, ant.nr_pvss, valstr))

                if db.noise_check_done:
                    noise = False
                    valstr = ''
                    if not ant.x.flat and ant.x.low_noise:
                        proc = (100.0 / ant.x.low_seconds) * ant.x.low_bad_seconds
                        valstr += ',Xproc=%5.3f,Xval=%3.1f,Xdiff=%5.3f,Xref=%3.1f' % (
                            proc, ant.x.low_val, ant.x.low_diff, ant.x.low_ref)
                    if not ant.y.flat and ant.y.low_noise:
                        proc = (100.0 / ant.y.low_seconds) * ant.y.low_bad_seconds
                        valstr += ',Yproc=%5.3f,Yval=%3.1f,Ydiff=%5.3f,Yref=%3.1f' % (
                            proc, ant.y.low_val, ant.y.low_diff, ant.y.low_ref)
                    if len(valstr):
                        log.add_line("%s,%s,%03d,LOW_NOISE%s" % (date, db.label, ant.nr_pvss, valstr))
                        noise = True

                    valstr = ''
                    if ant.x.high_noise:
                        proc = (100.0 / ant.x.high_seconds) * ant.x.high_bad_seconds
                        valstr += ',Xproc=%5.3f,Xval=%3.1f,Xdiff=%5.3f,Xref=%3.1f' % (
                            proc, ant.x.high_val, ant.x.high_diff, ant.x.high_ref)
                    if ant.y.high_noise:
                        proc = (100.0 / ant.y.high_seconds) * ant.y.high_bad_seconds
                        valstr += ',Yproc=%5.3f,Yval=%3.1f,Ydiff=%5.3f,Yref=%3.1f' % (
                            proc, ant.y.high_val, ant.y.high_diff, ant.y.high_ref)
                    if len(valstr):
                        log.add_line("%s,%s,%03d,HIGH_NOISE%s" % (date, db.label, ant.nr_pvss, valstr))
                        noise = True

                    valstr = ''
                    if not noise and ant.x.jitter:
                        proc = (100.0 / ant.x.jitter_seconds) * ant.x.jitter_bad_seconds
                        valstr += ',Xproc=%5.3f,Xdiff=%5.3f,Xref=%3.1f' % (
                            proc, ant.x.jitter_val, ant.x.jitter_ref)
                    if not noise and ant.y.jitter:
                        proc = (100.0 / ant.y.jitter_seconds) * ant.y.jitter_bad_seconds
                        valstr += ',Xproc=%5.3f,Ydiff=%5.3f,Yref=%3.1f' % (
                            proc, ant.y.jitter_val, ant.y.jitter_ref)
                    if len(valstr):
                        log.add_line("%s,%s,%03d,JITTER%s" % (date, db.label, ant.nr_pvss, valstr))
                        # lba = None


def hba_tile_report(db, date, log):
    logger.debug("generate hba-tile report")
    if db.hba.signal_check_done:
        if db.hba.rf_signal_to_low:
            log.add_line("%s,HBA,---,TOOLOW,MEDIANX=%3.1f,MEDIANY=%3.1f" % (
                date, db.hba.rf_ref_signal_x[0], db.hba.rf_ref_signal_y[0]))
        else:
            if db.hba.error:
                log.add_line("%s,HBA,---,TESTSIGNAL,SUBBANDX=%d,SIGNALX=%3.1f,SUBBANDY=%d,SIGNALY=%3.1f" % (
                    date, db.hba.rf_test_subband_x[0], db.hba.rf_ref_signal_x[0],
                    db.hba.rf_test_subband_y[0], db.hba.rf_ref_signal_y[0]))

    for tile in db.hba.tile:
        if tile.x.error or tile.y.error:
            # check for broken summators
            if db.hba.modem_check_done:
                valstr = ''
                if tile.c_summator_error:
                    log.add_line("%s,HBA,%03d,C_SUMMATOR" % (date, tile.nr))
                else:
                    for elem in tile.element:
                        if elem.no_modem:
                            valstr += ",E%02d=??" % elem.nr

                        elif elem.modem_error:
                            valstr += ",E%02d=error" % elem.nr
                    if len(valstr):
                        log.add_line("%s,HBA,%03d,MODEM%s" % (date, tile.nr, valstr))

            if db.hba.noise_check_done:
                valstr = ''
                noise = False

                if tile.x.low_noise:
                    proc = (100.0 / tile.x.low_seconds) * tile.x.low_bad_seconds
                    valstr += ',Xproc=%5.3f,Xval=%3.1f,Xdiff=%5.3f,Xref=%3.1f' % (
                        proc, tile.x.low_val, tile.x.low_diff, tile.x.low_ref)
                if tile.y.low_noise:
                    proc = (100.0 / tile.y.low_seconds) * tile.y.low_bad_seconds
                    valstr += ',Yproc=%5.3f,Yval=%3.1f,Ydiff=%5.3f,Yref=%3.1f' % (
                        proc, tile.y.low_val, tile.y.low_diff, tile.y.low_ref)
                if len(valstr):
                    log.add_line("%s,HBA,%03d,LOW_NOISE%s" % (date, tile.nr, valstr))
                    noise = True

                valstr = ''
                if tile.x.high_noise:
                    proc = (100.0 / tile.x.high_seconds) * tile.x.high_bad_seconds
                    valstr += ',Xproc=%5.3f,Xval=%3.1f,Xdiff=%5.3f,Xref=%3.1f' % (
                        proc, tile.x.high_val, tile.x.high_diff, tile.x.high_ref)
                if tile.y.high_noise:
                    proc = (100.0 / tile.y.high_seconds) * tile.y.high_bad_seconds
                    valstr += ',Yproc=%5.3f,Yval=%3.1f,Ydiff=%5.3f,Yref=%3.1f' % (
                        proc, tile.y.high_val, tile.y.high_diff, tile.y.high_ref)
                if len(valstr):
                    log.add_line("%s,HBA,%03d,HIGH_NOISE%s" % (date, tile.nr, valstr))
                    noise = True

                valstr = ''
                if (not noise) and tile.x.jitter:
                    proc = (100.0 / tile.x.jitter_seconds) * tile.x.jitter_bad_seconds
                    valstr += ',Xproc=%5.3f,Xdiff=%5.3f,Xref=%3.1f' % (proc, tile.x.jitter_val, tile.x.jitter_ref)
                if (not noise) and tile.y.jitter:
                    proc = (100.0 / tile.y.jitter_seconds) * tile.y.jitter_bad_seconds
                    valstr += ',Yproc=%5.3f,Ydiff=%5.3f,Yref=%3.1f' % (proc, tile.y.jitter_val, tile.y.jitter_ref)
                if len(valstr):
                    log.add_line("%s,HBA,%03d,JITTER%s" % (date, tile.nr, valstr))

            if db.hba.oscillation_check_done:
                valstr = ''
                if tile.x.osc:
                    valstr += ',X=1'
                if tile.y.osc:
                    valstr += ',Y=1'
                if len(valstr):
                    log.add_line("%s,HBA,%03d,OSCILLATION%s" % (date, tile.nr, valstr))

            if tile.p_summator_error:
                log.add_line("%s,HBA,%03d,P_SUMMATOR" % (date, tile.nr))

            if db.hba.summatornoise_check_done:
                valstr = ''
                if tile.x.summator_noise:
                    valstr += ',X=1'
                if tile.y.summator_noise:
                    valstr += ',Y=1'
                if len(valstr):
                    log.add_line("%s,HBA,%03d,SUMMATOR_NOISE%s" % (date, tile.nr, valstr))

            if db.hba.spurious_check_done:
                valstr = ''
                if tile.x.spurious:
                    valstr += ',X=1'
                if tile.y.spurious:
                    valstr += ',Y=1'
                if len(valstr):
                    log.add_line("%s,HBA,%03d,SPURIOUS%s" % (date, tile.nr, valstr))

            if db.hba.signal_check_done:
                valstr = ''
                if tile.x.too_low or tile.x.too_high:
                    valstr += ",X=%3.1f %d %3.1f %3.1f %d %3.1f" % (
                        tile.x.test_signal[0], db.hba.rf_test_subband_x[0], db.hba.rf_ref_signal_x[0],
                        tile.x.test_signal[1], db.hba.rf_test_subband_x[1], db.hba.rf_ref_signal_x[1])
                if tile.y.too_low or tile.y.too_high:
                    valstr += ",Y=%3.1f %d %3.1f %3.1f %d %3.1f" % (
                        tile.y.test_signal[0], db.hba.rf_test_subband_y[0], db.hba.rf_ref_signal_y[0],
                        tile.y.test_signal[1], db.hba.rf_test_subband_y[1], db.hba.rf_ref_signal_y[1])
                if len(valstr):
                    log.add_line("%s,HBA,%03d,RF_FAIL%s" % (date, tile.nr, valstr))


def hba_element_report(db, date, log):
    logger.debug("generate hba-element report")
    if not db.hba.element_check_done:
        return

    for tile in db.hba.tile:
        valstr = ''
        for elem in tile.element:
            # if tile.x.rcu_off or tile.y.rcu_off:
            #    continue
            if db.hba.modem_check_done and (elem.no_modem or elem.modem_error):
                if not tile.c_summator_error:
                    if elem.no_modem:
                        valstr += ",M%d=??" % elem.nr

                    elif elem.modem_error:
                        valstr += ",M%d=error" % elem.nr
            else:
                if elem.x.osc or elem.y.osc:
                    if elem.x.osc:
                        valstr += ",OX%d=1" % elem.nr
                    if elem.y.osc:
                        valstr += ",OY%d=1" % elem.nr

                elif elem.x.spurious or elem.y.spurious:
                    if elem.x.spurious:
                        valstr += ",SPX%d=1" % elem.nr
                    if elem.y.spurious:
                        valstr += ",SPY%d=1" % elem.nr

                elif elem.x.low_noise or elem.x.high_noise or elem.y.low_noise or \
                        elem.y.high_noise or elem.x.jitter or elem.y.jitter:
                    if elem.x.low_noise:
                        valstr += ",LNX%d=%3.1f %5.3f" % (elem.nr, elem.x.low_val, elem.x.low_diff)

                    if elem.x.high_noise:
                        valstr += ",HNX%d=%3.1f %5.3f" % (elem.nr, elem.x.high_val, elem.x.high_diff)

                    if (not elem.x.low_noise) and (not elem.x.high_noise) and (elem.x.jitter > 0.0):
                        valstr += ",JX%d=%5.3f" % (elem.nr, elem.x.jitter)

                    if elem.y.low_noise:
                        valstr += ",LNY%d=%3.1f %5.3f" % (elem.nr, elem.y.low_val, elem.y.low_diff)

                    if elem.y.high_noise:
                        valstr += ",HNY%d=%3.1f %5.3f" % (elem.nr, elem.y.high_val, elem.y.high_diff)

                    if (not elem.y.low_noise) and (not elem.y.high_noise) and (elem.y.jitter > 0.0):
                        valstr += ",JY%d=%5.3f" % (elem.nr, elem.y.jitter)
                else:
                    #logger.debug("check signal elem %d" % elem.nr)
                    if elem.x.rf_ref_signal[0] == 0 and elem.x.rf_ref_signal[1] == 0:
                        #logger.debug("x ref signal == 0")
                        log.add_line("%s,HBA,%03d,NOSIGNAL,E%02dX" % (date,
                                                                      tile.nr,
                                                                      elem.nr))
                    else:
                        if elem.x.error == 1:
                            #logger.debug("x-error")
                            valstr += ",X%d=%3.1f %d %3.1f %3.1f %d %3.1f" % (elem.nr,
                                                                              elem.x.test_signal[0],
                                                                              elem.x.rf_test_subband[0],
                                                                              elem.x.rf_ref_signal[0],
                                                                              elem.x.test_signal[1],
                                                                              elem.x.rf_test_subband[1],
                                                                              elem.x.rf_ref_signal[1])

                    if elem.y.rf_ref_signal[0] == 0 and elem.y.rf_ref_signal[1] == 0:
                        #logger.debug("y ref signal == 0")
                        log.add_line("%s,HBA,%03d,NOSIGNAL,E%02dY" % (date,
                                                                      tile.nr,
                                                                      elem.nr))
                    else:
                        if elem.y.error == 1:
                            #logger.debug("y-error")
                            valstr += ",Y%d=%3.1f %d %3.1f %3.1f %d %3.1f" % (elem.nr,
                                                                              elem.y.test_signal[0],
                                                                              elem.y.rf_test_subband[0],
                                                                              elem.y.rf_ref_signal[0],
                                                                              elem.y.test_signal[1],
                                                                              elem.y.rf_test_subband[1],
                                                                              elem.y.rf_ref_signal[1])

        if len(valstr):
            logger.debug("tile %d valstr=%s" % (tile.nr, valstr))
            log.add_line("%s,HBA,%03d,E_FAIL%s" % (date,
                                                   tile.nr,
                                                   valstr))
