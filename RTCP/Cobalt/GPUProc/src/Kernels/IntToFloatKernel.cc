//# IntToFloatKernel.cc
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

#include "IntToFloatKernel.h"

#include <GPUProc/gpu_utils.h>
#include <CoInterface/BlockID.h>
#include <CoInterface/Config.h>
#include <CoInterface/PrintVector.h>
#include <Common/lofar_complex.h>
#include <Common/LofarLogger.h>

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
    string IntToFloatKernel::theirSourceFile = "IntToFloat.cu";
    string IntToFloatKernel::theirFunction = "intToFloat";

    IntToFloatKernel::Parameters::Parameters(const Parset& ps, bool fftShift, bool beamFormerStationSubset) :
      Kernel::Parameters("intToFloat"),
      nrInputStations(ps.settings.antennaFields.size()),
      stationIndices(beamFormerStationSubset ? ObservationSettings::AntennaFieldName::indices(ps.settings.beamFormer.antennaFieldNames, ps.settings.antennaFieldNames) : vector<unsigned>()),
      nrBitsPerSample(ps.settings.nrBitsPerSample),

      nrSamplesPerSubband(ps.settings.blockSize),
      fftShift(fftShift),
      doStationSubset(beamFormerStationSubset)
    {
      dumpBuffers = 
        ps.getBool("Cobalt.Kernels.IntToFloatKernel.dumpOutput", false);
      dumpFilePattern = 
        str(format("L%d_SB%%03d_BL%%03d_IntToFloatKernel.dat") % 
            ps.settings.observationID);
    }


    unsigned IntToFloatKernel::Parameters::nrBytesPerComplexSample() const {
      return 2 * nrBitsPerSample / 8;
    }


    size_t IntToFloatKernel::Parameters::bufferSize(BufferType bufferType) const
    {
      switch (bufferType) {
      case IntToFloatKernel::INPUT_DATA:
        return
          (size_t) nrInputStations * NR_POLARIZATIONS * 
            nrSamplesPerSubband * nrBytesPerComplexSample();
      case IntToFloatKernel::OUTPUT_DATA:
        return
          (size_t) nrOutputStations() * NR_POLARIZATIONS * 
            nrSamplesPerSubband * sizeof(std::complex<float>);
      case IntToFloatKernel::STATION_INDICES:
        return 
          (size_t) stationIndices.size() * sizeof stationIndices[0];
      default:
        THROW(GPUProcException, "Invalid bufferType (" << bufferType << ")");
      }
    }


    IntToFloatKernel::IntToFloatKernel(const gpu::Stream& stream,
                                       const gpu::Module& module,
                                       const Buffers& buffers,
                                       const Parameters& params) :
      CompiledKernel(stream, gpu::Function(module, theirFunction), buffers, params),
      stationIndices(stream.getContext(), params.bufferSize(STATION_INDICES))
    {
      setArg(0, buffers.output);
      setArg(1, buffers.input);
      setArg(2, stationIndices);

      // upload stationIndices, as they are static across the observation
      gpu::HostMemory stationIndicesHost(stream.getContext(), params.bufferSize(STATION_INDICES));
      std::memcpy(stationIndicesHost.get<void>(), &params.stationIndices.front(),
                  stationIndicesHost.size());
      stream.writeBuffer(stationIndices, stationIndicesHost, true);

      ASSERTSTR(maxThreadsPerBlock % 2 == 0, "IntToFloat.cu requires an even stepsize.");
      setEnqueueWorkSizes( gpu::Grid(maxThreadsPerBlock, params.nrOutputStations()),
                           gpu::Block(maxThreadsPerBlock, 1) );

      unsigned nrSamples = params.nrOutputStations() * params.nrSamplesPerSubband * NR_POLARIZATIONS;
      nrOperations = (size_t) nrSamples * 2;
      nrBytesRead = (size_t) nrSamples * 2 * params.nrBitsPerSample / 8;
      nrBytesWritten = (size_t) nrSamples * sizeof(std::complex<float>);
    }

    //--------  Template specializations for KernelFactory  --------//

    template<> CompileDefinitions
    KernelFactory<IntToFloatKernel>::compileDefinitions() const
    {
      CompileDefinitions defs =
        KernelFactoryBase::compileDefinitions(itsParameters);

      defs["NR_INPUT_STATIONS"] = lexical_cast<string>(itsParameters.nrInputStations);
      defs["NR_OUTPUT_STATIONS"] = lexical_cast<string>(itsParameters.nrOutputStations());
      defs["NR_BITS_PER_SAMPLE"] =
        lexical_cast<string>(itsParameters.nrBitsPerSample);
      defs["NR_SAMPLES_PER_SUBBAND"] = 
        lexical_cast<string>(itsParameters.nrSamplesPerSubband);

      if (itsParameters.fftShift)
        defs["DO_FFTSHIFT"] = "1";
      if (itsParameters.doStationSubset)
        defs["DO_STATIONSUBSET"] = "1";

      return defs;
    }

  }
}

