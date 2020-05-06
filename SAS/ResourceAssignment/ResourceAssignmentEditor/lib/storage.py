#!/usr/bin/env python3

# mom.py
#
# Copyright (C) 2015
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
#
# $Id: mom.py 1580 2015-09-30 14:18:57Z loose $

"""
TODO: documentation
"""

import logging

logger = logging.getLogger(__name__)

def updateTaskStorageDetails(tasks, sqrpc, curpc):
    if not tasks:
        return

    def applyDefaults(task):
        '''apply sane default values for a task'''
        task['disk_usage'] = None
        task['disk_usage_readable'] = None
        task['data_pinned'] = False

    tasks = tasks if isinstance(tasks, list) else [tasks]

    if len(tasks) == 0:
        return

    for task in tasks:
        applyDefaults(task)

    cep4_tasks = [t for t in tasks if t['cluster'] == 'CEP4']

    try:
        if sqrpc:
            otdb_ids = [t['otdb_id'] for t in cep4_tasks]
            usages = sqrpc.getDiskUsageForTasks(otdb_ids=otdb_ids, include_scratch_paths=False).get('otdb_ids')

            if usages:
                for task in cep4_tasks:
                    otdb_id = task['otdb_id']
                    if otdb_id in usages:
                        usage = usages[otdb_id]
                        task['disk_usage'] = usage.get('disk_usage')
                        task['disk_usage_readable'] = usage.get('disk_usage_readable')
    except Exception as e:
        logger.error(str(e))

    try:
        if curpc:
            pinned_statuses = curpc.getPinnedStatuses()

            for task in tasks:
                otdb_id = int(task['otdb_id'])
                task['data_pinned'] = pinned_statuses.get(otdb_id, False)
    except Exception as e:
        logger.error(str(e))
