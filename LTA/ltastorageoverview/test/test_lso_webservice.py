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


import unittest
import urllib.request, urllib.error, urllib.parse
import json
import datetime
from io import StringIO
from lofar.lta.ltastorageoverview import store
from lofar.lta.ltastorageoverview.testing.common_test_ltastoragedb import LTAStorageDbTestMixin
from lofar.lta.ltastorageoverview.webservice import webservice as webservice
from flask_testing import LiveServerTestCase as FlaskLiveTestCase

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

class TestLTAStorageWebService(LTAStorageDbTestMixin, FlaskLiveTestCase):
    def create_app(self):
        webservice.db = self.db
        return webservice.app

    def setUp(self):
        super().setUp()
        self.fill_with_test_data()

    def fill_with_test_data(self):
        logger.info('filling test LTASO database with test data')
        self.db.insertSiteIfNotExists('siteA', 'srm://siteA.org')
        self.db.insertSiteIfNotExists('siteB', 'srm://siteB.org')

        rootDir_ids = []
        rootDir_ids.append(self.db.insertRootDirectory('siteA', 'rootDir1'))
        rootDir_ids.append(self.db.insertRootDirectory('siteA', 'rootDir2'))
        rootDir_ids.append(self.db.insertRootDirectory('siteB', 'path/to/rootDir3'))

        for rootDir_id in rootDir_ids:
            for j in range(2):
                subDir_id = self.db.insertSubDirectory('subDir_%d' % j, rootDir_id)

                if j == 0:
                    self.db.insertFileInfo('file_%d' % j, 271 * (j + 1), datetime.datetime.utcnow(), subDir_id)

                for k in range(2):
                    subsubDir_id = self.db.insertSubDirectory('subsubDir_%d' % k, subDir_id)

                    for l in range((j + 1) * (k + 1)):
                        self.db.insertFileInfo('file_%d' % l, 314 * (l + 1), datetime.datetime.utcnow(), subsubDir_id)

        logger.info('finished filling test LTASO database with test data')


    def testSites(self):
        response = urllib.request.urlopen('http://localhost:5000/rest/sites/')
        self.assertEqual(200, response.code)
        self.assertEqual('application/json', response.info()['Content-Type'])

        content = json.load(StringIO(response.read().decode("UTF-8")))

        self.assertTrue('sites' in content)
        sites = content['sites']

        sitesDict = dict([(x['name'], x) for x in sites])
        self.assertTrue('siteA' in sitesDict)
        self.assertEqual('srm://siteA.org', sitesDict['siteA']['url'])
        self.assertTrue('siteB' in sitesDict)
        self.assertEqual('srm://siteB.org', sitesDict['siteB']['url'])

        for site in sitesDict:
            response = urllib.request.urlopen('http://localhost:5000/rest/sites/%d' % (sitesDict[site]['id']))
            self.assertEqual(200, response.code)
            self.assertEqual('application/json', response.info()['Content-Type'])

            content = json.load(StringIO(response.read().decode("UTF-8")))

            self.assertTrue('id' in content)
            self.assertTrue('name' in content)
            self.assertTrue('url' in content)

    def testRootDirectories(self):
        response = urllib.request.urlopen('http://localhost:5000/rest/rootdirectories/')
        self.assertEqual(200, response.code)
        self.assertEqual('application/json', response.info()['Content-Type'])

        content = json.load(StringIO(response.read().decode("UTF-8")))
        self.assertTrue('rootDirectories' in content)

        rootDirectories = content['rootDirectories']
        self.assertEqual(3, len(rootDirectories))

        rootDirsDict = dict([(x['dir_name'], x) for x in rootDirectories])

        self.assertEqual('siteA', rootDirsDict['rootDir1']['site_name'])
        self.assertEqual('siteA', rootDirsDict['rootDir2']['site_name'])
        self.assertEqual('siteB', rootDirsDict['path/to/rootDir3']['site_name'])


# run tests if main
if __name__ == '__main__':
    unittest.main()
