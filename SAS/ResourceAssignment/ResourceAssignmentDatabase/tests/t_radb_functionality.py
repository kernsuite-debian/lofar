#!/usr/bin/python

# Copyright (C) 2012-2015    ASTRON (Netherlands Institute for Radio Astronomy)
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
import psycopg2
import os
from datetime import datetime, timedelta
from dateutil import parser
import logging
from pprint import pformat

logger = logging.getLogger(__name__)

import unittest.mock as mock
from multiprocessing import Process, Event

from lofar.sas.resourceassignment.database.testing.radb_common_testing import RADBCommonTestMixin

from lofar.sas.resourceassignment.database.radb import RADatabase
from lofar.common.postgres import PostgresDatabaseConnection, PostgresDBQueryExecutionError, FETCH_ONE, FETCH_ALL
from time import sleep

class ResourceAssignmentDatabaseTest(RADBCommonTestMixin, unittest.TestCase):

    class test_task:
        """ A lot of tests involve manipulation of a task (and its corresponding specification) in the RADB. A test task 
        that can be written to the RADB in preparation of the actual test makes the test-code more clean. """

        task_status = "prescheduled"
        task_type = "observation"
        starttime = '2017-05-10 10:00:00'
        endtime = '2017-05-10 12:00:00'
        content = ""
        cluster = "CEP4"

    def _insert_test_spec(self,
                          starttime='2017-05-10 13:00:00',
                          endtime='2017-05-10 14:00:00',
                          content='testcontent',
                          cluster='CEP4'):
        query = "INSERT INTO resource_allocation.specification (starttime, endtime, content, cluster) " \
                "VALUES ('%s', '%s', '%s', '%s') RETURNING id" % (starttime, endtime, content, cluster)
        with PostgresDatabaseConnection(self.dbcreds) as connection:
            res = connection.executeQuery(query, fetch=FETCH_ALL)
            connection.commit()
            return res[0]['id']
    #
    def test_insert_specification_creates_new_entry(self):
        # insert spec
        content = 'testcontent'
        ident = self._insert_test_spec(content=content)

        # check it is there
        query = "SELECT content FROM resource_allocation.specification WHERE id=%s" % ident
        with PostgresDatabaseConnection(self.dbcreds) as connection:
            res = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue(content in str(res))

    def test_update_specification_changes_entry(self):
        # insert spec
        ident = self._insert_test_spec()

        with PostgresDatabaseConnection(self.dbcreds) as connection:
            # update existing spec content
            newcontent = 'testcontent_new'
            query = "UPDATE resource_allocation.specification SET content = '%s'" % newcontent
            connection.executeQuery(query)

            # check updated content
            query = "SELECT content FROM resource_allocation.specification WHERE id=%s" % ident
            res = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue(newcontent in str(res))

    def test_delete_specification(self):
        # insert spec
        content = 'deletecontent'
        ident = self._insert_test_spec(content=content)

        with PostgresDatabaseConnection(self.dbcreds) as connection:
            # make sure it's there
            query = "SELECT content FROM resource_allocation.specification WHERE id=%s" % ident
            res = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue(content in str(res))

            # delete testspec again
            query = "DELETE FROM resource_allocation.specification WHERE id = %s" % ident
            connection.executeQuery(query)

            # make sure it's gone
            query = "SELECT content FROM resource_allocation.specification WHERE id=%s" % ident
            res = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertFalse(content in str(res))

    # triggers in place?
    def test_insert_specification_swaps_startendtimes_if_needed(self):
        #when inserting spec with start>endtime, should raise error
        with self.assertRaises(PostgresDBQueryExecutionError) as context:
            # insert spec
            starttime = '2017-05-10 12:00:00'
            endtime = '2017-05-10 10:00:00'
            self._insert_test_spec(starttime=starttime, endtime=endtime)

    #
    # radb functionality tests
    #
    #

    def _insert_test_task_and_specification(self, mom_id=1, otdb_id=2):
        """ Inserts a sample task and specification (see self.test_class) to the RADB

        :param mom_id:  optional alternative MoM ID. Should be set uniquely if within a test multiple tasks are to be
                        inserted
        :param otdb_id: optional alternative OTDB OD. Should be set uniquely if within a test multiple tasks are to be
                        inserted.
        :returns 2-tuple (task_id, spec_id) or None if task wasn't inserted
        """

        task = self.radb.insertOrUpdateSpecificationAndTask(mom_id=mom_id,
                                                    otdb_id=otdb_id,
                                                    task_status=self.test_task.task_status,
                                                    task_type=self.test_task.task_type,
                                                    starttime=self.test_task.starttime,
                                                    endtime=self.test_task.endtime,
                                                    content=self.test_task.content,
                                                    cluster=self.test_task.cluster)

        if task['inserted']:
            return task['task_id'], task['specification_id']

    def test_getTaskStatuses_succeeds(self):
        """ Verifies if radb.getTaskStatuses() successfully fetches all expected task statuses """

        expected_statuses = [
            {'id': 200, 'name': 'prepared'},
            {'id': 300, 'name': 'approved'},
            {'id': 320, 'name': 'on_hold'},
            {'id': 335, 'name': 'conflict'},
            {'id': 350, 'name': 'prescheduled'},
            {'id': 400, 'name': 'scheduled'},
            {'id': 500, 'name': 'queued'},
            {'id': 600, 'name': 'active'},
            {'id': 900, 'name': 'completing'},
            {'id': 1000, 'name': 'finished'},
            {'id': 1100, 'name': 'aborted'},
            {'id': 1150, 'name': 'error'},
            {'id': 1200, 'name': 'obsolete'}]

        statuses = self.radb.getTaskStatuses()

        self.assertEquals(statuses, expected_statuses)

    def test_getTaskStatusNames_succeeds(self):
        """ Verifies if radb.getTaskStatusNames() successfully fetches all expected task status names  """

        expected_names = ['prepared', 'approved', 'on_hold', 'conflict', 'prescheduled', 'scheduled', 'queued',
                          'active', 'completing', 'finished', 'aborted', 'error', 'obsolete']

        names = self.radb.getTaskStatusNames()

        self.assertEqual(sorted(expected_names), sorted(names))

    def test_getTaskStatusId_wrong_status_fails(self):
        """ Verifies if radb.getTaskStatusId() raises an Exception if the idea of an unknown status is requested """

        wrong_status = 'willywonka'

        self.assertRaises(KeyError, self.radb.getTaskStatusId, wrong_status)

    def test_getTaskStatusId_right_status_succeeds(self):
        """ Verifies if radb.getTaskStatusId() successfully fetches the expected status id for a given status. """

        status = 'scheduled'
        expected_status_id = 400

        status_id = self.radb.getTaskStatusId(status)

        self.assertEqual(status_id, expected_status_id)

    def test_getTaskTypes_succeeds(self):
        """ Verifies if radb.getTaskTypes() successfully fetches all expected task types """

        expected_task_types = [
            {'id': 0, 'name': 'observation'},
            {'id': 1, 'name': 'pipeline'},
            {'id': 2, 'name': 'reservation'}]

        task_types = self.radb.getTaskTypes()

        self.assertEqual(task_types, expected_task_types)

    def test_getTaskTypeNames_succeeds(self):
        """ Verifies if radb.getTaskTypeNames() successfully fetches all expected task type names """

        expected_task_type_names = ['observation', 'pipeline', 'reservation']

        task_type_names = self.radb.getTaskTypeNames()

        self.assertEqual(task_type_names, expected_task_type_names)

    def test_getTaskTypeId_wrong_type_name_fails(self):
        """ Verifies if radb.getTaskTypeId() raises an exception if a type id is requested for a wrong type name """

        wrong_type_name = 'willywonka'

        self.assertRaises(KeyError, self.radb.getTaskTypeId, wrong_type_name)

    def test_getTaskTypeId_right_type_name_succeeds(self):
        """ Verifies if radb.getTaskTypeId() successfully fetches the type id for a given type name. """

        type_name = 'reservation'
        expected_type_id = 2

        type_id = self.radb.getTaskTypeId(type_name)

        self.assertEqual(type_id, expected_type_id)

    def test_getResourceClaimStatuses_succeeds(self):
        """ Verifies if radb.getResourceClaimStatuses() successfully fetches all expected claim statuses. """

        expected_claim_statuses = [
            {'id': 0, 'name': 'tentative'},
            {'id': 1, 'name': 'claimed'},
            {'id': 2, 'name': 'conflict'}]

        claim_statuses = self.radb.getResourceClaimStatuses()

        self.assertEqual(claim_statuses, expected_claim_statuses)

    def test_getResourceClaimStatusNames_succeeds(self):
        """ Verifies if radb.getResourceClaimStatusNames() successfully fetches all expected claim status names. """

        expected_claim_status_names = ['tentative', 'claimed', 'conflict']

        claim_status_names = self.radb.getResourceClaimStatusNames()

        self.assertEqual(claim_status_names, expected_claim_status_names)

    def test_getResourceClaimStatusId_wrong_claim_name_fails(self):
        """ Verifies if radb.getResourceClaimStatusId() raises an exception if a claim status id is requested for wrong
        claim name. """

        wrong_claim_name = 'willywonka'

        self.assertRaises(KeyError, self.radb.getResourceClaimStatusId, wrong_claim_name)

    def test_getResourceClaimStatusId_right_claim_name_succeeds(self):
        """ Verifies if radb.getResourceClaimStatusId() successfully fetches the expected claim ID for a given claim
        name. """

        claim_name = 'conflict'
        expected_claim_id = 2

        claim_id = self.radb.getResourceClaimStatusId(claim_name)

        self.assertEqual(claim_id, expected_claim_id)

    def test_getTasksTimeWindow_no_ids_fails(self):
        """ Verify if radb.getTasksTimeWindow() raises an exception when called with an empty ID lists for every ID
        type. """

        self.assertRaises(KeyError, self.radb.getTasksTimeWindow, task_ids=[], mom_ids=[], otdb_ids=[])

    def test_getTasksTimeWindow_multiple_kinds_of_ids_fails(self):
        """ Verify if radb.getTasksTimeWindow() raises an exception when called with IDs of more than one type. """

        task_ids = [0, 1, 2, 3]
        mom_ids = [4, 5, 6, 7]
        otdb_ids = [8, 9, 10, 11]

        self.assertRaises(KeyError, self.radb.getTasksTimeWindow, task_ids, mom_ids, otdb_ids)

    def test_getTasksTimeWindow_empty_ids_list_succeeds(self):
        """ Verify if radb.getTasksTimeWindow() returns an empty list when requesting a time window for an empty list
        of IDs. """

        time_windows = [self.radb.getTasksTimeWindow([], None, None),
                        self.radb.getTasksTimeWindow(None, [], None),
                        self.radb.getTasksTimeWindow(None, None, [])]

        expected_time_windows = [[], [], []]
        self.assertCountEqual(time_windows, expected_time_windows)

    def test_getTasksTimeWindow_empty_db_returns_no_time_window_succeeds(self):
        """ Verify if radb.getTasksTimeWindow() returns an invalid time window when requesting a time window for a
        non-existing task. """

        # Ask time window for a non-existing task id
        time_window = self.radb.getTasksTimeWindow([0], None, None)

        time_window = [time_window['min_starttime'], time_window['max_endtime']]
        expected_time_window = [None, None]
        self.assertCountEqual(time_window, expected_time_window)

    def test_getTasksTimeWindow_normal_use_succeeds(self):
        """ Verify if radb.getTasksTimeWindow() successfully return the expected time window when requesting a time
        window for an existing task. """

        # Shoot a task into RADB which time window can later be queried
        starttime = '2017-05-10 10:00:00'
        endtime = '2017-05-10 12:00:00'
        mom_id = 1
        otdb_id = 2
        task_id, _ = self._insert_test_task_and_specification(mom_id=mom_id, otdb_id=otdb_id)

        # Now query RADB for time_window based on task_id, mom_id, and otdb_id
        time_windows = [self.radb.getTasksTimeWindow([task_id], None, None),
                        self.radb.getTasksTimeWindow(None, [mom_id], None),
                        self.radb.getTasksTimeWindow(None, None, [otdb_id])]

        # The time_window based on task_id, mom_id, and otdb_id should be the same
        expected_time_windows = 3*[{'max_endtime': parser.parse(endtime), 'min_starttime': parser.parse(starttime)}]
        self.assertCountEqual(time_windows, expected_time_windows)

    def test_getTasks_no_ids_fails(self):
        """ Verify if radb.getTasks() raises an exception when called with an empty ID lists for every ID type. """

        self.assertRaises(KeyError, self.radb.getTasks, task_ids=[], mom_ids=[], otdb_ids=[])

    def test_getTasks_multiple_kinds_of_ids_fails(self):
        """ Verify if radb.getTasks() raises an exception when called with filled ID lists for multiple ID types. """

        task_ids = [0, 1, 2, 3]
        mom_ids = [4, 5, 6, 7]
        otdb_ids = [8, 9, 10, 11]

        self.assertRaises(KeyError, self.radb.getTasks, task_ids=task_ids, mom_ids=mom_ids, otdb_ids=otdb_ids)

    def test_getTasks_empty_ids_list_succeeds(self):
        tasks = [self.radb.getTasks(task_ids=[], mom_ids=None, otdb_ids=None),
                 self.radb.getTasks(task_ids=None, mom_ids=[], otdb_ids=None),
                 self.radb.getTasks(task_ids=None, mom_ids=None, otdb_ids=[])]

        expected_tasks = [[], [], []]
        self.assertCountEqual(tasks, expected_tasks)

    def test_getTasks_empty_db_returns_empty_list_succeeds(self):
        """ Verify if radb.getTasks() successfully returns an empty list when called with a task ID that is non-existing
        in RADB. """

        tasks = self.radb.getTasks(task_ids=[0])

        self.assertEqual(tasks, [])

    def test_getTasks_normal_use_succeeds(self):
        """ Verify if radb.getTasks() successfully returns the expected tasks when requesting tasks related to an
        existing task. """

        # Shoot a task into RADB which can later be fetched
        task_id, _ = self._insert_test_task_and_specification()

        # Now query RADB for the task based on task_id
        task = self.radb.getTasks(task_ids=[task_id])[0]

        # The task's task ID should be the same to pass this test
        self.assertEqual(task['id'], task_id)

    def test_getTask_no_ids_fails(self):
        """ Verify if radb.getTask() raises an exception when called without arguments. """

        self.assertRaises(KeyError, self.radb.getTask)

    def test_getTask_multiple_kinds_of_ids_fails(self):
        """ Verify if radb.getTask() raises an exception when called with multiple ID types defined. """
        self.assertRaises(KeyError, self.radb.getTask, 1, 2, 3, 4)

    def test_getTask_empty_db_returns_none_succeeds(self):
        """ Verify if radb.getTask() successfully returns an None when called with a task ID that doesn't exist in
        RADB. """

        task = self.radb.getTask(id=0)

        self.assertIsNone(task)


    def test_getTask_normal_use_succeeds(self):
        """ Verify if radb.getTask() successfully returns the expected task when requested to. """

        # Shoot a task into RADB which fetched
        task_id, _ = self._insert_test_task_and_specification()

        task = self.radb.getTask(id=task_id)

        self.assertEqual(task['id'], task_id)

    def test_insertTask_with_invalid_specification_id_raises_exception(self):
        """ Verify if radb.insertTask() raises an exception when called with non-existing specification ID """

        with self.assertRaises(Exception):
            self.radb.insertTask(0, 0, 'conflict', 'observation', 1)

    def test_insertTask_with_invalid_id_type_raises_exception(self):
        """ Verify if radb.insertTask() raises an exception when called with illegal mom_id and otdb_id types """

        # Insert a specification in order to be sure we use a valid specification_id
        spec_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00', endtime='2017-05-10 12:00:00',
                                                         content="", cluster="CEP4")

        with self.assertRaises(Exception):
            self.radb.insertTask('monkey see', 'is monkey do', 'conflict', 'observation', spec_id)

    def test_insertTask_allows_nonexisting_mom_and_otdb_ids(self):
        """ Verify if radb.insertTask() allows the insertion of a task with non-exising mom_id and otdb_id values """

        # Insert a specification in order to be sure we use a valid specification_id
        spec_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00', endtime='2017-05-10 12:00:00',
                                                content="", cluster="CEP4")
        mom_id = otdb_id = -1

        task_id = self.radb.insertTask(mom_id, otdb_id, 'conflict', 'observation', spec_id)

        self.assertIsNotNone(task_id)

    def test_insertTask_duplicate_mom_ids_fails(self):
        """ Verify if radb.insertTask() raises exception when called with already occupied mom_id """

        # Insert a specification in order to be sure we use a valid specification_id
        spec_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00', endtime='2017-05-10 12:00:00',
                                                content="", cluster="CEP4")

        with self.assertRaises(Exception):
            self.radb.insertTask(1, 1, 'conflict', 'observation', spec_id)
            self.radb.insertTask(1, 2, 'conflict', 'observation', spec_id)

    def test_insertTask_duplicate_otdb_ids_fails(self):
        """ Verify if radb.insertTask() raises exception when called with already occupied otdb_id """

        # Insert a specification in order to be sure we use a valid specification_id
        spec_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00', endtime='2017-05-10 12:00:00',
                                                content="", cluster="CEP4")

        with self.assertRaises(Exception):
            self.radb.insertTask(1, 1, 'conflict', 'observation', spec_id)
            self.radb.insertTask(2, 1, 'conflict', 'observation', spec_id)

    def test_insertTask_with_invalid_task_status_raises_exception(self):
        """ Verify if radb.insertTask() raises an exception when called with invalid task status """

        # Insert a specification in order to be sure we use a valid specification_id
        specification_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00',
                                                         endtime='2017-05-10 12:00:00',
                                                         content="", cluster="CEP4")

        with self.assertRaises(Exception):
            self.radb.insertTask(0, 0, 'willywonka', 'observation', specification_id)

    def test_insertTask_with_invalid_task_type_raises_exception(self):
        """ Verify if radb.insertTask() raises an exception when called with invalid task type """

        # Insert a specification in order to be sure we use a valid specification_id
        specification_id = self.radb.insertSpecification(starttime='2017-05-10 10:00:00',
                                                         endtime='2017-05-10 12:00:00',
                                                         content="", cluster="CEP4")

        with self.assertRaises(Exception):
            self.radb.insertTask(0, 0, 'conflict', 'willywonka', specification_id)

    def test_insertTask_normal_use_succeeds(self):
        """ Verify if radb.insertTask() successfully inserts a task when called with valid arguments. """

        sample_starttime = '2017-05-10 10:00:00'
        sample_endtime = '2017-05-10 12:00:00'
        sample_task = {
            'id': 1,
            'starttime': parser.parse(sample_starttime),
            'endtime': parser.parse(sample_endtime),
            'cluster': 'CEP4',
            'status': 'approved',
            'status_id': 300,
            'type': 'observation',
            'type_id': 0,
            'mom_id': 0,
            'otdb_id': 0,
            'blocked_by_ids': [],
            'predecessor_ids': [],
            'successor_ids': [],
            'duration': (parser.parse(sample_endtime) - parser.parse(sample_starttime)).seconds,
        }

        # Insert a specification in order to be sure we use a valid specification_id
        sample_task['specification_id'] = self.radb.insertSpecification(starttime=sample_starttime,
                                                                        endtime=sample_endtime,
                                                                        cluster=sample_task['cluster'],
                                                                        content='',)

        task_id = self.radb.insertTask(sample_task['mom_id'], sample_task['otdb_id'], sample_task['status'],
                                       sample_task['type'], sample_task['specification_id'])
        sample_task['id'] = task_id
        task = self.radb.getTask(id=task_id)

        self.assertEqual(task, sample_task)

    def test_deleteTask_with_non_excisting_task_id_fails(self):
        """ Verify if radb.deleteTask() fails when called with a non-excisting task ID. """

        successfully_deleted = self.radb.deleteTask(0)

        self.assertFalse(successfully_deleted)

    def test_deleteTask_removes_task_successfully(self):
        """ Verify if radb.deleteTask() successfully deletes the expected task """

        # Shoot a task and corresponding specification into RADB which can later be deleted
        task_id, spec_id = self._insert_test_task_and_specification()

        successfully_deleted = self.radb.deleteTask(task_id)

        self.assertTrue(successfully_deleted)
        self.assertIsNone(self.radb.getTask(id=task_id))

    def test_deleteTask_leaves_specification_untouched(self):
        """ Verify if radb.deleteTask() leaves a task's specification untouched when deleting the task """

        # Shoot a task and corresponding specification into RADB which can later be deleted
        task_id, spec_id = self._insert_test_task_and_specification()

        self.radb.deleteTask(task_id)

        self.assertNotEqual(self.radb.getSpecification(spec_id), [])

    def test_updateTask_nonexisting_task_id_fails(self):
        """ Verify if radb.updateTask() fails when called with a non-existing task ID """

        task_id = -1

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id)


    def test_updateTask_invalid_task_status_raises_exception(self):
        """ Verify if radb.updateTask() raises an exception when called with illegal task_status """

        # Shoot a task and corresponding specification into RADB which can later be updated
        task_id, spec_id = self._insert_test_task_and_specification(mom_id=1, otdb_id=2)

        with self.assertRaises(Exception):
            self.radb.updateTask(task_id, task_status="willywonka")

    def test_updateTask_invalid_task_type_raises_exception(self):
        """ Verify if radb.updateTask() raises an exception when called with illegal task_type """

        # Shoot a task and corresponding specification into RADB which can later be updated
        task_id, spec_id = self._insert_test_task_and_specification(mom_id=1, otdb_id=2)

        with self.assertRaises(Exception):
            self.radb.updateTask(task_id, task_type="willywonka")

    def test_updateTask_invalid_specification_id_raises_exception(self):
        """ Verify if radb.updateTask() raises an exception when called with illegal specification ID """

        # Shoot a task and corresponding specification into RADB which can later be updated
        task_id, spec_id = self._insert_test_task_and_specification(mom_id=1, otdb_id=2)

        with self.assertRaises(Exception):
            self.radb.updateTask(task_id, spec_id=-1)                 # Illegal spec_id

    def test_updateTask_duplicate_mom_id_fail(self):
        """ Verify if radb.updateTask() raises an exception when called with an already occupied mom_id """

        # Shoot in two tasks and corresponding specifications into RADB with different mom_id and otdb_ids which can
        # later be updated
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=11)
        self._insert_test_task_and_specification(mom_id=2, otdb_id=12)

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id, mom_id=2)

    def test_updateTask_duplicate_otdb_id_fail(self):
        """ Verify if radb.updateTask() raises an exception when called with already existing otdb_id """

        # Shoot in two tasks and corresponding specifications into RADB with different mom_id and otdb_ids which can
        # later be updated
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=11)
        self._insert_test_task_and_specification(mom_id=2, otdb_id=12)

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id, otdb_id=12)

    def test_updateTask_normal_use_succeeds(self):
        """ Verify if radb.updateTask() successfully updates a task in RADB """

        # Shoot a task and corresponding specification into RADB which can later be updated
        mom_id = 1
        otdb_id = 2
        task_id, spec_id = self._insert_test_task_and_specification(mom_id=mom_id, otdb_id=otdb_id)
        new_task_status = "approved"
        new_task_type = "reservation"

        task_is_updated = self.radb.updateTask(task_id=task_id,
                                               mom_id=mom_id,
                                               otdb_id=otdb_id,
                                               task_status=new_task_status,
                                               task_type=new_task_type,
                                               specification_id=spec_id)
        task = self.radb.getTask(id=task_id)

        self.assertTrue(task_is_updated)
        self.assertEqual(task['status'], new_task_status)
        self.assertEqual(task['type'], new_task_type)

    def test_getTaskPredecessorIds_invalid_id_returns_empty_dict(self):
        """ Verify if radb.getTaskPredecessorIds() returns an empty dict when called with an invalid ID """

        id = -1

        task_and_predecessors = self.radb.getTaskPredecessorIds(id)

        self.assertEqual(task_and_predecessors, {})

    def test_getTaskPredecessorIds_valid_nonexisting_id_returns_empty_dict(self):
        """ Verify if radb.getTaskPredecessorIds() returns an empty dict when called with a valid ID that doesn't exist
        in RADB """

        id = 1

        task_and_predecessors = self.radb.getTaskPredecessorIds(id)

        self.assertEqual(task_and_predecessors, {})

    def test_getTaskPredecessorIds_normal_use_with_predecessor_succeeds(self):
        """ Verify if radb.getTaskPredecessorIds() returns an empty dict when called with a valid ID that exists in RADB
        and has a predecessor """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_pre1, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        # Add predecessors to task relation
        id = self.radb.insertTaskPredecessor(task_id, task_id_pre1)

        task_and_predecessors = self.radb.getTaskPredecessorIds(id)

        self.assertEqual(task_and_predecessors, {task_id: [task_id_pre1]})

    def test_getTaskSuccessorIds_invalid_id_returns_empty_dict(self):
        """ Verify if radb.getTaskSuccessorIds() returns an empty dict when called with an invalid ID """

        id = -1

        task_and_successors = self.radb.getTaskSuccessorIds(id)

        self.assertEqual(task_and_successors, {})

    def test_getTaskSuccessorIds_valid_nonexisting_id_returns_empty_dict(self):
        """ Verify if radb.getTaskSuccessorIds() returns an empty dict when called with a valid ID that doesn't exist in
        RADB """

        id = 1

        task_and_successors = self.radb.getTaskSuccessorIds(id)

        self.assertEqual(task_and_successors, {})

    def test_getTaskSuccessorIds_normal_use_with_successor_succeeds(self):
        """ Verify if radb.getTaskSuccessorIds() returns an empty dict when called with a valid ID that exists in RADB
        and has a successor """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_suc1, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        # Add predecessors to task relation
        id = self.radb.insertTaskPredecessor(task_id_suc1, task_id)

        task_and_successors = self.radb.getTaskSuccessorIds(id)

        self.assertEqual(task_and_successors, {task_id: [task_id_suc1]})

    def test_getTaskPredecessorIdsForTask_invalid_task_id_returns_empty_dict(self):
        """ Verify if radb.getTaskPredecessorIdsForTask() returns an empty dict when called with an invalid task ID """

        task_id = -1

        predecessors = self.radb.getTaskPredecessorIdsForTask(task_id)

        self.assertEqual(predecessors, [])

    def test_getTaskPredecessorIdsForTask_valid_nonexisting_task_id_returns_empty_dict(self):
        """ Verify if radb.getTaskPredecessorIdsForTask() returns an empty dict when called with a valid task ID that
        doesn't exist in RADB """

        task_id = 1

        predecessors = self.radb.getTaskPredecessorIdsForTask(task_id)

        self.assertEqual(predecessors, [])

    def test_getTaskPredecessorIdsForTask_normal_use_with_successor_succeeds(self):
        """ Verify if radb.getTaskPredecessorIdsForTask() returns an empty dict when called with a valid task ID that
        exists in RADB and has a predecessor """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_pre1, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        # Add predecessors to task relation
        self.radb.insertTaskPredecessor(task_id, task_id_pre1)

        predecessors = self.radb.getTaskPredecessorIdsForTask(task_id)

        self.assertEqual(predecessors, [task_id_pre1])

    def test_getTaskSuccessorIdsForTask_invalid_task_id_returns_empty_dict(self):
        """ Verify if radb.getTaskSuccessorIdsForTask() returns an empty dict when called with an invalid task ID """

        task_id = -1

        successors = self.radb.getTaskSuccessorIdsForTask(task_id)

        self.assertEqual(successors, [])

    def test_getTaskSuccessorIdsForTask_valid_nonexisting_task_id_returns_empty_dict(self):
        """ Verify if radb.getTaskSuccessorIdsForTask() returns an empty dict when called with a valid task ID that
        doesn't exist in RADB """

        task_id = 1

        successors = self.radb.getTaskSuccessorIdsForTask(task_id)

        self.assertEqual(successors, [])

    def test_getTaskSuccessorIdsForTask_normal_use_with_successor_succeeds(self):
        """ Verify if radb.getTaskSuccessorIdsForTask() returns an empty dict when called with a valid task ID that
        exists in RADB and has a successor """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_suc1, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        # Add predecessors to task relation
        self.radb.insertTaskPredecessor(task_id_suc1, task_id)

        successors = self.radb.getTaskSuccessorIdsForTask(task_id)

        self.assertEqual(successors, [task_id_suc1])

    def test_insertTaskPredecessor_invalid_ids(self):
        """ Verify if radb.insertTaskPredecessor() raise when called with invalid task ID and/or predecessor ID
        """

        invalid_id = -1

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertTaskPredecessor(invalid_id, 1)

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertTaskPredecessor(1, invalid_id)

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertTaskPredecessor(invalid_id, invalid_id)

    def test_insertTaskPredecessor_valid_nonexisting_ids_raise(self):
        """ Verify if radb.insertTaskPredecessor() returns None when called with valid but non-existing task ID and
        predecessor ID """

        task_id = 1
        predecessor_id = 1

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertTaskPredecessor(task_id, predecessor_id)

    def test_insertTaskPredecessor_normal_use_succeeds(self):
        """ Verify if radb.insertTaskPredecessor() returns an ID when called with valid and existing task and
        predecessor IDs. """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id_a, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_b, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)

        _id = self.radb.insertTaskPredecessor(task_id_a, task_id_b)

        self.assertIsNotNone(_id)

    def test_insertTaskPredecessors_normal_use_succeeds(self):
        """ Verify if radb.insertTaskPredecessors() returns a list of IDs when called with valid and existing task and
        predecessor IDs. """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id_a, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_b, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        task_id_c, _ = self._insert_test_task_and_specification(mom_id=3, otdb_id=12)

        ids = self.radb.insertTaskPredecessors(task_id_a, [task_id_b, task_id_c])

        self.assertIs(len(ids), 2)

    def test_reinsert_task_with_predecessor(self):
        """ Verify if radb.insertTaskPredecessor() returns an ID when called with valid and existing task and
        predecessor IDs. """

        # Shoot 2 unique tasks and corresponding specifications into RADB
        task_id_a, _ = self._insert_test_task_and_specification(mom_id=1, otdb_id=10)
        task_id_b, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)

        # link b to predecessor a and check it
        self.radb.insertTaskPredecessor(task_id_b, task_id_a)
        self.assertEqual([], self.radb.getTask(task_id_a)['predecessor_ids'])
        self.assertEqual([task_id_a], self.radb.getTask(task_id_b)['predecessor_ids'])

        # reinsert task b
        # check if b is still linked to a
        task_id_b, _ = self._insert_test_task_and_specification(mom_id=2, otdb_id=11)
        self.assertEqual([], self.radb.getTask(task_id_a)['predecessor_ids'])
        self.assertEqual([task_id_a], self.radb.getTask(task_id_b)['predecessor_ids'])

    def test_getSpecifications_select_all_on_empty_db_succeeds(self):
        """ Verify if radb.getSpecifications() returns an empty list on an empty RADB """

        self.assertEqual(self.radb.getSpecifications(), [])

    def test_getSpecifications_normal_use_no_filter_succeeds(self):
        """ Verify if radb.getSpecifications() returns a list containing all specifications that exist in the RADB """

        spec_ids = [self._insert_test_spec(), self._insert_test_spec(), self._insert_test_spec()]

        specifications = self.radb.getSpecifications()

        self.assertEqual(len(spec_ids), len(specifications))

    def test_getSpecifications_normal_use_select_one_succeeds(self):
        """ Verify if radb.getSpecifications() returns a list containing one of the three specifications that exist in
        the RADB """

        spec_ids = [self._insert_test_spec(), self._insert_test_spec(), self._insert_test_spec()]

        specifications = self.radb.getSpecifications(spec_ids[1])

        self.assertEqual(len(specifications), 1)

    def test_getSpecifications_normal_use_select_multiple_succeeds(self):
        """ Verify if radb.getSpecifications() returns a list containing two of the three specifications that exist in
        the RADB """

        spec_ids = [self._insert_test_spec(), self._insert_test_spec(), self._insert_test_spec()]

        specifications = self.radb.getSpecifications([spec_ids[1], spec_ids[2]])

        self.assertEqual(len(specifications), 2)

    def test_getSpecification_normal_use_select_one_succeeds(self):
        """ Verify if radb.getSpecification() returns a single single specification """

        spec_ids = [self._insert_test_spec(), self._insert_test_spec(), self._insert_test_spec()]

        specification = self.radb.getSpecification(spec_ids[1])

        self.assertTrue(specification)
        self.assertEqual(spec_ids[1], specification['id'])

    def test_task_and_claim_conflicts(self):
        # TODO: split up once the test setup is faster (not creating a new db for each test method)
        # for testing purposes let's give CEP4 storage a total size of 100
        cep4_id = 117
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100, total_capacity=100))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to full hour

        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', now, now+timedelta(hours=1),
        'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        spec_id1 = result['specification_id']
        task_id1 = result['task_id']

        task1 = self.radb.getTask(task_id1)
        self.assertTrue(task1)
        self.assertEqual(task_id1, task1['id'])

        # try to update the task status to scheduled, should not succeed, because it isn't prescheduled yet
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id1, task_status='scheduled')

        # try to update the task status to scheduled via prescheduled first
        self.assertTrue(self.radb.updateTask(task_id1, task_status='prescheduled'))
        self.assertTrue(self.radb.updateTask(task_id1, task_status='scheduled'))

        # ok, that works...
        # now unscheduled it again so we can add some claims
        self.assertTrue(self.radb.updateTask(task_id1, task_status='approved'))

        t1_claim1 = { 'resource_id': cep4_id,
                      'starttime': task1['starttime'],
                      'endtime': task1['endtime'],
                      'status': 'tentative',
                      'claim_size': 40 }

        # insert 1 claim
        t1_claim_ids = self.radb.insertResourceClaims(task_id1, [t1_claim1], 'foo', 1, 1)
        self.assertEqual(1, len(t1_claim_ids))

        #get claim using t1_claim_ids, and check if db version is equal to original
        t1_claims = self.radb.getResourceClaims(claim_ids=t1_claim_ids)
        self.assertEqual(1, len(t1_claims))
        for key, value in t1_claim1.items():
            if key != 'status':
                self.assertEqual(value, t1_claims[0][key])

        #get claim again via task_id1, and check if db version is equal to original
        t1_claims = self.radb.getResourceClaims(task_ids=task_id1)
        self.assertEqual(1, len(t1_claims))
        for key, value in t1_claim1.items():
            if key != 'status':
                self.assertEqual(value, t1_claims[0][key])

        # try to insert a claim with the wrong (already 'claimed') status. Should rollback, and return no ids.
        t1_claim2 = { 'resource_id': cep4_id,
                      'starttime': task1['starttime'],
                      'endtime': task1['endtime'],
                      'status': 'claimed',
                      'claim_size': 10 }
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertResourceClaims(task_id1, [t1_claim2], 'foo', 1, 1)
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_id1))) #there should still be one (proper/non-faulty) claim for this task

        # try to insert a claim with the wrong (already 'conflict') status. Should rollback, and return no ids.
        t1_claim3 = { 'resource_id': cep4_id,
                      'starttime': task1['starttime'],
                      'endtime': task1['endtime'],
                      'status': 'conflict',
                      'claim_size': 10 }
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertResourceClaims(task_id1, [t1_claim3], 'foo', 1, 1)
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.insertResourceClaims(task_id1, [t1_claim2], 'foo', 1, 1)
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_id1))) #there should still be one (proper/non-faulty) claim for this task

        # try to update the task status to scheduled (via prescheduled), should not succeed, since it's claims are not 'claimed' yet.
        self.assertTrue(self.radb.updateTask(task_id1, task_status='prescheduled'))
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.assertFalse(self.radb.updateTask(task_id1, task_status='scheduled'))
        self.assertEqual('prescheduled', self.radb.getTask(task_id1)['status'])

        # try to update the claim status to claimed, should succeed.
        self.assertTrue(self.radb.updateResourceClaims(t1_claim_ids, status='claimed'))
        self.assertEqual('claimed', self.radb.getResourceClaim(t1_claim_ids[0])['status'])

        # try to update the task status to scheduled again, should succeed this time.
        self.assertTrue(self.radb.updateTask(task_id1, task_status='scheduled'))
        self.assertEqual('scheduled', self.radb.getTask(task_id1)['status'])

        self.assertEqual(0, len(self.radb.get_overlapping_claims(t1_claim_ids[0])))
        self.assertEqual(0, len(self.radb.get_overlapping_tasks(t1_claim_ids[0])))

        self.assertEqual(40, self.radb.get_max_resource_usage_between(cep4_id, task1['starttime'], task1['starttime'], 'claimed')['usage'])
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, task1['starttime']-timedelta(hours=2), task1['starttime']-timedelta(hours=1), 'claimed')['usage'])

        logger.info('------------------------------ concludes task 1 ------------------------------')
        logger.info('-- now test with a 2nd task, and test resource availability, conflicts etc. --')

        # another task, fully overlapping with task1
        result = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', now, now+timedelta(hours=1), 'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        spec_id2 = result['specification_id']
        task_id2 = result['task_id']

        task2 = self.radb.getTask(task_id2)
        self.assertTrue(task2)

        # insert a claim which won't fit, claim status after insert should be 'conflict' instead of 'tentative'
        t2_claim1 = { 'resource_id': cep4_id,
                      'starttime': task2['starttime'],
                      'endtime': task2['endtime'],
                      'status': 'tentative',
                      'claim_size': 90 }

        t2_claim_ids = self.radb.insertResourceClaims(task_id2, [t2_claim1], 'foo', 1, 1)
        self.assertEqual(1, len(t2_claim_ids))

        # claim status after previous insert should be 'conflict' instead of 'tentative'
        t2_claims = self.radb.getResourceClaims(claim_ids=t2_claim_ids)
        self.assertEqual('conflict', t2_claims[0]['status'])
        # and the task's status should be conflict as well
        self.assertEqual('conflict', self.radb.getTask(task_id2)['status'])

        self.assertEqual(set([t1_claim_ids[0]]), set(c['id'] for c in self.radb.get_overlapping_claims(t2_claim_ids[0])))
        self.assertEqual(set([task_id1]), set(t['id'] for t in self.radb.get_overlapping_tasks(t2_claim_ids[0])))

        #try to connect this claim to task1, should fail
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(t2_claim_ids, task_id=task_id1)
        self.assertEqual(task_id2, t2_claims[0]['task_id'])

        #try to connect this claim to other resource, should fail
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(t2_claim_ids, resource_id=118)
        self.assertEqual(cep4_id, t2_claims[0]['resource_id'])

        # try to update the task status to scheduled (via prescheduled),
        # should not succeed, since it's claims are not 'claimed' yet.
        # setting it to prescheduled should not even succeed because of the claims in conflict
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id2, task_status='prescheduled')
        self.assertEqual('conflict', self.radb.getTask(task_id2)['status'])
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id2, task_status='scheduled')
        self.assertEqual('conflict', self.radb.getTask(task_id2)['status'])

        # try to update the claim status to claimed, should not succeed, since it still won't fit
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(t2_claim_ids, status='claimed')
        self.assertEqual('conflict', self.radb.getResourceClaim(t2_claim_ids[0])['status'])

        # do conflict resolution, shift task and claims
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, starttime=now+timedelta(hours=2),
                                                              endtime=now+timedelta(hours=3)))
        # now the task and claim status should not be conflict anymore
        self.assertEqual('tentative', self.radb.getResourceClaim(t2_claim_ids[0])['status'])
        self.assertEqual('approved', self.radb.getTask(task_id2)['status'])

        self.assertEqual(0, len(self.radb.get_overlapping_claims(t2_claim_ids[0])))
        self.assertEqual(0, len(self.radb.get_overlapping_tasks(t2_claim_ids[0])))

        # try to update the claim status to claimed, should succeed now
        self.assertTrue(self.radb.updateResourceClaims(t2_claim_ids, status='claimed'))
        self.assertEqual('claimed', self.radb.getResourceClaim(t2_claim_ids[0])['status'])

        # and try to update the task status to scheduled, should succeed now
        self.assertTrue(self.radb.updateTask(task_id2, task_status='prescheduled'))
        self.assertTrue(self.radb.updateTask(task_id2, task_status='scheduled'))
        self.assertEqual('scheduled', self.radb.getTask(task_id2)['status'])

        self.assertEqual(0, len(self.radb.get_overlapping_claims(t2_claim_ids[0])))
        self.assertEqual(0, len(self.radb.get_overlapping_tasks(t2_claim_ids[0])))

        # updating task/claim start/endtime should work, even for scheduled tasks with claimed claims
        # effect might be that a scheduled tasks goes to conflict
        # force conflict by moving back to original start/endtimes
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, starttime=task2['starttime'], endtime=task2['endtime']))
        self.assertEqual('conflict', self.radb.getResourceClaim(t2_claim_ids[0])['status'])
        self.assertEqual('conflict', self.radb.getTask(task_id2)['status'])

        # again do conflict resolution, shift task and claims
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, starttime=now+timedelta(hours=2), endtime=now+timedelta(hours=3)))
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, claim_status='claimed', task_status='prescheduled'))
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, task_status='scheduled'))
        # now the task and claim status should be scheduled/claimed
        self.assertEqual('scheduled', self.radb.getTask(task_id2)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(t2_claim_ids[0])['status'])

        # updating task/claim start/endtime should work, even for scheduled tasks with claimed claims
        # effect might be that a scheduled tasks goes to conflict
        # now, make simple endtime adjustment, task should stay scheduled

        logger.info("resource usages:\n%s", pformat(self.radb.getResourceUsages(now-timedelta(days=1.0), now+timedelta(days=2.0), cep4_id)))
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, endtime=now+timedelta(hours=2.75)))
        logger.info("resource usages:\n%s", pformat(self.radb.getResourceUsages(now-timedelta(days=1.0), now+timedelta(days=2.0), cep4_id)))

        # now the task and claim status should still be scheduled/claimed
        self.assertEqual('scheduled', self.radb.getTask(task_id2)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(t2_claim_ids[0])['status'])

        # now some weird corner case...
        # when a task is > queued (for example, finished)
        # then we don't want conflict statuses anymore if we update start/endtimes
        # test here with weird starttime shift back to overlap with task1
        self.assertTrue(self.radb.updateTask(task_id2, task_status='active'))
        self.assertEqual('active', self.radb.getTask(task_id2)['status'])
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, starttime=task1['starttime']))
        self.assertEqual('active', self.radb.getTask(task_id2)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(t2_claim_ids[0])['status'])

        #ok, that works, now set the start/end time back to 'normal' for some later test cases
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id2, starttime=now+timedelta(hours=2), endtime=now+timedelta(hours=3)))
        self.assertEqual('active', self.radb.getTask(task_id2)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(t2_claim_ids[0])['status'])


        logger.info('------------------------------ concludes task 2 ------------------------------')
        logger.info('-- now test with a 3rd task, and test resource availability, conflicts etc. --')

        #make sure we work with the latest info
        task1 = self.radb.getTask(task_id1)
        task2 = self.radb.getTask(task_id2)

        # another task, partially overlapping with both task1 & task3
        result = self.radb.insertOrUpdateSpecificationAndTask(2, 2, 'approved', 'observation',
                                                      task1['starttime'] + (task1['endtime']-task1['starttime'])/2,
                                                      task2['starttime'] + (task2['endtime']-task2['starttime'])/2,
                                                      'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        spec_id2 = result['specification_id']
        task_id3 = result['task_id']

        task3 = self.radb.getTask(task_id3)
        self.assertTrue(task3)

        # insert a claim which won't fit, claim status after insert should be 'conflict' instead of 'tentative'
        t3_claim1 = { 'resource_id': cep4_id,
                      'starttime': task3['starttime'],
                      'endtime': task3['endtime'],
                      'status': 'tentative',
                      'claim_size': 80 }

        t3_claim_ids = self.radb.insertResourceClaims(task_id3, [t3_claim1], 'foo', 1, 1)
        self.assertEqual(1, len(t3_claim_ids))

        # claim status after previous insert should be 'conflict' instead of 'tentative'
        t3_claims = self.radb.getResourceClaims(claim_ids=t3_claim_ids)
        self.assertEqual('conflict', t3_claims[0]['status'])
        # and the task's status should be conflict as well
        self.assertEqual('conflict', self.radb.getTask(task_id3)['status'])
        self.assertEqual(set([t1_claim_ids[0], t2_claim_ids[0]]), set(c['id'] for c in
                                                                      self.radb.get_overlapping_claims(t3_claim_ids[0])))
        self.assertEqual(set([task_id1, task_id2]), set(t['id'] for t in
                                                                      self.radb.get_overlapping_tasks(t3_claim_ids[0])))

        # try to update the task status to scheduled, should not succeed, since it's claims are not 'claimed' yet.
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateTask(task_id3, task_status='scheduled')
        self.assertEqual('conflict', self.radb.getTask(task_id3)['status'])

        # try to update the claim status to claimed, should not succeed, since it still won't fit
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(t3_claim_ids, status='claimed')
        self.assertEqual('conflict', self.radb.getResourceClaim(t3_claim_ids[0])['status'])

        # do conflict resolution, shift task away from task1 only (but keep overlapping with task2)
        self.assertTrue(self.radb.updateTaskAndResourceClaims(task_id3, starttime=task1['endtime'] + (task2['starttime']-task1['endtime'])/2))

        # now the task and claim status should still be in conflict
        self.assertEqual('conflict', self.radb.getResourceClaim(t3_claim_ids[0])['status'])
        self.assertEqual('conflict', self.radb.getTask(task_id3)['status'])

        self.assertEqual(set([t2_claim_ids[0]]), set(c['id'] for c in
                                                     self.radb.get_overlapping_claims(t3_claim_ids[0])))
        self.assertEqual(set([task_id2]), set(t['id'] for t in
                                              self.radb.get_overlapping_tasks(t3_claim_ids[0])))

        # do conflict resolution, reduce claim size (but keep overlapping with task2)
        self.assertTrue(self.radb.updateResourceClaim(t3_claim_ids[0], claim_size=5))

        # now the task and claim status should not be conflict anymore
        self.assertEqual('tentative', self.radb.getResourceClaim(t3_claim_ids[0])['status'])
        self.assertEqual('approved', self.radb.getTask(task_id3)['status'])

        self.assertEqual(1, len(self.radb.get_overlapping_claims(t3_claim_ids[0])))
        self.assertEqual(1, len(self.radb.get_overlapping_tasks(t3_claim_ids[0])))
        self.assertEqual(task2['id'], self.radb.get_overlapping_tasks(t3_claim_ids[0])[0]['id'])

        # try to update the claim status to claimed, should succeed now
        self.assertTrue(self.radb.updateResourceClaims(t3_claim_ids, status='claimed'))
        self.assertEqual('claimed', self.radb.getResourceClaim(t3_claim_ids[0])['status'])

        # and try to update the task status to scheduled, should succeed now
        self.assertTrue(self.radb.updateTask(task_id3, task_status='prescheduled'))
        self.assertTrue(self.radb.updateTask(task_id3, task_status='scheduled'))
        self.assertEqual('scheduled', self.radb.getTask(task_id3)['status'])

        # try to trick the radb by resetting the claim_size back to 80 now that it was claimed. Should fail.
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaim(t3_claim_ids[0], claim_size=80)
        #check if still 5, not 80
        self.assertEqual(5, self.radb.getResourceClaim(t3_claim_ids[0])['claim_size'])
        #and statuses should still be claimed/scheduled
        self.assertEqual('claimed', self.radb.getResourceClaim(t3_claim_ids[0])['status'])
        self.assertEqual('scheduled', self.radb.getTask(task_id3)['status'])


        # suppose the resource_usages table is broken for some reason, fix it....
        # break it first...
        self.radb.executeQuery('TRUNCATE TABLE resource_allocation.resource_usage;')
        self.radb.commit()
        #check that it's broken
        self.assertNotEqual(40, self.radb.get_max_resource_usage_between(cep4_id, task1['starttime'], task1['starttime'], 'claimed')['usage'])
        #fix it
        self.radb.rebuild_resource_usages_from_claims()
        #and test again that it's ok
        self.assertEqual(40, self.radb.get_max_resource_usage_between(cep4_id, task1['starttime'], task1['starttime'], 'claimed')['usage'])
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, task1['starttime']-timedelta(hours=2), task1['starttime']-timedelta(hours=1), 'claimed')['usage'])

    def test_resource_usages(self):
        # for testing purposous let's give CEP4 storage a total size of 100
        cep4_id = 117
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100, total_capacity=100))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour

        # we'll schedule some tasks in the future...        
        future = now + timedelta(hours=2)

        # insert one task, and reuse that for multiple  claims
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', future, future + timedelta(hours=1),
                                                      'content', 'CEP4')
        self.assertTrue(result['inserted'])
        task_id = result['task_id']
        task = self.radb.getTask(task_id)
        self.assertTrue(task)

        # insert a few claims one after the other, and check everything again and again in each intermediate step
        # because there are various special cases coded below where claims overlap/touch/etc which all need to be checked.

        # insert a claim, and check the usages for various timestamps
        claim1 = {'resource_id': cep4_id, 'starttime': future+timedelta(minutes=0), 'endtime': future+timedelta(minutes=10), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim1], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # insert another non-overlapping claim, and check the usages for various timestamps
        claim2 = {'resource_id': cep4_id, 'starttime': future+timedelta(minutes=20), 'endtime': future+timedelta(minutes=30), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim2], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # insert another claim which overlaps with both claim1 and claim2, and check the usages for various timestamps
        claim3 = {'resource_id': cep4_id, 'starttime': future+timedelta(minutes=5), 'endtime': future+timedelta(minutes=25), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim3], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])


        # insert another claim which overlaps with claim1 and ends at the same endtime as claim3, and check the usages for various timestamps
        claim4 = {'resource_id': cep4_id, 'starttime': future+timedelta(minutes=7.5), 'endtime': claim3['endtime'], 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim4], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage']) #c4_endtime should be equal to c3_endtime
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['endtime'], 'tentative')['usage']) #so usage should drop by 2*1 at this timestamp
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # insert another claim which starts when claim1 ends and last 1 minute, and check the usages for various timestamps
        claim5 = {'resource_id': cep4_id, 'starttime': claim1['endtime'], 'endtime': claim1['endtime']+timedelta(minutes=1), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim5], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage']) #drops by 1 because c1 ends, but climbs by 1 because c5 starts
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['starttime'], 'tentative')['usage']) #drops by 1 because c1 ends, but climbs by 1 because c5 starts
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['endtime'], 'tentative')['usage']) #drops by 1 because c5 ends
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # last edge case, insert another claim which starts when first claim starts, and end when last claim ends. Should lift all usages by 1 (except outer ones).
        claim6 = {'resource_id': cep4_id, 'starttime': claim1['starttime'], 'endtime': claim2['endtime'], 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim6], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage']) #c4_endtime should be equal to c3_endtime
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['endtime'], 'tentative')['usage']) #so usage should drop by 2*1 at this timestamp
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # conclude with two simple cases,
        # first final simple case: insert another claim follows (non overlapping/non-touching) all others
        claim7 = {'resource_id': cep4_id, 'starttime': claim2['endtime']+timedelta(minutes=10), 'endtime': claim2['endtime']+timedelta(minutes=20), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim7], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                logger.info('')
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=10), 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim7['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim7['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

        # second final simple case: insert another claim which precedes (non overlapping/non-touching) all the others
        claim8 = {'resource_id': cep4_id, 'starttime': claim1['starttime']-timedelta(minutes=20), 'endtime': claim1['starttime']-timedelta(minutes=10), 'status': 'tentative', 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim8], 'foo', 1, 1)
        # test usages twice, once to check the usages generated by insert-triggers, and then to check usages generated by rebuild_resource_usages_from_claims
        for i in range(2):
            if i == 1:
                # make sure the usage table is wiped, so asserts fail when rebuild_resource_usages_from_claims is erroneously roll'ed back.
                self.radb.executeQuery('TRUNCATE resource_allocation.resource_usage;')
                self.radb.rebuild_resource_usages_from_claims(cep4_id, 'tentative')
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(minutes=100), 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim8['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim8['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime']-timedelta(minutes=1), 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['starttime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim1['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['starttime'], 'tentative')['usage'])
            self.assertEqual( 3, self.radb.get_resource_usage_at_or_before(cep4_id, claim5['endtime'], 'tentative')['usage'])
            self.assertEqual( 4, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['starttime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim3['endtime'], 'tentative')['usage'])
            self.assertEqual( 2, self.radb.get_resource_usage_at_or_before(cep4_id, claim4['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim2['endtime'], 'tentative')['usage'])
            self.assertEqual( 1, self.radb.get_resource_usage_at_or_before(cep4_id, claim7['starttime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim7['endtime'], 'tentative')['usage'])
            self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(minutes=1000), 'tentative')['usage'])

    def test_overlapping_claims(self):
        # this is a special testcase to prove a bug found at 2017-08-16
        # the bug was that a claim that should fit, does not fit according to the radb claim-methods.
        # first, we'll prove that the bug exists (and that this test fails),
        # and then, we'll fix the code, (so this test succeeds)

        # for testing purposes let's give CEP4 storage a total size of 100
        cep4_id = 117
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100, total_capacity=100))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to full hour

        #nothing is claimed yet, so the claimable capacity should be 100 as well
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, now-timedelta(days=1.0), now+timedelta(days=1.0)))

        # we'll schedule some tasks in the future...        
        future = now + timedelta(hours=2)

        #insert one task, and reuse that for multiple overlapping claims
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', now, now+timedelta(hours=1),
                                                      'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])

        #create two overlapping claims
        claims = [ { 'resource_id': cep4_id,
                      'starttime': future,
                      'endtime': future+timedelta(hours=0.75),
                      'status': 'tentative',
                      'claim_size': 40 },
                   {'resource_id': cep4_id,
                    'starttime': future+timedelta(hours=0.25),
                    'endtime': future + timedelta(hours=1),
                    'status': 'tentative',
                    'claim_size': 40} ]

        # insert the claims
        claim_ids = self.radb.insertResourceClaims(task_id, claims, 'foo', 1, 1)
        self.assertEqual(2, len(claim_ids))
        claims_org = claims

        #get claim using t1_claim_ids, and check if db version is equal to original
        claims = self.radb.getResourceClaims(claim_ids=claim_ids)
        self.assertEqual(2, len(claims))
        for claim, claim_org in zip(claims, claims_org):
            for key, value in claim_org.items():
                if key != 'status':
                    self.assertEqual(value, claim_org[key])

        # try to update the claim status to claimed, should succeed.
        self.assertTrue(self.radb.updateResourceClaims(claim_ids, status='claimed'))
        for claim in self.radb.getResourceClaims(claim_ids=claim_ids):
            self.assertEqual('claimed', claim['status'])

        # check the resource usage trend
        logger.info("resource usages:\n%s", pformat(self.radb.getResourceUsages(future-timedelta(hours=1.0), future+timedelta(hours=2.0), cep4_id)))
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, future-timedelta(hours=1.0), future-timedelta(hours=0.01), 'claimed')['usage'])
        self.assertEqual(40, self.radb.get_max_resource_usage_between(cep4_id, future+timedelta(hours=0.0), future+timedelta(hours=0.2), 'claimed')['usage'])
        self.assertEqual(80, self.radb.get_max_resource_usage_between(cep4_id, future+timedelta(hours=0.3), future+timedelta(hours=0.6), 'claimed')['usage'])
        self.assertEqual(40, self.radb.get_max_resource_usage_between(cep4_id, future+timedelta(hours=0.80), future+timedelta(hours=1.0), 'claimed')['usage'])

        #check for a time range encapsulating the full task
        self.assertEqual(80, self.radb.get_max_resource_usage_between(cep4_id, future+timedelta(hours=-0.1), future+timedelta(hours=1.1), 'claimed')['usage'])

        #check for a time range not including the task
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, future+timedelta(hours=1.1), future+timedelta(hours=2.0), 'claimed')['usage'])
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, future-timedelta(hours=1.1), future-timedelta(hours=1.0), 'claimed')['usage'])

        # check that there are no overlapping conflicting claims/tasks
        for claim in claims:
            #both claims should overlap with one (the other) claim
            self.assertEqual(1, len(self.radb.get_overlapping_claims(claim['id'], 'claimed')))
            self.assertEqual(1, len(self.radb.get_overlapping_tasks(claim['id'], 'claimed')))

            #and there should be no overlapping claims of other status
            self.assertEqual(0, len(self.radb.get_overlapping_claims(claim['id'], 'tentative')))
            self.assertEqual(0, len(self.radb.get_overlapping_tasks(claim['id'], 'tentative')))

        #check claimable_capacity for various timestamps
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, future-timedelta(hours=1.0), future-timedelta(hours=1.0)))
        self.assertEqual(60, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.0), future+timedelta(hours=0.0)))
        self.assertEqual(60, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.2), future+timedelta(hours=0.2)))
        self.assertEqual(20, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.3), future+timedelta(hours=0.3)))
        self.assertEqual(20, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.5), future+timedelta(hours=0.5)))
        self.assertEqual(60, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.75), future+timedelta(hours=0.75)))
        self.assertEqual(60, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=0.8), future+timedelta(hours=0.8)))
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=1.0), future+timedelta(hours=1.0)))
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, future+timedelta(hours=10.0), future+timedelta(hours=10.0)))

        #check claimable_capacity for full task's timewindow (+extra)
        self.assertEqual(20, self.radb.get_resource_claimable_capacity(cep4_id, now-timedelta(hours=10.0), now+timedelta(hours=10.0)))


        #add an extra claim, overlapping with only the last claim of size 40. So it should fit (100-40=60 and 60>30).
        extra_claim = { 'resource_id': cep4_id,
                        'starttime': future+timedelta(hours=0.8),
                        'endtime': future+timedelta(hours=0.9),
                        'status': 'tentative',
                        'claim_size': 30 }
        extra_claim_ids = self.radb.insertResourceClaims(task_id, [extra_claim], 'foo', 1, 1)
        self.assertEqual(1, len(extra_claim_ids))

        #check the extra_claim's status, should be tentative. (used to be conflict before bug of 2017-08-16)
        for claim in self.radb.getResourceClaims(claim_ids=extra_claim_ids):
            self.assertEqual('tentative', claim['status'])

        # update the extra_claim status to 'claimed'. Should succeed.
        self.assertTrue(self.radb.updateResourceClaims(extra_claim_ids, status='claimed'))  #(used to fail before bug of 2017-08-16)
        for claim in self.radb.getResourceClaims(claim_ids=extra_claim_ids):
            self.assertEqual('claimed', claim['status']) #(used to be conflict before bug of 2017-08-16)

        #and finally, the task should be able to be scheduled (via prescheduled) as well.
        self.assertTrue(self.radb.updateTask(task_id, task_status='prescheduled'))
        self.assertTrue(self.radb.updateTask(task_id, task_status='scheduled'))
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

    def test_reinsert_task(self):
        # this is a special testcase to prove a bug found at 2017-08-28
        # the bug was that a specification is re-inserted, which causes the original spec to be deleted...
        # ... wich cascades, and deletes the task, and its claims, and it's usages, but that failed on the usages.
        # I've tried to reproduce the above bug which we see in production,
        # but unfortunately, I cannot reproduce it. The code just works as intended.
        # So, after consulting with JDM and AR, we decided to keep this test, and develop a consistency-check-method on the usage table.
        # We'll keep this new test anyway, just to prove that these cases work as expected.

        # for testing purposes let's give CEP4 storage a total size of 100
        cep4_id = 117
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100, total_capacity=100))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour

        # we'll schedule some tasks in the future...        
        future = now + timedelta(hours=2)

        # insert one task, and reuse that for multiple overlapping claims
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', future, future + timedelta(hours=1), 'first content',
                                                      'CEP4')
        self.assertTrue(result['inserted'])
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])
        self.assertEqual('first content', self.radb.getSpecification(task['specification_id'])['content'])

        # prove that we can re-insert the spec/task, and that the new task is indeed updated
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', future, future + timedelta(hours=1), 'second content',
                                                      'CEP4')
        self.assertTrue(result['inserted'])
        self.assertEqual(task_id, result['task_id']) # as per 20190916 inserting a task again should not yield a new task id.
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])
        self.assertEqual('second content', self.radb.getSpecification(task['specification_id'])['content']) #spec content should have been renewed

        # create and insert a claim
        claim = {'resource_id': cep4_id,
                 'starttime': task['starttime'],
                 'endtime': task['endtime'],
                 'status': 'tentative',
                 'claim_size': 40}
        claim_ids = self.radb.insertResourceClaims(task_id, [claim], 'foo', 1, 1)
        self.assertEqual(1, len(claim_ids))
        self.assertEqual(1, len(self.radb.getResourceClaims(claim_ids=claim_ids)))

        #check the extra_claim's status, should be tentative.
        for claim in self.radb.getResourceClaims(claim_ids=claim_ids):
            self.assertEqual('tentative', claim['status'])

        # update the extra_claim status to 'claimed'. Should succeed.
        self.assertTrue(self.radb.updateResourceClaims(claim_ids, status='claimed'))
        self.assertEqual(1, len(self.radb.getResourceClaims(claim_ids=claim_ids)))
        for claim in self.radb.getResourceClaims(claim_ids=claim_ids):
            self.assertEqual('claimed', claim['status'])

        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(hours=0.5), 'claimed')['usage'])
        self.assertEqual(40, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=0.5), 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=1.5), 'claimed')['usage'])

        # prove again that we can re-insert the spec/task (future with claims), and that the new task is indeed inserted and new,
        # and that the claim(s) and usage(s) were actually deleted (via cascading deletes)
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', future, future + timedelta(hours=1), 'third content',
                                                      'CEP4')
        self.assertTrue(result['inserted'])
        self.assertEqual(task_id, result['task_id']) # as per 20190916 inserting a task again should not yield a new task id.
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])
        self.assertEqual('third content', self.radb.getSpecification(task['specification_id'])['content']) #spec content should have been renewed

        # this newly inserted spec/task should have no claims anymore
        self.assertEqual( 0, len(self.radb.getResourceClaims()))
        # and all usages should future be 0
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(hours=0.5), 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=0.5), 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=1.5), 'claimed')['usage'])

        # 2017-08-29: ok, we could not reproduce the bug found on production,
        # so it seems there is a strange corner case which caused the usages table to become inconsistent.
        # after consulting with JDM and AR, we decided to mimic this inconsistency by 'corrupting' the table manually in this test,
        # and then act on the inconsistent table by detecting the inconsistency, and automatically repairing the usages table.
        # so, let's do that in the remainder of this test.

        #insert a claim again (cause we don't have a claim anymore since we inserted the spec/taks above)
        claim = {'resource_id': cep4_id,
                 'starttime': task['starttime'],
                 'endtime': task['endtime'],
                 'status': 'tentative',
                 'claim_size': 40}
        claim_ids = self.radb.insertResourceClaims(task_id, [claim], 'foo', 1, 1)
        self.assertEqual(1, len(claim_ids))
        self.assertEqual(1, len(self.radb.getResourceClaims(claim_ids=claim_ids)))

        # usages should be ok
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(hours=0.5), 'tentative')['usage'])
        self.assertEqual(40, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=0.5), 'tentative')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=1.5), 'tentative')['usage'])

        # now, let's break the usages table (intentionally, to mimic the production inconsistenty)
        # we shift one entry (where the claim starts) by one minute
        # result should be that when we change the claim (or delete the claim cause it's task/spec was deleted),
        # that the associated usage at the claim's starttime cannot be found anymore (which is the bug on production).
        self.radb.executeQuery("UPDATE resource_allocation.resource_usage SET as_of_timestamp = %s WHERE  as_of_timestamp = %s;", (future+timedelta(minutes=1), future))

        # check that the usages were indeed changed (the first one shifted in time)
        usages = self.radb.getResourceUsages()[cep4_id]['tentative']
        self.assertEqual({'usage': 40, 'as_of_timestamp': future+timedelta(minutes=1)}, usages[0])
        self.assertEqual({'usage':  0, 'as_of_timestamp': task['endtime']}, usages[1])

        # and prove again that we can re-insert the spec/task (future with claims and a corrupted usage table), and that the new task is indeed inserted and new,
        # and that the claim(s) and usage(s) were actually deleted (via cascading deletes)
        # 2017-08-29: YEAH! the insert fails just like on production. Now we can start making a fix!
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', future, future + timedelta(hours=1), 'fourth content',
                                                      'CEP4')
        self.assertTrue(result['inserted'])
        self.assertEqual(task_id, result['task_id']) # as per 20190916 inserting a task again should not yield a new task id.
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])
        self.assertEqual('fourth content', self.radb.getSpecification(task['specification_id'])['content']) #spec content should have been renewed

        # this newly inserted spec/task should have no claims anymore
        self.assertEqual( 0, len(self.radb.getResourceClaims()))
        # and all usages should future be 0
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future-timedelta(hours=0.5), 'tentative')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=0.5), 'tentative')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, future+timedelta(hours=1.5), 'tentative')['usage'])

    def test_claims_on_partially_misc_filled_resource(self):
        # this is a special testcase to prove a bug found at 2017-08-24
        # the bug was that a claim that should fit, does not fit according to the radb claim-methods.
        # the reason that it (erroneously) does not fit is an error in the get_resource_claimable_capacity_between method in sql.
        # first, we'll prove that the bug exists (and that this test fails),
        # and then, we'll fix the code, (so this test succeeds)

        #first make sure that there are no specs/tasks/claims lingering around
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        # for testing purposes let's give CEP4 storage a total size of 100
        cep4_id = 117
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100, total_capacity=100))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['available_capacity'])
        self.assertEqual(  0, self.radb.getResources(cep4_id, include_availability=True)[0]['used_capacity'])
        self.assertEqual(  0, self.radb.getResources(cep4_id, include_availability=True)[0]['misc_used_capacity'])

        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        #insert a task
        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start, start+timedelta(hours=2), 'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        task_id = result['task_id']

        task = self.radb.getTask(task_id)
        self.assertTrue(task)
        self.assertEqual(task_id, task['id'])

        #check if there is indeed still 100 claimable_capacity, and that there is no resource_usage
        #because there are no claims yet.
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, task['starttime'], task['endtime']))
        self.assertEqual(0, self.radb.get_max_resource_usage_between(cep4_id, task['starttime'], task['endtime'], 'claimed')['usage'])
        self.assertEqual(0, self.radb.get_current_resource_usage(cep4_id, 'claimed')['usage'])

        #add a claim for the task which should fit.
        #there is 100 available
        claim = { 'resource_id': cep4_id,
                  'starttime': task['starttime'],
                  'endtime': task['endtime'],
                  'status': 'tentative',
                  'claim_size': 60 }
        claim_id = self.radb.insertResourceClaims(task_id, [claim], 'foo', 1, 1)[0]
        claim = self.radb.getResourceClaims(claim_ids=[claim_id])[0]
        self.assertEqual('tentative', claim['status'])

        # because the claim is still tentative, there should be 100 claimable_capacity left
        self.assertEqual(100, self.radb.get_resource_claimable_capacity(cep4_id, task['starttime'], task['endtime']))

        # and the capacities of the resource should still be the same as in the beginning
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['available_capacity'])
        self.assertEqual(  0, self.radb.getResources(cep4_id, include_availability=True)[0]['used_capacity'])
        self.assertEqual(  0, self.radb.getResources(cep4_id, include_availability=True)[0]['misc_used_capacity'])

        # set the status to 'claimed', and check it.
        self.assertTrue(self.radb.updateResourceClaims(claim_id, status='claimed'))
        claim = self.radb.getResourceClaims(claim_ids=[claim_id])[0]
        self.assertEqual('claimed', claim['status'])

        #now the resource_usage should be 60
        self.assertEqual(60, self.radb.get_max_resource_usage_between(cep4_id, task['starttime'], task['endtime'], 'claimed')['usage'])
        self.assertEqual(60, self.radb.get_current_resource_usage(cep4_id, 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, start-timedelta(hours=1), 'claimed')['usage'])
        self.assertEqual(60, self.radb.get_resource_usage_at_or_before(cep4_id, claim['starttime'], 'claimed')['usage'])
        self.assertEqual(60, self.radb.get_resource_usage_at_or_before(cep4_id, start+timedelta(hours=0.25), 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, claim['endtime'], 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, task['endtime'], 'claimed')['usage'])
        self.assertEqual( 0, self.radb.get_resource_usage_at_or_before(cep4_id, task['endtime']+timedelta(hours=1), 'claimed')['usage'])

        # assume the data has NOT been written YET, and that the claim of size 60 does NOT occupy 60 YET on the resource
        # this happens during the observation. Data is being written, but the system does not know it yet.
        # then there should be still be 100-60(claimed)-nothing=40 claimable_capacity left
        self.assertEqual(40, self.radb.get_resource_claimable_capacity(cep4_id, task['starttime'], task['endtime']))

        # assume the observation finished, and data has been written
        # so, the claim of size 60 now occupies 60 on the resource
        # that would be detected (by the storagequeryservice) and propagated into the radb
        # so, let's update the available_capacity
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100-60))
        # check the capacities of the resource
        # please note that the misc_used_capacity=0 because we used exactly the same amount of diskspace as was claimed (as it should be)
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])
        self.assertEqual( 40, self.radb.getResources(cep4_id, include_availability=True)[0]['available_capacity'])
        self.assertEqual( 60, self.radb.getResources(cep4_id, include_availability=True)[0]['used_capacity'])
        self.assertEqual(  0, self.radb.getResources(cep4_id, include_availability=True)[0]['misc_used_capacity'])
        # and there should be 100-60=40 claimable_capacity left, because there is 60 claimed and 60 used (which matches fine, like it should)
        self.assertEqual(40, self.radb.get_resource_claimable_capacity(cep4_id, task['starttime'], task['endtime']))

        # so far, so good...
        # now onto the situation in practice....
        # suppose there is some additional (20) miscellaneous data on cep4, which is not known in claims (like backups/logs/other_data)
        # this should be reflected in the available_capacity and misc_used_capacity
        # available_capacity = 100-60-20 : 60 is claimed and in use, and 20 is other unaccounted for data.
        self.assertTrue(self.radb.updateResourceAvailability(cep4_id, available_capacity=100-60-20))
        self.assertEqual(100, self.radb.getResources(cep4_id, include_availability=True)[0]['total_capacity'])
        self.assertEqual( 20, self.radb.getResources(cep4_id, include_availability=True)[0]['available_capacity'])
        self.assertEqual( 80, self.radb.getResources(cep4_id, include_availability=True)[0]['used_capacity'])
        # and the used_capacity of 60 should be build up of the parts: resource_usage=60 and misc_used_capacity=20
        self.assertEqual( 60, self.radb.get_resource_usage_at_or_before(cep4_id, start+timedelta(hours=0.5), 'claimed')['usage'])
        self.assertEqual( 20, self.radb.getResources(cep4_id, include_availability=True)[0]['misc_used_capacity'])
        # and the resource_usage should still be 60 (because no claims were added/changed)
        self.assertEqual(60, self.radb.get_max_resource_usage_between(cep4_id, task['starttime'], task['endtime'], 'claimed')['usage'])
        self.assertEqual(60, self.radb.get_current_resource_usage(cep4_id, 'claimed')['usage'])
        # but, there should be less claimable capacity left: 100 -60 (claim) -20 (misc_data) = 20 claimable_capacity left
        self.assertEqual(20, self.radb.get_resource_claimable_capacity(cep4_id, task['starttime'], task['endtime']))
        # and for a new task (where there are no claims yet), there should be less claimable capacity left: 100-20 (misc_data) = 80 claimable_capacity left
        self.assertEqual(80, self.radb.get_resource_claimable_capacity(cep4_id, task['endtime'] + timedelta(hours=1), task['endtime'] + timedelta(hours=2)))

        #so, it should be possible to add an extra claim of 15 during this task (which should fit!)
        claim2 = { 'resource_id': cep4_id,
                   'starttime': task['starttime'],
                   'endtime': task['endtime'],
                   'status': 'tentative',
                   'claim_size': 15 }
        claim2_id = self.radb.insertResourceClaims(task_id, [claim2], 'foo', 1, 1)[0]
        claim2 = self.radb.getResourceClaims(claim_ids=[claim2_id])[0]
        self.assertEqual('tentative', claim2['status'])

        # and the claim should be able to have the status set to 'claimed'. check it.
        self.assertTrue(self.radb.updateResourceClaims(claim2_id, status='claimed'))
        claim2 = self.radb.getResourceClaims(claim_ids=[claim2_id])[0]
        self.assertEqual('claimed', claim2['status'])

        #and, it should also be possible to add an extra claim of 75 after this task (where there is no claim yet) (which should fit!)
        claim3 = { 'resource_id': cep4_id,
                   'starttime': task['endtime'] + timedelta(hours=1),
                   'endtime': task['endtime'] + timedelta(hours=2),
                   'status': 'tentative',
                   'claim_size': 75 }
        claim3_id = self.radb.insertResourceClaims(task_id, [claim3], 'foo', 1, 1)[0]
        claim3 = self.radb.getResourceClaims(claim_ids=[claim3_id])[0]
        self.assertEqual('tentative', claim3['status'])

        # and the claim should be able to have the status set to 'claimed'. check it.
        self.assertTrue(self.radb.updateResourceClaims(claim3_id, status='claimed'))
        claim3 = self.radb.getResourceClaims(claim_ids=[claim3_id])[0]
        self.assertEqual('claimed', claim3['status'])

    def test_double_claim_should_result_in_conflict_overlap_in_future(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start + timedelta(minutes=5),
                                                      start + timedelta(hours=2, minutes=5), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_conflict_within_larger_claim(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start + timedelta(minutes=5),
                                                      start + timedelta(hours=1, minutes=50), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_conflict_overlap_in_the_past(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start + timedelta(minutes=-5),
                                                      start + timedelta(hours=1, minutes=55), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]

        # task1 is partially in the way, so claim2 and task2 should have conflict status
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

        # updating claim2's status to claimed should not succeed
        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(claim2_id, status='claimed')
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_conflict_overlap_in_the_past_and_future(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start + timedelta(minutes=-5),
                                                      start + timedelta(hours=2, minutes=5), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_conflict_overlap_exactly(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_approved_with_no_overlap_future(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start + timedelta(hours=3),
                                                      start + timedelta(hours=5), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]

        self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

    def test_double_claim_should_result_in_approved_with_no_overlap_past(self):
        now = datetime.utcnow()
        start = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to current full hour

        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        result1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation', start + timedelta(hours=3),
                                                      start + timedelta(hours=5), 'foo', 'CEP4')
        task1_id = result1['task_id']

        task1 = self.radb.getTask(task1_id)

        claim1 = { 'resource_id': 212,
                  'starttime': task1['starttime'],
                  'endtime': task1['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim1_id = self.radb.insertResourceClaims(task1_id, [claim1], 'foo', 1, 1)[0]
        self.radb.updateResourceClaims(claim1_id, status='claimed')

        # claim same

        result2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation', start,
                                                      start + timedelta(hours=2), 'foo', 'CEP4')
        task2_id = result2['task_id']

        task2 = self.radb.getTask(task2_id)

        claim2 = { 'resource_id': 212,
                  'starttime': task2['starttime'],
                  'endtime': task2['endtime'],
                  'status': 'tentative',
                  'claim_size': 96 }
        claim2_id = self.radb.insertResourceClaims(task2_id, [claim2], 'foo', 1, 1)[0]

        self.radb.updateResourceClaims(claim2_id, status='claimed')

        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

    def test_dwellscheduler_high_low_priority_scenario(self):
        """special test case to prove and solve bug: https://support.astron.nl/jira/browse/SW-426
        """
        #start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id']) # cascades into tasks and claims

        ######################################################################################
        # setup phase, create tasks and claims. should just work.
        # we replay a responsive telescope trigger event, as performed by the dwellscheduler.
        # We have two tasks, one with high prio, and one with low.
        # the high prio tasks will have a conflict with the low one.
        ######################################################################################

        base_time = datetime.utcnow()
        # round to current full hour (for readability in logging)
        base_time = base_time - timedelta(minutes=base_time.minute, seconds=base_time.second, microseconds=base_time.microsecond)

        RESOURCE_ID = 252
        resource_max_cap = self.radb.get_resource_claimable_capacity(RESOURCE_ID, base_time, base_time)

        # insert the 'low prio' spec, task...
        spec_task_low = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'prescheduled', 'observation',
                                                             base_time + timedelta(minutes=5),
                                                             base_time + timedelta(minutes=10), 'foo', 'CEP4')
        task_low_id = spec_task_low['task_id']
        task_low = self.radb.getTask(task_low_id)


        # the dwellscheduler inserts the claim(s)...
        self.radb.insertResourceClaims(task_low_id, [{ 'resource_id': RESOURCE_ID,
                                                       'starttime': task_low['starttime'],
                                                       'endtime': task_low['endtime'],
                                                       'status': 'tentative',
                                                       'claim_size': resource_max_cap }],
                                       'user', 1)

        # ... and then the dwellscheduler sets the claims status to claimed...
        self.radb.updateResourceClaims(where_task_ids=[task_low_id], status="claimed")

        logger.info("task_low's claims: %s", self.radb.getResourceClaims(task_ids=task_low_id))

        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_low_id)))
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_low_id, status='claimed')))

        # ... and updates the spec's start and endtime to the already specified start and endtime
        # (why? not needed, but should not do any harm either)
        self.radb.updateSpecification(task_low['specification_id'],
                                      starttime=task_low['starttime'],
                                      endtime=task_low['endtime'])

        # finally make the task scheduled (via prescheduled_. Should still work.
        self.radb.updateTask(task_low_id, task_status='prescheduled')
        self.radb.updateTask(task_low_id, task_status='scheduled')

        # so fo so good. Everything should be normal and fine. Let's check.
        self.assertEqual('scheduled', self.radb.getTask(id=task_low_id)['status'])
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_low_id, status='claimed')))

        # now insert a second task, the so called high priority task,
        # overlapping with the beginning of task_low
        # so, the dwellscheduler finds task_low in task_high's higway
        # so, task_low is aborted by the dwellscheduler (later in the code).
        spec_task_high1 = self.radb.insertOrUpdateSpecificationAndTask(2, 2, 'approved', 'observation',
                                                              base_time,
                                                              base_time + timedelta(minutes=7), 'foo', 'CEP4')
        task_high1_id = spec_task_high1['task_id']
        task_high1 = self.radb.getTask(task_high1_id)

        # the dwellscheduler inserts the claim(s)...
        self.radb.insertResourceClaims(task_high1_id, [{ 'resource_id': RESOURCE_ID,
                                                         'starttime': task_high1['starttime'],
                                                         'endtime': task_high1['endtime'],
                                                         'status': 'tentative',
                                                         'claim_size': resource_max_cap }],
                                       'user', 1)

        logger.info("task_high1's claims: %s", self.radb.getResourceClaims(task_ids=task_high1_id))

        # we expect task_high1 to have on claim in conflict (with the claim of task_low)
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_high1_id)))
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_high1_id, status='claimed')))
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_high1_id, status='conflict')))

        claim_in_conflict = self.radb.getResourceClaims(task_ids=task_high1_id, status='conflict')[0]
        overlapping_claims = self.radb.get_overlapping_claims(claim_id=claim_in_conflict['id'])
        logger.info('claim_in_conflict: %s', claim_in_conflict)
        logger.info('overlapping_claims: %s', overlapping_claims)
        self.assertEqual(1, len(overlapping_claims))
        self.assertEqual(task_low_id, overlapping_claims[0]['task_id'])

        ########################################################################
        # end of setup phase, now let's (try to) reproduce the bug...
        # the dwellscheduler tries to abort task_low, to make room for task_high
        # this caused an erroneous database exception on the production system
        # but strangely enough we cannot repeat it here,
        # even though we follow the same code path.
        #
        # This leads us to the conclusion that there was a strange set of
        # circumstances in the data in the resource_usage table causing the bug in production.
        #
        # While examining the bug we did discover some errors in the sql code,
        # for which we added more additional tests:
        #  - test_task_releases_claims_when_set_to_approved
        #  - test_task_in_conflict_releases_claimed_claims
        #  - test_duplicate_full_claims_on_one_resource
        #  - test_task_and_claim_with_zero_duration
        #  - test_are_claims_in_conflict_released_by_removing_conclict_causing_claims
        #
        # Even though this test could not reproduce the error as it happened on production,
        # we'll keep it for future reference, and for future proof the the code still works.
        #
        ########################################################################

        with mock.patch('lofar.common.postgres.logger') as mocked_logger:
            with self.assertRaises(PostgresDBQueryExecutionError):
                self.radb.updateTaskAndResourceClaims(task_id=task_low_id, task_status='aborted',
                                                      endtime=task_low['starttime']) # yes, the endtime is set to the starttime

            # on production the above call produce the following log line:
            # 2018-06-29 09:46:16,240 ERROR Rolling back query='UPDATE resource_allocation.resource_claim SET (endtime) = (2018-06-29 11:59:17) WHERE task_id = 148052' due to error: 'duplicate key value violates unique constraint "usage_unique"
            # but unfortunately this error is not reproduced here,
            # the only thing we can test for is if a rollback occurs

            # test if there was a log line containing the database log message for 'claim starttime >= endtime'
            self.assertTrue(len([ca for ca in mocked_logger.error.call_args_list if 'Rolling back' in ca[0][0] and 'claim starttime >= endtime' in ca[0][0]]) > 0)


    def test_task_releases_claims_when_set_to_approved(self):
        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to full hour

        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                      now, now+timedelta(hours=1), 'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        self.assertIsNotNone(result['task_id'])
        task_id = result['task_id']
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])

        # select first (arbitrary) resource
        resource = self.radb.getResources(include_availability=True)[0]

        self.radb.insertResourceClaim(resource['id'], task_id, task['starttime'], task['endtime'],
                                      0.5*resource['available_capacity'], 'foo', 1)
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        self.assertEqual(1, len(tentative_claims))

        # set status to claimed
        self.radb.updateResourceClaims(where_task_ids=task_id, status='claimed')
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        self.assertEqual(0, len(tentative_claims))
        self.assertEqual(1, len(claimed_claims))

        # when setting the task to prescheduled and back to approved, all claimed claims should be released
        self.radb.updateTask(task_id=task_id, task_status='prescheduled')
        self.radb.updateTask(task_id=task_id, task_status='approved')
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])

        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        self.assertEqual(1, len(tentative_claims))
        self.assertEqual(0, len(claimed_claims))


    def test_task_in_conflict_releases_claimed_claims(self):
        """tests whether a task with multiple claims releases the claimed claims when the task goes to conflict.
        This is wanted behaviour, because when a single claim goes to conflict, then the task cannot be scheduled.
        So, it makes sense to release the other already claimed claims for other tasks.
        """
        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to full hour

        result = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                      now, now+timedelta(hours=1), 'foo', 'CEP4')
        self.assertTrue(result['inserted'])
        self.assertIsNotNone(result['task_id'])
        task_id = result['task_id']
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])

        # select first two (arbitrary) resources
        resources = self.radb.getResources(include_availability=True)
        resource1 = resources[0]
        resource2 = resources[1]

        # and insert a claim for each resource.
        # one claim should fit and be set to claimed...
        self.radb.insertResourceClaim(resource1['id'], task_id, task['starttime'], task['endtime'],
                                      0.5*resource1['available_capacity'], 'foo', 1)
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        self.assertEqual(1, len(tentative_claims))

        # set status to claimed
        self.radb.updateResourceClaims(where_task_ids=task_id, status='claimed')
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        self.assertEqual(0, len(tentative_claims))
        self.assertEqual(0, len(conflict_claims))
        self.assertEqual(1, len(claimed_claims))

        # the other claim should not fit and cause a conflict...
        self.radb.insertResourceClaim(resource2['id'], task_id, task['starttime'], task['endtime'],
                                      2.0*resource2['available_capacity'], 'foo', 1)

        # ... result should be that the task also goes to conflict ...
        task = self.radb.getTask(task_id)
        self.assertEqual('conflict', task['status'])

        # ... and that all the task's claimed claims should be released
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        self.assertEqual(1, len(tentative_claims))
        self.assertEqual(1, len(conflict_claims))
        self.assertEqual(0, len(claimed_claims))
        conflict_claim = conflict_claims[0]

        # a user/operator action could be to set the task back to approved
        # all claimed claims which were already set back to tentative should still be tentative
        # and claims in conflict should remain in conflict
        self.radb.updateTask(task_id=task_id, task_status='approved')
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])

        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        self.assertEqual(1, len(tentative_claims))
        self.assertEqual(1, len(conflict_claims))
        self.assertEqual(0, len(claimed_claims))
        self.assertEqual(conflict_claim['id'], conflict_claims[0]['id'])

    def test_duplicate_full_claims_on_one_resource(self):
        """special test case to prove and solve bug: https://support.astron.nl/jira/browse/SW-426
        We found out that inserting two duplicate claims for one resource does not result in the two claims
        having the conflict status, even though at least one of them should have it.
        """
        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        now = datetime.utcnow()
        # round to next full hour (for readability in logging)
        now = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        now = now + timedelta(hours=1)

        spec_task = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                         now, now + timedelta(minutes=10),
                                                         'foo', 'CEP4')

        task_id = spec_task['task_id']
        task = self.radb.getTask(task_id)

        RESOURCE_ID = 252
        resource_max_cap = self.radb.get_resource_claimable_capacity(RESOURCE_ID, now, now)

        # create one claim, with claim_size of max capacity
        claim = {'resource_id': RESOURCE_ID,
                 'starttime': task['starttime'],
                 'endtime': task['endtime'],
                 'status': 'tentative',
                 'claim_size': resource_max_cap}

        # insert the same claim twice, so two times the maxcap should not fit in total,
        # but should fit if only one is claimed
        self.radb.insertResourceClaims(task_id, [claim, claim], 'user', 1)

        # get the claims from the db, and check if there are 2, and check their status.
        # Both should have tentative status, and not conflict status,
        # because we did not claim anything yet.
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        self.assertEqual(2, len(tentative_claims))
        self.assertEqual(0, len(conflict_claims))
        self.assertEqual('approved', self.radb.getTask(task_id)['status'])

        # let's try to claim them both in one call.
        self.radb.updateResourceClaims(where_task_ids=[task_id], status='claimed')

        # Get the claims again from the db, and check if there are 2
        # one was successfully claimed, but put back to tentative,
        # because for the other there was no room, so it should be in conflict.
        # As a result of the claim in conflict, the task is in conflict as well.
        # And as a result of the task in conflict, all claimed claims are released and put back to tentative.
        # And because the claimed claim was put back to tentative, this frees up room for the claim in conflict,
        # which should not be in conflict anymore, but also tentative.
        # (Yes, this is quite confusing, but correct.)
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        self.assertEqual(2, len(tentative_claims))
        self.assertEqual(0, len(claimed_claims))
        self.assertEqual(0, len(conflict_claims))
        self.assertEqual('approved', self.radb.getTask(task_id)['status'])

        # let's try to claim only one.
        # One should fit, but as a result the other won't fit anymore and will go to conflict
        # which causes the task to go to conflict, which causes the claimed claim to be released,
        # which frees up space to the other which will be put to tentative after being in conflict.
        # (Yes, this is also quite confusing, but correct.)
        self.radb.updateResourceClaim(tentative_claims[0]['id'], status='claimed')
        tentative_claims = self.radb.getResourceClaims(task_ids=task_id, status='tentative')
        claimed_claims = self.radb.getResourceClaims(task_ids=task_id, status='claimed')
        conflict_claims = self.radb.getResourceClaims(task_ids=task_id, status='conflict')
        self.assertEqual(2, len(tentative_claims))
        self.assertEqual(0, len(claimed_claims))
        self.assertEqual(0, len(conflict_claims))
        self.assertEqual('approved', self.radb.getTask(task_id)['status'])


    def test_task_and_claim_with_zero_duration(self):
        """claims which claim a resource and release it at the same moment are now allowed (it's a paradox).
        """
        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        now = datetime.utcnow()

        spec_task = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                         now, now,  # tasks can have zero duration
                                                         'foo', 'CEP4')

        task_id = spec_task['task_id']
        task = self.radb.getTask(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(now, task['starttime'])
        self.assertEqual(now, task['endtime'])

        with mock.patch('lofar.common.postgres.logger') as mocked_logger:
            RESOURCE_ID = 252
            with self.assertRaises(PostgresDBQueryExecutionError):
                self.radb.insertResourceClaim(RESOURCE_ID, task_id,
                                              now, now,  # claims cannot have zero duration, test that!
                                              1, 'foo', 1)

            # test if there was a log line containing the database log message for 'claim starttime >= endtime'
            self.assertTrue(len([ca for ca in mocked_logger.error.call_args_list if 'claim starttime >= endtime' in ca[0][0]]) > 0)

        with mock.patch('lofar.common.postgres.logger') as mocked_logger:
            # try again, with multi-claim insert
            with self.assertRaises(PostgresDBQueryExecutionError):
                self.radb.insertResourceClaims(task_id, [{'resource_id': RESOURCE_ID,
                                                          'starttime': now,
                                                          'endtime': now,
                                                          'status': 'tentative',
                                                          'claim_size': 1}],
                                                          'foo', 1)

            # test if there was a log line containing the database log message for 'claim starttime >= endtime'
            self.assertTrue(len([ca for ca in mocked_logger.error.call_args_list if 'claim starttime >= endtime' in ca[0][0]]) > 0)

    def test_are_claims_in_conflict_released_by_removing_conflict_causing_claims(self):
        """test whether a claim which is in conflict is put automatically to tentative when the conflict-causing claim is released.
        """
        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        base_time = datetime.utcnow()
        # round to current full hour (for readability in logging)
        base_time = base_time - timedelta(minutes=base_time.minute, seconds=base_time.second,
                                          microseconds=base_time.microsecond)

        RESOURCE_ID = 252
        resource_max_cap = self.radb.get_resource_claimable_capacity(RESOURCE_ID, base_time, base_time)

        # insert a first task and full claim on a resource...
        spec_task1 = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                          base_time + timedelta(minutes=+0),
                                                          base_time + timedelta(minutes=+10), 'foo', 'CEP4')
        self.assertTrue(spec_task1['inserted'])
        task1_id = spec_task1['task_id']
        task1 = self.radb.getTask(task1_id)
        self.assertEqual('approved', task1['status'])

        claim1_id = self.radb.insertResourceClaim(RESOURCE_ID, task1_id,
                                                  task1['starttime'], task1['endtime'],
                                                  resource_max_cap, 'foo', 1)
        # claim it, and check it. Should succeed.
        self.radb.updateResourceClaim(claim1_id, status='claimed')
        self.assertEqual('claimed', self.radb.getResourceClaim(claim1_id)['status'])

        # insert second (partially overlapping) task and claim on same resource, which we expect to get a conflict status
        # because the first claim already claims the resource fully.
        spec_task2 = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation',
                                                          base_time + timedelta(minutes=+5),
                                                          base_time + timedelta(minutes=+15), 'foo', 'CEP4')
        self.assertTrue(spec_task2['inserted'])
        task2_id = spec_task2['task_id']
        task2 = self.radb.getTask(task2_id)
        self.assertEqual('approved', task2['status'])

        claim2_id = self.radb.insertResourceClaim(RESOURCE_ID, task2_id,
                                                  task2['starttime'], task2['endtime'],
                                                  resource_max_cap, 'foo', 1)
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

        # now let's see if releasing claim1 results in claim2 not having conflict state anymore
        self.radb.updateResourceClaim(claim1_id, status='tentative')
        self.assertEqual('tentative', self.radb.getResourceClaim(claim1_id)['status'])
        self.assertEqual('tentative', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task1_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

        # claim claim1 again, and check it. Should succeed.
        # and claim2 should go to conflict again.
        self.radb.updateResourceClaim(claim1_id, status='claimed')
        self.assertEqual('claimed', self.radb.getResourceClaim(claim1_id)['status'])
        self.assertEqual('conflict', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task1_id)['status'])
        self.assertEqual('conflict', self.radb.getTask(task2_id)['status'])

        # this time, resolve the conflict by shifting the endtime of claim1
        self.radb.updateResourceClaim(claim1_id, endtime=task2['starttime'])
        self.assertEqual('claimed', self.radb.getResourceClaim(claim1_id)['status'])
        self.assertEqual('tentative', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task1_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

        # and finally, we should be able to claim claim2 as well
        self.radb.updateResourceClaim(claim2_id, status='claimed')
        self.assertEqual('claimed', self.radb.getResourceClaim(claim1_id)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task1_id)['status'])
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

    def test_obsolete_claims_are_removed(self):
        '''Test if obsolete claims from finished tasks are removed automatically'''
        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        base_time = datetime.utcnow()
        # round to current full hour (for readability in logging)
        base_time = base_time - timedelta(minutes=base_time.minute, seconds=base_time.second,
                                          microseconds=base_time.microsecond)

        # insert a first task and full claim on a resource...
        spec_task = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'observation',
                                                          base_time + timedelta(minutes=-20),
                                                          base_time + timedelta(minutes=-10), 'foo', 'CEP4')
        self.assertTrue(spec_task['inserted'])
        task_id = spec_task['task_id']
        task = self.radb.getTask(task_id)
        self.assertEqual('approved', task['status'])

        claim1_id = self.radb.insertResourceClaim(0, task_id,
                                                  task['starttime'], task['endtime'],
                                                  1, 'foo', 1)

        # insert second (long-lasting) claim
        claim2_id = self.radb.insertResourceClaim(1, task_id,
                                                  task['starttime'], task['endtime'] + timedelta(days=100),
                                                  1, 'foo', 1)

        # task should have the two inserted claims
        self.assertEqual(set([claim1_id, claim2_id]), set(c['id'] for c in self.radb.getResourceClaims(task_ids=task_id)))

        # claim them, and check it. Should succeed.
        self.radb.updateTaskAndResourceClaims(task_id, task_status='prescheduled', claim_status='claimed')
        self.radb.updateTaskAndResourceClaims(task_id, task_status='scheduled')
        self.assertEqual('claimed', self.radb.getResourceClaim(claim1_id)['status'])
        self.assertEqual('claimed', self.radb.getResourceClaim(claim2_id)['status'])
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])
        # task should still have the two inserted claims
        self.assertEqual(set([claim1_id, claim2_id]), set(c['id'] for c in self.radb.getResourceClaims(task_ids=task_id)))

        # now, let's do the actual test...
        # finish the task, and check if claims are removed
        self.radb.updateTask(task_id, task_status='finished')
        self.assertEqual('finished', self.radb.getTask(task_id)['status'])
        # only the long lasting claim2 should remain
        self.assertEqual(set([claim2_id]), set(c['id'] for c in self.radb.getResourceClaims(task_ids=task_id)))

        # end the long-lasting claim
        self.radb.updateResourceClaim(claim2_id, endtime=task['endtime'] + timedelta(minutes=5))
        # task should still be finished...
        self.radb.updateTask(task_id, task_status='finished')
        # ...and now claims should remain
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id)))

    def test_20181108_bugfix_resource_usages(self):
        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour
        now += timedelta(hours=3)

        NUM_CLAIMS = 2
        NUM_CLAIMS_PER_RESOURCE = 2
        RESOURCE_ID = 0
        resource_max_cap = int(self.radb.get_resource_claimable_capacity(RESOURCE_ID, now, now))

        task1_id = self.radb.insertOrUpdateSpecificationAndTask(1, 1, 'approved', 'observation',
                                                        now+timedelta(hours=1),
                                                        now + timedelta(hours=2),
                                                        'content', 'CEP4')['task_id']
        task1 = self.radb.getTask(task1_id)

        claims1 = [{'resource_id': RESOURCE_ID,
                    'starttime': task1['starttime'],
                    'endtime': task1['endtime'],
                    'status': 'tentative',
                    'claim_size': resource_max_cap/NUM_CLAIMS_PER_RESOURCE}
                   for _ in range(NUM_CLAIMS)]

        self.radb.insertResourceClaims(task1_id, claims1, 'foo', 1, 1)

        # there should be NUM_CLAIMS tentative claims,
        # and usage should be one 'block' from start->endtime
        self.assertEqual(NUM_CLAIMS, len(self.radb.getResourceClaims(task_ids=task1_id, status='tentative')))
        self.assertEqual([{'as_of_timestamp': task1['starttime'], 'usage': resource_max_cap },
                          {'as_of_timestamp': task1['endtime'], 'usage': 0}],
                         self.radb.getResourceUsages(task1['starttime'], task1['endtime'], RESOURCE_ID)[RESOURCE_ID]['tentative'])

        # update the claims to 'claimed' status
        self.radb.updateResourceClaims(where_task_ids=task1_id, status='claimed')

        # now, there should be zero tentative claims, but NUM_CLAIMS 'claimed' claims
        # and usage should be one 'block' from start->endtime for claimed status
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task1_id, status='tentative')))
        self.assertEqual(NUM_CLAIMS, len(self.radb.getResourceClaims(task_ids=task1_id, status='claimed')))
        # self.assertEqual([],
        #                  self.radb.getResourceUsages(task1['starttime'], task1['endtime'], RESOURCE_ID)[RESOURCE_ID]['tentative'])
        self.assertEqual([{'as_of_timestamp': task1['starttime'], 'usage': resource_max_cap },
                          {'as_of_timestamp': task1['endtime'], 'usage': 0}],
                         self.radb.getResourceUsages(task1['starttime'], task1['endtime'], RESOURCE_ID)[RESOURCE_ID]['claimed'])

        # finish the task...
        self.radb.updateTask(task_id=task1_id, task_status='finished')

        # ... as a result there should be no more claims, and usages should be clean
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task1_id)))
        self.assertEqual([],
                         self.radb.getResourceUsages(task1['starttime'], task1['endtime'], RESOURCE_ID)[RESOURCE_ID]['tentative'])
        self.assertEqual([],
                         self.radb.getResourceUsages(task1['starttime'], task1['endtime'], RESOURCE_ID)[RESOURCE_ID]['claimed'])

        # insert second task after the first one (not overlapping)
        task2_id = self.radb.insertOrUpdateSpecificationAndTask(2, 2, 'approved', 'observation',
                                                        now + timedelta(hours=3),
                                                        now + timedelta(hours=4),
                                                        'content', 'CEP4')['task_id']
        task2 = self.radb.getTask(task2_id)

        # and insert claims for the second task
        claims2 = [{'resource_id': RESOURCE_ID,
                    'starttime': task2['starttime'],
                    'endtime': task2['endtime'],
                    'status': 'tentative',
                    'claim_size': resource_max_cap / NUM_CLAIMS_PER_RESOURCE}
                   for _ in range(NUM_CLAIMS)]

        self.radb.insertResourceClaims(task2_id, claims2, 'foo', 1, 1)

        # there should be NUM_CLAIMS tentative claims,
        # and usage should be one 'block' from start->endtime
        self.assertEqual(NUM_CLAIMS, len(self.radb.getResourceClaims(task_ids=task2_id, status='tentative')))
        self.assertEqual([{'as_of_timestamp': task2['starttime'], 'usage': resource_max_cap },
                          {'as_of_timestamp': task2['endtime'], 'usage': 0}],
                         self.radb.getResourceUsages(task2['starttime'], task2['endtime'], RESOURCE_ID)[RESOURCE_ID]['tentative'])

        # update the claims to 'claimed' status
        self.radb.updateResourceClaims(where_task_ids=task2_id, status='claimed')

        # now, there should be zero tentative claims, but NUM_CLAIMS 'claimed' claims
        # and usage should be one 'block' from start->endtime for claimed status
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task2_id, status='tentative')))
        self.assertEqual(NUM_CLAIMS, len(self.radb.getResourceClaims(task_ids=task2_id, status='claimed')))
        # self.assertEqual([],
        #                  self.radb.getResourceUsages(task2['starttime'], task2['endtime'], RESOURCE_ID)[RESOURCE_ID]['tentative'])
        self.assertEqual([{'as_of_timestamp': task2['starttime'], 'usage': resource_max_cap },
                          {'as_of_timestamp': task2['endtime'], 'usage': 0}],
                         self.radb.getResourceUsages(task2['starttime'], task2['endtime'], RESOURCE_ID)[RESOURCE_ID]['claimed'])


    def test_20190814_bugfix_SW_786(self):
        '''
        See: https://support.astron.nl/jira/browse/SW-786
        '''

        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        # ---------------------------------------------------------------------------
        # setup-phase: insert two tasks in the database, each with one tentative claim.
        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour
        for i in [1,2]:
            task_id = self.radb.insertOrUpdateSpecificationAndTask(i, i, 'approved', 'observation',
                                                                   now+timedelta(hours=1), now + timedelta(hours=2),
                                                                   'content', 'CEP4')['task_id']
            task = self.radb.getTask(task_id)

            claim = {'resource_id': 0,
                     'starttime': task['starttime'],
                     'endtime': task['endtime'],
                     'status': 'tentative',
                     'claim_size': 1}

            self.radb.insertResourceClaims(task_id, [claim], 'foo', 1, 1)

        tasks = self.radb.getTasks()
        task1_id = tasks[0]['id']
        task2_id = tasks[1]['id']

        # end setup-phase
        # ---------------------------------------------------------------------------

        # The actual test below has two concurrent processes which both modify the claims and/or task status/stoptime/stoptime
        # This should of course be possible, but as we can see in https://support.astron.nl/jira/browse/SW-786 and
        # https://support.astron.nl/jira/browse/SW-426 there are concurrency issues.

        start_loop_time = datetime.utcnow()
        TIMEOUT=5
        event1 = Event()
        event2 = Event()

        def updateTask1StatusLoop():
            with RADatabase(dbcreds=self.radb.dbcreds) as radb1:
                while datetime.utcnow()-start_loop_time < timedelta(seconds=TIMEOUT):
                    for status in ['tentative', 'claimed']:
                        if not radb1.updateResourceClaims(where_task_ids=[task1_id], status=status):
                            logger.error("Detected concurrency issue in updateTask1StatusLoop")
                            event1.set()
                            return

                        if event2.is_set():
                            logger.error("exiting updateTask1StatusLoop because of concurrency issue in updateTask2StartStopTimesLoop")
                            return

        def updateTask2StartStopTimesLoop():
            with RADatabase(dbcreds=self.radb.dbcreds) as radb2:
                while datetime.utcnow()-start_loop_time < timedelta(seconds=TIMEOUT):
                    task2 = radb2.getTask(task2_id)
                    if not radb2.updateTaskAndResourceClaims(task2_id,
                                                             starttime=task2['starttime']+timedelta(seconds=1),
                                                             endtime=task2['endtime']+timedelta(seconds=1)):
                        logger.error("Detected concurrency issue in updateTask2StartStopTimesLoop")
                        event2.set()
                        return

                    if event1.is_set():
                        logger.error("exiting updateTask2StartStopTimesLoop because of concurrency issue in updateTask1StatusLoop")
                        return

        # use multiprocessing.Process instead of threading.Thread for real concurrency
        p1 = Process(target=updateTask1StatusLoop, daemon=True)
        p2 = Process(target=updateTask2StartStopTimesLoop, daemon=True)
        p1.start()
        p2.start()
        p1.join(timeout=TIMEOUT)
        p2.join(timeout=TIMEOUT)

        self.assertFalse(event1.is_set() or event2.is_set(), "detected concurrency issues")

    def test_20190927_bugfix_SW_801(self):
        '''
        See: https://support.astron.nl/jira/browse/SW-801
        '''

        # start with clean database
        for spec in self.radb.getSpecifications():
            self.radb.deleteSpecification(spec['id'])  # cascades into tasks and claims

        # make sure the resource_usage is empty
        self.assertEqual(0, self.radb.executeQuery("SELECT COUNT(*) from resource_allocation.resource_usage;", fetch=FETCH_ONE)['count'])

        # we need a task....
        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour
        task_id = self.radb.insertOrUpdateSpecificationAndTask(0, 0, 'approved', 'reservation',
                                               now + timedelta(hours=1), now + timedelta(hours=2),
                                               'content', 'CEP4')['task_id']

        # check the task, should just be ok / as expected
        task = self.radb.getTask(task_id)
        self.assertIsNotNone(task)

        # ...and we need a claim....
        claim = {'resource_id': 0,
                 'starttime': task['starttime'],
                 'endtime': task['endtime'],
                 'status': 'tentative',
                 'claim_size': 1}
        self.radb.insertResourceClaims(task_id, [claim], 'foo', 1, 1)

        # check the claim, should just be ok / as expected
        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertIsNotNone(claims)
        self.assertEqual(1, len(claims))

        # check the usages, should just be ok / as expected
        usages = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage order by as_of_timestamp;", fetch=FETCH_ALL)
        self.assertEqual(2, len(usages))
        self.assertEqual(1, usages[0]['usage'])
        self.assertEqual(task['starttime'], usages[0]['as_of_timestamp'])
        self.assertEqual(task['endtime'], usages[1]['as_of_timestamp'])

        # "update" the claim start-/endtime to the same start-/endtime
        # this should not change anything, but the bug in SW-801 is that the usages get lost....
        self.radb.updateResourceClaims([c['id'] for c in claims], starttime=task['starttime'], endtime=task['endtime'])

        # check the usages again, they should be the same as above, but for bug SW-801 they are lost.
        usages = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage order by as_of_timestamp;", fetch=FETCH_ALL)
        self.assertEqual(2, len(usages))
        self.assertEqual(1, usages[0]['usage'])
        self.assertEqual(task['starttime'], usages[0]['as_of_timestamp'])
        self.assertEqual(task['endtime'], usages[1]['as_of_timestamp'])

    def test_resource_claimable_capacities(self):
        '''Test the get_resource_claimable_capacity and get_resource_claimable_capacities methods
        and compare the results against the expected total_capacity'''
        resources = self.radb.getResources(include_availability=True)
        resource_ids = [r['id'] for r in resources]
        now = datetime.utcnow()
        capacities = self.radb.get_resource_claimable_capacities(resource_ids, now, now)

        for resource_id in resource_ids:
            self.assertEqual(capacities[resource_id], self.radb.get_resource_claimable_capacity(resource_id, now, now))

        for resource_id, resource in zip(resource_ids, resources):
            self.assertEqual(capacities[resource_id], resource['total_capacity'])

        resources_with_claimable_capacities = self.radb.getResources(claimable_capacity_lower_bound=now, claimable_capacity_upper_bound=now)
        for resource_id, resource_with_claimable_capacity in zip(resource_ids, resources_with_claimable_capacities):
            self.assertEqual(capacities[resource_id], resource_with_claimable_capacity['claimable_capacity'])


    def test_bugfix_SW_833_removed_finished_claimes_and_usages(self):
        '''
        See: https://support.astron.nl/jira/browse/SW-833
        '''
        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond) # round to full hour

        # we should start with a clean usage table
        usages = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage;", fetch=FETCH_ALL)
        usage_deltas = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage_delta;", fetch=FETCH_ALL)
        self.assertEqual(0, len(usages))
        self.assertEqual(0, len(usage_deltas))

        task_id = self.radb.insertOrUpdateSpecificationAndTask(mom_id=0, otdb_id=0, task_status='approved', task_type='observation',
                                                               starttime=now+timedelta(hours=1), endtime=now+timedelta(hours=2),
                                                               content="", cluster="CEP4")['task_id']
        task = self.radb.getTask(task_id)
        self.radb.insertResourceClaim(resource_id=117, task_id=task_id,
                                      starttime=task['starttime'], endtime=task['endtime'], claim_size=100,
                                      username="", user_id=0)
        self.radb.insertResourceClaim(resource_id=118, task_id=task_id,
                                      starttime=task['starttime'], endtime=task['endtime']+timedelta(days=1), claim_size=100,
                                      username="", user_id=0)

        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertEqual(2, len(claims))
        for claim in claims:
            self.assertEqual('tentative', claim['status'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'] - timedelta(minutes=10), claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'], claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] - timedelta(seconds=1), claim['status'])['usage'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] + timedelta(minutes=10), claim['status'])['usage'])

        # resource usages tables should be filled
        usages = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage;", fetch=FETCH_ALL)
        usage_deltas = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage_delta;", fetch=FETCH_ALL)
        self.assertGreater(len(usages), 0)
        self.assertGreater(len(usage_deltas), 0)

        self.radb.updateTaskAndResourceClaims(task_id, claim_status='claimed', task_status='prescheduled')
        self.radb.updateTaskAndResourceClaims(task_id, task_status='scheduled')

        # check claims
        # should be claimed and 'using' the resources in the claim's time windows
        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertEqual(2, len(claims))
        for claim in claims:
            self.assertEqual('claimed', claim['status'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'] - timedelta(minutes=10), claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'], claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] - timedelta(seconds=1), claim['status'])['usage'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] + timedelta(minutes=10), claim['status'])['usage'])

        usages = self.radb.getResourceUsages()

        # let the task 'run'...
        self.radb.updateTaskAndResourceClaims(task_id, task_status='queued')
        self.radb.updateTaskAndResourceClaims(task_id, task_status='active')
        self.radb.updateTaskAndResourceClaims(task_id, task_status='completing')

        # check claims
        # should still be claimed and 'using' the resources
        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertEqual(2, len(claims))
        for claim in claims:
            self.assertEqual('claimed', claim['status'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'] - timedelta(minutes=10), claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'], claim['status'])['usage'])
            self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] - timedelta(seconds=1), claim['status'])['usage'])
            self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] + timedelta(minutes=10), claim['status'])['usage'])

        # allow the task to finish...
        # this should result in a trigger removing finished claims as well
        self.radb.updateTaskAndResourceClaims(task_id, task_status='finished')

        # check claims
        # one claim should be gone, the other ends in the future and should still be there
        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertEqual(1, len(claims))
        claim = claims[0]
        self.assertEqual('claimed', claim['status'])
        self.assertGreater(claim['endtime'], task['endtime'])
        self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'] - timedelta(minutes=10), claim['status'])['usage'])
        self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['starttime'], claim['status'])['usage'])
        self.assertEqual(100, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] - timedelta(seconds=1), claim['status'])['usage'])
        self.assertEqual(0, self.radb.get_resource_usage_at_or_before(claim['resource_id'], claim['endtime'] + timedelta(minutes=10), claim['status'])['usage'])

        # later, after data was ingested and cleaned-up, the storage-claim is deleted
        # this should result in a trigger removing the resource_usages as well
        self.radb.deleteResourceClaim(claim['id'])

        claims = self.radb.getResourceClaims(task_ids=task_id)
        self.assertEqual(0, len(claims))

        # in the end we should have a clean usage table again
        usages = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage;", fetch=FETCH_ALL)
        usage_deltas = self.radb.executeQuery("SELECT * from resource_allocation.resource_usage_delta;", fetch=FETCH_ALL)
        self.assertEqual(0, len(usages))
        self.assertEqual(0, len(usage_deltas))

os.environ['TZ'] = 'UTC'
logging.basicConfig(format='%(asctime)s %(levelname)s %(process)s %(threadName)s %(message)s', level=logging.DEBUG)

if __name__ == "__main__":
    unittest.main()
