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
import os, os.path

from lofar.common.testing.postgres import PostgresTestDatabaseInstance, PostgresTestMixin, PostgresDatabaseConnection
from lofar.lta.ltastorageoverview import store
logger = logging.getLogger(__name__)

class LTAStorageDbTestInstance(PostgresTestDatabaseInstance):
    def apply_database_schema(self):
        create_script_path = os.path.normpath(os.path.join(os.environ['LOFARROOT'], 'share', 'ltaso', 'create_db_ltastorageoverview.sql'))
        logger.info('  running ltaso create script create_script=%s', create_script_path)
        with open(create_script_path, 'r') as script:
            with PostgresDatabaseConnection(self.dbcreds) as db:
                db.executeQuery(script.read())

    def create_database_connection(self) -> store.LTAStorageDb:
        return store.LTAStorageDb(self.dbcreds)

class LTAStorageDbTestMixin(PostgresTestMixin):
    @classmethod
    def create_test_db_instance(cls) -> PostgresTestDatabaseInstance:
        return LTAStorageDbTestInstance()

    def setUp(self):
        # wipe all tables by truncating some which cascades into the rest.
        logger.debug("setUp: Wiping tables for each unittest.")
        self.db.executeQuery("TRUNCATE TABLE lta.site CASCADE;")
        self.db.commit()
