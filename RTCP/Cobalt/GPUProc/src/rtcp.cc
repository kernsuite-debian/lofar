//# rtcp.cc: Real-Time Central Processor application, GPU cluster version
//# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <csignal>
#include <ctime>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <omp.h>

#include <string>
#include <vector>
#include <iostream>

#include <mpi.h>
#include <InputProc/Transpose/MPIUtil.h>

#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string/replace.hpp>

#include <Common/LofarLogger.h>
#include <Common/SystemUtil.h>
#include <Common/StringUtil.h>
#include <Common/Thread/Trigger.h>
#include <Common/Thread/Thread.h>
#include <MessageBus/MessageBus.h>
#include <MessageBus/ToBus.h>
#include <MessageBus/Util.h>
#include <MessageBus/Protocols/TaskFeedbackProcessing.h>
#include <ApplCommon/PVSSDatapointDefs.h>
#include <ApplCommon/StationInfo.h>
#include <MACIO/RTmetadata.h>
#include <CoInterface/Parset.h>
#include <CoInterface/LTAFeedback.h>
#include <CoInterface/OutputTypes.h>
#include <CoInterface/OMPThread.h>
#include <CoInterface/Pool.h>
#include <CoInterface/Stream.h>
#include <CoInterface/SelfDestructTimer.h>
#include <InputProc/SampleType.h>
#include <InputProc/Delays/Delays.h>
#include <InputProc/WallClockTime.h>
#include <InputProc/Buffer/StationID.h>

#include "global_defines.h"
#include "CommandThread.h"
#include <GPUProc/Station/StationInput.h>
#include <GPUProc/Station/StationNodeAllocation.h>
#include "Pipelines/Pipeline.h"
#include "Storage/StorageProcesses.h"

#include <CoInterface/cpu_utils.h>
#include <GPUProc/SysInfoLogger.h>
#include <GPUProc/Package__Version.h>
#include <GPUProc/MPIReceiver.h>

using namespace LOFAR;
using namespace LOFAR::Cobalt;
using namespace std;
using boost::format;

/* Tuning parameters */

// Number of seconds to schedule for the allocation of resources. That is,
// we start allocating resources at startTime - allocationTimeout.
const time_t defaultAllocationTimeout = 15;

// Deadline for outputProc, in seconds.
const time_t defaultOutputProcTimeout = 60;

// Amount of seconds to stay alive after Observation.stopTime
// has passed.
const time_t defaultRtcpTimeout = 5 * 60;

static void usage(const char *argv0)
{
  cout << "RTCP: Real-Time Central Processing of the LOFAR radio telescope." << endl;
  cout << "RTCP provides correlation for the Standard Imaging mode and" << endl;
  cout << "beam-forming for the Pulsar mode." << endl;
  cout << "GPUProc version " << GPUProcVersion::getVersion() << " r" << GPUProcVersion::getRevision() << endl;
  cout << endl;
  cout << "Usage: " << argv0 << " parset" << " [-p]" << endl;
  cout << endl;
  cout << "  -p: enable profiling" << endl;
  cout << "  -h: print this message" << endl;
}

void ignore_sigpipe()
{
  struct sigaction sa;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = 0;
  sa.sa_handler = SIG_IGN;
  if (sigaction(SIGPIPE, &sa, NULL) < 0)
    THROW_SYSCALL("sigaction(SIGPIPE, <SIG_IGN>)");
}

string GPUProc_PVSSPrefix(const Parset &ps, int cpuNr)
{
  const string hostName = myHostname(false);

  // For GPUProc use boost::format to fill in the two conv specifications (%xx).
  string fmtStr(createPropertySetName(PSN_COBALTGPU_PROC, "", ps.PVSS_TempObsName()));
  format prFmt;
  prFmt.exceptions(boost::io::no_error_bits); // avoid throw
  prFmt.parse(fmtStr);
  int cbmNodeNr = hostName.compare(0, sizeof("cbm") - 1, "cbm") == 0 ?
                  atoi(hostName.c_str() + sizeof("cbm") - 1) : 0; // default 0 like atoi()
  return str(prFmt % cbmNodeNr % cpuNr);
}

string InputProc_PVSSPrefix(const Parset &ps, const string &antennaFieldName) {
  // For InputProc use boost::format to fill in one conv specifications (%xx).
  string fmtStrInputProc(createPropertySetName(PSN_COBALT_STATION_INPUT,
                                               "", ps.PVSS_TempObsName()));
  format prFmtInputProc;
  prFmtInputProc.exceptions(boost::io::no_error_bits); // avoid throw
  prFmtInputProc.parse(fmtStrInputProc);
  return str(prFmtInputProc % antennaFieldName);
}

int main(int argc, char **argv)
{
  /*
   * Parse command-line options
   */

  int opt;
  while ((opt = getopt(argc, argv, "ph")) != -1) {
    switch (opt) {
    case 'p':
      profiling = true;
      break;

    case 'h':
      usage(argv[0]);
      return EXIT_SUCCESS;

    default: /* '?' */
      usage(argv[0]);
      return EXIT_FAILURE;
    }
  }

  // we expect a parset filename as an additional parameter
  if (optind >= argc) {
    usage(argv[0]);
    return EXIT_FAILURE;
  }

  /*
   * Initialise the system environment
   */

  // Ignore SIGPIPE, as we handle disconnects ourselves
  ignore_sigpipe();

  // Make sure all time is dealt with and reported in UTC
  if (setenv("TZ", "UTC", 1) < 0)
    THROW_SYSCALL("setenv(TZ)");

  LOFAR::Cobalt::MPI mpi;

  /*
   * Initialise logger.
   */

  // Use LOG_*() for c-strings (incl cppstr.c_str()), and LOG_*_STR() for std::string.
  INIT_LOGGER("rtcp");

  LOG_INFO_STR("GPUProc version " << GPUProcVersion::getVersion() << " r" << GPUProcVersion::getRevision());
  LOG_INFO_STR("MPI rank " << mpi.rank() << " out of " << mpi.size() << " hosts");

  LOG_INFO("===== INIT =====");

  // Initialise message bus
  LOG_INFO("----- Initialising MessageBus");
  MessageBus::init();

  // Create a parameters set object based on the inputs
  LOG_INFO("----- Reading Parset");
  Parset ps(argv[optind]);

  // Start running us and all our threads at real time. SCHED_FIFO means the tasks will
  // not be interrupted unless blocked by IO, queues, mutexes, etc. Also (SCHED_FIFO/SCHED_RR)
  // tasks with higher priority can interrupt.
  //
  // Threads get priority 5 by default, and thus cannot interrupt each other.
  // The vital threads (that deal with station input and polling MPI to make it progress) will get priority 10.
  //Thread::ScopedPriority sp(ps.settings.realTime ? SCHED_FIFO : SCHED_OTHER, 5);

  LOG_INFO("----- Determining NUMA bindings");

  // If we are testing we do not want dependency on hardware specific cpu configuration
  const bool do_numa_bind = mpi.rank() >= 0 && (size_t)mpi.rank() < ps.settings.nodes.size();
  struct ObservationSettings::Node mynode;
  if(do_numa_bind) {
    mynode = ps.settings.nodes.at(mpi.rank());
  } else {
    LOG_WARN_STR("Rank " << mpi.rank() << " not present in node list -- using full machine");
  }

  LOG_INFO("----- Register at LogProcessor");
  // Send id string to the MAC Log Processor as context for further LOGs.
  // Also use it for MAC/PVSS data point logging as a key name prefix.
  string mdKeyPrefix = GPUProc_PVSSPrefix(ps, do_numa_bind ? mynode.cpu : 0);
  LOG_INFO_STR("MACProcessScope: " << mdKeyPrefix);
  mdKeyPrefix.push_back('.'); // keys look like: "keyPrefix.subKeyName", some with a "[x]" appended.

  // Create mdLogger for monitoring (PVSS). We can already log(), but start() the event send thread
  // much later, after the pipeline creation (post-fork()), so we don't crash.
  LOG_INFO("----- Setting up transport to PVSS Gateway");
  const string hostName = myHostname(false);
  const string mdRegisterName = PST_COBALTGPU_PROC + boost::lexical_cast<string>(do_numa_bind ? mynode.cpu : 0) + ":" +
                                boost::lexical_cast<string>(ps.settings.observationID) + "@" + hostName;
  const string mdHostName = ps.getString("Cobalt.PVSSGateway.host", "");

  // Don't connect to PVSS for non-real-time observations -- they have no proper flow control
  MACIO::RTmetadata mdLogger(ps.settings.observationID, mdRegisterName, ps.settings.realTime ? mdHostName : "");

  /* Tuning parameters */

  // Number of seconds to schedule for the allocation of resources. That is,
  // we start allocating resources at startTime - allocationTimeout.
  const time_t allocationTimeout = 
    ps.ParameterSet::getTime("Cobalt.Tuning.allocationTimeout", 
			     defaultAllocationTimeout);

  // Deadline for outputProc, in seconds.
  const time_t outputProcTimeout = 
    ps.ParameterSet::getTime("Cobalt.Tuning.outputProcTimeout",
			     defaultOutputProcTimeout);

  // Amount of seconds to stay alive after Observation.stopTime
  // has passed.
  const time_t rtcpTimeout = 
    ps.ParameterSet::getTime("Cobalt.Tuning.rtcpTimeout",
			     defaultRtcpTimeout);

  LOG_DEBUG_STR(
    "Tuning parameters:" <<
    "\n  allocationTimeout    : " << allocationTimeout << "s" <<
    "\n  outputProcTimeout    : " << outputProcTimeout << "s" <<
    "\n  rtcpTimeout          : " << rtcpTimeout << "s");

  setSelfDestructTimer(ps, rtcpTimeout);

  /*
   * INIT stage
   */

  if (mpi.rank() == 0) {
    LOG_INFO_STR("nr stations    = " << ps.settings.antennaFields.size());
    LOG_INFO_STR("nr subbands    = " << ps.settings.subbands.size());
    LOG_INFO_STR("bitmode        = " << ps.nrBitsPerSample());
    LOG_INFO_STR("output cluster = " << ps.settings.outputCluster);
  }

  // Bind this process to our socket before any threads are created. This causes
  // the binding to propagate to child threads.
  LOG_INFO("----- Initialising NUMA CPU bindings");

  if(do_numa_bind) {
    if (mynode.cpu != -1) {
      // set the processor affinity before any threads are created
      bindCPU(mynode.cpu, mynode.avoidCores);
    } else {
      LOG_INFO("Cannot bind CPU: cpu nr to bind to is set to -1");
    }
  }

  LOG_INFO("----- Initialising NUMA MPI NIC bindings");

  if(do_numa_bind) {
    // Select on the local NUMA InfiniBand interface (OpenMPI only, for now)
    if (mynode.mpi_nic != "") {
      LOG_DEBUG_STR("Binding MPI to interface " << mynode.mpi_nic);
      mpi.bindNIC(mynode.mpi_nic);
    }
  }

  LOG_INFO("----- Initialising GPUs");

  gpu::Platform platform;
  LOG_INFO_STR("GPU platform " << platform.getName());
  vector<gpu::Device> allDevices(platform.devices());

  LOG_INFO("----- Initialising NUMA GPU bindings");

  // The set of GPUs we're allowed to use
  vector<gpu::Device> devices;

  if(do_numa_bind) {
    // derive the set of gpus we're allowed to use
    for (size_t i = 0; i < mynode.gpus.size(); ++i) {
      ASSERTSTR(mynode.gpus[i] < allDevices.size(), "Request to use GPU #" << mynode.gpus[i] << ", but found only " << allDevices.size() << " GPUs");

      gpu::Device &d = allDevices[mynode.gpus[i]];

      devices.push_back(d);
    }
  } else {
    devices = allDevices;
  }

  for (size_t i = 0; i < devices.size(); ++i)
    LOG_INFO_STR("Bound to GPU #" << i << ": " << devices[i].pciId() << " " << devices[i].getName() << ". Compute capability: " <<
                 devices[i].getComputeCapabilityMajor() << "." <<
                 devices[i].getComputeCapabilityMinor() <<
                 " global memory: " << (devices[i].getTotalGlobalMem() / 1024 / 1024) << " Mbyte");

  LOG_INFO("----- Initialising Pipeline");

  // Distribute the subbands over the MPI ranks
  SubbandDistribution subbandDistribution; // rank -> [subbands]

  for( size_t subband = 0; subband < ps.settings.subbands.size(); ++subband) {
    int receiverRank = subband % mpi.size();

    subbandDistribution[receiverRank].push_back(subband);
  }

  Pool<struct MPIRecvData> MPI_receive_pool("rtcp::MPI_receive_pool", ps.settings.realTime);

  const std::vector<size_t> subbandIndices(subbandDistribution[mpi.rank()]);

  MPIReceiver MPI_receiver(MPI_receive_pool,
                           subbandIndices,
      std::find(subbandIndices.begin(), subbandIndices.end(), 0U) != subbandIndices.end(),
                           ps.settings.blockSize,
                           ps.settings.antennaFields.size(),
                           ps.nrBitsPerSample());
      
  SmartPtr<Pipeline> pipeline;

  // Creation of pipelines cause fork/exec, which we need to
  // do before we start doing anything fancy with libraries and threads.
  if ((ps.settings.correlator.enabled || ps.settings.beamFormer.enabled) &&
      !subbandIndices.empty()) {
    pipeline = new Pipeline(ps, subbandIndices, devices,
                            MPI_receive_pool, mdLogger, mdKeyPrefix, mpi.rank());
  } else {
    // RSP raw data output or piggy-backing only, or software test without pipeline
    pipeline = NULL;
  } 

  // After pipeline creation (post-fork()), allow creation of a thread to send
  // data points for monitoring (PVSS).
  //mdLogger.start();

  // Only ONE host should start the Storage processes
  SmartPtr<StorageProcesses> storageProcesses;

  if (mpi.rank() == 0) {
    LOG_INFO("----- Starting OutputProc");

    // NOTE: This fork()s.
    storageProcesses = new StorageProcesses(ps, "");
  }

  /*
   * Initialise MPI (we are done forking)
   */
  LOG_INFO("----- Calling MPI_Init_thread");
  mpi.init(argc, argv);

  LOG_INFO("----- Initialising OpenMP");

  // Allow usage of nested omp calls
  omp_set_nested(true);

  // Allow OpenMP thread registration
  OMPThread::init(); // Call AFTER MPI_Init, since this sets a signal handler which MPI_Init would override
  OMPThread::ScopedName sn("main");

  // Migrate all moveable and future memory to our socket.
  //
  // NOTE: This restricts the freedom for memory allocations to our socket.
  //       MPI_Init still wants this freedom, so we do this after.
  LOG_INFO("----- Initialising NUMA memory bindings");

  if(do_numa_bind) {
    if (mynode.cpu != -1) {
      bindMemory(mynode.cpu);
    } else {
      LOG_INFO("Cannot bind memory: cpu nr to bind to is set to -1");
    }
  }

  // Bindings are done -- Lock everything in memory (prevents swapping)
  try {
    unlimitedLockedMemory();
    lockAllMemory();
  } catch(SystemCallException &ex) {
    if (ps.settings.realTime) throw;
    LOG_WARN_STR("Cannot lock all memory: " << ex.what());
  }

  // IERS table information
  struct Delays::IERS_tablestats stats = Delays::get_IERS_tablestats();

  LOG_INFO_STR("Using IERS table " << stats.realpath
            << ", last entry is " << TimeDouble::toString(stats.last_entry_timestamp, false)
            << ", table written on " << TimeDouble::toString(stats.last_fs_modification, false));

  /*
   * RUN stage
   */

  // Periodically log system information
  SysInfoLogger siLogger(ps.settings.startTime, ps.settings.stopTime);

  LOG_INFO("===== LAUNCH =====");

  LOG_INFO_STR("Processing subbands " << subbandDistribution[mpi.rank()]);

  Trigger stopSwitch;
  SmartPtr<CommandThread> commandThread;

  #pragma omp parallel sections num_threads(2)
  {
    #pragma omp section
    {
      /*
       * COMMAND THREAD
       */

      // The CommandThread is used on rank 0 to receive commands while
      // running, typically through a pipe.
      //
      // NOTE: rank 0 is the first node in the run, NOT (necessarily) the node running mpirun
      //
      // It receives the early abort command ("stop") as its primary function,
      // in which case we gracefully shut down.
      //
      // Note that the CommandThread is needed to notify rtcp, as MPI cannot be
      // relied on to:
      //   * Propagate signals sent to mpirun to us (OpenMPI won't at all)
      //   * Propagate stdin reliably from mpirun to us:
      //       * Many processes started before mpirun read from stdin, spoiling or blocking our channel
      //       * (Open)MPI won't reopen stdin after it is closed by the first client to send commands

      OMPThread::ScopedName sn("CommandThr bcast");

      if (mpi.rank() == 0) {
        commandThread = new CommandThread(ps.settings.commandStream);
      }

      string command;

      do {
        // rank 0 obtains next command
        command = mpi.rank() == 0 ? commandThread->pop() : "";

        // sync command across nodes
        command = CommandThread::broadcast(command);

        // handle command
        if (command == "stop") {
          stopSwitch.trigger();
        }
      } while (command != "");

      LOG_DEBUG("[CommandThread] Done");
    }

    #pragma omp section
    {
      /*
       * THE OBSERVATION
       */

      OMPThread::ScopedName sn("observation");

      if (ps.settings.realTime) {
        // Wait just before the obs starts to allocate resources,
        // both the UDP sockets and the GPU buffers!
        LOG_INFO_STR("Waiting to start obs running from " << TimeStamp::convert(ps.settings.startTime, ps.settings.clockHz()) << " to " << TimeStamp::convert(ps.settings.stopTime, ps.settings.clockHz()));

        const time_t deadline = floor(ps.settings.startTime) - allocationTimeout;
        WallClockTime waiter;
        waiter.waitUntil(deadline);
      }

      #pragma omp parallel sections num_threads(3)
      {
        #pragma omp section
        {
          OMPThread::ScopedName sn("stations");

          // Construct list of stations to receive with this process
          struct receivingAntennaField {
            size_t idx;
            struct StationID id;
          };

          vector<struct receivingAntennaField> receivingAntennaFields;

          for (size_t stat = 0; stat < ps.settings.antennaFields.size(); ++stat) 
          {       
            const struct StationID stationID(
              StationID::parseFullFieldName(
              ps.settings.antennaFields.at(stat).name));
            const StationNodeAllocation allocation(stationID, ps, mpi.rank(), mpi.size());

            if (allocation.receivedHere()) 
            {
              struct receivingAntennaField r;

              r.idx = stat;
              r.id = stationID;
              receivingAntennaFields.push_back(r);
            }
          }

          // Read and forward station data over MPI
          #pragma omp parallel for num_threads(receivingAntennaFields.size())
          for (size_t i = 0; i < receivingAntennaFields.size(); i++) 
          {
            const struct receivingAntennaField &r = receivingAntennaFields[i];
            OMPThread::ScopedName sn(str(format("%s main") % r.id.name()));

            // For InputProc use the GPUProc mdLogger (same process), but our own key prefix.
            // Since InputProc is inside GPUProc, don't inform the MAC Log Processor.
            string mdKeyPrefixInputProc = InputProc_PVSSPrefix(ps, r.id.name());
            mdKeyPrefixInputProc.push_back('.'); // keys look like: "keyPrefix.subKeyName"

            mdLogger.log(mdKeyPrefixInputProc + PN_CSI_OBSERVATION_NAME,
                         boost::lexical_cast<string>(ps.settings.observationID));
            mdLogger.log(mdKeyPrefixInputProc + PN_CSI_NODE, hostName);
            mdLogger.log(mdKeyPrefixInputProc + PN_CSI_CPU,  do_numa_bind ? mynode.cpu : 0);


            sendInputToPipeline(ps, r.idx, subbandDistribution, mpi.rank(),
                                mdLogger, mdKeyPrefixInputProc, &stopSwitch);
          }
        }

        // receive data over MPI and insert into pool
        #pragma omp section
        {
          OMPThread::ScopedName sn("mpi recv");

          MPI_receiver.receiveInput();
        }

        // Retrieve items from pool and process further on
        #pragma omp section
        {
          OMPThread::ScopedName sn("obs process");

          // Process station data if needed and if any
          if ((ps.settings.correlator.enabled || ps.settings.beamFormer.enabled) &&
              !subbandDistribution[mpi.rank()].empty()) {
            pipeline->processObservation();
          }
        }
      }

      if (mpi.rank() == 0) {
        LOG_DEBUG_STR("Stopping CommandThread");
        commandThread->stop();
      }
    }
  }

  // Delete pipeline to release resources before next obs tries to allocate.
  // COMPLETING stage can take a while. (Better use proper functions & scopes.)
  pipeline = NULL;

  /*
   * Whether we've encountered an error; observation will
   * be set to ABORTED by OnlineControl if so.
   */
  int exitStatus = EXIT_SUCCESS;

  /*
   * COMPLETING stage
   */
  LOG_INFO("===== FINALISE =====");

  if (storageProcesses) {
    LOG_INFO("----- Processing final metadata (broken antenna information)");

    // retrieve and forward final meta data
    if (!storageProcesses->forwardFinalMetaData()) {
      LOG_ERROR("Forwarding final metadata failed");
      exitStatus = EXIT_FAILURE;
    }

    LOG_INFO("Stopping Storage processes");

    // graceful exit
    storageProcesses->stop(time(0) + outputProcTimeout);

    // send processing feedback
    ToBus bus("otdb.task.feedback.processing", broker_feedback());

    LTAFeedback fb(ps.settings);

    Protocols::TaskFeedbackProcessing msg(
      "Cobalt/GPUProc/rtcp",
      "",
      "Processing feedback",
      str(format("%s") % ps.settings.momID),
      str(format("%s") % ps.settings.observationID),
      fb.processingFeedback());

    bus.send(msg);

    // final cleanup
    storageProcesses = NULL;
  }

  LOG_INFO_STR("===== EXITING WITH STATUS " << exitStatus << " =====");
  return exitStatus;
}

