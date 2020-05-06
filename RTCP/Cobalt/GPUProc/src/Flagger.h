//# CorrelatorStep.h
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

#ifndef LOFAR_GPUPROC_FLAGGER_H
#define LOFAR_GPUPROC_FLAGGER_H

#include <CoInterface/MultiDimArray.h>
#include <CoInterface/SparseSet.h>

namespace LOFAR
{
  namespace Cobalt
  {
    // Collection of functions to tranfer the input flags to the output.
    class Flagger
    {
    public:
      // Convert the flags from one channel to multiple channels, per station.
      // If nrChannels > 1, nrPrefixedSamples are assumed to be already
      // prepended to the input flags as a result of the FIR-filter history.
      static void convertFlagsToChannelFlags(
        MultiDimArray<SparseSet<unsigned>, 1>const &inputFlags,
        MultiDimArray<SparseSet<unsigned>, 1>& flagsPerChannel,
        const unsigned nrSamplesPerChannel,
        const unsigned nrChannels,
        const ssize_t nrPrefixedSamples);
    };
  }
}

#endif
