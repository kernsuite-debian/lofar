#!/usr/bin/env python3

# telescope_model.py
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

class TelescopeModel:
    """ The MomXMLModel data structure contains the properties that are configurable in a MoM XML template """
    
    def __init__(self):
        self.target_ra = None
        self.target_dec = None
        self.calibrator_ra = None
        self.calibrator_dec = None
        self.start_time = None
        self.min_start_time = None
        self.max_end_time = None
        self.duration = None
        self.min_duration = None
        self.max_duration = None
        self.trigger_id = None
        self.station_selection = None  # for misc field
        self.custom_station_list = None    # custom stationset for mom
        self.outer_foldername = None
        self.inner_foldername = None
        self.projectname = None

