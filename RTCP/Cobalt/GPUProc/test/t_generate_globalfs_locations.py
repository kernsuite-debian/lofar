#!/usr/bin/env python3

import unittest

# Be able to find service python file
import sys, os
sys.path.insert(0, "{srcdir}/../src/scripts".format(**os.environ))

import generate_globalfs_locations as ggl

from lofar.parameterset import PyParameterSet

class ReplaceHost(unittest.TestCase):
  def test_replace(self):
    # Replace the host
    self.assertEqual(ggl.replace_host("CEP4:/foo/bar", "CEP4", ["host"]), "CEP4:host:/foo/bar")

    # Don't replace the host
    self.assertEqual(ggl.replace_host("locus001:/foo/bar", "CEP4", ["host"]), "locus001:/foo/bar")

  def test_rotate(self):
    # See if host array rotates
    hosts = ["foo", "bar", "baz"]

    self.assertEqual(ggl.replace_host("CEP4:/foo/bar", "CEP4", hosts), "CEP4:foo:/foo/bar")
    self.assertEqual(hosts, ["bar","baz","foo"])

    self.assertEqual(ggl.replace_host("CEP4:/foo/bar", "CEP4", hosts), "CEP4:bar:/foo/bar")
    self.assertEqual(ggl.replace_host("CEP4:/foo/bar", "CEP4", hosts), "CEP4:baz:/foo/bar")

class ProcessParset(unittest.TestCase):
  def test(self):
    parset = PyParameterSet("t_generate_globalfs_locations.in_parset", False)

    # obtain & check the cluster name
    cluster_name = parset.getString("Observation.Cluster.ProcessingCluster.clusterName")
    self.assertEqual(cluster_name, "CEP4")

    # process
    ggl.process_parset(parset, cluster_name, ["foo", "bar"])

    # check if hosts are replaced
    locations = parset._getStringVector1("Observation.DataProducts.Output_CoherentStokes.locations", True)
    for l in locations:
      self.assertTrue(l.startswith("CEP4:foo:") or l.startswith("CEP4:bar:"))

def main(argv):
  unittest.main()

if __name__ == "__main__":
  # run all tests
  import sys
  main(sys.argv[1:])
