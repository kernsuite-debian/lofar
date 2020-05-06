//# IntToFloat.cu: Convert integer input to float; transpose time and pol dims
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

#include "IntToFloat.cuh"

// SampleType is a COMPLEX sample
#if NR_BITS_PER_SAMPLE ==  4
typedef signed char SampleType;
#elif NR_BITS_PER_SAMPLE ==  8
typedef char2  SampleType;
#elif NR_BITS_PER_SAMPLE == 16
typedef short2 SampleType;
#else
#error unsupported NR_BITS_PER_SAMPLE: must be 4, 8, or 16
#endif

#if NR_BITS_PER_SAMPLE ==  4
#define REAL(sample) extractRI(sample, false)
#define IMAG(sample) extractRI(sample, true)
#else
#define REAL(sample) sample.x
#define IMAG(sample) sample.y
#endif

typedef SampleType (*SampledDataType)  [NR_INPUT_STATIONS][NR_SAMPLES_PER_SUBBAND][NR_POLARIZATIONS];
typedef float2     (*ConvertedDataType)[NR_OUTPUT_STATIONS][NR_POLARIZATIONS][NR_SAMPLES_PER_SUBBAND];

/**
 * This kernel performs a conversion of the integer valued input to floats and
 * transposes the data to get per station: first all samples with polX, then polY.
 * - It supports 8 and 16 bit (char and short) input, which is selectable using
 *   the define NR_BITS_PER_SAMPLE
 * - In 8 bit mode the converted samples with value -128 are clamped to -127.0f
 *
 * @param[out] convertedDataPtr    pointer to output data of ConvertedDataType,
 *                                 a 4D array [station_out][polarizations][n_samples_subband][complex]
 *                                 of floats (2 complex polarizations).
 * @param[in]  sampledDataPtr      pointer to input data; this can either be a
 *                                 4D array [station_in][n_samples_subband][polarizations][complex]
 *                                 of shorts or chars, depending on NR_BITS_PER_SAMPLE.
 * @param[in]  stationIndices      list of input stations to use for each output station
 *                                 1D array [station_out]
 *                                 of unsigned
 *
 * Required preprocessor symbols:
 * - NR_SAMPLES_PER_CHANNEL: > 0
 * - NR_BITS_PER_SAMPLE: 8 or 16
 * - NR_INPUT_STATIONS
 * - NR_OUTPUT_STATIONS
 *
 * Optional preprocessor symbols:
 * - DO_FFTSHIFT, if an fft-shift is to be performed as well
 * - DO_STATIONSUBSET, if the stationIndices input array is to be used to select a subset
 *                     of stations.
 *
 * Execution configuration:
 * - Use a 1D thread block. No restrictions.
 * - Use a 2D grid dim, where the x dim has 1 block and the y dim represents the
 *   number of output stations (i.e. antenna fields).
 */

extern "C" {
__global__ void intToFloat(void *convertedDataPtr,
                           const void *sampledDataPtr,
                           const unsigned *stationIndices)
{
  ConvertedDataType convertedData = (ConvertedDataType)convertedDataPtr;
  SampledDataType   sampledData   = (SampledDataType)  sampledDataPtr;

#ifdef DO_STATIONSUBSET
  uint station_in  = stationIndices[blockIdx.y];
  uint station_out = blockIdx.y;
#else
  uint station_in  = blockIdx.y;
  uint station_out = blockIdx.y;
#endif

#ifdef DO_FFTSHIFT
  // Multiplication factor: 1 for even samples, -1 for odd samples
  //const float factor = 1 - 2 * (threadIdx.x % 2); 
  const float factor = threadIdx.x % 2 ? -1.0f : +1.0f;
#else
  const float factor = 1.0f;
#endif

  // For even increases, we always process either even or odd samples
  for (int time = threadIdx.x; time < NR_SAMPLES_PER_SUBBAND; time += blockDim.x)
  {
    float4 sample;

    sample = make_float4(convertIntToFloat(REAL((*sampledData)[station_in][time][0])) * factor,
                         convertIntToFloat(IMAG((*sampledData)[station_in][time][0])) * factor,
                         convertIntToFloat(REAL((*sampledData)[station_in][time][1])) * factor,
                         convertIntToFloat(IMAG((*sampledData)[station_in][time][1])) * factor);

    float2 sampleX = make_float2(sample.x, sample.y);
    (*convertedData)[station_out][0][time] = sampleX;
    float2 sampleY = make_float2(sample.z, sample.w);
    (*convertedData)[station_out][1][time] = sampleY;
  }

}

}

