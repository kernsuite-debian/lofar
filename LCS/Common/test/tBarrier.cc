//# tBarrier.cc: Test program for thread synchronization barrier
//#
//# Copyright (C) 2016
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
//# $Id: tBarrier.cc 34983 2016-07-14 17:29:29Z amesfoort $

#include <lofar_config.h>

#include <unistd.h> // alarm(3)
#include <Common/Thread/Thread.h>
#include <Common/Thread/Barrier.h>

using namespace std;
using namespace LOFAR;

static void testTrivial()
{
#ifdef USE_THREADS
  Barrier bar(1);
  bar.wait();
#endif
}

#ifdef USE_THREADS
static Barrier barTestUse(4); // for 3 thread + main thread

struct Thr {
  Thr() : thread(this, &Thr::f) { }

private:
  void f() {
    barTestUse.wait();
    barTestUse.wait();
    barTestUse.wait();
  }

  Thread thread;
};
#endif

static void testUse()
{
#ifdef USE_THREADS
  Thr t1;
  Thr t2;
  Thr t3;

  barTestUse.wait();
  barTestUse.wait();
  barTestUse.wait();
#endif
}

static void testError()
{
#ifdef USE_THREADS
  int exc = 0;

  // count 0 is invalid
  try {
    Barrier(0);
  } catch (Exception& ) {
    exc = 1;
  }

  ASSERT(exc == 1);
#endif
}


int main()
{
  INIT_LOGGER("tBarrier");

  alarm(10); // don't wait until ctest timeout on deadlock

  testTrivial();
  testUse();
  testError();

  return 0;
}
