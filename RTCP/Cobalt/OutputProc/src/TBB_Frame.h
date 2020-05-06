//# TBB_Frame.h: TBB packet definitions
//# Copyright (C) 2012-2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#ifndef LOFAR_COBALT_OUTPUTPROC_TBBFRAME_H
#define LOFAR_COBALT_OUTPUTPROC_TBBFRAME_H 1

#include <cstdint>
#include <complex>
#include <ctime>
#include <string>
#include <vector>
#include <map>

namespace LOFAR
{
    namespace Cobalt
    {
        /**
         * This reflects the fact that LOFAR's TBB boards can produce spectral
         * time series for a maximum of 487 frequency bands.
         */
        const uint32_t MAX_TBB_SPECTRAL_SUBBANDS{487U};
        /**
         * The bit shift and mask for the uint32_t in the TBB frame header that
         * represent the slice and band numbers.
         */
        const uint32_t TBB_SLICE_NR_SHIFT{10U};
        const uint32_t TBB_BAND_NR_MASK{((1U << TBB_SLICE_NR_SHIFT) - 1U)};

        /**
         * For transient, TBB always sends sends 1024 samples per frame (from the
         * spec and seen in data).
         * For spectral, it depends on the nr of subbands (max is equal to
         * MAX_TBB_SPECTRAL_NSAMPLES).
         */
        // RSP FFT block size in samples (complex 16 bit value)
        const uint32_t SPECTRAL_TRANSFORM_SIZE{1024U};
        // equal to nr bits in TBB_Header::bandSel[]
        const uint32_t RSP_NR_SUBBANDS{(SPECTRAL_TRANSFORM_SIZE / 2U)};
        // for spectral it depends on #subbands
        const uint32_t DEFAULT_TBB_TRANSIENT_NSAMPLES{1024U};

    /*
     * Incoming UDP frame format.
     * From 'TBB Design Description.doc', Doc.id: LOFAR-ASTRON-SDD-047, rev. 2.8 (2009-11-30), by Arie Doorduin, Wietse Poiesz
     * available at: http://www.lofar.org/project/lofardoc/document.php
     *
     * There are two types of data that can be transferred: transient data and spectral (subband) data. Everything is in little-endian byte order.
     */
    struct TBB_Header {
      uint8_t stationID;        // Data source station identifier
      uint8_t rspID;            // Data source RSP board identifier
      uint8_t rcuID;            // Data source RCU board identifier
      uint8_t sampleFreq;       // Sample frequency in MHz of the RCU boards: 160 or 200

      uint32_t seqNr;           // Used internally by TBB. Set to 0 by RSP before computing crc16 (but written again before we receive it)
      uint32_t time;            // Time instance in seconds of the first sample in payload
      // The time field is relative, but if used as UNIX time, uint32_t wraps at 06:28:15 UTC on 07 Feb 2106
      // (int32_t wraps at 03:14:08 UTC on 19 Jan 2038)

      // In transient mode indicates sample number of the first payload sample in current seconds interval.
      // In spectral mode indicates frequency band and slice (transform block of 1024 samples) of first payload sample.
      /**
       * Use a union to make it clear by using an implicit variable name that
       * in raw voltage mode the value is a sample number and in spectral mode
       * a band/slice number.
       */
      union
      {
          uint32_t sampleNrOrBandSliceNr;
          uint32_t sampleNr;
          uint32_t bandSliceNr; // in spectral mode: bandNr[9:0] and sliceNr[31:10]
      };

      uint16_t nOfSamplesPerFrame; // Total number of samples in the frame payload
      uint16_t nOfFreqBands;    // Number of frequency bands for each spectrum in spectral mode. Is set to 0 for transient mode. Descriptive for this packet's payload.

      uint8_t bandSel[64];      // Each bit in the band selector field indicates whether the band with the bit index is present in the spectrum or not.

      uint16_t spare;           // For future use. Set to 0.
      uint16_t crc16;           // CRC16 over frame header, with seqNr set to 0.


      // Returns lowest band nr bit set in bandSel, or RSP_NR_SUBBANDS if not found.
      uint32_t getFirstBandSelNr() const;

      std::string to_string() const;
    };

    /*
     * In transient mode, a sample is a signed 12 bit integer. In spectral mode, it is a complex int16_t.
     * In the TBBs, transient samples are packed (2 samples per 3 bytes) with the checksum all the way at the end. This changes on transfer.
     *
     * TBB stores a frame in 2040 bytes (actually, 2048 with preamble and gaps). It sends a frame at a time, so derive our max from it.
     *
     * In spectral mode the frame size is only 2012 bytes!
     */
    const uint32_t MAX_TBB_DATA_SIZE_SPECTRAL_MODE{(2012 - sizeof(TBB_Header) - sizeof(uint32_t))};
    // 1948: TBB frame size without header and payload crc32.
    const uint32_t MAX_TBB_DATA_SIZE_TRANSIENT_MODE{(2040 - sizeof(TBB_Header) - sizeof(uint32_t))};
    // 1298 (.666: 1 byte padding when indeed 1298 samples would ever be stored in TBB)
    const uint32_t MAX_TBB_TRANSIENT_NSAMPLES{(MAX_TBB_DATA_SIZE_TRANSIENT_MODE / 3 * 2)};
    // Is 480:
    const uint32_t MAX_TBB_SPECTRAL_NSAMPLES{(MAX_TBB_DATA_SIZE_SPECTRAL_MODE / (2 * sizeof(int16_t)))};

    struct TBB_Payload {
      // Unpacked, sign-extended (for transient) samples without padding, i.e. as received.
      // Frames might not be full; the doc says the crc32 is always sent right after (no padding),
      // so we include the crc32 in 'data', but note that the crc32 is a little endian uint32_t, hence ' + 2'.
        union
        {
            int16_t data[MAX_TBB_TRANSIENT_NSAMPLES];
            int16_t spectralData[MAX_TBB_SPECTRAL_NSAMPLES + 2U][2];
        };
    };

    struct TBB_Frame {
      static const unsigned transientFrameSize;
      static const unsigned spectralFrameSize;

      TBB_Header header;
      TBB_Payload payload;
    };


    // Station meta data from other sources than the parset.
    struct StationMetaData {
      // If we receive data from a station not in the obs, we won't have all the meta data.
      bool available;

      // from the antenna field files
      std::vector<double> antPositions;
      std::vector<double> normalVector;     // [3]
      std::vector<double> rotationMatrix;   // [3, 3] row-major order

      // from the station calibration table files
      //...
    };

    typedef std::map<unsigned, StationMetaData> StationMetaDataMap; // stationID -> StationMetaData


    void logErrorRateLimited(time_t *lastErrorTime, const std::string& msg);

  } // namespace Cobalt
} // namespace LOFAR

#endif

