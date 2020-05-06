import logging
from .peakslib import *

logger = logging.getLogger('main.chk.sho..')
logger.debug("init logger")


def check_for_short(data, band, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    min_pwr = parset.as_float('short.mean-pwr.min')
    max_pwr = parset.as_float('short.mean-pwr.max')

    _data = data.mean_spectras(freq_band=band, polarity='xy', masked=True)
    short_info = list()
    for data_nr, rcu in enumerate(data.rcus(band, 'xy')):
        mean_signal = ma.mean(_data[data_nr, :])
        if min_pwr < mean_signal < max_pwr:
            logger.info("rcu=%d: cable shorted" % rcu)
            short_info.append((rcu, mean_signal))
    return short_info
