//# MessageBus.h: Wrapper for generic QPID tooling (initialisation, teardown, helper functions, etc)
//#
//# Copyright (C) 2015
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR software suite.
//# The LOFAR software suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published
//# by the Free Software Foundation, either version 3 of the License, or
//# (at your option) any later version.
//#
//# The LOFAR software suite is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
//#
//# $Id: MessageBus.h 31882 2015-06-22 07:50:04Z mol $

#ifndef LOFAR_MESSAGEBUS_MESSAGEBUS_H
#define LOFAR_MESSAGEBUS_MESSAGEBUS_H

namespace LOFAR {

namespace MessageBus {
  // Generic initialisation of the Messaging framework
  void init();
}

} // namespace LOFAR

#endif

