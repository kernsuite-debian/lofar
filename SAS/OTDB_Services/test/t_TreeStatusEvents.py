#!/usr/bin/env python3
#coding: iso-8859-15
#
# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: Backtrace.cc 31468 2015-04-13 23:26:52Z amesfoort $
"""
RPC functions that allow access to (VIC) trees in OTDB.

TaskSpecificationRequest: get the specification(parset) of a tree as dict.
KeyUpdateCommand        : function to update the value of multiple (existing) keys.
StatusUpdateCommand     : finction to update the status of a tree.
"""

from lofar.messaging.messagebus import *
from lofar.sas.otdb.TreeStatusEvents import create_service
import threading
import sys
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

from lofar.sas.otdb.testing.otdb_common_testing import OTDBTestInstance

with OTDBTestInstance('t_TreeStatusEvents.in.unittest_db.dump.gz') as test_db:
    with TemporaryExchange(__name__) as tmp_exchange:
        with tmp_exchange.create_temporary_queue() as tmp_queue:
            with tmp_queue.create_frombus() as frombus:

                with NamedTemporaryFile(mode='w+') as state_file:
                    state_file.file.write((datetime.utcnow()-timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S"))
                    state_file.file.flush()

                    t = threading.Thread(target=create_service, args=(tmp_exchange.address, test_db.dbcreds, state_file.name))
                    t.daemon = True
                    t.start()

                    with test_db.create_database_connection() as db:
                        db.executeQuery("select setTreeState(1, %d, %d::INT2,'%s'::boolean);" % (1099266, 500, False))
                        db.commit()

                    msg = frombus.receive(timeout=500, acknowledge=True)	  # TreeStateEvent are send every 2 seconds
                    logger.info(msg)
                    try:
                        ok = (msg.content['treeID'] == 1099266 and msg.content['state'] == 'queued')
                    except IndexError:
                        ok = False

sys.exit(not ok)   # 0 = success
