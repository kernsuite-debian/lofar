//# outputProc.cc
//# Copyright (C) 2008-2015  ASTRON (Netherlands Institute for Radio Astronomy)
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

//# Always #include <lofar_config.h> first!
#include <lofar_config.h>

#include <cstdio> // for setvbuf
#include <unistd.h>
#include <omp.h>
#include <time.h>
#include <string>
#include <stdexcept>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <Common/LofarLogger.h>
#include <Common/CasaLogSink.h>
#include <Common/Exceptions.h>
#include <Common/NewHandler.h>
#include <Stream/PortBroker.h>
#include <CoInterface/Exceptions.h>
#include <CoInterface/Parset.h>
#include <CoInterface/Stream.h>
#include <CoInterface/OMPThread.h>
#include <OutputProc/Package__Version.h>
#include <MessageBus/MessageBus.h>
#include "GPUProcIO.h"

#define STDLOG_BUFFER_SIZE     1024

using namespace LOFAR;
using namespace LOFAR::Cobalt;
using namespace std;
using boost::format;

// install a new handler to produce backtraces for bad_alloc
LOFAR::NewHandler h(LOFAR::BadAllocException::newHandler);

// Use a terminate handler that can produce a backtrace.
Exception::TerminateHandler t(Exception::terminate);

static char stdoutbuf[STDLOG_BUFFER_SIZE];
static char stderrbuf[STDLOG_BUFFER_SIZE];

static void usage(const char *argv0)
{
  cout << "OutputProc: Data writer for the Real-Time Central Processing of the" << endl;
  cout << "LOFAR radio telescope." << endl;
  cout << "OutputProc provides CASA Measurement Set files with correlated data" << endl;
  cout << "for the Standard Imaging mode and HDF5 files with beamformed data" << endl;
  cout << "for the Pulsar mode." << endl; 
  cout << "OutputProc version " << OutputProcVersion::getVersion() << " r" << OutputProcVersion::getRevision() << endl;
  cout << endl;
  cout << "Usage: " << argv0 << " ObservationID mpi_rank" << endl;
  cout << endl;
  cout << "  -h: print this message" << endl;
}

int main(int argc, char *argv[])
{
  setvbuf(stdout, stdoutbuf, _IOLBF, sizeof stdoutbuf);
  setvbuf(stderr, stderrbuf, _IOLBF, sizeof stderrbuf);

  int opt;
  while ((opt = getopt(argc, argv, "h")) != -1) {
    switch (opt) {
    case 'h':
      usage(argv[0]);
      return EXIT_SUCCESS;

    default: /* '?' */
      usage(argv[0]);
      return EXIT_FAILURE;
    }
  }

  if (argc != 3 && argc != 2) {
    usage(argv[0]);
    return EXIT_FAILURE;
  }

  int observationID = boost::lexical_cast<int>(argv[1]);

  // Ignore SIGPIPE, as we handle disconnects ourselves
  struct sigaction sa;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = SIG_IGN;
  if (sigaction(SIGPIPE, &sa, NULL) < 0)
    THROW_SYSCALL("sigaction(SIGPIPE, <SIG_IGN>)");

  // Make sure all time is dealt with and reported in UTC
  if (setenv("TZ", "UTC", 1) < 0)
    THROW_SYSCALL("setenv(TZ)");

  INIT_LOGGER("outputProc"); // also attaches to CasaLogSink

  LOG_DEBUG_STR("Started: " << argv[0] << ' ' << argv[1] << ' ' << argv[2]);
  LOG_INFO_STR("OutputProc version " << OutputProcVersion::getVersion() << " r" << OutputProcVersion::getRevision());

  MessageBus::init();

  omp_set_nested(true);

  OMPThread::init();

  // Prevent stalling in the PortBroker or the resulting connection from COBALT
  alarm(3600);

  PortBroker::createInstance(storageBrokerPort(observationID));

  // retrieve control stream to receive the parset and report back
  string resource = getStorageControlDescription(observationID);
  PortBroker::ServerStream controlStream(resource);

  if (process(controlStream)) {
    LOG_INFO("Program terminated succesfully");
    return EXIT_SUCCESS;
  } else {
    LOG_ERROR("Program terminated with errors");
    return EXIT_FAILURE;
  }
}

