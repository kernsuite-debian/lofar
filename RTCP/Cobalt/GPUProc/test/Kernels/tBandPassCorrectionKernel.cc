//# tBandPassCorrectionKernel.cc: test Kernels/BandPassCorrectionKernel class
//# Copyright (C) 2013  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <Common/LofarLogger.h>
#include <CoInterface/Parset.h>
#include <GPUProc/gpu_wrapper.h>
#include <GPUProc/gpu_utils.h>
#include <GPUProc/BandPass.h>
#include <GPUProc/Kernels/BandPassCorrectionKernel.h>
#include <GPUProc/PerformanceCounter.h>
#include <CoInterface/BlockID.h>

using namespace std;
using namespace LOFAR::Cobalt;

int main() {
  INIT_LOGGER("tBandPassCorrectionKernel");

  // Set up gpu environment
  try {
    gpu::Platform pf;
    cout << "Detected " << pf.size() << " GPU devices" << endl;
  } catch (gpu::GPUException& e) {
    cerr << "No GPU device(s) found. Skipping tests." << endl;
    return 3;
  }
  gpu::Device device(0);
  vector<gpu::Device> devices(1, device);
  gpu::Context ctx(device);
  gpu::Stream stream(ctx);

  Parset ps("tBandPassCorrectionKernel.in_parset");
  BandPassCorrectionKernel::Parameters params(ps);
  params.nrDelayCompensationChannels = 64; // unused
  params.nrHighResolutionChannels = 4096;
  params.nrSamplesPerChannel = 
    ps.settings.blockSize / params.nrHighResolutionChannels;

  KernelFactory<BandPassCorrectionKernel> factory(params);

  // Get the buffers as created by factory
  gpu::DeviceMemory 
    inputData(ctx, factory.bufferSize(BandPassCorrectionKernel::INPUT_DATA)),
    filteredData(ctx, factory.bufferSize(BandPassCorrectionKernel::OUTPUT_DATA));

  unique_ptr<BandPassCorrectionKernel> kernel(factory.create(stream, inputData, filteredData));

  BlockID blockId;
  kernel->enqueue(blockId);
  stream.synchronize();

  return 0;
}

