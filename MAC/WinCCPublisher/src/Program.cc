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

#include "Program.h"

#include <Manager.hxx>

#include "PublisherResources.h"

namespace LOFAR {
    namespace WINCCPUBLISHER {

using namespace std;
using namespace WINCCWRAPPER;

Program::Program(WinCCWrapper &winCCWrapper, PublisherResources &publisherResources, ToBus &toBus) :
	winCCWrapper(winCCWrapper), publisherResources(publisherResources), toBus(toBus)
{
    this->winCCWrapper.set_connect_datapoints_callback(
        [this](std::string name, std::string value)
	{
	    handle_connect(name, value); 
	}
    );
    this->winCCWrapper.connect_datapoints(publisherResources.getDataPoints());
}

void Program::handle_connect(std::string name, std::string value)
{
    Messaging::MonitoringMessage sendMsg = create_monitor_message(name, value);

    toBus.send(sendMsg);
}

LOFAR::Messaging::MonitoringMessage Program::create_monitor_message(
		    const string &name, const string &value)
{
    Messaging::MonitoringMessage sendMsg;
    string subject = string("WinCCPublisher : ") + name;
    sendMsg.setSubject(subject);

    qpid::types::Variant::Map content;
    content["name"]  = name;
    content["value"]  = value;

    qpid::messaging::encode(content, sendMsg);

    return sendMsg;
}

Program::~Program()
{
    winCCWrapper.exit(); 
}

void Program::run()
{
    winCCWrapper.run();
}

    } // namespace WINCCPUBLISHER
} // namespace LOFAR
