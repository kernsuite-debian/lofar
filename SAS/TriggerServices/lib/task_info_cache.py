#!/usr/bin/env python3

# Copyright (C) 2015-2017
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
#
# $Id$

"""
task_info_cache is a module which provides the TaskInfoCache class which caches the info for the current active tasks (observation/pipeline)"""

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler

from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC

from lofar.common.lcu_utils import get_current_stations
from pprint import pformat
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)

class TaskInfo(object):
    def __init__(self, parset, mom_task, mom_project, radb_task):
        self.parset = parset
        self.mom_task = mom_task
        self.mom_project = mom_project
        self.radb_task = radb_task

    def __str__(self):
        return pformat(self.parset) + '\n' + \
               pformat(self.mom_task) + '\n' + \
               pformat(self.mom_project) + '\n' + \
               pformat(self.radb_task)


class TaskInfoCache(OTDBEventMessageHandler):

    def __init__(self,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):
        """
        Creates a TaskInfoCache instance, which listens for OTDB task status events, and then fetches and caches relevant info for the current active task(s).

        :param exchange:
        :param broker:
        """

        # the internal cache is a dict with a mapping of otdb_id->TaskInfo
        self._cache = {}

        # the internal project cache is a dict with a mapping of project_name->project_info_dict
        self._project_cache = {}

        # the internal stations cache is a list of the currently used stations
        self._stations_cache = []

        # internal rpc's to fetch the needed information
        self._otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker, timeout=DEFAULT_RPC_TIMEOUT)
        self._momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker, timeout=DEFAULT_RPC_TIMEOUT)
        self._radbrpc = RADBRPC.create(exchange=exchange, broker=broker, timeout=DEFAULT_RPC_TIMEOUT)

    def get_cached_tasks_otdb_ids(self):
        return list(self._cache.keys())

    def get_active_tasks(self, active_at, task_type=None):
        '''
        get a list of tasks which are active at the given timestamp (t.start <= active_at <= t.end)
        :param active_at: datetime
        :param task_type: string like 'observation' or 'pipeline' to filter by task type. No filtering is applied when task_type=None.
        :return: list of active TaskInfo's
        '''
        tasks =  [ti for ti in list(self._cache.values())
                  if ti.radb_task['starttime'] <= active_at and ti.radb_task['endtime'] >= active_at]

        if task_type is not None:
            tasks = [ti for ti in tasks if ti.radb_task['type'] == task_type]

        return tasks

    def get_task_info(self, otdb_id):
        return self._cache[int(otdb_id)]

    def get_project_info(self, project_name):
        return self._project_cache[project_name]

    def get_project_names(self):
        return sorted(self._project_cache.keys())

    def get_stations(self):
        return self._stations_cache

    def start_handling(self, numthreads=None):
        logger.info("TaskInfoCache starting to listening for upcoming tasks...")
        self._otdbrpc.open()
        self._momrpc.open()
        self._radbrpc.open()
        super(OTDBEventMessageHandler, self).start_handling()

        # make sure we start with a filled projects/stations cache
        self._update_projects_cache()
        self._update_stations_cache()
        self._update_active_tasks_cache()
        logger.info("TaskInfoCache is ready for use, listening for upcoming tasks, and preloaded with projects, stations and active tasks.")

    def stop_handling(self):
        self._otdbrpc.close()
        self._momrpc.close()
        self._radbrpc.close()
        super(OTDBEventMessageHandler, self).stop_handling()
        logger.info("TaskInfoCache stopped listening for upcoming tasks.")

    def onObservationScheduled(self, otdb_id, modificationTime):
        """ overrides OTDBEventMessageHandler.onObservationQueued and calls self._add_task_to_cache """
        return self._update_semi_static_cache_and_add_task_to_cache(otdb_id)

    def onObservationQueued(self, otdb_id, modificationTime):
        """ overrides OTDBEventMessageHandler.onObservationQueued and calls self._add_task_to_cache """
        # update internal project/station cache (could have been updated by a user in the meantime)
        return self._update_semi_static_cache_and_add_task_to_cache(otdb_id)

    def onObservationStarted(self, otdb_id, modificationTime):
        """ overrides OTDBEventMessageHandler.onObservationStarted and calls self._add_task_to_cache """
        return self._update_semi_static_cache_and_add_task_to_cache(otdb_id)

    def onObservationFinished(self, otdb_id, modificationTime):
        """ overrides OTDBEventMessageHandler.onObservationFinished and calls self._remove_task_from_cache """
        return self._remove_task_from_cache(otdb_id)

    def onObservationAborted(self, otdb_id, modificationTime):
        """ overrides OTDBEventMessageHandler.onObservationAborted and calls self._remove_task_from_cache """
        return self._remove_task_from_cache(otdb_id)

    def _update_semi_static_cache_and_add_task_to_cache(self, otdb_id):
        self._update_stations_cache()
        return self._add_task_to_cache(otdb_id)

    def _update_semi_static_cache(self):
        # update internal project/station cache (could have been updated by a user in the meantime)
        self._update_projects_cache()
        self._update_stations_cache()

    def _update_projects_cache(self):
        # update internal project cache (could have been updated by a user in the meantime)
        self._project_cache = {str(p['name']):p for p in self._momrpc.getProjects()}
        logger.info("TaskInfoCache: updated projects cache.")

    def _update_stations_cache(self):
        # update internal stations cache (could have been updated by a user in the meantime)
        self._stations_cache = get_current_stations('today_nl', as_host_names=False)
        logger.info("TaskInfoCache: updated stations cache.")

    def _update_active_tasks_cache(self):
        now = datetime.utcnow()
        tasks = self._radbrpc.getTasks(lower_bound=now - timedelta(hours=6),
                                       upper_bound=now + timedelta(hours=12),
                                       task_status=['scheduled', 'queued', 'active', 'completing'])

        tasks_with_mom_id = [t for t in tasks if t.get('mom_id') is not None]
        task_otdb_ids = [t['otdb_id'] for t in tasks_with_mom_id]

        logger.info("TaskInfoCache: adding %s active tasks to cache: %s", len(task_otdb_ids), ', '.join(str(id) for id in task_otdb_ids))

        for otdb_id in task_otdb_ids:
            self._add_task_to_cache(otdb_id)
        logger.info("TaskInfoCache: updated active tasks cache.")

    def _add_task_to_cache(self, otdb_id):
        logger.info("adding info for otdb_id=%s to cache", otdb_id)

        # fetch individual data for task from various rpc's
        radb_task = self._radbrpc.getTask(otdb_id=otdb_id)
        if radb_task.get('mom_id') is None:
            logger.warning("skipping adding cache info for otdb_id=%s because it's mom_id is None.", otdb_id)
            return

        parset = self._otdbrpc.taskGetSpecification(otdb_id=otdb_id)["specification"]
        mom_task_info = self._momrpc.getObjectDetails(radb_task['mom_id'])[radb_task['mom_id']]

        # fetch the task's project info from the updated project cache
        project_info = self.get_project_info(mom_task_info['project_name'])
        self._cache[otdb_id] = TaskInfo(parset, mom_task_info, project_info, radb_task)

        logger.info("cache info for otdb_id=%s: %s", otdb_id, self._cache[otdb_id])

    def _remove_task_from_cache(self, otdb_id):
        logger.info("removing info for otdb_id=%s to cache")
        if otdb_id in self._cache:
            del self._cache[otdb_id]

if __name__ == '__main__':
    """Example usage"""
    from lofar.common.util import waitForInterrupt
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    # start listening on all default messaging buses,
    # and let the TaskInfoCache instance log the events as they come along.
    with OTDBBusListener(TaskInfoCache):
        waitForInterrupt()
