//# InputThread.cc
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

//# Always #include <lofar_config.h> first!
#include <lofar_config.h>

#include "InputThread.h"

#include <Common/Timer.h>
#include <Stream/NullStream.h>
#include <Stream/SocketStream.h>
#include <Stream/StreamFactory.h>
#include <CoInterface/Stream.h>


namespace LOFAR
{
  namespace Cobalt
  {
    InputThread::InputThread(const Parset &parset, OutputType outputType,
                             unsigned streamNr, Pool<StreamableData> &outputPool,
                             const std::string &logPrefix)
      :
      itsLogPrefix(logPrefix + "[InputThread] "),
      itsNrIntegrationsReceived(0),
      itsNrIntegrations(outputType == CORRELATED_DATA ? parset.settings.correlator.nrIntegrations :
                                                        parset.settings.nrRspRawBlocks()),
      itsInputDescriptor(getStreamDescriptorBetweenIONandStorage(parset, outputType, streamNr)),
      itsOutputPool(outputPool),
      itsDeadline(parset.settings.realTime ? parset.settings.stopTime : 0)
    {
      ASSERT((parset.settings.correlator.enabled && outputType == CORRELATED_DATA) ||
             (parset.settings.rspRaw.enabled     && outputType == RSP_RAW_DATA));
    }


    void InputThread::process()
    {
      try {
        LOG_INFO_STR(itsLogPrefix << "Creating connection from " << itsInputDescriptor << "..." );
        SmartPtr<Stream> streamFromION(createStream(itsInputDescriptor, true, itsDeadline));
        LOG_INFO_STR(itsLogPrefix << "Creating connection from " << itsInputDescriptor << ": done" );

        for(SmartPtr<StreamableData> data; (data = itsOutputPool.free.remove()) != NULL; itsOutputPool.filled.append(data)) {
          data->read(streamFromION, 1); // Cobalt writes with an alignment of 1
          ++itsNrIntegrationsReceived; // for RSP_RAW_DATA we need to count bytes, but N/A here

          LOG_DEBUG_STR(itsLogPrefix << "Received data block with seq nr " << data->sequenceNumber());
        }
      } catch (TimeOutException &) {
        LOG_WARN_STR(itsLogPrefix << "Connection from " << itsInputDescriptor << " timed out");
      } catch (EndOfStreamException &) {
        LOG_INFO_STR(itsLogPrefix << "Connection from " << itsInputDescriptor << " closed by foreign host");
      } catch (SystemCallException &ex) {
        LOG_WARN_STR(itsLogPrefix << "Connection from " << itsInputDescriptor << " failed: " << ex.text());
      }

      // report statistics
      const float didNotReceivePerc = itsNrIntegrations == 0 ? 0.0 : 100.0 - 100.0 * itsNrIntegrationsReceived / itsNrIntegrations;
      const float didNotSendPerc = didNotReceivePerc;

      if (didNotReceivePerc > 0)
        LOG_WARN_STR(itsLogPrefix << "Did not receive " << didNotReceivePerc << "% of the data: received=" <<
                     itsNrIntegrationsReceived << " expected=" << itsNrIntegrations);
      if (didNotSendPerc > 0)
        LOG_WARN_STR(itsLogPrefix << "Did not send " << didNotSendPerc << "% of the data");

      // Append end-of-stream marker
      itsOutputPool.filled.append(NULL, false);
    }
  } // namespace Cobalt
} // namespace LOFAR

