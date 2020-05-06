# t_message.py: Test program for the module lofar.messaging.message
#
# Copyright (C) 2015
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
#
# $Id: t_messages.py 1576 2015-09-29 15:22:28Z loose $

"""
Test program for the module lofar.messaging.message
"""

import unittest
import uuid
import struct
import proton
from lofar.messaging.messages import LofarMessage


class DefaultLofarMessage(unittest.TestCase):
    """
    Class to test default constructed LofarMessage class
    """

    def setUp(self):
        """
        Create default constructed object
        """
        self.message = LofarMessage()

    def test_message_id(self):
        """
        Object attribute MessageId must be a valid UUID string
        """
        self.assertIsNotNone(self.message.id)
        self.assertTrue(isinstance(self.message.id, uuid.UUID))

#TODO: add more tests


if __name__ == '__main__':
    unittest.main()
