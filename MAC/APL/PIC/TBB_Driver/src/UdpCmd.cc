// UdpCmd.cc: implementation of the UdpCmd class
//
// Copyright (C) 2018
// ASTRON (Netherlands Foundation for Research in Astronomy)
// P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// $Id$
#include <lofar_config.h>
#include <iostream>
#include <fstream>
#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <netinet/in.h>
#include <net/ethernet.h>

#include "UdpCmd.h"
#include "UdpIpTools.h"

using namespace LOFAR;
using namespace GCF::TM;
using namespace TBB_Protocol;
using namespace TP_Protocol;
using namespace TBB;

//--Constructors for a UdpCmd object.----------------------------------------
UdpCmd::UdpCmd()
{
    TS = TbbSettings::instance();
    setWaitAck(true);
}

//--Destructor for UdpCmd.---------------------------------------------------
UdpCmd::~UdpCmd()
{
}

// ----------------------------------------------------------------------------
bool UdpCmd::isValid(GCFEvent& event)
{
    if((event.signal == TBB_UDP) || (event.signal == TP_UDP_ACK))
    {
        return (true);
    }

    return (false);
}

// ----------------------------------------------------------------------------
void UdpCmd::saveTbbEvent(GCFEvent& event)
{
    LOFAR::TBB_Protocol::TBBUdpEvent tbb_event(event);
    setBoards(tbb_event.boardmask);
    nextBoardNr();
}

// ----------------------------------------------------------------------------
void UdpCmd::sendTpEvent()
{
    TPUdpEvent tp_event;
    tp_event.opcode = oc_UDP;
    tp_event.status = 0;
    uint32 itsMode(TS->getChOperatingMode(
        getBoardNr() * TS->nrChannelsOnBoard()));
    if(itsMode == 0)
    {
        itsMode = TBB_MODE_TRANSIENT;
    }

    // fill in destination mac address
    string2mac(TS->getSrcMacCep(getBoardNr()).c_str(), tp_event.srcmac);
    string2mac(TS->getDstMacCep(getBoardNr()).c_str(), tp_event.dstmac);
    // fill in udp-ip header
    setup_udpip_header(getBoardNr(), itsMode,
        TS->getSrcIpCep(getBoardNr()).c_str(),
        TS->getDstIpCep(getBoardNr()).c_str(), tp_event.ip, tp_event.udp);

    TS->boardPort(getBoardNr()).send(tp_event);
    TS->boardPort(getBoardNr()).setTimer(TS->timeout());
}

// ----------------------------------------------------------------------------
void UdpCmd::saveTpAckEvent(GCFEvent& event)
{
    // in case of a time-out, set error mask
    if(event.signal == F_TIMER)
    {
        setStatus(getBoardNr(), TBB_TIME_OUT);
    }
    else
    {
        TPUdpAckEvent tp_ack(event);

        if(tp_ack.status != 0)
        {
            setStatus(getBoardNr(), (tp_ack.status << 24));
        }

        LOG_DEBUG_STR(
            formatString("Received UdpAck from boardnr[%d]", getBoardNr()));
    }

    nextBoardNr();
}

// ----------------------------------------------------------------------------
void UdpCmd::sendTbbAckEvent(GCFPortInterface* clientport)
{
    TBBUdpAckEvent tbb_ack;
    for(std::size_t boardnr(0U); boardnr < MAX_N_TBBOARDS; ++boardnr)
    {
        tbb_ack.status_mask[boardnr]  = getStatus(boardnr);
    }

    if(clientport->isConnected())
    {
        clientport->send(tbb_ack);
    }
}
