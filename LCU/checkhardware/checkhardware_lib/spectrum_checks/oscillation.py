import logging
from .peakslib import *


logger = logging.getLogger('main.chk.osc..')
logger.debug("init logger")


def check_for_oscillation(data, band, pol, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param pol: polarity to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    min_peak_pwr = parset.as_float('oscillation.min-peak-pwr')
    passband = parset.as_int_list('oscillation.passband')
    if passband is None:
        logger.warning("no passband found, use default 1:511")
        passband = list(range(1,512,1))
    data.set_passband(band, passband)

    info = list()
    _data = data.spectras(freq_band=band, polarity=pol, masked=True)
    mean_spectras = ma.mean(_data, axis=1)
    mean_spectra = ma.mean(mean_spectras, axis=0)
    mean_low = ma.mean(_data.min(axis=1))
    info.append((-1, 0, 0, 0))

    for data_nr, rcu in enumerate(data.rcus(band, pol)):
        # logger.debug("rcu=%d  rcu_bin=%d" %(rcu, rcu_bin))
        peaks = SearchPeak(mean_spectras[data_nr, :] - mean_spectra)
        if peaks.valid_data:
            peaks.search(delta=min_peak_pwr, min_width=2, max_width=8)
            max_val = mean_spectras[data_nr, :].max()
            max_n_peaks = peaks.n_max_peaks()
            max_sum_peaks = peaks.get_sum_peaks()

            bin_low = _data[data_nr, :, :].min(axis=0).mean()

            logger.debug("rcu=%d: number-of-peaks=%d  max_value=%3.1f  peaks_sum=%5.3f low_value=%3.1f" % (
                          rcu, max_n_peaks, max_val, max_sum_peaks, bin_low))

            out_of_band_peaks = 0
            for peak_sb, min_sb, max_sb in peaks.max_peaks:
                if peak_sb in range(0, 25, 1):
                    out_of_band_peaks += 1
                if peak_sb in range(488, 512, 1):
                    out_of_band_peaks += 1
                if out_of_band_peaks >= 2:
                    logger.debug("detected out of band peaks")
                    # info.append((rcu, max_sum_peaks, max_n_peaks, bin_low))
                    continue

            if max_n_peaks > 5:
                if bin_low > (mean_low + 2.0):  # peaks.getSumPeaks() > (median_sum_peaks * 2.0):
                    logger.debug("detected peaks in complete band")
                    info.append((rcu, max_sum_peaks, max_n_peaks, bin_low))
                    continue

            if max_val > 150.0:  # only one high peek
                logger.debug("detected peak > 150 dB")
                info.append((rcu, max_sum_peaks, max_n_peaks, bin_low))
                continue

    data.reset_masked_sb(band)
    return info  # (sorted(info,reverse=True))
