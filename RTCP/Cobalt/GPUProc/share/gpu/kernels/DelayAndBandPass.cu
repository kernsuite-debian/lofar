//# DelayAndBandPass.cu
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

/** @file
* This file contains a CUDA implementation of the GPU kernel for the delay
* and bandpass correction. It can also transpose the data (pol to dim 0).
*
* Usually, this kernel will be run after the polyphase filter kernel FIR.cl. In
* that case, the input data for this kernel is already in floating point format
* (@c NR_CHANNELS > 1). However, if this kernel is the first in row, then the
* input data is still in integer format (@c NR_CHANNELS == 1), and this kernel
* needs to do the integer-to-float conversion. If we do BANDPASS_CORRECTION
* (implies NR_CHANNELS > 1), then we typically also want to transpose the pol
* dim to the stride 1 dim (@c DO_TRANSPOSE).
*
* @attention The following pre-processor variables must be supplied when
* compiling this program. Please take the pre-conditions for these variables
* into account:
* - @c NR_CHANNELS: 1 or a multiple of 16
* - if @c NR_CHANNELS == 1 (input data is in integer format):
*   - @c NR_BITS_PER_SAMPLE: 4, 8 or 16
*   - @c NR_SAMPLES_PER_SUBBAND: a multiple of 16
* - if @c NR_CHANNELS > 1 (input data is in floating point format):
*   - @c NR_SAMPLES_PER_CHANNEL: a multiple of 16
* - @c NR_SAPS: > 0
* - @c NR_POLARIZATIONS: 2
* - @c SUBBAND_BANDWIDTH: a multiple of @c NR_CHANNELS
*
* - @c DELAY_COMPENSATION: defined or not
* - @c BANDPASS_CORRECTION: defined or not
* - @c DO_TRANSPOSE: defined or not
*/

#include "gpu_math.cuh"

#include "IntToFloat.cuh"


#if NR_CHANNELS == 1
//# #chnl==1 && BANDPASS_CORRECTION is rejected on the CPU early, (TODO)
//# but once here, don't do difficult and adjust cleanly here.
#  undef BANDPASS_CORRECTION
#endif

#if defined DO_TRANSPOSE
typedef  fcomplex(*OutputDataType)[NR_STATIONS][NR_CHANNELS][NR_SAMPLES_PER_CHANNEL][NR_POLARIZATIONS];
#else
typedef  fcomplex(*OutputDataType)[NR_STATIONS][NR_POLARIZATIONS][NR_CHANNELS][NR_SAMPLES_PER_CHANNEL];
#endif

typedef  fcomplex(*InputDataType)[NR_STATIONS][NR_POLARIZATIONS][NR_SAMPLES_PER_CHANNEL][NR_CHANNELS];
typedef  const double(*DelaysType)[NR_SAPS][NR_DELAYS][NR_POLARIZATIONS]; // 2 Polarizations; in seconds
typedef  const double2(*Phase0sType)[NR_STATIONS]; // 2 Polarizations; in radians
typedef  const float(*BandPassFactorsType)[NR_CHANNELS];

inline __device__ fcomplex sincos_f2f(float phi)
{
  float2 r;

  sincosf(phi, &r.y, &r.x);
  return r;
}

inline __device__ fcomplex sincos_d2f(double phi)
{
  double s, c;

  sincos(phi, &s, &c);
  return make_float2(c, s);
}

/**
* This kernel performs (up to) three operations on the input data:
* - Apply a fine delay by doing a per channel phase correction.
* - Apply a bandpass correction to compensate for the errors introduced by the
*   polyphase filter that produced the subbands. This error is deterministic,
*   hence it can be fully compensated for.
* - Transpose the data so that the time slices for each channel are placed
*   consecutively in memory.
*
* @param[out] correctedDataPtr    pointer to output data of ::OutputDataType,
*                                 a 3D array [station][channel][sample][complex]
*                                 of ::complex (2 complex polarizations)
* @param[in]  filteredDataPtr     pointer to input data; this can either be a
*                                 4D array [station][polarization][sample][channel][complex]
*                                 of ::fcomplex
* @param[in]  subbandFrequency    center freqency of the subband
* @param[in]  beam                index number of the beam
* @param[in]  delaysAtBeginPtr    pointer to delay data of ::DelaysType,
*                                 a 2D array [beam][station] of float2 (real:
*                                 2 polarizations), containing delays in
*                                 seconds at begin of integration period
* @param[in]  delaysAfterEndPtr   pointer to delay data of ::DelaysType,
*                                 a 2D array [beam][station] of float2 (real:
*                                 2 polarizations), containing delays in
*                                 seconds after end of integration period
* @param[in]  phase0sPt     r     pointer to phase offset data of
*                                 ::Phase0sType, a 1D array [station] of
*                                 float2 (real: 2 polarizations), containing
*                                 phase offsets in radians
* @param[in]  bandPassFactorsPtr  pointer to bandpass correction data of
*                                 ::BandPassFactorsType, a 1D array [channel] of
*                                 float, containing bandpass correction factors
*/

extern "C" {
  __global__ void applyDelaysAndCorrectBandPass(fcomplex * correctedDataPtr,
    const fcomplex * filteredDataPtr,
    const unsigned * delayIndices,
    double subbandFrequency,
    unsigned beam,
    const double * delaysAtBeginPtr,
    const double * delaysAfterEndPtr,
    const double * phase0sPtr,
    const float * bandPassFactorsPtr)
  {
    OutputDataType outputData = (OutputDataType)correctedDataPtr;
    InputDataType inputData = (InputDataType)filteredDataPtr;

    /* The z dimension is NR_STATIONS wide. */
    const unsigned station = blockIdx.z * blockDim.z + threadIdx.z;
    const unsigned delayIdx = delayIndices[station];

    /*
     * channel: will cover all channels
     * timeStart & timeInc: will cover all samples
     */

#ifdef DO_TRANSPOSE
    /* X width: 256 wide, split into major and minor. */
    /* minor is used to index channels */
    /* major is used to index time */
    /* (minor,major) is used for a local transpose before writing output */
    const unsigned major = (blockIdx.x * blockDim.x + threadIdx.x) / 16;
    const unsigned minor = (blockIdx.x * blockDim.x + threadIdx.x) % 16;

    /* Y width: NR_CHANNELS/16 (or 1 if NR_CHANNELS == 1) */
    const unsigned channel = NR_CHANNELS == 1 ? 0 : (blockIdx.y * blockDim.y + threadIdx.y) * 16 + minor;

    /* NR_CHANNELS == 1: Start at 0..255,        jump by 256 */
    /* NR_CHANNELS  > 1: Start at 0..15 (major), jump by 16 */
    const unsigned timeStart = NR_CHANNELS == 1 ? threadIdx.x : major;
    const unsigned timeInc = NR_CHANNELS == 1 ? blockDim.x : 16;
#else
    /* Y width: nrChannels, with 16 per block (or 1 if NR_CHANNELS == 1) */
    const unsigned channel = blockIdx.y * blockDim.y + threadIdx.y;

    /* X width: nrSamplesPerChannel, with 16 per block */
    const unsigned timeStart = blockIdx.x * blockDim.x + threadIdx.x;

    /* Do one sample per thread */
    const unsigned timeInc = NR_SAMPLES_PER_CHANNEL;
#endif

#if defined BANDPASS_CORRECTION
    BandPassFactorsType bandPassFactors = (BandPassFactorsType)bandPassFactorsPtr;

    float weight((*bandPassFactors)[channel]);
#endif

#if defined DELAY_COMPENSATION
    DelaysType delaysAtBegin = (DelaysType)delaysAtBeginPtr;
    DelaysType delaysAfterEnd = (DelaysType)delaysAfterEndPtr;
    Phase0sType phase0s = (Phase0sType)phase0sPtr;

    /*
    * Delay compensation means rotating the phase of each sample BACK.
    *
    * n     = channel number (f.e. 0 .. 255)
    * f_n   = channel frequency of channel n
    * f_ref = base frequency of subband (f.e. 200 MHz)
    * df    = delta frequency of 1 channel (f.e. 768 Hz)
    *
    * f_n := f_ref + n * df
    *
    * m      = sample number (f.e. 0 .. 3071)
    * tau_m  = delay at sample m
    * tau_0  = delayAtBegin (f.e. -2.56us .. +2.56us)
    * dtau   = delta delay for 1 sample (f.e. <= 1.6ns)
    *
    * tau_m := tau_0 + m * dtau
    *
    * Then, the required phase shift is:
    *
    *   phi_mn = -2 * pi * f_n * tau_m
    *          = -2 * pi * (f_ref + n * df) * (tau_0 + m * dtau)
    *          = -2 * pi * (f_ref * tau_0 + f_ref * m * dtau + tau_0 * n * df + m * n * df * dtau)
    *                       -------------   ----------------   --------------   -----------------
    *                           O(100)           O(0.1)            O(0.01)          O(0.001)
    *
    * Finally, we also want to correct for fixed phase offsets per station,
    * as given by the phase0 array.
    */

    const double frequency = NR_CHANNELS == 1
      ? subbandFrequency
      : subbandFrequency - 0.5 * SUBBAND_BANDWIDTH + channel * (SUBBAND_BANDWIDTH / NR_CHANNELS);

    const double2 delayAtBegin = make_double2((*delaysAtBegin)[beam][delayIdx][0], (*delaysAtBegin)[beam][delayIdx][1]);
    const double2 delayAfterEnd = make_double2((*delaysAfterEnd)[beam][delayIdx][0], (*delaysAfterEnd)[beam][delayIdx][1]);

    // Calculate the angles to rotate for for the first and (beyond the) last sample.
    //
    // We need to undo the delay, so we rotate BACK, resulting in a negative constant factor.
    const double2 phiAtBegin = -2.0 * M_PI * frequency * delayAtBegin - (*phase0s)[delayIdx];
    const double2 phiAfterEnd = -2.0 * M_PI * frequency * delayAfterEnd - (*phase0s)[delayIdx];
#endif

    for (unsigned time = timeStart; time < NR_SAMPLES_PER_CHANNEL; time += timeInc)
    {
      fcomplex sampleX = (*inputData)[station][0][time][channel];
      fcomplex sampleY = (*inputData)[station][1][time][channel];

#if defined DELAY_COMPENSATION    
      // Offset of this sample between begin and end.
      const double timeOffset = double(time) / NR_SAMPLES_PER_CHANNEL;

      // Interpolate the required phase rotation for this sample.
      //
      // Single precision angle + sincos is measured to be good enough (2013-11-20).
      // Note that we do the interpolation in double precision still.
      // We can afford to if we keep this kernel memory bound.
      const float2 phi = make_float2(phiAtBegin.x  * (1.0 - timeOffset)
        + phiAfterEnd.x *        timeOffset,
        phiAtBegin.y  * (1.0 - timeOffset)
        + phiAfterEnd.y *        timeOffset);

      sampleX = sampleX * sincos_f2f(phi.x);
      sampleY = sampleY * sincos_f2f(phi.y);
#endif

#if defined BANDPASS_CORRECTION
      sampleX.x *= weight;
      sampleX.y *= weight;
      sampleY.x *= weight;
      sampleY.y *= weight;
#endif

      // Support all variants of NR_CHANNELS and DO_TRANSPOSE for testing etc.
      // Transpose: data order is [station][channel][time][pol]
#if NR_CHANNELS > 1 && defined DO_TRANSPOSE
      __shared__ fcomplex tmp[16][17][2]; // one too wide to avoid bank-conflicts on read

      tmp[major][minor][0] = sampleX;
      tmp[major][minor][1] = sampleY;
      __syncthreads();
      (*outputData)[station][channel - minor + major][time - major + minor][0] = tmp[minor][major][0];
      (*outputData)[station][channel - minor + major][time - major + minor][1] = tmp[minor][major][1];
      __syncthreads();
#elif NR_CHANNELS == 1 && defined DO_TRANSPOSE
      (*outputData)[station][0][time][0] = sampleX;
      (*outputData)[station][0][time][1] = sampleY;

#else
      // No transpose: data order is [station][pol][channel][time]
      (*outputData)[station][0][channel][time] = sampleX;
      (*outputData)[station][1][channel][time] = sampleY;
#endif
    }
  }
}

