/* PacketStream.h
 * Copyright (C) 2012-2013  ASTRON (Netherlands Institute for Radio Astronomy)
 * P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
 *
 * This file is part of the LOFAR software suite.
 * The LOFAR software suite is free software: you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * The LOFAR software suite is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
 *
 * $Id$
 */

#ifndef LOFAR_INPUT_PROC_PACKETSTREAM_H
#define LOFAR_INPUT_PROC_PACKETSTREAM_H

#include <Stream/Stream.h>
#include <Common/Thread/Cancellation.h>
#include <CoInterface/RSP.h>
#include <CoInterface/RSPTimeStamp.h>
#include "PacketFactory.h"

namespace LOFAR
{
  namespace Cobalt
  {
    /* Generate a Stream of RSP packets. */

    class PacketStream: public Stream
    {
    public:
      // 'factory' will be copied.
      PacketStream( const PacketFactory &factory, const TimeStamp &from, const TimeStamp &to, size_t boardNr = 0 )
      :
        factory(factory),
        from(from),
        to(to),
        current(from),
        boardNr(boardNr),
        offset(0)
      {
      }

      virtual size_t tryRead(void *ptr, size_t size)
      {
        Cancellation::point();

        if (size == 0) {
          return 0;
        }

        if (current >= to) {
          THROW(EndOfStreamException, "No data beyond " << to);
        }

        if (offset == 0) {
          // generate new packet
          factory.makePacket(packet, current, boardNr);
          current += packet.header.nrBlocks;
        }

        size_t pktSize = packet.packetSize();
        size_t numBytes = std::min(pktSize - offset, size);
        memcpy(ptr, reinterpret_cast<char*>(&packet) + offset, numBytes);

        offset += numBytes;
        if (offset == pktSize) {
          // written full packet, so we'll need a new one on next read
          offset = 0;
        }

        return numBytes;
      }

      virtual size_t tryWrite(const void * /*ptr*/, size_t /*size*/)
      {
        THROW(NotImplemented, "Writing to PacketStream is not supported");
      }

      virtual size_t tryReadv(const struct iovec *iov, int iovcnt)
      {
        Cancellation::point();

        size_t nread = 0;
        for (int i = 0; i < iovcnt; i++) {
          if (iov[i].iov_len == 0) {
            continue;
          }

          if (current >= to) {
            if (nread == 0) {
              THROW(EndOfStreamException, "No data beyond " << to);
            } else {
              break;
            }
          }

          if (offset == 0) {
            // generate new packet
            factory.makePacket(packet, current, boardNr);
            current += packet.header.nrBlocks;
          }

          size_t pktSize = packet.packetSize();
          size_t numBytes = std::min(pktSize - offset, iov[i].iov_len);
          memcpy(iov[i].iov_base, reinterpret_cast<char*>(&packet) + offset, numBytes);

          offset += numBytes;
          if (offset == pktSize) {
            // written full packet, so we'll need a new one on next read
            offset = 0;
          }

          nread += numBytes;

          // Mimic tryRead() impl above: max 1 (partial) packet per buffer.
          // Then we can only use the next iov if we could exactly fill the previous, else our retval is ambiguous.
          if (numBytes < pktSize) {
            break;
          }
        }

        return nread;
      }

      virtual size_t tryWritev(const struct iovec * /*iov*/, int /*iovcnt*/)
      {
        THROW(NotImplemented, "Writing to PacketStream is not supported");
      }

      virtual std::string description() const {
        //TODO: fill in all the packetstream details
        return "PacketStream ";
      }

    private:
      PacketFactory factory;

      const TimeStamp from;
      const TimeStamp to;
      TimeStamp current;
      const size_t boardNr;

      struct RSP packet;

      // Write offset within packet. If 0, a new
      // packet is required.
      size_t offset;
    };
  }
}

#endif

