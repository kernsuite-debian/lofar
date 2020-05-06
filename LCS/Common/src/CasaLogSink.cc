//# CasaLogSink.cc: LogSink to convert casacore messages to LOFAR 
//#
//# Copyright (C) 2011
//# ASTRON (Netherlands Institute for Radio Astronomy)
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

// @author Ger van Diepen (gvd AT astron DOT nl)

#include <lofar_config.h>
#include <Common/CasaLogSink.h>
#include <string>
#include <Common/LofarLogger.h>


namespace LOFAR {

#ifdef HAVE_AIPSPP

  CasaLogSink::CasaLogSink()
    : casacore::LogSinkInterface (casacore::LogFilter())
  {}

  CasaLogSink::CasaLogSink (casacore::LogMessage::Priority filter)
    : casacore::LogSinkInterface (casacore::LogFilter(filter))
  {}

  CasaLogSink::CasaLogSink (const casacore::LogFilterInterface& filter)
    : casacore::LogSinkInterface (filter)
  {}

  CasaLogSink::~CasaLogSink()
  {}

  void CasaLogSink::attach()
  {
    casacore::LogSinkInterface* globalSink = new LOFAR::CasaLogSink;
    // Note that the pointer is taken over by LogSink.
    casacore::LogSink::globalSink (globalSink);
  }

  casacore::Bool CasaLogSink::postLocally (const casacore::LogMessage& message)
  {
    casacore::Bool posted = casacore::False;
    if (filter().pass(message)) {
      std::string msg (message.origin().location() + ": " + message.message());
      posted = casacore::True;
      switch (message.priority()) {
      case casacore::LogMessage::DEBUGGING:
      case casacore::LogMessage::DEBUG2:
      case casacore::LogMessage::DEBUG1:
	{
	  LOG_DEBUG (msg);
	  break;
	}
      case casacore::LogMessage::NORMAL5:
      case casacore::LogMessage::NORMAL4:
      case casacore::LogMessage::NORMAL3:
      case casacore::LogMessage::NORMAL2:
      case casacore::LogMessage::NORMAL1:
      case casacore::LogMessage::NORMAL:
	{
	  LOG_INFO (msg);
	  break;
	}
      case casacore::LogMessage::WARN:
	{
	  LOG_WARN (msg);
	  break;
	}
      case casacore::LogMessage::SEVERE:
	{
	  LOG_ERROR (msg);
	  break;
	}
      }
    }
    return posted;
  }

  void CasaLogSink::clearLocally()
  {}

  casacore::String CasaLogSink::localId()
  {
    return casacore::String("CasaLogSink");
  }

  casacore::String CasaLogSink::id() const
  {
    return casacore::String("CasaLogSink");
  }

#else
  void CasaLogSink::attach()
  {
    cerr << "WARNING: no casa logging available." << endl;
  }
#endif

} // end namespaces
