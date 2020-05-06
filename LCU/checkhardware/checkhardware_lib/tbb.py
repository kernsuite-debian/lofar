import logging
import numpy as np
from .lofar import *

logger = logging.getLogger('main.tbb')
logger.debug("starting tbb logger")

# class for checking TBB boards using tbbctl
class TBB(object):
    def __init__(self, db):
        self.db = db
        self.nr = self.db.nr_tbb
        self.driverstate = True
        #tbbctl('--free')

    # check software versions of driver, tbbctl and TP/MP firmware
    def check_versions(self, parset):
        logger.info("=== TBB Version check ===")
        answer = tbbctl('--version')

        # check if Driver is available
        if answer.find('TBBDriver is NOT responding') > 0:
            logger.warning("No TBBDriver")
            self.driverstate = False
        else:
            infolines = answer.splitlines()
            info = infolines[4:6] + infolines[9:-1]

            # check if image_nr > 0 for all boards
            if str(info).count('V') != (self.nr * 4):
                logger.warning("WARNING, Not all boards in working image")

            for tbb in self.db.tbb:
                board_info = info[2 + tbb.nr].strip().split('  ')
                if 'board not active' in board_info:
                    logger.warning("Board %d not available" % tbb.nr)
                    tbb.tp_version = 'na'
                    tbb.mp_version = 'na'
                    continue
                if 'mpi time-out' in board_info:
                    logger.warning("Board %d in factory image" % tbb.nr)
                    tbb.tp_version = 'na'
                    tbb.mp_version = 'na'
                    continue
                # print board_info
                if board_info[3].split()[1] != parset.as_string('version.tp'):
                    logger.warning("Board %d Not right TP version" % tbb.nr)
                    tbb.tp_version = board_info[3].split()[1]

                if board_info[4].split()[1] != parset.as_string('version.mp'):
                    logger.warning("Board %d Not right MP version" % tbb.nr)
                    tbb.mp_version = board_info[4].split()[1]
        logger.info("=== Done TBB Version check ===")
        self.db.add_test_done('TV')
        return

    # Check memory address and data lines
    def check_memory(self):
        logger.info("=== TBB Memory check ===")
        tbbctl('--free')
        for tbb in self.db.tbb:
            if not tbb.board_active:
                logger.info("Board %d ot active" % tbb.nr)
                tbb.memory_ok = 0
                continue
            answer = tbbctl('--testddr=%d' % tbb.nr)
            info = answer.splitlines()[-3:]
            memory_ok = True
            if info[0].strip() != 'All Addresslines OK':
                logger.info("Board %d Addresline error" % tbb.nr)
                memory_ok = False

            if info[1].strip() != 'All Datalines OK':
                logger.info("Board %d Datalines error" % tbb.nr)
                memory_ok = False

            if not memory_ok:
                tbb.memory_ok = 0
                logger.info(answer)
        logger.info("=== Done TBB Memory check ===")
        self.db.add_test_done('TM')
        return

    def check_board(self, parset):
        board_ok = True
        logger.info("=== TBB Board check ===")
        if not check_active_tbbdriver():
            logger.warning("TBBDriver down, skip test")
            return False
        answer = tbbctl('--status')

        mp_temp = np.zeros((self.db.nr_tbb, 4), float)
        mp_temp[:,:] = -1

        for line in answer.splitlines():
            if 'ETH' in line or 'clock' in line:
                info = line.split()
            else:
                continue
            #print info
            try:
                tbb_nr = int(info[0].strip())
                if not self.db.tbb[tbb_nr].board_active:
                    logger.info("Board %d ot active" % tbb_nr)
                    continue
                if tbb_nr in range(12):
                    tbb = self.db.tbb[tbb_nr]
                    tbb.voltage1_2 = float(info[3][:-1])
                    tbb.voltage2_5 = float(info[4][:-1])
                    tbb.voltage3_3 = float(info[5][:-1])
                    tbb.pcb_temp = float(info[6][:-2])
                    tbb.tp_temp = float(info[7][:-2])
                    tbb.mp0_temp = float(info[8][:-2])
                    tbb.mp1_temp = float(info[10][:-2])
                    tbb.mp2_temp = float(info[12][:-2])
                    tbb.mp3_temp = float(info[14][:-2])
                    mp_temp[tbb_nr, 0] = tbb.mp0_temp
                    mp_temp[tbb_nr, 1] = tbb.mp1_temp
                    mp_temp[tbb_nr, 2] = tbb.mp2_temp
                    mp_temp[tbb_nr, 3] = tbb.mp3_temp

            except ValueError:
                logger.warning("value error in parse stage: %s" % line)
            except IndexError:
                logger.warning("index error in parse stage: %s" % line)
            except:
                raise

        mp_temp = np.ma.masked_less(mp_temp, 1.0)
        mp_check_temp = np.ma.median(mp_temp[:,:]) + parset.as_float('temperature.mp.max_delta')

        for tbb in self.db.tbb:
            logger.debug("TBB board %2d, voltages: 1.2V=%4.2f, 2.5V=%4.2f, 3.3V=%4.2f" % (
                tbb.nr, tbb.voltage1_2, tbb.voltage2_5, tbb.voltage3_3))

            if not (parset.as_float('voltage.1_2.min') <= tbb.voltage1_2 <= parset.as_float('voltage.1_2.max')):
                tbb.voltage_ok = 0
                logger.info("TBB board %2d, bad voltage 1.2V=%4.2fV" % (tbb.nr, tbb.voltage1_2))
            if not (parset.as_float('voltage.2_5.min') <= tbb.voltage2_5 <= parset.as_float('voltage.2_5.max')):
                tbb.voltage_ok = 0
                logger.info("TBB board %2d, bad voltage 2.5V=%4.2fV" % (tbb.nr, tbb.voltage2_5))
            if not (parset.as_float('voltage.3_3.min') <= tbb.voltage3_3 <= parset.as_float('voltage.3_3.max')):
                tbb.voltage_ok = 0
                logger.info("TBB board %2d bad voltage 3.3V=%4.2fV" % (tbb.nr, tbb.voltage3_3))

        for tbb in self.db.tbb:
            logger.debug(
                "TBB board %2d, temperatures: pcb=%3.0f, tp=%3.0f, mp0=%3.0f, mp1=%3.0f, mp2=%3.0f, mp3=%3.0f" % (
                    tbb.nr, tbb.pcb_temp, tbb.tp_temp, tbb.mp0_temp, tbb.mp1_temp, tbb.mp2_temp, tbb.mp3_temp))
            if tbb.pcb_temp > parset.as_float('temperature.max'):
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature pcb_temp=%3.0f" % (tbb.nr, tbb.pcb_temp))
            if tbb.tp_temp > parset.as_float('temperature.tp.max'):
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature tp_temp=%3.0f" % (tbb.nr, tbb.tp_temp))
            if tbb.mp0_temp > parset.as_float('temperature.mp.max') or tbb.mp0_temp > mp_check_temp:
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature mp0_temp=%3.0f" % (tbb.nr, tbb.mp0_temp))
            if tbb.mp1_temp > parset.as_float('temperature.mp.max') or tbb.mp1_temp > mp_check_temp:
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature mp1_temp=%3.0f" % (tbb.nr, tbb.mp1_temp))
            if tbb.mp2_temp > parset.as_float('temperature.mp.max') or tbb.mp2_temp > mp_check_temp:
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature mp2_temp=%3.0f" % (tbb.nr, tbb.mp2_temp))
            if tbb.mp3_temp > parset.as_float('temperature.mp.max') or tbb.mp3_temp > mp_check_temp:
                tbb.temp_ok = 0
                logger.info("TBB board %2d, high temperature mp3_temp=%3.0f" % (tbb.nr, tbb.mp3_temp))
        logger.debug("mp check temperature= %3.1f" % mp_check_temp)
        logger.info("=== Done TBB Board check ===")
        self.db.add_test_done('TBC')
        return board_ok
        # end of cTBB class
