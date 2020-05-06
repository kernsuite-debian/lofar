// ReadBandCmd.cc: implementation of the ReadBandCmd class
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

#include <cstring>
#include <lofar_config.h>
#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <APL/PIC/TBB_Driver/TP_Protocol.ph>
#include <APL/TBB_Protocol/TBB_Protocol.ph>
#include <GCF/TM/GCF_Protocols.h>
#include "DriverSettings.h"

#include "ReadBandCmd.h"


/**
 * The following two using statements are necessary for the macros that are
 * defined in the two auto-generated *_Protocol.ph files.
 */
using namespace LOFAR::TP_Protocol;
using namespace LOFAR::GCF::TM;


// Ctor for ReadBandCmd
LOFAR::TBB::ReadBandCmd::ReadBandCmd():
    TS(LOFAR::TBB::TbbSettings::instance()),
    channel(0U),
    subband(0U),
    time(0U),
    slicenr(0U),
    period(0U)
{
    std::memset(readstatus, 0U, sizeof(readstatus));
    std::memset(total_nof_samples, 0U, sizeof(total_nof_samples));
    std::memset(nof_samples_next_frame, 0U, sizeof(nof_samples_next_frame));
    std::memset(mp_index, 0U, sizeof(mp_index));
    std::memset(interval_start_address, 0U, sizeof(interval_start_address));
    std::memset(buffer_stop_seconds, 0U, sizeof(buffer_stop_seconds));
    std::memset(buffer_stop_slices, 0U, sizeof(buffer_stop_slices));
    std::memset(not_used, 0U, sizeof(not_used));
    std::memset(writer_status, 0U, sizeof(writer_status));
    setWaitAck(true);
}

// Dtor for ReadBandCmd
LOFAR::TBB::ReadBandCmd::~ReadBandCmd()
{
}

bool LOFAR::TBB::ReadBandCmd::isValid(LOFAR::MACIO::GCFEvent& event)
{
    if((event.signal == TBB_READBAND)
    || (event.signal == TP_READBAND_ACK))
    {
        return(true);
    }
    return(false);
}

void LOFAR::TBB::ReadBandCmd::saveTbbEvent(LOFAR::MACIO::GCFEvent& event)
{
    LOFAR::TBB_Protocol::TBBReadbandEvent tbb_event(event);
    setBoards(tbb_event.boardmask);
    channel = tbb_event.channel;
    subband = tbb_event.subband;
    time = tbb_event.time;
    slicenr = tbb_event.slicenr;
    period = tbb_event.period;

    nextBoardNr();
}

void LOFAR::TBB::ReadBandCmd::sendTpEvent()
{
    LOFAR::TP_Protocol::TPReadbandEvent tp_event;
    tp_event.opcode = LOFAR::TP_Protocol::oc_READBAND;
    tp_event.status = 0;
    tp_event.channel = channel;
    tp_event.subband = subband;
    tp_event.time = time;
    tp_event.slicenr = slicenr;
    tp_event.period = period;

    const std::size_t boardNr(getBoardNr());
    TS->boardPort(boardNr).send(tp_event);
    TS->boardPort(boardNr).setTimer(TS->timeout());
}

void LOFAR::TBB::ReadBandCmd::saveTpAckEvent(GCFEvent& event)
{
    const size_t boardNr(getBoardNr());

    // No time out, normal processing.
    if(event.signal != F_TIMER)
    {
        LOFAR::TP_Protocol::TPReadbandAckEvent tp_ack(event);
        LOG_DEBUG_STR(formatString("Received ReadBandAck from "
            "boardnr[%d]", getBoardNr()));

        // Status is OK, normal processing.
        if(tp_ack.status == 0)
        {
            readstatus[boardNr] = tp_ack.readstatus;
            total_nof_samples[boardNr] = tp_ack.total_nof_samples;
            nof_samples_next_frame[boardNr] = tp_ack.nof_samples_next_frame;
            mp_index[boardNr] = tp_ack.mp_index;
            interval_start_address[boardNr] = tp_ack.interval_start_address;
            buffer_stop_seconds[boardNr] = tp_ack.buffer_stop_seconds;
            buffer_stop_slices[boardNr] = tp_ack.buffer_stop_slices;
            not_used[boardNr] = tp_ack.not_used;
            writer_status[boardNr] = tp_ack.writer_status;
        }
        else
        {
            setStatus(boardNr, (tp_ack.status << 24));
        }
    }
    else
    // in case of a time-out, set error mask
    {
        setStatus(getBoardNr(), LOFAR::TBB_Protocol::TBB_TIME_OUT);
    }

    setDone(true);
}

void LOFAR::TBB::ReadBandCmd::sendTbbAckEvent(
    GCFPortInterface* clientport)
{
    if(clientport->isConnected())
    {
        LOFAR::TBB_Protocol::TBBReadbandAckEvent tbb_ack;

        for (std::size_t boardnr(0U); boardnr < MAX_N_TBBOARDS; ++boardnr)
        {
            tbb_ack.readstatus[boardnr] = readstatus[boardnr];
            tbb_ack.status_mask[boardnr] = getStatus(boardnr);
        }

        clientport->send(tbb_ack);
    }
}
