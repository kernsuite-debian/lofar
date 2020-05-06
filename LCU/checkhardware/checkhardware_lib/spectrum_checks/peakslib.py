
from numpy import ma, fft, power, arange, isscalar, NaN, Inf, zeros
from sys import exit
import logging
from checkhardware_lib.data import *

logger = logging.getLogger('main.chk.pea..')
logger.debug("init logger")

class SearchPeak(object):
    """
    search for all peaks (min & max) in spectra
    """
    def __init__(self, data):
        self.valid_data = False
        if len(data.shape) == 1:
            self.valid_data = True
            self.data = data.copy()
            self.n_data = len(data)
            self.max_peaks = []
            self.min_peaks = []
        return

    def search(self, delta, min_width=1, max_width=100, skip_list=()):
        self.max_peaks = []
        self.min_peaks = []

        x = arange(0, len(self.data), 1)

        if not isscalar(delta):
            exit('argument delta must be a scalar')

        if delta <= 0:
            exit('argument delta must be positive')

        maxval, minval = -200, 200
        maxpos, minpos = 1, 1

        lookformax = True

        # add subband to skiplist
        skiplist = []
        if len(skip_list) > 0:
            for max_pos, min_sb, max_sb in skip_list:
                for sb in range(min_sb, max_sb+1, 1):
                    skiplist.append(sb)

        # skip subband 0 (always high signal)
        for i in range(1, self.n_data, 1):
            # sleep(0.001)
            if ma.count_masked(self.data) > 1 and self.data.mask[i] is True:
                continue

            now = self.data[i]
            if now > maxval:
                maxval = now
                maxpos = x[i]

            if now < minval:
                minval = now
                minpos = x[i]

            if lookformax:
                if now < (maxval - delta):
                    if maxpos not in skiplist:
                        peakwidth, min_sb, max_sb = self.get_peak_width(maxpos, delta)
                        # logger.debug("maxpos=%d, width=%d" %(maxpos, peakwidth))
                        if min_width < peakwidth < max_width:
                            self.max_peaks.append([maxpos, min_sb, max_sb])
                    minval = now
                    minpos = x[i]
                    lookformax = False
            else:
                if now > (minval + delta):
                    if minpos not in skiplist:
                        self.min_peaks.append([minpos, minpos, minpos])
                    maxval = now
                    maxpos = x[i]
                    lookformax = True

        # if no peak found with the given delta, return maximum found
        if len(self.max_peaks) == 0:
            self.max_peaks.append([-1, -1, -1])
        return

    # return data[nr]
    def get_peak_value(self, nr):
        try:
            return self.data[nr]
        except IndexError:
            return NaN
        except:
            raise

    def get_peak_width(self, nr, delta):
        peakval = self.data[nr]
        minnr = nr
        maxnr = nr
        for sb in range(nr, 0, -1):
            if self.data[sb] < peakval:
                minnr = sb
            if self.data[sb] <= (peakval - delta):
                break
        for sb in range(nr, self.data.shape[0], 1):
            if self.data[sb] < peakval:
                maxnr = sb
            if self.data[sb] <= (peakval - delta):
                break
        return maxnr-minnr, minnr, maxnr

    # return value and subband nr
    def get_max_peak(self, sb_list=None):
        maxval = 0.0
        minsb = 0.0
        maxsb = 0.0
        binnr = -1
        if sb_list is None:
            check_range = list(range(512))
        else:
            check_range = sb_list
        for peak, min_sb, max_sb in self.max_peaks:
            if peak not in check_range:
                continue
            if self.data[peak] > maxval:
                maxval = self.data[peak]
                binnr = peak
                minsb = min_sb
                maxsb = max_sb
        return maxval, binnr, minsb, maxsb

    def get_sum_peaks(self):
        peaksum = 0.0
        for peak, min_sb, max_sb in self.max_peaks:
            peaksum += self.data[peak]
        return peaksum

    # return value and sbband nr
    def get_min_peak(self):
        minval = Inf
        nr_bin = -1

        for peak in self.min_peaks:
            if self.data[peak] < minval:
                minval = self.data[peak]
                nr_bin = peak
        return minval, nr_bin

    def n_max_peaks(self):
        return len(self.max_peaks)
