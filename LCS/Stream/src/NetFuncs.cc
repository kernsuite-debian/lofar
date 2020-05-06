//# NetFuncs.cc: 
//#
//# Copyright (C) 2015, 2017
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
//# $Id$

#include <lofar_config.h>

#include <Stream/NetFuncs.h>
#include <Stream/FileStream.h>
#include <Common/Thread/Mutex.h>
#include <Common/LofarLogger.h>
#include <Common/SystemCallException.h>

#include <cstring>
#include <cstdio>
#include <netdb.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/socket.h>

#include <boost/format.hpp>
using boost::format;

namespace {
  LOFAR::Mutex getAddrInfoMutex;
}

namespace LOFAR {

  safeAddrInfo::safeAddrInfo()
  :
    addrinfo(0)
  {
  }

  safeAddrInfo::~safeAddrInfo() {
    if(addrinfo) freeaddrinfo(addrinfo);
  }

  void safeGetAddrInfo(safeAddrInfo &result, bool TCP, const std::string &hostname, uint16 port) {
    struct addrinfo hints;
    char portStr[16];

    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_INET; // IPv4
    hints.ai_flags = AI_NUMERICSERV; // we only use numeric port numbers, not strings like "smtp"

    if (TCP) {
      hints.ai_socktype = SOCK_STREAM;
      hints.ai_protocol = IPPROTO_TCP;
    } else {
      hints.ai_socktype = SOCK_DGRAM;
      hints.ai_protocol = IPPROTO_UDP;
    }

    snprintf(portStr, sizeof portStr, "%hu", port);

    {
      // getaddrinfo does not seem to be thread safe
      ScopedLock sl(getAddrInfoMutex);

      int retval;

      if ((retval = getaddrinfo(hostname.c_str(), portStr, &hints, &result.addrinfo)) != 0) {
        const std::string errorstr = gai_strerror(retval);

        throw SystemCallException(str(format("getaddrinfo(%s): %s") % hostname % errorstr), 0, THROW_ARGS); // TODO: SystemCallException also adds strerror(0), which is useless here
      }
    }
  }

  IfAddrs::IfAddrs() {
    if (getifaddrs(&ifa) != 0) {
      THROW_SYSCALL("getifaddrs");
    }
  }

  IfAddrs::~IfAddrs() {
    if (ifa) {
      freeifaddrs(ifa);
    }
  }

  std::set<std::string> myInterfaces(bool as_fqdn, bool onlyWithLink, long speedBps) {
    IfAddrs ifas;
    std::set<std::string> if_names;

    struct ifaddrs *ap;
    for (ap = ifas.ifa; ap != NULL; ap = ap->ifa_next) {

      if (ap->ifa_addr == NULL) {
        continue;
      }
      if (!(ap->ifa_flags & IFF_UP)) {
        continue;
      }

      int salen = 0;
      int family = ap->ifa_addr->sa_family;
      if (family == AF_INET) {
        salen = sizeof(struct sockaddr_in);
      } else if (family == AF_INET6) {
        struct sockaddr_in6 *sin6 = (struct sockaddr_in6 *)ap->ifa_addr;
        if (IN6_IS_ADDR_LINKLOCAL(&sin6->sin6_addr) ||
            IN6_IS_ADDR_MC_LINKLOCAL(&sin6->sin6_addr)) {
          continue; // IPv6 link-local
        }

        salen = sizeof(struct sockaddr_in6);
      } else {
        continue;
      }

      if (onlyWithLink) {
        string if_carrier_file_name(str(format("/sys/class/net/%s/carrier") % ap->ifa_name));

        FileStream file(if_carrier_file_name);
        if (file.readLine() != "1")
          continue;
      }

      if (speedBps > 0) {
        try {
          string if_speed_file_name(str(format("/sys/class/net/%s/speed") % ap->ifa_name));

          FileStream file(if_speed_file_name);

          // file contains one line, with speed of the interface in Mbps
          string line = file.readLine();

          // convert to Bps
          long ifSpeedBps = stol(line) * 1000000L;

          if(ifSpeedBps != speedBps)
            continue;
        } catch(LOFAR::SystemCallException) {
            continue;
        }
      }

      if (as_fqdn) {
        // See safeGetAddrInfo() above. If getaddrinfo does not seem to be thread safe,
        // then better lock getnameinfo too, and with the same mutex.
        ScopedLock sl(getAddrInfoMutex);

        char hostname[NI_MAXHOST];
        int retval = getnameinfo(ap->ifa_addr, salen, hostname, sizeof(hostname),
                                 NULL, 0, NI_NAMEREQD);
        if (retval != 0) {
          const std::string errorstr = gai_strerror(retval);
          LOG_DEBUG_STR(str(format("myHostnames(): failed to getnameinfo() for some addr of type %d on interface %s: %s") %
                            family % ap->ifa_name % errorstr));
          continue;
        }

        if_names.insert(hostname);
      } else {
        if_names.insert(string(ap->ifa_name));
      }
    }

    return if_names;
  }

  struct sockaddr getInterfaceIP(const std::string &iface) {
    int fd = -1;
    struct ifreq ifr;

    if ((fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
      THROW_SYSCALL("socket");

    try {
      memset(&ifr, 0, sizeof ifr);
      snprintf(ifr.ifr_name, sizeof ifr.ifr_name, "%s", iface.c_str());

      if (ioctl(fd, SIOCGIFADDR, &ifr) < 0)
        THROW_SYSCALL("ioctl");
    } catch(...) {
      close(fd);
      throw;
    }

    close(fd);
    return ifr.ifr_addr;
  }

  int getSocketPort(int fd) {
    struct sockaddr_in sin;
    socklen_t addrlen = sizeof sin;

    if (getsockname(fd, (struct sockaddr *)&sin, &addrlen) < 0)
      THROW_SYSCALL("getsockname");

    if (sin.sin_family != AF_INET)
      return 0;

    if (addrlen != sizeof sin)
      return 0;

    return ntohs(sin.sin_port);
  }
}
