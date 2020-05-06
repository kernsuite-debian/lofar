# mock.py: mocked version of WinCCWrapper
#
# Copyright (C) 2016
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the APERTIF software suite.
# The APERTIF software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The APERTIF software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the APERTIF software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id:  $

"""
this module defines a mocked version of lofar.common.wincc.pywincc.WinCCWrapper"""


from apertif.common.astronLogger import get_logger
logger = get_logger('apertif')

class MockWinCCWrapper:
    '''mocked version of lofar.common.wincc.pywincc.WinCCWrapper with same API,
    faking a database storage backend by storing all set values in a local dict
    '''
    def __init__(self):
        self.last_set_values = {}
        self.last_set_valid_values = {}

    def set_datapoint(self, name, value, valid):
        logger.info('MockWinCCWrapper: storing value=%s valid=%s for datapoint=%s', value, valid, name)
        self.last_set_values[name] = value
        self.last_set_valid_values[name] = valid

    def set_datapoint_int(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_long(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_bool(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_float(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_string(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_time(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_list(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def set_datapoint_vector(self, name, value, valid):
        return self.set_datapoint(name, value, valid)

    def get_datapoint(self, name):
        return self.last_set_values[name]

    def get_datapoint_int(self, name):
        return self.get_datapoint(name)

    def get_datapoint_long(self, name):
        return self.get_datapoint(name)

    def get_datapoint_float(self, name):
        return self.get_datapoint(name)

    def get_datapoint_bool(self, name):
        return self.get_datapoint(name)

    def get_datapoint_string(self, name):
        return self.get_datapoint(name)

    def get_datapoint_time(self, name):
        return self.get_datapoint(name)

    def get_datapoint_list(self, name):
        return self.get_datapoint(name)

    def get_datapoint_vector(self, name):
        return self.get_datapoint(name)

    def set_datapoint_valid(self, name):
        self.last_set_valid_values[name] = True

    def set_datapoint_invalid(self, name):
        self.last_set_valid_values[name] = False

