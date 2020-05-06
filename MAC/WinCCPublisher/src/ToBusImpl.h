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

#ifndef WINCCSERVICES_TOBUS_IMPL_H
#define WINCCSERVICES_TOBUS_IMPL_H

#include <string>

#include "ToBus.h"

#include <Messaging/Message.h>
#include <Messaging/ToBus.h>

namespace LOFAR {
    namespace WINCCPUBLISHER {

class ToBusImpl : public ToBus
{
public:
    ToBusImpl(const std::string &address);
    void send(const Messaging::Message &message);
private:
    Messaging::ToBus toBus;
};

    } // namespace WINCCPUBLISHER
} // namespace LOFAR

#endif
