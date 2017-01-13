//# IOPriority.h: Linux specific priority functions
//# Copyright (C) 2011-2013, 2016
//# ASTRON (Netherlands Institute for Radio Astronomy)
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
//# $Id: IOPriority.h 36029 2016-11-21 11:04:38Z mol $

#ifndef LOFAR_COMMON_IOPRIORITY_H
#define LOFAR_COMMON_IOPRIORITY_H

#define IOPRIO_BITS             (16)
#define IOPRIO_CLASS_SHIFT      (13)
#define IOPRIO_PRIO_MASK        ((1UL << IOPRIO_CLASS_SHIFT) - 1)

#define IOPRIO_PRIO_CLASS(mask) ((mask) >> IOPRIO_CLASS_SHIFT)
#define IOPRIO_PRIO_DATA(mask)  ((mask) & IOPRIO_PRIO_MASK)
#define IOPRIO_PRIO_VALUE(class, data)  (((class ) << IOPRIO_CLASS_SHIFT) | data)

#include <pwd.h>
#include <sched.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <malloc.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/syscall.h>   /* For SYS_xxx definitions */
#include <sys/resource.h>

#if defined __linux__
#include <linux/version.h>
#endif

namespace LOFAR
{

enum {
  IOPRIO_WHO_PROCESS = 1,
  IOPRIO_WHO_PGRP,
  IOPRIO_WHO_USER,
};


enum {
  IOPRIO_CLASS_NONE,
  IOPRIO_CLASS_RT,
  IOPRIO_CLASS_BE,
  IOPRIO_CLASS_IDLE,
};


inline int ioprio_set(int which, int who, int ioprio)
{
#if defined __linux__
  #if (LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,13))
  return syscall(SYS_ioprio_set, which, who, ioprio);
  #else
  return -1;
  #endif
#else
  return -1;
#endif
}

inline int ioprio_get(int which, int who)
{
#if defined __linux__
  #if (LINUX_VERSION_CODE >= KERNEL_VERSION(2,6,13))
  return syscall(SYS_ioprio_get, which, who);
  #else
  return -1;
  #endif
#else
  return -1;
#endif
}

// realTime true requires CAP_SYS_ADMIN. false does not require a capability,
// but does set to the more favorable prio 0 with IOPRIO_CLASS_BE (default 4).
inline void setIOpriority(bool realTime)
{
  if (ioprio_set(IOPRIO_WHO_PROCESS, getpid(),
                 realTime ? IOPRIO_PRIO_VALUE(IOPRIO_CLASS_RT, 7) :
                            IOPRIO_PRIO_VALUE(IOPRIO_CLASS_BE, 0)) != 0) {
    switch (errno) {
    case EPERM:
    {
      struct passwd *user = getpwnam("lofarsys");
      if ((user != NULL) && (getuid() != user->pw_uid))
        LOG_WARN_STR("Failed to set IO priority, permission denied");
      else
        LOG_ERROR_STR("Failed to set IO priority, capability CAP_SYS_ADMIN not set?");
    } break;
    case EINVAL:
    case ESRCH:
    default:
      LOG_ERROR_STR("Failed to set IO priority: " << errno);
    }
  }
}


inline void setRTpriority()
{
  int priority = sched_get_priority_min(SCHED_RR);
  struct sched_param sp;
  sp.sched_priority = priority;

  if (sched_setscheduler(0, SCHED_RR, &sp) < 0) {
    switch (errno) {
    case EPERM:
    {
      struct passwd *user = getpwnam("lofarsys");
      if ((user != NULL) && (getuid() != user->pw_uid))
        LOG_WARN_STR("Failed to set RT priority, permission denied");
      else
        LOG_ERROR_STR("Failed to set RT priority, capability CAP_SYS_NICE not set?");
    } break;

    case EINVAL:
    case ESRCH:
    default:
      LOG_ERROR_STR("Failed to set RT priority: " << errno);
    }
  }
}


inline void tweakMalloc()
{
  // Reduce calls to brk()
  mallopt(M_TOP_PAD, 16*1024*1024);
  mallopt(M_TRIM_THRESHOLD, 16*1024*1024);
}


inline void lockInMemory(rlim_t memLockLimit = RLIM_INFINITY)
{
  struct passwd *user = getpwnam("lofarsys");
  bool am_lofarsys = (user != NULL) && (getuid() == user->pw_uid);

  if (mlockall(MCL_CURRENT | MCL_FUTURE) < 0) {
    switch (errno) {
    case ENOMEM:
    case EPERM:
    {
      if (am_lofarsys)
        LOG_ERROR_STR("Failed to lock application in memory, capability CAP_IPC_LOCK not set?");
      else
        LOG_WARN_STR("Failed to lock application in memory, permission denied");
    } break;
    case EINVAL:
    default:
      LOG_ERROR_STR("Failed to lock application in memory: flags invalid");
    }
  }

  const struct rlimit limit = { memLockLimit, memLockLimit };

  // Set MEMLOCK limit
  if (setrlimit(RLIMIT_MEMLOCK, &limit) < 0) {
    if (am_lofarsys)
      LOG_ERROR_STR("Failed to set MEMLOCK limit");
    else
      LOG_WARN_STR("Failed to set MEMLOCK limit");
  }

  // Set DATA limit
  if (setrlimit(RLIMIT_DATA, &limit) < 0) {
    if (am_lofarsys)
      LOG_ERROR_STR("Failed to set DATA limit");
    else
      LOG_WARN_STR("Failed to set DATA limit");
  }
}

} // namespace LOFAR

#endif
