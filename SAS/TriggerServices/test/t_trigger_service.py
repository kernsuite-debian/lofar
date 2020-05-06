#!/usr/bin/env python3

# t_trigger_service.py
#
# Copyright (C) 2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import logging

from lofar.triggerservices.trigger_service import TriggerServiceMessageHandler, ALERTHandler, DEFAULT_TBB_PROJECT
import lofar.triggerservices.trigger_service as serv
from lofar.specificationservices.translation_service import SpecificationTranslationHandler
from lxml import etree

from unittest import mock

TRIGGER_PATH = 't_trigger_service.in/trigger_testing_20_03_17.xml'
TEST_USER = 'test'
TEST_HOST = 'localhost'
TEST_PROJECT = 'myproject'
LOCALDIR = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))

class TestTriggerHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        p = os.getenv('LOFARROOT')

        with open(TRIGGER_PATH) as f:
            cls.trigger_xml = f.read()

        cls.handler = TriggerServiceMessageHandler()

    def setUp(self):
        logging.info('-----------------')
        logging.info('Setup test %s' % self._testMethodName)

    def test_add_trigger_should_send_notification(self):
        with mock.patch('lofar.triggerservices.trigger_service._send_notification') as m, \
             mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc:
                serv._add_trigger(TEST_USER, TEST_HOST, TEST_PROJECT, self.trigger_xml)
                m.assert_called_once()

    def test_valid_trigger_should_add_specification_and_return_trigger_id(self):
        with mock.patch('lofar.triggerservices.trigger_service.validationrpc') as valrpc, \
             mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc, \
             mock.patch('lofar.triggerservices.trigger_service.translationrpc') as transrpc, \
             mock.patch('lofar.triggerservices.trigger_service.specificationrpc') as specrpc:

                tid = '42'

                valrpc.validate_trigger_specification.return_value = {'valid': True}
                #valrpc.validate_specification.return_value = {'valid': True}
                momrpc.get_project_priority.return_value = {'priority':1}
                momrpc.add_trigger.return_value = {'row_id': tid}
                momrpc.get_trigger_quota.return_value = {'used_triggers': 5, 'allocated_triggers': 6}
                transrpc.trigger_to_specification.return_value = {'specification':"<specification />"}

                response = self.handler.handle_trigger(TEST_USER, TEST_HOST, self.trigger_xml)

                specrpc.add_specification.assert_called_once()
                self.assertEqual(response['trigger-id'], tid)

    def test_invalid_trigger_should_raise_exception(self):
        with mock.patch('lofar.triggerservices.trigger_service.validationrpc') as valrpc:
                valrpc.validate_trigger_specification.return_value = {'valid': False}
                with self.assertRaises(Exception) as exception:
                    self.handler.handle_trigger(TEST_USER, TEST_HOST, self.trigger_xml)

    def test_unauthorized_trigger_should_raise_exception(self):
        with mock.patch('lofar.triggerservices.trigger_service.validationrpc') as valrpc, \
             mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc, \
             mock.patch('lofar.triggerservices.trigger_service.translationrpc') as transrpc, \
             mock.patch('lofar.triggerservices.trigger_service.specificationrpc') as specrpc:
                valrpc.validate_specification.return_value = {'valid': True}
                momrpc.allows_triggers.return_value = {'allows': False}
                with self.assertRaises(Exception) as exception:
                    self.handler.handle_trigger(TEST_USER, TEST_HOST, self.trigger_xml)

    def test_trigger_exceeding_quota_should_raise_exception(self):
        with mock.patch('lofar.triggerservices.trigger_service.validationrpc') as valrpc, \
             mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc, \
             mock.patch('lofar.triggerservices.trigger_service.translationrpc') as transrpc, \
             mock.patch('lofar.triggerservices.trigger_service.specificationrpc') as specrpc:
                valrpc.validate_specification.return_value = {'valid': True}
                momrpc.allows_triggers.return_value = {'allows': True}
                momrpc.get_trigger_quota.return_value = {'used_triggers': 5, 'allocated_triggers': 5}
                with self.assertRaises(Exception) as exception:
                    self.handler.handle_trigger(TEST_USER, TEST_HOST, self.trigger_xml)


class TestALERTHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        with open(LOCALDIR + '/example_voevent.xml') as f:
            cls.voevent_xml = f.read()
            cls.voevent_etree = etree.fromstring(cls.voevent_xml)

        cls.handler = ALERTHandler()

    def setUp(self):
        logging.info('-----------------')
        logging.info('Setup test %s' % self._testMethodName)

        popen_patcher = mock.patch('lofar.common.subprocess_utils.Popen')
        self.addCleanup(popen_patcher.stop)
        popen_patcher.start()

        get_current_stations_patcher = mock.patch('lofar.common.lcu_utils.get_current_stations', return_value=['cs001'])
        self.addCleanup(get_current_stations_patcher.stop)
        get_current_stations_patcher.start()

    def test_valid_voevent_should_invoke_tbb_dump(self):
        with mock.patch('lofar.mac.tbbservice.client.tbbservice_rpc.TBBRPC.do_tbb_subband_dump') as dump, \
             mock.patch('lofar.triggerservices.voevent_decider.ALERTDecider') as sciencecheck:

            self.handler._cache.get_project_info = mock.MagicMock()
            self.handler._cache.get_project_info.return_value = {'allow_triggers':True,
                                                                 'num_used_triggers': 4,
                                                                 'num_allowed_triggers': 5}
            self.handler._cache.get_active_tasks = mock.MagicMock()
            self.handler._cache.get_stations = mock.MagicMock()
            self.handler._cache.get_stations.return_value = ['CS004C']

            test_task = mock.MagicMock()
            test_task.radb_task = dict(otdb_id=123456)
            self.handler._cache.get_active_tasks.return_value = [test_task]
            sciencecheck.is_acceptable.return_value = True

            self.handler.handle_event(self.voevent_xml, self.voevent_etree)
            dump.assert_called_once()

    def test_voevent_exceeding_quota_should_raise_exception(self):
        with mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc:
            momrpc.allows_triggers.return_value = {'allows': True}
            momrpc.get_trigger_quota.return_value = {'used_triggers': 5, 'allocated_triggers': 5}

            with self.assertRaises(Exception) as err:
                self.handler.handle_event(self.voevent_xml, self.voevent_etree)
            self.assertTrue('pre-flight checks!' in str(err.exception))

    def test_voevent_not_authorized_should_raise_exception(self):
        with mock.patch('lofar.triggerservices.trigger_service.momqueryrpc') as momrpc:
            momrpc.allows_triggers.return_value = {'allows': False}
            momrpc.get_trigger_quota.return_value = {'used_triggers': 4, 'allocated_triggers': 5}

            with self.assertRaises(Exception) as err:
                self.handler.handle_event(self.voevent_xml, self.voevent_etree)
            self.assertTrue('pre-flight checks!' in str(err.exception))


if __name__ == '__main__':
    logformat = "%(asctime)s %(levelname)8s %(funcName)25s:%(lineno)-5d | %(threadName)10s | %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO)
    unittest.main()

