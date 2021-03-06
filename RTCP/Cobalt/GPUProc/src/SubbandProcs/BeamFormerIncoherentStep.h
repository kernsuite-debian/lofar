//# BeamFormerIncoherentStep.h
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
//# $Id: BeamFormerIncoherentStep.h 42125 2019-03-08 13:17:27Z mol $

#ifndef LOFAR_GPUPROC_CUDA_BEAM_FORMER_INCOHERENT_STEP_H
#define LOFAR_GPUPROC_CUDA_BEAM_FORMER_INCOHERENT_STEP_H


#include <complex>

#include <Common/LofarLogger.h>
#include <CoInterface/Parset.h>

#include <boost/shared_ptr.hpp>
#include <GPUProc/gpu_wrapper.h>

#include <GPUProc/MultiDimArrayHostBuffer.h>
#include <CoInterface/BlockID.h>

#include "SubbandProcInputData.h"
#include "SubbandProcOutputData.h"
#include "ProcessStep.h"

#include <GPUProc/Kernels/FFT_Kernel.h>
#include <GPUProc/Kernels/FFTShiftKernel.h>
#include <GPUProc/Kernels/FIR_FilterKernel.h>
#include <GPUProc/Kernels/IncoherentStokesKernel.h>
#include <GPUProc/Kernels/IncoherentStokesTransposeKernel.h>


namespace LOFAR
{
  namespace Cobalt
  {
    class BeamFormerIncoherentStep : public ProcessStep
    {
    public:
      struct Factories
      {
        Factories(const Parset &ps, size_t nrSubbandsPerSubbandProc = 1);

        KernelFactory<IncoherentStokesTransposeKernel> incoherentStokesTranspose;
        KernelFactory<FFT_Kernel> incoherentInverseFFT;
        KernelFactory<FFTShiftKernel> incoherentInverseFFTShift;
        SmartPtr< KernelFactory<FIR_FilterKernel> > incoherentFirFilter;
        SmartPtr< KernelFactory<FFT_Kernel> > incoherentFinalFFT;
        KernelFactory<IncoherentStokesKernel> incoherentStokes;
      };

      BeamFormerIncoherentStep(const Parset &parset,
        gpu::Stream &i_queue,
        gpu::Context &context,
        Factories &factories,
        boost::shared_ptr<gpu::DeviceMemory> i_devA,
        boost::shared_ptr<gpu::DeviceMemory> i_devB
        );

      gpu::DeviceMemory outputBuffer();

      void process(const SubbandProcInputData &input);

      void readOutput(SubbandProcOutputData &output);

    private:

      // Data members
      boost::shared_ptr<gpu::DeviceMemory> devA;
      boost::shared_ptr<gpu::DeviceMemory> devB;

      // *****************************************************************
      //  Objects needed to produce incoherent stokes output
      const bool incoherentStokesPPF;

      // Transpose 
      std::unique_ptr<IncoherentStokesTransposeKernel> incoherentTranspose;

      // Inverse (4k points) FFT
      std::unique_ptr<FFT_Kernel> incoherentInverseFFT;

      // Inverse FFT-shift
      std::unique_ptr<FFTShiftKernel> incoherentInverseFFTShiftKernel;

      // Poly-phase filter (FIR + FFT)
      std::unique_ptr<FIR_FilterKernel> incoherentFirFilterKernel;
      std::unique_ptr<FFT_Kernel> incoherentFinalFFT;

      // Incoherent Stokes
      std::unique_ptr<IncoherentStokesKernel> incoherentStokesKernel;

      PerformanceCounter outputCounter;

      size_t nrIncoherent(const BlockID &blockID) const;
    };
  }
}

#endif

