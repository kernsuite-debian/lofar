import logging
from .peakslib import *

logger = logging.getLogger('main.chk.rf_..')
logger.debug("init logger")


def check_rf_power(data, band, pol, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param pol: polarity to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    #logger.debug('parset= %s' % str(parset))
    subbands = parset.as_int_list('rf.subbands')
    min_signal = parset.as_float('rf.min-sb-pwr')
    low_deviation = parset.as_float('rf.negative-deviation')
    high_deviation = parset.as_float('rf.positive-deviation')

    logger.debug("band=%s pol=%s  subband=%s" % (
                  band, pol, str(subbands)))
    logger.debug("min_signal=%5.1fdB low_deviation=%5.1fdB high_deviation=%5.1fdB" % (
                  min_signal, low_deviation, high_deviation))

    signal_info = dict()
    test_info = dict()
    test_sb = None

    # _data = (rcus x secs x subbands), all data for given band and pol
    _data = data.spectras(freq_band=band, polarity=pol, masked=True)
    # 1 spectra with median from all rcu spectra (max from all seconds)
    median_spectra = ma.median(ma.max(_data, axis=1), axis=0)

    if len(subbands) > 1:
        peaks = SearchPeak(median_spectra)
        peaks.search(delta=6.0, min_width=2)
        maxval, binnr, minsb, maxsb = peaks.get_max_peak(sb_list=subbands)
        if maxval >= min_signal:
            test_sb = binnr
    else:
        test_sb = subbands[0]

    if not test_sb:
        test_info['valid'] = False
        test_info['subband'] = -1
        test_info['test_val'] = 0.0
        return test_info, signal_info

    test_sb_value = median_spectra[test_sb]

    test_info['subband'] = test_sb
    test_info['test_val'] = test_sb_value

    # logger.debug("test_sb_value=%s  min_signal=%s" % (str(test_sb_value), str(min_signal)))
    if test_sb_value > min_signal:
        test_info['valid'] = True
    else:
        test_info['valid'] = False

    # sb_data = rcus values, median value of total seconds
    sb_data = ma.max(data.subbands(freq_band=band, polarity=pol, sb_set=test_sb, masked=True), axis=1)
    rcu_list = data.rcus(band=band, polarity=pol)
    logger.debug("used test_sb=%d" % test_sb)
    #logger.debug("sb_data=%s" % str(sb_data))
    for data_nr, rcu in enumerate(rcu_list):
        # logger.debug("data_nr=%d  rcu=%d  val=%5.1fdB" % (data_nr, rcu, sb_data[data_nr]))
        if np.ma.is_masked(sb_data[data_nr]):
            signal_info[str(rcu)] = {'value': 0.0, 'status': 'masked'}
        elif sb_data[data_nr] < 2.0:
            signal_info[str(rcu)] = {'value': sb_data[data_nr], 'status': 'no_signal'}
        elif 55.0 < sb_data[data_nr] < 65.0:
            signal_info[str(rcu)] = {'value': sb_data[data_nr], 'status': 'no_power'}
        elif sb_data[data_nr] < (test_sb_value + low_deviation):
            signal_info[str(rcu)] = {'value': sb_data[data_nr], 'status': 'low'}
        elif sb_data[data_nr] > (test_sb_value + high_deviation):
            signal_info[str(rcu)] = {'value': sb_data[data_nr], 'status': 'high'}
        else:
            signal_info[str(rcu)] = {'value': sb_data[data_nr], 'status': 'normal'}

    return test_info, signal_info
