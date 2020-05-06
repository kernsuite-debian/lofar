#!/usr/bin/env python3

import unittest
from unittest import mock
from lofar.common.postgres import *
from lofar.common.testing.postgres import PostgresTestDatabaseInstance, PostgresTestMixin
import psycopg2
import signal
from copy import deepcopy

import logging
logger = logging.getLogger(__name__)

class MyPostgresTestDatabaseInstance(PostgresTestDatabaseInstance):
    def apply_database_schema(self):
        # use 'normal' psycopg2 API to connect and setup the database,
        # not the PostgresDatabaseConnection class, because that's the object-under-test.
        logger.debug("connecting to %s test-postgres-database-instance...", self.dbcreds.stringWithHiddenPassword())
        with psycopg2.connect(**self.dbcreds.psycopg2_connect_options()) as connection:
            with connection.cursor() as cursor:
                logger.debug("creating database user and tables in %s test-postgres-database-instance...", self.dbcreds.stringWithHiddenPassword())
                cursor.execute("CREATE TABLE IF NOT EXISTS foo (id serial NOT NULL, bar text NOT NULL, PRIMARY KEY (id));")
                connection.commit()

class MyPostgresTestMixin(PostgresTestMixin):
    @classmethod
    def create_test_db_instance(cls) -> PostgresTestDatabaseInstance:
        return MyPostgresTestDatabaseInstance()


class TestPostgres(MyPostgresTestMixin, unittest.TestCase):
    def test_connection_error_with_incorrect_dbcreds(self):
        #connect to incorrect port -> should result in PostgresDBConnectionError
        incorrect_dbcreds = deepcopy(self.dbcreds)
        incorrect_dbcreds.port += 1

        # test if connecting fails
        with mock.patch('lofar.common.postgres.logger') as mocked_logger:
            with self.assertRaises(PostgresDBConnectionError):
                NUM_CONNECT_RETRIES = 2
                with PostgresDatabaseConnection(dbcreds=incorrect_dbcreds, connect_retry_interval=0.1, num_connect_retries=NUM_CONNECT_RETRIES) as db:
                    pass

            # check logging
            self.assertEqual(NUM_CONNECT_RETRIES, len([ca for ca in mocked_logger.info.call_args_list if 'retrying to connect' in ca[0][0]]))
            self.assertEqual(NUM_CONNECT_RETRIES+1, len([ca for ca in mocked_logger.debug.call_args_list if 'connecting to database' in ca[0][0]]))
            self.assertEqual(NUM_CONNECT_RETRIES+1, len([ca for ca in mocked_logger.error.call_args_list if 'could not connect' in ca[0][0]]))

    def test_reconnect_on_connection_loss(self):

        # define a helper class on top of the normal PostgresDatabaseConnection
        # which is able to restart the testing-pginstance after the first reconnect attempt (for testing purposes)
        # the object under test is still the  PostgresDatabaseConnection!
        class HelperPostgresDatabaseConnection(PostgresDatabaseConnection):
            def __init__(self, dbcreds: DBCredentials, pginstance):
                super().__init__(dbcreds, num_connect_retries=1, connect_retry_interval=.1, query_timeout=2)
                self.pginstance = pginstance
                self.reconnect_was_called = False

            def reconnect(self):
                # do normal reconnect (won't work because the pginstance is stopped...)
                try:
                    super().reconnect()
                #ignore any exceptions here, should be handled by the normal PostgresDatabaseConnection
                finally:
                    self.reconnect_was_called = True
                    if not self.pginstance.is_alive():
                        # restart the pginstance, so any next reconnect will work
                        logger.info("restarting test-postgres-database-instance...")
                        self.pginstance.start()
                        logger.info("restarted test-postgres-database-instance")

        with HelperPostgresDatabaseConnection(dbcreds=self.dbcreds, pginstance=self._test_db_instance._postgresql) as db:
            # insert some test data
            db.executeQuery("INSERT INTO foo (bar) VALUES ('my_value');")
            db.commit()

            # do normal select query, should work.
            result = db.executeQuery("SELECT * from foo;", fetch=FETCH_ALL)
            self.assertEqual([{'id':1, 'bar': 'my_value'}], result)

            # terminate the pginstance (simulating a production database malfunction)
            logger.info("terminating %s test-postgres-database-instance...", self.dbcreds.stringWithHiddenPassword())
            self._test_db_instance._postgresql.terminate(signal.SIGTERM)
            logger.info("terminated %s test-postgres-database-instance", self.dbcreds.stringWithHiddenPassword())

            # prove that the database is down by trying to connect which results in a PostgresDBConnectionError
            with self.assertRaises(PostgresDBConnectionError):
                with PostgresDatabaseConnection(dbcreds=self.dbcreds, num_connect_retries=0):
                    pass

            # do normal select query on our original connection again (even though the database itself is down)
            # should work anyway, because the executeQuery tries to reconnect,
            # and our helper class restarts the database server after the first reconnect attempt.
            result2 = db.executeQuery("SELECT * from foo;", fetch=FETCH_ALL)
            self.assertEqual([{'id':1, 'bar': 'my_value'}], result2)
            self.assertTrue(db.reconnect_was_called)

    def test_handling_of_database_exceptions(self):
        with PostgresDatabaseConnection(dbcreds=self.dbcreds) as db:

            db.executeQuery('''CREATE OR REPLACE FUNCTION error_func() RETURNS void AS
                               $BODY$
                               BEGIN
                               RAISE EXCEPTION 'something is very wrong';
                               END;
                               $BODY$ LANGUAGE plpgsql VOLATILE;''')

            with self.assertRaises(PostgresDBQueryExecutionError):
                db.executeQuery("SELECT * FROM error_func();")


logging.basicConfig(format='%(asctime)s %(process)s %(threadName)s %(levelname)s %(message)s', level=logging.DEBUG)

if __name__ == "__main__":
    unittest.main()
