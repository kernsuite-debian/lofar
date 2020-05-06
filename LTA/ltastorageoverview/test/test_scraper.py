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

import logging

import unittest
from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin
from lofar.lta.ltastorageoverview import scraper

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


class TestLocation(unittest.TestCase):
    def test_isRoot(self):
        loc = scraper.Location('srm://srm.grid.sara.nl:8443', '/foo/bar')
        self.assertFalse(loc.isRoot())

        loc = scraper.Location('srm://srm.grid.sara.nl:8443', '/')
        self.assertTrue(loc.isRoot())

    def test_malformed_location(self):
        with self.assertRaises(ValueError) as context:
            scraper.Location('http://astron.nl', '/foo/bar')
            self.assertTrue('malformed srm url' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            scraper.Location('srm://srm.grid.sara.nl:8443', 'some_dir_name')
            self.assertTrue('malformed directory' in str(context.exception))


class TestScraper(LTAStorageDbTestMixin, unittest.TestCase):
    # TODO: implement unittests
    pass

# run tests if main
if __name__ == '__main__':
    unittest.main()
