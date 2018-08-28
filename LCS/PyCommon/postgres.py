#!/usr/bin/python

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
from Queue import Queue, Empty
from datetime import  datetime
import time
import re
import select
import psycopg2
import psycopg2.extras
import psycopg2.extensions
from lofar.common.datetimeutils import totalSeconds
from lofar.common import dbcredentials

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

class PostgresDatabaseConnection(object):
    def __init__(self,
                 host='',
                 database='',
                 username='',
                 password='',
                 port=5432,
                 log_queries=False, auto_commit_selects=True, num_connect_retries=5, connect_retry_interval=1.0):
        self._host = host
        self._database = database
        self._username = username
        self._password = password
        self._port = port
        self._connection = None
        self._log_queries = log_queries
        self.__connection_retries = 0
        self.__auto_commit_selects = auto_commit_selects
        self.__num_connect_retries = num_connect_retries
        self.__connect_retry_interval = connect_retry_interval
        self._connect()

    def _connect(self):
        for i in range(self.__num_connect_retries):
            try:
                self._disconnect()

                logger.debug("%s connecting to db %s:*****@%s on %s:%s", type(self).__name__,
                             self._username,
                             self._database,
                             self._host,
                             self._port)
                self._connection = psycopg2.connect(host=self._host,
                                                    user=self._username,
                                                    password=self._password,
                                                    database=self._database,
                                                    port=self._port,
                                                    connect_timeout=5)

                if self._connection:
                    logger.debug("%s connected to db %s", type(self).__name__, self._database)
                    return
            except Exception as e:
                logger.error(e)
                if i == self.__num_connect_retries-1:
                    raise

                logger.debug('retrying to connect to %s in %s seconds', self._database, self.__connect_retry_interval)
                time.sleep(self.__connect_retry_interval)

    def _disconnect(self):
        if self._connection:
            logger.debug("%s disconnecting from db: %s", type(self).__name__, self._database)
            self._connection.close()
            self._connection = None

    def __enter__(self):
        '''connects to the database'''
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''disconnects from the database'''
        self._disconnect()

    def _queryAsSingleLine(self, query, qargs=None):
        line = ' '.join(query.replace('\n', ' ').split())
        if qargs:
            line = line % tuple(['\'%s\'' % a if isinstance(a, basestring) else a for a in qargs])
        return line

    def executeQuery(self, query, qargs=None, fetch=FETCH_NONE):
        '''execute the query and reconnect upon OperationalError'''
        try:
            with self._connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
                start = datetime.utcnow()
                cursor.execute(query, qargs)
                if self._log_queries:
                    elapsed = datetime.utcnow() - start
                    elapsed_ms = 1000.0 * totalSeconds(elapsed)
                    logger.info('executed query in %.1fms%s yielding %s rows: %s', elapsed_ms,
                                                                                   ' (SLOW!)' if elapsed_ms > 250 else '', # for easy log grep'ing
                                                                                   cursor.rowcount,
                                                                                   self._queryAsSingleLine(query, qargs))

                try:
                    self._log_database_notifications()

                    result = []
                    if fetch == FETCH_ONE:
                        result = cursor.fetchone()

                    if fetch == FETCH_ALL:
                        result = cursor.fetchall()

                    if self.__auto_commit_selects and re.search('select', query, re.IGNORECASE):
                        #prevent dangling in idle transaction on server
                        self.commit()

                    return result
                except Exception as e:
                    logger.error("error while fetching result(s) for %s: %s", self._queryAsSingleLine(query, qargs), e)

        except (psycopg2.OperationalError, AttributeError) as e:
            logger.error(str(e))
            while self.__connection_retries < 5:
                logger.info("(re)trying to connect to database")
                self.__connection_retries += 1
                self._connect()
                if self._connection:
                    self.__connection_retries = 0
                    return self.executeQuery(query, qargs, fetch)
                time.sleep(i*i)
        except (psycopg2.IntegrityError, psycopg2.ProgrammingError, psycopg2.InternalError, psycopg2.DataError)as e:
            logger.error("Rolling back query=\'%s\' due to error: \'%s\'" % (self._queryAsSingleLine(query, qargs), e))
            self.rollback()
            return []
        except Exception as e:
            logger.error(str(e))

        return []

    def _log_database_notifications(self):
        if self._log_queries and self._connection.notices:
            for notice in self._connection.notices:
                logger.info('database log message %s', notice.strip())
        del self._connection.notices[:]

    def commit(self):
        if self._log_queries:
            logger.debug('commit')
        self._connection.commit()

    def rollback(self):
        if self._log_queries:
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
    def __init__(self,
                 host='',
                 database='',
                 username='',
                 password='',
                 port=5432):
        '''Create a new PostgresListener'''
        super(PostgresListener, self).__init__(host=host,
                                               database=database,
                                               username=username,
                                               password=password,
                                               port=port)
        self.__listening = False
        self.__lock = Lock()
        self.__callbacks = {}
        self.__waiting = False
        self.__queue = Queue()

    def _connect(self):
        super(PostgresListener, self)._connect()
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

        logger.info("Started listening to %s" % ', '.join([str(x) for x in self.__callbacks.keys()]))

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
        logger.info("Waiting while listening to %s" % ', '.join([str(x) for x in self.__callbacks.keys()]))

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

