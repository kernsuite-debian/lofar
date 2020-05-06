import logging
from .peakslib import *

logger = logging.getLogger('main.chk.noi..')
logger.debug("init logger")

def check_for_noise(data, band, pol, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param pol: polarity to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    low_deviation = parset.as_float('noise.negative-deviation')
    high_deviation = parset.as_float('noise.positive-deviation')
    max_diff = parset.as_float('noise.max-difference')
    passband = parset.as_int_list('noise.passband')
    if passband is None:
        logger.warning("no passband found, use default 1:511")
        passband = list(range(1,512,1))
    data.set_passband(band, passband)

    _data = data.spectras(freq_band=band, polarity=pol, masked=True)
    #logger.info("data shape %s" %(str(_data.shape)))
    high_info = list()
    low_info = list()
    jitter_info = list()

    ref_value = float(ma.median(_data))
    # loop over rcus
    for data_nr, rcu in enumerate(data.rcus(band, pol)):
        # logger.debug("rcu=%d  data_nr=%d" %(rcu, data_nr))
        data_nr_value = float(ma.median(_data[data_nr, :, :]))
        if data_nr_value < (ref_value + low_deviation):
            logger.debug("data_nr=%d: masked, low signal, ref=%5.3f val=%5.3f" % (data_nr, ref_value, data_nr_value))
            low_info.append((rcu, _data[data_nr, :, :].min(), -1, (ref_value+low_deviation),
                            (_data[data_nr, :, :].max() - _data[data_nr, :, :].min())))
            data.mask_rcu(rcu)
    spec_median = ma.median(_data, axis=2)
    spec_max = spec_median.max(axis=1)
    spec_min = spec_median.min(axis=1)
    ref_value = float(ma.median(_data))
    ref_diff = float(ma.median(spec_max) - ma.median(spec_min))
    ref_std = float(ma.std(spec_median))
    # high_limit = ref_value + min(max((ref_std * 3.0),0.75), high_deviation)
    high_limit = ref_value + max((ref_std * 3.0), high_deviation)
    low_limit = ref_value + min((ref_std * -3.0), low_deviation)
    n_secs = _data.shape[1]
    logger.debug("median-signal=%5.3fdB, median-fluctuation=%5.3fdB, std=%5.3f, high_limit=%5.3fdB low_limit=%5.3fdB" % (
                 ref_value, ref_diff, ref_std, high_limit, low_limit))
    # loop over rcus
    for data_nr, rcu in enumerate(data.rcus(band, pol)):
        # logger.debug("rcu=%d  data_nr=%d" %(rcu, data_nr))
        peaks = SearchPeak(_data[data_nr, 0, :])
        if not peaks.valid_data:
            return low_info, high_info, jitter_info
        peaks.search(delta=10.0)
        if peaks.n_max_peaks() >= 30:
            logger.debug("rcu=%d: found %d peaks, skip noise test" % (rcu, peaks.n_max_peaks()))
        else:
            n_bad_high_secs = 0
            n_bad_low_secs = 0
            if _data.shape[1] == 1:
                n_bad_high_secs = 1
                n_bad_low_secs = 1

            data_nr_max_diff = spec_max[data_nr] - spec_min[data_nr]
            # logger.debug("data_nr_max_diff %f" %(data_nr_max_diff))
            # loop over secs
            for val in spec_median[data_nr, :]:
                # logger.debug("data_nr=%d: high-noise value=%5.3fdB  max-ref-value=%5.3fdB" %(data_nr, val, ref_value))
                if val > high_limit:
                    n_bad_high_secs += 1

                if val < low_limit:
                    n_bad_low_secs += 1

            if n_bad_high_secs > 1:
                high_info.append((rcu, spec_max[data_nr], n_bad_high_secs, high_limit, data_nr_max_diff))
                logger.debug("rcu=%d: max-noise=%5.3f  %d of %d seconds bad" % (
                             rcu, spec_max[data_nr], n_bad_high_secs, n_secs))

            if n_bad_low_secs > 1:
                low_info.append((rcu, spec_min[data_nr], n_bad_low_secs, low_limit, data_nr_max_diff))
                logger.debug("rcu=%d: min-noise=%5.3f %d of %d seconds bad" % (
                             rcu, spec_min[data_nr], n_bad_low_secs, n_secs))

            if (n_bad_high_secs == 0) and (n_bad_low_secs == 0):
                max_cnt = 0
                min_cnt = 0
                if data_nr_max_diff > (ref_diff + max_diff):
                    check_high_value = ref_value + (ref_diff / 2.0)
                    check_low_value = ref_value - (ref_diff / 2.0)
                    for val in spec_median[data_nr, :]:
                        if val > check_high_value:
                            max_cnt += 1
                        if val < check_low_value:
                            min_cnt += 1

                    # minimal 20% of the values must be out of the check band
                    secs = _data.shape[1]
                    if max_cnt > (secs * 0.10) and min_cnt > (secs * 0.10):
                        n_bad_jitter_secs = max_cnt + min_cnt
                        jitter_info.append((rcu, data_nr_max_diff, ref_diff, n_bad_jitter_secs))
                    logger.debug("rcu=%d: max spectrum fluctuation %5.3f dB" % (rcu, data_nr_max_diff))

    data.reset_masked_sb(band)
    return low_info, high_info, jitter_info
