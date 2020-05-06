//# cpu_utils.cc
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

#include <sched.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/mman.h>
#include <fstream>
#include <algorithm>
#include <pthread.h>

#include <Common/LofarLogger.h>
#include <CoInterface/Parset.h>
#include <CoInterface/Exceptions.h>
#include <CoInterface/PrintVector.h>

#ifdef HAVE_LIBNUMA
#include <numa.h>
#include <numaif.h>
#endif

#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>

using namespace std;

namespace LOFAR
{
  namespace Cobalt
  {
    static cpu_set_t lastRequestedBinding;
    static bool requestedBinding = false;

    static vector<unsigned> cpusetToVector(const cpu_set_t &cpuSet)
    {
       vector<unsigned> cores;

       for (size_t c = 0; c < CPU_SETSIZE; c++)
         if (CPU_ISSET(c, &cpuSet))
           cores.push_back(c);

       return cores;
    }

    vector<unsigned> cpuBinding()
    {
      cpu_set_t mask;
      pthread_t thread = pthread_self();

      if (pthread_getaffinity_np(thread, sizeof(cpu_set_t), &mask) != 0)
        THROW_SYSCALL("pthread_getaffinity_np");

      return cpusetToVector(mask);
    }

    void bindCPU(unsigned socket, const std::vector<unsigned> &skipCores)
    {
      LOG_DEBUG_STR("[NUMA] Binding to CPU " << socket);

      // Get the number of cores
      unsigned numCores = sysconf(_SC_NPROCESSORS_ONLN);

      // Determine the cores local to the specified socket
      vector<unsigned> localCores;

      for (unsigned core = 0; core < numCores; ++core) {
        // The file below contains an integer indicating the physical CPU
        // hosting this core.
        std::ifstream fs(str(boost::format("/sys/devices/system/cpu/cpu%u/topology/physical_package_id") % core).c_str());

        unsigned physical_cpu;
        fs >> physical_cpu;

        if (!fs.good())
          continue;

        if (find(skipCores.begin(), skipCores.end(), core) != skipCores.end())
          continue;

        // Add this core to the mask if it matches the requested CPU
        if (physical_cpu == socket)
          localCores.push_back(core);
      }

      if (localCores.empty())
        THROW(GPUProcException, "No suitable cores found for CPU: " << socket << " (avoiding cores " << skipCores << ")");

      // put localCores in a cpu_set
      cpu_set_t maskRequested;

      CPU_ZERO(&maskRequested); 

      for (vector<unsigned>::const_iterator i = localCores.begin(); i != localCores.end(); ++i)
        CPU_SET(*i, &maskRequested);

      LOG_INFO_STR("[NUMA] Requested core affinity: " << cpusetToVector(maskRequested));

      // assign the mask and set the affinity
      if (sched_setaffinity(0, sizeof(cpu_set_t), &maskRequested) != 0)
        THROW_SYSCALL("sched_setaffinity");

      lastRequestedBinding = maskRequested;
      requestedBinding = true;
    }

    void rebindCPU() {
      if (!requestedBinding)
        // bindCPU() was never called
        return;

      // assign the mask and set the affinity
      if (sched_setaffinity(0, sizeof(cpu_set_t), &lastRequestedBinding) != 0)
        THROW_SYSCALL("sched_setaffinity");
    }

    void unlimitedLockedMemory() {
      // Remove limits on locked memory
      struct rlimit unlimited = { RLIM_INFINITY, RLIM_INFINITY };

      if (setrlimit(RLIMIT_MEMLOCK, &unlimited) < 0)
        THROW_SYSCALL("setrlimit(RLIMIT_MEMLOCK, unlimited)");
    }

    void lockAllMemory() {
      if (mlockall(MCL_CURRENT | MCL_FUTURE) < 0)
      {
        THROW_SYSCALL("mlockall(MCL_CURRENT | MCL_FUTURE)");
      } else {
        LOG_DEBUG("All memory is now pinned.");
      }
    }

    void bindMemory(int socket) {
    #ifdef HAVE_LIBNUMA
        if (numa_available() != -1) {
          // force node + memory binding for future allocations
          struct bitmask *numa_node = numa_allocate_nodemask();
          numa_bitmask_clearall(numa_node);
          numa_bitmask_setbit(numa_node, socket);
          numa_bind(numa_node);
          numa_bitmask_free(numa_node);

          // only allow allocation on this node in case
          // the numa_alloc_* functions are used
          numa_set_strict(1);

          // retrieve and report memory binding
          numa_node = numa_get_membind();
          vector<string> nodestrs;
          for (size_t i = 0; i < numa_node->size; i++)
            if (numa_bitmask_isbitset(numa_node, i))
              nodestrs.push_back(str(boost::format("%s") % i));

          // migrate currently used memory to our node
          numa_migrate_pages(0, numa_all_nodes_ptr, numa_node);

          numa_bitmask_free(numa_node);

          LOG_DEBUG_STR("[NUMA] Bound to memory on nodes " << nodestrs);
        } else {
          LOG_INFO("[NUMA] Cannot bind memory: libnuma reports NUMA is not available");
        }
    #else
        LOG_WARN("[NUMA] Cannot bind memory (no libnuma support)");
    #endif
    }

    int socketOfMemory(void *ptr)
    {
    #ifdef HAVE_LIBNUMA
      int status[1];
      int ret_code;

      status[0] = -1;
      ret_code = numa_move_pages(0 /*self memory */, 1, &ptr,
        NULL, status, 0);

      if (ret_code) {
        THROW_SYSCALL("numa_move_pages");
      }

      return status[0];
    #else
      return -1;
    #endif
    }
  }
}

