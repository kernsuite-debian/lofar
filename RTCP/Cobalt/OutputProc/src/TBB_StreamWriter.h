//# TBB_StreamWriter.h: manage incoming TBB stream from 1 station with in-/output thread pair
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

#ifndef LOFAR_COBALT_OUTPUTPROC_TBBSTREAMWRITER_H
#define LOFAR_COBALT_OUTPUTPROC_TBBSTREAMWRITER_H 1

#ifndef USE_THREADS // from the LOFAR build system
#error The TBB writer needs multi-threading (USE_THREADS).
#endif

#include "TBB_Frame.h"
#include <sys/time.h>
#include <boost/scoped_ptr.hpp>
#include <boost/crc.hpp>

#include <Common/Thread/Thread.h>
#include <CoInterface/Queue.h>
#include <Stream/FileStream.h>

namespace LOFAR
{
  namespace Cobalt
  {

    class TBB_Writer;

    class TBB_StreamWriter
    {
      /*
       * - The input thread receives incoming TBB frame headers, checks the header CRC, and puts them in a frameQueue.
       * - The output thread checks the data CRC, creates an HDF5 file per station, creates groups and datasets,
       *   writes the data, and returns empty frame pointers through the emptyQueue back to the input thread.
       *
       * On timeouts for all input threads, the main thread sends C++ thread cancellations. Input appends a NULL msg to notify output.
       * This isolates (soft) real-time input from HDF5/disk latencies, and the HDF5 C library from C++ cancellation exceptions.
       */

      /*
       * Queue size: With TBB_PRINT_QUEUE_LEN defined, the max used buffer size observed was 343.
       * This was for 1 udp stream (instead of 6 or 12) from 1 station. Having 1024 buffers per thread seems reasonable.
       */
      static const unsigned theirNrFrameBuffers = 1024;

      TBB_Frame itsFrameBuffers[theirNrFrameBuffers];

      // Thread-safe queue with pointers that point into itsFrameBuffers.
      Queue<TBB_Frame*> itsReceiveQueue; // input  -> output thread
      Queue<TBB_Frame*> itsFreeQueue;    // output -> input  thread

      TBB_Writer& itsWriter;
      boost::crc_optimal<16, 0x8005 /*, 0, 0, false, false*/> itsCrc16gen;
#ifdef TBB_DUMP_RAW_STATION_FRAMES
      boost::scoped_ptr<LOFAR::FileStream> itsRawStationData;
#endif
      const std::string& itsLogPrefix;
      time_t itsLastLogErrorTime;
      const std::string& itsInputStreamName;
      int& itsInExitStatus;
      int& itsOutExitStatus;

      // See TBB_Writer_main.cc::doTBB_Run() why this is used racily for now.
      struct timeval itsInputTimeoutStamp;

      boost::scoped_ptr<Thread> itsOutputThread;
      boost::scoped_ptr<Thread> itsInputThread;
      // Thread objects must be last in TBB_StreamWriter for safe destruction.


      // do not use
      TBB_StreamWriter();
      TBB_StreamWriter(const TBB_StreamWriter& rhs);
      TBB_StreamWriter& operator=(const TBB_StreamWriter& rhs);

    public:
      TBB_StreamWriter(TBB_Writer& writer, const std::string& inputStreamName,
                       const std::string& logPrefix, int& inExitStatus, int& outExitStatus);
      ~TBB_StreamWriter();

      // Main thread
      time_t getTimeoutStampSec() const;

    private:
      // Input threads
      void frameHeaderLittleToHost(TBB_Header& fh) const;
      bool crc16tbb(const TBB_Header* header);
      bool doTransient() const;
      bool checkFrame(TBB_Header& header, unsigned receivedSize);
      void mainInputLoop();

      // Output threads
      void mainOutputLoop();
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

