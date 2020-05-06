//# generator.cc: Generates fake data resembling a single station.
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

#include <string>
#include <vector>
#include <omp.h>
#include <unistd.h>

#include <Common/LofarLogger.h>
#include <Stream/StreamFactory.h>
#include <Stream/NetFuncs.h>

#include <InputProc/Station/PacketFactory.h>
#include <InputProc/Station/Generator.h>
#include <CoInterface/Parset.h>

#include <mpi.h>
#include <InputProc/Transpose/MPIUtil.h>

using namespace LOFAR;
using namespace Cobalt;
using namespace std;

void usage()
{
  cerr << "Usage: generator -p parset [options]" << endl;
  cerr << endl;
  cerr << "Generates the RSP data streams as they would come from a station." << endl;
  cerr << "If run in MPI, the stations for which to generate are distributed among the nodes." << endl;
  cerr << endl;
  cerr << "-h              Show this help." << endl;
  cerr << "-p parset       Read configuration from given (augmented) parset." << endl;
  cerr << "-s stations     Override station list (comma separated)." << endl;
}

// Create a skeleton parset
void populateParsetSkeleton(Parset &ps)
{
  // Add one beam
  ps.add("Observation.nrBeams", "1");
  ps.add("Observation.Beam[0].subbandList", "[0]");

  // Add at least one station
  ps.add("Observation.VirtualInstrument.stationList", "[CS001]");
}

int main( int argc, char **argv )
{
  // Initialise MPI object before the logger, to make $MPIRANK available
  LOFAR::Cobalt::MPI mpi;

  INIT_LOGGER( "generate" );

  int opt;
  Parset ps;
  string stationListOverride = "";

  populateParsetSkeleton(ps);

  // parse all command-line options
  while ((opt = getopt(argc, argv, "hp:s:")) != -1) {
    switch (opt) {
    case 'p':
      ps.adoptFile(optarg);
      break;

    case 's':
      stationListOverride = optarg;
      break;

    case 'h':
      usage();
      exit(0);

    default: /* '?' */
      usage();
      exit(1);
    }
  }

  // we expect no further arguments
  if (optind != argc) {
    usage();
    exit(1);
  }

  if (stationListOverride != "")
    ps.replace("Observation.VirtualInstrument.stationList", "[" + stationListOverride + "]");

  // regenerate ps.settings
  ps.updateSettings();

  mpi.init(argc, argv);
  LOG_INFO_STR("MPI rank " << mpi.rank() << " out of " << mpi.size() << " hosts");

  omp_set_nested(true);
  omp_set_num_threads(16);

  struct BoardMode mode(ps.settings.nrBitsPerSample, ps.settings.clockMHz);
  const TimeStamp from(time(0), 3, mode.clockHz());
  const TimeStamp to(0);

  // get all 10Gbps interfaces which are connected
  set<string> interfaces_set = myInterfaces(false, true, 10e9);

  vector<string> interfaces;
  for(auto iface : interfaces_set) {
    if(iface.find("10GB") != string::npos)
      interfaces.push_back(iface);
  }

  if(interfaces.size() > 0) {
      LOG_INFO_STR("Using the following interfaces for sending udp packets: " << interfaces);
  } else {
      LOG_ERROR_STR("No interfaces available for sending udp packets");
      exit(1);
  }

  #pragma omp parallel for num_threads(ps.settings.antennaFields.size())
  for (size_t f = 0; f < ps.settings.antennaFields.size(); ++f) {
    const ObservationSettings::AntennaField& field = ps.settings.antennaFields[f];

    // Distribute the fields round-robin over the MPI processes
    if (static_cast<int>(f) % mpi.size() != mpi.rank())
      continue;

    // Skip stations without any boards defined
    if (field.inputStreams.size() == 0) {
      LOG_WARN_STR("[" << field.name << "] No streams defined. Ignoring.");
      continue;
    }

    vector< SmartPtr<Stream> > outputStreams;

    for (size_t s = 0; s < field.inputStreams.size(); ++s) {
      string desc = field.inputStreams[s];

      // distribute the outgoing streams over the available network interfaces (round robin)
      if(interfaces.size() > 1) {
        desc += ":" + interfaces[(f+outputStreams.size())%interfaces.size()];
      }

      LOG_INFO_STR("[" << field.name << "] Creating stream to " << desc);
      outputStreams.push_back(createStream(desc, false));
      LOG_INFO_STR("[" << field.name << "] Created stream to " << desc);
    }

    struct StationID stationID(field.name);

    PacketFactory factory(mode);
    Generator g(stationID, outputStreams, factory, from, to);

    // Generate packets
    g.process();
  }
}

