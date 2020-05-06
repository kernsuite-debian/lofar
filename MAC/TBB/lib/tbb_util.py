from lofar.mac.tbb.tbb_config import *
from lxml import etree
from lofar.common.cep4_utils import *
from lofar.common.subprocess_utils import check_output_returning_strings

import logging
logger = logging.getLogger(__name__)

def wrap_remote_composite_command(cmd):
    if isinstance(cmd, list):
        cmd = ' '.join(cmd)

    # wrap the whole remote commandline in double quotes
    # (because multiple ';'-seperated commands are interpreted on the way somewhere)
    cmd = '"%s"' % cmd
    return cmd

def get_cpu_nodes_running_tbb_datawriter_via_slurm():
    '''
    Get the cpu node numbers where a tbb datawriter is currently running via slurm
    :return: list cpu node numbers (ints)
    '''
    cmd = '''sacct --name=run-tbbwriter --user=lofarsys -o nodelist%128 -n -s R -X'''
    cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
    logger.debug('executing command: %s', ' '.join(cmd))
    out = check_output_returning_strings(cmd).strip()
    logger.debug('  out: %s', out)
    return convert_slurm_nodes_string_to_node_number_list(out)

def get_cpu_nodes_running_tbb_datawriter(timeout=60):
    '''
    Get the cpu node numbers where any tbb datawriter is currently running (via slurm via any other means)
    :return: list cpu node numbers (ints)
    '''
    result = []
    available_nodes = get_cep4_up_and_running_cpu_nodes()
    procs = {}
    start = datetime.utcnow()

    for node_nr in available_nodes:
        cmd = 'pgrep TBB_Writer'
        cmd = wrap_command_in_cep4_cpu_node_ssh_call(cmd, node_nr, via_head=True)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        procs[node_nr] = proc

    while not all(p.poll() is not None for p in list(procs.values())):
        sleep(0.1)
        if datetime.utcnow() - start > timedelta(seconds=timeout):
            break

    for node_nr, proc in list(procs.items()):
        if proc.returncode == 0:
            result.append(node_nr)

    return result

def get_cpu_nodes_available_for_tbb_datawriters_sorted_by_load(min_nr_of_free_nodes=1, max_normalized_load=0.5):
    """
    Get a list of cpu node numbers which are available to start tbb datawriters on.
    That is the set of cpu nodes which are available, and are not runnig any tbbwriters at the moment.
    The list is sorted ascending by load.
    :param int min_nr_of_free_nodes: return at least this amount of free nodes, even if their load is too high.
                                     If not enough nodes are up, then of course it cannot be guaranteed that we return this amount.
    :param float max_normalized_load: filter free nodes which are at most max_normalized_load
    :return: list of node numbers
    """
    all_available_nodes = set(get_cep4_up_and_running_cpu_nodes())
    nodes_running_datawriters1 = set(get_cpu_nodes_running_tbb_datawriter_via_slurm())
    nodes_running_datawriters2 = set(get_cpu_nodes_running_tbb_datawriter())
    nodes_running_datawriters = nodes_running_datawriters1.union(nodes_running_datawriters2)
    logger.info("nodes_running_datawriters: %s", nodes_running_datawriters)

    free_available_nodes = sorted(list(all_available_nodes - nodes_running_datawriters))
    logger.info("free_available_nodes: %s", free_available_nodes)

    filtered_sorted_free_available_nodes = get_cep4_available_cpu_nodes_sorted_ascending_by_load(max_normalized_load,
                                                                                                 min_nr_of_free_nodes,
                                                                                                 free_available_nodes)
    logger.info("filtered_sorted_free_available_nodes: %s", filtered_sorted_free_available_nodes)
    return filtered_sorted_free_available_nodes

def split_stations_by_boardnumber(stations):
    """
    Stations are assumed to have 12 boards unless their name starts with 'cs' / 'rs'
    Some alias groups are known to have only 6 boards, but others will be assumed to have 12 boards.

    :param stations: comma-separated list of stations
    :return: dict of lists with tbb board count as key and list of stations as value
    """
    logger.info('Determining number of TBB boards of provided stations')

    def has6boards(station):
        return station in groups_with_6boards or station.lower()[:2] in ['cs', 'rs']

    if isinstance(stations, str):
        stationlist = stations.split(',')
    else:
        # assume stations is iterable and can be converted to a list
        stationlist = list(stations)

    stationslists = {6: [x for x in stationlist if has6boards(x)],
                     12: [x for x in stationlist if not has6boards(x)]}

    stationslists = {k: v for k, v in list(stationslists.items()) if len(v) > 0} # remove empty
    logger.debug("Board counts: %s" % stationslists)
    return stationslists


def expand_range(input_range):
    """
    Take an input string that describes an integer range "7-29" and return the individual numbers in that range as strings in a list ["7", "8", ..., "29"].
    :param input_range:  An input string of the format "7-29" or "16"
    :return:  A list of the individual integer numbers in the range as strings.
    """
    items = []
    index = input_range.find("-")
    if index == 0 or index == (len(input_range) - 1):
        raise ValueError("Cannot convert %s into a number!" % (input_range))
    elif index == -1:
        # Could be a single value.  Check if it is a digit.
        if input_range.isdigit() is True:
            items.append(input_range)
        else:
            raise ValueError("Cannot convert %s into a number!" % (input_range))
    else:
        range_begin = input_range[:index]
        if range_begin.isdigit() is True:
            range_begin = int(range_begin)
        else:
            raise ValueError("Cannot convert %s into a number!" % (range_begin))
        range_end = input_range[(index + 1):]
        if range_end.isdigit() is True:
            range_end = int(range_end)
        else:
            raise ValueError("Cannot convert %s into a number!" % (range_end))
        for element in range(range_begin, range_end + 1):
            items.append(str(element))
    return items


def expand_list(input_list):
    """
    Convert an input string of the form "1,17-33,64,1299-1344" to a list of strings that consists of each individual integer that is given and of all integers in every range.
    :param input_list:  An input string containing integer ranges "7-29" or individual integers "33" all separated by ",".
    :return:  A list of all the individual integer numbers and of all the integers in the ranges.  The list elements are strings.
    """
    items = []
    split_by_comma = input_list.split(",")
    for item in split_by_comma:
        if item.isdigit() is True:
            items.append(item)
        else:
            items += expand_range(item)

    logger.debug("Input list: \"%s\"\nFound these elements in the list: \"%s\"" % (input_list, items))
    return items


def calculate_adjusted_start_time(dm, start_time, sub_band):
    """
    Calculate an adjusted start time for data in a sub-band in TBB memory.
    Interstellar and intergalactic dispersion smear out electro-magnetic pulses
    so that higher frequencies of a pulse will arrive earlier at a receiver
    than lower frequencies of the same pulse.  Mostly free electrons in the path
    of the pulse "delay" the different frequencies.
    The three parameters, dispersion measure, recording start time of the
    highest frequency and the target frequency as sub-band allow us to
    calculate the recording start time for the target frequency.  The calculated
    start time will always be >= the start time of the highest frequency.
    :param dm:  Dispersion measure
    :param start_time:  Start time of the entire TBB
    :param sub_band:  The sub-band for which the time delay shall be calculated.
    :return:  A tuple of two values.  The first value represents the adjusted
    start time in seconds, the second value represents the remainder of the
    adjusted start time in units of 5 microseconds.
    """
    sub_band_frequency = lowest_frequency + sub_band_width * sub_band
    time_delay_sub_band = k_DM * dm * (sub_band_frequency**(-2) - highest_frequency**(-2))
    adjusted_start_time = start_time + time_delay_sub_band

    # The TBB needs the adjusted start time as two parameters:  full seconds and
    # the fractional remainder in units of 5 microseconds.
    full_seconds = int(adjusted_start_time)
    slice_nr = int((adjusted_start_time - full_seconds) / slice_size)

    logger.info("Calculated the sub-band start time:  "
        "lowest frequency = %fMHz, "
        "highest frequency = %fMHz, "
        "sub-band width = %fMHz, "
        "slice size = %fs, "
        "sub-band = %d, "
        "sub-band frequency = %fMHz, "
        "start time of the highest frequency = %fs, "
        "dispersion measure = %f, "
        "calculated start time delay = %fs, "
        "sub-band start time = %fs, "
        "sub-band start time, seconds only = %ds, "
        "sub-band start time, slice # = %d."
        % (lowest_frequency, highest_frequency, sub_band_width, slice_size,
           sub_band, sub_band_frequency, start_time, dm, time_delay_sub_band,
           adjusted_start_time, full_seconds, slice_nr))
    return (full_seconds, slice_nr)


# Todo: Consider to move this elsewhere, once we know where this parsing is supposed to happen eventually
def parse_parset_from_voevent(voevent):
        """
        Parse the voevent for required values and create a parset from those.
        :param voevent: the voevent as xml string # see https://export.arxiv.org/pdf/1710.08155
        :return: A parset dict
        """
        logger.debug('Parsing VOEvent: %s ' % voevent)
        try:
            root = etree.fromstring(voevent)
            dm_param = root.find("./What/Group[@name='event parameters']/Param[@name='dm']")
            dm_unit = dm_param.attrib['unit']
            dm_value = dm_param.attrib['value']
            trigger_version = root.attrib['version']
            trigger_id = root.attrib['ivorn'] # todo: clarify: how does this relate to the RT TriggerID (in OTDB)?
            isotime = root.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Time/TimeInstant/ISOTime').text
            coordsys = root.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoordSystem').attrib['id']
            ra = root.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C1').text # I bet there is a funny story about this structure... wtf?!
            dec = root.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C2').text
            freq = root.find("./What/Group[@name='observatory parameters']/Param[@name='centre_frequency']").attrib['value']

            # Todo: Parse all relevant information
            parset = {
                'Observation.TBB.TBBsetting.triggerDispersionMeasure': dm_value,
                'Observation.TBB.TBBsetting.triggerDispersionMeasureUnit': dm_unit,
                'Observation.TBB.TBBsetting.triggerType': 'FRB_VO', # todo: determine from event to allow other types?
                'Observation.TBB.TBBsetting.triggerVersion': trigger_version,
                'Observation.TBB.TBBsetting.triggerId': trigger_id,
                'Observation.TBB.TBBsetting.time': isotime,
                'Observation.TBB.TBBsetting.fitDirectionCoordinateSystem': coordsys,
                'Observation.TBB.TBBsetting.fitDirectionAngle1': ra,
                'Observation.TBB.TBBsetting.fitDirectionAngle2': dec,
                'Observation.TBB.TBBsetting.referenceFrequency': freq
            }
            logger.debug('Created parset: %s' % parset)
            return parset

        except Exception as ex:
            logger.exception("Error while parsing VOEvent: %s" % (ex,))
            raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print(get_cpu_nodes_available_for_tbb_datawriters_sorted_by_load())
