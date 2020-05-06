//# cpu_utils.h: Helper functions for cpu specific functionality
//# Copyright (C) 2012-2013  ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
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
//# $Id$

// \file
// Include for processor optimalizetion functionality

#ifndef LOFAR_COINTERFACE_CPU_UTILS_H
#define LOFAR_COINTERFACE_CPU_UTILS_H

#include <CoInterface/Parset.h>
#include <vector>

namespace LOFAR
{
  namespace Cobalt
  {
    // Request no limit on amount of locked memory.
    // Throws a SystemCallException on failure.
    void unlimitedLockedMemory();

    // Locks all memory, current and future, to prevent it from being swapped.
    // Throws a SystemCallException on failure.
    void lockAllMemory();

    // Bind the thread to the specified socket, saves this configuration for rebindCPU()
    void bindCPU(unsigned socket, const std::vector<unsigned> &skipCores = std::vector<unsigned>());

    // Bind the thread to the same cores specified earlier, to restore the configuration
    void rebindCPU();

    // Returns all cores we are bound to
    std::vector<unsigned> cpuBinding();

    // Bind the memory to the specified socket. Moves already allocated memory.
    //
    // NOTE: Does NOT move pinned memory, f.e. created by pinAllMemory() or cuMemHostAlloc()
    void bindMemory(int socket);

    // Return the socket hosting the given memory (or -1 if unknown)
    int socketOfMemory(void *ptr);
  }
}
#endif
