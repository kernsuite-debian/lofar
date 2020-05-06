// StopTimedCmd.cc: implementation of the StopTimedCmd class
//
// Copyright (C) 2017
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
#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <APL/PIC/TBB_Driver/TP_Protocol.ph>
#include <APL/TBB_Protocol/TBB_Protocol.ph>
#include <GCF/TM/GCF_Protocols.h>
#include "DriverSettings.h"

#include "StopTimedCmd.h"


/**
 * The following two using statements are necessary for the macros that are
 * defined in the two auto-generated *_Protocol.ph files.
 */
using namespace LOFAR::TP_Protocol;
using namespace LOFAR::GCF::TM;


// Ctor for StopTimedCmd
LOFAR::TBB::StopTimedCmd::StopTimedCmd():
    TS(LOFAR::TBB::TbbSettings::instance()),
    time(0U),
    slicenr(0U)
{
    setWaitAck(true);
}

// Dtor for StopTimedCmd
LOFAR::TBB::StopTimedCmd::~StopTimedCmd()
{
}

bool LOFAR::TBB::StopTimedCmd::isValid(LOFAR::MACIO::GCFEvent& event)
{
    if((event.signal == TBB_STOPTIMED)
    || (event.signal == TP_STOPTIMED_ACK))
    {
        return(true);
    }
    return(false);
}

void LOFAR::TBB::StopTimedCmd::saveTbbEvent(LOFAR::MACIO::GCFEvent& event)
{
    LOFAR::TBB_Protocol::TBBStoptimedEvent tbb_event(event);
    setBoards(tbb_event.boardmask);
    time = tbb_event.time;
    slicenr = tbb_event.slicenr;

    nextBoardNr();
}

void LOFAR::TBB::StopTimedCmd::sendTpEvent()
{
    LOFAR::TP_Protocol::TPStoptimedEvent tp_event;
    tp_event.opcode = LOFAR::TP_Protocol::oc_STOPTIMED;
    tp_event.status = 0;
    tp_event.time = time;
    tp_event.slicenr = slicenr;

    const std::size_t boardNr(getBoardNr());
    TS->boardPort(boardNr).send(tp_event);
    TS->boardPort(boardNr).setTimer(TS->timeout());
}

void LOFAR::TBB::StopTimedCmd::saveTpAckEvent(GCFEvent& event)
{
    const size_t boardNr(getBoardNr());

    // No time out, normal processing.
    if(event.signal != F_TIMER)
    {
        LOFAR::TP_Protocol::TPStoptimedAckEvent tp_ack(event);
        LOG_DEBUG_STR(formatString("Received StopTimedAck from "
            "boardnr[%d]", getBoardNr()));

        // Status is not OK, set error flag.
        if(tp_ack.status != 0)
        {
            setStatus(boardNr, (tp_ack.status << 24));
        }
    }
    else
    // in case of a time-out, set error mask
    {
        setStatus(boardNr, LOFAR::TBB_Protocol::TBB_TIME_OUT);
    }

    nextBoardNr();
}

void LOFAR::TBB::StopTimedCmd::sendTbbAckEvent(
    GCFPortInterface* clientport)
{
    if(clientport->isConnected())
    {
        LOFAR::TBB_Protocol::TBBStoptimedAckEvent tbb_ack;
        for (std::size_t  boardnr(0U); boardnr < MAX_N_TBBOARDS; ++boardnr)
        {
            tbb_ack.status_mask[boardnr] = getStatus(boardnr);
        }

        clientport->send(tbb_ack);
    }
}
