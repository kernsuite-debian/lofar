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

#ifndef WINCCSERVICES_PROGRAM_H
#define WINCCSERVICES_PROGRAM_H

#include <memory>

#include <WinCCWrapper.h>

#include <Messaging/LofarMessages.h>

#include "PublisherResources.h"
#include "ToBusImpl.h"

namespace LOFAR {
    namespace WINCCPUBLISHER {

class Program
{
public:
    Program(WINCCWRAPPER::WinCCWrapper &winCCWrapper, PublisherResources &publisherResources, ToBus &toBus);
    ~Program();

    void run();
private:
    WINCCWRAPPER::WinCCWrapper &winCCWrapper;
    PublisherResources &publisherResources;
    ToBus &toBus;

    void handle_connect(std::string name, std::string value);
    LOFAR::Messaging::MonitoringMessage create_monitor_message(const std::string &name, const std::string &value);
};

    } // namespace WINCCPUBLISHER
} // namespace LOFAR

#endif
