from .peakslib import *

logger = logging.getLogger('main.chk.dow..')
logger.debug("init logger")

def check_for_down(data, band, parset):
    """
    :param data: recorded antenna data data
    :param band: band to check
    :param parset: parameterset with check settings
    :return: list with found failures
    """
    subbands =parset.as_int_list('down.passband')
    if subbands is None:
        logger.warning("no passband found, use default 250:350")
        subbands = list(range(250,351,1))

    # _data = (rcus x subbands)
    _data = data.median_spectras(freq_band=band, polarity='xy', masked=True)
    down_info = list()
    shifted_info = list()
    start_sb = min(subbands)
    stop_sb = max(subbands)
    center_sb = (stop_sb + start_sb) / 2

    peaks = SearchPeak(ma.median(_data, axis=0))
    if not peaks.valid_data:
        return down_info, shifted_info

    min_peak_width = 3
    peaks.search(delta=3, min_width=min_peak_width)
    logger.debug("found peaks with bandwidth > %d = %s" % (min_peak_width, str([i[0] for i in peaks.max_peaks])))

    # search for nearest peak to center of subbands
    median_max_peak_val = 0.0
    median_max_peak_sb = 0
    median_min_sb = 0
    median_max_sb = 0
    min_gap = 100
    for max_pos, min_sb, max_sb in peaks.max_peaks:
        if abs(max_pos - center_sb) < min_gap:
            min_gap = abs(max_pos - center_sb)
            median_max_peak_val = peaks.get_peak_value(max_pos)
            median_max_peak_sb  = max_pos
            median_min_sb  = min_sb
            median_max_sb  = max_sb

    median_bandwidth = median_max_sb - median_min_sb

    #(median_max_val, median_max_sb, min_sb, max_sb) = peaks.get_max_peak(sb_list=subbands)
    # peakwidth, min_sb, max_sb = peaks.getPeakWidth(median_max_sb, delta)
    # median_max_sb += start_sb

    median_subbands_pwr = float(ma.median(_data[:, start_sb: stop_sb]))
    logger.debug("reference peak in band %d .. %d : subband=%d, bw(3dB)=%d, median-value-band=%3.1fdB" % (
                 start_sb, stop_sb, median_max_peak_sb, median_bandwidth, median_subbands_pwr))

    down_info.append((-1, median_max_peak_sb, median_max_peak_val, median_bandwidth, median_subbands_pwr))


    mean_pwr_array = zeros((data.max_rcus()), 'f')
    peaks_pwr_array = zeros((data.max_rcus()), 'f')
    peaks_sb_array = zeros((data.max_rcus()), 'i')
    peaks_bw_array = zeros((data.max_rcus()), 'i')

    for data_nr, rcu in enumerate(data.rcus(band, 'xy')):
        mean_pwr_array[rcu] = float(ma.mean(_data[data_nr, start_sb: stop_sb]))
        peaks = SearchPeak(_data[data_nr, :])
        if peaks.valid_data:
            peaks.search(delta=3, min_width=3)

            # search for nearest peak to center of subbands
            max_peak_val = 0.0
            max_peak_sb = 0
            min_sb = 0
            max_sb = 0
            min_gap = 100
            for _max_pos, _min_sb, _max_sb in peaks.max_peaks:
                if abs(_max_pos - center_sb) < min_gap:
                    min_gap = abs(_max_pos - center_sb)
                    max_peak_val = peaks.get_peak_value(max_pos)
                    max_peak_sb  = _max_pos
                    min_sb  = _min_sb
                    max_sb  = _max_sb

            peak_bandwidth = max_sb - min_sb

            #(maxpeak_val, maxpeak_sb, min_sb, max_sb) = peaks.get_max_peak(sb_list=subbads)

            if max_peak_sb > 0:
                # peakwidth, min_sb, max_sb = peaks.getPeakWidth(maxpeak_sb, delta)
                peaks_bw_array[rcu]  = peak_bandwidth
                peaks_pwr_array[rcu] = max_peak_val
                peaks_sb_array[rcu]  = max_peak_sb
            else:
                peaks_bw_array[rcu] = stop_sb - start_sb
                peaks_sb_array[rcu] = (stop_sb + start_sb) / 2
                peaks_pwr_array[rcu] = peaks.get_peak_value(peaks_sb_array[rcu])


    x_rcus = data.rcus(band, 'x')
    for x_rcu in x_rcus:
        if data.mode(x_rcu) in (1, 2):
            y_rcu = x_rcu - 1
        else:
            y_rcu = x_rcu + 1
        x_value_trigger = False
        x_down_trigger = False
        y_value_trigger = False
        y_down_trigger = False
        thunderstorm = False
        logger.debug("rcu=%d: X-top, sb=%d, pwr=%3.1fdB, bw=%d, mean-value-band=%3.1f" % (
                     x_rcu, peaks_sb_array[x_rcu], peaks_pwr_array[x_rcu], peaks_bw_array[x_rcu], mean_pwr_array[x_rcu]))
        logger.debug("rcu=%d: Y-top, sb=%d, pwr=%3.1fdB, bw=%d, mean-value-band=%3.1f" % (
                     y_rcu, peaks_sb_array[y_rcu], peaks_pwr_array[y_rcu], peaks_bw_array[y_rcu], mean_pwr_array[y_rcu]))

        # if both polaritys not shifted and 1 pol is higher then average and the other is lower then average
        if abs(peaks_sb_array[x_rcu] - median_max_sb) < 3 and abs(peaks_sb_array[y_rcu] - median_max_sb) < 3:
            if (mean_pwr_array[x_rcu] < (median_subbands_pwr - 3.0) and mean_pwr_array[y_rcu] > (median_subbands_pwr + 3.0)):
                thunderstorm = True
            if (mean_pwr_array[y_rcu] < (median_subbands_pwr - 3.0) and mean_pwr_array[x_rcu] > (median_subbands_pwr + 3.0)):
                thunderstorm = True

        if thunderstorm:
            logger.debug("skip down test, probably thunderstorm active")
        else:
            if 66.0 < mean_pwr_array[x_rcu] < (median_subbands_pwr - 2.0):
                logger.debug("rcu=%d: mean signal in test band for X lower than normal" % x_rcu)
                x_value_trigger = True
            if 66.0 < mean_pwr_array[y_rcu] < (median_subbands_pwr - 2.0):
                logger.debug("rcu=%d: mean signal in test band for Y lower than normal" % y_rcu)
                y_value_trigger = True

            if abs(peaks_sb_array[x_rcu] - median_max_peak_sb) > 10 or abs(median_bandwidth - peaks_bw_array[x_rcu]) > 10:
                if peaks_bw_array[x_rcu] > 3:
                    logger.debug("rcu=%d: X broken or antenna down" % x_rcu)
                    x_down_trigger = True
            if abs(peaks_sb_array[y_rcu] - median_max_peak_sb) > 10 or abs(median_bandwidth - peaks_bw_array[y_rcu]) > 10:
                if peaks_bw_array[y_rcu] > 3:
                    logger.debug("rcu=%d: Y broken or antenna down" % y_rcu)
                    y_down_trigger = True

            if (x_value_trigger and x_down_trigger) or (y_value_trigger and y_down_trigger):
                down_info.append((x_rcu, peaks_sb_array[x_rcu], peaks_pwr_array[x_rcu], peaks_bw_array[x_rcu], mean_pwr_array[x_rcu]))
                down_info.append((y_rcu, peaks_sb_array[y_rcu], peaks_pwr_array[y_rcu], peaks_bw_array[x_rcu], mean_pwr_array[y_rcu]))
            else:
                if (peaks_bw_array[x_rcu] > 20) and (abs(peaks_sb_array[x_rcu] - median_max_peak_sb) > 10):
                    logger.debug("rcu=%d: X-top shifted normal=%d, now=%d" % (
                                 x_rcu, median_max_peak_sb, peaks_sb_array[x_rcu]))
                    shifted_info.append((x_rcu, peaks_sb_array[x_rcu], median_max_peak_sb))
                if (peaks_bw_array[y_rcu] > 20) and (abs(peaks_sb_array[y_rcu] - median_max_peak_sb) > 10):
                    logger.debug("rcu=%d: Y-top shifted normal=%d, now=%d" % (
                                 y_rcu, median_max_peak_sb, peaks_sb_array[y_rcu]))
                    shifted_info.append((y_rcu, peaks_sb_array[y_rcu], median_max_peak_sb))


    # if more than half the antennes are down or shifted, skip test
    if len(down_info) > (_data.shape[0] / 2):
        down_info = list()
    if len(shifted_info) > (_data.shape[0] / 2):
        shifted_info = list()
    return down_info, shifted_info
