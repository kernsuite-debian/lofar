//# GPUProcIO.cc: Routines for communicating with GPUProc
//# Copyright (C) 2008-2014, 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
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

#include "GPUProcIO.h"

#include <cstring>
#include <vector>
#include <time.h>    // for time()
#include <unistd.h>  // for alarm()
#include <omp.h>
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#include <Common/LofarLogger.h>
#include <Common/StringUtil.h>
#include <Common/SystemUtil.h>
#include <Common/Exceptions.h>
#include <Common/IOPriority.h>
#include <MessageBus/ToBus.h>
#include <MessageBus/Util.h>
#include <MessageBus/Protocols/TaskFeedbackDataproducts.h>
#include <Stream/PortBroker.h>
#include <Stream/NetFuncs.h>
#include <ApplCommon/PVSSDatapointDefs.h>
#include <ApplCommon/StationInfo.h>
#include <MACIO/RTmetadata.h>
#include <CoInterface/Exceptions.h>
#include <CoInterface/OMPThread.h>
#include <CoInterface/Parset.h>
#include <CoInterface/FinalMetaData.h>
#include <CoInterface/Stream.h>
#include <CoInterface/SmartPtr.h>
#include <CoInterface/SelfDestructTimer.h>
#include "SubbandWriter.h"
#include "RSPRawWriter.h"
#include "OutputThread.h"

using namespace LOFAR;
using namespace LOFAR::Cobalt;
using namespace std;
using boost::format;
using boost::lexical_cast;

namespace LOFAR {
  namespace Cobalt {

// Deadline for the wrap up after the obs end, in seconds.
const time_t defaultOutputProcTimeout = 300;

size_t getMaxRunTime(const Parset &parset)
{
  if (!parset.settings.realTime)
    return 0;

  // Deadline for outputProc, in seconds.
  const time_t outputProcTimeout = 
    parset.ParameterSet::getTime("Cobalt.Tuning.outputProcTimeout",
           defaultOutputProcTimeout);

  const time_t now = time(0);
  const double stopTime = parset.settings.stopTime;

  if (now < stopTime + outputProcTimeout)
    return stopTime + outputProcTimeout - now;
  else
    return 0;
}

bool process(Stream &controlStream)
{
  bool success(true);

  Parset parset(&controlStream);

  string myHostName = myHostname(false);
  // Get all my hostnames to see which output files are my responsibility.
  set<string> myHostNames = myInterfaces(true, false, -1); // includes IPv4, IPv6 loopback name(s)
  myHostNames.insert(myHostname(true)); // might be different (e.g. on cbt nodes)
  set<string> myShortHostNames; // to avoid changing myHostNames while iterating
  string hostNameConcat;
  for (set<string>::iterator it = myHostNames.begin(); it != myHostNames.end(); ++it) {
    size_t pos = it->find('.');
    if (pos != string::npos) {
      string shortName = it->substr(0, pos);
      myShortHostNames.insert(shortName);

      hostNameConcat += shortName;
      hostNameConcat += ' ';
    }

    hostNameConcat += *it;
    hostNameConcat += ' ';
  }
  myHostNames.insert(myShortHostNames.begin(), myShortHostNames.end());
  LOG_INFO_STR("Expecting and writing data for data products for hostnames: " << hostNameConcat);

  setIOpriority(false); // first elevate to highest possible without need for special privileges
  if (parset.settings.realTime) {
    /*
     * Real-time observation
     */

    // Acquire elevated IO and CPU priorities
    setIOpriority(true); // reqs CAP_SYS_ADMIN iff passing realTime is true
    setRTpriority();

    // Prevent swapping of our buffers
    //lockInMemory(16UL * 1024UL * 1024UL * 1024UL); // limit memory to 16 GB

    // Deadline for outputProc, in seconds.
    const time_t outputProcTimeout = 
      parset.ParameterSet::getTime("Cobalt.Tuning.outputProcTimeout",
             defaultOutputProcTimeout);

    setSelfDestructTimer(parset, outputProcTimeout);
  } else {
    // Kill any existing alarms
    alarm(0);
  }

  // Send id string to the MAC Log Processor as context for further LOGs.
  // Also use it for MAC/PVSS data point logging as a key name prefix.
  // For outputProc there are no conv specifications (%xx) to be filled in.
  string mdKeyPrefix(createPropertySetName(PSN_COBALT_OUTPUT_PROC, "", parset.PVSS_TempObsName()));
  LOG_INFO_STR("MACProcessScope: " << mdKeyPrefix);
  mdKeyPrefix.push_back('.'); // keys look like: "keyPrefix.subKeyName[x]"

  const string mdRegisterName = string(PST_COBALT_OUTPUT_PROC) + ":" +
                                lexical_cast<string>(parset.settings.observationID) + "@" + myHostName;
  const string mdHostName = parset.getString("Cobalt.PVSSGateway.host", "");
  MACIO::RTmetadata mdLogger(parset.settings.observationID, mdRegisterName, mdHostName);
  mdLogger.start();

  {
    // make sure "parset" and "mdLogger" stay in scope for the lifetime of the SubbandWriters

    vector<SmartPtr<SubbandWriter> > subbandWriters;
    vector<SmartPtr<TABOutputThread> > tabWriters;
    vector<SmartPtr<RSPRawWriter> > rspRawWriters;

    /*
     * Construct writers
     */

    // Process correlated data
    if (parset.settings.correlator.enabled) {
      for (size_t fileIdx = 0; fileIdx < parset.settings.correlator.files.size(); ++fileIdx)
      {
        struct ObservationSettings::Correlator::File &file = parset.settings.correlator.files[fileIdx];

        if (myHostNames.find(file.location.host) == myHostNames.end()) {
          continue;
        }

        LOG_DEBUG_STR("starting with fileIdx " << fileIdx);

        mdLogger.log(mdKeyPrefix + PN_COP_STORAGE_HOST + '[' + lexical_cast<string>(fileIdx) + ']', myHostName);

        string logPrefix = str(format("[stream %3u file %s] ")
                               % fileIdx % file.location.filename);

        SubbandWriter *writer = new SubbandWriter(parset, fileIdx, mdLogger, mdKeyPrefix, logPrefix);
        subbandWriters.push_back(writer);

        LOG_DEBUG_STR("done with fileIdx " << fileIdx);
      }
    }

    map<size_t, SmartPtr<Arena> > arenas;
    map<size_t, SmartPtr<Allocator> > allocators;
    map<size_t, SmartPtr<Pool<TABTranspose::BeamformedData> > > outputPools;
    TABTranspose::Receiver::CollectorMap collectors;

    // Process beam-formed data
    if (parset.settings.beamFormer.enabled) {
      for (size_t fileIdx = 0; fileIdx < parset.settings.beamFormer.files.size(); ++fileIdx)
      {
        struct ObservationSettings::BeamFormer::File &file = parset.settings.beamFormer.files[fileIdx];

        if (myHostNames.find(file.location.host) == myHostNames.end()) {
          continue;
        }

        const unsigned allFileIdx = fileIdx + (parset.settings.correlator.enabled ? parset.settings.correlator.files.size() : 0);
        mdLogger.log(mdKeyPrefix + PN_COP_STORAGE_HOST + '[' + lexical_cast<string>(allFileIdx) + ']', myHostName);

        LOG_DEBUG_STR("Allocating transpose buffers for " << file.location.filename);

        struct ObservationSettings::BeamFormer::StokesSettings &stokes =
          file.coherent ? parset.settings.beamFormer.coherentSettings
                        : parset.settings.beamFormer.incoherentSettings;

        const size_t nrSubbands = file.lastSubbandIdx - file.firstSubbandIdx;
        const size_t nrChannels = stokes.nrChannels;
        const size_t nrSamples = stokes.nrSamples;
        const size_t alignment = TABTranspose::BeamformedData::alignment;

        // poolSize is the buffer size (in #blocks) for the queue to disk
        const size_t poolSize = 60;

        arenas[fileIdx] = new MallocedArena(poolSize * (MultiDimArray<float,3>::nrElements(boost::extents[nrSamples][nrSubbands][nrChannels]) * sizeof(float) + alignment), alignment);
        allocators[fileIdx] = new SparseSetAllocator(*arenas[fileIdx]);
        outputPools[fileIdx] = new Pool<TABTranspose::BeamformedData>(str(format("process::outputPool [stream %u]") % fileIdx), parset.settings.realTime);

        // Create and fill an outputPool for this fileIdx
        for (size_t i = 0; i < poolSize; ++i)
	      outputPools[fileIdx]->free.append(new TABTranspose::BeamformedData(nrSubbands, nrChannels, nrSamples, *allocators[fileIdx]), false);

        string logPrefix = str(format("[stream %3u file %s] ")
                                                    % fileIdx % file.location.filename);

        // Create a collector for this fileIdx
        // #blocks here is the number of blocks that can be collected in parallel on
        // the input side (what the correlator sends)
        collectors[fileIdx] = new TABTranspose::BlockCollector(
          *outputPools[fileIdx], fileIdx, nrSubbands, nrChannels, nrSamples, parset.settings.nrBlocks(), parset.settings.realTime ? 5 : 0, logPrefix, parset.settings.blockDuration());

        LOG_DEBUG_STR("Setting up writer for " << file.location.filename);

        TABOutputThread *writer = new TABOutputThread(parset, fileIdx, *outputPools[fileIdx], mdLogger, mdKeyPrefix, logPrefix);
        tabWriters.push_back(writer);
      }
    }

    if (parset.settings.rspRaw.enabled) {
      for (size_t fileIdx = 0; fileIdx < parset.settings.rspRaw.files.size(); ++fileIdx)
      {
        struct ObservationSettings::RSPRaw::File &file = parset.settings.rspRaw.files[fileIdx];

        if (myHostNames.find(file.location.host) == myHostNames.end()) {
          continue;
        }

        LOG_INFO_STR("starting with RSP raw fileIdx " << fileIdx);

        // The rest of the system doesn't know about RSP raw data output, but if monitoring did, enable this:
        /*
        const unsigned allFileIdx = fileIdx + (parset.settings.correlator.enabled ? parset.settings.correlator.files.size() : 0) +
                                              (parset.settings.beamFormer.enabled ? parset.settings.beamFormer.files.size() : 0);
        mdLogger.log(mdKeyPrefix + PN_COP_STORAGE_HOST + '[' + lexical_cast<string>(allFileIdx) + ']', myHostName);
        */

        string logPrefix = str(format("[obs %u RSP raw stream %3u] ")
                               % parset.settings.observationID % fileIdx);

        RSPRawWriter *writer = new RSPRawWriter(parset, fileIdx, mdLogger, mdKeyPrefix, logPrefix);
        rspRawWriters.push_back(writer);

        LOG_INFO_STR("done with RSP raw fileIdx " << fileIdx);
      }
    }

    LOG_INFO_STR("Finished setting up writers");

    /*
     * PROCESS
     */

    FinalMetaData finalMetaData;

    // Set up receiver engine for 2nd transpose
    TABTranspose::MultiReceiver mr("2nd-transpose-", collectors);


#   pragma omp parallel sections num_threads(4)
    {
      // Done signal from controller, by sending the final meta data
#     pragma omp section
      {
        OMPThread::ScopedName sn("finalMetaData");

        // Add final meta data (broken tile information, etc)
        // that is obtained after the end of an observation.
        LOG_INFO_STR("Waiting for final meta data");

        try {
          finalMetaData.read(controlStream);
        } catch (LOFAR::Exception &err) {
          success = false;
          LOG_ERROR_STR("Failed to read broken tile information: " << err);
        }

        if (parset.settings.realTime) {
          // Real-time observations: stop now. MultiReceiver::kill
          // will stop the TABWriters.
          mr.kill(0);
        } else {
          // Non-real-time observations: wait until all data has been
          // processed. The TABWriters will stop once they received
          // the last block.
        }

        // SubbandWriters finish on their own once their InputThread
        // gets disconnected.
      }

      // SubbandWriters
#     pragma omp section
      {
        OMPThread::ScopedName sn("subbandWr");

#       pragma omp parallel for num_threads(subbandWriters.size())
        for (int i = 0; i < (int)subbandWriters.size(); ++i) {
          OMPThread::ScopedName sn(str(format("subbandWr %u") % subbandWriters[i]->streamNr()));

          subbandWriters[i]->process();
        }
      }

      // TABWriters
#     pragma omp section
      {
        OMPThread::ScopedName sn("tabWr");

#       pragma omp parallel for num_threads(tabWriters.size())       
        for (int i = 0; i < (int)tabWriters.size(); ++i) {
          OMPThread::ScopedName sn(str(format("tabWr %u") % tabWriters[i]->streamNr()));
          tabWriters[i]->process();
        }
      }

      // RSPRawWriters
#     pragma omp section
      {
        OMPThread::ScopedName sn("rspRawWr");

#       pragma omp parallel for num_threads(rspRawWriters.size())
        for (int i = 0; i < (int)rspRawWriters.size(); ++i) {
          OMPThread::ScopedName sn(str(format("rspRawWr %u") % rspRawWriters[i]->streamNr()));
          rspRawWriters[i]->process();
        }
      }
    }

    /*
     * FINAL META DATA
     */

    // Add final meta data (broken tile information, etc)
    // that is obtained after the end of an observation.
    LOG_DEBUG_STR("Processing final meta data");

    for (size_t i = 0; i < subbandWriters.size(); ++i)
      subbandWriters[i]->fini(finalMetaData);
    for (size_t i = 0; i < tabWriters.size(); ++i)
      tabWriters[i]->fini(finalMetaData);

    /*
     * LTA FEEDBACK
     */

    LOG_DEBUG_STR("Forwarding LTA feedback");

    ToBus bus("otdb.task.feedback.dataproducts", broker_feedback());

    const std::string myName = str(boost::format("Cobalt/OutputProc on %s") % myHostName);

    for (size_t i = 0; i < subbandWriters.size(); ++i) {
      Protocols::TaskFeedbackDataproducts msg(
        myName,
        "",
        str(boost::format("Feedback for Correlated Data, subband %s") % subbandWriters[i]->streamNr()),
        str(format("%s") % parset.settings.momID),
        str(format("%s") % parset.settings.observationID),
        subbandWriters[i]->feedbackLTA());

      bus.send(msg);
    }

    for (size_t i = 0; i < tabWriters.size(); ++i) {
      Protocols::TaskFeedbackDataproducts msg(
        myName,
        "",
        str(boost::format("Feedback for Beamformed Data, file nr %s") % tabWriters[i]->streamNr()),
        str(format("%s") % parset.settings.momID),
        str(format("%s") % parset.settings.observationID),
        tabWriters[i]->feedbackLTA());

      bus.send(msg);
    }

    // The rest of the system doesn't know about RSP raw data output, but if feedback did, enable this:
    /*
    for (size_t i = 0; i < rspRawWriters.size(); ++i) {
      Protocols::TaskFeedbackDataproducts msg(
        myName,
        "",
        str(boost::format("Feedback for RSP Raw Data, file nr %s") % rspRawWriters[i]->streamNr()),
        str(format("%s") % parset.settings.momID),
        str(format("%s") % parset.settings.observationID),
        rspRawWriters[i]->feedbackLTA());

      bus.send(msg);
    }
    */

    /*
     * SIGN OFF
     */

    bool sentFeedback = true;

    controlStream.write(&sentFeedback, sizeof sentFeedback);
    controlStream.write(&success, sizeof success);

    return success;
  }
}

  } // namespace Cobalt
} // namespace LOFAR

