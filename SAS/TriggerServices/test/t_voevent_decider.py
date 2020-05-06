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
import datetime
import logging
from lofar.triggerservices.voevent_decider import ALERTDecider
from lxml import etree

LOCALDIR = os.environ.get('srcdir', os.path.dirname(os.path.abspath(__file__)))

class TestVOEventDecider(unittest.TestCase):

    def setUp(self):
        self.alertdecider = ALERTDecider()
        with open(LOCALDIR + '/example_voevent.xml') as f:
            self.voevent = etree.parse(f).getroot()

    def test_ALERTDecider_rejects_test_event(self):
        self.assertFalse(self.alertdecider.is_acceptable(self.voevent))

    def test_ALERTDecider_raises_ValueError_on_past_event(self):
        self.voevent.attrib['role'] = 'utility'  # pretend it's a real event
        with self.assertRaises(ValueError) as err:
            self.alertdecider.is_acceptable(self.voevent)
        self.assertTrue('past' in str(err.exception))

    def test_ALERTDecider_raises_ValueError_on_futuristic_event(self):
        self.voevent.attrib['role'] = 'utility'  # pretend it's a real event
        isotime = self.voevent.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Time/TimeInstant/ISOTime')
        isotime.text = (datetime.datetime.utcnow() + datetime.timedelta(minutes=35)).isoformat()
        with self.assertRaises(ValueError) as err:
            self.alertdecider.is_acceptable(self.voevent)
        self.assertTrue('future' in str(err.exception))

    def test_ALERTDecider_accepts_live_event_in_near_future(self):
        self.voevent.attrib['role'] = 'utility'  # pretend it's a real event
        isotime = self.voevent.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Time/TimeInstant/ISOTime')
        isotime.text = (datetime.datetime.utcnow() + datetime.timedelta(minutes=25)).isoformat()
        self.assertTrue(self.alertdecider.is_acceptable(self.voevent))



if __name__ == '__main__':
    logformat = "%(asctime)s %(levelname)8s %(funcName)25s:%(lineno)-5d | %(threadName)10s | %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO)
    unittest.main()




