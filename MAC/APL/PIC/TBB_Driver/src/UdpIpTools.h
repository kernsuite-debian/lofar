//#  -*- mode: c++ -*-
//#
//#  UdpIpTools.h: III
//#
//#  Copyright (C) 2002-2004
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
//#  $Id$

#ifndef UDP_IP_TOOLS_H_
#define UDP_IP_TOOLS_H_

#include <Common/LofarTypes.h>

namespace LOFAR {
	namespace TBB {

static const uint16 BASEUDPPORT = 0x7BB0; // (=31664) start numbering src and dst UDP ports at this number
static const uint16 TRANSIENT_FRAME_SIZE = 2140; // bytes, header(88) + payload(2048) + CRC(4)
static const uint16 SUBBANDS_FRAME_SIZE = 2040;  // bytes, header(88) + payload(1948) + CRC(4)

//==============================================================================
// Convert a string containing a Ethernet MAC address
// to an array of 6 bytes.
void string2mac(const char* macstring, uint32 mac[2]);
// Convert a string containing an IP address
// to an array of 6 bytes.
uint32 string2ip(const char* ipstring);
// Setup an appropriate UDP/IP header
void setup_udpip_header(uint32 boardnr, uint32 mode, const char *srcip, const char *dstip, uint32 ip_hdr[5], uint32 udp_hdr[2]);
// Compute the 16-bit 1-complements checksum for the IP header.
uint16 compute_ip_checksum(void* addr, int count);
//==============================================================================

	} // end TBB namespace
} // end LOFAR namespace

#endif /* UDP_IP_TOOLS_H_ */
