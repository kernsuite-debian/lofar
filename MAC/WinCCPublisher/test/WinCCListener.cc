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

#include <memory>
#include <string>

#include <Common/ParameterSet.h>
#include <Common/LofarLocators.h>
#include <Messaging/Message.h>
#include <Messaging/FromBus.h>
#include <Messaging/DefaultSettings.h>

int main()
{
    double timeOut{0.5};

    std::string queueName{""};

    LOFAR::ConfigLocator configLocator;
    std::string configPath = configLocator.locate("WinCCPublisher.conf");

    if(configPath != "")
    {
        LOFAR::ParameterSet parameterSet{configPath, LOFAR::KeyCompare::NOCASE};

        queueName = parameterSet.getString("queuename");
    }
    else
    {
        std::cout << "Could not find WinCCPublisher.conf" << std::endl;
        return 1;
    }

    LOFAR::Messaging::FromBus fromBus{queueName, LOFAR::Messaging:defaultBroker, "{create: always, delete: always}"};

    while (1)
    {
        std::unique_ptr<LOFAR::Messaging::Message> recvMsg{fromBus.getMessage(timeOut)};
        if(recvMsg != nullptr)
        {
            qpid::types::Variant::Map map;

            qpid::messaging::decode(*recvMsg, map);

            std::cout << recvMsg->getSubject();

            for(std::map<std::string, qpid::types::Variant>::iterator iter = map.begin(); iter != map.end(); ++iter)
            {
                std::cout << iter->first << ": " << iter->second << " ";
            }

            std::cout << std::endl;
        }
    }

    return 0;
}
