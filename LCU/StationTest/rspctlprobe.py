#!/usr/bin/env python3

import logging
import re
import subprocess

import json
import os
import argparse

import tempfile
import shutil
import time
import socket

import traceback
from functools import reduce

name = __name__ if __name__ != '__main__' else 'rspctlprobe'
logger = logging.getLogger(name)

# --------------------------------NICE PRINTOUT
def table_maxlength_per_column(column):
    """
    Computes the width in character of a column made of strings
    :param column: list of values [ row1, row2 ... ]
    :return: max value
    """
    return reduce(max, list(map(len, column)))

def compute_table_width(data, margin = 1):
    """
    Compute the column width in characters
    :param data: table made of a list of columns
    :type data: list
    :param margin: number of character to use as a margin for all the columns
    :type margin: int
    :return: a list of all the column sizes
    """
    return [x + 2 * margin for x in list(map(table_maxlength_per_column, data))]

def table_fix_string_length(string, length):
    """
    Reformat each string to have the same character width
    :param string: the string to reformact
    :type string: str
    :param length: the length of the final string
    :type length: str
    :return: a formatted string with the request character size
    """
    return '{:^{width}}'.format(string, width = length)

def table_format_column(column, length):
    """
    Given a column of values it formats them to have the requested character size
    :param column: the column of data
    :type column: list
    :param length: the length you want to have for that column
    :return:
    """
    return [table_fix_string_length(x, length) for x in column]

def table_transpose(table):
    """
    Transpose a list of rows in a list of columns and viceversa
    :param table: the table to format
    :type table: a list of list of strings
    :return:
    """
    return list(zip(*table))

def table_format(table, separator = "|", margin_size = 1):
    """
    Format a table of values
    :param table: table of values
    :param separator: character used to separate the columns
    :param margin_size: size of the margin in characters
    :return:
    """
    # compute the size needed taking into account also the margins of each column in the table
    column_desired_size = compute_table_width(table, margin_size)
    # format each column with the desired number of characters
    formatted_columns = [table_format_column(column, size) for column, size in zip(table, column_desired_size)]
    # transpose the list of columns in list of rows and concatenate the values to obtain rows using the separator
    return [separator.join(row) for row in table_transpose(formatted_columns)]

def table_print_out_table(write_function, table):
    """
    Calls the write function for each row in the new formatted table
    :param write_function: the function to be called
    :param table: the table to format
    :return: None
    """
    try:
        for row in table_format(table):
            write_function(row + "\n")
    except Exception as e:
        logger.error("Error formatting table: %s", e)

# ---------------------------------UTILITIES
def issue_rspctl_command(cmd):
    """
    Issue the command over a shell and catches the output
    :param cmd: a list of the arguments to be executed
    :type cmd: list
    :return: a tuple with the stdout and the sterr of the execution
    :rtype: tuple
    """
    cmd = ["rspctl"] + cmd

    try:
        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = proc.communicate()

        if proc.returncode == 0:
            return out, err
        else:
            raise Exception("Program failed with error: \n" +
                            "STDOUT: %s\n" % out +
                            "STDERR: %s\n" % err)
    except OSError as e:
        raise Exception("Error executing " + " ".join(cmd) + ":" + e.strerror)

def list_mode(l):
    """
    Return the most frequent element in the list
    :param l: input list
    :return: the most frequent element
    """
    return max(set(l), key = l.count)

# ----------------------------------COMMANDS
# -------Clock
def parse_clock_output(out, err):
    """
    Parse the output of the rspctl --clock

    Output pattern:
    "Sample frequency: clock=??? MHz"
    :param: out stdout
    :param: err stderr
    :return: the int value of the clock in Mhz
    :rtype: int
    """
    match = re.search("\s*Sample frequency: clock=(\d{3})MHz\s*", out)
    if match:
        return int(match.group(1))
    else:
        raise Exception("Couldn't query the clock: \n" +
                        "%s\n" % out +
                        "STDOUT: %s\n" % out +
                        "STDERR: %s\n" % err)

def query_clock():
    """
    Execute the command rspctl --clock and and parses the result
    :return: the clock in Mhz
    :rtype: int
    """
    out, err = issue_rspctl_command(['--clock'])
    return parse_clock_output(out, err)

class RCUBoard:
    """
    This class describes the properties of a RCUBoard
    """
    def __init__(self,
                 identifier = -1,
                 status = None,
                 mode = None,
                 delay = None,
                 attenuation = None,
                 sub_bands = None,
                 xcsub_bands = None):

        self.id = identifier
        self.status = status
        self.mode = mode
        self.delay = delay
        self.attenuation = attenuation
        self.sub_bands = sub_bands
        self.xcsub_bands = xcsub_bands

    def __str__(self):
        return "RCU[%d] status:%s mode:%s delay:%s attenuation:%s sub_bands:%s xcsub_bands:%s" % (
            self.id,
            self.status,
            self.mode,
            self.delay,
            self.attenuation,
            self.sub_bands,
            self.xcsub_bands)

    def __getitem__(self, item):
        return getattr(self, item)

# -------RCU mode
def parse_rcu_output(out, err):
    """
    Parse the output of rspctl --rcu
    Output pattern:
    "RCU[ 0].control=0x10003000 => OFF, mode:0, delay=00, att=00
     RCU[ 1].control=0x10003000 => OFF, mode:0, delay=00, att=00
     RCU[ 2].control=0x10003000 => OFF, mode:0, delay=00, att=00
     RCU[ 3].control=0x10003000 => OFF, mode:0, delay=00, att=00"
    :param: out stdout
    :param: err stderr
    :return: a dict indexed by the rcu board id and the properties parsed such as the status, the mode,
            the delay and the attenuation
    :rtype: dict
    """
    rcu_values = [_f for _f in out.split('\n') if _f]    # It filters empty strings
    rcu_by_id = {}    # list of RCUs listed by ID

    for rcu_value in rcu_values:
        match = re.search("RCU\[\s*(?P<RCU_id>\d+)\].control=" +    # parsing id
                          "\d+x\w+\s=>\s*(?P<status>\w+)," +    # parsing status
                          "\smode:(?P<mode>\-?\d)," +    # parsing mode
                          "\sdelay=(?P<delay>\d+)," +    # parsing delay
                          "\satt=(?P<attenuation>\d+)", rcu_value)    # parsing attenuation
        if match:
            rcu_id = int(match.group('RCU_id'))
            rcu_board = RCUBoard(identifier = rcu_id,
                                 status = match.group('status'),
                                 mode = match.group('mode'),
                                 delay = match.group('delay'),
                                 attenuation = match.group('attenuation')
                                 )

            rcu_by_id[rcu_id] = rcu_board
        else:
            raise Exception("Couldn't query the rcu: \n" +
                            "STDOUT: %s\n" % out +
                            "STDERR: %s\n" % err)
    return rcu_by_id

def query_rcu_mode():
    """
    Execute the command rspctl --rcu and parses the result
    :return: the properties per rcu board
    :rtype: dict
    """
    out, err = issue_rspctl_command(['--rcu'])
    return parse_rcu_output(out, err)

# -------Subbands
def parse_subbands_output(out, err):
    """

    Parses the output of rspctl --subbands

    Output pattern:
    "RCU[ 0].subbands=(0,1) x (0,243)
    [ 142 144 146 148 150 152 154 156 158 160 162 164 166 168 170 172 174 176 178 180 182 184 186 188 190 192 194 196 198 200 202 204 206 208 210 212 214 216 218 220 222 224 226 228 230 232 234 236 238 240 242 244 246 248 250 252 254 256 258 260 262 264 266 268 270 272 274 276 278 280 282 284 286 288 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ]

    RCU[ 1].subbands=(0,1) x (0,243)
    [ 143 145 147 149 151 153 155 157 159 161 163 165 167 169 171 173 175 177 179 181 183 185 187 189 191 193 195 197 199 201 203 205 207 209 211 213 215 217 219 221 223 225 227 229 231 233 235 237 239 241 243 245 247 249 251 253 255 257 259 261 263 265 267 269 271 273 275 277 279 281 283 285 287 289 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1

    :param: out stdout
    :param: err stderr
    :return: a dict indexed by the rcuboard id and the properties parsed such as the active state, the mode,
            the delay and the attenuation
    :rtype: dict
    """

    rcu_values = filter(None, out.split('\n'))[1:]    # FILTERS empty strings

    rcu_by_id = {}

    i_row = 0
    while i_row < len(rcu_values):
        value = rcu_values[i_row]
        match = re.search("RCU\[\s*(?P<RCU_id>\d+)\]" +    # parsing RCU id
                          ".subbands=\(\d+,(?P<n_rows>\d)\)\s+x\s+\(0," +    # parsing the number of rows
                          "(?P<n_elements>\d+)\)\s*",    # parsing the number of elements
                          value)
        if match:
            rcu_id = int(match.group('RCU_id'))
            n_rows = int(match.group('n_rows')) + 1

        else:
            raise Exception("Couldn't query the subband: \n" +
                            "%s\n" % value +
                            "STDOUT: %s\n" % out +
                            "STDERR: %s\n" % err)

        sub_band_list = []
        for i in range(n_rows):
            # Parsing the string [ 143 145 ... or ... 122 123] into a list of integers
            row = list(map(int, [_f for _f in rcu_values[i_row + i + 1].strip().lstrip('[').rstrip(']').split(' ') if _f]))
            sub_band_list.append(row)

        i_row = i_row + n_rows + 1    # ADVANCE

        rcu_by_id[rcu_id] = sub_band_list

    return rcu_by_id

def query_sub_bands_mode():
    """
     Execute the command rspctl --subbands and parses the result
    :return: the properties per rcu board
    :rtype: dict
    """
    out, err = issue_rspctl_command(['--subbands'])
    return parse_subbands_output(out, err)

# -------XCSub bands
def parse_xcsub_bands_output(out, err):
    """

    Parses the output of rspctl --xcsubbands

    Output pattern:
    "getsubbandsack.timestamp=1511262126 - Tue, 21 Nov 2017 11:02:06.000000  +0000
    RCU[ 0].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
     0 0 0 0 ]

    RCU[ 1].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
    0 0 0 0 ]

    RCU[ 2].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
     0 0 0 0 ]

    RCU[ 3].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
     0 0 0 0 ]

    RCU[ 4].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
    0 0 0 0 ]

    RCU[ 5].xcsubbands=(0,1) x (0,3)
    [ 0 0 0 0
    0 0 0 0 ]

    :param: out stdout
    :param: err stderr
    :return: a dict indexed by the rcu board id containing the list of xcsub bands used
    :rtype: dict
    """

    rcu_values = filter(None, out.split('\n'))[1:]    # it filters empty strings

    rcu_by_id = {}

    i_row = 0
    while i_row < len(rcu_values):
        value = rcu_values[i_row]
        match = re.search("RCU\[\s*(?P<RCU_id>\d+)\]." +
                          "xcsubbands=\(\d+,(?P<n_rows>\d)\)\s+x\s+\(0,(?P<n_elements>\d+)\)\s*", value)
        if match:
            rcu_id = int(match.group('RCU_id'))
            n_rows = int(match.group('n_rows')) + 1
        else:
            raise Exception("Couldn't query the subband: \n" +
                            "%s\n" % value +
                            "STDOUT: %s\n" % out +
                            "STDERR: %s\n" % err)

        xcsub_bands_list = []
        for i in range(n_rows):
            # Parsing the string [ 143 145 ... or ... 122 123] into a list of integers
            row = list(map(int, [_f for _f in rcu_values[i_row + i + 1].strip().lstrip('[').rstrip(']').split(' ') if _f]))
            xcsub_bands_list.append(row)

        i_row = i_row + n_rows + 1    # ADVANCE
        # concatenates the two rows -> computes the max xcsub_band and returns the value
        # [NOTE max accepts only a couple of values]
        val = reduce(lambda x, a: max(x, a), reduce(lambda x, a: x + a, xcsub_bands_list))
        # The xcsub band index is expressed as the double of the actual sub band:
        #  even for the X polarization
        #  odd for the Y polarization
        val = (val - 1) // 2 if rcu_id % 2 else val // 2

        rcu_by_id[rcu_id] = val
    return rcu_by_id

def query_xcsub_bands_mode():
    """
     Execute the command rspctl --subbands and parses the result
    :return: the properties per rcu board
    :rtype: dict
    """
    out, err = issue_rspctl_command(['--xcsubband'])
    return parse_xcsub_bands_output(out, err)

# -------Spectral inversion
def parse_spinv_output(out, err):
    """
    Parses the output of rspctl --spinv

    Output pattern:
    "getSIack.timestamp=1507887895 - Fri, 13 Oct 2017 09:44:55.000000  +0000

    Board[00]:  .   .   .   .   .   .   .   .
    Board[01]:  .   .   .   .   .   .   .   .
    Board[02]:  .   .   .   .   .   .   .   .
    Board[03]:  .   .   .   .   .   .   .   .
    Board[04]:  .   .   .   .   .   .   .   .
    Board[05]:  .   .   .   .   .   .   .   .
    Board[06]:  .   .   .   .   .   .   .   .
    Board[07]:  .   .   .   .   .   .   .   .
    Board[08]:  .   .   .   .   .   .   .   .
    Board[09]:  .   .   .   .   .   .   .   .
    Board[10]:  .   .   .   .   .   .   .   .
    Board[11]:  .   .   .   .   .   .   .   .
    Board[12]:  .   .   .   .   .   .   .   .
    Board[13]:  .   .   .   .   .   .   .   .
    Board[14]:  .   .   .   .   .   .   .   .
    Board[15]:  .   .   .   .   .   .   .   .
    Board[16]:  .   .   .   .   .   .   .   .
    Board[17]:  .   .   .   .   .   .   .   .
    Board[18]:  .   .   .   .   .   .   .   .
    Board[19]:  .   .   .   .   .   .   .   .
    Board[20]:  .   .   .   .   .   .   .   .
    Board[21]:  .   .   .   .   .   .   .   .
    Board[22]:  .   .   .   .   .   .   .   .
    Board[23]:  .   .   .   .   .   .   .   .


    :param: out stdout
    :param: err stderr
    :return: a dict indexed by the rcuboard id and the properties parsed such as the active state, the mode,
            the delay and the attenuation
    :rtype: dict
    """

    board_values = filter(None, out.split('\n'))[1:]    # FILTERS empty strings
    rcu_by_id = {}
    for board_value in board_values:
        temp = board_value.split(":")
        match = re.search("Board\[(\w+)\]", temp[0])

        if match:
            board_id = int(match.group(1))
        else:
            raise Exception("Couldn't query the spinv: \n" +
                            "%s\n" % board_value +
                            "STDOUT: %s\n" % out +
                            "STDERR: %s\n" % err)

        match = re.findall("(\d+|\.)", temp[1])

        spinv_values = [x if x != '.' else '' for x in match]

        # this is a delicate point since some antenna might have not changed the spec inv setting
        # is not straightforward to define whether or not the spec inv is on
        rcu_by_id[board_id] = {"spinv": spinv_values, "ispinv": '' not in spinv_values}

    return rcu_by_id

def query_spinv_mode():
    """
     Execute the command rspctl --spinv and parses the result
    :return: the spectral inversion status
    :rtype: dict
    """
    out, err = issue_rspctl_command(['--specinv'])
    return parse_spinv_output(out, err)

def execute_xcstatistics_mode(parameters):
    """
    Execute the command rspclt --xcstatistics from a dict of parameters
    :param parameters: The properties for the xcstatistics command
    :type parameters: dict
    :return:
    :rtype:
    """
    logger.info("Executing xcstatistics with these parameters %s", parameters)
    cmd_list = []

    if 'xcangle' in parameters:
        cmd_list.append('--xcangle')

    cmd_list.append('--xcstatistics')

    if 'duration' in parameters:
        cmd_list.append('--duration=%d' % parameters['duration'])
    if 'integration' in parameters:
        cmd_list.append('--integration=%d' % parameters['integration'])
    if 'directory' in parameters:
        cmd_list.append('--directory=%s' % parameters['directory'])
    if 'select'in parameters:
        cmd_list.append('--select=%s' % parameters['select'])

    issue_rspctl_command(cmd_list)

# ----------------------------------Merging information

def query_status():
    """
    Query the status of the station in particular collect its statistics executing

    rspctl --clock to collect the clock
    rspctl --subbands to see the sub band involved
    rspctl --rcu to collect status mode delay and attenuation
    rspctl --spinv to collect the status of the spectral inversion
    """
    try:
        sub_bands = query_sub_bands_mode()
    except Exception as e:
        logger.error("error querying sub band: %s", e)
        raise Exception('Error querying sub band')

    try:
        xcsub_bands = query_xcsub_bands_mode()
    except Exception as e:
        logger.error("error querying xcsub bands: %s", e)
        raise Exception('Error querying xcsub band')

    try:
        rcu = query_rcu_mode()
    except Exception as e:
        logger.error("error querying rcu status: %s", e)
        raise Exception('Error querying rcu')

    try:
        clock = query_clock()
    except Exception as e:
        logger.error("error querying clock: %s", e)
        raise Exception('Error querying clock')

    try:
        boards_spinv = query_spinv_mode()
    except Exception as e:
        logger.error("error querying spectral inversion: %s", e)
        raise Exception('Error querying spectral inversion')

    for k in list(rcu.keys()):
        rcu_i = rcu[k]
        rcu_i.sub_bands = sub_bands[k]
        rcu_i.xcsub_bands = xcsub_bands[k]

    res = {"rcus": rcu, "clock": clock, "boards-spinv": boards_spinv}

    rcus_mode = [rcu[i]["mode"] for i in rcu]
    rcus_xcsub_band = [rcu[i]["xcsub_bands"] for i in rcu]

    res["mode"] = list_mode(rcus_mode)
    res["xcsub_band"] = list_mode(rcus_xcsub_band)

    return res

def dump_info_file(path, res):
    """
    Dump the information collected in json format into the directory specified in path
    :param path: where to store the information file
    :type path: str
    :param res: result of the query
    :type res: dict
    """

    file_path = os.path.join(path, "infos")
    with open(file_path, 'w') as fout:
        fout.write(json.dumps(res, indent = 4, separators = (',', ': ')))

def query_xcstatistics(options):
    """
    Perform the query of the status information and the xcstatistics with the given options
    and afterwards dumps the information into the directory specified in the options
    with the timestamp


    :param options: options that involve the rspctl --xcstatistics
    :type options: dict
    """
    final_directory = os.path.join(options['directory'])
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)

    res = query_status()

    subband = res["xcsub_band"]
    mode = res["mode"]

    filename = "_mode_%s_xst_sb%0.3d.dat" % (mode, subband)

    temporary_output_directory = tempfile.mkdtemp(prefix = "rspctlprobe_tmp")

    options['directory'] = temporary_output_directory
    integration = options['integration']

    duration = options['duration']

    logger.info("query xcstatistics and storing them into directory %s", options['directory'])

    execute_xcstatistics_mode(options)

    # List all the file in the temporary directory
    file_list = [f for f in os.listdir(temporary_output_directory)
                 if os.path.isfile(os.path.join(temporary_output_directory, f))][0]
    timestamp = file_list.rstrip("_xst.dat")

    res["timestamp"] = timestamp
    filename = timestamp + filename

    shutil.copy(os.path.join(temporary_output_directory, file_list), os.path.join(final_directory, filename))
    shutil.rmtree(temporary_output_directory)

    rcus = res["rcus"]
    header = ["RCUID", "delay", "attenuation", "mode", "status", "xcsub_bands"]
    ids = [[header[0]] + list(map(str, list(rcus.keys())))]    # Create the id column of the file
    table = [[key] + [str(rcus[i][key]) for i in rcus] for key in header[1:]]
    table = ids + table

    fileout = os.path.join(final_directory, "summary.info")

    with open(fileout, "a") as out:
        out.write("\n")
        out.write("timestamp = {} , mode = {} , xcsubband = {}, integration = {}, duration = {}\n".format(
            res["timestamp"],
            res["mode"],
            res["xcsub_band"],
            integration,
            duration))
        table_print_out_table(out.write, table)

    return res

def query_most_common_mode():
    """
    Return the most frequent mode that the RCUs have
    :return: the mode
    """
    rcus_mode = query_rcu_mode()
    rcus_mode = [rcus_mode[rcu] for rcu in rcus_mode]
    return int(list_mode([x['mode'] for x in rcus_mode]))

def set_mode(mode):
    """
    Set the mode on all the rsp boards

    :param mode: the mode to be set
    :type mode: int
    """

    if mode == query_most_common_mode():
        return True

    logger.info('switching rcu mode to %d', mode)
    issue_rspctl_command(["--mode={}".format(mode)])
    logger.info('mode change command issued')

    for i in range(10):
        time.sleep(3)
        outmode = query_most_common_mode()
        logger.info('current rsp mode is {}'.format(outmode))
        if mode == outmode:
            logger.info('mode changed correctly to {}'.format(outmode))
            return True
    raise Exception('Cannot change rsp mode')

def set_xcsubband(subband):
    """
    Set the crosslet subband from which collecting the statistics on all the rsp boards

    :param subband: the list of subband
    :type subband: string
    """
    logger.info('switching rcu xcsubband to %d', subband)
    issue_rspctl_command(["--xcsubband={}".format(subband)])
    logger.debug('xcsubband change command issued')
    for i in range(10):
        time.sleep(1)
        xcsub_bands = list(query_xcsub_bands_mode().values())
        out_xcsubband = list_mode(xcsub_bands)
        if subband == out_xcsubband:
            logger.info('xcsubband changed correctly to %d', out_xcsubband)
            return True
    raise Exception('Cannot change rsp xcsubband to {}'.format(subband))

def produce_xcstatistics(integration_time = 1, duration = 1, add_options = None, output_directory = "./"):
    """
    Execute the command to compute the xcstatistics with a given integration and duration.
     It is also possible to specify an output directory and additional options.
    :param integration_time: integration time
    :param duration: duration time
    :param add_options:  additional options as a dict{}
    :param output_directory:
    :return:
    """
    if not add_options:
        add_options = {}

    add_options["integration"] = integration_time
    add_options["duration"] = duration
    add_options["directory"] = output_directory

    res = query_xcstatistics(add_options)
    return res

def batch_produce_xcstatistics(integration_time,
                               duration,
                               wait_time = None,
                               xcsub_bands = None,
                               mode = None,
                               add_options = None,
                               output_directory = "./"):
    """
    Produces the xcstatistics for a list of integration_times durations and wait_times on the given set of xcsubband
    storing everything in the output directory.
    :param integration_time: list of integration times
    :param duration: list of duration of the single
    :param wait_time: list of wait times
    :param xcsub_bands: list of sub band where to compute the crosslet statistics
    :param mode: mode of the array
    :param add_options: additional options to pass to rspctl
    :param output_directory: the output directory
    :return: None
    """

    if not wait_time:
        wait_time = [0]

    if not add_options:
        add_options = {}

    if mode != -2:
        set_mode(mode)

    for ind, (i, d, w) in enumerate(zip(integration_time, duration, wait_time)):
        if not xcsub_bands:
            produce_xcstatistics(i, d, add_options, output_directory)
        else:
            for xcsub_band in xcsub_bands:
                set_xcsubband(xcsub_band)
                produce_xcstatistics(i, d, add_options, output_directory)

        time.sleep(w)

# ----------------------------------MAIN CODE LOGIC
def setup_logging():
    """
    Setup the logging system
    """
    logging.basicConfig(
        format = '%(asctime)s - %(name)s: %(message)s',
        datefmt = "%m/%d/%Y %I:%M:%S %p",
        level = logging.DEBUG)

def init():
    """
    Init phase of the program
    """
    setup_logging()

def setup_command_argument_parser():
    parser = argparse.ArgumentParser(
         formatter_class=argparse.RawDescriptionHelpFormatter,
         description = "es: python3 /opt/stationtest/rspctlprobe.py --mode 3 --xcsubband 150:250:50 --xcstatistics --integration 1 --duration 5 --wait 10 --loops 2 --directory /localhome/data")

    parser.add_argument('--xcstatistics', action = 'store_true')
    parser.add_argument('--integration', type = int, default = [1], nargs = '+')
    parser.add_argument('--duration', type = int, default = [1], nargs = '+')
    parser.add_argument('--xcangle', default = 'False')
    parser.add_argument('--directory', default = os.getcwd())
    parser.add_argument('--wait', type = int, default = [0], nargs = '+')
    parser.add_argument('--xcsubband', type = str, default = "")
    parser.add_argument('--loops', type = int, default = 1)
    parser.add_argument('--mode', type = int, default = -2)
    return parser

def parse_and_execute_command_arguments():
    """
    Parses the command line arguments and execute the procedure linked
    :return:
    :rtype:
    """
    parser = setup_command_argument_parser()
    program_arguments = parser.parse_args()

    if program_arguments.xcstatistics:
        options = {}
        if program_arguments.xcangle:
            options['xcangle'] = True

        try:
            if program_arguments.xcsubband:
                if ":" in program_arguments.xcsubband:
                    start, end, step = map(int, program_arguments.xcsubband.split(":"))
                    xcsub_bands = [int(i) for i in range(start, end+step, step)]
                elif "," in program_arguments.xcsubband:
                    xcsub_bands = [int(i) for i in program_arguments.xcsubband.split(",")]
                else:
                    xcsub_bands = [int(program_arguments.xcsubband)]

                for i in range(program_arguments.loops):
                    batch_produce_xcstatistics(program_arguments.integration,
                                               program_arguments.duration,
                                               wait_time = program_arguments.wait,
                                               xcsub_bands = xcsub_bands,
                                               mode = program_arguments.mode,
                                               add_options = options,
                                               output_directory = program_arguments.directory)

            else:
                for i in range(program_arguments.loops):
                    batch_produce_xcstatistics(program_arguments.integration,
                                               program_arguments.duration,
                                               wait_time = program_arguments.wait,
                                               mode = program_arguments.mode,
                                               add_options = options,
                                               output_directory = program_arguments.directory)
            set_mode(0) # SWITCH BACK TO MODE 0 AT THE END
        except Exception as e:
            logger.error('error executing rspctl : %s', e)
            logger.error('traceback \n%s', traceback.format_exc())
            raise e
    else:
        parser.error('please specify a task')

def main():
    init()
    logging.basicConfig(format = '%(asctime)s ' + socket.gethostname() + ' %(levelname)s %(message)s',
                        level = logging.INFO)
    parse_and_execute_command_arguments()

if __name__ == '__main__':
    main()
