//# Flagger.cc
//# Copyright (C) 2012-2013  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <GPUProc/Flagger.h>
#include <Common/LofarLogger.h>

namespace LOFAR
{
  namespace Cobalt
  {
    void Flagger::convertFlagsToChannelFlags(
      MultiDimArray<LOFAR::SparseSet<unsigned>, 1>const &inputFlags,
      MultiDimArray<SparseSet<unsigned>, 1>& flagsPerChannel,
      const unsigned nrSamples,
      const unsigned nrChannels,
      const ssize_t nrPrefixedSamples)
    {
      ASSERT(inputFlags.num_elements() == flagsPerChannel.num_elements());

      // If nrChannels == 1, we do not expect nrPrefixedSamples
      ASSERT(nrChannels > 1 || nrPrefixedSamples == 0);

      unsigned nrSamplesPerChannel = nrSamples / nrChannels;
      unsigned log2NrChannels = log2(nrChannels);

      // Convert the flags per sample to flags per channel
      for (unsigned station = 0; station < inputFlags.num_elements(); station ++) 
      {
        // reset the channel flags for this station
        flagsPerChannel[station].reset();

        // get the flag ranges
        const SparseSet<unsigned>::Ranges &ranges = inputFlags[station].getRanges();
        for (SparseSet<unsigned>::const_iterator it = ranges.begin();
          it != ranges.end(); it ++) 
        {
          unsigned begin_idx;
          unsigned end_idx;
          if (nrChannels == 1)
          {
            // do nothing, just take the ranges as supplied
            begin_idx = it->begin; 
            end_idx = std::min(nrSamplesPerChannel, it->end);
          }
          else
          {
            // Never flag before the start of the time range               
            // use bitshift to divide to the number of channels. 
            //
            // In case of nrPrefixedSamples, there are FIR Filter
            // samples in front of those who we split the flags for.
            // In that case, nrPrefixedSamples == NR_TAPS - 1.
            //
            // NR_TAPS is the width of the filter: they are
            // absorbed by the FIR and thus should be excluded
            // from the original flag set.
            //
            // The original flag set can span up to
            //    [0, nrSamplesPerBlock + nrChannels * (NR_TAPS - 1))
            // of which the FIRST (NR_TAPS - 1) samples belong to
            // the previous block, and are used to initialise the
            // FIR filter. Every sample i of the current block is thus
            // actually at index (i + nrChannels * (NR_TAPS - 1)),
            // or, after converting to channels, at index (i' + NR_TAPS - 1).
            //
            // At the same time, every sample is affected by
            // the NR_TAPS-1 samples before it. So, any flagged
            // sample in the input flags NR_TAPS samples in
            // the channel.
            begin_idx = std::max(0L, 
              (signed) (it->begin >> log2NrChannels) - nrPrefixedSamples);

            // The min is needed, because flagging the last input
            // samples would cause NR_TAPS subsequent samples to
            // be flagged, which aren't necessarily part of this block.
            end_idx = std::min(nrSamplesPerChannel, 
              ((it->end - 1) >> log2NrChannels) + 1);
          }

          // Now copy the transformed ranges to the channelflags
          flagsPerChannel[station].include(begin_idx, end_idx);
        }
      }
    }
  }
}
