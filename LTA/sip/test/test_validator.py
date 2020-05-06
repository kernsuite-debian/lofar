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

# $Id: $

try:
    import pyxb
except ImportError as e:
    print(str(e))
    print('Please install python3 package pyxb: sudo apt-get install python3-pyxb')
    exit(3)    # special lofar test exit code: skipped test

import unittest
from lofar.lta.sip import validator

VALIDFILE_PATH = "/tmp/valid_sip.xml"    # todo: how to deploy in testdir?

class TestSIPvalidator(unittest.TestCase):
    def test_validate(self):
        self.assertTrue(validator.validate(VALIDFILE_PATH))
        self.assertTrue(validator.check_consistency(VALIDFILE_PATH))
        self.assertTrue(validator.main(VALIDFILE_PATH))

# run tests if main
if __name__ == '__main__':
    unittest.main()
