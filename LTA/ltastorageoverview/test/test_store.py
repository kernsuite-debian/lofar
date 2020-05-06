#!/usr/bin/env python3

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

# $Id$

from datetime import datetime
import time
from pprint import pformat
import unittest

from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin
from lofar.common.postgres import FETCH_ALL, PostgresDBQueryExecutionError

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


class TestLTAStorageDb(LTAStorageDbTestMixin, unittest.TestCase):
    def testSites(self):
        siteA_id = self.db.insertSiteIfNotExists('siteA', 'srm://siteA.org')
        siteB_id = self.db.insertSiteIfNotExists('siteB', 'srm://siteB.org')

        sites = self.db.sites()
        siteNames = [x['name'] for x in sites]
        self.assertEqual(2, len(siteNames))
        self.assertTrue('siteA' in siteNames)
        self.assertTrue('siteB' in siteNames)

        site = self.db.site(siteA_id)
        self.assertEqual('siteA', site['name'])

        site = self.db.site(siteB_id)
        self.assertEqual('siteB', site['name'])

    def testRootDirs(self):
        siteA_id = self.db.insertSiteIfNotExists('siteA', 'srm://siteA.org')
        siteB_id = self.db.insertSiteIfNotExists('siteB', 'srm://siteB.org')

        dirA1_id = self.db.insertRootDirectory('siteA', 'rootDir1')
        dirA2_id = self.db.insertRootDirectory('siteA', 'rootDir2')
        dirA3_id = self.db.insertRootDirectory('siteA', 'path/to/rootDir3')

        dirB1_id = self.db.insertRootDirectory('siteB', 'rootDir1')
        dirB2_id = self.db.insertRootDirectory('siteB', 'path/to/otherRootDir')

        rootDirs = self.db.rootDirectories()
        self.assertEqual(5, len(rootDirs))

        rootDirsDict = {rd['root_dir_id']:rd for rd in rootDirs}

        self.assertEqual('rootDir1', rootDirsDict[dirA1_id]['dir_name'])
        self.assertEqual(siteA_id, rootDirsDict[dirA1_id]['site_id'])
        self.assertEqual('siteA', rootDirsDict[dirA1_id]['site_name'])

        self.assertEqual('rootDir2', rootDirsDict[dirA2_id]['dir_name'])
        self.assertEqual(siteA_id, rootDirsDict[dirA2_id]['site_id'])
        self.assertEqual('siteA', rootDirsDict[dirA2_id]['site_name'])

        self.assertEqual('path/to/rootDir3', rootDirsDict[dirA3_id]['dir_name'])
        self.assertEqual(siteA_id, rootDirsDict[dirA3_id]['site_id'])
        self.assertEqual('siteA', rootDirsDict[dirA3_id]['site_name'])

        self.assertEqual('rootDir1', rootDirsDict[dirB1_id]['dir_name'])
        self.assertEqual(siteB_id, rootDirsDict[dirB1_id]['site_id'])
        self.assertEqual('siteB', rootDirsDict[dirB1_id]['site_name'])

        self.assertEqual('path/to/otherRootDir', rootDirsDict[dirB2_id]['dir_name'])
        self.assertEqual(siteB_id, rootDirsDict[dirB2_id]['site_id'])
        self.assertEqual('siteB', rootDirsDict[dirB2_id]['site_name'])

        root_dir_ids_siteA = set(d['root_dir_id'] for d in self.db.rootDirectoriesForSite(siteA_id))
        self.assertEqual(set([dirA1_id, dirA2_id, dirA3_id]), root_dir_ids_siteA)

        root_dir_ids_siteB = set(d['root_dir_id'] for d in self.db.rootDirectoriesForSite(siteB_id))
        self.assertEqual(set([dirB1_id, dirB2_id]), root_dir_ids_siteB)

        root_dirs_non_existing_site = self.db.rootDirectoriesForSite(999)
        self.assertEqual([], root_dirs_non_existing_site)

    def testNonExistingDir(self):
        dir = self.db.directoryByName('fjsdka;58432aek5843rfsjd8-sa')
        self.assertEqual(None, dir)

    def testLeastRecentlyVisitedDirectory(self):
        self.db.insertSiteIfNotExists('siteA', 'srm://siteA.org')

        dir_ids = []
        for i in range(3):
            dir_id = self.db.insertRootDirectory('siteA', 'rootDir_%d' % i)
            dir_ids.append(dir_id)

            self.db.updateDirectoryLastVisitTime(dir_id, datetime.utcnow())
            time.sleep(0.002)

        visitStats = self.db.visitStats()
        self.assertTrue('siteA' in visitStats)
        self.assertTrue('least_recent_visited_dir_id' in visitStats['siteA'])

        lvr_dir_id = visitStats['siteA']['least_recent_visited_dir_id']
        self.assertEqual(dir_ids[0], lvr_dir_id)

        self.db.updateDirectoryLastVisitTime(dir_ids[0], datetime.utcnow())
        self.db.updateDirectoryLastVisitTime(dir_ids[1], datetime.utcnow())

        visitStats = self.db.visitStats()
        lvr_dir_id = visitStats['siteA']['least_recent_visited_dir_id']
        self.assertEqual(dir_ids[2], lvr_dir_id)

    def testDuplicateSubDirs(self):
        self.db.insertSiteIfNotExists('siteA', 'srm://siteA.org')
        self.db.insertSiteIfNotExists('siteB', 'srm://siteB.org')

        dirA_id = self.db.insertRootDirectory('siteA', 'rootDir1')
        dirB_id = self.db.insertRootDirectory('siteB', 'rootDir1')

        subDirA1_id = self.db.insertSubDirectory('foo', dirA_id)
        subDirA2_id = self.db.insertSubDirectory('bar', dirA_id)
        subDirB1_id = self.db.insertSubDirectory('foo', dirB_id)

        self.assertNotEquals(None, subDirA1_id)
        self.assertNotEquals(None, subDirA2_id)
        self.assertNotEquals(None, subDirB1_id)

        with self.assertRaises(PostgresDBQueryExecutionError):
            self.db.insertSubDirectory('foo', dirA_id)

    def _fill_test_db_with_sites_and_root_dirs(self):
        """
        helper method to fill empty database with simple sites and root dirs
        """
        self.db.insertSiteIfNotExists('siteA', 'srm://siteA.foo.bar:8443')
        self.db.insertSiteIfNotExists('siteB', 'srm://siteB.foo.bar:8443')

        self.db.insertRootDirectory('siteA', '/root_dir_1')
        self.db.insertRootDirectory('siteA', '/root_dir_2')
        self.db.insertRootDirectory('siteA', '/long/path/to/root_dir_3')
        self.db.insertRootDirectory('siteB', '/root_dir_1')


    def test_insert_missing_directory_tree_if_needed(self):
        """ Test core method _insertMissingDirectoryTreeIfNeeded for all known root dirs.
        Should result in new directory entries in the database for the new sub directories only.
        """
        self._fill_test_db_with_sites_and_root_dirs()

        for site in self.db.sites():
            site_id = site['id']
            for root_dir in self.db.rootDirectoriesForSite(site_id):
                root_dir_path = root_dir['dir_name']

                # root dir should already exist
                dir = self.db.directoryByName(root_dir_path, site_id)
                self.assertIsNotNone(dir)

                # insert the not-so-missing root dir.
                # nothing should happen, because the root dir already exists
                new_dir_ids = self.db.insert_missing_directory_tree_if_needed(root_dir_path, site_id)
                self.assertEqual(0, len(new_dir_ids))

                # now insert some new subdirs, with multiple levels.
                for subdir_path in ['/foo', '/bar/xyz']:
                    dir_path = root_dir_path + subdir_path
                    # dir should not exist yet
                    self.assertIsNone(self.db.directoryByName(dir_path, site_id))

                    # let the handler insert the missing dirs.
                    self.db.insert_missing_directory_tree_if_needed(dir_path, site_id)

                    # dir should exist now
                    dir = self.db.directoryByName(dir_path, site_id)
                    self.assertIsNotNone(dir)

                    # check if new dir has expected root dir
                    parents = self.db.parentDirectories(dir['dir_id'])
                    self.assertEqual(root_dir['root_dir_id'], parents[0]['id'])

    def test_insert_missing_directory_tree_if_needed_for_path_with_unknown_rootdir(self):
        """ Test core method _insertMissingDirectoryTreeIfNeeded for a path with an unknown root dir
        Should raise LookupError.
        """
        self._fill_test_db_with_sites_and_root_dirs()

        for site in self.db.sites():
            site_id = site['id']
            with self.assertRaises(LookupError) as context:
                incorrect_dir_path = '/fdjsalfja5h43535h3oiu/5u905u3f'
                self.db.insert_missing_directory_tree_if_needed(incorrect_dir_path, site_id)
            self.assertTrue('Could not find parent root dir' in str(context.exception))

    def testProjectsAndObservations(self):
        #first insert a lot of data...
        self.db.insertSiteIfNotExists('juelich', 'srm://lofar-srm.fz-juelich.de:8443')
        self.db.insertSiteIfNotExists('sara', 'srm://srm.grid.sara.nl:8443')

        juelich_root_dir_id = self.db.insertRootDirectory('juelich', '/pnfs/fz-juelich.de/data/lofar/ops/')
        sara_root_dir_id = self.db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/ops')

        juelich_projects_dir_id = self.db.insertSubDirectory('/pnfs/fz-juelich.de/data/lofar/ops/projects', juelich_root_dir_id)
        sara_projects_dir_id = self.db.insertSubDirectory('/pnfs/grid.sara.nl/data/lofar/ops/projects', sara_root_dir_id)

        for project_nr, project_name in enumerate(['lc8_001', '2017lofarobs', 'ddt5_001']):
            # projects are sometimes stored at multiple sites
            for projects_dir_id in [juelich_projects_dir_id, sara_projects_dir_id]:
                project_dir_id = self.db.insertSubDirectory('/pnfs/fz-juelich.de/data/lofar/ops/projects/' + project_name,
                                                       projects_dir_id)
                for obs_nr in range(3):
                    obs_name = 'L%06d' % ((project_nr+1)*1000 + obs_nr)
                    obs_dir_id = self.db.insertSubDirectory('/pnfs/fz-juelich.de/data/lofar/ops/projects/' + project_name + '/' + obs_name,
                                                       project_dir_id)

                    for sb_nr in range(244):
                        file_name = '%s_SB%03d.MS.tar' % (obs_name, sb_nr)
                        self.db.insertFileInfo(file_name, 1, datetime.utcnow(), obs_dir_id, False)
                    self.db.commit()

        # then check the results
        # TODO check the results
        logger.info(pformat(self.db.executeQuery('select * from metainfo.project_directory', fetch=FETCH_ALL)))
        logger.info(pformat(self.db.executeQuery('select * from metainfo.project_stats', fetch=FETCH_ALL)))
        logger.info(pformat(self.db.executeQuery('select * from metainfo.project_observation_dataproduct', fetch=FETCH_ALL)))

# run tests if main
if __name__ == '__main__':
    unittest.main()
