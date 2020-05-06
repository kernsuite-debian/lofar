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

#include "ConfigReaderImpl.h"

#include <stdexcept>

namespace LOFAR {
    namespace WINCCPUBLISHER {

using namespace std;

void ConfigReaderImpl::load(const std::string &config_file_name)
{
    const string configPath = configLocator.locate(config_file_name);

    if(configPath != "")
    {
        parameterSet = std::unique_ptr<ParameterSet>(new ParameterSet(configPath, KeyCompare::NOCASE));
    }
    else
    {
        throw std::invalid_argument("Could not locate the config file: " + config_file_name);
    }
}

std::string ConfigReaderImpl::get_string(const std::string &string_name)
{
    return parameterSet->getString(string_name);

    if(parameterSet->isDefined(string_name))
    {
        return parameterSet->getString(string_name);
    }
    else
    {
        throw std::invalid_argument("Cound not find item: " + string_name + " in config file");
    }
}

    } // namespace WINCCPUBLISHER
} // namespace LOFAR
