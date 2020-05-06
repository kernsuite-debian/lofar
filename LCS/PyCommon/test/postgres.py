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
import psycopg2
import os, sys
import logging

logger = logging.getLogger(__name__)

import testing.postgresql
from lofar.common.dbcredentials import Credentials
from lofar.common.postgres import PostgresDatabaseConnection

class PostgresTestDatabaseInstance():
    ''' A helper class which instantiates a running postgres server (not interfering with any other test/production postgres servers)
    Best used in a 'with'-context so the server is destroyed automagically.
    Derive your own sub-class and implement apply_database_schema with your own sql schema to setup your type of database.
    '''

    def __init__(self, user_name: str = 'test_user') -> None:
        self._postgresql = None
        self.dbcreds = Credentials()
        self.dbcreds.user = user_name
        self.dbcreds.password = 'test_password'  # cannot be empty...

    def __enter__(self):
        '''create/instantiate the postgres server'''
        try:
            self.create()
        except Exception as e:
            logger.exception(e)
            self.destroy()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''destroy the running postgres server'''
        self.destroy()

    def create(self):
        '''instantiate the isolated postgres server'''
        logger.info('creating test-database instance...')

        self._postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)()

        # fill credentials with the dynamically created postgress instance (e.g. port changes for each time)
        self.dbcreds.host = self._postgresql.dsn()['host']
        self.dbcreds.database = self._postgresql.dsn()['database']
        self.dbcreds.port = self._postgresql.dsn()['port']

        try:
            # connect to db as root
            conn = psycopg2.connect(**self._postgresql.dsn())
            cursor = conn.cursor()

            # create user role
            query = "CREATE USER %s WITH SUPERUSER PASSWORD '%s'" % (self.dbcreds.user, self.dbcreds.password)
            cursor.execute(query)

            logger.info('Created test-database instance. It is avaiblable at: %s', self.dbcreds.stringWithHiddenPassword())
        finally:
            cursor.close()
            conn.commit()
            conn.close()

        logger.info('Applying test-database schema...')
        self.apply_database_schema()

    def destroy(self):
        '''destroy the running postgres server'''
        try:
            if self._postgresql:
                logger.info('removing test-database instance at %s', self.dbcreds.stringWithHiddenPassword())
                self._postgresql.stop()
                logger.info('test-database instance removed')
        except Exception as e:
            logger.info('error while removing test-database instance at %s: %s', self.dbcreds.stringWithHiddenPassword(), e)

    def apply_database_schema(self):
        ''' Override and implement this method. Open a connection to the database specified by self.dbcreds, and apply your database's sql schema.'''
        raise NotImplementedError("Please override PostgresTestDatabaseInstance.apply_database_schema and setup your database with an sql schema.")

    def create_database_connection(self) -> PostgresDatabaseConnection:
        ''' Factory method to create a PostgresDatabaseConnection to the testing-database.
        Override and implement this method if you want to use your PostgresDatabaseConnection-subclass using the given self.dbcreds, and return it.
        Note: you should connect/disconnect the connection yourself, so recommended usage is in a 'with'-context'''
        return PostgresDatabaseConnection(self.dbcreds)

    def print_database_instance_log(self):
        '''print the log of the testing-database instance (can help debugging sql statements)'''
        try:
            if self._postgresql:
                db_log_file_name = os.path.join(self._postgresql.base_dir, '%s.log' % self._postgresql.name)
                logger.info('Printing test-postgress-database server log for reference: %s', db_log_file_name)
                with open(db_log_file_name, 'r') as db_log_file:
                    for line in db_log_file.readlines():
                        print("  postgres log: %s" % line.strip(), file=sys.stderr)
        except Exception as e:
            logger.error("Error while printing test-postgress-database server log: %s", e)

class PostgresTestMixin():
    '''
    A common test mixin class from which you can/should derive to get a freshly setup postgres testing instance with your sql setup scripts applied.
    It implements the unittest setUpClass/tearDownClass methods and uses them as a template method pattern to do all the testing-database setup/teardown work for you.
    '''

    # class variables are initialized in setUpClass
    _test_db_instance  = None
    db                 = None

    @classmethod
    def create_test_db_instance (cls) -> PostgresTestDatabaseInstance:
        raise NotImplementedError("Please implement create_test_db_instance in your subclass and return your preferred PostgresTestDatabaseInstance-subclass")

    @classmethod
    def setUpClass(cls):
        # create a running isolated test database instance
        cls._test_db_instance = cls.create_test_db_instance()
        cls._test_db_instance.create()

        # create a single PostgresDatabaseConnection for the entire test suite
        logger.info('Creating PostgresDatabaseConnection to test-database...')
        cls.db = cls._test_db_instance.create_database_connection()
        cls.db.connect()
        logger.info('PostgresDatabaseConnection to test-database %s is ready to be used.', cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.disconnect()
        cls._test_db_instance.print_database_instance_log()
        cls._test_db_instance.destroy()

    @property
    def dbcreds(self) -> Credentials:
        return self._test_db_instance.dbcreds
