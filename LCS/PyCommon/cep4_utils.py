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
from subprocess import Popen, PIPE
from lofar.common.subprocess_utils import check_output_returning_strings, communicate_returning_strings, execute_in_parallel
from random import randint
import math
import os
from time import sleep
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

# a selection of slurm states relevant for lofar usage
SLURM_AVAILABLE_STATES = {'idle','mix'}
SLURM_IN_USES_STATES = {'alloc','mix'}
SLURM_UNAVAILABLE_STATES = {'down','drain','drng','resv','maint'}
SLURM_STATES = SLURM_AVAILABLE_STATES | SLURM_IN_USES_STATES | SLURM_UNAVAILABLE_STATES

# lofar cep4 default slurm partitions
SLURM_CPU_PARTITION = 'cpu'
SLURM_GPU_PARTITION = 'gpu'
SLURM_PARTITIONS = {SLURM_CPU_PARTITION, SLURM_GPU_PARTITION}

def wrap_command_in_cep4_head_node_ssh_call(cmd):
    '''wrap the command in an ssh call to head.cep4
    :param list cmd: a subprocess cmd list
    :return: the same subprocess cmd list, but then wrapped with cep4 ssh calls
    '''
    ssh_cmd = ssh_cmd_list(user='lofarsys', host='head.cep4.control.lofar')
    return ssh_cmd + ([cmd] if isinstance(cmd, str) else cmd)

def wrap_command_in_cep4_random_node_ssh_call(cmd, partition: str=SLURM_CPU_PARTITION, via_head=True):
    '''wrap the command in an ssh call an available random cep4 node (via head.cep4)
    :param list cmd: a subprocess cmd list
    :param bool via_head: when True, route the cmd first via the cep4 head node
    :return: the same subprocess cmd list, but then wrapped with cep4 ssh calls
    '''
    # pick a random  available node
    node_nrs = get_cep4_available_nodes(partition=partition)
    node_nr = node_nrs[randint(0, len(node_nrs)-1)]
    return wrap_command_in_cep4_node_ssh_call(cmd, node_nr, partition=partition, via_head=via_head)

def wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(cmd, partition: str=SLURM_CPU_PARTITION, via_head=True):
    '''wrap the command in an ssh call to the available random cep4 node with the lowest load (via head.cep4)
    :param list cmd: a subprocess cmd list
    :param bool via_head: when True, route the cmd first via the cep4 head node
    :return: the same subprocess cmd list, but then wrapped with cep4 ssh calls
    '''
    lowest_load_node_nr = get_cep4_node_with_lowest_load(partition=partition)
    if lowest_load_node_nr is None:
        raise RuntimeError("No node available in partition %s to run the cmd on. cmd=%s" % (partition, cmd))
    return wrap_command_in_cep4_node_ssh_call(cmd, lowest_load_node_nr, partition=partition, via_head=via_head)

def wrap_command_in_cep4_node_ssh_call(cmd, node_nr, partition=SLURM_CPU_PARTITION, via_head=True):
    '''wrap the command in an ssh call the given cep4 node (via head.cep4)
    :param list cmd: a subprocess cmd list
    :param int node_nr: the number of the node in the partition where to execute the command
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :param bool via_head: when True, route the cmd first via the cep4 head node
    :return: the same subprocess cmd list, but then wrapped with cep4 ssh calls
    '''
    ssh_cmd = ssh_cmd_list(host='%s%02d.cep4' % (partition, node_nr), user='lofarsys')
    remote_cmd = ssh_cmd + ([cmd] if isinstance(cmd, str) else cmd)
    if via_head:
        return wrap_command_in_cep4_head_node_ssh_call(remote_cmd)
    else:
        return remote_cmd

def wrap_command_for_docker(cmd, image_name, image_label='', mount_dirs=['/data'], added_privileges=False):
    '''wrap the command to be run in a docker container for the lofarsys user and environment
    :param list cmd: a subprocess cmd list
    :param string image_name: the name of the docker image to run
    :param string image_label: the optional label of the docker image to run
    :return: the same subprocess cmd list, but then wrapped with docker calls
    '''
    #fetch the lofarsys user id and group id first from the cep4 head node
    id_string = '%s:%s' % (check_output_returning_strings(wrap_command_in_cep4_head_node_ssh_call(['id', '-u'])).strip(),
                           check_output_returning_strings(wrap_command_in_cep4_head_node_ssh_call(['id', '-g'])).strip())

    #return the docker run command for the lofarsys user and environment
    dockerized_cmd = ['docker', 'run', '--rm', '--net=host']
    if added_privileges:
        dockerized_cmd += ['--cap-add=sys_nice', '--cap-add=sys_admin'] #, '--cap-add=ipc_lock', '--privileged']
    for d in mount_dirs:
        dockerized_cmd += ['-v', '%s:%s' % (d,d)]

    dockerized_cmd += ['-u', id_string,
                       '-v', '/etc/passwd:/etc/passwd:ro',
                       '-v', '/etc/group:/etc/group:ro',
                       '-v', '$HOME:$HOME',
                       '-e', 'HOME=$HOME',
                       '-e', 'USER=$USER',
                       '-w', '$HOME',
                       '%s:%s' % (image_name, image_label) if image_label else image_name]
    dockerized_cmd += cmd
    return dockerized_cmd

def get_cep4_slurm_nodes(states, partition: str) -> []:
    '''
    get a list of cep4 nodes from the given partition which have (one of) the given states according to slurm
    states: set/list of slurm states, see predefined sets: SLURM_AVAILABLE_STATES, SLURM_IN_USES_STATES, SLURM_UNAVAILABLE_STATES
    partition: one of the known SLURM_PARTITIONS
    :return: a list of node numbers (ints) of the nodes in the partition
    '''
    slurm_nodes = []

    try:
        # filter out unknown states
        if any(s for s in states if s not in SLURM_STATES):
            raise ValueError("the given states:%s are not valid slurm states:%s" % (states, SLURM_STATES))

        logger.debug('determining available cep4 nodes states:%s, partition:%s', states, partition)

        # find out which nodes are available
        cmd = ['sinfo -p %s -t %s' % (partition, ','.join(states))]
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)

        logger.debug('executing command: %s', ' '.join(cmd))
        out = check_output_returning_strings(cmd)
        lines = out.split('\n')
        for state in states:
            try:
                line = next(l for l in lines if state in l).strip()
                # get nodes string part of line:
                nodes_part = line.split(' ')[-1]
                slurm_nodes += convert_slurm_nodes_string_to_node_number_list(nodes_part)

            except StopIteration:
                pass  # no line with state in line

    except Exception as e:
        logger.exception(e)

    slurm_nodes = sorted(list(set(slurm_nodes)))
    logger.debug('cep4 nodes with states:%s in partition:%s are: %s', states, partition, slurm_nodes)
    return slurm_nodes

def get_cep4_available_nodes(partition: str=SLURM_CPU_PARTITION):
    '''
    get a list of cep4 nodes which are currently up and running  (either totally free, or partially free) according to slurm
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :return: a list of node numbers (ints)
    '''
    available_cep4_nodes = get_cep4_slurm_nodes(SLURM_AVAILABLE_STATES, partition=partition)

    if not available_cep4_nodes:
        logger.warning('no cep4 nodes available in partition %s', partition)

    return available_cep4_nodes

def get_cep4_up_and_running_nodes(partition: str=SLURM_CPU_PARTITION):
    '''
    get a list of cep4 nodes which are currently up and running (either totally free, partially free, or totally used) according to slurm
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :return: a list of node numbers (ints)
    '''
    cep4_nodes = get_cep4_slurm_nodes(SLURM_AVAILABLE_STATES | SLURM_IN_USES_STATES, partition=partition)

    if not cep4_nodes:
        logger.warning('no cep4 nodes up and running in partition %s', partition)

    return cep4_nodes

def convert_slurm_nodes_string_to_node_number_list(slurm_string):
    ''' converts strings like: cpu[01-03,11-12]' to [1,2,3,11,12]
    or 'cpu01' to [1]
    :param slurm_string: a string in 'slurm-like' node format, like cpu[01-03,11-12] or cpu01
    :return: a list of node numbers (ints)
    '''
    if isinstance(slurm_string, bytes):
        slurm_string = slurm_string.decode('utf-8')

    result = []
    stripped_slurm_string = slurm_string.strip()
    left_bracket_idx = stripped_slurm_string.find('[')
    right_bracket_idx = stripped_slurm_string.find(']', left_bracket_idx)
    if left_bracket_idx != -1 and right_bracket_idx != -1:
        # example: cpu[01-17,23-47]'
        # then: nodes='01-17,23-47'
        nodes_string = stripped_slurm_string[left_bracket_idx+1:right_bracket_idx]

        for part in nodes_string.split(','):
            if '-' in part:
                lower, sep, upper = part.partition('-')
                result += list(range(int(lower), int(upper) + 1))
            else:
                result.append(int(part))
    else:
        # example: 'cpu01'
        # then: nodes='01'
        # assume all nodes always start with 'cpu' (which is the case on cep4)
        node = int(stripped_slurm_string[3:])
        result.append(node)
    return result

def execute_in_parallel_on_cep4_nodes(cmd, node_nrs=None, partition: str=SLURM_CPU_PARTITION,
                                      timeout=3600, max_parallel=32, via_head=True):
    '''
    execute the given cmd in parallel over the given node numbers on the given partition, returning a dict with node_nr:popen_result pairs
    :param list cmd: a subprocess cmd list
    :param node_nrs: optional list of node numbers to get the load for. If None, then all up-and-running nodes are queried.
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :param int timeout: time out after this many seconds
    :param int max_parallel: maximum number of concurrent executed commands.
    :param bool via_head: when True, route the cmd first via the cep4 head node
    :raises a SubprocessTimoutError if any of the commands time out
    :return: a dict with node_nr:popen_result pairs
    '''
    if node_nrs == None:
        node_nrs = get_cep4_up_and_running_nodes(partition=partition)

    node_cmds = [wrap_command_in_cep4_node_ssh_call(cmd, node_nr, partition=partition, via_head=via_head)
                 for node_nr in node_nrs]

    cmd_results = execute_in_parallel(node_cmds, timeout=timeout, max_parallel=max_parallel, gather_stdout_stderr=True)

    results = {}
    for node_nr, result in zip(node_nrs, cmd_results):
        results[node_nr] = result
    return results

def get_cep4_nodes_loads(node_nrs=None, partition: str=SLURM_CPU_PARTITION, normalized=False):
    '''
    get the 5min load for each given cep4 node nr
    :param node_nrs: optional list of node numbers to get the load for. If None, then all up-and-running nodes are queried.
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :param bool normalized: when True, then normalize the loads with the number of cores.
    :return: dict with node_nr -> load mapping
    '''
    if node_nrs == None:
        node_nrs = get_cep4_up_and_running_nodes(partition=partition)

    procs = {}
    loads = {}
    logger.debug('getting 5min load for cep4 %s nodes %s', partition, ', '.join((str(x) for x in node_nrs)))

    # spawn load commands in parallel
    load_cmd = ['cat', '/proc/loadavg']

    for node_nr, result in execute_in_parallel_on_cep4_nodes(load_cmd, node_nrs=node_nrs, partition=partition).items():
        try:
            load = float(result.stdout.split()[1])
        except:
            load = 1e10
        loads[node_nr] = load

    if normalized:
        num_proc_cmd = ['grep', '-c', '^processor', '/proc/cpuinfo']

        for node_nr, result in execute_in_parallel_on_cep4_nodes(num_proc_cmd, node_nrs=node_nrs, partition=partition).items():
            try:
                num_proc = int(result.stdout)
            except Exception as e:
                logger.warning("could not get number of cpus for node %s%s: %s. Using estimated default of 24.",
                               partition, node_nr, e)
                num_proc = 24
            loads[node_nr] = loads[node_nr]/float(num_proc)

    logger.info('5min %sloads for cep4 %s nodes: %s', 'normalized ' if normalized else '',
                partition,
                ', '.join('%s%02d:%.3f' % (partition, nr, loads[nr]) for nr in sorted(loads.keys())))
    return loads

def get_cep4_available_nodes_sorted_ascending_by_load(max_normalized_load=0.33, min_nr_of_nodes=0, node_nrs=None, partition: str=SLURM_CPU_PARTITION):
    '''
    get the cep4 available node numbers sorted ascending by load (5min).
    :param float max_normalized_load: filter available nodes which are at most max_normalized_load
    :param int min_nr_of_nodes: do return this minimum number of nodes, even if their load is higher than max_normalized_load
                                If not enough nodes are up, then of course it cannot be guaranteed that we return this amount.
    :param list node_nrs: optional list of node numbers to apply the filtering on. If None, then all up-and-running nodes are queried.
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :return: sorted list of node numbers.
    '''
    if not node_nrs:
        node_nrs = get_cep4_up_and_running_nodes(partition=partition)
    loads = get_cep4_nodes_loads(node_nrs, partition=partition, normalized=True)
    load_tuples_list = [(cpu_nr,load) for cpu_nr,load in list(loads.items())]
    sorted_load_tuples_list = sorted(load_tuples_list, key=lambda x: x[1])

    # return at least min_nr_of_nodes...
    sorted_node_nrs = [tup[0] for tup in sorted_load_tuples_list[:min_nr_of_nodes]]

    # ...and add all remaining nodes with low load
    sorted_node_nrs += [tup[0] for tup in sorted_load_tuples_list[min_nr_of_nodes:] if tup[1] <= max_normalized_load]

    logger.info('available cep4 %s nodes sorted (asc) by load (max_normalized_load=%s, min_nr_of_nodes=%s): %s',
                 partition, max_normalized_load, min_nr_of_nodes, sorted_node_nrs)
    return sorted_node_nrs

def get_cep4_node_with_lowest_load(max_normalized_load=0.33, partition: str=SLURM_CPU_PARTITION):
    '''
    get the cep4 node which has the lowest (5min) load of them all. Preferably a node which is not fully used yet.
    :param float max_normalized_load: filter nodes which a at most max_normalized_load
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :return: the node number (int) with the lowest load.
    '''
    # first see if there are any not-fully-used nodes available
    nodes = get_cep4_available_nodes(partition=partition)

    if not nodes: # if not, then just query all up and running nodes
        nodes = get_cep4_up_and_running_nodes(partition=partition)

    node_nrs = get_cep4_available_nodes_sorted_ascending_by_load(max_normalized_load=max_normalized_load,
                                                                 min_nr_of_nodes=1,
                                                                 node_nrs=nodes,
                                                                 partition=partition)
    if node_nrs:
        logger.debug('cep4 %snode with lowest load: %s', partition, node_nrs[0])
        return node_nrs[0]
    return None

def parallelize_cmd_over_cep4_cpu_nodes(cmd, parallelizable_option, parallelizable_option_values,
                                        max_normalized_load=0.5, min_nr_of_nodes=1,
                                        timeout=3600,
                                        partition: str = SLURM_CPU_PARTITION,
                                        via_head=True):
    '''run the given cmd in parallel on multiple available cpu nodes.
    :param list cmd: a subprocess cmd list
    :param string parallelizable_option: the option which is given to the parallelized cmd for a subset of the  parallelizable_option_values
    :param list parallelizable_option_values: the list of values which is chunked for the parallelized cmd for the parallelizable_option
    :param float max_normalized_load: filter available nodes which have at most max_normalized_load
    :param int min_nr_of_nodes: run on this minimum number of nodes, even if their load is higher than max_normalized_load
    :param int timeout: timeout in seconds after which the workers are killed
    :param str partition: the (slurm) partition 'cpu'/'gpu'
    :return: True if all processes on all cpu nodes exited ok, else False
    '''
    available_cep4_nodes = get_cep4_available_nodes_sorted_ascending_by_load(max_normalized_load=max_normalized_load,
                                                                             min_nr_of_nodes=min_nr_of_nodes,
                                                                             partition=partition)

    if len(available_cep4_nodes) == 0:
        logger.warning('No cep4 cpu nodes available..')
        return False

    num_workers = max(1, min(len(available_cep4_nodes), len(parallelizable_option_values)))
    num_option_values_per_worker = int(math.ceil(len(parallelizable_option_values) / float(num_workers)))
    cmd_list = []

    logger.info('parallelizing cmd: %s over option %s with values %s',
                ' '.join(str(x) for x in cmd),
                parallelizable_option,
                ' '.join(str(x) for x in parallelizable_option_values))

    # start the workers
    for i in range(num_workers):
        option_values_for_worker = parallelizable_option_values[i * num_option_values_per_worker:(i + 1) * num_option_values_per_worker]
        if option_values_for_worker:
            option_values_for_worker_csv = ','.join([str(s) for s in option_values_for_worker])
            worker_cmd = cmd + [parallelizable_option, option_values_for_worker_csv]
            worker_cmd = wrap_command_in_cep4_node_ssh_call(worker_cmd, available_cep4_nodes[i], partition=partition, via_head=via_head)
            cmd_list.append(worker_cmd)

    results = execute_in_parallel(cmd_list, timeout=timeout, gather_stdout_stderr=False)

    failed_results = [r for r in results if r.returncode != 0]
    success = len(failed_results) == 0

    if success:
        logger.info('all parallelized cmds finished successfully')
    else:
        logger.error('%s/%s parallelized cmds finished with errors', len(failed_results), num_workers)

    return success

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    logger.info(convert_slurm_nodes_string_to_node_number_list('  \t  cpu[20-39,41,45-48]  '))
    logger.info(convert_slurm_nodes_string_to_node_number_list('  \t  cpu03  '))
    logger.info(get_cep4_available_nodes())
    logger.info(get_cep4_available_nodes_sorted_ascending_by_load(min_nr_of_nodes=3, partition=SLURM_CPU_PARTITION))
    logger.info(get_cep4_available_nodes_sorted_ascending_by_load(min_nr_of_nodes=3, partition=SLURM_GPU_PARTITION))

