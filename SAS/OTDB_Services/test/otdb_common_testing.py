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
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

from lofar.common.testing.postgres import PostgresTestDatabaseInstance


class OTDBTestInstance(PostgresTestDatabaseInstance):
    '''Helper class which uses the OTDBCommonTestMixin without a unittest.TestCase to setup/teardown a test OTDB instance'''
    def __init__(self, gzipped_schema_dump_filename):
        super().__init__()
        self.gzipped_schema_dump_filename = gzipped_schema_dump_filename

    def apply_database_schema(self):
        logger.info('applying OTDB sql schema to %s', self.dbcreds)

        cmd1 = ['gzip', '-dc', self.gzipped_schema_dump_filename]

        cmd2 = ['psql', '-U', self.dbcreds.user, '-h', self.dbcreds.host,
                '-p', str(self.dbcreds.port), self.dbcreds.database]

        logger.info('executing: %s', ' '.join(cmd1))
        logger.info('executing: %s', ' '.join(cmd2))

        proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(cmd2, stdin=proc1.stdout)
        proc1.wait(timeout=60)
        proc2.wait(timeout=60)

        if proc1.returncode != 0:
            raise RuntimeError("Could not execute cmd: '%s' error=%s" % (' '.join(cmd1), proc1.stderr))

        if proc2.returncode != 0:
            raise RuntimeError("Could not execute cmd: '%s' error=%s" % (' '.join(cmd2), proc2.stderr))
