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

#include <Resources.hxx>

#include "WinCCResources.h"

namespace LOFAR {
    namespace WINCCWRAPPER {

using namespace std;

WinCCResources::WinCCResources(const std::string &project_name)
{
    init(project_name);
}

WinCCResources::WinCCResources(const::std::string &program_name, const std::string &project_name, const int num)
{
    init(program_name, project_name, num);
}


void WinCCResources::init(const::std::string &program_name, const std::string & project_name, const int num)
{
    std::vector<std::string> args{program_name};

    if(project_name.compare("-currentproj") == 0){
        args.push_back("-currentproj");
    }else{
        args.push_back("-proj");
        args.push_back(project_name);
    }
    args.push_back("-log");
    args.push_back("+stderr");

    args.push_back("-num");
    args.push_back(std::to_string(num));


    int ownArgc = args.size();

    char * ownArgv[ownArgc];

    for(int i=0; i<ownArgc; i++){
        ownArgv[i] = const_cast<char *>(args.at(i).c_str());
    }

    Resources::init(ownArgc, ownArgv);
}



void WinCCResources::init(const std::string & project_name)
{
    std::vector<std::string> args{"WinCCWrapper"};

    if(project_name.compare("-currentproj") == 0){
        args.push_back("-currentproj");
    }else{
        args.push_back("-proj");
        args.push_back(project_name);
    }
    args.push_back("-log");
    args.push_back("+stderr");

    int ownArgc = args.size();

    char * ownArgv[ownArgc];

    for(int i=0; i<ownArgc; i++){
        ownArgv[i] = const_cast<char *>(args.at(i).c_str());
    }

    Resources::init(ownArgc, ownArgv);
}

    } // namespace WINCCWRAPPER
} // namespace LOFAR
