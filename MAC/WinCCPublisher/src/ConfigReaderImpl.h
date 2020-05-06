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

#ifndef WINCCSERVICES_CONFIG_READER_IMPL_H
#define WINCCSERVICES_CONFIG_READER_IMPL_H

#include <string>
#include <memory>

#include <Common/LofarLocators.h>
#include <Common/ParameterSet.h>

#include "ConfigReader.h"

namespace LOFAR {
    namespace WINCCPUBLISHER {

class ConfigReaderImpl : public ConfigReader
{
public:
    void load(const std::string &config_file_name);
    std::string get_string(const std::string &string_name);
private:
    ConfigLocator configLocator;
    std::unique_ptr<ParameterSet> parameterSet;
};

    } // namespace WINCCPUBLISHER
} // namespace LOFAR

#endif
