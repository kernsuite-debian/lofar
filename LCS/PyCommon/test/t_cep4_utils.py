#!/usr/bin/env python3

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

import unittest
from subprocess import call

import logging
from lofar.common.cep4_utils import *

logger = logging.getLogger(__name__)

class TestCep4Utils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cep4_true_cmd = wrap_command_in_cep4_head_node_ssh_call(['true'])
            if call(cep4_true_cmd) == 0:
                logger.info('We can reach the CEP4 head node. Continuing with tests...')
            else:
                logger.warning('Cannot reach the CEP4 head node. skipping tests...')
                raise unittest.SkipTest('Cannot reach the CEP4 head node. skipping tests...')
        except:
            raise unittest.SkipTest('Cannot reach the CEP4 head node. skipping tests...')

    def test_01_wrap_command_in_cep4_head_node_ssh_call(self):
        cmd = wrap_command_in_cep4_head_node_ssh_call(['true'])
        logger.info('executing command: %s', ' '.join(cmd))
        self.assertEqual(0, call(cmd))

    def test_02_get_cep4_available_cpu_nodes(self):
        node_nrs = get_cep4_available_nodes()
        self.assertTrue(isinstance(node_nrs, list))
        self.assertTrue(len(node_nrs) > 0)

    def test_03_wrap_command_in_cep4_random_node_ssh_call(self):
        '''
        this test calls and tests the functionality of the following methods via
        wrap_command_in_cep4_random_node_ssh_call: get_cep4_available_nodes, _wrap_command_in_cep4_node_ssh_call
        '''
        cmd = wrap_command_in_cep4_random_node_ssh_call(['true'], via_head=True)
        logger.info('executing command: %s', ' '.join(cmd))
        self.assertEqual(0, call(cmd))

    def test_04_wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(self):
        '''
        this test calls and tests the functionality of the following methods via
        wrap_command_in_cep4_random_node_ssh_call:
        get_cep4_available_nodes, get_cep4_nodes_loads,
        get_cep4_available_cpu_nodes_sorted_ascending_by_load, _wrap_command_in_cep4_node_ssh_call
        '''
        cmd = wrap_command_in_cep4_available_node_with_lowest_load_ssh_call(['true'], via_head=True)
        logger.info('executing command: %s', ' '.join(cmd))
        self.assertEqual(0, call(cmd))

    def test_05_wrap_command_for_docker_in_cep4_head_node_ssh_call(self):
        '''
        this test calls and tests the functionality of wrap_command_for_docker and
        wrap_command_in_cep4_head_node_ssh_call.
        It is assumed that a docker image is available on head.cep4.
        '''
        #wrap the command in a docker call first, and then in an ssh call
        cmd = wrap_command_for_docker(['true'], 'adder', 'latest')
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
        logger.info('executing command: %s', ' '.join(cmd))
        self.assertEqual(0, call(cmd))

    def test_06_get_slurm_info_from_within_docker_via_cep4_head(self):
        '''
        test to see if we can execute a command via ssh on the head node,
        from within a docker container, started via ssh on the head node (yes, that's multiple levels of indirection)
        '''
        # use the slurm sinfo command (because it's available on the head nodes only)...
        cmd = ['sinfo']
        # ...called on cep4 headnode...
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
        # ...from with the docker container...
        cmd = wrap_command_for_docker(cmd, 'adder', 'latest')
        # ...which is started on the cep4 head node
        cmd = wrap_command_in_cep4_head_node_ssh_call(cmd)
        logger.info('executing command: %s', ' '.join(cmd))

        #redirect stdout/stderr to /dev/null
        with open('/dev/null', 'w') as dev_null:
            self.assertEqual(0, call(cmd, stdout=dev_null, stderr=dev_null))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    unittest.main()
