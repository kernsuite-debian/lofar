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

#include <WinCCWrapper.h>

#include "ConfigReaderImpl.h"
#include "PublisherResources.h"
#include "ToBusImpl.h"
#include "Program.h"

using namespace LOFAR::WINCCWRAPPER;
using namespace LOFAR::WINCCPUBLISHER;

int main()
{
    // Create dependencies

    ConfigReaderImpl configReader;

    configReader.load("WinCCPublisher.conf");

    PublisherResources publisherResources{configReader};

    ToBusImpl toBus{publisherResources.getQueueName()};

    WinCCWrapper winCCWrapper{""}; 

    // Create program and run

    Program program(winCCWrapper, publisherResources, toBus);

    program.run();

    return 0;
}