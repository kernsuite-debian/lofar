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
from lofar.lta.sip import siplib
from lofar.lta.sip import validator
from lofar.lta.sip import constants
from lofar.lta.sip import feedback
import uuid

TMPFILE_PATH = "/tmp/test_siplib.xml"    # todo: how to deploy in testdir?
FEEDBACK_PATH = "/tmp/testmetadata_file.Correlated.modified"    # todo: how to deploy in testdir?

def create_basicdoc():
    return siplib.Sip(
            project_code = "code",
            project_primaryinvestigator = "pi",
            project_contactauthor = "coauthor",
            # project_telescope="LOFAR",
            project_description = "awesome project",
            project_coinvestigators = ["sidekick1", "sidekick2"],
            dataproduct = siplib.SimpleDataProduct(
                siplib.DataProductMap(
                    type = "Unknown",
                    identifier = siplib.Identifier("test"),
                    size = 1024,
                    filename = "/home/paulus/test.h5",
                    fileformat = "HDF5",
                    process_identifier = siplib.Identifier("test"),
                    checksum_md5 = "hash1",
                    checksum_adler32 = "hash2",
                    storageticket = "ticket"
                )
            )
        )

class TestSIPfeedback(unittest.TestCase):

    def test_basic_doc(self):
        # create example doc with mandatory attributes
        print("===\nCreating basic document:\n")
        mysip = create_basicdoc()
        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

    def test_dataproducts(self):
        mysip = create_basicdoc()
        print("===\nAdding related generic dataproduct:\n")
        with open(FEEDBACK_PATH) as f:
            text = f.readlines()
            fb = feedback.Feedback(text)
        pipe_label = siplib.Identifier('test')
        dataproducts = fb.get_dataproducts(prefix = "test.prefix", process_identifier = pipe_label)
        for dp in dataproducts:
            print("...adding:", dp)
            mysip.add_related_dataproduct(dp)

        mysip.save_to_file(TMPFILE_PATH)
        self.assertTrue(validator.validate(TMPFILE_PATH))

# run tests if main
if __name__ == '__main__':
    unittest.main()
