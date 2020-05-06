#!/usr/bin/env python3

import unittest
import tempfile
from lofar.common.dbcredentials import *

def setUpModule():
  pass

def tearDownModule():
  pass

class TestCredentials(unittest.TestCase):
  def test_default_values(self):
    c = Credentials()

    self.assertEqual(c.type, "postgres")
    self.assertEqual(c.host, "localhost")
    self.assertEqual(c.port, 0)
    #self.assertEqual(c.user, "")
    self.assertEqual(c.password, "")
    self.assertEqual(c.database, "")

  def test_pg_connect_options(self):
    c = Credentials()

    self.assertEqual(
      c.pg_connect_options(),
      { "host": "localhost",
        "port": -1,
        "user": c.user,
        "passwd": "",
        "dbname": "",
      })


class TestDBCredentials(unittest.TestCase):
  def test_set_get(self):
    dbc = DBCredentials(filepatterns=[])

    c_in = Credentials()
    c_in.host = "example.com"
    c_in.port = 1234
    c_in.user = "root"
    c_in.password = "secret"
    c_in.database = "mydb"

    dbc.set("DATABASE", c_in)
    c_out = dbc.get("DATABASE")

    self.assertEqual(str(c_out), str(c_in))

  def test_get_non_existing(self):
    dbc = DBCredentials(filepatterns=[])

    with self.assertRaises(DBCredentials.NoSectionError):
      dbc.get("UNKNOWN")

  def test_list(self):
    dbc = DBCredentials(filepatterns=[])

    c = Credentials()
    c.host = "foo"
    dbc.set("FOO", c)

    c = Credentials()
    c.host = "bar"
    dbc.set("BAR", c)

    self.assertEqual(sorted(dbc.list()), ["BAR", "FOO"])


  def test_config(self):
    f = tempfile.NamedTemporaryFile()
    f.write(b"""
[database:DATABASE]
type = postgres
host = example.com
port = 1234
user = root
password = secret
database = mydb
""")
    f.flush() # don't close since that will delete the TemporaryFile

    # test if DATABASE is there
    dbc = DBCredentials(filepatterns=[f.name])
    self.assertEqual(dbc.list(), ["DATABASE"])

    # test if credentials match with what we've written
    c_in = Credentials()
    c_in.host = "example.com"
    c_in.port = 1234
    c_in.user = "root"
    c_in.password = "secret"
    c_in.database = "mydb"

    c_out = dbc.get("DATABASE")

    self.assertEqual(str(c_out), str(c_in))

  def test_freeform_config_option(self):
    f = tempfile.NamedTemporaryFile()
    f.write(b"""
[database:DATABASE]
foo = bar
test = word word
""")
    f.flush() # don't close since that will delete the TemporaryFile

    # extract our config
    dbc = DBCredentials(filepatterns=[f.name])
    c_out = dbc.get("DATABASE")

    # test if the free-form config options got through
    self.assertEqual(c_out.config["foo"], "bar")
    self.assertEqual(c_out.config["test"], "word word")

def main(argv):
  unittest.main()

if __name__ == "__main__":
  # run all tests
  import sys
  main(sys.argv[1:])
