//# NetFuncs.h: 
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

#ifndef LOFAR_LCS_STREAM_NETFUNCS_H
#define LOFAR_LCS_STREAM_NETFUNCS_H

#include <Common/LofarTypes.h>

#include <string>
#include <set>
#include <sys/types.h>
#include <ifaddrs.h>
#include <netdb.h>

namespace LOFAR {
  // A wrapper on 'struct addrInfo' to make sure it is freed correctly
  struct safeAddrInfo {
    struct addrinfo *addrinfo;

    safeAddrInfo();
    ~safeAddrInfo();
  };

  // A wrapper on 'struct ifaddrs' to make sure it is freed correctly
  struct IfAddrs {
    struct ifaddrs *ifa;

    IfAddrs();
    ~IfAddrs();
  };

  // Do a thread-safe lookup of 'hostname:port', and store the result in 'result'.
  // TCP=false means UDP.
  void safeGetAddrInfo(safeAddrInfo &result, bool TCP, const std::string &hostname, uint16 port);

  // Returns either the network interface name, or the full hostnames (FQDNs) of the network interfaces in this machine.
  // Includes names (if avail) of IPv4, IPv6, and loopback interfaces.
  // Excludes names of interfaces that are down.
  // Also not included is the system hostname if it is different from any interface hostname (e.g. on cbt nodes).
  std::set<std::string> myInterfaces(bool as_fqdn=true, bool onlyWithLink=false, long speedBps=-1);

  // Retrieve the IP of an interface ("eth0") as an 'ifreq' struct, which can be used as sockaddr.
  struct sockaddr getInterfaceIP(const std::string &iface);

  // Returns the TCP/UDP port number allocated to a socket, or 0 if unknown.
  int getSocketPort(int fd);
}

#endif
