import logging
from .lofar import *

logger = logging.getLogger('main.spu')
logger.debug("starting spu logger")

class SPU(object):
    def __init__(self, db):
        self.db = db
        self.board_info_str = []
        self.board_info_val = [-1, 0.0, 0.0, 0.0, 0.0, 0]

    def extract_board_info(self, line):
        li = line.split("|")
        if not li[0].strip().isdigit():
            return False

        self.board_info_str = [i.strip() for i in li]

        if li[0].strip().isdigit():
            self.board_info_val[0] = int(li[0].strip())
        else:
            self.board_info_val[0] = -1

        for i in range(1, 5, 1):
            if li[i].strip().replace('.', '').isdigit():
                self.board_info_val[i] = float(li[i].strip())
            else:
                self.board_info_val[i] = 0.0

        if li[5].strip().isdigit():
            self.board_info_val[5] = int(li[5].strip())
        else:
            self.board_info_val[5] = 0
        return True

    def check_status(self, parset):
        """
        check PSU if boards idle and fully loaded
        """
        logger.info("=== SPU status check ===")
        if not check_active_rspdriver():
            logger.warning("RSPDriver down, skip test")
            return

        noload = []
        fullload_3 = []
        fullload_5 = []
        logger.debug("check spu no load")
        answer = rspctl('--spustatus')

        # check if Driver is available
        if answer.find('No Response') > 0:
            logger.warning("No RSPDriver")

        else:
            infolines = answer.splitlines()
            for line in infolines:
                if self.extract_board_info(line):
                    bi = self.board_info_val
                    noload.append([bi[0], bi[1], bi[2], bi[3], bi[4]])
                    self.db.spu[bi[0]].temp = bi[5]
                    bi = self.board_info_str
                    logger.debug("Subrack %s voltages: rcu=%s  lba=%s  hba=%s  spu=%s  temp: %s" % (
                        bi[0], bi[1], bi[2], bi[3], bi[4], bi[5]))

            # turn on all hbas
            logger.debug("check spu full load mode 3")
            rsp_rcu_mode(3, self.db.lbh.select_list())
            answer = rspctl('--spustatus')
            infolines = answer.splitlines()
            for line in infolines:
                if self.extract_board_info(line):
                    bi = self.board_info_val
                    fullload_3.append([bi[0], bi[1], bi[2], bi[3], bi[4]])
                    bi = self.board_info_str
                    logger.debug("Subrack %s voltages: rcu=%s  lba=%s  hba=%s  spu=%s  temp: %s" % (
                        bi[0], bi[1], bi[2], bi[3], bi[4], bi[5]))

            # turn on all hbas
            logger.debug("check spu full load mode 5")
            rsp_rcu_mode(5, self.db.hba.select_list())
            answer = rspctl('--spustatus')
            infolines = answer.splitlines()
            for line in infolines:
                if self.extract_board_info(line):
                    bi = self.board_info_val
                    fullload_5.append([bi[0], bi[1], bi[2], bi[3], bi[4]])
                    bi = self.board_info_str
                    logger.debug("Subrack %s voltages: rcu=%s  lba=%s  hba=%s  spu=%s  temp: %s" % (
                        bi[0], bi[1], bi[2], bi[3], bi[4], bi[5]))

            #logger.debug("noload=%s" % str(noload))
            #logger.debug("fullload_3=%s" % str(fullload_3))
            #logger.debug("fullload_5=%s" % str(fullload_5))
            for sr in range(self.db.nr_spu):
                #logger.debug("sr=%d" % sr)
                # calculate mean of noload, fullload_3, fullload_5
                self.db.spu[sr].rcu_5_0_volt = (noload[sr][1] + fullload_3[sr][1] + fullload_5[sr][1]) / 3.0
                self.db.spu[sr].lba_8_0_volt = fullload_3[sr][2]
                self.db.spu[sr].hba_48_volt = fullload_5[sr][3]
                self.db.spu[sr].spu_3_3_volt = (noload[sr][4] + fullload_3[sr][4] + fullload_5[sr][4]) / 3.0

                if self.db.spu[sr].temp > parset.as_float('temperature.max'):
                    self.db.spu[sr].temp_ok = 0

                if (not (parset.as_float('voltage.5_0.min') <= noload[sr][1] <= parset.as_float('voltage.5_0.max')) or
                        not (parset.as_float('voltage.5_0.min') < fullload_3[sr][1] <= parset.as_float('voltage.5_0.max')) or
                        not (parset.as_float('voltage.5_0.min') <= fullload_5[sr][1] <= parset.as_float('voltage.5_0.max')) or
                        (noload[sr][1] - fullload_3[sr][1]) > parset.as_float('voltage.5_0.max-drop')):
                    self.db.spu[sr].rcu_ok = 0
                    logger.info("SPU voltage 5.0V out of range")

                if (not (parset.as_float('voltage.8_0.min') <= noload[sr][2] <= parset.as_float('voltage.8_0.max')) or
                        not (parset.as_float('voltage.8_0.min') <= fullload_3[sr][2] <= parset.as_float('voltage.8_0.max')) or
                        (noload[sr][2] - fullload_3[sr][2]) > parset.as_float('voltage.8_0.max-drop')):
                    self.db.spu[sr].lba_ok = 0
                    logger.info("SPU voltage 8.0V out of range")

                if (not (parset.as_float('voltage.48_0.min') <= noload[sr][3] <= parset.as_float('voltage.48_0.max')) or
                        not (parset.as_float('voltage.48_0.min') <= fullload_5[sr][3] <= parset.as_float('voltage.48_0.max')) or
                        (noload[sr][3] - fullload_5[sr][3]) > parset.as_float('voltage.48_0.max-drop')):
                    self.db.spu[sr].hba_ok = 0
                    logger.info("SPU voltage 48V out of range")

                if (not (parset.as_float('voltage.3_3.min') <= noload[sr][4] <= parset.as_float('voltage.3_3.max')) or
                        not (parset.as_float('voltage.3_3.min') <= fullload_3[sr][4] <= parset.as_float('voltage.3_3.max')) or
                        not (parset.as_float('voltage.3_3.min') <= fullload_5[sr][4] <= parset.as_float('voltage.3_3.max')) or
                        (noload[sr][4] - fullload_5[sr][4]) > parset.as_float('voltage.3_3.max-drop')):
                    self.db.spu[sr].spu_ok = 0
                    logger.info("SPU voltage 3.3V out of range")

        logger.info("=== Done SPU check ===")
        self.db.add_test_done('SPU')
        return
