#!/usr/bin/env python3

# Copyright (C) 2017 ASTRON (Netherlands Institute for Radio Astronomy)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest import mock
import os

from lofar.triggerservices.trigger_cancellation_service import TriggerCancellationHandler


class TestTriggerCancellationHandler(unittest.TestCase):
    project_name = "test_lofar"
    trigger_id = 1
    obs_sas_id = 22
    obs_mom_id = 44
    mom_link = "https://lofar.astron.nl/mom3/user/main/list/setUpProjectList.do"

    def setUp(self):
        self.momqueryrpc_mock = mock.MagicMock()

        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': self.trigger_id, 'status': "OK" }
        self.momqueryrpc_mock.getMoMIdsForOTDBIds.return_value = {self.obs_sas_id: self.obs_mom_id}

    def test_start_listening_opens_momquery_rpc(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.start_handling()

        self.momqueryrpc_mock.open.assert_called()

    def test_stop_listening_closes_momquery_rpc(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.stop_handling()

        self.momqueryrpc_mock.close.assert_called()

    # Aborted

    def test_onObservationAborted_does_not_call_cancel_trigger_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_not_called()

    def test_onObservationAborted_calls_cancel_trigger_with_correct_trigger(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_called()


    def test_onObservationAborted_uses_correct_triggerid_and_sets_correct_cancellation_reason(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        # correct otdb id is used to obtain trigger
        call_otdb_id = self.momqueryrpc_mock.getMoMIdsForOTDBIds.call_args[0][0]
        self.assertEqual(self.obs_sas_id, call_otdb_id)

        # correct trigger id and reason are used to abort
        call_id, call_reason = self.momqueryrpc_mock.cancel_trigger.call_args[0]
        self.assertEqual(self.trigger_id, call_id)
        self.assertIn('aborted', call_reason)

    # Error

    def test_onObservationError_does_not_call_cancel_trigger_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationError(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_not_called()

    def test_onObservationError_calls_cancel_trigger_when_its_a_trigger(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationError(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_called()

    def test_onObservationError_uses_correct_triggerid_and_sets_correct_cancellation_reason(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationError(self.obs_sas_id, None)

        # correct otdb id is used to obtain trigger
        call_otdb_id = self.momqueryrpc_mock.getMoMIdsForOTDBIds.call_args[0][0]
        self.assertEqual(self.obs_sas_id, call_otdb_id)

        # correct trigger id and reason are used to abort
        call_id, call_reason = self.momqueryrpc_mock.cancel_trigger.call_args[0]
        self.assertEqual(self.trigger_id, call_id)
        self.assertIn('error', call_reason)

    # Conflict

    def test_onObservationConflict_does_not_call_cancel_trigger_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_not_called()

    def test_onObservationConflict_calls_cancel_trigger_when_its_a_trigger(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.momqueryrpc_mock.cancel_trigger.assert_called()

    def test_onObservationConflict_uses_correct_triggerid_and_sets_correct_cancellation_reason(self):
        handler = TriggerCancellationHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        # correct otdb id is used to obtain trigger
        call_otdb_id = self.momqueryrpc_mock.getMoMIdsForOTDBIds.call_args[0][0]
        self.assertEqual(self.obs_sas_id, call_otdb_id)

        # correct trigger id and reason are used to abort
        call_id, call_reason = self.momqueryrpc_mock.cancel_trigger.call_args[0]
        self.assertEqual(self.trigger_id, call_id)
        self.assertIn('conflict', call_reason)


if __name__ == "__main__":
    unittest.main()
