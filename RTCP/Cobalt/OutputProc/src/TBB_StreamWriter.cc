//# TBB_StreamWriter.cc: manage incoming TBB stream from 1 station with in-/output thread pair
//# Copyright (C) 2012-2017  ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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

#include "TBB_StreamWriter.h"
#include <csignal>
#include <endian.h>
#if __BYTE_ORDER != __BIG_ENDIAN && __BYTE_ORDER != __LITTLE_ENDIAN
#error Byte order is neither big endian nor little endian: not supported
#endif
#include <boost/lexical_cast.hpp>
#include <boost/format.hpp>

#include <Common/LofarLogger.h>
#include <Stream/StreamFactory.h>
#include "TBB_Writer.h"

namespace LOFAR
{
  namespace Cobalt
  {

    using namespace std;

    static void maskSignals()
    {
      sigset_t sigset_all_masked;
      ::sigfillset(&sigset_all_masked);
      int rv;
      if ((rv = ::pthread_sigmask(SIG_SETMASK, &sigset_all_masked, NULL)) != 0) {
        LOG_WARN_STR("TBB: maskSignals(): pthread_sigmask() failed: " << boost::lexical_cast<string>(rv));
      }
    }


    TBB_StreamWriter::TBB_StreamWriter(TBB_Writer& writer, const string& inputStreamName,
                                       const string& logPrefix,
                                       int& inExitStatus, int& outExitStatus)
      : itsWriter(writer),
        itsLogPrefix(logPrefix),
        itsLastLogErrorTime(0),
        itsInputStreamName(inputStreamName),
        itsInExitStatus(inExitStatus),
        itsOutExitStatus(outExitStatus),
        itsInputTimeoutStamp()
    {
      for (unsigned i = 0; i < theirNrFrameBuffers; i++) {
        itsFreeQueue.append(&itsFrameBuffers[i]);
      }

#ifdef TBB_DUMP_RAW_STATION_FRAMES
      struct timeval ts;
      ::gettimeofday(&ts, NULL);
      string rawStDataFilename = str(boost::format("tbb_raw_station_frames_%ld_%p.fraw") % ts.tv_sec % (void*)itsFrameBuffers);
      try {
        itsRawStationData = new FileStream(rawStDataFilename, S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
      } catch (exception& exc) {
        LOG_WARN(itsLogPrefix + "Failed to open raw station data file: " + exc.what());
      }
#endif

      itsOutputThread.reset(new Thread(this, &TBB_StreamWriter::mainOutputLoop, "TBB-out-thr", logPrefix + "OutputThread: "));
      try {
        itsInputThread.reset(new Thread(this, &TBB_StreamWriter::mainInputLoop, "TBB-in-thr", logPrefix + "InputThread: "));
      } catch (exception& ) {
        itsReceiveQueue.append(NULL, false); // tell output thread to stop
        throw;
      }
      // Don't change any member vars here, as threads have already started
    }

    TBB_StreamWriter::~TBB_StreamWriter()
    {
      itsInputThread->cancel(); // input thread will notify output thread via NULL message
    }

    time_t TBB_StreamWriter::getTimeoutStampSec() const
    {
      return itsInputTimeoutStamp.tv_sec; // racy read (and no access once guarantee), but only to terminate after timeout
    }

    void TBB_StreamWriter::frameHeaderLittleToHost(TBB_Header& header) const
    {
      header.seqNr = le32toh(header.seqNr);
      header.time = le32toh(header.time);
      header.sampleNrOrBandSliceNr = le32toh(header.sampleNrOrBandSliceNr);
      header.nOfSamplesPerFrame = le16toh(header.nOfSamplesPerFrame);
      header.nOfFreqBands = le16toh(header.nOfFreqBands);
      header.spare = le16toh(header.spare);
      header.crc16 = le16toh(header.crc16);
    }

    /*
     * Assumes that the seqNr field in the TBB_Frame at buf has been zeroed.
     * Takes a ptr to a complete header. (Drop too small frames earlier.)
     */
    bool TBB_StreamWriter::crc16tbb(const TBB_Header* header)
    {
      itsCrc16gen.reset();

      const char* ptr = reinterpret_cast<const char*>(header); // to char* for strict-aliasing
      for (unsigned i = 0; i < sizeof(*header) - sizeof(header->crc16); i += 2) {
        int16_t val;
        memcpy(&val, &ptr[i], sizeof val); // strict-aliasing safe
        val = __bswap_16(val);
        itsCrc16gen.process_bytes(&val, sizeof val);
      }

      // It is also possible to process header->crc16 and see if checksum() equals 0.
      uint16_t crc16val = header->crc16;
#if __BYTE_ORDER == __BIG_ENDIAN
      crc16val = __bswap_16(crc16val);
#endif
      return itsCrc16gen.checksum() == crc16val;
    }

    bool TBB_StreamWriter::doTransient() const
    {
      return itsWriter.getAllSubbandCentralFreqs().empty();
    }

    bool TBB_StreamWriter::checkFrame(TBB_Header& header, unsigned receivedSize)
    {
      /**
       * Make sure that the received frame contains enough bytes that represent
       * at least a header.
       */
      const uint32 HEADERSIZE = sizeof(TBB_Header);
      if(receivedSize < HEADERSIZE)
      {
          logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "Received a frame that is smaller than at least the header size: "
              + boost::lexical_cast<string>(receivedSize) + ", minimum size expected: "
              + boost::lexical_cast<string>(HEADERSIZE));
          return false;
      }

      uint32_t seqNr = header.seqNr; // save (little endian)
      header.seqNr = 0; // for crc computation
      /**
       * TODO 2018-11-13, thomas
       * Disabled CRC16 header check because the ALERT firmware appears to
       * be broken.  It sends headers with wrong checksums.
       */
      bool crcOk = crc16tbb(&header);
      crcOk = true;
      header.seqNr = seqNr; // restore (but seqNr not used except in error msg)
      frameHeaderLittleToHost(header);
      if (!crcOk) {
        /*
         * The TBB spec states that each frame has the same fixed length, so the previous values are a good base guess if the header crc fails.
         * But it is not clear if it is worth the effort to try to guess to fix something up. For now, drop and log.
         */
        logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "crc16 error: " + header.to_string());
        return false;
      }

      if ( doTransient() ) {
        if ( header.sampleFreq != itsWriter.getSampleFreqMHz() ) {
            logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "dropping frame with unexpected value for header field sampleFreq: " +
                                                    boost::lexical_cast<string>((unsigned)header.sampleFreq));
            return false;
        }

        if ( header.nOfFreqBands != 0 ) {
            logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "dropping frame with unexpected value for header field nOfFreqBands: " +
                                                    boost::lexical_cast<string>(header.nOfFreqBands));
            return false;
        }

        if ( sizeof(TBB_Header) + header.nOfSamplesPerFrame * sizeof(int16_t) + /*crc32:*/sizeof(uint32_t) != TBB_Frame::transientFrameSize ) {
            logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "dropping frame with unexpected value for header field nOfSamplesPerFrame: " +
                                                    boost::lexical_cast<string>(header.nOfSamplesPerFrame));
            return false;
        }
      } else { /*spectral*/

        // NOTE: in spectral mode, TBB_Dipole code only supports packets with 1 band in a packet. Already enforce here.
        if ( header.nOfFreqBands != 1 ) {
            logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "unexpected value for header field nOfFreqBands: " +
                                                    boost::lexical_cast<string>(header.nOfFreqBands) +
                               " Not dropping frame, because for spectral mode we are still filling in all the correct details in the header. Header: " + header.to_string());

            //TODO: Disabling this check for now, just returning true instead of false. But we do want the error to be logged.
            return true;
            //return false;
        }

        if ( sizeof(TBB_Header) + header.nOfSamplesPerFrame * 2 * sizeof(int16_t) + /*crc32:*/sizeof(uint32_t) != TBB_Frame::spectralFrameSize) {
            logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "unexpected value for header field nOfSamplesPerFrame: " +
                                                    boost::lexical_cast<string>(header.nOfSamplesPerFrame) +
                               " Not dropping frame, because for spectral mode we are still filling in all the correct details in the header. Header: " + header.to_string());

            //TODO 20181128: seems like the packet size changed due to crc, but that's not taken into account of the tests yet.
            // Disabling this check for now, just returning true instead of false. But we do want the error to be logged.
            return true;
            //return false;
        }
      }

      return true;
    }

    void TBB_StreamWriter::mainInputLoop()
    {
      // Mask all signals for workers to force signal delivery to the main thread.
      maskSignals();

      // Always (try to) notify output thread to stop at the end, else we may hang.
      class NotifyOutputThread
      {
        Queue<TBB_Frame*>& queue;
      public:
        NotifyOutputThread(Queue<TBB_Frame*>& queue) : queue(queue) { }

        ~NotifyOutputThread() {
          try {
            queue.append(NULL, false);
          } catch (exception& exc) {
            LOG_WARN_STR("TBB: may have failed to notify output thread to terminate: " << exc.what());
          }
        }
      } notifyOutThr(itsReceiveQueue);

      boost::scoped_ptr<Stream> stream;
      try {
        stream.reset(createStream(itsInputStreamName, true));
      } catch (Exception& exc) { // SystemCallException or CoInterfaceException (or TimeOutException)
        LOG_WARN(itsLogPrefix + exc.text());
        return;
      }
      LOG_DEBUG(itsLogPrefix + "reading incoming data from " + itsInputStreamName);

      const unsigned expectedFrameSize = doTransient() ? TBB_Frame::transientFrameSize : TBB_Frame::spectralFrameSize;
      while (true) {
        TBB_Frame* frame;

        try {
          frame = itsFreeQueue.remove();
          unsigned nread = stream->tryRead(frame, expectedFrameSize); // read() once for udp
          if(nread != expectedFrameSize)
          {
              logErrorRateLimited(&itsLastLogErrorTime, itsLogPrefix + "received a frame with wrong size: "
                  + boost::lexical_cast<string>(nread)
                  + ", expected: " + boost::lexical_cast<string>(expectedFrameSize));
          }

          // Notify master that we are still busy.
          ::gettimeofday(&itsInputTimeoutStamp, NULL);

#ifdef TBB_DUMP_RAW_STATION_FRAMES
          if (itsRawStationData) {
            try {
              itsRawStationData->write(frame, nread);
            } catch (exception& exc) {
              LOG_WARN(itsLogPrefix + "failed to write raw station input frame to file " + exc.text());
            }
          }
#endif

          if (checkFrame(frame->header, nread)) {
            itsReceiveQueue.append(frame);
          } else {
            itsFreeQueue.append(frame); // drop bad frame
          }
        } catch (EndOfStreamException& ) { // after end of stream, for input from file or pipe
          itsInExitStatus = EXIT_SUCCESS;
          break;
        } catch (exception& exc) {
          LOG_FATAL(itsLogPrefix + exc.what());
          break;
        } catch (...) { // thread cancellation exc induced after timeout, for input from udp
          itsInExitStatus = EXIT_SUCCESS;
          throw; // mandatory
        }
      }
    }

    void TBB_StreamWriter::mainOutputLoop()
    {
      // Mask all signals for workers to force delivery to the main thread.
      maskSignals();

      bool running = true;
      while (running) {
        TBB_Frame *frame;
        try {
          frame = NULL;
          frame = itsReceiveQueue.remove();



          if (frame == NULL) {
            LOG_INFO_STR("mainOutputLoop: we have a frame is NULL exiting");
            itsOutExitStatus = EXIT_SUCCESS;
            break;
          }

          LOG_DEBUG_STR("mainOutputLoop: we have a frame: " << frame->header.to_string());

#ifdef TBB_PRINT_QUEUE_LEN
          LOG_INFO(itsLogPrefix + "recvqsz=" + boost::lexical_cast<string>(itsReceiveQueue.size()));
#endif

          itsWriter.getStation(frame->header)->processPayload(*frame);

          // Tolerate the following exceptions. Maybe next rsp/rcu is ok; probably not...
        } catch (SystemCallException& exc) {
          LOG_WARN(itsLogPrefix + exc.text());
        } catch (StorageException& exc) {
          LOG_WARN_STR(itsLogPrefix << exc);
        } catch (dal::DALException& exc) {
          LOG_WARN(itsLogPrefix + exc.what());
        } catch (out_of_range& exc) {
          LOG_WARN(itsLogPrefix + exc.what());
        } catch (Exception& exc) {
          // Config/parset errors are fatal.
          LOG_FATAL_STR(itsLogPrefix << exc);
          running = false;
        } catch (exception& exc) {
          // Other errors are fatal.
          LOG_FATAL(itsLogPrefix + exc.what());
          running = false;
        }

        if (frame != NULL) {
          try {
            itsFreeQueue.append(frame);
          } catch (exception& exc) {
            LOG_WARN(itsLogPrefix + "may have lost a frame buffer (2): " + exc.what());
          }
        }
      }
    }

  } // namespace Cobalt
} // namespace LOFAR

