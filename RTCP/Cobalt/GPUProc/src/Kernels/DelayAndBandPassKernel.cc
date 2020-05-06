//# DelayAndBandPassKernel.cc
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

#include "DelayAndBandPassKernel.h"

#include <GPUProc/gpu_utils.h>
#include <GPUProc/BandPass.h>
#include <CoInterface/BlockID.h>
#include <CoInterface/Config.h>
#include <Common/lofar_complex.h>
#include <Common/LofarLogger.h>

#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#include <fstream>

using boost::lexical_cast;
using boost::format;

namespace LOFAR
{
  namespace Cobalt
  {
    string DelayAndBandPassKernel::theirSourceFile = "DelayAndBandPass.cu";
    string DelayAndBandPassKernel::theirFunction = "applyDelaysAndCorrectBandPass";

    DelayAndBandPassKernel::Parameters::Parameters(const Parset& ps, bool correlator) :
      Kernel::Parameters(correlator ? "delayAndBandPass" : "delayCompensation"),
      nrStations(correlator ? ps.settings.antennaFieldNames.size() : ps.settings.beamFormer.antennaFieldNames.size()),
      delayIndices(nrStations),
      nrDelays(ps.settings.antennaFieldNames.size()),
      nrBitsPerSample(ps.settings.nrBitsPerSample),
      nrChannels(correlator ? ps.settings.correlator.nrChannels
                            : ps.settings.beamFormer.nrDelayCompensationChannels),
      nrSamplesPerChannel(ps.settings.blockSize / nrChannels),
      subbandBandwidth(ps.settings.subbandWidth()),

      nrSAPs(ps.settings.SAPs.size()),
      
      delayCompensation(ps.settings.delayCompensation.enabled),
      correctBandPass(correlator ? ps.settings.corrections.bandPass
                                 : false),
      transpose(correlator ? true
                           : false)
    {
      if (correlator) {
        // Use identity mappnig for station indices
        for (unsigned i = 0; i < nrStations; i++)
          delayIndices[i] = i;
      } else {
        delayIndices = ObservationSettings::AntennaFieldName::indices(
          ps.settings.beamFormer.antennaFieldNames,
          ps.settings.antennaFieldNames);
      }

      dumpBuffers = 
        ps.getBool("Cobalt.Kernels.DelayAndBandPassKernel.dumpOutput", false);
      dumpFilePattern = 
        str(format("L%d_SB%%03d_BL%%03d_DelayAndBandPassKernel_%c%c%c.dat") % 
            ps.settings.observationID %
            (correctBandPass ? "B" : "b") %
            (delayCompensation ? "D" : "d") %
            (transpose ? "T" : "t"));
    }


    unsigned DelayAndBandPassKernel::Parameters::nrSamplesPerSubband() const {
      return nrChannels * nrSamplesPerChannel;
    }


    unsigned DelayAndBandPassKernel::Parameters::nrBytesPerComplexSample() const {
      return sizeof(std::complex<float>);
    }


    size_t DelayAndBandPassKernel::Parameters::bufferSize(BufferType bufferType) const {
      switch (bufferType) {
      case DelayAndBandPassKernel::INPUT_DATA: 
        return 
          (size_t) nrStations * NR_POLARIZATIONS * 
            nrSamplesPerSubband() * nrBytesPerComplexSample();
      case DelayAndBandPassKernel::OUTPUT_DATA:
        return
          (size_t) nrStations * NR_POLARIZATIONS * 
            nrSamplesPerSubband() * sizeof(std::complex<float>);
      case DelayAndBandPassKernel::DELAY_INDICES:
        return
          delayIndices.size() * sizeof delayIndices[0];
      case DelayAndBandPassKernel::DELAYS:
        return 
          (size_t) nrSAPs * nrDelays * 
            NR_POLARIZATIONS * sizeof(double);
      case DelayAndBandPassKernel::PHASE_ZEROS:
        return
          (size_t) nrDelays * NR_POLARIZATIONS * sizeof(double);
      case DelayAndBandPassKernel::BAND_PASS_CORRECTION_WEIGHTS:
        return
          correctBandPass ? (size_t) nrChannels * sizeof(float) : 1UL;
      default:
        THROW(GPUProcException, "Invalid bufferType (" << bufferType << ")");
      }
    }


    DelayAndBandPassKernel::DelayAndBandPassKernel(const gpu::Stream& stream,
                                       const gpu::Module& module,
                                       const Buffers& buffers,
                                       const Parameters& params) :
      CompiledKernel(stream, gpu::Function(module, theirFunction), buffers, params),
      delayIndices(stream.getContext(), params.bufferSize(DELAY_INDICES)),
      delaysAtBegin(stream.getContext(), params.bufferSize(DELAYS)),
      delaysAfterEnd(stream.getContext(), params.bufferSize(DELAYS)),
      phase0s(stream.getContext(), params.bufferSize(PHASE_ZEROS)),
      bandPassCorrectionWeights(stream.getContext(), params.bufferSize(BAND_PASS_CORRECTION_WEIGHTS))
    {
      LOG_DEBUG_STR("DelayAndBandPassKernel:" <<
                    " delayCompensation=" <<
                    (params.delayCompensation ? "true" : "false") <<
                    " #channels/sb=" << params.nrChannels <<
                    " correctBandPass=" << 
                    (params.correctBandPass ? "true" : "false") <<
                    " transpose=" << (params.transpose ? "true" : "false"));

      ASSERT(params.nrChannels % 16 == 0 || params.nrChannels == 1);
      ASSERT(params.nrSamplesPerChannel % 16 == 0);

      setArg(0, buffers.output);
      setArg(1, buffers.input);
      setArg(2, delayIndices);
      setArg(5, delaysAtBegin);
      setArg(6, delaysAfterEnd);
      setArg(7, phase0s);
      setArg(8, bandPassCorrectionWeights);

      if (params.transpose)
        setEnqueueWorkSizes( gpu::Grid(256,
                                     params.nrChannels == 1 ?
                                       1 :
                                       params.nrChannels / 16,
                                     params.nrStations),
                             gpu::Block(256, 1, 1) );
      else
        setEnqueueWorkSizes( gpu::Grid(params.nrSamplesPerChannel,
                                     params.nrChannels,
                                     params.nrStations),
                             gpu::Block(16, params.nrChannels == 1 ? 1 : 16, 1) );
      
      size_t nrSamples = (size_t)params.nrStations * params.nrChannels * params.nrSamplesPerChannel * NR_POLARIZATIONS;
      nrOperations = nrSamples * 12;
      nrBytesRead = nrBytesWritten = nrSamples * params.nrBytesPerComplexSample();

      // Initialise bandpass correction weights
      if (params.correctBandPass)
      {
        gpu::HostMemory bpWeights(stream.getContext(), bandPassCorrectionWeights.size());
        BandPass::computeCorrectionFactors(bpWeights.get<float>(), params.nrChannels);
        stream.writeBuffer(bandPassCorrectionWeights, bpWeights, true);
      }

      // upload delayIndices, as they are static across the observation
      gpu::HostMemory delayIndicesHost(stream.getContext(), params.bufferSize(DELAY_INDICES));
      std::memcpy(delayIndicesHost.get<void>(), &params.delayIndices.front(),
                  delayIndicesHost.size());
      stream.writeBuffer(delayIndices, delayIndicesHost, true);
    }


    void DelayAndBandPassKernel::enqueue(const BlockID &blockId,
                                         double subbandFrequency, unsigned SAP)
    {
      setArg(3, subbandFrequency);
      setArg(4, SAP);
      Kernel::enqueue(blockId);
    }

    //--------  Template specializations for KernelFactory  --------//

    template<> CompileDefinitions
    KernelFactory<DelayAndBandPassKernel>::compileDefinitions() const
    {
      CompileDefinitions defs =
        KernelFactoryBase::compileDefinitions(itsParameters);

      defs["NR_STATIONS"] = lexical_cast<string>(itsParameters.nrStations);
      defs["NR_DELAYS"] = lexical_cast<string>(itsParameters.nrDelays);
      defs["NR_BITS_PER_SAMPLE"] =
        lexical_cast<string>(itsParameters.nrBitsPerSample);

      defs["NR_CHANNELS"] = lexical_cast<string>(itsParameters.nrChannels);
      defs["NR_SAMPLES_PER_CHANNEL"] = 
        lexical_cast<string>(itsParameters.nrSamplesPerChannel);
      defs["NR_SAMPLES_PER_SUBBAND"] = 
        lexical_cast<string>(itsParameters.nrSamplesPerSubband());
      defs["SUBBAND_BANDWIDTH"] =
        str(format("%.7f") % itsParameters.subbandBandwidth);

      defs["NR_SAPS"] =
        lexical_cast<string>(itsParameters.nrSAPs);

      if (itsParameters.delayCompensation)
        defs["DELAY_COMPENSATION"] = "1";

      if (itsParameters.correctBandPass)
        defs["BANDPASS_CORRECTION"] = "1";

      if (itsParameters.transpose)
        defs["DO_TRANSPOSE"] = "1";

      return defs;
    }
  }
}
