//# RSP.h: RSP data format
//# Copyright (C) 2012-2013, 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
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

#ifndef LOFAR_INTERFACE_RSP_H
#define LOFAR_INTERFACE_RSP_H

#include <cstddef>
#include <complex>

#include "RSPTimeStamp.h"
#include <Common/LofarTypes.h>

namespace LOFAR
{
  namespace Cobalt
  {

    // WARNING: All data is in Little Endian format!
    //
    // Note that C++ bit fields are implementation dependent,
    // so we cannot use them.

    /* A structure fit for the maximum payload size. When reading UDP,
     * just read them straight into this struct, and ::read() will return
     * the size of the packet.
     *
     * When reading packets from file, make sure you read the right number
     * of bytes (see packetSize()).
     */

    struct RSP {
      // ----------------------------------------------------------------------
      // Header and payload, in little endian!
      // ----------------------------------------------------------------------

      struct Header {
        // 2: Beamlet Data CoInterface 5.0: no longer supported
        // 3: Beamlet Data CoInterface 6.0 (add 8- and 4-bit mode support apart from 16-bit mode)
        uint8 version;

        // bit (0=LSB)
        //
        // 4:0    RSP board number
        // 5      (reserved, set to 0)
        // 6      0: payload ok, 1: payload has data errors
        // 7      0: 160 MHz     1: 200 MHz
        uint8 sourceInfo1;

        // bit (0=LSB)
        //
        // 1:0    0: 16-bit      1: 8-bit       2: 4-bit
        // 7:2    (reserved, set to 0)
        uint8 sourceInfo2;

        // identifiers
        uint8 configuration;
        uint16 station;

        // number of beamlets, typically at maximum:
        //   16-bit: 61
        //    8-bit: 122
        //    4-bit: 244
        uint8 nrBeamlets;

        // number of Xr+Xi+Yr+Yi samples per beamlet, typically 16
        uint8 nrBlocks;

        // UNIX timestamp in UTC (= # seconds since 1970-01-01 00:00:00)
        // 0xFFFFFFFF = clock not initialised
        uint32 timestamp;

        // Sample offset within the timestamp.
        //
        // 160 MHz: 160M/1024 = 156250 samples/second.
        //
        // 200 MHz: 200M/1024 = 195212.5 samples/second.
        //                      Even seconds have 195213 samples,
        //                      odd seconds have 195212 samples.
        uint32 blockSequenceNumber;
      } header;

      // Payload, allocated for maximum size.
      // Actual size depends on the header (nrBeamlets, nrBlocks). It changed in the past (61 vs 60) and
      // may be less for tests, old pre-recorded data, in 4 bit mode for 1 of the boards, and
      // RSP raw output for offline reprocessing or piggy-backing (selectable beamlet subset).
      union Payload {
        char data[8130];

        // samples are structured as samples[nrBeamlets][nrBlocks],
        // so first all blocks of the first beamlet, then all blocks of the second
        // beamlet, etc.
        //
        // for 4-bit mode:
        //  low octet: real      (2's complement)
        // high octet: imaginary (2's complement)

        struct samples16bit_t { int16 Xr, Xi, Yr, Yi;
        } samples16bit[61 * 16];
        struct samples8bit_t { int8 Xr, Xi, Yr, Yi;
        } samples8bit[122 * 16];
        struct samples4bit_t { int8 X, Y;
        } samples4bit[244 * 16];
      } payload;


      // ----------------------------------------------------------------------
      // Helper functions
      // ----------------------------------------------------------------------

      unsigned rspBoard() const
      {
        return header.sourceInfo1 & 0x1F;
      }

      void rspBoard(unsigned nr)
      {
        header.sourceInfo1 &= ~0x1F;
        header.sourceInfo1 |= (nr & 0x1F);
      }

      bool payloadError() const
      {
        return header.sourceInfo1 & 0x40;
      }

      void payloadError(bool error)
      {
        if (error)
          header.sourceInfo1 |= 0x40;
        else 
          header.sourceInfo1 &= ~0x40;
      }

      unsigned clockMHz() const
      {
        return header.sourceInfo1 & 0x80 ? 200 : 160;
      }

      void clockMHz(unsigned freq)
      {
        switch (freq) {
        default:
        case 200:
          header.sourceInfo1 |= 0x80; 
          break;
        case 160:
          header.sourceInfo1 &= ~0x80;
          break;
        }
      }

      unsigned bitMode() const
      {
        //if (header.version < 3)  // disabled: Beamlet Data CoInterface 5.0 is too old to care and in a hot path
        //  return 16;
        return 16 >> header.sourceInfo2; // 0x0: 16, 0x1: 8, 0x2: 4
      }

      void bitMode(unsigned mode)
      {
        header.sourceInfo2 &= ~0x3;
        switch (mode) {
        default:
        case 16:
          header.sourceInfo2 |= 0x0;
          break;
        case 8 :
          header.sourceInfo2 |= 0x1;
          break;
        case 4 :
          header.sourceInfo2 |= 0x2;
          break;
        }
      }

      TimeStamp timeStamp() const
      {
        return TimeStamp(header.timestamp, header.blockSequenceNumber, clockMHz() * 1000000);
      }

      void timeStamp(const TimeStamp& ts)
      {
        header.timestamp = ts.getSeqId();
        header.blockSequenceNumber = ts.getBlockId();
      }

      void timeStampError()
      {
        header.timestamp = 0xFFFFFFFF; // clock not initialised
      }

      size_t packetSize() const
      {
        return sizeof(RSP::Header) + header.nrBlocks * header.nrBeamlets * 2 * 2 * bitMode() / 8;
      }


      // ----------------------------------------------------------------------
      // Payload decoding (for debug purposes, assumes data is converted to native
      // endianness)
      // ----------------------------------------------------------------------
      std::complex<int> sample( unsigned beamlet, unsigned block, char polarisation /* 'X' or 'Y' */) const
      {
        const unsigned offset = beamlet * header.nrBlocks + block;

        switch( bitMode() ) {
        default:
        case 16:
          return polarisation == 'X' ? std::complex<int>(payload.samples16bit[offset].Xr,
                                                         payload.samples16bit[offset].Xi)
                 : std::complex<int>(payload.samples16bit[offset].Yr,
                                     payload.samples16bit[offset].Yi);

        case 8:
          return polarisation == 'X' ? std::complex<int>(payload.samples8bit[offset].Xr,
                                                         payload.samples8bit[offset].Xi)
                 : std::complex<int>(payload.samples8bit[offset].Yr,
                                     payload.samples8bit[offset].Yi);

        case 4:
          return polarisation == 'X' ? decode4bit(payload.samples4bit[offset].X)
                 : decode4bit(payload.samples4bit[offset].Y);
        }
      }

    private:

      // decode the 4-bit complex type.
      static std::complex<int> decode4bit( int8 sample )
      {
        // intermediate after << will be int, not int8,
        // so cast to get a signed int8 value.
        int8 re = (int8)(sample << 4) >> 4; // preserve sign
        int8 im =       (sample     ) >> 4; // preserve sign

        // balance range to [-7..7], subject to change!
        if (re == -8) re = -7;
        if (im == -8) im = -7;

        return std::complex<int>(re, im);
      }
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

