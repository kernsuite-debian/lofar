//# t_cpu_utils.cc: test cpu utilities
//# Copyright (C) 2013  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <CoInterface/cpu_utils.h>

#include <cstring>
#include <cstdio>
#include <sched.h>
#include <cstdlib>
#include <omp.h>
#include <string>
#include <iostream>

#include <Common/LofarLogger.h>
#include <Common/SystemCallException.h>
#include <Common/SystemUtil.h>
#include <CoInterface/PrintVector.h>

#include <UnitTest++.h>

using namespace std;
using namespace LOFAR::Cobalt;

const unsigned nprocs = sysconf( _SC_NPROCESSORS_ONLN );

static void test_cpu(unsigned cpuId)
{
  int status = 0;

  bindCPU(cpuId);

  // Validate the correct setting of the affinity
  cpu_set_t mask;  
  if (sched_getaffinity(0, sizeof(cpu_set_t), &mask) != 0)
    THROW_SYSCALL("sched_getaffinity");

  // expect alternating on cbt nodes
  // (the original test code intended this, but was broken in many ways (still a poor idea to make it so specific))
  int expect = !cpuId;
  for (unsigned i = 0; i < nprocs; i++) {
    if (CPU_ISSET(i, &mask) != expect) {
      LOG_FATAL_STR("cpuId=" << cpuId << " Found that core " << i << " is" << (!expect ? " " : " NOT ") <<
                    "in the set while it should" << (expect ? " " : " NOT ") << "be!");
      status = 1;
    }
    expect ^= 1;
  }

  CHECK(status == 0);
}

static void test_memory(unsigned cpuId)
{
  bindMemory(cpuId);

  void *buffer = malloc(1024);
  ASSERT(buffer);

  // the buffer will almost surely be on the wrong socket for at least one value of cpuId
  CHECK_EQUAL(cpuId, socketOfMemory(buffer));

  free(buffer);
}

TEST(cpu0) {
  test_cpu(0);
}

TEST(cpu1) {
  test_cpu(1);
}

TEST(cpu_avoid_cores) {
  bindCPU(0);

  // Check which cores we are bound to
  cpu_set_t mask;  
  if (sched_getaffinity(0, sizeof(cpu_set_t), &mask) != 0)
    THROW_SYSCALL("sched_getaffinity");

  // Need a multi-core machine
  if(CPU_COUNT(&mask) < 2)
    return;

  // Find at least two cores we're bound to
  int first = -1, second = -1;

  for (unsigned i = 0; i < CPU_SETSIZE; i++) {
    if (CPU_ISSET(i, &mask)) {
      if (first == -1)
        first = i;
      else if (second == -1)
        second = i;
      else
        break;
    }
  }

  CHECK(first != -1);
  CHECK(second != -1);

  // Avoid binding to the first core
  bindCPU(0, std::vector<unsigned>{ static_cast<unsigned>(first) });

  // Verify binding
  if (sched_getaffinity(0, sizeof(cpu_set_t), &mask) != 0)
    THROW_SYSCALL("sched_getaffinity");

  CHECK(!CPU_ISSET(first, &mask));
  CHECK(CPU_ISSET(second, &mask));
}

TEST(openmp_binding) {
  bindCPU(0);

  const vector<unsigned> allCores = cpuBinding();

  CHECK(allCores.size() >= 2);

  // Avoid binding on first core
  const unsigned forbiddenCore = allCores[0];

  bindCPU(0, vector<unsigned>{ forbiddenCore });

  cout << "Selected forbidden core: " << forbiddenCore << endl;

  #pragma omp parallel for num_threads(16)
  for(int i = 0; i < 16; ++i)
  {
     const vector<unsigned> threadCores = cpuBinding();

     #pragma omp critical (cout)
     { cout << "Thread is bound to " << threadCores << endl; }

     // forbidden core should NOT be in our list
     CHECK(find(threadCores.begin(), threadCores.end(), forbiddenCore) == threadCores.end());

     // other cores should be in our list
     for(size_t i = 0; i < allCores.size(); i++) {
       unsigned core = allCores[i];

       if (core == forbiddenCore)
         continue;

       CHECK(find(threadCores.begin(), threadCores.end(), core) != threadCores.end());
     }
  }
} 

TEST(memory0) {
  test_memory(0);
}

TEST(memory1) {
  test_memory(1);
}

TEST(memorymove) {
  if(nprocs >= 2) {
    bindMemory(0);

    void *buffer = malloc(1024);
    ASSERT(buffer);

    CHECK_EQUAL(0, socketOfMemory(buffer));

    // move the memory
    bindMemory(1);

    CHECK_EQUAL(1, socketOfMemory(buffer));
  }
}

int main()
{
  INIT_LOGGER("t_cpu_utils");

  return UnitTest::RunAllTests() > 0;
}

