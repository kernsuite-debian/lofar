//# RSPRawWriter.cc: Write raw data stream of an RSP board to storage
//# Copyright (C) 2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include "RSPRawWriter.h"

#include <CoInterface/OMPThread.h>
#include <Common/Timer.h>

#include <boost/format.hpp>
using boost::format;

namespace LOFAR
{
  namespace Cobalt
  {
    RSPRawWriter::RSPRawWriter(const Parset &parset, unsigned streamNr,
        RTmetadata &mdLogger, const std::string &mdKeyPrefix,
        const std::string &logPrefix)
    :
      itsStreamNr(streamNr),
      itsOutputPool(str(format("RSPRawWriter::itsOutputPool [stream %u]") % streamNr), parset.settings.realTime),
      itsInputThread(parset, RSP_RAW_DATA, streamNr, itsOutputPool, logPrefix),
      itsOutputThread(parset, streamNr, itsOutputPool, mdLogger, mdKeyPrefix, logPrefix)
    {
      for (unsigned i = 0; i < preAllocateReceiveQueue; i++) {
        RSPRawData *data = new RSPRawData();
        itsOutputPool.free.append(data);
      }
    }


    void RSPRawWriter::process()
    {
#     pragma omp parallel sections num_threads(2)
      {
#       pragma omp section
        {
          OMPThread::ScopedName sn(str(format("RSPRaw input %u") % itsStreamNr));

          itsInputThread.process();
        }

#       pragma omp section
        {
          OMPThread::ScopedName sn(str(format("RSPRaw output %u") % itsStreamNr));

          itsOutputThread.process();
        }
      }
    }


    void RSPRawWriter::fini( const FinalMetaData &finalMetaData )
    {
      itsOutputThread.fini(finalMetaData);
    }


    ParameterSet RSPRawWriter::feedbackLTA() const
    {
      return itsOutputThread.feedbackLTA();
    }
  } // namespace Cobalt
} // namespace LOFAR

