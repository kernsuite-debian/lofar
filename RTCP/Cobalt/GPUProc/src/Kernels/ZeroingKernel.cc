//# ZeroingKernel.cc
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

#include "ZeroingKernel.h"

#include <GPUProc/gpu_utils.h>
#include <CoInterface/BlockID.h>
#include <CoInterface/Config.h>
#include <CoInterface/SubbandMetaData.h>
#include <Common/lofar_complex.h>
#include <Common/Timer.h>

#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#include <fstream>
#include <algorithm>

using boost::lexical_cast;
using boost::format;

namespace LOFAR
{
  namespace Cobalt
  {
    string ZeroingKernel::theirSourceFile = "Zeroing.cu";
    string ZeroingKernel::theirFunction = "Zeroing";

    ZeroingKernel::Parameters::Parameters(const Parset& ps, unsigned nrSTABs, unsigned nrChannels, const std::string &name):
      Kernel::Parameters(name),
      nrSTABs(nrSTABs),

      nrChannels(nrChannels),
      nrSamplesPerChannel(ps.settings.blockSize / nrChannels)
    {
      dumpBuffers = 
        ps.getBool("Cobalt.Kernels.ZeroingKernel.dumpOutput", false);
      dumpFilePattern = 
        str(format("L%d_SB%%03d_BL%%03d_ZeroingKernel.dat") % 
            ps.settings.observationID);
    }


    size_t ZeroingKernel::Parameters::bufferSize(BufferType bufferType) const
    {
      switch (bufferType) {
      case ZeroingKernel::INPUT_DATA:
      case ZeroingKernel::OUTPUT_DATA: // fall thru
        return (size_t)nrSTABs * NR_POLARIZATIONS *
          nrChannels * nrSamplesPerChannel *
          sizeof(std::complex<float>);

      case ZeroingKernel::MASK:
        return (size_t)nrSTABs * nrSamplesPerChannel;
          
      default:
        THROW(GPUProcException, "Invalid bufferType (" << bufferType << ")");
      }
    }

    ZeroingKernel::ZeroingKernel(const gpu::Stream& stream,
                                   const gpu::Module& module,
                                   const Buffers& buffers,
                                   const Parameters& params) :
      CompiledKernel(stream, gpu::Function(module, theirFunction), buffers, params),
      nrSTABs(params.nrSTABs),
      nrSamplesPerChannel(params.nrSamplesPerChannel),
      gpuMask(stream.getContext(), params.bufferSize(MASK)),
      hostMask(stream.getContext(), params.bufferSize(MASK)),
      computeMaskTimer("ZeroingKernel: compute mask", true, true)
    {
      setArg(0, buffers.input);
      setArg(1, gpuMask);
      
      // Number of samples per channel must be even
      ASSERT(params.nrSamplesPerChannel % 2 == 0);

      // We definitely want the lowest data dimensions in the same warp.
      // The size of the x dimension was tuned manually on a K10, using
      // tZeroingKernel | grep mean
      setEnqueueWorkSizes(
        gpu::Grid(params.nrSamplesPerChannel, params.nrChannels, params.nrSTABs * NR_POLARIZATIONS),
        gpu::Block(std::max(1U, 64U / params.nrChannels), params.nrChannels, NR_POLARIZATIONS));
    }


    void ZeroingKernel::enqueue(const BlockID &blockId, const MultiDimArray<SparseSet<unsigned>, 1> &channelFlags)
    {
      // marshall flags to GPU host buffer
      computeMaskTimer.start();
      for(unsigned station = 0; station < nrSTABs; ++station) {
        //LOG_DEBUG_STR("Flags for block " << blockId << ", station " << station << ": " << channelFlags[station]);
        channelFlags[station].toByteset(hostMask.get<char>() + station * nrSamplesPerChannel, nrSamplesPerChannel);
      }
      computeMaskTimer.stop();

      // Copy host buffer to GPU
      itsStream.writeBuffer(gpuMask, hostMask, false);

      Kernel::enqueue(blockId);
    }

    //--------  Template specializations for KernelFactory  --------//

    template<> CompileDefinitions
      KernelFactory<ZeroingKernel>::compileDefinitions() const
    {
      CompileDefinitions defs =
        KernelFactoryBase::compileDefinitions(itsParameters);

      defs["NR_STABS"] = lexical_cast<string>(itsParameters.nrSTABs);
      defs["NR_CHANNELS"] = lexical_cast<string>(itsParameters.nrChannels);
      defs["NR_SAMPLES_PER_CHANNEL"] = 
        lexical_cast<string>(itsParameters.nrSamplesPerChannel);

      return defs;
    }

  }
}
