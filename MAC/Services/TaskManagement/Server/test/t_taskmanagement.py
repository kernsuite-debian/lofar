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

# $Id:  $
import unittest

from lofar.mac.services.taskmanagement.server.taskmanagement import TaskManagementHandler
from lofar.sas.otdb.otdbrpc import OTDBPRCException
from unittest import mock


class TestServiceSkeletonHandler(unittest.TestCase):
    obs_otdb_id = 6726
    running_obs_otdb_id = 9389
    pipeline_otdb_id = 8792
    reservation_otdb_id = 2783
    queued_obs_otdb_id = 9321

    def setUp(self):
        def get_task_side_effect(otdb_id):
            if otdb_id == self.obs_otdb_id:
                return {"status": "prescheduled", "type": "observation"}
            if otdb_id == self.running_obs_otdb_id:
                return {"status": "running", "type": "observation"}
            if otdb_id == self.queued_obs_otdb_id:
                return {"status": "queued", "type": "observation"}
            if otdb_id == self.pipeline_otdb_id:
                return {"status": "prescheduled", "type": "pipeline"}
            if otdb_id == self.reservation_otdb_id:
                return {"status": "prescheduled", "type": "reservation"}

        otdbrpc_patcher = mock.patch('lofar.mac.services.taskmanagement.server.taskmanagement.OTDBRPC')
        self.addCleanup(otdbrpc_patcher.stop)
        self.otdbrpc_mock = otdbrpc_patcher.start()

        radbrpc_patcher = mock.patch('lofar.mac.services.taskmanagement.server.taskmanagement.RADBRPC')
        self.addCleanup(radbrpc_patcher.stop)
        self.radbrpc_mock = radbrpc_patcher.start()

        self.radbrpc_mock().getTask.side_effect = get_task_side_effect

        obs_ctrl_rpc_patcher = mock.patch('lofar.mac.services.taskmanagement.server.taskmanagement.ObservationControlRPCClient')
        self.addCleanup(obs_ctrl_rpc_patcher.stop)
        self.obs_ctrl_rpc_mock = obs_ctrl_rpc_patcher.start()

        logger_patcher = mock.patch('lofar.mac.services.taskmanagement.server.taskmanagement.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        self.handler = TaskManagementHandler()
        self.handler.start_handling()

    def test_AbortTask_should_abort_non_running_or_scheduled_observation(self):
        self.handler.AbortTask(self.obs_otdb_id)

        self.assertEqual(1, self.otdbrpc_mock().taskSetStatus.call_count)

    def test_AbortTask_should_abort_a_pipeline(self):
        self.handler.AbortTask(self.pipeline_otdb_id)

        self.assertEqual(1, self.otdbrpc_mock().taskSetStatus.call_count)

    def test_AbortTask_should_abort_a_reservation(self):
        self.handler.AbortTask(self.reservation_otdb_id)

        self.assertEqual(1, self.otdbrpc_mock().taskSetStatus.call_count)

    def test_AbortTask_should_not_abort_a_running_observation(self):
        self.handler.AbortTask(self.running_obs_otdb_id)

        self.assertEqual(0, self.otdbrpc_mock().taskSetStatus.call_count)

    def test_AbortTask_should_not_abort_a_queued_observation(self):
        self.handler.AbortTask(self.queued_obs_otdb_id)

        self.assertEqual(0, self.otdbrpc_mock().taskSetStatus.call_count)

    def test_AbortTask_should_abort_running_observation(self):
        self.handler.AbortTask(self.running_obs_otdb_id)

        self.obs_ctrl_rpc_mock().abort_observation.assert_called_with(self.running_obs_otdb_id)

    def test_AbortTask_should_return_aborted_true_on_success_for_running_observations(self):
        self.obs_ctrl_rpc_mock().abort_observation.return_value = {"aborted": True,
                                                                   "otdb_id": self.running_obs_otdb_id}

        result = self.handler.AbortTask(self.running_obs_otdb_id)

        self.assertTrue(result["aborted"])
        self.assertEqual(self.running_obs_otdb_id, result["otdb_id"])

    def test_AbortTask_should_return_aborted_false_on_failure_for_running_observations(self):
        self.obs_ctrl_rpc_mock().abort_observation.return_value = {"aborted": False,
                                                                   "otdb_id": self.running_obs_otdb_id}

        result = self.handler.AbortTask(self.running_obs_otdb_id)

        self.assertFalse(result["aborted"])
        self.assertEqual(self.running_obs_otdb_id, result["otdb_id"])

    def test_AbortTask_should_return_aborted_false_on_exception_setting_task_status(self):
        self.otdbrpc_mock().taskSetStatus.side_effect = OTDBPRCException("Not aborted")

        result = self.handler.AbortTask(self.pipeline_otdb_id)

        self.assertFalse(result["aborted"])

    def test_AbortTask_should_return_aborted_true_on_setting_task_status_to_aborted(self):
        result = self.handler.AbortTask(self.pipeline_otdb_id)

        self.assertTrue(result["aborted"])

    def test_AbortTask_should_log_aborting_of_active_task(self):
        self.handler.AbortTask(self.running_obs_otdb_id)

        self.logger_mock.info.assert_any_call("Aborting active task: %s", self.running_obs_otdb_id)

    def test_AbortTask_should_log_aborting_of_inactive_task(self):
        self.handler.AbortTask(self.pipeline_otdb_id)

        self.logger_mock.info.assert_any_call("Aborting inactive task: %s", self.pipeline_otdb_id)

if __name__ == "__main__":
    unittest.main()
