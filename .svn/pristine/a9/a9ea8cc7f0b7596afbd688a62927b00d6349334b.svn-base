#!/usr/bin/env python

import unittest
import tempfile
from lofar.common.defaultmailaddresses import PipelineEmailConfig

def setUpModule():
  pass

def tearDownModule():
  pass



class TestPipelineEmailAddress(unittest.TestCase):
    def test_access_returns_correct_value(self):
        f = tempfile.NamedTemporaryFile()
        f.write("""
[Pipeline]
error-sender = softwaresupport@astron.nl
        """)
        f.flush()

        pec = PipelineEmailConfig(filepatterns=[f.name])
        self.assertEqual(pec["error-sender"], "softwaresupport@astron.nl")

    def test_access_nonexistent_key_raises_exception(self):
        f = tempfile.NamedTemporaryFile()
        f.write("""
[Pipeline]
error-sender = softwaresupport@astron.nl
        """)
        f.flush()
        pec = PipelineEmailConfig(filepatterns=[f.name])
        with self.assertRaises(Exception):
            print pec["non-existant"]

    def test_access_nonexisting_config_file_raises_exception(self):

        with self.assertRaises(Exception):
            dbc = PipelineEmailConfig(filepatterns=[])

    def test_access_malformed_config_file_raises_exception(self):
        f = tempfile.NamedTemporaryFile()
        f.write("""
[Pipeline]
error-sender
        """)
        f.flush()
        pec = PipelineEmailConfig(filepatterns=[f.name])
        with self.assertRaises(Exception):
            print pec["error-sender"]
        

def main():
  unittest.main()

if __name__ == "__main__":
  # run all tests
  import sys
  main()
