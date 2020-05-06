//#  -*- mode: c++ -*-
//#
//#  UdpIpTools.cc: III
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
//#  $Id: UdpIpTools.h 35973 2016-11-14 11:59:30Z donker $

#include <lofar_config.h>
#include "UdpIpTools.h"
#include <APL/TBB_Protocol/TBB_Protocol.ph>
#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <netinet/in.h>
#include <net/ethernet.h>
#include <cstdio>


namespace LOFAR {
    using namespace TBB_Protocol;

	namespace TBB {

void string2mac(const char* macstring, uint32 mac[2])
{
	unsigned int hx[ETH_ALEN] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };

	sscanf(macstring, "%x:%x:%x:%x:%x:%x", &hx[5], &hx[4], &hx[3], &hx[2], &hx[1], &hx[0]);

	mac[0]   = ((hx[0] & 0xFF))
			+ ((hx[1] & 0xFF) << 8)
			+ ((hx[2] & 0xFF) << 16)
			+ ((hx[3] & 0xFF) << 24);

	mac[1]   = ((hx[4] & 0xFF))
			+ ((hx[5] & 0xFF) << 8);

	for ( int i = 0; i < 2; i++) {
		LOG_DEBUG_STR(formatString("MAC[%d]= 0x%08X", i, mac[i]));
	}
}

uint32 string2ip(const char* ipstring)
{
	uint32 result;
	unsigned int hx[sizeof(uint32)] = { 0x00, 0x00, 0x00, 0x00 };

	sscanf(ipstring, "%d.%d.%d.%d", &hx[3], &hx[2], &hx[1], &hx[0]);

	result   = ((hx[0] & 0xFF))
			+ ((hx[1] & 0xFF) << 8)
			+ ((hx[2] & 0xFF) << 16)
			+ ((hx[3] & 0xFF) << 24);

	return result;
}

uint16 compute_ip_checksum(void* addr, int count)
{
	// Compute Internet Checksum for "count" bytes
	// beginning at location "addr".

	uint32 sum = 0;

	uint16* addr16 = static_cast<uint16*>(addr);
	while (count > 1) {
		//  This is the inner loop
		sum += *addr16++;
		count -= 2;
	}

	//  Add left-over byte, if any
	if (count > 0) {
		sum += * reinterpret_cast<uint8 *>(addr16);
	}
	//  Fold 32-bit sum to 16 bits
	while (sum >> 16) {
		sum = (sum & 0xffff) + (sum >> 16);
	}
	return(~sum) & 0xffff;
}

void setup_udpip_header(uint32 boardnr, uint32 mode, const char *srcip, const char *dstip, uint32 ip_hdr[5], uint32 udp_hdr[2])
{
	uint32 iphdr[5];
	uint32 udphdr[2];

	uint32 ip_hdr_size  = sizeof(iphdr); // bytes
	uint32 udp_hdr_size = sizeof(udphdr); // bytes

	uint32 data_size = 0;

	if (mode == TBB_MODE_TRANSIENT) data_size = TRANSIENT_FRAME_SIZE;
	if (mode == TBB_MODE_SUBBANDS) data_size = SUBBANDS_FRAME_SIZE;

	// IP header values
	uint32 version          = 4; // IPv4
	uint32 ihl              = 5; // 5 x uint32, no options field
	uint32 tos              = 0;
	uint32 total_length     = ip_hdr_size + udp_hdr_size + data_size;
	uint32 identification   = 0;
	uint32 flags_offset     = 0x2 << 13;
	uint32 ttl              = 128;
	uint32 protocol         = 0x11;
	uint16 header_checksum  = 0; // set to zero for checksum calculation
	uint32 src_ip_address   = string2ip(srcip);
	uint32 dst_ip_address   = string2ip(dstip);
	// UDP header values
	uint32 src_udp_port     = BASEUDPPORT + boardnr;
	uint32 dst_udp_port     = BASEUDPPORT + boardnr;
	uint32 length           = udp_hdr_size + data_size;
	uint32 checksum         = 0; // disable checksum

	// put all ip settings on the correct place
	iphdr[0] = ((version & 0xF) << 28)
			 + ((ihl & 0xF) << 24)
			 + ((tos & 0xFF) << 16)
			 + (total_length & 0xFFFF);
	iphdr[1] = ((identification & 0xFFFF) << 16)
			 + (flags_offset & 0xFFFF);
	iphdr[2] = ((ttl & 0xFF) << 24)
			 + ((protocol & 0xFF) << 16)
			 + (header_checksum & 0xFFFF);
	iphdr[3] = src_ip_address;
	iphdr[4] = dst_ip_address;

	// compute header checksum
	header_checksum = compute_ip_checksum(&iphdr, ip_hdr_size);
	iphdr[2] += header_checksum; // add checksum
	LOG_DEBUG_STR(formatString("Checksum = 0x%04X", header_checksum));

	// put all udp settings on the correct place
	udphdr[0] = ((src_udp_port & 0xFFFF) << 16)
			  + (dst_udp_port & 0XFFFF);
	udphdr[1] = ((length & 0xFFFF) << 16)
			  + (checksum & 0xFFFF);

	memcpy(ip_hdr, iphdr, ip_hdr_size);
	memcpy(udp_hdr, udphdr, udp_hdr_size);

	/*
	for (int i = 0; i < 5; i++) {
		ip_hdr[i] = iphdr[i];
	}
	for (int i = 0; i < 2; i++) {
		udp_hdr[i] = udphdr[i];
	}
	*/

	for ( int i = 0; i < 5; i++) {
		LOG_DEBUG_STR(formatString("IP[%d]= 0x%08X", i, ip_hdr[i]));
	}
	for ( int i = 0; i < 2; i++) {
		LOG_DEBUG_STR(formatString("UDP[%d]= 0x%08X", i, udp_hdr[i]));
	}
}

	} // end TBB namespace
} // end LOFAR namespace
