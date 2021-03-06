//# BeamFormerPreprocessingStep.cc
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

#include "BeamFormerPreprocessingStep.h"

#include <GPUProc/global_defines.h>
#include <GPUProc/gpu_wrapper.h>
#include <GPUProc/Flagger.h>

#include <CoInterface/Parset.h>
#include <ApplCommon/PosixTime.h>
#include <Common/LofarLogger.h>

#include <iomanip>

namespace LOFAR
{
  namespace Cobalt
  {
    BeamFormerPreprocessingStep::Factories::Factories(const Parset &ps) :
        intToFloat(IntToFloatKernel::Parameters(
          ps, 
          ps.settings.beamFormer.nrDelayCompensationChannels > 1,
          true)),

        firstFFT(FFT_Kernel::Parameters(
          ps.settings.beamFormer.nrDelayCompensationChannels,
          ps.settings.beamFormer.antennaFieldNames.size() * NR_POLARIZATIONS * ps.settings.blockSize,
          true,
          "FFT (beamformer, 1st)")),
        fftShift(FFTShiftKernel::Parameters(ps,
          ps.settings.beamFormer.antennaFieldNames.size(),
          ps.settings.beamFormer.nrDelayCompensationChannels,
          "FFT-shift (beamformer)")),

        zeroing(ZeroingKernel::Parameters(ps,
          ps.settings.beamFormer.antennaFieldNames.size(),
          ps.settings.beamFormer.nrDelayCompensationChannels,
          "Zeroing (beamformer)")),

        delayCompensation(DelayAndBandPassKernel::Parameters(ps, false)),

        bandPassCorrection(BandPassCorrectionKernel::Parameters(ps))
    {
    }

    BeamFormerPreprocessingStep::BeamFormerPreprocessingStep(
      const Parset &parset,
      gpu::Stream &i_queue,
      gpu::Context &context,
      Factories &factories,
      boost::shared_ptr<gpu::DeviceMemory> i_devA,
      boost::shared_ptr<gpu::DeviceMemory> i_devB)
      :
      ProcessStep(parset, i_queue),
      flagsPerChannel(boost::extents[parset.settings.antennaFields.size()])
    {
      devA=i_devA;
      devB=i_devB;
      (void)context;

      // intToFloat + FFTShift: A -> B
      intToFloatKernel = std::unique_ptr<IntToFloatKernel>(
        factories.intToFloat.create(queue, *devA, *devB));

      // FFT: B -> B
      firstFFT = std::unique_ptr<FFT_Kernel>(
        factories.firstFFT.create(queue, *devB, *devB));

      // zeroing: B -> B
      zeroingKernel = std::unique_ptr<ZeroingKernel>(
        factories.zeroing.create(queue, *devB, *devB));

      // delayComp: B -> A
      delayCompensationKernel = std::unique_ptr<DelayAndBandPassKernel>(
        factories.delayCompensation.create(queue, *devB, *devA));

      // bandPass: A -> B
      bandPassCorrectionKernel = std::unique_ptr<BandPassCorrectionKernel>(
        factories.bandPassCorrection.create(queue, *devA, *devB));
    }

    void BeamFormerPreprocessingStep::writeInput(const SubbandProcInputData &input)
    {
      if (ps.settings.delayCompensation.enabled)
      {
        queue.writeBuffer(delayCompensationKernel->delaysAtBegin,
          input.delaysAtBegin, false);
        queue.writeBuffer(delayCompensationKernel->delaysAfterEnd,
          input.delaysAfterEnd, false);
        queue.writeBuffer(delayCompensationKernel->phase0s,
          input.phase0s, false);
      }
    }

    void BeamFormerPreprocessingStep::process(const SubbandProcInputData &input)
    {

      //****************************************
      // Enqueue the kernels
      // Note: make sure to call the right enqueue() for each kernel.
      // Otherwise, a kernel arg may not be set...
      intToFloatKernel->enqueue(input.blockID);

      firstFFT->enqueue(input.blockID);

      // Convert input flags to channel flags
      Flagger::convertFlagsToChannelFlags(
        input.inputFlags,
        flagsPerChannel,
        ps.settings.blockSize,
        ps.settings.beamFormer.nrDelayCompensationChannels,
        0);

      zeroingKernel->enqueue(
        input.blockID,
        flagsPerChannel);

      // The centralFrequency and SAP immediate kernel args must outlive kernel runs.
      delayCompensationKernel->enqueue(
        input.blockID,
        ps.settings.subbands[input.blockID.globalSubbandIdx].centralFrequency,
        ps.settings.subbands[input.blockID.globalSubbandIdx].SAP);

      bandPassCorrectionKernel->enqueue(
        input.blockID);
    }
  }
}
