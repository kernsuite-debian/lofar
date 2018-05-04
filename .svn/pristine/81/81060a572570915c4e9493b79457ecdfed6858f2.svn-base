//# tSem_t.cc: simple test program for POSIX semaphore wrapper
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
//# $Id$

#include <lofar_config.h>

#include <csignal>
#include <Common/Thread/Sem_t.h>
#include <Common/LofarLogger.h>

using namespace LOFAR;

static volatile std::sig_atomic_t sigint_seen; // sig_atomic_t is one of the few types a signal handler may read/write from/to
static Sem_t *sigSem_p;

static void sigHandler(int sig_nr)
{
  if (sig_nr == SIGINT) {
    sigint_seen = 1;
    int err = sigSem_p->post_nothrow();
    if (err) {
      // printf not safe in signal handler...
      const char msg[] = "ERROR: post";
      size_t msgLen = 11;
      if (::write(STDERR_FILENO, msg, msgLen) != 0) {
        sigint_seen = 2;
      }
    }
  }
}

static void testSimple() {
  int val0 = 3;
  Sem_t sem(0, val0);

  ASSERT(sem.getvalue() == val0);

  sem.wait();
  ASSERT(sem.getvalue() == val0-1);

  sem.post();
  sem.post();

  for (int i = 0; i < val0+1; i++) {
    sem.wait();
  }
  ASSERT(sem.getvalue() ==  0);

  // test with release from signal handler
  struct sigaction sa;
  sa.sa_handler = sigHandler;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = 0;
  ASSERT(sigaction(SIGINT, &sa, NULL) == 0); // keyb INT (typically Ctrl-C)

  Sem_t sigSem;
  sigSem_p = &sigSem;

  std::raise(SIGINT);
  sigSem.wait();
  ASSERT(sigint_seen == 1);

  // trywait
  ASSERT(!sem.trywait());
  sem.post();
  ASSERT(sem.trywait());

#if _POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600  // OS X does not have sem_timedwait()
  LOG_INFO("Testing timedwait wrapper");

  // timedwait
  struct timespec ts1 = {::time(0), 0};
  ASSERT(!sem.timedwait(&ts1));

  sem.post();
  struct timespec ts2 = {::time(0)-1, 0};
  // underlying timedwait is specified to succeed if decr is possible immediately,
  // even if abs_timeout already passed
  ASSERT(sem.timedwait(&ts2));
#endif
}

int main()
{
  INIT_LOGGER("tSem_t");

  alarm(8); // don't wait for default test timeout on deadlock

  testSimple(); // impl is a thin wrapper around system lib functions, so a few simple tests is enough

  return 0;
}
