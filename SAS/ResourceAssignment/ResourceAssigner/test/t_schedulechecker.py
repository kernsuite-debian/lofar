#!/usr/bin/env python3

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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.


import unittest
from unittest import mock
import datetime

from lofar.sas.resourceassignment.resourceassigner.schedulechecker import ScheduleChecker, movePipelineAfterItsPredecessors
from lofar.parameterset import parameterset

ra_notification_prefix = "ra_notification_prefix"


class TestingScheduleChecker(ScheduleChecker):
    def __init__(self, rarpc, momrpc, curpc, otdbrpc):
        # super gets not done to be able to insert mocks as early as possible otherwise the RPC block unittesting
        self._radbrpc = rarpc
        self._momrpc = momrpc
        self._curpc = curpc
        self._otdbrpc = otdbrpc


class ScheduleCheckerTest(unittest.TestCase):
    def setUp(self):
        thread_patcher = mock.patch('threading.Thread')
        thread_patcher.start()
        self.addCleanup(thread_patcher.stop)

        self.rarpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassignmentservice.rpc.RADBRPC')
        self.addCleanup(self.rarpc_patcher.stop)
        self.rarpc_mock = self.rarpc_patcher.start()

        momrpc_patcher = mock.patch('lofar.mom.momqueryservice.momqueryrpc')
        self.addCleanup(momrpc_patcher.stop)
        self.momrpc_mock = momrpc_patcher.start()

        curpc_patcher = mock.patch('lofar.sas.datamanagement.cleanup.rpc')
        self.addCleanup(curpc_patcher.stop)
        self.curpc_mock = curpc_patcher.start()

        otdbrpc_patcher = mock.patch('lofar.sas.otdb.otdbrpc.OTDBRPC')
        self.addCleanup(otdbrpc_patcher.stop)
        self.otdbrpc_mock = otdbrpc_patcher.start()

        # Default return values
        self.rarpc_mock.getTasks.return_value = [ { 'id': 'id', 'mom_id': '1', 'otdb_id': 'otdb_id', 'status': 'approved', 'type': 'observation', 'specification_id': 'specification_id' } ]
        self.momrpc_mock.getObjectDetails.return_value = { 1: { 'object_status': 'approved' } }

        self.rarpc_mock.deleteSpecification.return_value = True
        self.curpc_mock.getPathForOTDBId.return_value = { 'found': True }
        self.curpc_mock.removeTaskData.return_value = { 'deleted': True }

    def assert_all_services_opened(self):
        self.assertTrue(self.rarpc_mock.open.called, "RARPC.open was not called")
        self.assertTrue(self.momrpc_mock.open.called, "MOMRPC.open was not called")
        self.assertTrue(self.curpc_mock.open.called, "CURPC.open was not called")

    def assert_all_services_closed(self):
        self.assertTrue(self.rarpc_mock.close.called, "RARPC.close was not called")
        self.assertTrue(self.momrpc_mock.close.called, "MOMRPC.close was not called")
        self.assertTrue(self.curpc_mock.close.called, "CURPC.close was not called")

    def test_contextManager_opens_and_closes_all_services(self):
        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock):
            self.assert_all_services_opened()

        self.assert_all_services_closed()

    def test_movePipelineAfterItsPredecessors(self):
        """ Test if a pipeline is really moved beyond its predecessor. """

        self.rarpc_mock.getTasks.return_value = mock.DEFAULT

        def tasks(*args, **kwargs):
            if 'task_ids' in kwargs:
                return [ { 'id': '2', 'endtime': datetime.datetime(2017, 0o1, 0o1) } ]
            elif 'lower_bound' in kwargs:
                return []
            return mock.DEFAULT

        self.rarpc_mock.getTasks.side_effect = tasks

        task = {
          'id': 1,
          'status': 'scheduled',
          'otdb_id': 'otdb_id',
          'type': 'pipeline',
          'cluster': 'CEP4',
          'predecessor_ids': '1',
          'starttime': datetime.datetime(2016, 12, 31),
          'endtime': datetime.datetime(2017, 12, 31)
        }

        movePipelineAfterItsPredecessors(task, self.rarpc_mock)

        self.assertTrue(self.rarpc_mock.updateTaskAndResourceClaims.called, "Pipeline properties not updated.")
        self.assertTrue(self.rarpc_mock.updateTaskAndResourceClaims.call_args[1]["starttime"] >= datetime.datetime(2017, 0o1, 0o1), "Pipeline not moved after predecessor")
        self.assertEqual(
           self.rarpc_mock.updateTaskAndResourceClaims.call_args[1]["endtime"] - self.rarpc_mock.updateTaskAndResourceClaims.call_args[1]["starttime"],
           task["endtime"] - task["starttime"],
           "Pipeline duration changed after move")

    @mock.patch('lofar.sas.resourceassignment.resourceassigner.schedulechecker.movePipelineAfterItsPredecessors')
    def test_checkScheduledAndQueuedPipelines(self, movePipeline_mock):
        """ Test whether all scheduled/queued pipelines get a move request. """

        self.rarpc_mock.getTasks.return_value = [ { 'id': 'id', 'status': 'scheduled', 'type': 'pipeline', 'starttime': datetime.datetime.utcnow() } ]
        self.rarpc_mock.getTask.return_value =    { 'id': 'id', 'status': 'scheduled', 'type': 'pipeline', 'starttime': datetime.datetime.utcnow() }

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkScheduledAndQueuedPipelines()

            self.assertTrue(movePipeline_mock.called, "Pipeline was not moved.")

    def test_checkRunningPipelines(self):
        """ Test whether the end time of running pipelines is extended if they run beyond their end time. """

        self.rarpc_mock.getTasks.return_value = [ { 'id': 'id', 'mom_id': '1', 'otdb_id': 'otdb_id', 'status': 'active', 'type': 'pipeline', 'specification_id': 'specification_id', 'endtime': datetime.datetime.utcnow() } ]

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkRunningPipelines()

            self.assertTrue(self.rarpc_mock.updateTaskAndResourceClaims.called, "Task was not updated.")
            self.assertTrue("endtime" in self.rarpc_mock.updateTaskAndResourceClaims.call_args[1], "Task end-time was not updated.")

    def test_checkUnRunTasksForMoMOpenedStatus_mom_opened_otdb_approved(self):
        """ Test if a MoM task on 'opened' and in OTDB on 'approved' causes the task to be deleted. """
        self.momrpc_mock.getObjectDetails.return_value = { 1: { 'object_status': 'opened' } }

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkUnRunTasksForMoMOpenedStatus()

            self.assertTrue(self.curpc_mock.removeTaskData.called, "Task output was not deleted from disk")
            self.assertTrue(self.rarpc_mock.deleteSpecification.called, "Object was not removed from RADB")

    def test_checkUnRunTasksForMoMOpenedStatus_mom_approved_otdb_approved(self):
        """ Test if a MoM task on 'approved' and in OTDB on 'approved' causes the task NOT to be deleted. """
        self.momrpc_mock.getObjectDetails.return_value = { 1: { 'object_status': 'approved' } }

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkUnRunTasksForMoMOpenedStatus()

            self.assertFalse(self.curpc_mock.removeTaskData.called, "Task output was deleted from disk")
            self.assertFalse(self.rarpc_mock.deleteSpecification.called, "Object was removed from RADB")

    def test_checkUnRunTasksForMoMOpenedStatus_mom_notexisting_otdb_approved(self):
        """ Test if a task is not in MoM, and 'approved' in OTDB. This causes the task to be deleted. """
        self.momrpc_mock.getObjectDetails.return_value = {}

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkUnRunTasksForMoMOpenedStatus()

            self.assertTrue(self.rarpc_mock.deleteSpecification.called, "Object was not removed from RADB")

    def test_checkUnRunTasksForMoMOpenedStatus_only_observations_pipelines(self):
        """ Test if only observations and pipelines are compared against the MoMDB (and not maintenance or reservation tasks, for example). """

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock, self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkUnRunTasksForMoMOpenedStatus()

            self.assertEquals(self.rarpc_mock.getTasks.call_args[1]["task_type"], ['observation', 'pipeline'], "Only observations and pipelines must be matched against MoMDB")

    def test_checkUnRunReservations_does_not_delete_unscheduled_reservations(self):
        self.rarpc_mock.getTasks.return_value = [{'otdb_id': 123, 'id': 22, 'specification_id': 44}]
        self.otdbrpc_mock.taskGetStatus.return_value = 'unscheduled'

        with TestingScheduleChecker(self.rarpc_mock, self.momrpc_mock, self.curpc_mock,
                                    self.otdbrpc_mock) as schedulechecker:
            schedulechecker.checkUnRunReservations()

        self.rarpc_mock.deleteSpecification.assert_not_called()

if __name__ == '__main__':
    unittest.main()

