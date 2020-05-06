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
import sys

from lofar.sas.resourceassignment.resourceassigner.resource_availability_checker import ResourceAvailabilityChecker, CouldNotFindClaimException

from lofar.sas.resourceassignment.resourceassigner.schedulers import ScheduleException
from lofar.sas.resourceassignment.resourceassigner.schedulers import BasicScheduler
from lofar.sas.resourceassignment.resourceassigner.schedulers import StationScheduler
from lofar.sas.resourceassignment.resourceassigner.schedulers import PriorityScheduler
from lofar.sas.resourceassignment.resourceassigner.schedulers import DwellScheduler

from lofar.sas.resourceassignment.database.radb import FETCH_ONE

import logging
logger = logging.getLogger(__name__)

from lofar.sas.resourceassignment.database.testing.radb_common_testing import RADBCommonTestMixin

class SchedulerTest(RADBCommonTestMixin, unittest.TestCase):
    """ create test radb postgres instance, and use that in a ResourceAvailabilityChecker"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._enforce_limited_station_group_list()

    @classmethod
    def _enforce_limited_station_group_list(cls):
        # for test simplicity, create a simple virtual instrument which makes debugging easier.
        # this is safe, because we are working on a test database

        LIMITED_STATION_GROUP_LIST = ('CS001', 'CS002', 'RS106', 'RS205')

        unwanted_resource_group_ids = [rg['id'] for rg in cls.radb.getResourceGroups()
                                       if rg['type'] == 'station' and rg['name'] not in LIMITED_STATION_GROUP_LIST]

        if unwanted_resource_group_ids:
            cls.radb.executeQuery("DELETE FROM virtual_instrument.resource_group rg WHERE rg.id in (%s)" % (
                                    ', '.join([str(id) for id in unwanted_resource_group_ids])),)
            cls.radb.commit()

    def setUp(self):
        super().setUp()
        self.resource_availability_checker = ResourceAvailabilityChecker(self.radb)

class BasicSchedulerTest(SchedulerTest):
    def new_task(self, mom_otdb_id=0, starttime=None, endtime=None):
        """
        insert a new test specification and task into the testing radb
        :param mom_otdb_id: optional mom/otdb id
        :param starttime: optional starttime if None, then datetime(2017, 1, 1, 1, 0, 0) is used
        :param endtime: optional endtime if None, then datetime(2017, 1, 1, 2, 0, 0) is used
        :return: the new radb's task id
        """

        if starttime is None:
            starttime = datetime.datetime(2017, 1, 1, 1, 0, 0)

        if endtime is None:
            endtime = datetime.datetime(2017, 1, 1, 2, 0, 0)

        return self.radb.insertOrUpdateSpecificationAndTask(mom_id=mom_otdb_id,
                                                    otdb_id=mom_otdb_id,
                                                    task_status='approved',
                                                    task_type='observation',
                                                    starttime=starttime,
                                                    endtime=endtime,
                                                    content='',
                                                    cluster='CEP4')['task_id']

    def get_specification_tree(self, task_id):
        return {}

    def new_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """factory method returning a scheduler class specific for this test class.
        In this case, in the BasicSchedulerTest class, it returns a new BasicScheduler."""
        return self.new_basic_scheduler(task_id, resource_estimator, specification_tree)

    def new_basic_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """return a new BasicScheduler"""
        return BasicScheduler(task_id,
                              specification_tree if specification_tree else self.get_specification_tree(task_id),
                              resource_estimator if resource_estimator else lambda _:[],
                              self.resource_availability_checker, self.radb)

    def get_station_bandwidth_max_capacity(self):
        resource_CS001bw0 = [r for r in self.radb.getResources(resource_types="bandwidth", include_availability=True)
                             if r['name']=='CS001bw0'][0]
        return resource_CS001bw0['total_capacity']

    def get_CEP4_storage_max_capacity(self):
        resource_cep4_storage = [r for r in self.radb.getResources(resource_types="storage", include_availability=True)
                             if r['name']=='CEP4_storage:/data'][0]
        return resource_cep4_storage['total_capacity']

    def test_schedule_task(self):
        """ Whether a task (that fits) can be scheduled. """

        # Resources we need
        task_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': 512},
                       "root_resource_group": "CS001",
                       "resource_count": 1 } ]
        scheduler = self.new_scheduler(task_id, lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must succeed and be committed
        self.assertTrue(allocation_successful)

        # Claim must be present in database
        claims = self.radb.getResourceClaims(task_ids=task_id, extended=True)
        self.assertTrue(claims)
        self.assertEqual(len(claims), 1)

        # Claim must be valid
        claim = claims[0]
        task = self.radb.getTask(task_id)

        self.assertEqual(claim["status"],             "claimed")
        self.assertEqual(claim["starttime"],          task["starttime"])
        self.assertEqual(claim["endtime"],            task["endtime"])
        self.assertEqual(claim["claim_size"],         512)
        self.assertEqual(claim["resource_type_name"], "bandwidth")

    def test_multiple_resources(self):
        """ Whether a task (that fits) can be scheduled. """

        # Resources we need
        task_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': 512},
                       "root_resource_group": "CS001",
                       "resource_count": 1 },
                     {'resource_types': {'bandwidth': 512},
                      "root_resource_group": "CS002",
                      "resource_count": 1} ]

        scheduler = self.new_scheduler(task_id, lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must succeed
        self.assertTrue(allocation_successful)

        # Claim must be present in database
        claims = self.radb.getResourceClaims(task_ids=task_id, extended=True)
        self.assertTrue(claims)
        self.assertEqual(len(claims), 2)

    def test_schedule_too_large_task(self):
        """ Whether a task with too large claims will be rejected by the scheduler. """

        # Resources we need
        task_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': 1e99},
                       "root_resource_group": "CS001",
                       "resource_count": 1 } ]
        scheduler = self.new_scheduler(task_id, lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        if self.__class__ == BasicSchedulerTest: # This inheritence of test is not ideal
            # Allocation must fail, and commit called so we get a conflicted state
            self.assertFalse(allocation_successful)
        else:
            # Allocation must fail, and rollback called
            self.assertFalse(allocation_successful)

    def test_schedule_two_tasks_too_large_task(self):
        """ Whether two tasks that fit individually but not together will be rejected by the scheduler. """

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        # we claim two bandwidth resources because CS001 has two network lines
        # they should both be claimed, so that the next task cannot just take the other free line.
        task_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 1 },
                     {'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1} ]
        scheduler = self.new_scheduler(task_id, lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Second task must fail, because both network lines were already filled.
        task2_id = self.new_task(1)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 1 },
                     {'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1} ]
        scheduler = self.new_scheduler(task2_id, lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertFalse(allocation_successful)



class StationSchedulerTest(BasicSchedulerTest):
    # The StationScheduler must not regress on the BasicScheduler, so we inherit all its tests

    def get_specification_tree(self, task_id):
        return { "task_type": "observation",
                 "specification": { "Observation.VirtualInstrument.stationList": [] },
                 "station_requirements": [] }

    def new_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the StationSchedulerTest class, it returns a new StationScheduler.

        Please note that in most/all of the tests in this StationSchedulerTest test class
        we explicitly use the new_station_scheduler factory method to get the specific
        StationScheduler. In derived test classes, this means that we then still use a StationScheduler
        and not another scheduler type via a overridden new_scheduler method.
        """
        return self.new_station_scheduler(task_id, resource_estimator, specification_tree)

    def new_station_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """factory method returning a StationScheduler.
        Can be overridden in derived test classes."""
        return StationScheduler(task_id,
                                specification_tree if specification_tree else self.get_specification_tree(task_id),
                                resource_estimator if resource_estimator else self.fake_resource_estimator,
                                self.resource_availability_checker, self.radb)

    def fake_resource_estimator(self, specification_tree):
        """ Return an estimate for each station, plus a fixed storage claim of half the available storage capacity. """

        stations = specification_tree["specification"]["Observation.VirtualInstrument.stationList"]

        # We don't get here without requesting stations
        assert stations

        max_bw_cap = self.get_station_bandwidth_max_capacity()
        max_storage_cap = self.get_CEP4_storage_max_capacity()

        return [
          { "resource_types": {"bandwidth": max_bw_cap },
            "resource_count": 1,
            "station": station_name,
            "root_resource_group": station_name
          } for station_name in stations
        ] + [
          { "resource_types": {"storage": 0.4*max_storage_cap},
            "resource_count": 1,
            "root_resource_group": "CEP4"
            }
        ]

    def test_expand_station_list(self):
        """ Test whether _expand_station_list correctly expands the station sets we defined in our FakeRADatabase. """

        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=self.get_specification_tree(0))

        self.assertEqual(sorted(scheduler._expand_station_list("ALL")),    ["CS001","CS002","RS106","RS205"])
        self.assertEqual(sorted(scheduler._expand_station_list("CORE")),   ["CS001","CS002"])
        self.assertEqual(sorted(scheduler._expand_station_list("REMOTE")), ["RS106","RS205"])
        self.assertEqual(sorted(scheduler._expand_station_list("CS002")),  ["CS002"])

        with self.assertRaises(ScheduleException):
            scheduler._expand_station_list("UNKNOWN")

    def test_requirements_satisfied_without(self):
        """ Test whether _requirements_satisfied_without functions correctly. """

        func = StationScheduler._requirements_satisfied_without

        self.assertTrue (func([],[]))
        self.assertTrue (func([(["CS001","CS002"],1)],[]))
        self.assertTrue (func([(["CS001","CS002"],1)],["CS001"]))
        self.assertFalse(func([(["CS001","CS002"],1)],["CS001","CS002"]))
        self.assertFalse(func([(["CS001","CS002"],2)],["CS001"]))
        self.assertFalse(func([(["CS001","CS002"],2)],["CS002"]))
        self.assertFalse(func([(["CS001","CS002"],3)],[]))

    def test_find_one_station(self):
        """ Test whether a requirement for a single station can be satisfied. """

        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("RS106", 1), ]

        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must succeed
        self.assertTrue(allocation_successful)

        # The specified station must be allocated, plus storage claim
        self.assertTrue(len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')) == 2)

    def test_find_any_station(self):
        """ Test whether a requirement for a single station can be satisfied. """

        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("ALL", 1), ]

        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must succeed
        self.assertTrue(allocation_successful)

        # All 4 stations must be allocated (allocation is greedy), plus storage claim
        self.assertTrue(len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')) == 5)

    def test_find_zero_stations(self):
        """ Test whether a requirement for a zero station cannot be satisfied if no stations are left. """

        # preparation: do a first scheduling, which should succeed and claim the station
        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("RS106", 1), ]
        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        self.assertTrue(allocation_successful)
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))

        # real test, try to claim same station again. Should fail now.
        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("RS106", 0), ]

        task_id = self.new_task(1)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must fail
        self.assertFalse(allocation_successful)
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))


    def test_find_overlap_stations(self):
        """ Test whether requirements for overlapping station sets can be satisfied. """

        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("CORE", 2), ("ALL", 4), ]

        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must succeed
        self.assertTrue(allocation_successful)

        # All 4 stations must be allocated (allocation is greedy), plus storage claim
        self.assertTrue(len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')) == 5)

    def test_require_too_many_stations(self):
        """ Test whether requiring too many stations (than exist) fails. """

        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("CORE", 3), ]

        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        # Allocation must fail
        self.assertFalse(allocation_successful)

    def test_require_more_stations_than_available(self):
        """ Test whether requiring too many stations (than are available) fails. """

        specification_tree = self.get_specification_tree(0)
        specification_tree["station_requirements"] = [ ("REMOTE", 2), ]

        # preparation: do a first scheduling, which should succeed and claim the two remote stations
        task_id = self.new_task(0)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        self.assertTrue(allocation_successful)
        self.assertEqual(3, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))

        # real test, try to claim the two remote stations again. Should fail now.
        task_id = self.new_task(1)
        scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()

        self.assertFalse(allocation_successful)
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))


    def test_2obs_coexist(self):
        """ Test whether 2 obs requiring different station sets can be scheduled in parallel. """

        for mom_id in (0,1):
          station_set = "CORE" if mom_id == 0 else "REMOTE"
          specification_tree = self.get_specification_tree(mom_id)
          specification_tree["station_requirements"] = [ (station_set, 2), ]

          task_id = self.new_task(mom_id)
          scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
          (allocation_successful, changed_tasks) = scheduler.allocate_resources()

          # Allocation must succeed
          self.assertTrue(allocation_successful)
          self.assertTrue(len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')) == 3) # 2 stations + 1 storage claim

    def test_2obs_no_fit(self):
        """ Test whether 2 obs requiring station sets from the same set will conflict. """

        allocation_successful = {}
        # Two observations both requesting 2 core stations
        for mom_id in (0,1):
          specification_tree = self.get_specification_tree(mom_id)
          specification_tree["station_requirements"] = [ ("REMOTE", 2), ]

          task_id = self.new_task(mom_id)
          scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
          (allocation_successful[mom_id], changed_tasks) = scheduler.allocate_resources()

        # Second allocation must fail
        self.assertTrue(allocation_successful[0])
        self.assertFalse(allocation_successful[1])

    def test_3obs_no_fit_storage(self):
        """ Test whether 3 obs requiring different stations but together too much storage fit. """

        allocation_successful = {}
        # Two observations both requesting 2 core stations
        for mom_id in (0,1,2):
          station_name = { 0: "CS001", 1: "CS002", 2: "RS106" }[mom_id]
          specification_tree = self.get_specification_tree(mom_id)
          specification_tree["station_requirements"] = [ (station_name, 1), ]

          task_id = self.new_task(mom_id)
          scheduler = self.new_station_scheduler(task_id, specification_tree=specification_tree)
          (allocation_successful[mom_id], changed_tasks) = scheduler.allocate_resources()

        # Second allocation must fail
        self.assertTrue(allocation_successful[0])
        self.assertTrue(allocation_successful[1])
        self.assertFalse(allocation_successful[2])

class PrioritySchedulerTest(StationSchedulerTest):
    # The PriorityScheduler must not regress on the StationScheduler, so we inherit all its tests

    def mock_momrpc(self):
        def momrpc_mock_get_project_priorities_for_objects(mom_ids):
            # priority increments by 1000 ids
            return {mom_id: mom_id // 1000 for mom_id in mom_ids}

        momrpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.schedulers.MoMQueryRPC')
        self.addCleanup(momrpc_patcher.stop)
        self.momrpc_mock = momrpc_patcher.start()
        self.momrpc_mock.create.side_effect = lambda **kwargs: self.momrpc_mock
        self.momrpc_mock.get_project_priorities_for_objects.side_effect = momrpc_mock_get_project_priorities_for_objects

    def mock_datetime(self):
        datetime_patcher = mock.patch('lofar.sas.resourceassignment.resourceassigner.schedulers.datetime')
        self.addCleanup(datetime_patcher.stop)
        self.datetime_mock = datetime_patcher.start()

        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)
        self.datetime_mock.max = datetime.datetime.max

    def setUp(self):
        super(PrioritySchedulerTest, self).setUp()

        self.mock_momrpc()
        self.mock_datetime()

    def new_task_without_momid(self, otdb_id):
        return self.radb.insertOrUpdateSpecificationAndTask(mom_id=None,
                                                    otdb_id=otdb_id,
                                                    task_status='approved',
                                                    task_type='observation',
                                                    starttime=datetime.datetime(2017, 1, 1, 1, 0, 0),
                                                    endtime=datetime.datetime(2017, 1, 1, 2, 0, 0),
                                                    content='',
                                                    cluster='CEP4')['task_id']

    def new_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the PrioritySchedulerTest class, it returns a new PriorityScheduler."""
        return self.new_priority_scheduler(task_id, resource_estimator, specification_tree)

    def new_station_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the PrioritySchedulerTest class, it returns a new PriorityScheduler."""
        return self.new_priority_scheduler(task_id, resource_estimator, specification_tree)

    def new_priority_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        return PriorityScheduler(task_id,
                                 specification_tree if specification_tree else self.get_specification_tree(task_id),
                                 resource_estimator if resource_estimator else self.fake_resource_estimator,
                                 self.resource_availability_checker, self.radb)

    def test_unschedule_lower_priority_future_task(self):
        """
        Whether two future tasks that fit individually but not together will be accepted by the scheduler by unscheduling the
        lower-priority task.
        """

        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed (for the test the mom_id determines the prio)
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='prescheduled')
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # Second task must succeed as it has a higher priority (for the test the mom_id determines the prio)
        task2_id = self.new_task(1000)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task2_id, status='claimed')))

        # First task must have been unscheduled
        # as a result, it should not have any claimed claims anymore
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task_id, status='conflict')))
        # and the low-prio task should now have conflict state (cause the high-prio task claimed the resources)
        self.assertEqual('conflict', self.radb.getTask(task_id)['status'])


    def test_kill_lower_priority_running_task(self):
        """
        Whether two tasks that fit individually but not together will be accepted by the scheduler by killing the
        running lower-priority task.
        """

        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        # (for the test the mom_id determines the prio)
        task_id = self.new_task(0, starttime=datetime.datetime(2017, 1, 1, 12, 0, 0),
                                     endtime=datetime.datetime(2017, 1, 1, 13, 0, 0))
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "RS106",
                      "resource_count": 1 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='prescheduled')
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])
        self.assertEqual(datetime.datetime(2017, 1, 1, 12, 0, 0), self.radb.getTask(task_id)['starttime'])
        self.assertEqual(datetime.datetime(2017, 1, 1, 13, 0, 0), self.radb.getTask(task_id)['endtime'])

        # shift utcnow and fake that the task is running
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 12, 10, 0)
        self.radb.updateTask(task_id, task_status='active')
        self.assertEqual('active', self.radb.getTask(task_id)['status'])

        # Second task must succeed as it has a higher priority
        # start it in a minute after now
        # (or else it will still have overlap and conflicts with beginning of just-aborted running task)
        # (for the test the mom_id determines the prio)
        task2_id = self.new_task(1000, starttime=datetime.datetime(2017, 1, 1, 12, 11, 0),
                                         endtime=datetime.datetime(2017, 1, 1, 13, 11, 0))
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "RS106",
                      "resource_count": 1 } ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # First task must have been killed
        self.assertTrue(len(changed_tasks) > 0)
        self.assertTrue(changed_tasks[0].radb_id == task_id)
        self.assertTrue(changed_tasks[0].status == "aborted")

        # First task must have its endtime cut short to utcnow
        # and all claims should have been deleted.
        self.assertEqual(datetime.datetime(2017, 1, 1, 12, 10, 0), self.radb.getTask(task_id)['endtime'])
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id)))

        # and the starttime should still be the original
        self.assertEqual(datetime.datetime(2017, 1, 1, 12, 0, 0), self.radb.getTask(task_id)['starttime'])
        # and status should be aborted
        self.assertEqual('aborted', self.radb.getTask(task_id)['status'])


    def test_do_not_unschedule_higher_priority_future_task(self):
        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed (for the test the mom_id determines the prio)
        task_id = self.new_task(1000)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='prescheduled')
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # Second task must succeed as it has a higher priority (for the test the mom_id determines the prio)
        task2_id = self.new_task(0) #(for the test the mom_id determines the prio)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertFalse(allocation_successful)

        # the second (low-prio) task could not be scheduled
        # as a result there are no claims allocated and the task stays in approved state.
        # Thought by JS: I think that's wrong, and does not give the proper feedback to the user.
        # I think that the claims and task should go to conflict to make it clear to the user what happened.
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task2_id)))

        # First task must NOT have been unscheduled
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))


    def test_do_not_kill_higher_priority_running_task(self):

        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First (task must succeed)
        task_id = self.new_task(1000) #(for the test the mom_id determines the prio)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='prescheduled')
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # shift utcnow and fake that the task is running
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 1, 10, 0)
        self.radb.updateTask(task_id, task_status='active')
        self.assertEqual('active', self.radb.getTask(task_id)['status'])

        # Second task must succeed as it has a higher priority
        # start it in a minute after now
        # (or else it will still have overlap and conflicts with beginning of just-aborted running task)
        # (for the test the mom_id determines the prio)
        task2_id = self.new_task(0, starttime=datetime.datetime(2017, 1, 1, 1, 11, 0))
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertFalse(allocation_successful)

        # the second (low-prio) task could not be scheduled
        # as a result there are no claims allocated and the task stays in approved state.
        # Thought by JS: I think that's wrong, and does not give the proper feedback to the user.
        # I think that the claims and task should go to conflict to make it clear to the user what happened.
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task2_id)))

        # First task must NOT have been killed
        self.assertEqual('active', self.radb.getTask(task_id)['status'])
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))

    def test_not_unschedule_equal_priority(self):
        """ Whether two tasks that fit individually but not together get rejected priorities do not allow an override. """

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        task1_id = self.new_task(1) #mom_id=1 and mom_id=0 yield equal priorities
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task1_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task1_id)['status'])
        self.radb.updateTask(task1_id, task_status='prescheduled')
        self.radb.updateTask(task1_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task1_id)['status'])

        # Second task must fail as it has a lower priority
        task2_id = self.new_task(0) #mom_id=1 and mom_id=0 yield equal priorities
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertFalse(allocation_successful)

        self.assertEqual('scheduled', self.radb.getTask(task1_id)['status'])
        # Thought by JS: I think it's wrong that task2 has approved status, and does not give the proper feedback to the user.
        # I think that the claims and task should go to conflict to make it clear to the user what happened.
        self.assertEqual('approved', self.radb.getTask(task2_id)['status'])

    def test_partial_conflict(self):
        """ Whether a task gets scheduled correctly if it has a partial conflict after the first fit. """


        # utcnow lies before the tasks we are scheduling (the tasks lie in the future)
        self.datetime_mock.utcnow.return_value = datetime.datetime(2017, 1, 1, 0, 0, 0)

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed (for the test the mom_id determines the prio)
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': 0.25*max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1 },
                     {'resource_types': {'bandwidth': 0.25 * max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1}
                     ]

        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        self.assertEqual('approved', self.radb.getTask(task_id)['status'])
        self.radb.updateTask(task_id, task_status='prescheduled')
        self.radb.updateTask(task_id, task_status='scheduled')
        self.assertEqual('scheduled', self.radb.getTask(task_id)['status'])

        # Second task must succeed as it has a higher priority (for the test the mom_id determines the prio)
        task2_id = self.new_task(1000)
        estimates = [{'resource_types': {'bandwidth': 0.25*max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1 },
                     {'resource_types': {'bandwidth': 0.95 * max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 1}
                     ]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task2_id, status='claimed')))

        # First task must have been unscheduled
        # as a result, it should not have any claimed claims anymore
        self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_id, status='tentative')))
        self.assertEqual(1, len(self.radb.getResourceClaims(task_ids=task_id, status='conflict')))
        # and the low-prio task should now have conflict state (cause the high-prio task claimed the resources)
        self.assertEqual('conflict', self.radb.getTask(task_id)['status'])

    def test_should_not_kill_a_task_without_a_mom_id(self):
        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        task_id = self.new_task_without_momid(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "RS106",
                      "resource_count": 1 }]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        task2_id = self.new_task(1000)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "RS106",
                      "resource_count": 1 }]
        scheduler = self.new_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertFalse(allocation_successful)
        self.assertTrue(len(changed_tasks) == 0)

    def test_open_should_call_open_on_momqueryrpc(self):
        max_bw_cap = self.get_station_bandwidth_max_capacity()
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        scheduler.open()

        self.assertTrue(self.momrpc_mock.open.called)

    def test_close_should_call_close_on_momqueryrpc(self):
        max_bw_cap = self.get_station_bandwidth_max_capacity()
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        scheduler = self.new_scheduler(task_id, resource_estimator=lambda _: estimates)
        scheduler.close()

        self.assertTrue(self.momrpc_mock.close.called)

    def test_context_manager_use_calls_open_on_momqueryrpc(self):
        max_bw_cap = self.get_station_bandwidth_max_capacity()
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        with self.new_scheduler(task_id, resource_estimator=lambda _: estimates) as scheduler:
            pass

        self.assertTrue(self.momrpc_mock.open.called)

    def test_context_manager_use_calls_close_on_momqueryrpc(self):
        max_bw_cap = self.get_station_bandwidth_max_capacity()
        task_id = self.new_task(0)
        estimates = [{'resource_types': {'bandwidth': max_bw_cap},
                      "root_resource_group": "CS001",
                      "resource_count": 2 } ]
        with self.new_scheduler(task_id, resource_estimator=lambda _: estimates) as scheduler:
            pass

        self.assertTrue(self.momrpc_mock.close.called)


class DwellSchedulerTest(PrioritySchedulerTest):
    # The DwellScheduler must not regress on the PriorityScheduler, so we inherit all its tests

    class TestResourceAvailabilityChecker(ResourceAvailabilityChecker):
        """Helper class to keep track of arguments in calls to get_is_claimable"""
        def get_is_claimable(self, requested_resources, available_resources):
            self.last_requested_resources = requested_resources
            self.last_available_resources = available_resources
            return super(DwellSchedulerTest.TestResourceAvailabilityChecker, self).get_is_claimable(requested_resources,
                                                                                                    available_resources)

    def setUp(self):
        super(DwellSchedulerTest, self).setUp()
        self.resource_availability_checker = DwellSchedulerTest.TestResourceAvailabilityChecker(self.radb)

    def new_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the DwellSchedulerTest class, it returns a new DwellScheduler."""
        return self.new_dwell_scheduler(task_id, resource_estimator, specification_tree, allow_dwelling=False)

    def new_station_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the DwellSchedulerTest class, it returns a new DwellScheduler."""
        return self.new_dwell_scheduler(task_id, resource_estimator, specification_tree, allow_dwelling=False)

    def new_priority_scheduler(self, task_id, resource_estimator=None, specification_tree=None):
        """overridden factory method returning a scheduler class specific for this test class.
        In this case, in the DwellSchedulerTest class, it returns a new DwellScheduler."""
        return self.new_dwell_scheduler(task_id, resource_estimator, specification_tree, allow_dwelling=False)

    def new_dwell_scheduler(self, task_id, resource_estimator=None, specification_tree=None, allow_dwelling=True):
        if allow_dwelling:
            min_starttime = datetime.datetime(2017, 1, 1, 1, 0, 0)
            max_starttime = datetime.datetime(2017, 1, 2, 1, 0, 0)
        else:
            # we do not want dwelling, so limit the dwell starttime window to the task's actual starttime.
            min_starttime = self.radb.getTask(task_id)['starttime']
            max_starttime = min_starttime

        return DwellScheduler(task_id,
                              specification_tree if specification_tree else self.get_specification_tree(task_id),
                              resource_estimator if resource_estimator else self.fake_resource_estimator,
                              min_starttime,
                              max_starttime,
                              datetime.timedelta(hours=1),            # duration
                              self.resource_availability_checker, self.radb)

    def test_no_dwell(self):
        """ Whether a task will not dwell unnecessarily on an empty system. """

        # Task must succeed
        task_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': 512},
                       "root_resource_group": "CS001",
                       "resource_count": 1 } ]
        scheduler = self.new_dwell_scheduler(task_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Task must be positioned at start of dwelling period.
        task = self.radb.getTask(task_id)
        self.assertEqual(scheduler.min_starttime, task["starttime"])
        self.assertEqual(scheduler.min_starttime+scheduler.duration, task["endtime"])

    def test_dwell(self):
        """ Whether a task will dwell after an existing task. """

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        task1_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        scheduler = self.new_dwell_scheduler(task1_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Second task must also succeed
        task2_id = self.new_task(1)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        scheduler = self.new_dwell_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Second task must have been moved, first task not
        self.assertEqual(self.radb.getTask(task1_id)["starttime"], datetime.datetime(2017, 1, 1, 1, 0, 0))
        self.assertEqual(self.radb.getTask(task1_id)["endtime"],   datetime.datetime(2017, 1, 1, 2, 0, 0))
        self.assertEqual(self.radb.getTask(task2_id)["starttime"], datetime.datetime(2017, 1, 1, 2, 1, 0))
        self.assertEqual(self.radb.getTask(task2_id)["endtime"],   datetime.datetime(2017, 1, 1, 3, 1, 0))

    def test_dwell_respect_claim_endtime(self):
        """ Whether a dwelling task will honour the claim endtimes, instead of the task endtime. """

        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        task1_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        # use normal basic scheduler for first normal task, which we want to schedule in a normal (non-dwell) way.
        scheduler = self.new_basic_scheduler(task1_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task1_id, status='claimed')))

        # Extend claim
        task = self.radb.getTask(task1_id)
        self.radb.updateResourceClaims(where_task_ids=task1_id, endtime=task["endtime"] + datetime.timedelta(hours=1))
        self.assertEqual(2, len(self.radb.getResourceClaims(task_ids=task1_id, status='claimed')))

        # Second task must also succeed
        task2_id = self.new_task(1)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        scheduler = self.new_dwell_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Second task must have been moved beyond 1st claim endtime, first task not
        self.assertEqual(self.radb.getTask(task1_id)["starttime"], datetime.datetime(2017, 1, 1, 1, 0, 0))
        self.assertEqual(self.radb.getTask(task1_id)["endtime"],   datetime.datetime(2017, 1, 1, 2, 0, 0))
        self.assertEqual(self.radb.getTask(task2_id)["starttime"], datetime.datetime(2017, 1, 1, 3, 1, 0))
        self.assertEqual(self.radb.getTask(task2_id)["endtime"],   datetime.datetime(2017, 1, 1, 4, 1, 0))

    def test_dwellScheduler_should_give_all_available_resources_on_second_pass(self):
        """
        This tests bug LSRT-60 where the second observation of template two does not get scheduled
        when dwelling is active. The basic scheduler keeps track of resources that can't be killed.
        The guess is that its used for optimization purposes. The cause of the bug is that this list
        does not get cleared and on dwelling to the next part it should fit. But the resources in
        that list get subtracted from the list handed to the resource_availability checker.
        This test verifies that the complete list should be provided on the second try.
        """
        max_bw_cap = self.get_station_bandwidth_max_capacity()

        # First task must succeed
        task1_id = self.new_task(0)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        scheduler = self.new_dwell_scheduler(task1_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # Second task must also succeed
        task2_id = self.new_task(1)
        estimates = [{ 'resource_types': {'bandwidth': max_bw_cap},
                       "root_resource_group": "CS001",
                       "resource_count": 2 }]
        scheduler = self.new_dwell_scheduler(task2_id, resource_estimator=lambda _: estimates)
        (allocation_successful, changed_tasks) = scheduler.allocate_resources()
        self.assertTrue(allocation_successful)

        # avialable resources can be limited by tracking unkillable resources. They should be
        # cleared on the second try like in this test.
        self.assertEqual(set(r['name'] for r in self.resource_availability_checker.last_available_resources),
                         set(r['name'] for r in self.radb.getResources(include_availability=True)))

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stdout)

if __name__ == '__main__':
    unittest.main()

