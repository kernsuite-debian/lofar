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

    down_info = list()
    shifted_info = list()
    start_sb = min(subbands)
    stop_sb = max(subbands)

    normal_center_sb = 294
    normal_bw_3db    = 45

    x_data = data.median_spectras(freq_band=band, polarity='x', masked=True)
    y_data = data.median_spectras(freq_band=band, polarity='y', masked=True)
    median_spectra_x = ma.median(x_data, axis=0)
    median_spectra_y = ma.median(y_data, axis=0)


    x_data_delta = x_data - median_spectra_x
    x_data_delta = x_data_delta + x_data_delta.min()
    y_data_delta = y_data - median_spectra_y
    y_data_delta = y_data_delta + y_data_delta.min()

    min_peak_width = 10

    # get some median information
    peaks = SearchPeak(median_spectra_x)
    if not peaks.valid_data:
        return down_info, shifted_info

    peaks.search(delta=3, min_width=min_peak_width)
    #logger.debug("found X peaks with bandwidth > %d = %s" % (min_peak_width, str([i[0] for i in peaks.max_peaks])))

    # search for nearest peak to center of subbands
    x_median_max_peak_val = 0.0
    x_median_max_peak_sb = 0
    x_median_min_sb = 0
    x_median_max_sb = 0
    min_gap = 500
    for max_pos, min_sb, max_sb in peaks.max_peaks:
        if abs(max_pos - normal_center_sb) < min_gap:
            min_gap = abs(max_pos - normal_center_sb)
            x_median_max_peak_val = peaks.get_peak_value(max_pos)
            x_median_max_peak_sb  = max_pos
            x_median_min_sb  = min_sb
            x_median_max_sb  = max_sb

    x_median_bandwidth = x_median_max_sb - x_median_min_sb
    x_median_subbands_pwr = float(ma.median(x_data[:, start_sb: stop_sb]))
    logger.debug("median X peak all rcu's in band %d .. %d : subband=%d, bw(3dB)=%d, median-value-band=%3.1fdB" % (
                 start_sb, stop_sb, x_median_max_peak_sb, x_median_bandwidth, x_median_subbands_pwr))

    down_info.append(('Xref', x_median_max_peak_sb, x_median_max_peak_val, x_median_bandwidth, x_median_subbands_pwr))


    peaks = SearchPeak(median_spectra_y)
    if not peaks.valid_data:
        return down_info, shifted_info

    peaks.search(delta=3, min_width=min_peak_width)
    #logger.debug("found Y peaks with bandwidth > %d = %s" % (min_peak_width, str([i[0] for i in peaks.max_peaks])))

    # search for nearest peak to center of subbands
    y_median_max_peak_val = 0.0
    y_median_max_peak_sb = 0
    y_median_min_sb = 0
    y_median_max_sb = 0
    min_gap = 500
    for max_pos, min_sb, max_sb in peaks.max_peaks:
        if abs(max_pos - normal_center_sb) < min_gap:
            min_gap = abs(max_pos - normal_center_sb)
            y_median_max_peak_val = peaks.get_peak_value(max_pos)
            y_median_max_peak_sb  = max_pos
            y_median_min_sb  = min_sb
            y_median_max_sb  = max_sb

    y_median_bandwidth = y_median_max_sb - y_median_min_sb
    y_median_subbands_pwr = float(ma.median(x_data[:, start_sb: stop_sb]))
    logger.debug("median Y peak all rcu's in band %d .. %d : subband=%d, bw(3dB)=%d, median-value-band=%3.1fdB" % (
                 start_sb, stop_sb, y_median_max_peak_sb, y_median_bandwidth, y_median_subbands_pwr))

    down_info.append(('Yref', y_median_max_peak_sb, y_median_max_peak_val, y_median_bandwidth, y_median_subbands_pwr))


    mean_pwr_array = zeros((data.max_rcus()), 'f')
    peaks_pwr_array = zeros((data.max_rcus()), 'f')
    peaks_sb_array = zeros((data.max_rcus()), 'i')
    peaks_bw_array = zeros((data.max_rcus()), 'i')

    # for all rcus fill above arrays with data
    for data_nr, rcu in enumerate(data.rcus(band, 'x')):
        mean_pwr_array[rcu] = float(ma.median(x_data[data_nr, start_sb: stop_sb]))
        peaks = SearchPeak(x_data_delta[data_nr, :])
        if peaks.valid_data:
            peaks.search(delta=3, min_width=min_peak_width)
            #logger.debug("RCU %d found X peaks with bandwidth > %d = %s" % (rcu, min_peak_width, str([i[0] for i in peaks.max_peaks])))

            # search for nearest peak to center of subbands
            max_peak_val = 0.0
            max_peak_sb = 0
            min_sb = 0
            max_sb = 0
            min_gap = 500
            for _max_pos, _min_sb, _max_sb in peaks.max_peaks:
                if _max_pos not in subbands:
                    continue
                if abs(_max_pos - normal_center_sb) < min_gap:
                    min_gap = abs(_max_pos - normal_center_sb)
                    max_peak_val = x_data[data_nr, _max_pos]
                    max_peak_sb  = _max_pos
                    min_sb  = _min_sb
                    max_sb  = _max_sb

            if max_peak_sb > 0:
                logger.debug("RCU %d X: max. peak(s) found on subband(s) %s" % (rcu, str([i[0] for i in peaks.max_peaks])))
                peaks = SearchPeak(x_data[data_nr, :])
                peak_bandwidth, _min_sb, _max_sb = peaks.get_peak_width(max_peak_sb, 3)
                # peakwidth, min_sb, max_sb = peaks.getPeakWidth(maxpeak_sb, delta)
                peaks_bw_array[rcu]  = peak_bandwidth
                peaks_pwr_array[rcu] = max_peak_val
                peaks_sb_array[rcu]  = max_peak_sb
            else:
                peaks = SearchPeak(x_data[data_nr, :])
                peak_bandwidth, _min_sb, _max_sb = peaks.get_peak_width(normal_center_sb, 3)
                peaks_bw_array[rcu] = peak_bandwidth
                peaks_sb_array[rcu] = normal_center_sb
                peaks_pwr_array[rcu] = x_data[data_nr, _max_pos]

    for data_nr, rcu in enumerate(data.rcus(band, 'y')):
        mean_pwr_array[rcu] = float(ma.median(y_data[data_nr, start_sb: stop_sb]))
        peaks = SearchPeak(y_data_delta[data_nr, :])
        if peaks.valid_data:
            peaks.search(delta=3, min_width=min_peak_width)
            #logger.debug("RCU %d found Y peaks with bandwidth > %d = %s" % (rcu, min_peak_width, str([i[0] for i in peaks.max_peaks])))

            # search for nearest peak to center of subbands
            max_peak_val = 0.0
            max_peak_sb = 0
            min_sb = 0
            max_sb = 0
            min_gap = 200
            for _max_pos, _min_sb, _max_sb in peaks.max_peaks:
                if _max_pos not in subbands:
                    continue
                if abs(_max_pos - normal_center_sb) < min_gap:
                    min_gap = abs(_max_pos - normal_center_sb)
                    max_peak_val = y_data[data_nr, _max_pos]
                    max_peak_sb  = _max_pos
                    min_sb  = _min_sb
                    max_sb  = _max_sb



            if max_peak_sb > 0:
                logger.debug("RCU %d Y: max. peak(s) found on subband(s) %s" % (rcu, str([i[0] for i in peaks.max_peaks])))
                peaks = SearchPeak(y_data[data_nr, :])
                peak_bandwidth, _min_sb, _max_sb = peaks.get_peak_width(max_peak_sb, 3)
                # peakwidth, min_sb, max_sb = peaks.getPeakWidth(maxpeak_sb, delta)
                peaks_bw_array[rcu]  = peak_bandwidth
                peaks_pwr_array[rcu] = max_peak_val
                peaks_sb_array[rcu]  = max_peak_sb
            else:
                peaks = SearchPeak(y_data[data_nr, :])
                peak_bandwidth, _min_sb, _max_sb = peaks.get_peak_width(normal_center_sb, 3)
                peaks_bw_array[rcu] = peak_bandwidth
                peaks_sb_array[rcu] = normal_center_sb
                peaks_pwr_array[rcu] = y_data[data_nr, _max_pos]

    # check for down or shifted tops of the noise-floor
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

        # if both polarity's not shifted and 1 pol is higher then average and the other is lower then average
        if abs(peaks_sb_array[x_rcu] - normal_center_sb) < 3 and abs(peaks_sb_array[y_rcu] - normal_center_sb) < 3:
            if (mean_pwr_array[x_rcu] < (x_median_subbands_pwr - 3.0) and mean_pwr_array[y_rcu] > (y_median_subbands_pwr + 3.0)):
                thunderstorm = True
            if (mean_pwr_array[y_rcu] < (y_median_subbands_pwr - 3.0) and mean_pwr_array[x_rcu] > (x_median_subbands_pwr + 3.0)):
                thunderstorm = True

        if thunderstorm:
            logger.debug("skip down test, probably thunderstorm active")
        else:
            if 66.0 < mean_pwr_array[x_rcu] < (x_median_subbands_pwr - 2.0):
                logger.debug("rcu=%d: mean signal in test band for X lower than normal" % x_rcu)
                x_value_trigger = True
            if 66.0 < mean_pwr_array[y_rcu] < (y_median_subbands_pwr - 2.0):
                logger.debug("rcu=%d: mean signal in test band for Y lower than normal" % y_rcu)
                y_value_trigger = True

            if abs(peaks_sb_array[x_rcu] - normal_center_sb) > 10 or abs(normal_bw_3db - peaks_bw_array[x_rcu]) > 10:
                if peaks_bw_array[x_rcu] > 3:
                    logger.debug("rcu=%d: X broken or antenna down" % x_rcu)
                    x_down_trigger = True
            if abs(peaks_sb_array[y_rcu] - normal_center_sb) > 10 or abs(normal_bw_3db - peaks_bw_array[y_rcu]) > 10:
                if peaks_bw_array[y_rcu] > 3:
                    logger.debug("rcu=%d: Y broken or antenna down" % y_rcu)
                    y_down_trigger = True

            if (x_value_trigger and x_down_trigger) and (y_value_trigger and y_down_trigger):
                down_info.append((x_rcu, peaks_sb_array[x_rcu], peaks_pwr_array[x_rcu], peaks_bw_array[x_rcu], mean_pwr_array[x_rcu]))
                down_info.append((y_rcu, peaks_sb_array[y_rcu], peaks_pwr_array[y_rcu], peaks_bw_array[y_rcu], mean_pwr_array[y_rcu]))
                #logger.debug("down_info=%s" % str(down_info))
            else:
                if (peaks_bw_array[x_rcu] > 20) and (abs(peaks_sb_array[x_rcu] - normal_center_sb) > 10):
                    logger.debug("rcu=%d: X-top shifted normal=%d, now=%d" % (
                                 x_rcu, normal_center_sb, peaks_sb_array[x_rcu]))
                    shifted_info.append((x_rcu, peaks_sb_array[x_rcu], normal_center_sb))
                if (peaks_bw_array[y_rcu] > 20) and (abs(peaks_sb_array[y_rcu] - normal_center_sb) > 10):
                    logger.debug("rcu=%d: Y-top shifted normal=%d, now=%d" % (
                                 y_rcu, normal_center_sb, peaks_sb_array[y_rcu]))
                    shifted_info.append((y_rcu, peaks_sb_array[y_rcu], normal_center_sb))


    # if more than half the antennes are down or shifted, skip test
    if len(down_info) > len(data.rcus(band, 'xy')) / 2:
        down_info = list()
    if len(shifted_info) > len(data.rcus(band, 'xy')) / 2:
        shifted_info = list()
    return down_info, shifted_info
