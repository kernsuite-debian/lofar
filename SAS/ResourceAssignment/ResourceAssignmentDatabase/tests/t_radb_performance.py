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
import os, sys
from datetime import datetime, timedelta
from dateutil import parser
from pprint import pformat
from random import randint
from lofar.common.datetimeutils import totalSeconds
import logging
logger = logging.getLogger(__name__)


from lofar.sas.resourceassignment.database.testing.radb_common_testing import RADBCommonTestMixin
from lofar.sas.resourceassignment.database.radb import RADatabase, FETCH_ONE

class ResourceAssignmentDatabaseTest(RADBCommonTestMixin, unittest.TestCase):
    def test_resource_usages_performance(self):
        ELAPSED_TRESHOLD = 2.0 #max allowed insert/update/delete time in seconds

        num_resources = self.radb.executeQuery('select count(id) from virtual_instrument.resource;', fetch=FETCH_ONE)['count']
        # make sure all resources have 1000 units available
        MAX_CAPACITY=1000
        self.radb.executeQuery('update resource_monitoring.resource_capacity set (available, total) = (%s, %s);', (MAX_CAPACITY,MAX_CAPACITY))

        # pretend that we have an almost unlimited amount of storage space
        self.radb.executeQuery('update resource_monitoring.resource_capacity set (available, total) = (%s, %s) ' \
                                'where resource_id in (select id from virtual_instrument.resource_view where type_name = \'storage\');',
                                (1e9*MAX_CAPACITY,1e9*MAX_CAPACITY))

        # keep a list of storage-type resource(ids), so we can create long lasting claims for these.
        storage_resource_ids = set(r['id'] for r in self.radb.getResources(resource_types='storage'))

        now = datetime.utcnow()
        now -= timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)  # round to full hour
        spec_ids = []
        filename = 'resource_usages_performance%s.csv' % (datetime.utcnow().strftime('%Y%m%dT%H%M%S'),)
        with open(filename, 'w') as file:
            file.write('#tasks, #claims, #claims_per_resource, #inserted_claims, elapsed_insert\n')
            counter = 0
            # it is not common to claim a single resource multiple times for the same task, but it can happen, so test for it.
            for preferred_num_claims_per_resource in [1, 2, 5, 10, 20, 50]:
                # let's test over a feasible range of #claims. A lofar observation usually has ~200 claims.
                for num_claims_to_insert in [1, 2, 5, 10, 20, 50, 100, 200, 500]:
                    num_claims_to_insert = min(num_claims_to_insert, preferred_num_claims_per_resource*num_resources)
                    num_claims_per_resource = min(preferred_num_claims_per_resource, num_claims_to_insert)

                    for oversubscription_factor in [1, 999]:
                        counter += 1

                        logger.info('*****************************************************************')
                        logger.info('starting task and claim scheduling: counter=%s num_claims_per_resource=%s num_claims_to_insert=%s oversubscription_factor=%s',
                                    counter, num_claims_per_resource, num_claims_to_insert, oversubscription_factor)

                        result = self.radb.insertOrUpdateSpecificationAndTask(counter, counter, 'approved', 'observation',
                                                                      now+timedelta(hours=3*counter),
                                                                      now + timedelta(hours=3*counter + 1),
                                                                      'content', 'CEP4')
                        task_id = result['task_id']
                        task = self.radb.getTask(task_id)
                        spec_ids.append(task['specification_id'])

                        claims = [{'resource_id': q/num_claims_per_resource,
                                   'starttime': task['starttime'],
                                   'endtime': task['endtime'],
                                   'status': 'tentative',
                                   'claim_size': oversubscription_factor*MAX_CAPACITY/num_claims_per_resource}
                                  for q in range(num_claims_to_insert)]

                        # extend claims on storage resources
                        for claim in claims:
                            if claim['resource_id'] in storage_resource_ids:
                                claim['endtime'] += timedelta(days=100)

                        start = datetime.utcnow()
                        self.radb.insertResourceClaims(task_id, claims, 'foo', 1, 1)
                        elapsed_insert = totalSeconds(datetime.utcnow() - start)

                        num_tasks = self.radb.executeQuery('select count(id) from resource_allocation.task;', fetch=FETCH_ONE)['count']
                        num_claims = self.radb.executeQuery('select count(id) from resource_allocation.resource_claim;', fetch=FETCH_ONE)['count']
                        has_storage_claims = len(self.radb.getResourceClaims(task_ids=task_id, resource_type='storage')) > 0

                        # enforce perfomance criterion: inserting claims should take less than ELAPSED_TRESHOLD sec
                        self.assertLess(elapsed_insert, ELAPSED_TRESHOLD, msg="insertResourceClaims took longer than allowed. (%ssec > %ssec) num_tasks=%s num_claims=%s num_claims_to_insert=%s num_claims_per_resource=%s" %(
                                                                  elapsed_insert, ELAPSED_TRESHOLD, num_tasks, num_claims, num_claims_to_insert, num_claims_per_resource))

                        if oversubscription_factor > 1:
                            # (deliberate) oversubscription of resources
                            # so, expect the claims and task to be in conflict
                            self.assertGreater(len(self.radb.getResourceClaims(task_ids=task_id, status='conflict')), 0)
                            self.assertEqual('conflict', self.radb.getTask(task_id)['status'])

                            # solve oversubscription
                            start = datetime.utcnow()
                            self.radb.updateResourceClaims(where_task_ids=task_id, claim_size=MAX_CAPACITY/num_claims_per_resource)
                            elapsed_status_update = totalSeconds(datetime.utcnow() - start)

                            # enforce perfomance criterion: updating claims should take less than ELAPSED_TRESHOLD sec
                            self.assertLess(elapsed_status_update, ELAPSED_TRESHOLD,
                                            msg="updateResourceClaims took longer than allowed. (%ssec > %ssec) num_tasks=%s num_claims=%s num_claims_to_insert=%s num_claims_per_resource=%s" % (
                                                 elapsed_status_update, ELAPSED_TRESHOLD, num_tasks, num_claims, num_claims_to_insert, num_claims_per_resource))

                            # check if not oversubscribed anymore
                            self.assertEqual(0, len(self.radb.getResourceClaims(task_ids=task_id, status='conflict')))
                            self.assertEqual('approved', self.radb.getTask(task_id)['status'])

                        # no oversubscription (anymore), so expect all claims to be claimable...
                        start = datetime.utcnow()
                        self.radb.updateTaskAndResourceClaims(task_id=task_id, claim_status='claimed')
                        elapsed_status_update = totalSeconds(datetime.utcnow() - start)

                        # are they indeed claimed?
                        self.assertEqual(num_claims_to_insert, len(self.radb.getResourceClaims(task_ids=task_id, status='claimed')))

                        # enforce perfomance criterion: updating claims should take less than 2*ELAPSED_TRESHOLD sec (2* because we update both tasks and claims)
                        self.assertLess(elapsed_status_update, 2*ELAPSED_TRESHOLD, msg="updateTaskAndResourceClaims took longer than allowed. (%ssec > %ssec) num_tasks=%s num_claims=%s num_claims_to_insert=%s num_claims_per_resource=%s" % (
                                                                                 elapsed_status_update, ELAPSED_TRESHOLD, num_tasks, num_claims, num_claims_to_insert, num_claims_per_resource))

                        # ... and proceed with cycling through the task status
                        for task_status in ['prescheduled', 'scheduled', 'queued', 'active', 'completing', 'finished']:
                            # update the task status
                            start = datetime.utcnow()
                            self.radb.updateTaskAndResourceClaims(task_id=task_id, task_status=task_status)
                            elapsed_status_update = totalSeconds(datetime.utcnow() - start)

                            # enforce perfomance criterion: updating task status should take less than  2*ELAPSED_TRESHOLD sec (2* because we update both tasks and claims)
                            self.assertLess(elapsed_status_update, 2*ELAPSED_TRESHOLD, msg="updateTaskAndResourceClaims took longer than allowed. (%ssec > %ssec) num_tasks=%s num_claims=%s num_claims_to_insert=%s num_claims_per_resource=%s task_status=%s" % (
                                                                                            elapsed_status_update, ELAPSED_TRESHOLD, num_tasks, num_claims, num_claims_to_insert, num_claims_per_resource, task_status))

                            # check task status
                            self.assertEqual(task_status, self.radb.getTask(task_id)['status'])

                        # task should now be finished
                        self.assertEqual('finished', self.radb.getTask(task_id)['status'])
                        # and all non-long-lasting (storage) claims should be removed.
                        self.assertEqual(0, len(list(c for c in self.radb.getResourceClaims(task_ids=task_id) if c['endtime'] <= task['endtime'])))

                        if has_storage_claims:
                            # and all long-lasting (storage) claims should still be there.
                            # (they are removed by  the cleanupservice ending/removing the storage claims)
                            self.assertGreater(len(list(c for c in self.radb.getResourceClaims(task_ids=task_id) if c['endtime'] > task['endtime'])), 0)

                        logger.info('TEST RESULT: radb now contains %d tasks, %d claims, insert of %d claims with %d claims per resource takes on average %.3fsec',
                                    num_tasks, num_claims, num_claims_to_insert, num_claims_per_resource, elapsed_insert)
                        file.write('%d, %d, %d, %d, %.3f\n' % (num_tasks, num_claims, num_claims_per_resource, num_claims_to_insert, elapsed_insert))
                        file.flush()

            logger.info('removing all test specs/tasks/claims from db')
            delete_elapsed_list = []

            file.write('\n\n#tasks, #claims, elapsed_delete\n')

            for spec_id in spec_ids:
                num_tasks = self.radb.executeQuery('select count(id) from resource_allocation.task;', fetch=FETCH_ONE)['count']
                num_claims = self.radb.executeQuery('select count(id) from resource_allocation.resource_claim;', fetch=FETCH_ONE)['count']
                start = datetime.utcnow()
                self.radb.deleteSpecification(spec_id)
                elapsed = totalSeconds(datetime.utcnow() - start)
                delete_elapsed_list.append(elapsed)

                # enforce perfomance criterion: (cascading) delete of spec should take less than ELAPSED_TRESHOLD sec
                self.assertLess(elapsed, ELAPSED_TRESHOLD)

                file.write('%d, %d, %.3f\n' % (num_tasks, num_claims, elapsed))
                file.flush()

        logger.info('average spec delete time: %.3f', sum(delete_elapsed_list)/float(len(delete_elapsed_list)))
        logger.info('Done. Results can be found in file: %s', filename)

os.environ['TZ'] = 'UTC'
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stdout)

if __name__ == "__main__":
    unittest.main()
