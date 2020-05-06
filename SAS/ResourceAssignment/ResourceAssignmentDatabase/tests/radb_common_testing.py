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
import unittest
import psycopg2
import os, sys
from datetime import datetime, timedelta
from dateutil import parser
import logging

logger = logging.getLogger(__name__)

from lofar.common.postgres import PostgresDatabaseConnection, FETCH_ALL
from lofar.common.testing.postgres import PostgresTestMixin, PostgresTestDatabaseInstance
from lofar.sas.resourceassignment.database.radb import RADatabase

class RADBTestDatabaseInstance(PostgresTestDatabaseInstance):
    '''
    '''

    def __init__(self) -> None:
        super().__init__(user_name='resourceassignment')

    def apply_database_schema(self):
        logger.info('applying RADB sql schema to %s', self.dbcreds)

        with PostgresDatabaseConnection(self.dbcreds) as db:
            # populate db tables
            # These are applied in given order to set up test db
            # Note: cannot use create_and_populate_database.sql since '\i' is not understood by cursor.execute()
            sql_basepath = os.environ['LOFARROOT'] + "/share/radb/sql/"
            sql_createdb_paths = [sql_basepath + "create_database.sql",
                                  sql_basepath + "/add_resource_allocation_statics.sql",
                                  sql_basepath + "/add_virtual_instrument.sql",
                                  sql_basepath + "/add_notifications.sql",
                                  sql_basepath + "/add_functions_and_triggers.sql"]

            for sql_path in sql_createdb_paths:
                logger.debug("setting up database. applying sql file: %s", sql_path)
                with open(sql_path) as sql:
                    db.executeQuery(sql.read())
                    db.commit()

    def create_database_connection(self) -> RADatabase:
        self.radb = RADatabase(self.dbcreds)
        return self.radb


class RADBCommonTestMixin(PostgresTestMixin):
    '''
    A common test mixin class from which you can derive to get a freshly setup postgres testing instance with the latest RADB sql setup scripts applied.
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.radb = cls.db

    def setUp(self):
        # wipe all tables by truncating specification which cascades into the rest.
        logger.debug("setUp: Wiping radb tables for each unittest.")
        self.db.executeQuery("TRUNCATE TABLE resource_allocation.specification CASCADE;")
        self.db.executeQuery("TRUNCATE TABLE resource_allocation.resource_usage CASCADE;")
        self.db.executeQuery("TRUNCATE TABLE resource_allocation.resource_usage_delta CASCADE;")
        self.db.commit()

    @classmethod
    def create_test_db_instance(cls) -> RADBTestDatabaseInstance:
        return RADBTestDatabaseInstance()


class RADBCommonTest(RADBCommonTestMixin, unittest.TestCase):
    # database created?
    def test_select_tables_contains_tables_for_each_schema(self):
        with PostgresDatabaseConnection(self.dbcreds) as connection:
            query = "SELECT table_schema,table_name FROM information_schema.tables"
            result = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue('resource_allocation' in str(result))
            self.assertTrue('resource_monitoring' in str(result))
            self.assertTrue('virtual_instrument' in str(result))

    # resource allocation_statics there?
    def test_select_task_types_contains_obervation(self):
        with PostgresDatabaseConnection(self.dbcreds) as connection:
            query = "SELECT * FROM resource_allocation.task_type"
            result = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue('observation' in str(result))

    # virtual instrument there?
    def test_select_virtualinstrument_units_contain_rcuboard(self):
        with PostgresDatabaseConnection(self.dbcreds) as connection:
            query = "SELECT * FROM virtual_instrument.unit"
            result = connection.executeQuery(query, fetch=FETCH_ALL)
            self.assertTrue('rcu_board' in str(result))

__all__ = ['RADBCommonTestMixin']

if __name__ == "__main__":
    os.environ['TZ'] = 'UTC'
    logging.basicConfig(format = '%(asctime)s %(levelname)s %(message)s', level = logging.INFO)
    unittest.main()
