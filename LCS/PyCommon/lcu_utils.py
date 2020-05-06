# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

from lofar.common.ssh_utils import ssh_cmd_list
from lofar.common.subprocess_utils import execute_in_parallel, wrap_composite_command, communicate_returning_strings
from subprocess import Popen, PIPE

import os
import uuid
import struct
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

class LCURuntimeError(RuntimeError):
    pass

def wrap_command_in_lcu_head_node_ssh_call(cmd):
    '''wrap the command in an ssh call to head.cep4
    :param list cmd: a subprocess cmd list
    cpu node. Otherwise, the command is executed on the head node.
    :return: the same subprocess cmd list, but then wrapped with cep4 ssh calls
    '''
    ssh_cmd = ssh_cmd_list('lcuhead.control.lofar', 'lofarsys')
    return ssh_cmd + ([cmd] if isinstance(cmd, str) else cmd)

def wrap_command_in_lcu_station_ssh_call(cmd, station, via_head=True):
    '''wrap the command in an ssh call the given station lcu node (via lcuhead)
    :param list cmd: a subprocess cmd list
    :param string station: the station name or lcu hostname (a station name is automagically converted to the lcu hostname)
    :param bool via_head: when True, route the cmd first via the lcuhead node
    :return: the same subprocess cmd list, but then wrapped with lcu ssh calls
    '''
    ssh_cmd = ssh_cmd_list(stationname2hostname(station), 'lofarsys')
    remote_cmd = ssh_cmd + ([cmd] if isinstance(cmd, str) else cmd)
    if via_head:
        return wrap_command_in_lcu_head_node_ssh_call(remote_cmd)

    return remote_cmd

def execute_in_parallel_over_stations(cmd, stations, timeout=3600, max_parallel=10):
    """
    Execute the given cmd in parallel on the given list of stations.
    This is a python equivalent of the lcurun script on lcuhead.
    :param cmd: string of list of strings with the commandline to be executed remotely (so without any ssh calls in it)
    :param list stations: list of station names or lcu hostnames on which to execute the command
    :param int timeout: time out after this many seconds
    :param int max_parallel: maximum number of concurrent executed commands (ssh limits the number of concurrent connections, so the default of 10 is quite safe/ok)
    :raises a SubprocessTimoutError if any of the commands time out
    :return: dict with a mapping of station -> cmd_result which contains the returncode, stdout and stderr
    """
    cmd_list = [wrap_command_in_lcu_station_ssh_call(cmd, station, via_head=True)
                for station in ([stations] if isinstance(stations, str) else stations)]

    # and execute them for all stations in parallel
    # the dict comprehension + zip method link the results of the execute_in_parallel to the associated stations
    # so the returned dict is a mapping of station->cmd_result
    return { station: result
             for station, result in zip(stations,
                                        execute_in_parallel(cmd_list, timeout=timeout, max_parallel=max_parallel))}

def execute_in_parallel_over_station_group(cmd, station_group='today', timeout=3600, max_parallel=10):
    """
    Execute the given cmd in parallel on the stations in the given station group.
    This is a python equivalent of the lcurun script on lcuhead.
    :param cmd: string of list of strings with the commandline to be executed remotely (so without any ssh calls in it)
    :param station_group - string: one of the predefined operator station groups, like: 'today', 'today_nl', 'core', etc. Defaults to 'today' which means all active stations.
    :param int max_parallel: maximum number of concurrent executed commands (ssh limits the number of concurrent connections, so the default of 10 is quite safe/ok)
    :param int timeout: time out after this many seconds
    :raises a SubprocessTimoutError if any of the commands time out
    :return: dict with a mapping of station -> cmd_result which contains the returncode, stdout and stderr
    """
    stations = get_current_stations(station_group=station_group, as_host_names=True)
    return execute_in_parallel_over_stations(cmd=cmd, stations=stations, timeout=timeout, max_parallel=max_parallel)

def translate_user_station_string_into_station_list(user_station_string: str):
    '''
    try to deal with user input like 'cs001,cs001' or 'today' or ... etc
    No guarantees! just best effort!
    :param user_station_string: a string like 'cs001,cs001' or 'today' or ... etc
    :return: a list of station names
    '''
    logger.debug("translating '%s'", user_station_string)

    if isinstance(user_station_string, bytes):
        user_station_string = user_station_string.decode('utf-8')

    if not isinstance(user_station_string, str):
        raise ValueError("cannot parse user_station_string: %s", (user_station_string,))

    if ',' in user_station_string:
        result = user_station_string.split(',')
        logger.info("translate_user_station_string_into_station_list(%s) -> %s", user_station_string, result)
        return result

    # maybe 'stations' is a group. Do lookup.
    current_stations = get_current_stations(user_station_string, as_host_names=False)
    if current_stations:
        logger.info("translate_user_station_string_into_station_list(%s) -> %s", user_station_string, current_stations)
        return current_stations

    # just treat the stations string as list of stations and hope for the best
    logger.info("translate_user_station_string_into_station_list(%s) -> %s", user_station_string, [user_station_string])
    return [user_station_string]

def get_current_stations(station_group='today', as_host_names=True):
    '''
    Wrapper function around the amazing lcurun and stations.txt operators system.
    Get a list of the currently used station names, either as hostname, or as parset-like station name (default)
    :param station_group - string: one of the predefined operator station groups, like: 'today', 'today_nl', 'core', etc. Defaults to 'today' which means all active stations.
    :param as_host_names - bool: return the station names as ssh-able hostnames if True (like cs001c, cs002c). return the station names as parset-like VirtualInstrument.stationList names if False (like CS001, CS002).
    :return: the station names for the given station_group as ssh-able hostnames if as_host_names=True (like cs001c, cs002c) or as parset-like VirtualInstrument.stationList names if as_host_names=False (like CS001, CS002).
    '''
    cmd = ['cat', '/opt/operations/bin/stations.txt']
    cmd = wrap_command_in_lcu_head_node_ssh_call(cmd)
    logger.debug('executing cmd: %s', ' '.join(cmd))
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = communicate_returning_strings(proc)

    if proc.returncode != 0:
        raise LCURuntimeError("Could not fetch stations.txt file. sdterr=%s" % (err, ))

    station_file_lines = out.splitlines(False)
    station_group_filter = station_group.strip()+' '
    station_group_line = next(l for l in station_file_lines if l.startswith(station_group_filter))
    station_aliases = station_group_line.split(' ')[-1].split(',')
    station_hostnames = []
    for station_alias in station_aliases:
        # the alias mapping is at the top of the file, so the first matching line holds the mapping
        station_alias_line = next(l for l in station_file_lines if station_alias in l)
        station_hostname = station_alias_line.split()[0].strip()
        station_hostnames.append(station_hostname)

    if as_host_names:
        logger.info("station hostnames in group '%s': %s", station_group, ' '.join(station_hostnames))
        return station_hostnames

    station_names = [hostname2stationname(x) for x in station_hostnames]
    logger.info("stations in group '%s': %s", station_group, ' '.join(station_names))
    return station_names

def stationname2hostname(station_name):
    '''Convert a parset-like station name to a lcu hostname, like CS001 to cs001c'''
    # assume a hostname is encoded as stationname in lowercase with a c appended, like cs001c for CS001
    if not station_name.islower() or not (station_name.endswith('c') or station_name.endswith('control.lofar')):
        return station_name.lower().strip() + 'c'

    #assume given station_name is already in the form of an lcu hostname
    return station_name

def hostname2stationname(station_hostname):
    '''Convert a lcu hostname to a parset-like station name , like cs001c or cs001c.control.lofar to CS001'''
    # assume a hostname is encoded as stationname in lowercase with a c appended, like cs001c for CS001
    stationname = station_hostname.split('.')[0].strip().upper()
    return stationname[:-1] if stationname.endswith('C') else stationname

def get_stations_rcu_mode(stations=None):
    '''
    Get the current rcu mode of a station.
    :param stations - string or list of strings: 1 or more station names, or lcu hostnames
    :return: dict with station rcu mode integer pairs
    '''

    if stations == None:
        stations = get_current_stations(as_host_names=True)
    elif isinstance(stations, str):
        stations = [stations]

    procs = {}
    for station in stations:
        cmd = ["rspctl", "--rcu | grep ON | awk '{ print $4 }' | grep mode | cut -c 6-6 | sort -u | head -n 1"]
        cmd = wrap_command_in_lcu_station_ssh_call(cmd, station, via_head=True)
        logger.debug('executing cmd: %s', ' '.join(cmd))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        procs[station] = proc

    result = {}
    for station, proc in list(procs.items()):
        out, err = communicate_returning_strings(proc)

        if proc.returncode != 0:
            logger.warning("Could not determine rcu mode for station %s. sdterr=%s" % (station, err))

        try:
            rcu_mode = int(out.strip())
            logger.debug('station %s is in rcumode=%s', station, rcu_mode)
            result[station] = rcu_mode
        except ValueError:
            logger.warning("Could not determine rcu mode for station %s. sdterr=%s" % (station, err))

    return result

def get_station_cable_delays(stations=None):
    '''
    Get a dict of stationname:cable_delay pairs for the given list of stations (or all current stations if None given)
    :param stations - string or list of strings: station name(s) or lcu hostname(s)
    :return: dict like {<station_name>: { 'LBL': {'lengths': [...], 'delays': [...] },
                                          'LBH': {'lengths': [...], 'delays': [...] },
                                          'HBA': {'lengths': [...], 'delays': [...] } } }
             lengths are in meters, delays are in seconds.
             list items are in order of RCU_id (or dipole_nr).
    '''
    if stations == None:
        stations = get_current_stations()
    elif isinstance(stations, str):
        stations = [stations]

    stations = [hostname2stationname(s) for s in stations]

    cable_delay_files = {}
    cable_delay_procs = {}

    try:
        for station in stations:
            # fetch the cable_delays without intermediate saves to disk using multiple ssh's and pipes.
            # write the result in a local temp file for further processing.
            # local temp files are removed at end.
            tmpfilename = '/tmp/cable_delay_%s_%s' % (station, uuid.uuid4())
            cable_delay_files[station] = tmpfilename
            logger.debug('copying cable_delay file for station %s in file %s', station, tmpfilename)
            cmd = ['cat', '''/opt/lofar/etc/StaticMetaData/%s-CableDelays.conf''' % (station, )]
            cmd = wrap_command_in_lcu_station_ssh_call(cmd, station, via_head=True)
            logger.debug('executing cmd: %s', ' '.join(cmd))
            tmpfile = open(tmpfilename, 'wb')
            proc = Popen(cmd, stdout=tmpfile, stderr=PIPE, close_fds=True)
            cable_delay_procs[station] = proc

        # wait for all fetching procs to finish...
        #TODO: add timeout?
        for station, proc in list(cable_delay_procs.items()):
            out, err = communicate_returning_strings(proc)
            if proc.returncode != 0:
                logger.warning("Could not fetch cable_delay file for station %s. stderr=%s", station, err)

        # gather results...
        cable_delays = {}
        # for each station, parse temp file
        for station, filename in list(cable_delay_files.items()):
            try:
                proc = cable_delay_procs[station]
                if proc.returncode == 0:
                    # store header and complex table in result dict
                    cable_delays[station] = parse_station_cable_delay_file(filename)
            except Exception as e:
                # log exception anbd just continue with next station cable_delay file
                logger.error("error while parsing cable_delay file for station %s: %s", station, e)

    finally:
        # cleanup all temp files
        for filename in list(cable_delay_files.values()):
            try:
                logger.debug('deleting local intermediate cable_delay file %s', tmpfilename)
                os.remove(filename)
            except OSError:
                pass

    if cable_delays:
        logger.info('fetched cable_delay(s) for station(s): %s', ' '.join(sorted(cable_delays.keys())))

    return cable_delays

def parse_station_cable_delay_file(filename):
    """Parse a station cable delay file and return delays in a dict.
    :param filename: string, filename/path to parse
    :return: dict like: { 'LBL': {'lengths': [...], 'delays': [...] },
                          'LBH': {'lengths': [...], 'delays': [...] },
                          'HBA': {'lengths': [...], 'delays': [...] } }
             lengths are in meters, delays are in seconds.
             list items are in order of RCU_id (or dipole_nr).
    """
    result = {'LBL': {'lengths': [], 'delays': []},
              'LBH': {'lengths': [], 'delays': []},
              'HBA': {'lengths': [], 'delays': []}}
    with open(filename, 'r') as tmpfile:
        lines = tmpfile.readlines()

        # read (and ignore) all header lines which start with a #
        for data_start_idx, line in enumerate(lines):
            if not line.lstrip().startswith('#'):
                break

        # parse the rest of the lines which contain the data
        # raise upon any unexpected error
        for idx, line in enumerate(lines[data_start_idx:]):
            items = line.strip().split()
            rcu_id = int(items[0])
            if rcu_id != idx:
                raise LCURuntimeError('Error while parsing %s: unexpected rcu_id=%s' % (filename, rcu_id))
            if len(items) < 7:
                raise LCURuntimeError('Error while parsing %s: cannot parse items=%s in line=%s' % (filename, items, line))
            result['LBL']['lengths'].append(float(items[1]))
            result['LBL']['delays'].append(float(items[2])*1e-9) #convert nsec -> sec
            result['LBH']['lengths'].append(float(items[3]))
            result['LBH']['delays'].append(float(items[4])*1e-9) #convert nsec -> sec
            result['HBA']['lengths'].append(float(items[5]))
            result['HBA']['delays'].append(float(items[6])*1e-9) #convert nsec -> sec
    return result

def get_station_calibration_tables(stations=None, antenna_set_and_filter=None, timeout=60):
    '''
    Get a dict of stationname:caltable pairs for the given list of stations (or all current stations if None given)
    :param stations - string or list of strings: station name(s) or lcu hostname(s)
    :param antenna_set_and_filter - string: the antenna_set name and filter'name' from the parset like: LBA_INNER-10_90, or HBA-170_230 etc. If None, then the current rcu_mode is retreived and the caltables for the current rcu mode are returned
    :return: dict like {<station_name>: tuple(calibration_header_dict, numpy complex array)}
    '''
    if stations == None:
        stations = get_current_stations()
    elif isinstance(stations, str):
        stations = [stations]

    stations = [hostname2stationname(s) for s in stations]

    caltable_files = {}
    caltable_procs = {}
    caltable_postfixes = {}

    # caltable files have either a LBA_INNER-10_90, or HBA-170_230 etc postfix, or a mode<nr> postfix
    # these are essentially the same, and on the lcu's the files are equal (in fact they are symlinked.)
    # So, depending on the knowledge of the requester, one eiter asks for an 'antenna_set_and_filter' postfix, or an 'rcu_mode' postfix,
    # but the result is the same.
    if antenna_set_and_filter:
        for station in stations:
            caltable_postfixes[station] = '-%s' % (antenna_set_and_filter,)
        logger.info('fetching calibration table(s) for %s for stations %s', antenna_set_and_filter, ' '.join(stations))
    else:
        rcu_modes = get_stations_rcu_mode(stations)
        for station, rcu_mode in list(rcu_modes.items()): # only loop over stations which have valid rcu_mode
            caltable_postfixes[station] = '_mode%s' % (rcu_mode,)

        logger.info('fetching calibration table(s) for rcu mode(s) %s for stations %s', ' '.join([str(m) for m in sorted(list(set(rcu_modes.values())))]), ' '.join(sorted(rcu_modes.keys())))
    try:
        for station, postfix in list(caltable_postfixes.items()):
            # fetch the caltable without intermediate saves to disk using multiple ssh's and pipes.
            # write the result in a local temp file for further processing.
            # local temp files are removed at end.
            tmpfilename = '/tmp/caltable_%s_%s_%s' % (postfix, station, uuid.uuid4())
            caltable_files[station] = tmpfilename
            logger.debug('writing caltable for station %s in file %s', station, tmpfilename)
            cmd = ['cat', '''/opt/lofar/etc/CalTable%s.dat''' % (postfix, )]
            cmd = wrap_command_in_lcu_station_ssh_call(cmd, station, via_head=True)
            logger.debug('executing cmd: %s', ' '.join(cmd))
            tmpfile = open(tmpfilename, 'wb')
            proc = Popen(cmd, stdout=tmpfile, stderr=PIPE, close_fds=True)
            caltable_procs[station] = proc

        # wait for all fetching procs to finish...
        #TODO: add timeout?
        for station, proc in list(caltable_procs.items()):
            out, err = communicate_returning_strings(proc)
            if proc.returncode != 0:
                logger.warning("Could not fetch calibration table for station %s. stderr=%s", station, err)

        # gather results...
        caltables = {}
        # for each station, parse temp file
        for station, filename in list(caltable_files.items()):
            try:
                proc = caltable_procs[station]
                if proc.returncode == 0:
                    # store header and complex table in result dict
                    caltables[station] = parse_station_calibration_file(filename)
            except Exception as e:
                # log exception anbd just continue with next station caltable file
                logger.error("error while parsing calibration file for station %s: %s", station, e)

    finally:
        # cleanup all temp files
        for filename in list(caltable_files.values()):
            try:
                logger.debug('deleting local intermediate caltable file %s', tmpfilename)
                os.remove(filename)
            except OSError:
                pass

    if caltables:
        logger.info('fetched calibration table(s) for stations %s', ' '.join(sorted(caltables.keys())))

    return caltables

def parse_station_calibration_file(filename):
    '''
    read and parse a station calibration file and return a tuple of the header and a numpy complex array of cal-values
    '''
    try:
        # import numpy here and not at top of file, so anybody can use lcu_utils methods, but is not forced into having numpy.
        import numpy as np
    except ImportError:
        raise LCURuntimeError("Cannot interpret station calibration tables without numpy. Please install numpy.")

    with open(filename, 'rb') as tmpfile:
        rawdata = tmpfile.read()

        # read header and convert it to a key-value dict
        HEADER_END = 'HeaderStop\n' #assume unix line endings
        header_end_idx = rawdata.find(HEADER_END)
        if header_end_idx == -1:
            raise LCURuntimeError("Cannot find header in %s" % (filename,))

        header_end_idx += len(HEADER_END)

        header_dict = {}
        for line in rawdata[:header_end_idx].splitlines():
            if '=' in line:
                items = line.partition('=')
                header_dict[items[0].strip()] = items[2].strip()

        # magic numbers (stolen from MAC/APL/PAC/ITRFBeamServer/src/StatCal.cc )
        NUMBER_OF_SUBBANDS = 512
        COMPLEX_SIZE = 2 # a complex is two doubles

        header_station = header_dict.get('CalTableHeader.Observation.Station')
        if header_station.startswith('CS') or header_station.startswith('RS'):
            NUMBER_OF_ANTENNA = 96
        else:
            NUMBER_OF_ANTENNA = 192 #international

        # using the magic numbers and knowledge from MAC/APL/PAC/ITRFBeamServer/src/StatCal.cc
        # interpret the byte array as list of doubles,
        # convert to numpy array,
        # convert to complex, and transpose for correct axes (antenna first, then frequency)
        fmt = '%dd' % (NUMBER_OF_ANTENNA * NUMBER_OF_SUBBANDS * COMPLEX_SIZE)
        data = np.array(struct.unpack(fmt, rawdata[header_end_idx:header_end_idx+struct.calcsize(fmt)]))
        data.resize(NUMBER_OF_SUBBANDS, NUMBER_OF_ANTENNA, COMPLEX_SIZE)

        complexdata = np.empty(shape=(NUMBER_OF_SUBBANDS, NUMBER_OF_ANTENNA), dtype=complex)
        complexdata.real = data[:, :, 0]
        complexdata.imag = data[:, :, 1]
        complexdata = complexdata.transpose()

        # return tuple of header and complex table in result dict
        return (header_dict, complexdata)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    import pprint
    # pprint.pprint(get_station_cable_delays(['CS004', 'CS005']))
    # print get_station_calibration_tables(['CS001', 'RS407'], antenna_set_and_filter='LBA_INNER-10_90') #['CS001', 'DE601'])
    #pprint.pprint(execute_in_parallel_over_stations(cmd=wrap_composite_command('sleep 1; date'),
    #                                                stations=['cs026c' for i in range(10)]))
    pprint.pprint(execute_in_parallel_over_station_group(cmd=wrap_composite_command('sleep 1 ; date ; sleep 1 ;'), station_group='today_core'))
