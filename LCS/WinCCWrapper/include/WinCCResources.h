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

#ifndef WINCC_RESOURCES_H
#define WINCC_RESOURCES_H

namespace LOFAR {
    namespace WINCCWRAPPER {

/*! The WinCCResources is used to connect to the running wincc instance. This class is used by the WinCCWrapper class, and is not intended to be used externally.*/
class WinCCResources
{
public:
    WinCCResources(const std::string &project_name);

    WinCCResources(const std::string &program_name, const std::string &project_name, const int num);
private:
    void init(const std::string &project_name);
    void init(const std::string &program_name, const std::string &project_name, const int num);
};

    } // namespace WINCCWRAPPER
} // namespace LOFAR

#endif
