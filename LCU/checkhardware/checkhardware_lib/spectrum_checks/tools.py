import logging
from .peakslib import *

logger = logging.getLogger('main.chk.too..')
logger.debug("init logger")

def psd(data, sampletime):
    """
    :param data: data for fft
    :param sampletime: used sampletime
    :return: fft
    """
    if data.ndim != 1:
        return [], []
    fft_data = fft.fft(data)
    n = fft_data.size
    psd_freq = fft.fftfreq(n, sampletime)
    _psd = power(abs(fft_data), 2) / n
    return _psd[:n // 2], psd_freq[:n // 2]
