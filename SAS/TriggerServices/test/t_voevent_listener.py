#!/usr/bin/env python3

# t_trigger_service.py
#
# Copyright (C) 2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.


import unittest
import os
import shutil
import tempfile
import subprocess
import logging
import filecmp
import threading
from lofar.triggerservices.voevent_listener import _SimpleVOEventListener

LOCALDIR = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = tempfile.mkdtemp()  # this is where comet keeps track of handled events, which it won't accept them again
_, tmppath = tempfile.mkstemp()


class TestVOEventListener(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # todo: create proper test coverage - Note that this was kind of an emergency project and proper testing
        # todo: ...according to agreed coding standards was put out of action.

        print('This is a stub! Not enough test coverage here...' )

        # todo: check for running broker on localhost and use different ports then
        subprocess.check_call("twistd comet -rb --local-ivo=ivo://alert/test --eventdb=%s" % DB_PATH, shell=True)

        # Start event handler
        handler = _SimpleVOEventListener(write_to_file=True, file_path=tmppath)
        t = threading.Thread(target=handler.start_listening)
        t.daemon = True
        t.start()

    @classmethod
    def tearDownClass(cls):
        print('Cleaning up...')
        os.remove(tmppath)
        shutil.rmtree(DB_PATH)
        subprocess.call('pkill -f "twistd comet"', shell=True)  # todo: make this more specific?

    def test_received_voevent_is_identical_to_sent_voevent(self):

        try:
            event_path = LOCALDIR + '/example_voevent.xml'
            subprocess.check_call("comet-sendvo --host=127.0.0.1 --port=8098 < %s" % event_path, shell=True)
        except:
            print("VO-Event sending failed. Are you running a broker on localhost?\n"
                  " -> E.g. run 'twistd comet -rb --local-ivo=ivo://alert/test'")
            raise

        self.assertTrue(filecmp.cmp(tmppath, event_path))


if __name__ == '__main__':
    logformat = "%(asctime)s %(levelname)8s %(funcName)25s:%(lineno)-5d | %(threadName)10s | %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO)
    unittest.main()




