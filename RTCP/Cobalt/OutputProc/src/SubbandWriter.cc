//# SubbandWriter.cc: Write a subband of visibility data (UV) to storage
//# Copyright (C) 2008-2013, 2017
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

#include <lofar_config.h>

#include "SubbandWriter.h"

#include <CoInterface/CorrelatedData.h>
#include <CoInterface/Allocator.h>
#include <CoInterface/OMPThread.h>
#include <Common/Timer.h>

#include <boost/format.hpp>
using boost::format;

namespace LOFAR
{
  namespace Cobalt
  {
    SubbandWriter::SubbandWriter(const Parset &parset, unsigned streamNr,
        RTmetadata &mdLogger, const std::string &mdKeyPrefix,
        const std::string &logPrefix)
    :
      itsStreamNr(streamNr),
      itsArena(0),
      itsAllocator(0),
      itsOutputPool(str(format("SubbandWriter::itsOutputPool [stream %u]") % streamNr), parset.settings.realTime),
      itsInputThread(parset, CORRELATED_DATA, streamNr, itsOutputPool, logPrefix),
      itsOutputThread(parset, streamNr, itsOutputPool, mdLogger, mdKeyPrefix, logPrefix),
      itsAlignment(512),
      itsNrStations(parset.settings.correlator.stations.size()),
      itsNrChannels(parset.settings.correlator.nrChannels),
      itsNrSamples(parset.settings.correlator.nrSamplesPerIntegration())
    {
      ASSERT(preAllocateReceiveQueue <= maxReceiveQueueSize);

      // We alloc all memory at once to avoid maxReceiveQueueSize malloc() calls, which occasionally stall on CEP4
      itsArena = new MallocedArena(maxReceiveQueueSize * CorrelatedData::size(itsNrStations, itsNrChannels, itsNrSamples, itsAlignment), itsAlignment);

      itsAllocator = new SparseSetAllocator(*itsArena);

      for (unsigned i = 0; i < preAllocateReceiveQueue; i++) {
        CorrelatedData *data = new CorrelatedData(itsNrStations, itsNrChannels, itsNrSamples, *itsAllocator, itsAlignment);
        itsOutputPool.free.append(data);
      }
    }

    
    void SubbandWriter::process()
    {
#     pragma omp parallel sections num_threads(3)
      {
#       pragma omp section
        {
          OMPThread::ScopedName sn(str(format("allocator %u") % itsStreamNr));

          for (unsigned i = preAllocateReceiveQueue; i < maxReceiveQueueSize; i++) {
            CorrelatedData *data = new CorrelatedData(itsNrStations, itsNrChannels, itsNrSamples, *itsAllocator, itsAlignment);
            itsOutputPool.free.append(data);
          }
        }

#       pragma omp section
        {
          OMPThread::ScopedName sn(str(format("uv input %u") % itsStreamNr));

          itsInputThread.process();
        }

#       pragma omp section
        {
          OMPThread::ScopedName sn(str(format("uv output %u") % itsStreamNr));

          itsOutputThread.process();
        }
      }
    }


    void SubbandWriter::fini( const FinalMetaData &finalMetaData )
    {
      itsOutputThread.fini(finalMetaData);
    }


    ParameterSet SubbandWriter::feedbackLTA() const
    {
      return itsOutputThread.feedbackLTA();
    }
  } // namespace Cobalt
} // namespace LOFAR

