//# getCobaltHosts.cc: Real-Time Central Processor application, GPU cluster version
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
#include <unistd.h>
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>

#include <CoInterface/Parset.h>

using namespace std;
using namespace LOFAR;
using namespace LOFAR::Cobalt;

static void usage(const char *argv0)
{
  cerr << "Helper program used in combination with rtcp" << endl;
  cerr << "Extracts information from a parset and prints it in a machine-readable format." << endl;
  cerr << endl;
  cerr << "Usage: " << argv0 << " [-O] [-C] parset" << endl;
  cerr << endl;
  cerr << "  -O  Prints a space seperate list of outputProc hosts" << endl;
  cerr << "  -C  Prints the host that commands the run (first host GPUProc runs on)." << endl;
}

int main(int argc, char **argv)
{
  /*
  * Parse command-line options
  */

  int opt;
  bool printOutputProcHosts = false;
  bool printCommandHost = false;

  while ((opt = getopt(argc, argv, "hOC")) != -1) {
    switch (opt) {
    case 'O':
      printOutputProcHosts = true;
      break;

    case 'C':
      printCommandHost = true;
      break;

    default: /* '?' */
      usage(argv[0]);
      exit(1);
    }
  }

  // we expect a parset filename as an additional parameter
  if (optind >= argc) {
    usage(argv[0]);
    exit(1);
  }

  INIT_LOGGER("getCobaltHosts");

  // Open the parset
  Parset ps(argv[optind]);

  if (printOutputProcHosts) {
    // Get the list of stations and output to stdout space separated
    std::vector<string>::const_iterator host = ps.settings.outputProcHosts.begin();
    if (host != ps.settings.outputProcHosts.end()) {
      cout << *host;
      ++host;

      for ( ; host != ps.settings.outputProcHosts.end(); ++host) {
        cout << ' ' << *host;
      }
    }

    return 0;
  }

  if (printCommandHost) {
    // Print commanding host, that is, the one that will run on MPI rank 0.
    ASSERT(ps.settings.nodes.size() > 0);

    cout << ps.settings.nodes[0].hostName << endl;
    return 0;
  }

  // Nothing to do -- print usage and fail
  usage(argv[0]);
  return 1;
}
