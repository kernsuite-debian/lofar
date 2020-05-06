//# Zeroing.cu: zero ranges of samples
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

#include "gpu_math.cuh"
#include <stdio.h>

typedef float2 FilteredDataType[NR_STABS][NR_POLARIZATIONS][NR_SAMPLES_PER_CHANNEL][NR_CHANNELS];

typedef char MaskType[NR_STABS][NR_SAMPLES_PER_CHANNEL];

/**
 * Zero samples that have been flagged. Clears samples for all channels for
 * ranged specified per station.
 *
 * @param[data] a multi-dimensional array with time samples of type complex
 * float in the last dimension.
 * @param[mask] an 2D array of bytes, each representing a sample of a station.
 * A value of 0 means ignore this sample, a value of 1 means zero this sample.
 */

extern "C"
{
  __global__ void Zeroing(FilteredDataType data,
                           MaskType mask)
  {
    int sample  = blockIdx.x * blockDim.x + threadIdx.x;
    int channel = (blockIdx.y * blockDim.y + threadIdx.y);
    int station = (blockIdx.z * blockDim.z + threadIdx.z) / 2;
    int pol     = (blockIdx.z * blockDim.z + threadIdx.z) % 2;

    if (mask[station][sample]) {
      // Clear our sample
      data[station][pol][sample][channel] = make_float2(0.0f, 0.0f);
    }
  }
}
