#!/usr/bin/env python3

import unittest
from lofar.lta.ingest.common.srm import *

import logging
logger = logging.getLogger(__name__)

class TestSrm(unittest.TestCase):
    """
    Test various methods from the srm module.
    Unfortunately, we cannot do unittests on actual srm calls, as we need real srm sites and certificates for that.
    """

    def test_get_site_surl(self):
        self.assertEqual('srm://srm.grid.sara.nl:8443',
                         get_site_surl('srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346/L658346_SB019_uv.MS_8190b749.tar'))

        self.assertEqual('srm://lofar-srm.fz-juelich.de:8443',
                         get_site_surl('srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884'))

        self.assertEqual('srm://lta-head.lofar.psnc.pl:8443',
                         get_site_surl('srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lt10_004/658456/L658456_SAP000_B000_P012_bf_03c23eb1.tar'))

        with self.assertRaises(SrmException) as context:
            get_site_surl('http://nu.nl')
        self.assertTrue('invalid srm_url' in str(context.exception))

    def test_path_in_site(self):
        self.assertEqual('/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346/L658346_SB019_uv.MS_8190b749.tar',
                         get_path_in_site('srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346/L658346_SB019_uv.MS_8190b749.tar'))

        self.assertEqual('/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884',
                         get_path_in_site('srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884'))

        self.assertEqual('/lofar/ops/projects/lt10_004/658456/L658456_SAP000_B000_P012_bf_03c23eb1.tar',
                         get_path_in_site('srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lt10_004/658456/L658456_SAP000_B000_P012_bf_03c23eb1.tar'))

        # check if tailing '/' is removed
        self.assertEqual('/foo/bar',
                         get_path_in_site('srm://lta-head.lofar.psnc.pl:8443/foo/bar/'))

        with self.assertRaises(SrmException) as context:
            get_path_in_site('http://nu.nl')
        self.assertTrue('invalid srm_url' in str(context.exception))

    def test_dir_path_in_site(self):
        self.assertEqual('/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346',
                         get_dir_path_in_site('srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346'))

        self.assertEqual('/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346',
                         get_dir_path_in_site('srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346/'))

        self.assertEqual('/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346',
                         get_dir_path_in_site('srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc10_010/658346/L658346_SB019_uv.MS_8190b749.tar'))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG)
    unittest.main()
