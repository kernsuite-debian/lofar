//# RSPRawSender.h: Sender for RSP raw output
//# Copyright (C) 2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#ifndef LOFAR_GPUPROC_RSPRAWSENDER_H
#define LOFAR_GPUPROC_RSPRAWSENDER_H

// \file
// Sender for RSP raw output. Corresponding receiver: OutputProc/src/InputThread.h
// Sender can also be used for COBALT RSP data piggy-backing.

#include <ctime> // time_t
#include <string>
#include <Stream/SocketStream.h>
#include <CoInterface/RSP.h>
#include <CoInterface/SmartPtr.h>

namespace LOFAR
{
  namespace Cobalt
  {

class RSPRawSender {
public:
  RSPRawSender();

  // deadline is an absolute timestamp or 0 for no connection timeout (blocking).
  RSPRawSender(unsigned maxNrPacketsPerTrySend, unsigned maxNrBeamletsToSend,
               const std::string& streamDesc, time_t deadline = 0);

  ~RSPRawSender();

  bool initialized() const;

  void swap(RSPRawSender& other) /*noexcept*/;

  // Ensure nrPackets <= maxNrPacketsPerSend (passed upon object construction).
  // If deadline (passed upon object construction) was non-zero, trySend() may drop packets to avoid blocking.
  void trySend(struct RSP *packets, unsigned nrPackets);

  unsigned getNrDroppedPackets() const;

private:
  void trySendUdp(SocketStream *sockStream, struct RSP *packets,
                  unsigned packetSize, unsigned nrPackets);
  void trySendByteStream(struct RSP *packets, unsigned packetSize, unsigned nrPackets);
  void trySendPending();

  SmartPtr<Stream> itsStream;
  std::vector<unsigned> itsSentMsgSizes;
  unsigned itsMaxNrBeamletsToSend;
  unsigned itsNrDroppedPackets;
  std::vector<unsigned char> itsPendingData; // w/ non-UDP to retry sending the remainder of a partially sent RSP packet
};

  } // namespace Cobalt
} // namespace LOFAR

#endif

