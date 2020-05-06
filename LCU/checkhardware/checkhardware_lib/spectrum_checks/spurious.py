import logging
from .peakslib import *

logger = logging.getLogger('main.chk.spu..')
logger.debug("init logger")


def check_for_spurious(data, band, pol, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param pol: polarity to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    min_peak_pwr = parset.as_float('spurious.min-peak-pwr')
    passband = parset.as_int_list('spurious.passband')
    if passband is None:
        logger.warning("no passband found, use default 1:511")
        passband = list(range(1,512,1))
    data.set_passband(band, passband)

    info = list()

    _data = data.spectras(freq_band=band, polarity=pol, masked=True)
    max_data = ma.max(_data, axis=1)
    mean_data = ma.mean(_data, axis=1)
    median_spec = ma.mean(max_data, axis=0)
    peaks = SearchPeak(median_spec)
    if not peaks.valid_data:
        return info

    # first mask peaks available in all data
    peaks.search(delta=(min_peak_pwr / 2.0))  # deta=20 for HBA
    for peak, min_sb, max_sb in peaks.max_peaks:
        peakwidth = max_sb - min_sb
        if peakwidth > 8:
            continue
        min_sb = max(min_sb - 1, 0)
        max_sb = min(max_sb + 1, peaks.n_data - 1)
        logger.debug("mask sb %d..%d" % (min_sb, max_sb))
        for i in range(min_sb, max_sb, 1):
            mean_data[:, i] = ma.masked

    # search in all data for spurious
    for data_nr, rcu in enumerate(data.rcus(band, pol)):
        # logger.debug("rcu=%d  data_nr=%d" % (rcu, data_nr))
        peaks = SearchPeak(mean_data[data_nr, :])
        if peaks.valid_data:
            peaks.search(delta=min_peak_pwr)
            for peak, min_sb, max_sb in peaks.max_peaks:
                peakwidth = max_sb - min_sb
                if peakwidth > 10:
                    continue
                peak_val = peaks.get_peak_value(peak)
                if peakwidth < 100 and peak_val != NaN:
                    logger.debug("rcu=%d: spurious, subband=%d..%d, peak=%3.1fdB" % (
                                 rcu, min_sb, max_sb, peak_val))
            if peaks.n_max_peaks() > 10:
                # print data_nr, peaks.nMaxPeaks()
                info.append(rcu)

    data.reset_masked_sb(band)
    return info
