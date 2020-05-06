import logging
from .peakslib import *

logger = logging.getLogger('main.chk.fla..')
logger.debug("init logger")

def check_for_flat(data, band, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    min_pwr = parset.as_float('flat.mean-pwr.min')
    max_pwr = parset.as_float('flat.mean-pwr.max')

    _data = data.mean_spectras(freq_band=band, polarity='xy', masked=True)
    flat_info = list()
    for data_nr, rcu in enumerate(data.rcus(band, 'xy')):
        mean_signal = ma.mean(_data[data_nr, :])
        if min_pwr < mean_signal < max_pwr:
            logger.info("rcu=%d: cable probable off" % rcu)
            flat_info.append((rcu, mean_signal))
    return flat_info
