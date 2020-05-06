# test_utils.py: test utils for lofar software
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
# $Id: test_utils.py 1584 2015-10-02 12:10:14Z loose $
#
"""
This package contains different utilities that are common for LOFAR software testing
"""

from lxml.doctestcompare import LXMLOutputChecker, PARSE_XML
from doctest import Example
import unittest
import os

def assertEqualXML(test, expected):
    output_checker = LXMLOutputChecker()
    if not output_checker.check_output(expected, test, PARSE_XML):
        diff = output_checker.output_difference(Example("", expected), test, PARSE_XML)
        msg = diff
        for line in diff.split("\n"):
            if msg == diff:
                msg = msg + "\nDiff summary:\n"
            if "got:" in line or line.strip().startswith(('+', '-')):
                msg = msg + line + "\n"
        if msg == "":
            msg = diff
        raise AssertionError(msg)


# decorators for selective tests
integration_test = unittest.skipIf(os.environ.get('SKIP_INTEGRATION_TESTS', default='False').lower() in ['1', 'true'],
                                   'Integration tests are disabled via env SKIP_INTEGRATION_TESTS')
unit_test = unittest.skipIf(os.environ.get('SKIP_UNIT_TESTS', default='False').lower() in ['1', 'true'],
                            'Unit tests are disabled via env SKIP_UNIT_TESTS')
