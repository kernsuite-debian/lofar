import logging
from .peakslib import *


logger = logging.getLogger('main.chk.sum..')
logger.debug("init logger")


def check_for_summator_noise(data, band, pol, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param pol: polarity to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    min_peak_pwr = parset.as_float('summator-noise.min-peak-pwr')
    passband = parset.as_int_list('summator-noise.passband')
    if passband is None:
        logger.warning("no passband found, use default 1:511")
        passband = list(range(1,512,1))
    data.set_passband(band, passband)

    sn_info = list()  # summator noise
    _data = data.spectras(freq_band=band, polarity=pol, masked=True)

    n_secs = _data.shape[1]
    secs = (n_secs//2,n_secs-1)

    for data_nr, rcu in enumerate(data.rcus(band, pol)):
        # logger.debug("rcu=%d  data_nr=%d" %(rcu, data_nr))
        sum_sn_peaks = 0
        max_peaks = 0
        for sec in secs:
            peaks_ref = SearchPeak(_data[:, sec, :].mean(axis=0))
            if peaks_ref.valid_data:
                peaks_ref.search(delta=min_peak_pwr, min_width=3)

            peaks = SearchPeak(_data[data_nr, sec, :])
            if peaks.valid_data:
                peaks.search(delta=min_peak_pwr, skip_list=peaks_ref.max_peaks)
                n_peaks = peaks.n_max_peaks()
                if n_peaks < 3:
                    continue
                sn_peaks = 0
                last_sb, min_sb, max_sb = peaks.max_peaks[0]
                last_sb_val = peaks.get_peak_value(last_sb)
                for sb, min_sb, max_sb in peaks.max_peaks[1:]:
                    sb_val = peaks.get_peak_value(sb)

                    sb_diff = sb - last_sb
                    sb_val_diff = sb_val - last_sb_val
                    if sb_diff in (3, 4):
                        if abs(sb_val_diff) < 2.0:
                            sn_peaks += 1
                        elif sn_peaks < 6 and abs(sb_val_diff) > 3.0:
                            sn_peaks = 0
                    last_sb = sb
                    last_sb_val = sb_val

                sum_sn_peaks += sn_peaks
                max_peaks = max(max_peaks, n_peaks)

        if sum_sn_peaks > (len(secs) * 3.0):
            sn_peaks = sum_sn_peaks / len(secs)
            sn_info.append((rcu, sn_peaks, max_peaks))

    data.reset_masked_sb(band)
    return sn_info
