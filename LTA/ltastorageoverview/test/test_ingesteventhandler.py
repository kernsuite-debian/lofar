#!/usr/bin/env python3

# Copyright (C) 2018 ASTRON (Netherlands Institute for Radio Astronomy)
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

# $Id$

from datetime import datetime
import unittest

from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin
from lofar.lta.ltastorageoverview.ingesteventhandler import LTASOIngestEventHandler

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


class TestLTASOIngestEventHandler(LTAStorageDbTestMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.fill_with_test_data()

    def fill_with_test_data(self):
        self.db.insertSiteIfNotExists('siteA', 'srm://siteA.foo.bar:8443')
        self.db.insertSiteIfNotExists('siteB', 'srm://siteB.foo.bar:8443')

        self.db.insertRootDirectory('siteA', '/root_dir_1')
        self.db.insertRootDirectory('siteA', '/root_dir_2')
        self.db.insertRootDirectory('siteA', '/long/path/to/root_dir_3')
        self.db.insertRootDirectory('siteB', '/root_dir_1')

        self._markAllDirectoriesRecentlyVisited()

    def _markAllDirectoriesRecentlyVisited(self):
        """pretend that all dirs were recently visited
        """
        self.db.executeQuery('''update scraper.last_directory_visit set visit_date=%s;''', (datetime.utcnow(), ))
        self.db.commit()

    def test_01_schedule_srmurl_for_visit_unknown_site(self):
        """ try to schedule some unknown site's surl. Should raise.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        with self.assertRaises(LookupError) as context:
            surl = 'srm://foo.bar:1234/fdjsalfja5h43535h3oiu/5u905u3f'
            handler._schedule_srmurl_for_visit(surl)
        self.assertTrue('Could not find site' in str(context.exception))

    def test_02_mark_directory_for_a_visit(self):
        """ Test core method _mark_directory_for_a_visit for all known root dirs.
        Should set the last visit time for each dir way in the past.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)
        now = datetime.utcnow()

        for site in self.db.sites():
            for root_dir in self.db.rootDirectoriesForSite(site['id']):
                dir_id = root_dir['root_dir_id']
                # make sure the dir's last visit time is recent
                self.db.updateDirectoryLastVisitTime(dir_id, now)
                timestamp_before_mark = self.db.directoryLastVisitTime(dir_id)
                self.assertEqual(now, timestamp_before_mark)

                # let the handler mark the dir for a next visit...
                handler._mark_directory_for_a_visit(dir_id)

                # by marking the dir for a next visit, the dir's last visit time is set way in the past.
                timestamp_after_mark = self.db.directoryLastVisitTime(dir_id)
                self.assertLess(timestamp_after_mark, timestamp_before_mark)

    def test_03_insert_missing_directory_tree_if_needed(self):
        """ Test core method _insert_missing_directory_tree_if_needed for all known root dirs.
        Should result in new directory entries in the database for the new sub directories only.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        for site in self.db.sites():
            site_surl = site['url']
            site_id = site['id']
            for root_dir in self.db.rootDirectoriesForSite(site_id):
                dir_path = root_dir['dir_name']
                surl = site_surl + dir_path

                # root dir should already exist
                dir = self.db.directoryByName(dir_path, site_id)
                self.assertIsNotNone(dir)

                # let the handler insert the not-so-missing dirs.
                # nothing should happen, because the root dir already exists
                new_dir_ids = handler._insert_missing_directory_tree_if_needed(surl)
                self.assertEqual(0, len(new_dir_ids))

                # now insert some new subdirs, with multiple levels.
                for subdir_path in ['/foo', '/bar/xyz']:
                    dir_path = root_dir['dir_name'] + subdir_path
                    surl = site_surl + dir_path
                    # dir should not exist yet
                    self.assertIsNone(self.db.directoryByName(dir_path, site_id))

                    # let the handler insert the missing dirs.
                    handler._insert_missing_directory_tree_if_needed(surl)

                    # dir should exist now
                    dir = self.db.directoryByName(dir_path, site_id)
                    self.assertIsNotNone(dir)

                    # check if new dir has expected root dir
                    parents = self.db.parentDirectories(dir['dir_id'])
                    self.assertEqual(root_dir['root_dir_id'], parents[0]['id'])

    def test_04_insert_missing_directory_tree_if_needed_for_path_with_unknown_rootdir(self):
        """ Test core method _insert_missing_directory_tree_if_needed for a path with an unknown root dir
        Should raise LookupError.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        for site in self.db.sites():
            with self.assertRaises(LookupError) as context:
                surl = site['url'] + '/fdjsalfja5h43535h3oiu/5u905u3f'
                handler._insert_missing_directory_tree_if_needed(surl)
            self.assertTrue('Could not find parent root dir' in str(context.exception))

    def test_05_schedule_srmurl_for_visit_for_root_dir(self):
        """ Test higher level method _schedule_srmurl_for_visit for all known root dirs.
        Should result in marking the dir matching the surl as being the dir which should be visited next.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        for site in self.db.sites():
            for root_dir in self.db.rootDirectoriesForSite(site['id']):
                self._markAllDirectoriesRecentlyVisited()
                now = datetime.utcnow()

                dir_id = root_dir['root_dir_id']
                surl = site['url'] + root_dir['dir_name']
                handler._schedule_srmurl_for_visit(surl)

                # surl was scheduled for a visit, so this dir should be the least_recent_visited_dir
                site_visit_stats = self.db.visitStats(datetime.utcnow())[site['name']]
                self.assertEqual(dir_id, site_visit_stats['least_recent_visited_dir_id'])

                # mimick a directory visit by the scraper, by setting the last visit time to now.
                self.db.updateDirectoryLastVisitTime(dir_id, now)

                # we faked a visit, so this dir should not be the least_recent_visited_dir anymore
                site_visit_stats = self.db.visitStats(now)[site['name']]
                self.assertNotEqual(dir_id, site_visit_stats.get('least_recent_visited_dir_id'))

    def test_06_schedule_srmurl_for_visit_for_new_root_sub_dir(self):
        """ Test higher level method _schedule_srmurl_for_visit for all new unknown subdirs of the known root dirs.
        Should result in marking the dir matching the surl as being the dir which should be visited next.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        for site in self.db.sites():
            for root_dir in self.db.rootDirectoriesForSite(site['id']):
                self._markAllDirectoriesRecentlyVisited()
                now = datetime.utcnow()

                # create the subdir surl
                sub_dir_name = '/foo'
                sub_dir_path = root_dir['dir_name'] + sub_dir_name
                surl = site['url'] + sub_dir_path

                # call the method under test
                handler._schedule_srmurl_for_visit(surl)

                # surl was scheduled for a visit, all other dir's were marked as visited already...
                # so there should be a new dir for this surl, and it should be the least_recent_visited_dir
                site_visit_stats = self.db.visitStats(datetime.utcnow())[site['name']]

                least_recent_visited_dir_id = site_visit_stats.get('least_recent_visited_dir_id')
                self.assertIsNotNone(least_recent_visited_dir_id)

                least_recent_visited_dir = self.db.directory(least_recent_visited_dir_id)
                self.assertEqual(sub_dir_path, least_recent_visited_dir['dir_name'])

                # mimick a directory visit by the scraper, by setting the last visit time to now.
                self.db.updateDirectoryLastVisitTime(least_recent_visited_dir_id, now)

                # we faked a visit, so this dir should not be the least_recent_visited_dir anymore
                site_visit_stats = self.db.visitStats(now)[site['name']]
                self.assertNotEqual(least_recent_visited_dir_id, site_visit_stats.get('least_recent_visited_dir_id'))

    def test_07_schedule_srmurl_for_visit_for_path_with_unknown_rootdir(self):
        """ Test higher level method _schedule_srmurl_for_visit for a path with an unknown root dir
        Should raise LookupError.
        """
        handler = LTASOIngestEventHandler(dbcreds=self.dbcreds)

        for site in self.db.sites():
            with self.assertRaises(LookupError) as context:
                surl = site['url'] + '/fdjsalfja5h43535h3oiu/5u905u3f'
                handler._schedule_srmurl_for_visit(surl)
            self.assertTrue('Could not find parent root dir' in str(context.exception))

    def test_08_integration_test_with_messagebus(self):
        """ Full blown integration test listening for notifications on the bus,
        and checking which dir is up for a visit next.
        Needs a working local qpid broker. Test is skipped if qpid not available.
        """
        try:
            broker = None
            connection = None

            import uuid
            from threading import Event
            from qpid.messaging import Connection, ConnectError
            from qpidtoollibs import BrokerAgent
            from lofar.messaging.messagebus import ToBus
            from lofar.messaging.messages import EventMessage
            from lofar.lta.ingest.common.config import DEFAULT_INGEST_NOTIFICATION_PREFIX

            # setup broker connection
            connection = Connection.establish('127.0.0.1')
            broker = BrokerAgent(connection)

            # add test service bus
            busname = 'test-LTASOIngestEventHandler-%s' % (uuid.uuid1())
            broker.addExchange('topic', busname)

            sync_event = Event()

            class SyncedLTASOIngestEventHandler(LTASOIngestEventHandler):
                """This derived LTASOIngestEventHandler behaves exactly like the normal
                object under test LTASOIngestEventHandler, but it also sets a sync_event
                to sync between the listener thread and this main test thread"""
                def _handleMessage(self, msg):
                    super(SyncedLTASOIngestEventHandler, self)._handleMessage(msg)
                    sync_event.set()

            with SyncedLTASOIngestEventHandler(self.dbcreds, busname=busname):
                for site in self.db.sites():
                    for root_dir in self.db.rootDirectoriesForSite(site['id']):
                        self._markAllDirectoriesRecentlyVisited()

                        # create the subdir surl
                        sub_dir_name = '/foo'
                        sub_dir_path = root_dir['dir_name'] + sub_dir_name
                        surl = site['url'] + sub_dir_path

                        with ToBus(busname) as sender:
                            msg = EventMessage(subject=DEFAULT_INGEST_NOTIFICATION_PREFIX+"TaskFinished",
                                               content={'srm_url': surl})
                            sender.send(msg)

                        # wait for the handler to have processed the message
                        self.assertTrue(sync_event.wait(2))
                        sync_event.clear()

                        # surl should have been scheduled for a visit, all other dir's were marked as visited already...
                        # so there should be a new dir for this surl, and it should be the least_recent_visited_dir
                        site_visit_stats = self.db.visitStats(datetime.utcnow())[site['name']]

                        least_recent_visited_dir_id = site_visit_stats.get('least_recent_visited_dir_id')
                        self.assertIsNotNone(least_recent_visited_dir_id)

                        least_recent_visited_dir = self.db.directory(least_recent_visited_dir_id)
                        self.assertEqual(sub_dir_path, least_recent_visited_dir['dir_name'])

        except ImportError as e:
            logger.warning("skipping test due to: %s", e)
        except ConnectError as e:
            logger.warning("skipping test due to: %s", e)
        finally:
            # cleanup test bus and exit
            if broker:
                broker.delExchange(busname)
            if connection:
                connection.close()


# run tests if main
if __name__ == '__main__':
    unittest.main()
