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

import logging
from datetime import datetime, timedelta

from lofar.lta.ltastorageoverview import store
from lofar.common.datetimeutils import totalSeconds
from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin

logger = logging.getLogger()

class LTAStorageDbTestInstance():
    '''Helper class which uses the LTAStorageDbTestMixin without a unittest.TestCase to setup/teardown a test LTAStorageDb instance'''
    def __init__(self):
        self._db_creator = LTAStorageDbTestMixin()

    @property
    def dbcreds(self):
        return self._db_creator.dbcreds

    def __enter__(self):
        self._db_creator.setUpClass()
        self._db_creator.setUp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db_creator.tearDownClass()


def main():
    from optparse import OptionParser
    from lofar.common import dbcredentials

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='execute a performance test by inserting many files on an empty test database.')
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    with LTAStorageDbTestInstance() as test_db:
        base_date = datetime.utcnow()

        db = store.LTAStorageDb(test_db.dbcreds)

        db.insertSiteIfNotExists('sara', 'srm://srm.siteA.nl:8444')
        rootdir_id = db.insertRootDirectory('sara', '/pnfs/grid.siteA.nl/data/lofar/ops')
        projects_dir_id = db.insertSubDirectory('/pnfs/grid.siteA.nl/data/lofar/ops/projects', rootdir_id)

        total_num_files_inserted = 0

        with open('db_perf.csv', 'w') as file:
            for cycle_nr in range(1, 10):
                for project_nr in range(1, 10):
                    # project_name = 'lc%d_%03d/%d' % (cycle_nr, project_nr, os.getpid())
                    project_name = 'lc%d_%03d' % (cycle_nr, project_nr)
                    projectdir_id = db.insertSubDirectory('/pnfs/grid.siteA.nl/data/lofar/ops/projects/%s' % (project_name,), projects_dir_id)

                    obs_base_id = cycle_nr*100000+project_nr*1000
                    for obs_nr, obsId in enumerate(range(obs_base_id, obs_base_id+20)):
                        obsName = 'L%s' % obsId

                        obsdir_id = db.insertSubDirectory('/pnfs/grid.siteA.nl/data/lofar/ops/projects/%s/%s' % (project_name, obsName), projectdir_id)

                        fileinfos = [('%s_SB%3d' % (obsName, sbNr), 1000+sbNr+project_nr*cycle_nr, base_date + timedelta(days=10*cycle_nr+project_nr, minutes=obs_nr, seconds=sbNr), obsdir_id) for sbNr in range(0, 2)]
                        now = datetime.utcnow()
                        file_ids = db.insertFileInfos(fileinfos)
                        total_num_files_inserted += len(file_ids)
                        elapsed = totalSeconds(datetime.utcnow() - now)
                        line = '%s,%s' % (total_num_files_inserted, elapsed)
                        print(line)
                        file.write(line + '\n')

if __name__ == "__main__":
    main()

