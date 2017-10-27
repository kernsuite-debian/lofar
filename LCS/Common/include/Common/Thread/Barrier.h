//#  Barrier.h: thread synchronization barrier
//#
//#  Copyright (C) 2016
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id: Barrier.h 36879 2017-03-17 16:19:45Z amesfoort $

#ifndef LOFAR_LCS_COMMON_BARRIER_H
#define LOFAR_LCS_COMMON_BARRIER_H

#ifdef USE_THREADS

#include <pthread.h>

#if !_POSIX_BARRIERS  // OS X
// Don't bother yet providing our own barrier impl. We hardly use it. Just warn.
#warning _POSIX_BARRIERS not defined on this system: code using LOFAR::Barrier will not compile
#else

#include <Common/LofarLogger.h>
#include <Common/SystemCallException.h>

namespace LOFAR {

class Barrier {
public:
  explicit Barrier(unsigned count)
  {
    int rv = pthread_barrier_init(&bar, NULL, count);
    if (rv != 0) {
      throw SystemCallException("pthread_barrier_init", rv, THROW_ARGS);
    }
  }

  ~Barrier()
  {
    int rv = pthread_barrier_destroy(&bar);
    if (rv != 0) {
      // get backtrace w/out stack unwinding from destr (could be done w/out exc)
      try {
        throw SystemCallException("pthread_barrier_destroy", rv, THROW_ARGS);
      } catch (SystemCallException &exc) {
        LOG_ERROR_STR("pthread_barrier_destroy() failed: " << exc.what());
      }
    }
  }

  void wait()
  {
    int rv = pthread_barrier_wait(&bar);
    if (rv != 0 && rv != PTHREAD_BARRIER_SERIAL_THREAD) {
      throw SystemCallException("pthread_barrier_wait", rv, THROW_ARGS);
    }
  }

private:
  pthread_barrier_t bar;

  // don't use
  Barrier();
  Barrier(const Barrier& ); // cannot wait or destroy on a copy
  Barrier& operator=(const Barrier& ); // idem
};

} // namespace LOFAR

#endif
#endif

#endif
