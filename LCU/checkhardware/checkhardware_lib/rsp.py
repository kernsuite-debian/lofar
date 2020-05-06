
import numpy as np
from .lofar import *

logger = logging.getLogger('main.rsp')
logger.debug("starting rsp logger")

# class for checking RSP boards using rspctl
class RSP(object):
    def __init__(self, db):
        self.db = db
        self.nr = self.db.nr_rsp

    # check software versions of driver, tbbctl and TP/MP firmware
    def check_versions(self, parset):
        logger.info("=== RSP Version check ===")
        #print parset.get_set()
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return
        answer = rspctl('--version')

        # check if Driver is available
        if answer.find('No Response') > 0:
            logger.warning("No RSPDriver")
            images_ok = False
        else:
            infolines = answer.splitlines()
            info = infolines

            images_ok = True
            # check if image_nr > 0 for all boards
            if str(info).count('0.0') != 0:
                logger.warning("Not all boards in working image")
                images_ok = False

            for rsp in self.db.rsp:
                board_info = info[rsp.nr].split(',')

                if board_info[1].split()[3] != parset.as_string('version.bp'):
                    logger.warning("Board %d Not right BP version" % rsp.nr)
                    rsp.bp_version = board_info[1].split()[3]
                    images_ok = False

                if board_info[2].split()[3] != parset.as_string('version.ap'):
                    logger.warning("Board %d Not right AP version" % rsp.nr)
                    rsp.ap_version = board_info[2].split()[3]
                    images_ok = False

        if not check_active_rspdriver():
            logger.warning("RSPDriver down while testing, skip result")
            return False

        logger.info("=== Done RSP Version check ===")
        self.db.add_test_done('RV')
        return images_ok

    def check_board(self, parset):
        ok = True
        logger.info("=== RSP Board check ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return False
        answer = rspctl('--status')

        bp_temp = np.zeros((self.db.nr_rsp,), float)
        bp_temp[:] = -1

        ap_temp = np.zeros((self.db.nr_rsp, 4), float)
        ap_temp[:,:] = -1

        p2 = 0
        for rsp in self.db.rsp:
            p1 = answer.find("RSP[%2d]" % rsp.nr, p2)
            p2 = answer.find("\n", p1)
            d = [float(i.split(":")[1].strip()) for i in answer[p1 + 7:p2].split(',')]
            if len(d) == 3:
                logger.debug("RSP board %2d, voltages: 1.2V=%4.2f, 2.5V=%4.2f, 3.3V=%4.2f" % (
                             rsp.nr, d[0], d[1], d[2]))
                rsp.voltage1_2 = d[0]
                rsp.voltage2_5 = d[1]
                rsp.voltage3_3 = d[2]

        for rsp in self.db.rsp:
            p1 = answer.find("RSP[%2d]" % rsp.nr, p2)
            p2 = answer.find("\n", p1)
            d = [float(i.split(":")[1].strip()) for i in answer[p1 + 7:p2].split(',')]
            if len(d) == 6:
                logger.debug("RSP board %2d, temperatures: pcb=%3.0f, bp=%3.0f, ap0=%3.0f, ap1=%3.0f, ap2=%3.0f, ap3=%3.0f" % (
                             rsp.nr, d[0], d[1], d[2], d[3], d[4], d[5]))
                rsp.pcb_temp = d[0]
                rsp.bp_temp  = d[1]
                rsp.ap0_temp = d[2]
                rsp.ap1_temp = d[3]
                rsp.ap2_temp = d[4]
                rsp.ap3_temp = d[5]
                bp_temp[rsp.nr]    = d[1]
                ap_temp[rsp.nr, 0] = d[2]
                ap_temp[rsp.nr, 1] = d[3]
                ap_temp[rsp.nr, 2] = d[4]
                ap_temp[rsp.nr, 3] = d[5]

        bp_temp = np.ma.masked_less(bp_temp, 0)
        bp_check_temp = np.ma.median(bp_temp[:]) + parset.as_float('temperature.bp.max_delta')
        logger.debug("bp avarage temp= %3.1f, check temperature= %3.1f" % (
                     np.ma.mean(bp_temp[:]), bp_check_temp))

        ap_temp = np.ma.masked_less(ap_temp, 0)
        ap_check_temp = np.ma.median(ap_temp[:,:]) + parset.as_float('temperature.ap.max_delta')
        logger.debug("ap avarage temp= %3.1f, check temperature= %3.1f" % (
                     np.ma.mean(ap_temp[:,:]), ap_check_temp))

        for rsp in self.db.rsp:
            if not (parset.as_float('voltage.1_2.min') <= rsp.voltage1_2 <= parset.as_float('voltage.1_2.max')):
                rsp.voltage_ok = 0
                logger.info("RSP board %2d bad voltage 1.2V=%4.2fV" % (rsp.nr, rsp.voltage1_2))
            if not (parset.as_float('voltage.2_5.min') <= rsp.voltage2_5 <= parset.as_float('voltage.2_5.max')):
                rsp.voltage_ok = 0
                logger.info("RSP board %2d bad voltage 2.5V=%4.2fV" % (rsp.nr, rsp.voltage2_5))
            if not (parset.as_float('voltage.3_3.min') <= rsp.voltage3_3 <= parset.as_float('voltage.3_3.max')):
                rsp.voltage_ok = 0
                logger.info("RSP board %2d bad voltage 3.3V=%4.2fV" % (rsp.nr, rsp.voltage3_3))

            if rsp.pcb_temp > parset.as_float('temperature.max'):
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature pcb_temp=%3.0f" % (rsp.nr, rsp.pcb_temp))

            if rsp.bp_temp > parset.as_float('temperature.bp.max') or rsp.bp_temp > bp_check_temp:
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature bp_temp=%3.0f" % (rsp.nr, rsp.bp_temp))

            if rsp.ap0_temp > parset.as_float('temperature.ap.max') or rsp.ap0_temp > ap_check_temp:
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature ap0_temp=%3.0f" % (rsp.nr, rsp.ap0_temp))

            if rsp.ap1_temp > parset.as_float('temperature.ap.max') or rsp.ap1_temp > ap_check_temp:
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature ap1_temp=%3.0f" % (rsp.nr, rsp.ap1_temp))

            if rsp.ap2_temp > parset.as_float('temperature.ap.max') or rsp.ap2_temp > ap_check_temp:
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature ap2_temp=%3.0f" % (rsp.nr, rsp.ap2_temp))

            if rsp.ap3_temp > parset.as_float('temperature.ap.max') or rsp.ap3_temp > ap_check_temp:
                rsp.temp_ok = 0
                logger.info("RSP board %2d, high temperature ap3_temp=%3.0f" % (rsp.nr, rsp.ap3_temp))
        logger.info("=== Done RSP Board check ===")
        self.db.add_test_done('RBC')
        return ok
        # end of RSP class
