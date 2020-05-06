//# TBB_Frame.cc: TBB packet definitions
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

#include <lofar_config.h>

#include "TBB_Frame.h"
#include <cstdint>
#include <complex>
#include <climits> // CHAR_BIT
#include <strings.h> // ffs()
#include <boost/format.hpp>

#include <Common/LofarLogger.h>

namespace LOFAR
{
  namespace Cobalt
  {

    using namespace std;

    void logErrorRateLimited(time_t *lastErrorTime, const string& msg)
    {
      const int logErrorRateSecs = 1;
      time_t ts = ::time(NULL);
      if (ts > *lastErrorTime + logErrorRateSecs) {
        *lastErrorTime = ts;
        LOG_ERROR(msg);
      }
    }


    const unsigned TBB_Frame::transientFrameSize = sizeof(TBB_Header) +
              DEFAULT_TBB_TRANSIENT_NSAMPLES * sizeof(int16_t) + /*crc32:*/sizeof(uint32_t);
    const unsigned TBB_Frame::spectralFrameSize = sizeof(TBB_Header) +
              MAX_TBB_SPECTRAL_NSAMPLES * sizeof(std::complex< int16_t >) + /*crc32:*/sizeof(uint32_t);

    uint32_t TBB_Header::getFirstBandSelNr() const
    {
      //TODO: implement like https://github.com/liamconnor/tbb-tools/blob/master/read_tbb_data.py#L157
      //for now, just return 0 to test the signal path
      LOG_DEBUG("TBB_Header::getFirstBandSelNr returning band=0 for testing");
      return 0;

      // 64 bit scans would be ~8x faster, but require fixes for band order (and endian)
      for (unsigned i = 0; i < sizeof(bandSel) / sizeof(bandSel[0]); i++) {
        int pos = ::ffs(bandSel[i]); // ffs() returns 1-indexed val, or 0 if not found
        if (pos != 0) {
          return i * CHAR_BIT + pos - 1;
        }
      }
      return RSP_NR_SUBBANDS; // invalid band nr: not found
    }

    // or make operator<<(ostream& out, ...) as we used to have. Missing from to_string(): bandSel bitfield
    string TBB_Header::to_string() const
    {
      return str(boost::format("stationID=%u rspID=%u rcuID=%u sampleFreq=%u seqNr=%u time=%u sampleNr_or_bandSliceNr=%u nOfSamplesPerFrame=%u nOfFreqBands=%u spare=%u crc16=%u") %
                 (unsigned)stationID % (unsigned)rspID % (unsigned)rcuID % (unsigned)sampleFreq % seqNr % time %
                 sampleNrOrBandSliceNr % nOfSamplesPerFrame % nOfFreqBands % spare % crc16);
    }

  } // namespace Cobalt
} // namespace LOFAR

