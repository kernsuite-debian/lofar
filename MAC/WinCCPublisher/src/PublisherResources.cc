//# Copyright (C) 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR Software Suite.
//#
//# The LOFAR Software Suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published by
//# the Free Software Foundation, either version 3 of the License, or (at your
//# option) any later version.
//#
//# The LOFAR Software Suite is distributed in the hope that it will be
//# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
//# Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along with
//# The LOFAR Software Suite.  If not, see <http://www.gnu.org/licenses/>.

#include <ErrHdl.hxx>
#include <Resources.hxx>
#include <string>

#include <Common/StringUtil.h>

#include "PublisherResources.h"

namespace LOFAR {
    namespace WINCCPUBLISHER {

using namespace std;

PublisherResources::PublisherResources(ConfigReader& configReader) :
    configReader(configReader)
{
    readConfigFile();
}

void PublisherResources::readConfigFile()
{
    std::string all_dataPoints = configReader.get_string("datapoints");
    dataPoints = StringUtil::split(all_dataPoints, ',');

    queueName = configReader.get_string("queuename");
}

    } // namespace WINCCPUBLISHER
} // namespace LOFAR
