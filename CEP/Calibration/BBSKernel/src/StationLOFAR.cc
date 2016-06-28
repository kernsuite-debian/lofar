//# StationLOFAR.cc: Description of a LOFAR station.
//#
//# Copyright (C) 2013
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR software suite.
//# The LOFAR software suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published
//# by the Free Software Foundation, either version 3 of the License, or
//# (at your option) any later version.
//#
//# The LOFAR software suite is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
//#
//# $Id$

#include <lofar_config.h>
#include <BBSKernel/StationLOFAR.h>

namespace LOFAR
{
namespace BBS
{

StationLOFAR::StationLOFAR(const string &name, const casa::MPosition &position,
    const StationResponse::Station::ConstPtr &station)
    :   Station(name, position),
        itsStation(station)
{
}

StationResponse::Station::ConstPtr StationLOFAR::station() const
{
    return itsStation;
}

} //# namespace BBS
} //# namespace LOFAR
