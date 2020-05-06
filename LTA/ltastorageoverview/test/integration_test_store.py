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

import logging
from datetime import datetime, timedelta
import unittest
from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


class IntegrationTestLTAStorageDb(LTAStorageDbTestMixin, unittest.TestCase):
    """
    Bigger tests for the lofar.lta.ltastorageoverview.store.LTAStorageDb
    which test more complex behaviour with bigger amounts of data.
    """

    def testDirectoryTreesAndStats(self):
        """Quite a big test, almost an integration test.
        It consists of two stages/phases:
        1) inserts a tree of directories and files in various sites and projects,
        2) test if the automatically computed tree- and dirstats are correct.
        """

        base_time = datetime.utcnow()
        base_time -= timedelta(seconds=base_time.second, microseconds=base_time.microsecond)

        ###########################################################
        # STAGE 1: insertion and check phase.
        # insert the sites, directories, and files
        # and check the dir- and tree stats directly after insertion
        ###########################################################
        NUM_SITES = 2
        NUM_PROJECTS = 3
        NUM_PROJECT_SUBDIRS = 4
        NUM_SUB_SUBDIRS = 5

        # helper dict to store all subdir id's for each dir.
        dir2subdir = {}

        for site_nr in range(NUM_SITES):
            site_name = 'site%d' % site_nr
            site_url = 'srm://%s.org' % site_name
            self.db.insertSiteIfNotExists(site_name, site_url)

            for project_nr in range(NUM_PROJECTS):
                rootDir_id = self.db.insertRootDirectory(site_name, 'rootDir_%d' % project_nr)
                dir2subdir[rootDir_id] = []

                for subdir_nr in range(NUM_PROJECT_SUBDIRS):
                    subDir_id = self.db.insertSubDirectory('subDir_%d' % subdir_nr, rootDir_id)
                    dir2subdir[subDir_id] = []
                    dir2subdir[rootDir_id].append(subDir_id)
                    for file_nr in range(project_nr*subdir_nr):
                        self.db.insertFileInfo('file_%d' % file_nr, 271*(file_nr+1), base_time + timedelta(days=10*site_nr+project_nr, hours=subdir_nr, seconds=file_nr), subDir_id)

                        dir_files = self.db.filesInDirectory(subDir_id)
                        dir_stats = self.db.directoryTreeStats(subDir_id)

                        self.assertEqual(sum(f['size'] for f in dir_files), dir_stats['dir_total_file_size'])
                        self.assertEqual(len(dir_files), dir_stats['dir_num_files'])
                        if dir_files:
                            self.assertEqual(min(f['size'] for f in dir_files), dir_stats['dir_min_file_size'])
                            self.assertEqual(max(f['size'] for f in dir_files), dir_stats['dir_max_file_size'])
                            self.assertEqual(min(f['creation_date'] for f in dir_files), dir_stats['dir_min_file_creation_date'])
                            self.assertEqual(max(f['creation_date'] for f in dir_files), dir_stats['dir_max_file_creation_date'])

                    for subsubdir_nr in range(NUM_SUB_SUBDIRS):
                        subsubDir_id = self.db.insertSubDirectory('subsubDir_%d' % subsubdir_nr, subDir_id)
                        dir2subdir[subsubDir_id] = []
                        dir2subdir[subDir_id].append(subsubDir_id)
                        for kk in range(project_nr*subdir_nr*subsubdir_nr):
                            self.db.insertFileInfo('file_%d_%d' % (subdir_nr,kk), 314*(kk+1), base_time + timedelta(days=10*site_nr+project_nr, hours=10*subdir_nr+subsubdir_nr+2, seconds=kk), subsubDir_id)

                            dir_files = self.db.filesInDirectory(subsubDir_id)
                            dir_stats = self.db.directoryTreeStats(subsubDir_id)

                            self.assertEqual(sum(f['size'] for f in dir_files), dir_stats['dir_total_file_size'])
                            self.assertEqual(len(dir_files), dir_stats['dir_num_files'])
                            if dir_files:
                                self.assertEqual(min(f['size'] for f in dir_files), dir_stats['dir_min_file_size'])
                                self.assertEqual(max(f['size'] for f in dir_files), dir_stats['dir_max_file_size'])
                                self.assertEqual(min(f['creation_date'] for f in dir_files), dir_stats['dir_min_file_creation_date'])
                                self.assertEqual(max(f['creation_date'] for f in dir_files), dir_stats['dir_max_file_creation_date'])

                                tree_totals = self.db.totalFileSizeAndNumFilesInTree(subDir_id, dir_stats['dir_min_file_creation_date'], dir_stats['dir_max_file_creation_date'])
                                self.assertEqual(tree_totals['tree_num_files'], dir_stats['dir_num_files'])
                                self.assertEqual(tree_totals['tree_total_file_size'], dir_stats['dir_total_file_size'])

                    # test 1st level subdir again, and also check inclusion of 2nd level subdirs in tree stats
                    dir_files = self.db.filesInDirectory(subDir_id)
                    dir_stats = self.db.directoryTreeStats(subDir_id)
                    # this dir only...
                    self.assertEqual(sum(f['size'] for f in dir_files), dir_stats['dir_total_file_size'])
                    self.assertEqual(len(dir_files), dir_stats['dir_num_files'])
                    if dir_files:
                        self.assertEqual(min(f['size'] for f in dir_files), dir_stats['dir_min_file_size'])
                        self.assertEqual(max(f['size'] for f in dir_files), dir_stats['dir_max_file_size'])
                        self.assertEqual(min(f['creation_date'] for f in dir_files), dir_stats['dir_min_file_creation_date'])
                        self.assertEqual(max(f['creation_date'] for f in dir_files), dir_stats['dir_max_file_creation_date'])

                    # including subdirs in tree...
                    self.assertEqual(sum(f['file_size'] for f in self.db.filesInTree(subDir_id)), dir_stats['tree_total_file_size'])
                    self.assertEqual(len(self.db.filesInTree(subDir_id)), dir_stats['tree_num_files'])

        ####################################################################################
        # STAGE 2: reporting phase.
        # loop over the sites, directories, and files now that the database has been filled.
        # and check the dir- and tree stats totals
        ####################################################################################
        for site in self.db.sites():
            site_id = site['id']

            rootDirs = self.db.rootDirectoriesForSite(site_id)
            self.assertEqual(NUM_PROJECTS, len(rootDirs))

            for root_dir_id in [x['root_dir_id'] for x in rootDirs]:
                subDirs = self.db.subDirectories(root_dir_id, 1, False)
                self.assertEqual(NUM_PROJECT_SUBDIRS, len(subDirs))

                for subDir in subDirs:
                    subDir_parent_id = subDir['parent_dir_id']
                    self.assertEqual(root_dir_id, subDir_parent_id)
                    self.assertTrue(subDir['id'] in dir2subdir[root_dir_id])

                    subsubDirs = self.db.subDirectories(subDir['id'], 1, False)
                    self.assertEqual(NUM_SUB_SUBDIRS, len(subsubDirs))

                    for subsubDir in subsubDirs:
                        subsubDir_parent_id = subsubDir['parent_dir_id']
                        self.assertEqual(subDir['id'], subsubDir_parent_id)
                        self.assertTrue(subsubDir['id'] in dir2subdir[subDir['id']])

                # check various selects of files in the tree, for each file
                tree_files = sorted(self.db.filesInTree(root_dir_id), key=lambda f: f['file_creation_date'])
                for file in tree_files:
                    # check if filesInTree return this one file when time delimited for this specific file_creation_date
                    file_creation_date = file['file_creation_date']
                    selected_tree_files = self.db.filesInTree(root_dir_id, file_creation_date, file_creation_date)
                    self.assertEqual(1, len(selected_tree_files))
                    self.assertEqual(file['file_creation_date'], selected_tree_files[0]['file_creation_date'])
                    self.assertEqual(file['file_size'], selected_tree_files[0]['file_size'])

                    # get the 'totals' for this root_dir, but select only this file by date.
                    # should return 1 file.
                    tree_totals = self.db.totalFileSizeAndNumFilesInTree(root_dir_id, file_creation_date, file_creation_date)
                    self.assertEqual(1, tree_totals['tree_num_files'])
                    self.assertEqual(file['file_size'], tree_totals['tree_total_file_size'])

                # check some ranges files/times
                for idx, file in enumerate(tree_files):
                    file_creation_date = file['file_creation_date']

                    #select any file >= file_creation_date
                    expected_selected_tree_files = tree_files[idx:]
                    selected_tree_files = self.db.filesInTree(root_dir_id, file_creation_date, None)
                    self.assertEqual(len(expected_selected_tree_files), len(selected_tree_files))
                    selected_tree_files_ids = set([f['file_id'] for f in selected_tree_files])
                    for expected_file in expected_selected_tree_files:
                        self.assertTrue(expected_file['file_id'] in selected_tree_files_ids)

                    # and check the totals as well
                    tree_totals = self.db.totalFileSizeAndNumFilesInTree(root_dir_id, file_creation_date, None)
                    self.assertEqual(len(expected_selected_tree_files), tree_totals['tree_num_files'])
                    self.assertEqual(sum(f['file_size'] for f in expected_selected_tree_files), tree_totals['tree_total_file_size'])

                    #select any file <= file_creation_date
                    expected_selected_tree_files = tree_files[:idx+1]
                    selected_tree_files = self.db.filesInTree(root_dir_id, None, file_creation_date)
                    self.assertEqual(len(expected_selected_tree_files), len(selected_tree_files))
                    selected_tree_files_ids = set([f['file_id'] for f in selected_tree_files])
                    for expected_file in expected_selected_tree_files:
                        self.assertTrue(expected_file['file_id'] in selected_tree_files_ids)

                    # and check the totals as well
                    tree_totals = self.db.totalFileSizeAndNumFilesInTree(root_dir_id, None, file_creation_date)
                    self.assertEqual(len(expected_selected_tree_files), tree_totals['tree_num_files'])
                    self.assertEqual(sum(f['file_size'] for f in expected_selected_tree_files), tree_totals['tree_total_file_size'])

# run tests if main
if __name__ == '__main__':
    unittest.main()
