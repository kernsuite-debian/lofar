//# tZeroingKernel.cc: test ZeroingKernel class
//#
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


#include <lofar_config.h>

#include <GPUProc/Kernels/ZeroingKernel.h>
#include <GPUProc/MultiDimArrayHostBuffer.h>
#include <CoInterface/BlockID.h>
#include <CoInterface/SubbandMetaData.h>
#include <CoInterface/Config.h>
#include <CoInterface/Parset.h>
#include <Common/LofarLogger.h>

#include <UnitTest++.h>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/scoped_ptr.hpp>
#include <iostream>
#include <iomanip>
#include <vector>

using namespace std;
using namespace boost;
using namespace LOFAR;
using namespace LOFAR::Cobalt;

typedef complex<float> fcomplex;

// Fixture for testing correct translation of parset values
struct ParsetSUT
{
  size_t  nrChannels, nrStations, nrSamples;

  Parset parset;

  ParsetSUT(size_t nrStations, size_t nrChannels,
            size_t nrSamples)
  :
    nrChannels(nrChannels),
    nrStations(nrStations),
    nrSamples(nrSamples)
  {
    // 4 for number of stokes
    parset.add("Observation.DataProducts.Output_Correlated.enabled", "true");
    parset.add("Cobalt.Correlator.nrChannelsPerSubband", lexical_cast<string>(nrChannels));
    parset.add("Observation.VirtualInstrument.stationList",
      str(format("[%d*RS000]") % nrStations));
    parset.add("Observation.antennaSet", "LBA_INNER");
    parset.add("Observation.rspBoardList", "[0]");
    parset.add("Observation.rspSlotList", "[0]");
    parset.add("Cobalt.blockSize",
      lexical_cast<string>(nrSamples));
    parset.add("Observation.nrBeams", "1");
    parset.add("Observation.Beam[0].subbandList", "[0]");
    parset.add("Observation.DataProducts.Output_Correlated.filenames", "[dummy.raw]");
    parset.add("Observation.DataProducts.Output_Correlated.locations",  "[:.]");
    //parset.add(""); //ps.settings.beamFormer.nrDelayCompensationChannels
    parset.updateSettings();

  }
};


struct SUTWrapper : ParsetSUT
{
  gpu::Device device;
  gpu::Context context;
  gpu::Stream stream;
  size_t nrSTABs;
  KernelFactory<ZeroingKernel> factory;
  MultiDimArrayHostBuffer<fcomplex, 4> hData;
  MultiDimArrayHostBuffer<fcomplex, 4> hRefOutput;
  gpu::DeviceMemory deviceMemory;
  scoped_ptr<ZeroingKernel> kernel;

  SUTWrapper(size_t nrStations, size_t nrChannels, size_t nrSamples) :
    ParsetSUT(nrStations, nrChannels, nrSamples),
    device(gpu::Platform().devices()[0]),
    context(device),
    stream(context),
    nrSTABs(parset.settings.antennaFields.size()),
    factory(ZeroingKernel::Parameters(parset, nrStations, nrChannels)),
    hData(
      boost::extents[nrStations][NR_POLARIZATIONS][nrSamples / nrChannels][nrChannels],
      context),
    hRefOutput(
      boost::extents[nrStations][NR_POLARIZATIONS][nrSamples / nrChannels][nrChannels],
      context),
    deviceMemory(context, factory.bufferSize(ZeroingKernel::INPUT_DATA)),
    kernel(factory.create(stream, deviceMemory, deviceMemory))
  {
    initializeHostBuffers();
  }


  // Initialize all the elements of the input host buffer to (1, 2)
  void initializeHostBuffers()
  {
    cout << "Kernel buffersize set to: " << factory.bufferSize(
              ZeroingKernel::INPUT_DATA) << endl;
    cout << "\nInitializing host buffers..." << endl
      << " buffers.input.size()  = " << setw(7) << deviceMemory.size() << endl
      << " hData.size()  = " << setw(7) << hData.size() << endl
      << " buffers.output.size() = " << setw(7) << deviceMemory.size() 
      << endl;
    CHECK_EQUAL(deviceMemory.size(), hData.size());
    fill(hData.data(), hData.data() + hData.num_elements(),
             fcomplex(1.0f, 2.0f));
    fill(hRefOutput.data(), hRefOutput.data() + hRefOutput.num_elements(),
             fcomplex(1.0f, 2.0f));
  }

  void runKernel(const MultiDimArray<SparseSet<unsigned>, 1> &channelFlags)
  {
    // Dummy BlockID
    BlockID blockId;
    // Copy input data from host- to device buffer synchronously
    stream.writeBuffer(deviceMemory, hData, true);
    // Launch the kernel
    kernel->enqueue(blockId, channelFlags);
    // Copy output data from device- to host buffer synchronously
    stream.readBuffer(hData, deviceMemory, true);
  }

};

// Test if we can succesfully create all necessary classes and run the kernel
TEST(BasicRun)
{
  cout << "running test: BasicRun" << endl;
  SUTWrapper sut(2, 1, 4096);
  MultiDimArray<SparseSet<unsigned>, 1> channelFlags(boost::extents[sut.nrSTABs]);

  sut.runKernel(channelFlags);
}

// If we flag nothing, nothing should change
TEST(NothingFlaggedTest)
{
  cout << "running test: NothingFlaggedTest" << endl;
  SUTWrapper sut(5, 64, 1024);
  MultiDimArray<SparseSet<unsigned>, 1> channelFlags(boost::extents[sut.nrSTABs]);

  // run kernel
  cout << "Running kernel" << endl;
  sut.runKernel(channelFlags);

  // compare output
  cout << "Comparing output" << endl;
  CHECK_ARRAY_EQUAL(sut.hRefOutput.data(),
    sut.hData.data(),
    sut.hData.num_elements());
  cout << "Comparing output: done" << endl;
}

// If we flag one sample, it should zero in the output
TEST(SingleFlagTest)
{
  cout << "running test: SingleFlagTest" << endl;

  SUTWrapper sut(1, 64, 1024);
  MultiDimArray<SparseSet<unsigned>, 1> channelFlags(boost::extents[sut.nrSTABs]);

  // flag a sample
  cout << "Flagging 1 sample" << endl;
  channelFlags[0].include(13);

  // also zero reference output for flagged sample
  for (unsigned pol = 0; pol < NR_POLARIZATIONS; pol++)
    for (unsigned c = 0; c < sut.nrChannels; c++)
      sut.hRefOutput[0][pol][13][c] = 0.0f;

  // run kernel
  cout << "Running kernel" << endl;
  sut.runKernel(channelFlags);

  // compare output
  cout << "Comparing output" << endl;
  CHECK_ARRAY_EQUAL(sut.hRefOutput.data(),
    sut.hData.data(),
    sut.hData.num_elements());
  cout << "Comparing output: done" << endl;
}

// Flag patterns of input and check if the kernel zeroes the correct samples
TEST(PatternsTest)
{
  cout << "running test: PatternsTest" << endl;

  size_t nrStations[] = { 12, 53, 66, 77, 80 };
  size_t nrSamples = 16384;
  size_t nrChannels[] = { 1, 16, 64, 256 };

  for (unsigned st = 0; st < sizeof nrStations / sizeof nrStations[0]; ++st)
  for (unsigned ch = 0; ch < sizeof nrChannels / sizeof nrChannels[0]; ++ch)
  {
    cout << "******* pattern testing stations: " << nrStations[st]
      << " channels: " << nrChannels[ch] << endl;

    SUTWrapper sut(nrStations[st], nrChannels[ch], nrSamples);
    MultiDimArray<SparseSet<unsigned>, 1> channelFlags(boost::extents[sut.nrSTABs]);

    // flag samples (with different patterns per station)
    cout << "Flagging samples" << endl;
    for (unsigned st_z = 0; st_z < nrStations[st]; st_z++)
    for (unsigned sample_z = st_z; sample_z < nrSamples/nrChannels[ch]; sample_z += st_z + 1) {
      channelFlags[st_z].include(sample_z);

      // also zero reference output
      for (unsigned pol = 0; pol < NR_POLARIZATIONS; pol++)
        for (unsigned c = 0; c < sut.nrChannels; c++)
          sut.hRefOutput[st_z][pol][sample_z][c] = 0.0f;
    }

    // run kernel
    cout << "Running kernel" << endl;
    sut.runKernel(channelFlags);

    // compare output
    cout << "Comparing output" << endl;
    CHECK_ARRAY_EQUAL(sut.hRefOutput.data(),
      sut.hData.data(),
      sut.hData.num_elements());
    cout << "Comparing output: done" << endl;
  }
}

// Flag all samples, and test GPU performance
TEST(PerformanceTest)
{
  cout << "running test: PerformanceTest" << endl;

  size_t nrStations = 80;
  size_t nrSamples = 196608;
  size_t nrChannels[] = { 1, 16, 64, 256 };

  for (unsigned ch = 0; ch < sizeof nrChannels / sizeof nrChannels[0] ; ++ch)
  {
    cout << "******* performance testing stations: " << nrStations
      << " channels: " << nrChannels[ch] << endl;

    SUTWrapper sut(nrStations, nrChannels[ch], nrSamples);
    MultiDimArray<SparseSet<unsigned>, 1> channelFlags(boost::extents[sut.nrSTABs]);

    // flag all samples (worst case)
    cout << "Flagging samples" << endl;
    for (unsigned st_z = 0; st_z < nrStations; st_z++)
      channelFlags[st_z].include(0, nrSamples / nrChannels[ch]);

    // run kernel
    cout << "Running kernel" << endl;
    for (int n = 0; n < 10; ++n)
      sut.runKernel(channelFlags);
  }
}


int main()
{
  INIT_LOGGER("tZeroingKernel");

  try {
    gpu::Platform pf;
  }
  catch (gpu::GPUException&) {
    cerr << "No GPU device(s) found. Skipping tests." << endl;
    return 3;
  }
  return UnitTest::RunAllTests() == 0 ? 0 : 1;  

}

