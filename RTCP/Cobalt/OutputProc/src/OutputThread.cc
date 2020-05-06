//# OutputThread.cc:
//# Copyright (C) 2009-2013, 2017
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

#include "OutputThread.h"

#include <unistd.h>
#include <set>
#include <sstream>
#include <iomanip>
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#include <Common/SystemCallException.h>
#include <Common/Thread/Mutex.h>
#include <Common/Thread/Cancellation.h>
#include <Common/StreamUtil.h> // LOFAR::print()
#include <ApplCommon/PVSSDatapointDefs.h>

#include <CoInterface/OutputTypes.h>
#include <CoInterface/Exceptions.h>
#include <CoInterface/LTAFeedback.h>
#include <CoInterface/BudgetTimer.h>

#if defined HAVE_AIPSPP
#include <casacore/casa/Exceptions/Error.h>
#endif

#include "MSWriterFile.h"
#include "MSWriterCorrelated.h"
#include "MSWriterDAL.h"
#include "MSWriterNull.h"

namespace LOFAR
{
  namespace Cobalt
  {

    static Mutex casacoreMutex;

    using namespace std;
    using boost::lexical_cast;

    template<typename T> OutputThread<T>::OutputThread(const Parset &parset,
          unsigned streamNr, Pool<T> &outputPool,
          RTmetadata &mdLogger, const std::string &mdKeyPrefix,
          const std::string &logPrefix, const std::string &targetDirectory)
      :
      itsParset(parset),
      itsStreamNr(streamNr),
      itsMdLogger(mdLogger),
      itsMdKeyPrefix(mdKeyPrefix),
      itsLogPrefix(logPrefix),
      itsTargetDirectory(targetDirectory),
      itsBlocksWritten(0),
      itsBlocksDropped(0),
      itsBlocksDroppedByMe(0),
      itsFractionalBlocksWritten(0.0),
      itsNrExpectedBlocks(0),
      itsNextSequenceNumber(0),
      itsBlockDuration(parset.settings.blockDuration()),
      itsOutputPool(outputPool)
    {
    }


    template<typename T> OutputThread<T>::~OutputThread()
    {
    }


    template<typename T> void OutputThread<T>::checkForDroppedData(StreamableData *data)
    {
      // TODO: check for dropped data at end of observation

      ASSERTSTR(data->sequenceNumber() >= itsNextSequenceNumber, "Received block nr " << data->sequenceNumber() << " out of order! I expected nothing before " << itsNextSequenceNumber);

      size_t droppedBlocks = data->sequenceNumber() - itsNextSequenceNumber;

      const string streamNrStr = '[' + lexical_cast<string>(itsStreamNr) + ']';

      if (droppedBlocks > 0) {
        itsBlocksDropped += droppedBlocks;

        LOG_WARN_STR(itsLogPrefix << "Did not receive " << droppedBlocks << " blocks");

        itsMdLogger.log(itsMdKeyPrefix + PN_COP_DROPPED + streamNrStr,
                        itsBlocksDropped * static_cast<float>(itsBlockDuration));
      }

      if (data->doReadWithSequenceNumber()) {
        itsNextSequenceNumber = data->sequenceNumber() + 1;
      } // else, droppedBlocks is useless, but itsBlocksWritten is valid
      itsBlocksWritten++;
      itsFractionalBlocksWritten += 1.0 - data->outputLossFraction(); // doubles have enough precision for this to go well

      itsMdLogger.log(itsMdKeyPrefix + PN_COP_DROPPING + streamNrStr,
                      droppedBlocks > 0); // logged too late if dropping: not anymore...
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_WRITTEN  + streamNrStr,
                      itsBlocksWritten * static_cast<float>(itsBlockDuration));
    }


    template<typename T> void OutputThread<T>::doWork()
    {
      BudgetTimer writeTimer(
        "writeOutput",
        itsBlockDuration,
        true, true);

      for (SmartPtr<T> data; (data = itsOutputPool.filled.remove()) != 0; itsOutputPool.free.append(data)) {
        if (itsParset.settings.realTime) {
          try {
            BudgetTimer::StartStop ss(writeTimer);

            if (itsParset.settings.writeToDisk)
              itsWriter->write(data);
          } catch (SystemCallException &ex) {
            LOG_WARN_STR(itsLogPrefix << "OutputThread caught non-fatal exception: " << ex.what());
            itsBlocksDroppedByMe++;
            continue;
          }
        } else { // no try/catch: any loss (e.g. disk full) is fatal in non-real-time mode
          itsWriter->write(data);
        }

        checkForDroppedData(data);

        // print debug info for the other blocks
        LOG_DEBUG_STR(itsLogPrefix << "Written block with seqno = " << data->sequenceNumber() << "(which was " << (100.0 - 100.0 * data->outputLossFraction()) << "% complete), " << itsBlocksWritten << " blocks written, " << itsBlocksDropped << " blocks not received");
      }
    }


    template<typename T>
    void OutputThread<T>::logInitialStreamMetadataEvents(const string& dataProductType,
                                                         const string& fileName,
                                                         const string& directoryName)
    {
      // Write data points wrt @dataProductType output file for monitoring (PVSS).
      const string streamNrStr = '[' + lexical_cast<string>(itsStreamNr) + ']';

      itsMdLogger.log(itsMdKeyPrefix + PN_COP_DATA_PRODUCT_TYPE + streamNrStr, dataProductType);
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_FILE_NAME         + streamNrStr, fileName);
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_DIRECTORY         + streamNrStr, directoryName);

      // After obs start these dynarray data points are written conditionally, so init.
      // While we only have to write the last index (PVSSGateway will zero the rest),
      // we'd have to find out who has the last subband. Don't bother, just init all.
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_DROPPING + streamNrStr, 0);
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_WRITTEN  + streamNrStr, 0.0f);
      itsMdLogger.log(itsMdKeyPrefix + PN_COP_DROPPED  + streamNrStr, 0.0f);
    }


    template<typename T> void OutputThread<T>::cleanUp() const
    {
      // report statistics
      const float lostPerc = 100.0 * itsBlocksDroppedByMe / itsNrExpectedBlocks;
      const float didNotSendPerc = itsNrExpectedBlocks == 0 ? 0.0 : 100.0 - 100.0 * itsFractionalBlocksWritten / itsNrExpectedBlocks;
      const float didNotReceivePerc = didNotSendPerc + lostPerc;

      if (didNotReceivePerc > 0)
        LOG_WARN_STR(itsLogPrefix << "Did not receive " << didNotReceivePerc << "% of the data");
      if (lostPerc > 0)
        LOG_ERROR_STR(itsLogPrefix << "I lost " << lostPerc << "% of the data");
      if (didNotSendPerc > 0)
        LOG_WARN_STR(itsLogPrefix << "Did not send " << didNotSendPerc << "% of the data");

      LOG_INFO_STR(itsLogPrefix << "Finished writing " << itsBlocksWritten << " blocks, dropped " << itsBlocksDropped << " blocks.");

      if (didNotSendPerc > 0)
        LOG_ERROR_STR(itsLogPrefix << "Total output data loss is " << didNotSendPerc << "%.");
      else
        LOG_INFO_STR(itsLogPrefix << "Total output data loss is " << didNotSendPerc << "%.");
    }


    template<typename T> void OutputThread<T>::init()
    {
      try {
        ASSERT(itsWriter.get());

        itsWriter->init();
      } catch (Exception &ex) {
        LOG_ERROR_STR(itsLogPrefix << "Could not create meta data: " << ex);

        if (!itsParset.settings.realTime)   
          THROW(StorageException, ex); 
#if defined HAVE_AIPSPP
      } 
      catch (casacore::AipsError &ex)
      {
        LOG_ERROR_STR(itsLogPrefix << "Could not create meta data (AipsError): " << ex.what());

        if (!itsParset.settings.realTime)    
          THROW(StorageException, ex.what()); 
#endif
      }
    }


    template<typename T> void OutputThread<T>::fini( const FinalMetaData &finalMetaData )
    {
      try {
        // fini the data product
        ASSERT(itsWriter.get());

        itsWriter->fini(finalMetaData);
      } catch (Exception &ex) {
        LOG_ERROR_STR(itsLogPrefix << "Could not add final meta data: " << ex);

        if (!itsParset.settings.realTime)   
          THROW(StorageException, ex); 
#if defined HAVE_AIPSPP
      } 
      catch (casacore::AipsError &ex)
      {
        LOG_ERROR_STR(itsLogPrefix << "Could not add final meta data (AipsError): " << ex.what());

        if (!itsParset.settings.realTime)    
          THROW(StorageException, ex.what()); 
#endif
      }
    }


    template<typename T> ParameterSet OutputThread<T>::feedbackLTA() const
    {
      ParameterSet result;

      try {
        result.adoptCollection(itsWriter->configuration());
      } catch (Exception &ex) {
        LOG_ERROR_STR(itsLogPrefix << "Could not obtain feedback for LTA: " << ex);
      }

      return result;
    }


    template<typename T> void OutputThread<T>::process()
    {
      LOG_DEBUG_STR(itsLogPrefix << "process() entered");

      createMS();

#     pragma omp parallel sections num_threads(2)
      {
#       pragma omp section
        {
          doWork();
          cleanUp();
        }

#       pragma omp section
        {
          init();
        }
      }

      LOG_INFO_STR(itsLogPrefix << "Finalised data product.");
    }

    // Make required instantiations
    template class OutputThread<StreamableData>;
    template class OutputThread<TABTranspose::BeamformedData>;


    SubbandOutputThread::SubbandOutputThread(const Parset &parset,
          unsigned streamNr, Pool<StreamableData> &outputPool,
          RTmetadata &mdLogger, const std::string &mdKeyPrefix,
          const std::string &logPrefix, const std::string &targetDirectory)
      :
      OutputThread<StreamableData>(
          parset,
          streamNr,
          outputPool,
          mdLogger,
          mdKeyPrefix,
          logPrefix + "[SubbandOutputThread] ",
          targetDirectory)
    {
      itsBlockDuration = parset.settings.correlator.integrationTime();
    }


    void SubbandOutputThread::createMS()
    {
      ScopedLock sl(casacoreMutex);
      ScopedDelayCancellation dc; // don't cancel casacore calls

      const std::string directoryName =
        itsTargetDirectory == ""
        ? itsParset.getDirectoryName(CORRELATED_DATA, itsStreamNr)
        : itsTargetDirectory;
      const std::string fileName = itsParset.getFileName(CORRELATED_DATA, itsStreamNr);

      const std::string path = directoryName + "/" + fileName;
      LOG_INFO_STR(itsLogPrefix << "Writing correlated data to " << path);

      if (itsParset.settings.realTime) {
        try {
          itsWriter = new MSWriterCorrelated(itsLogPrefix, path, itsParset, itsStreamNr);

          logInitialStreamMetadataEvents("Correlated", fileName, directoryName);
        } catch (Exception &ex) {
          LOG_ERROR_STR(itsLogPrefix << "Cannot open " << path << ": " << ex.what());
          itsWriter = new MSWriterNull(itsParset);

#if defined HAVE_AIPSPP
        } catch (casacore::AipsError &ex) {
          LOG_ERROR_STR(itsLogPrefix << "Caught AipsError: " << ex.what());
          itsWriter = new MSWriterNull(itsParset);
#endif
        }
      } else { // don't handle exception in non-RT: it is fatal: avoid rethrow for a clean stracktrace
        itsWriter = new MSWriterCorrelated(itsLogPrefix, path, itsParset, itsStreamNr);

        logInitialStreamMetadataEvents("Correlated", fileName, directoryName);
      }

      itsNrExpectedBlocks = itsParset.settings.correlator.nrIntegrations;
    }


    TABOutputThread::TABOutputThread(const Parset &parset,
        unsigned streamNr, Pool<TABTranspose::BeamformedData> &outputPool,
        RTmetadata &mdLogger, const std::string &mdKeyPrefix,
        const std::string &logPrefix,
        const std::string &targetDirectory)
      :
      OutputThread<TABTranspose::BeamformedData>(
          parset,
          streamNr,
          outputPool,
          mdLogger,
          mdKeyPrefix,
          logPrefix + "[TABOutputThread] ",
          targetDirectory)
    {
    }


    void TABOutputThread::createMS()
    {
      // even the HDF5 writer accesses casacore, to perform conversions
      ScopedLock sl(casacoreMutex);
      ScopedDelayCancellation dc; // don't cancel casacore calls

      const std::string directoryName =
        itsTargetDirectory == ""
        ? itsParset.getDirectoryName(BEAM_FORMED_DATA, itsStreamNr)
        : itsTargetDirectory;
      const std::string fileName = itsParset.getFileName(BEAM_FORMED_DATA, itsStreamNr);

      const std::string path = directoryName + "/" + fileName;
      LOG_INFO_STR(itsLogPrefix << "Writing beamformed data to " << path);

      if (itsParset.settings.realTime) {
        try {
#ifdef HAVE_DAL
          itsWriter = new MSWriterDAL<float,3>(path, itsParset, itsStreamNr);
#else
          itsWriter = new MSWriterFile(path);
#endif
          logInitialStreamMetadataEvents("Beamformed", fileName, directoryName);

        } catch (Exception &ex) {
          LOG_ERROR_STR(itsLogPrefix << "Cannot open " << path << ": " << ex.what());
          itsWriter = new MSWriterNull(itsParset);

#if defined HAVE_AIPSPP
        } catch (casacore::AipsError &ex) {
          LOG_ERROR_STR(itsLogPrefix << "Caught AipsError: " << ex.what());
          itsWriter = new MSWriterNull(itsParset);
#endif
        }
      } else { // don't handle exception in non-RT: it is fatal: avoid rethrow for a clean stracktrace
#ifdef HAVE_DAL
        itsWriter = new MSWriterDAL<float,3,1>(path, itsParset, itsStreamNr);
#else
        itsWriter = new MSWriterFile(path);
#endif
        logInitialStreamMetadataEvents("Beamformed", fileName, directoryName);
      }

      itsNrExpectedBlocks = itsParset.settings.nrBlocks();
    }


    RSPRawOutputThread::RSPRawOutputThread(const Parset &parset,
          unsigned streamNr, Pool<StreamableData> &outputPool,
          RTmetadata &mdLogger, const std::string &mdKeyPrefix,
          const std::string &logPrefix, const std::string &targetDirectory)
      :
      OutputThread<StreamableData>(
          parset,
          streamNr,
          outputPool,
          mdLogger,
          mdKeyPrefix,
          logPrefix + "[RSPRawOutputThread] ",
          targetDirectory)
    {
    }

    void RSPRawOutputThread::createMS()
    {
      // Unlike the other output types, there is no need to grab casacoreMutex
      // or delay cancellation, because the RSP raw writer does not use casacore or libhdf5.

      const std::string directoryName =
        itsTargetDirectory == ""
        ? itsParset.getDirectoryName(RSP_RAW_DATA, itsStreamNr)
        : itsTargetDirectory;
      const std::string fileName = itsParset.getFileName(RSP_RAW_DATA, itsStreamNr);

      const std::string path = directoryName + "/" + fileName;
      LOG_INFO_STR(itsLogPrefix << "Writing RSP raw data to " << path);

      // Write parset as observation metadata. We end up with many duplicate files,
      // but at least we get the parset, even if storage node(s) fail.
      Parset rspRawParset = makeRspRawParset();

      if (itsParset.settings.realTime) {
        try {
          itsWriter = new MSWriterFile(path);
          rspRawParset.writeFile(path + ".parset"); // relies on (recursive) mkdir by MSWriterFile()

          // The rest of the system doesn't know about RSP raw data output, but if monitoring did, enable this:
          //logInitialStreamMetadataEvents("RSPRaw", fileName, directoryName);
        } catch (Exception& ex) {
          LOG_ERROR_STR(itsLogPrefix << "Cannot open " << path << ": " << ex.what());
          itsWriter = new MSWriterNull(itsParset);
        }
      } else { // don't handle exception in non-RT: it is fatal: avoid rethrow for a clean stracktrace
        itsWriter = new MSWriterFile(path);
        rspRawParset.writeFile(path + ".parset"); // relies on (recursive) mkdir by MSWriterFile()

        // The rest of the system doesn't know about RSP raw data output, but if monitoring did, enable this:
        //logInitialStreamMetadataEvents("RSPRaw", fileName, directoryName);
      }

      // NOTE: for RSP raw we need to count bytes instead of blocks, but N/A here.
      itsNrExpectedBlocks = itsParset.settings.nrRspRawBlocks();
    }

    Parset RSPRawOutputThread::makeRspRawParset()
    {
      LOG_INFO("makeRspRawParset() begin");

      Parset rspRawParset(itsParset);

      // Patch several parset key values for easy setup of (single node) offline reprocessing.
      rspRawParset.replace("Observation.startTime",
                           LOFAR::timeString(rspRawParset.settings.rspRaw.startTime, true, "%F %T"));
      rspRawParset.replace("Observation.stopTime",
                           LOFAR::timeString(rspRawParset.settings.rspRaw.stopTime,  true, "%F %T"));
      rspRawParset.replace("Cobalt.realTime", "false");
      rspRawParset.replace("Observation.DataProducts.Output_RSPRaw.enabled", "false");

      const unsigned nrBoards = rspRawParset.settings.rspRaw.nrBeamletsPerBoardList.size();
      set<string> stationNameSet;
      for (unsigned af = 0; af < rspRawParset.settings.rspRaw.antennaFieldNames.size(); ++af)
      {
        const string antFieldName = rspRawParset.settings.rspRaw.antennaFieldNames[af].fullName();

        string rspPortsValue(1, '[');
        string dataslotListValue(1, '[');
        string rspBoardListValue(1, '[');
        for (unsigned b = 0; b < nrBoards; ++b)
        {
          unsigned nrBeamlets = rspRawParset.settings.rspRaw.nrBeamletsPerBoardList[b];
          if (nrBeamlets == 0) {
            // It is valid to completely filter streams, but they must all be at the end in the list.
            // If nrBeamlets half-way is 0 we cannot generate a valid dataslot list, which computes nrBeamlets-1.
            for (++b; b < nrBoards; ++b) {
              if (nrBeamlets != 0) {
                LOG_WARN_STR("makeRspRawParset(): empty nr beamlets per board found for antenna field " <<
                             antFieldName << " followed by non-empty nr beamlets. Observation data output unaffected, " <<
                             "but cannot write valid DataslotList in RSP *output* parset to support offline post-processing.");
                break;
              }
            }
            break;
          }

          if (b > 0) {
            rspPortsValue += ", ";
            dataslotListValue += ", ";
            rspBoardListValue += ", ";
          }

          rspPortsValue += "file:" + rspRawParset.getFileName(RSP_RAW_DATA, af * nrBoards + b);

          dataslotListValue += str(boost::format("0..%u") % (nrBeamlets - 1));
          rspBoardListValue += str(boost::format("%u*%u") % nrBeamlets % b);

          stationNameSet.insert(rspRawParset.settings.rspRaw.antennaFieldNames[af].station);
        }

        rspPortsValue.push_back(']');
        rspRawParset.replace("PIC.Core." + antFieldName + ".RSP.sources", rspPortsValue);
        rspRawParset.replace("PIC.Core." + antFieldName + ".RSP.receiver", "localhost");

        dataslotListValue.push_back(']');
        rspRawParset.replace("Observation.Dataslots." + antFieldName + ".DataslotList", dataslotListValue);
        rspBoardListValue.push_back(']');
        rspRawParset.replace("Observation.Dataslots." + antFieldName + ".RSPBoardList", rspBoardListValue);
      }

      ostringstream stationListStr;
      LOFAR::print(stationListStr, stationNameSet.begin(), stationNameSet.end(), ",", "[", "]");
      rspRawParset.replace("Observation.VirtualInstrument.stationList", stationListStr.str());

      rspRawParset.updateSettings(); // not needed and may WARN, but does some checks and to return valid obj

      LOG_INFO("makeRspRawParset() end");

      return rspRawParset;
    }

  } // namespace Cobalt
} // namespace LOFAR

