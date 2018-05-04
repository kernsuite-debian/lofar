# cache.py: function return value cache
#
# copyright (c) 2015
# astron (netherlands institute for radio astronomy)
# p.o.box 2, 7990 aa dwingeloo, the netherlands
#
# this file is part of the lofar software suite.
# the lofar software suite is free software: you can redistribute it
# and/or modify it under the terms of the gnu general public license as
# published by the free software foundation, either version 3 of the
# license, or (at your option) any later version.
#
# the lofar software suite is distributed in the hope that it will be
# useful, but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license along
# with the lofar software suite. if not, see <http://www.gnu.org/licenses/>.
#
# $id: __init__.py 1568 2015-09-18 15:21:11z loose $

import functools

class cache(object):
    """ A simple cache for function call return values in Python 2. 

        Use:

          @cache
          def foo(x):
            return x

        Causes foo() to be evaluated only for new values of x. """

    # If the needs for this class ever expands significantly, we should consider
    # switching to python 3, which provides a more comprehensive functools.lru_cache.

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        key = "%s %s" % (args, kwargs) # we can't hash on (args,kwargs) directly

        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)

        return self.cache[key]

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)
