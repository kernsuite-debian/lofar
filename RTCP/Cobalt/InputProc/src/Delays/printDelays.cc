//# printDelays.cc: Print all delays generated for an observation
//# Copyright (C) 2012-2014  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <iostream>
#include <boost/format.hpp>

#include <Common/LofarLogger.h>

#include <CoInterface/Parset.h>
#include <InputProc/Delays/Delays.h>

using namespace LOFAR;
using namespace Cobalt;
using namespace std;
using boost::format;

string printDouble3Vector( const vector<double> &vec )
{
  ASSERT(vec.size() == 3);

  return str(format("[%.3f, %.3f, %.3f]") % vec[0] % vec[1] % vec[2]);
}

void printDelays( const Parset &ps, ssize_t antennaFieldIdx ) {
  const string antennaFieldName = ps.settings.antennaFields[antennaFieldIdx].name;

  /* Determine start/stop/blocksize parameters */
  const TimeStamp from(ps.settings.startTime * ps.settings.subbandWidth(), ps.settings.clockHz());
  const TimeStamp to(ps.settings.stopTime * ps.settings.subbandWidth(), ps.settings.clockHz());
  ssize_t block = -1;
  size_t blockSize = ps.settings.blockSize;

  /* Print header */
  cout << "# Station:          " << antennaFieldName << endl;
  cout << "# Phase center:     " << printDouble3Vector(ps.settings.antennaFields[antennaFieldIdx].phaseCenter) << endl;
  cout << "# Clock correction: " << str(format("%.15f") % ps.settings.antennaFields[antennaFieldIdx].clockCorrection) << endl;
  cout << "# block field timestamp dir.x dir.y dir.z delay" << endl;
  cout.flush();

  /* Start delay compensation thread */
  Delays delays(ps, antennaFieldIdx, from, blockSize);

  /* Produce and print delays for the whole observation */
  for (TimeStamp current = from + block * blockSize; current < to; current += blockSize, ++block) 
  {
    Delays::AllDelays delaySet(ps);

    delays.getNextDelays(delaySet);


    Delays::Delay d = delaySet.SAPs[0].SAP;
    cout << str(format("%9s %u %.15f %.15f %.15f %.15f %.15e")
          % antennaFieldName
          % block
          % current.getSeconds()
          % d.direction[0] % d.direction[1] % d.direction[2]
          % d.delay) << endl;
  }
}

int main( int argc, char **argv )
{
  INIT_LOGGER( "printDelays" );

  if (argc < 2) {
    cerr << "Syntax: printDelays L1234.parset [antenna_field_name]" << endl;
    exit(1);
  }

  Parset ps(argv[1]);

  ssize_t antennaFieldIdx = -1;
  
  if (argc >= 3) {
    const string antennaFieldName = argv[2];

    antennaFieldIdx = ps.settings.antennaFieldIndex(antennaFieldName);

    if (antennaFieldIdx < 0) {
      LOG_ERROR_STR("Could not find antenna field name in parset: " << antennaFieldName);
      exit(1);
    }
  }

  const TimeStamp from(ps.settings.startTime * ps.settings.subbandWidth(), ps.settings.clockHz());
  const TimeStamp to(ps.settings.stopTime * ps.settings.subbandWidth(), ps.settings.clockHz());
  size_t blockSize = ps.settings.blockSize;

  /* Print header */
  cout << "# Parset:           " << argv[1] << endl;
  cout << "# Delay comp?:      " << ps.settings.delayCompensation.enabled << endl;
  cout << "# Clock corr?:      " << ps.settings.corrections.clock << endl;
  cout << "# Ref Phase center: " << printDouble3Vector(ps.settings.delayCompensation.referencePhaseCenter) << endl;
  cout << "#" << endl;
  cout << "# Start:            " << from << endl;
  cout << "# Stop:             " << to << endl;
  cout << "# BlockSize:        " << blockSize << " samples" << endl;
  cout << "#" << endl;
  cout << "# Applied delay := delay + clockCorrection" << endl;
  cout << "# Printed delays are those at beginning of reported block = end of previous block" << endl;
  cout << "# COBALT does linear interpolation between begin and end delay for every block." << endl;
  cout << endl;

  if (antennaFieldIdx >= 0) {
    // print specified field
    printDelays(ps, antennaFieldIdx);
  } else {
    // print all fields
    for (size_t f = 0; f < ps.settings.antennaFields.size(); ++f)
      printDelays(ps, f);
  }


  return 0;
}


