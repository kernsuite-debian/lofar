#!/usr/bin/env python3

# trigger_handler.py
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


"""
This module contains the logic to decide whether it makes scientifically sense to accept a certain vo event.
"""

import logging
import datetime
from lxml import etree
import lofar.triggerservices.trigger_service
import time
import dateutil.parser

logger = logging.getLogger(__name__)

class DeciderInterface:
    """
    A simple interface that should be implemented by a decider class to accept or reject events.
    Note: This is not the place to perform permission or system state checks, but rather things like e.g. whether an
    event is visible or interesting enough to be observed.

    Example:
    ---
    class AcceptAllDecider(DeciderInterface):
        def is_acceptable(self, voevent_root):
            logger.info('Accepting all events.')
            return True
    ---
    """

    def is_acceptable(self, voevent_root):
        """
        This should be overwritten by project-specific logic that decide whether the provided VO event should be
        accepted or not. This logic should usually be provided by the PI.

        :param voevent_root: the root node of the event as an lxml etree
        :return: True to accept the event, False to reject/drop it
        """
        raise NotImplementedError



class ALERTDecider(DeciderInterface):
    """
    Alert event acceptance based on input from Sander
    """
    def is_acceptable(self, voevent_root):

        # check if this event is marked as 'test'
        role = voevent_root.attrib['role']
        logger.info('Role: %s' % role)
        if role.lower() == 'test':
            logger.info('Role is test! Everyone, this is just an exercise! Rejecting the event.')
            return False

        # check that event toa is between now and in half an hour...
        # ...read from event
        isotime = voevent_root.find('./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Time/TimeInstant/ISOTime').text
        reference_frequency = float(voevent_root.find("./What/Group[@name='observatory parameters']/Param[@name='centre_frequency']").attrib['value'])
        dm = float(voevent_root.find("./What/Group[@name='event parameters']/Param[@name='dm']").attrib['value'])
        # ...determine time to arrival
        reference_time = time.mktime(dateutil.parser.parse(isotime).timetuple())  # convert time string to seconds
        now = time.mktime(datetime.datetime.utcnow().timetuple())
        centertime = lofar.triggerservices.trigger_service.translate_arrival_time_to_frequency(reference_time, reference_frequency, dm, target_frequency=200)
        diff = centertime - now
        # ...check if out of bounds:
        if diff < 0:
            msg = 'Event whooshed already past! (%s seconds ago)' % -diff
            logger.error(msg)
            raise ValueError(msg)
        if diff > 1800:
            msg = 'Event will arrive too far in the future! (%s seconds from now)' % diff
            logger.error(msg)
            raise ValueError(msg)

        # accept the request is nothing was wrong
        return True


