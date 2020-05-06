# threading_utils.py: test utils for lofar software
#
# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
#
"""
This module contains various utilities/methods that are common for LOFAR threading usage
"""

import threading
import contextlib
import logging

logger = logging.getLogger(__name__)

class TimeoutLock:
    """
    A TimeoutLock is a threading.RLock which you can use in a 'with' context in conjunction with a timeout.
    Apparently a threading.Lock class cannot be subclassed, hence this quite elaborate implementation wrapping most
    threading.Lock methods.

    Example usage:

    my_lock = TimeoutLock()

    with my_lock.timeout_context(3) as have_lock:
        if have_lock:
            print('got the lock')
            # do something ....
        else:
            print('timeout: lock not available')
            # do something else ...


    See: https://stackoverflow.com/questions/16740104/python-lock-with-statement-and-timeout/16782391
    """
    def __init__(self):
        self._lock = threading.RLock()

    def acquire(self, blocking=True, timeout=-1):
        """wrapper around threading.Lock.aquire"""
        return self._lock.acquire(blocking, timeout)

    def release(self):
        """wrapper around threading.Lock.release"""
        self._lock.release()

    @contextlib.contextmanager
    def timeout_context(self, timeout=-1):
        """Calling this method in a 'with' statement gives you a lock_aquire_result object
        which you can check if you did aquire thre lock within the given timeout.

        my_lock = TimeoutLock()

        with my_lock.timeout_context(3) as have_lock:
            if have_lock:
                print('got the lock')
        """
        if timeout is None:
            timeout = -1

        acquire_result = self.acquire(timeout=timeout)
        yield acquire_result
        if acquire_result:
            self.release()

    def __enter__(self):
        """provide normal context manager with endless blocking aquire to mimick normal threading.Lock class."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """provide normal context manager with endless blocking aquire to mimick normal threading.Lock class."""
        self.release()
