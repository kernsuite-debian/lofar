//# Sem_t.h: C++ wrapper around the POSIX unnamed semaphore interface
//# Copyright (C) 2016  ASTRON (Netherlands Institute for Radio Astronomy)
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
//# $Id: Sem_t.h 37655 2017-06-19 12:40:06Z amesfoort $

#ifndef LOFAR_LCS_COMMON_SEMT_H
#define LOFAR_LCS_COMMON_SEMT_H

#include <semaphore.h>
#include <cerrno>

#include <Common/SystemCallException.h>
#include <Common/LofarLogger.h>

namespace LOFAR {

// POSIX unnamed semaphore
// This semaphore is also usable for interprocess communication.
// Signal handlers can use post_nothrow() (async-signal-safe).
// (The Semaphore name is used by a pthreads based impl with other adv/disadv.)
class Sem_t {
  ::sem_t sem;

public:
  explicit Sem_t(int pshared = 0, unsigned int value = 0) {
    if (UNLIKELY(::sem_init(&sem, pshared, value) < 0)) {
      THROW_SYSCALL("sem_init");
    }
  }

  // no other processes or threads must be waiting on this semaphore
  ~Sem_t() {
    if (UNLIKELY(::sem_destroy(&sem) < 0)) {
      // get backtrace w/out stack unwinding from destr (could be done w/out exc)
      try {
        THROW_SYSCALL("sem_destroy");
      } catch (SystemCallException &exc) {
        LOG_ERROR_STR("sem_destroy() failed: " << exc.what());
      }
    }
  }

  void getvalue(int *semval) {
    // ignore ret val; errno can only be EINVAL; shows up at any other call
    ::sem_getvalue(&sem, semval);
  }

  // somewhat more useful getvalue() interface when ignoring ret val anyway
  int getvalue() {
    int semval;
    ::sem_getvalue(&sem, &semval);
    return semval;
  }

  // not async-signal-safe due to error handler; see post_nothrow() below
  void post() {
    if (UNLIKELY(::sem_post(&sem) < 0)) {
      THROW_SYSCALL("sem_post");
    }
  }

  // async-signal-safe
  int post_nothrow() {
    return ::sem_post(&sem);
  }

  void wait() {
    if (UNLIKELY(::sem_wait(&sem) < 0)) {
      THROW_SYSCALL("sem_wait");
    }
  }

  bool trywait() {
    if (::sem_trywait(&sem) < 0) {
      if (errno == EAGAIN) {
        return false;
      }
      THROW_SYSCALL("sem_trywait");
    }
    return true;
  }

#if _POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600  // OS X does not have sem_timedwait()
  bool timedwait(const struct timespec *abs_timeout) {
    if (::sem_timedwait(&sem, abs_timeout) < 0) {
      if (errno == ETIMEDOUT) {
        return false;
      }
      THROW_SYSCALL("sem_timedwait");
    }
    return true;
  }
#endif

private:
  Sem_t(const Sem_t&);
  Sem_t& operator=(const Sem_t&);
};

} // namespace LOFAR

#endif
