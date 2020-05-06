#!/usr/bin/env python3

# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id$

'''
Module with nice postgres helper methods and classes.
'''

import logging
from threading import Thread, Lock
from queue import Queue, Empty
from datetime import  datetime, timedelta
import collections
import time
import re
import select
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from lofar.common.util import single_line_with_single_spaces
from lofar.common.datetimeutils import totalSeconds
from lofar.common.dbcredentials import DBCredentials

logger = logging.getLogger(__name__)

def makePostgresNotificationQueries(schema, table, action, column_name='id'):
    action = action.upper()
    if action not in ('INSERT', 'UPDATE', 'DELETE'):
        raise ValueError('''trigger_type '%s' not in ('INSERT', 'UPDATE', 'DELETE')''' % action)

    change_name = '''{table}_{action}'''.format(table=table, action=action)
    if column_name != 'id':
        change_name += '_column_' + column_name
    function_name = '''NOTIFY_{change_name}'''.format(change_name=change_name)
    function_sql = '''
    CREATE OR REPLACE FUNCTION {schema}.{function_name}()
    RETURNS TRIGGER AS $$
    DECLARE payload text;
    BEGIN
    {begin_update_check}SELECT CAST({column_value} AS text) INTO payload;
    PERFORM pg_notify(CAST('{change_name}' AS text), payload);{end_update_check}
    RETURN {value};
    END;
    $$ LANGUAGE plpgsql;
    '''.format(schema=schema,
                function_name=function_name,
                table=table,
                action=action,
                column_value=('OLD' if action == 'DELETE' else 'NEW') + '.' + column_name,
                value='OLD' if action == 'DELETE' else 'NEW',
                change_name=change_name.lower(),
                begin_update_check='IF ROW(NEW.*) IS DISTINCT FROM ROW(OLD.*) THEN\n' if action == 'UPDATE' else '',
                end_update_check='\nEND IF;' if action == 'UPDATE' else '')

    trigger_name = 'T_%s' % function_name

    trigger_sql = '''
    CREATE TRIGGER {trigger_name}
    AFTER {action} ON {schema}.{table}
    FOR EACH ROW
    EXECUTE PROCEDURE {schema}.{function_name}();
    '''.format(trigger_name=trigger_name,
                function_name=function_name,
                schema=schema,
                table=table,
                action=action)

    drop_sql = '''
    DROP TRIGGER IF EXISTS {trigger_name} ON {schema}.{table} CASCADE;
    DROP FUNCTION IF EXISTS {schema}.{function_name}();
    '''.format(trigger_name=trigger_name,
               function_name=function_name,
               schema=schema,
               table=table)

    sql = drop_sql + '\n' + function_sql + '\n' + trigger_sql
    sql_lines = '\n'.join([s.strip() for s in sql.split('\n')]) + '\n'
    return sql_lines

FETCH_NONE=0
FETCH_ONE=1
FETCH_ALL=2

class PostgresDBError(Exception):
    pass

class PostgresDBConnectionError(PostgresDBError):
    pass

class PostgresDBQueryExecutionError(PostgresDBError):
    pass

class PostgresDatabaseConnection:
    def __init__(self,
                 dbcreds: DBCredentials,
                 auto_commit_selects: bool=False,
                 num_connect_retries: int=5,
                 connect_retry_interval: float=1.0,
                 query_timeout: float=3600):
        self._dbcreds = dbcreds
        self._connection = None
        self._cursor = None
        self.__auto_commit_selects = auto_commit_selects
        self.__num_connect_retries = num_connect_retries
        self.__connect_retry_interval = connect_retry_interval
        self.__query_timeout = query_timeout

    def connect_if_needed(self):
        if not self.is_connected:
            self.connect()

    def connect(self):
        if self.is_connected:
            logger.debug("already connected to database: %s", self)
            return

        for retry_cntr in range(self.__num_connect_retries+1):
            try:
                logger.debug("connecting to database: %s", self)

                self._connection = psycopg2.connect(host=self._dbcreds.host,
                                                    user=self._dbcreds.user,
                                                    password=self._dbcreds.password,
                                                    database=self._dbcreds.database,
                                                    port=self._dbcreds.port,
                                                    connect_timeout=5)

                if self._connection:
                    self._cursor = self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

                    logger.info("connected to database: %s", self)

                    # see http://initd.org/psycopg/docs/connection.html#connection.notices
                    # try to set the notices attribute with a non-list collection,
                    # so we can log more than 50 messages. Is only available since 2.7, so encapsulate in try/except.
                    try:
                        self._connection.notices = collections.deque()
                    except TypeError:
                        logger.warning("Cannot overwrite self._connection.notices with a deque... only max 50 notifications available per query. (That's ok, no worries.)")

                    # we have a proper connection, so return
                    return
            except psycopg2.DatabaseError as dbe:
                error_string = single_line_with_single_spaces(dbe)
                logger.error(error_string)

                if self._is_recoverable_connection_error(dbe):
                    # try to reconnect on connection-like-errors
                    if retry_cntr == self.__num_connect_retries:
                        raise PostgresDBConnectionError("Error while connecting to %s. error=%s" % (self, error_string))

                    logger.info('retrying to connect to %s in %s seconds', self.database, self.__connect_retry_interval)
                    time.sleep(self.__connect_retry_interval)
                else:
                    # non-connection-error, raise generic PostgresDBError
                    raise PostgresDBError(error_string)

    def disconnect(self):
        if self._connection is not None or self._cursor is not None:
            logger.debug("disconnecting from database: %s", self)

            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None

            if self._connection is not None:
                self._connection.close()
                self._connection = None

            logger.info("disconnected from database: %s", self)

    def _is_recoverable_connection_error(self, error: psycopg2.DatabaseError) -> bool:
        '''test if psycopg2.DatabaseError is a recoverable connection error'''
        if isinstance(error, psycopg2.OperationalError) and re.search('connection', str(error), re.IGNORECASE):
            return True

        if error.pgcode is not None:
            # see https://www.postgresql.org/docs/current/errcodes-appendix.html#ERRCODES-TABLE
            if error.pgcode.startswith('08') or error.pgcode.startswith('57P') or error.pgcode.startswith('53'):
                return True

        return False

    def __str__(self) -> str:
        '''returns the class name and connection string with hidden password.'''
        return "%s %s" % (self.__class__.__name__, self._dbcreds.stringWithHiddenPassword())

    @property
    def database(self) -> str:
        '''returns the database name'''
        return self._dbcreds.database

    @property
    def dbcreds(self) -> DBCredentials:
        '''returns the database credentials'''
        return self._dbcreds

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.closed==0

    def reconnect(self):
        logger.info("reconnecting %s", self)
        self.disconnect()
        self.connect()

    def __enter__(self):
        '''connects to the database'''
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''disconnects from the database'''
        self.disconnect()

    @staticmethod
    def _queryAsSingleLine(query, qargs=None):
        line = ' '.join(single_line_with_single_spaces(query).split())
        if qargs:
            line = line % tuple(['\'%s\'' % a if isinstance(a, str) else a for a in qargs])
        return line

    def executeQuery(self, query, qargs=None, fetch=FETCH_NONE):
        start = datetime.utcnow()
        while True:
            try:
                return self._do_execute_query(query, qargs, fetch)
            except PostgresDBConnectionError as e:
                logger.warning(e)
                if datetime.utcnow() - start < timedelta(seconds=self.__query_timeout):
                    try:
                        # reconnect, log retrying..., and do the retry in the next loop iteration
                        self.reconnect()
                        logger.info("retrying %s", self._queryAsSingleLine(query, qargs))
                    except PostgresDBConnectionError as ce:
                        logger.warning(ce)
                else:
                    raise

    def _do_execute_query(self, query, qargs=None, fetch=FETCH_NONE):
        '''execute the query and reconnect upon OperationalError'''
        query_log_line = self._queryAsSingleLine(query, qargs)

        try:
            self.connect_if_needed()

            # log
            logger.debug('executing query: %s', query_log_line)

            # execute (and time it)
            start = datetime.utcnow()
            self._cursor.execute(query, qargs)
            elapsed = datetime.utcnow() - start
            elapsed_ms = 1000.0 * totalSeconds(elapsed)

            # log execution result
            logger.info('executed query in %.1fms%s yielding %s rows: %s', elapsed_ms,
                                                                           ' (SLOW!)' if elapsed_ms > 250 else '', # for easy log grep'ing
                                                                           self._cursor.rowcount,
                                                                           query_log_line)

            # log any notifications from within the database itself
            self._log_database_notifications()

            self._commit_selects_if_needed(query)

            # fetch and return results
            if fetch == FETCH_ONE:
                row = self._cursor.fetchone()
                return dict(row) if row is not None else None
            if fetch == FETCH_ALL:
                return [dict(row) for row in self._cursor.fetchall() if row is not None]
            return []

        except psycopg2.OperationalError as oe:
            if self._is_recoverable_connection_error(oe):
                raise PostgresDBConnectionError("Could not execute query due to connection errors. '%s' error=%s" %
                                                (query_log_line,
                                                 single_line_with_single_spaces(oe)))
            else:
                self._log_error_rollback_and_raise(oe, query_log_line)

        except Exception as e:
            self._log_error_rollback_and_raise(e, query_log_line)

    def _log_error_rollback_and_raise(self, e: Exception, query_log_line: str):
        self._log_database_notifications()
        error_string = single_line_with_single_spaces(e)
        logger.error("Rolling back query=\'%s\' due to error: \'%s\'" % (query_log_line, error_string))
        self.rollback()
        if isinstance(e, PostgresDBError):
            # just re-raise our PostgresDBError
            raise
        else:
            # wrap original error in PostgresDBQueryExecutionError
            raise PostgresDBQueryExecutionError("Could not execute query '%s' error=%s" % (query_log_line, error_string))

    def _commit_selects_if_needed(self, query):
        if self.__auto_commit_selects and re.search('select', query, re.IGNORECASE):
            # prevent dangling in idle transaction on server
            self.commit()

    def _log_database_notifications(self):
        try:
            if self._connection.notices:
                for notice in self._connection.notices:
                    logger.info('database log message %s', notice.strip())
                if isinstance(self._connection.notices, collections.deque):
                    self._connection.notices.clear()
                else:
                    del self._connection.notices[:]
        except Exception as e:
            logger.error(str(e))

    def commit(self):
        if self.is_connected:
            logger.info('commit')
            self._connection.commit()

    def rollback(self):
        if self.is_connected:
            logger.info('rollback')
            self._connection.rollback()


class PostgresListener(PostgresDatabaseConnection):
    ''' This class lets you listen to postgress notifications
    It execute callbacks when a notifocation occurs.
    Make your own subclass with your callbacks and subscribe them to the appriate channel.
    Example:

    class MyListener(PostgresListener):
        def __init__(self, host, database, username, password):
            super(MyListener, self).__init__(host=host, database=database, username=username, password=password)
            self.subscribe('foo', self.foo)
            self.subscribe('bar', self.bar)

        def foo(self, payload = None):
            print "Foo called with payload: ", payload

        def bar(self, payload = None):
            print "Bar called with payload: ", payload

    with MyListener(...args...) as listener:
        #either listen like below in a loop doing stuff...
        while True:
            #do stuff or wait,
            #the listener calls the callbacks meanwhile in another thread

        #... or listen like below blocking
        #while the listener calls the callbacks meanwhile in this thread
        listener.waitWhileListening()
    '''
    def __init__(self, dbcreds: DBCredentials):
        '''Create a new PostgresListener'''
        super(PostgresListener, self).__init__(dbcreds=dbcreds,
                                               auto_commit_selects=True)
        self.__listening = False
        self.__lock = Lock()
        self.__callbacks = {}
        self.__waiting = False
        self.__queue = Queue()

    def connect(self):
        super(PostgresListener, self).connect()
        self._connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def subscribe(self, notification, callback):
        '''Subscribe to a certain postgres notification.
        Call callback method in case such a notification is received.'''
        logger.info("Subscribed %sto %s" % ('and listening ' if self.isListening() else '', notification))
        with self.__lock:
            self.executeQuery("LISTEN %s;", (psycopg2.extensions.AsIs(notification),))
            self.__callbacks[notification] = callback

    def unsubscribe(self, notification):
        '''Unubscribe from a certain postgres notification.'''
        logger.info("Unsubscribed from %s" % notification)
        with self.__lock:
            self.executeQuery("UNLISTEN %s;", (psycopg2.extensions.AsIs(notification),))
            if notification in self.__callbacks:
                del self.__callbacks[notification]

    def isListening(self):
        '''Are we listening? Has the listener been started?'''
        with self.__lock:
            return self.__listening

    def start(self):
        '''Start listening. Does nothing if already listening.
        When using the listener in a context start() and stop()
        are called upon __enter__ and __exit__

        This method return immediately.
        Listening and calling callbacks takes place on another thread.
        If you want to block processing and call the callbacks on the main thread,
        then call waitWhileListening() after start.
        '''
        if self.isListening():
            return

        self.connect()

        logger.info("Started listening to %s" % ', '.join([str(x) for x in list(self.__callbacks.keys())]))

        def eventLoop():
            while self.isListening():
                if select.select([self._connection],[],[],2) != ([],[],[]):
                    self._connection.poll()
                    while self._connection.notifies:
                        try:
                            notification = self._connection.notifies.pop(0)
                            logger.debug("Received notification on channel %s payload %s" % (notification.channel, notification.payload))

                            if self.isWaiting():
                                # put notification on Queue
                                # let waiting thread handle the callback
                                self.__queue.put((notification.channel, notification.payload))
                            else:
                                # call callback on this listener thread
                                self._callCallback(notification.channel, notification.payload)
                        except Exception as e:
                            logger.error(str(e))

        self.__thread = Thread(target=eventLoop)
        self.__thread.daemon = True
        self.__listening = True
        self.__thread.start()

    def stop(self):
        '''Stop listening. (Can be restarted)'''
        with self.__lock:
            if not self.__listening:
                return
            self.__listening = False

        self.__thread.join()
        self.__thread = None

        logger.info("Stopped listening")
        self.stopWaiting()
        self.disconnect()

    def __enter__(self):
        '''starts the listener upon contect enter'''
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''stops the listener upon contect enter'''
        self.stop()

    def _callCallback(self, channel, payload = None):
        '''call the appropiate callback based on channel'''
        try:
            callback = None
            with self.__lock:
                if channel in self.__callbacks:
                    callback = self.__callbacks[channel]

            if callback:
                if payload:
                    callback(payload)
                else:
                    callback()
        except Exception as e:
            logger.error(str(e))

    def isWaiting(self):
        '''Are we waiting in the waitWhileListening() method?'''
        with self.__lock:
            return self.__waiting

    def stopWaiting(self):
        '''break from the blocking waitWhileListening() method'''
        with self.__lock:
            if self.__waiting:
                self.__waiting = False
                logger.info("Continuing from blocking waitWhileListening")

    def waitWhileListening(self):
        '''
        block calling thread until interrupted or
        until stopWaiting is called from another thread
        meanwhile, handle the callbacks on this thread
        '''
        logger.info("Waiting while listening to %s" % ', '.join([str(x) for x in list(self.__callbacks.keys())]))

        with self.__lock:
            self.__waiting = True

        while self.isWaiting():
            try:
                notification = self.__queue.get(True, 1)
                channel = notification[0]
                payload = notification[1]

                self._callCallback(channel, payload)
            except KeyboardInterrupt:
                # break
                break
            except Empty:
                pass

        self.stopWaiting()

