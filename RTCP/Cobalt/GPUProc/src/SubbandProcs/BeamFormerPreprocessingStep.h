//# BeamFormerPreprocessingStep.h
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
//# $Id: BeamFormerPreprocessingStep.h 42125 2019-03-08 13:17:27Z mol $

#ifndef LOFAR_GPUPROC_CUDA_BEAM_FORMER_PREPROCESSING_STEP_H
#define LOFAR_GPUPROC_CUDA_BEAM_FORMER_PREPROCESSING_STEP_H

#include <complex>

#include <Common/LofarLogger.h>
#include <CoInterface/Parset.h>

#include <boost/shared_ptr.hpp>
#include <GPUProc/gpu_wrapper.h>

#include <GPUProc/MultiDimArrayHostBuffer.h>
#include <CoInterface/BlockID.h>
#include <CoInterface/SparseSet.h>
#include <CoInterface/MultiDimArray.h>

#include "SubbandProcInputData.h"
#include "SubbandProcOutputData.h"
#include "ProcessStep.h"

#include <GPUProc/KernelFactory.h>
#include <GPUProc/Kernels/BandPassCorrectionKernel.h>
#include <GPUProc/Kernels/DelayAndBandPassKernel.h>
#include <GPUProc/Kernels/FFTShiftKernel.h>
#include <GPUProc/Kernels/FFT_Kernel.h>
#include <GPUProc/Kernels/IntToFloatKernel.h>
#include <GPUProc/Kernels/ZeroingKernel.h>

namespace LOFAR
{
  namespace Cobalt
  {
    class BeamFormerPreprocessingStep: public ProcessStep
    {
    public:
      struct Factories {
        Factories(const Parset &ps);

        KernelFactory<IntToFloatKernel> intToFloat;

        KernelFactory<FFT_Kernel> firstFFT;
        KernelFactory<FFTShiftKernel> fftShift;

        KernelFactory<ZeroingKernel> zeroing;

        KernelFactory<DelayAndBandPassKernel> delayCompensation;

        KernelFactory<BandPassCorrectionKernel> bandPassCorrection;
      };

      BeamFormerPreprocessingStep(const Parset &parset,
        gpu::Stream &i_queue, 
        gpu::Context &context,
        Factories &factories,
        boost::shared_ptr<gpu::DeviceMemory> i_devA,
        boost::shared_ptr<gpu::DeviceMemory> i_devB);

      void writeInput(const SubbandProcInputData &input);

      void process(const SubbandProcInputData &input);

    private:
      // Preallocated flags for FFT-ed data -- used locally
      MultiDimArray<SparseSet<unsigned>, 1> flagsPerChannel;

      //Data members
      boost::shared_ptr<gpu::DeviceMemory> devA;
      boost::shared_ptr<gpu::DeviceMemory> devB;

      // Int -> Float conversion
      std::unique_ptr<IntToFloatKernel> intToFloatKernel;

      // First (64 points) FFT
      std::unique_ptr<FFT_Kernel> firstFFT;

      // Zeroing flagged samples
      std::unique_ptr<ZeroingKernel> zeroingKernel;

      // Delay compensation
      std::unique_ptr<DelayAndBandPassKernel> delayCompensationKernel;

      // Bandpass correction and tranpose
      std::unique_ptr<BandPassCorrectionKernel> bandPassCorrectionKernel;
    };
  }
}

#endif
