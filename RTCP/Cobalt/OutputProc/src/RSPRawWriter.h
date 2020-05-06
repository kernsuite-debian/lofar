//# RSPRawWriter.h: Write raw data stream of an RSP board to storage
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

#ifndef LOFAR_STORAGE_RSPBOARDWRITER_H
#define LOFAR_STORAGE_RSPBOARDWRITER_H

#include <string>

#include <CoInterface/Parset.h>
#include <CoInterface/Pool.h>
#include <CoInterface/StreamableData.h>
#include <CoInterface/FinalMetaData.h>
#include "InputThread.h"
#include "OutputThread.h"

namespace LOFAR
{
  namespace Cobalt
  {
    /*
     * RSPRawWriter is responsible for completely handling the reception
     * and writing of one stream of data from an RSP board (via InputProc/GPUProc).
     *
     * It maintains an InputThread and RSPRawOutputThread, connected by
     * an internal Pool<> of data blocks.
     */
    class RSPRawWriter
    {
    public:
      RSPRawWriter(const Parset &parset,
                   unsigned streamNr,
                   RTmetadata &mdLogger,
                   const std::string &mdKeyPrefix,
                   const std::string &logPrefix);

      void process();

      void fini(const FinalMetaData &finalMetaData);

      ParameterSet feedbackLTA() const;

      unsigned streamNr() const { return itsStreamNr; }

    private:
      static const unsigned preAllocateReceiveQueue = 32; // number of elements to construct before starting

      const unsigned itsStreamNr;

      Pool<StreamableData> itsOutputPool;

      InputThread itsInputThread;
      RSPRawOutputThread itsOutputThread;
    };
  } // namespace Cobalt
} // namespace LOFAR

#endif

