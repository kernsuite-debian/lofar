//# ZeroingKernel.h
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

#ifndef LOFAR_GPUPROC_CUDA_ZEROING_KERNEL_H
#define LOFAR_GPUPROC_CUDA_ZEROING_KERNEL_H

#include <Common/Timer.h>

#include <CoInterface/Parset.h>
#include <CoInterface/MultiDimArray.h>
#include <CoInterface/SparseSet.h>

#include <GPUProc/Kernels/Kernel.h>
#include <GPUProc/KernelFactory.h>
#include <GPUProc/gpu_wrapper.h>

namespace LOFAR
{
  namespace Cobalt
  {
    class ZeroingKernel : public CompiledKernel
    {
    public:
      static std::string theirSourceFile;
      static std::string theirFunction;

      enum BufferType
      {
        INPUT_DATA,
        OUTPUT_DATA,
        MASK
      };

      // Parameters that must be passed to the constructor of the
      // IntToFloatKernel class.
      struct Parameters : Kernel::Parameters
      {
        Parameters(const Parset& ps, unsigned nrSTABs, unsigned nrChannels, const std::string &name = "Zeroing");
        unsigned nrSTABs;

        unsigned nrChannels;
        unsigned nrSamplesPerChannel;

        size_t bufferSize(BufferType bufferType) const;
      };

      // Construct a Zeroing kernel.
      // \pre The number of samples per channel must be even.
      // \pre The product of the number of stations, the number of
      // polarizations, the number of channels per subband, and the number of
      // samples per channel must be divisible by the maximum number of threads
      // per block (typically 1024).
      ZeroingKernel(const gpu::Stream &stream,
                     const gpu::Module &module,
                     const Buffers &buffers,
                     const Parameters &param);

      // Run the kernel. "channelFlags" is the set of flags, one for each station/tab
      void enqueue(const BlockID &blockId, const MultiDimArray<SparseSet<unsigned>, 1> &channelFlags);

    private:
      const unsigned nrSTABs;
      const unsigned nrSamplesPerChannel;

      // The flag mask per sample (1=flagged, 0=ok)
      gpu::DeviceMemory gpuMask;
      gpu::HostMemory hostMask;

      NSTimer computeMaskTimer;
    };

    //# --------  Template specializations for KernelFactory  -------- #//

    template<> CompileDefinitions
    KernelFactory<ZeroingKernel>::compileDefinitions() const;
  }

}

#endif

