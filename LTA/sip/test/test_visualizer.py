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
import time
import os
from lofar.lta.sip import visualizer
from lofar.lta.sip import ltasip

INPUTFILE_PATH = "/tmp/valid_sip.xml"

class TestSIPvisualizer(unittest.TestCase):
    def test_visualize(self):
      with open(INPUTFILE_PATH) as f:
        xml = f.read()
        sip = ltasip.CreateFromDocument(xml)
        path = INPUTFILE_PATH + ".visualize"
        format = 'svg'
        visualizer.visualize_sip(sip, path, format)
        st = os.stat(INPUTFILE_PATH + ".visualize.svg")
        self.assertTrue(st.st_size > 0 and (time.time() - st.st_mtime) < 60)

# run tests if main
if __name__ == '__main__':
    unittest.main()
