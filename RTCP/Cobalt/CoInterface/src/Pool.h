//# Pool.h
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

#ifndef LOFAR_COINTERFACE_POOL_H
#define LOFAR_COINTERFACE_POOL_H

#include <CoInterface/Queue.h>
#include <CoInterface/SmartPtr.h>

namespace LOFAR
{
  namespace Cobalt
  {
    // The pool operates using a free and a filled queue to cycle through buffers. Producers
    // move elements free->filled, and consumers move elements filled->free. By
    // wrapping the elements in a SmartPtr, memory leaks are prevented.
    //
    // If warn_on_bad_performance == True, the queues will log warnings if they are not filled/freed
    // fast enough (see Queue.h for more details).
    //
    // batch_size is the number of elements appended to "filled" in short repetition, too fast for the consumer
    // to reasonably consume between appends.
    template <typename T>
    struct Pool
    {
      typedef T element_type;

      Queue< SmartPtr<element_type> > free;
      Queue< SmartPtr<element_type> > filled;

      Pool(const std::string &name, bool warn_on_bad_performance, int batch_size = 1)
      :
        free(name + " [.free]", warn_on_bad_performance ? true : false, -1),
        filled(name + " [.filled]", false, warn_on_bad_performance ? batch_size : -1)
      {
      }
    };
  }
}

#endif
