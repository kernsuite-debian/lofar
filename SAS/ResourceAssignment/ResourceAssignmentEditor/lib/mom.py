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

def updateTaskMomDetails(task, momrpc):
    '''fill in the task propeties with mom object and project details.
    :param task: dictionary or list of dictionaries with the task(s)
    :param momrpc: MoM rpc object the query for details'''
    def applyDefaults(t):
        '''apply sane default values for a task'''
        t['name'] = 'Task (sasId: %d)' % t['otdb_id']
        t['project_name'] = '<unknown>'
        t['project_mom_id'] = -99

    tasklist = task if isinstance(task, list) else [task]

    if len(tasklist) == 0:
        return

    for t in tasklist:
        applyDefaults(t)

    if not momrpc:
        return

    try:
        momIds = ','.join([str(t['mom_id']) for t in tasklist])
        details = momrpc.getObjectDetails(momIds)

        for t in tasklist:
            mom_id = t['mom_id']
            if mom_id in details:
                m = details[mom_id]
                t['name'] = m['object_name']
                t['project_name'] = m['project_name']
                t['project_mom_id'] = m['project_mom2id']
                t['project_mom2object_id'] = m['project_mom2objectid']
                t['description'] = m.get('object_description', '')
                t['sub_type'] = m.get('object_type', t['type']).lower()
                t['mom2object_id'] = m['object_mom2objectid']
                t['mom_object_group_id'] = m['object_group_id']
                t['mom_object_group_name'] = m.get('object_group_name')
                t['mom_object_group_mom2object_id'] = m.get('object_group_mom2objectid')
                t['mom_object_parent_group_id'] = m['parent_group_mom2id']
                t['mom_object_parent_group_name'] = m['parent_group_name']
            elif t['type'] == 'reservation':
                t['project_name'] = 'Reservations'
                t['project_mom_id'] = -97
            else:
                t['project_name'] = 'OTDB Only'
                t['project_mom_id'] = -98

        results = momrpc.getDataProducts(momIds)

        for t in tasklist:
            mom_id = t['mom_id']
            t['ingest_status'] = None
            t['nr_of_dataproducts'] = None
            if mom_id in results:
                dps = results[mom_id]
                if dps != None:
                    t['nr_of_dataproducts'] = len(dps)
                    if len(dps) > 0:
                        num_ingested = 0
                        num_ingest_pending = 0
                        num_ingest_running = 0
                        num_ingest_failed = 0
                        num_ingest_hold = 0
                        num_ingest_aborted = 0
                        for dp in dps:
                            if dp['status'] == 'ingested':
                                num_ingested += 1
                            elif dp['status'] == 'pending':
                                num_ingest_pending += 1
                            elif dp['status'] == 'running':
                                num_ingest_running += 1
                            elif dp['status'] == 'failed':
                                num_ingest_failed += 1
                            elif dp['status'] == 'on_hold':
                                num_ingest_hold += 1
                            elif dp['status'] == 'aborted':
                                num_ingest_aborted += 1

                        ingestable_dataproducts = [dp for dp in dps if dp['status'] not in [None, 'has_data', 'no_data', 'populated'] ]

                        if num_ingested > 0 and num_ingested == len(ingestable_dataproducts):
                            t['ingest_status'] = 'ingested'
                        elif num_ingest_pending + num_ingest_running > 0:
                            t['ingest_status'] = 'ingesting'
                        elif num_ingest_failed + num_ingest_aborted + num_ingest_hold > 0:
                            t['ingest_status'] = 'failed'

    except Exception as e:
        logger.error(str(e))

