//# MWBlobIO.cc: 
//#
//# Copyright (c) 2007
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

#include <lofar_config.h>


#include <LMWCommon/MWBlobIO.h>
#include <LMWCommon/MWError.h>
#include <Blob/BlobOStream.h>
#include <Blob/BlobIStream.h>

namespace LOFAR { namespace CEP {

  MWBlobOut::MWBlobOut (LOFAR::BlobString& buf, int operation, int streamId,
                        int workerId)
    : itsBuf    (buf),
      itsStream (itsBuf)
  {
    itsStream.putStart ("mw", 1);
    itsOperOffset = buf.size();
    itsStream << static_cast<LOFAR::int32>(operation)
	      << static_cast<LOFAR::int32>(streamId)
	      << static_cast<LOFAR::int32>(workerId);
    ASSERT (buf.size() == itsOperOffset + 3*sizeof(LOFAR::int32));
    itsTimeOffset = buf.size();
    // Put empty times. They will be set later by setTimes.
    itsStream << float(0) << float(0) << float(0) << double(0);
    ASSERT (buf.size() == itsTimeOffset
                                + 3*sizeof(float) + sizeof(double));
  }

  void MWBlobOut::setOperation (int operation)
  {
    using LOFAR::uchar;
    LOFAR::int32 oper = operation;
    uchar* ptr = const_cast<uchar*>(itsBuf.getBuffer()) + itsOperOffset;
    // Use memcpy, because in buffer it might be unaligned.
    memcpy (ptr, &oper, sizeof(LOFAR::int32));
  }

  void MWBlobOut::setTimes (const casacore::Timer& low, const LOFAR::NSTimer& high)
  {
    using LOFAR::uchar;
    float t[3];
    t[0] = low.real();
    t[1] = low.system();
    t[2] = low.user();
    uchar* ptr = const_cast<uchar*>(itsBuf.getBuffer()) + itsTimeOffset;
    // Use memcpy, because in buffer it might be unaligned.
    memcpy (ptr, t, 3*sizeof(float));
    double d = high.getElapsed();
    memcpy (ptr + 3*sizeof(float), &d, sizeof(double));
  }


  MWBlobIn::MWBlobIn (const LOFAR::BlobString& buf)
    : itsBuf    (buf),
      itsStream (itsBuf)
  {
    int version = itsStream.getStart ("mw");
    ASSERT (version==1);
    itsStream >> itsOper >> itsStreamId >> itsWorkerId
              >> itsElapsedTime >> itsSystemTime >> itsUserTime >> itsPrecTime;
  }


}} //end namespaces
