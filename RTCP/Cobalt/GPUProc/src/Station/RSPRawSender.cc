//# RSPRawSender.cc: Sender for RSP raw output
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

#include <lofar_config.h>

#include "RSPRawSender.h"

#include <cstring>
#include <fcntl.h>
#include <sys/socket.h>
#include <utility> // std::swap()
#include <Common/LofarLogger.h>
#include <Common/SystemCallException.h>
#include <Stream/StreamFactory.h>

using namespace std;

namespace LOFAR {
  namespace Cobalt {

    RSPRawSender::RSPRawSender() :
      itsStream(NULL),
      itsSentMsgSizes(0),
      itsMaxNrBeamletsToSend(0),
      itsNrDroppedPackets(0)
    {
    }

    RSPRawSender::RSPRawSender(unsigned maxNrPacketsPerTrySend, unsigned maxNrBeamletsToSend,
                               const string& streamDesc, time_t deadline) :
      itsStream(createStream(streamDesc, false, deadline)),
      itsSentMsgSizes(maxNrPacketsPerTrySend), // trySend() in hot code: pre-allocate is easy and acceptable
      itsMaxNrBeamletsToSend(maxNrBeamletsToSend),
      itsNrDroppedPackets(0)
    {
      ASSERTSTR(maxNrPacketsPerTrySend > 0, "maxNrPacketsPerTrySend must be > 0");

      // In RT mode InputProc threads may not block. Prefer not sent (i.e. dropped) packets.
      if (deadline != 0) {
        FileDescriptorBasedStream *fdStream = dynamic_cast<FileDescriptorBasedStream *>(itsStream.get());
        if (fdStream != NULL) {
          fdStream->fcntl(F_SETFL, fdStream->fcntl(F_GETFL) | O_NONBLOCK);
        }
      }
    }

    RSPRawSender::~RSPRawSender()
    {
      try {
        trySendPending(); // try, but it may be way too late
      } catch (SystemCallException& ) {
        itsNrDroppedPackets += 1; // count partially sent as dropped now
      }

      if (itsNrDroppedPackets > 0) {
        SocketStream *sockStream = dynamic_cast<SocketStream *>(itsStream.get());
        if (sockStream == NULL) {
          LOG_WARN_STR("RSPRawSender: number of RSP packets not sent: " << itsNrDroppedPackets);
        } else {
          LOG_WARN_STR("RSPRawSender " << sockStream->getHostname() << ':' << sockStream->getPort() <<
                       " number of RSP packets not sent: " << itsNrDroppedPackets);
        }
      }
    }

    bool RSPRawSender::initialized() const
    {
      return itsStream != NULL;
    }

    void RSPRawSender::swap(RSPRawSender& other) /*noexcept*/
    {
      std::swap(itsStream, other.itsStream);
      std::swap(itsSentMsgSizes, other.itsSentMsgSizes);
      std::swap(itsMaxNrBeamletsToSend, other.itsMaxNrBeamletsToSend);
      std::swap(itsNrDroppedPackets, other.itsNrDroppedPackets);
    }

    unsigned RSPRawSender::getNrDroppedPackets() const
    {
      return itsNrDroppedPackets;
    }

    void RSPRawSender::trySend(struct RSP *packets, unsigned nrPackets)
    {
      ASSERTSTR(nrPackets <= itsSentMsgSizes.size(), "nrPackets > max indicated when sender was constructed");

      /*
       * Patch packet headers if we need to send only the 1st N beamlets.
       * Note: we assume all packets (per RSP board) have the same nrBeamlets and size.
       * If not in nrBeamlets, we may incorrectly restore some of the packet headers below...
       * If not in size, we may append bogus (or uninit data), but struct RSP is large enough.
       */
      const uint8 packetNrBeamlets = packets[0].header.nrBeamlets; // save to restore
      if (itsMaxNrBeamletsToSend < packetNrBeamlets) {
        for (unsigned i = 0; i < nrPackets; i++) {
          packets[i].header.nrBeamlets = itsMaxNrBeamletsToSend;
        }
      }

      unsigned packetSize = packets[0].packetSize();
      SocketStream *sockStream = dynamic_cast<SocketStream *>(itsStream.get());
      try {
        if (sockStream != NULL && sockStream->protocol == SocketStream::UDP) {
          trySendUdp(sockStream, packets, packetSize, nrPackets);
        } else { // no SocketStream or SocketStream::TCP
          trySendByteStream(packets, packetSize, nrPackets);
        }
      } catch (SystemCallException& exc) {
        itsNrDroppedPackets += nrPackets;
        if (exc.error == EAGAIN || exc.error == EWOULDBLOCK) {
          LOG_WARN("RSPRawSender: sent fewer packets than requested to avoid blocking");
        } else {
          static bool errorSeen; // C++11: wrap into std::atomic, use mem order relaxed
          if (!errorSeen) {
            errorSeen = true;
            SocketStream *sockStream = dynamic_cast<SocketStream *>(itsStream.get());
            if (sockStream == NULL) {
              LOG_ERROR_STR("RSPRawSender: " << exc.what()); // backtrace not useful here
            } else {
              LOG_ERROR_STR("RSPRawSender: stream: " << sockStream->getHostname() <<
                            ':' << sockStream->getPort() << ' ' << exc.what()); // idem
            }
          }
        }
      }

      if (itsMaxNrBeamletsToSend < packetNrBeamlets) {
        for (unsigned i = 0; i < nrPackets; i++) {
          packets[i].header.nrBeamlets = packetNrBeamlets; // restore
        }
      }
    }

    void RSPRawSender::trySendUdp(SocketStream *sockStream, struct RSP *packets,
                                  unsigned packetSize, unsigned nrPackets)
    {
      /*
       * MSG_CONFIRM: Inform link-layer to just send the data without periodic ARP probing.
       * We haven't seen any replies (network peer doesn't send any in this case, with its downsides),
       * but we cannot afford stalls.
       */
      unsigned nrSent = sockStream->sendmmsg(packets, packetSize, sizeof(struct RSP), itsSentMsgSizes, MSG_CONFIRM);
      if (nrSent < nrPackets) { // don't check itsSentMsgSizes: resending remainders won't help with UDP (message oriented)
        itsNrDroppedPackets += nrPackets - nrSent;
        LOG_WARN("RSPRawSender::trySendUdp(): fewer sent to avoid blocking"); // not retried, not even in non-RT...
      }
    }

    void RSPRawSender::trySendByteStream(struct RSP *packets, unsigned packetSize, unsigned nrPackets)
    {
      // With TCP we must avoid partial RSP frame transfer. Try sending any remaining data of 1 RSP packet first.
      trySendPending(); // may throw

      // Prepare writev(2)
      // TODO: sendmmsg() has this too. Extract it, unify, and init iov in constructor. Bring recvmmsg() + users in line too.
      vector<struct iovec> iov(nrPackets);
      for (unsigned i = 0; i < nrPackets; i++) {
        iov[i].iov_base = (char *)packets + i * sizeof(struct RSP);
        iov[i].iov_len = packetSize;
      }

      size_t bytesSent = itsStream->tryWritev(&iov[0], nrPackets); // may throw
      if (bytesSent < nrPackets * packetSize) {
        // Drop, except for unsent data of partially sent packet (if so). Stash that to retry later.
        unsigned nrSent = bytesSent / packetSize;
        unsigned partialPacketSent = bytesSent % packetSize;
        if (partialPacketSent != 0) {
          LOG_WARN("RSPRawSender::trySendByteStream(): partial packet sent: will retry remainder later");
          const char *data = (char *)iov[nrSent].iov_base + partialPacketSent;
          size_t size = packetSize - partialPacketSent;
          itsPendingData.resize(size);
          std::memcpy(&itsPendingData[0], data, size);
          nrSent += 1; // partially sent and stashed
        }

        itsNrDroppedPackets += nrPackets - nrSent;
        LOG_WARN("RSPRawSender::trySendByteStream(): fewer sent to avoid blocking"); // not retried, not even in non-RT...
      }
    }

    void RSPRawSender::trySendPending()
    {
      if (!itsPendingData.empty()) {
        size_t bytesSent = itsStream->tryWrite(&itsPendingData[0], itsPendingData.size()); // may throw
        size_t newSize = itsPendingData.size() - bytesSent;
        std::memmove(&itsPendingData[0], &itsPendingData[bytesSent], newSize); // at most 8k
        itsPendingData.resize(newSize);
      }
    }

  } // namespace Cobalt
} // namespace LOFAR

