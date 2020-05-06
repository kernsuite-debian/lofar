# __init__.py: Module initialization file.
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
# $Id: __init__.py 1568 2015-09-18 15:21:11Z loose $

"""
Lofar's messaging package.
See lofar.messaging.messagebus and lofar.messaging.rpc for documentation and working examples.
"""

from lofar.common import isProductionEnvironment, isTestEnvironment

def adaptNameToEnvironment(name):
    if isProductionEnvironment():
        return name #return original name only for PRODUCTION LOFARENV

    if isTestEnvironment():
        return 'test.%s' % name #return 'test.' prefixed name only for TEST LOFARENV

    # in all other cases prefix queue/bus name with 'devel.'
    return 'devel.%s' % name

from .messagebus import *
from .messages import *
from .config import *
from .rpc import *
