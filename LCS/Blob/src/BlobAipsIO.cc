//# BlobAipsIO.cc: A Blob buffer for Aips++ ByteIO
//#
//# Copyright (C) 2006
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

#if !defined(HAVE_AIPSPP)
#warning AIPS++ is not available, but BlobAipsIO needs it.
#else

#include <Blob/BlobAipsIO.h>

using namespace casacore;

namespace LOFAR {

  BlobAipsIO::BlobAipsIO (BlobOStream& os)
    : itsOBuf (&os),
      itsIBuf (0)
  {
    itsOBuf->putStart ("BlobAipsIO", 1);
  }

  BlobAipsIO::BlobAipsIO (BlobIStream& is)
    : itsOBuf (0),
      itsIBuf (&is)
  {
    itsIBuf->getStart ("BlobAipsIO");
  }

  BlobAipsIO::~BlobAipsIO()
  {
    if (itsOBuf) {
      itsOBuf->putEnd();
    } else {
      itsIBuf->getEnd();
    }
  }

  void BlobAipsIO::write (Int64 size, const void* buf)
  {
    itsOBuf->put (static_cast<const uchar*>(buf), size);
  }

  void BlobAipsIO::write (uInt size, const void* buf)
  {
    itsOBuf->put (static_cast<const uchar*>(buf), size);
  }

  Int64 BlobAipsIO::read (Int64 size, void* buf, Bool)
  {
    itsIBuf->get (static_cast<uchar*>(buf), size);
    return size;
  }

  Int BlobAipsIO::read (uInt size, void* buf, Bool)
  {
    itsIBuf->get (static_cast<uchar*>(buf), size);
    return size;
  }

  Int64 BlobAipsIO::length()
  {
    return -1;
  }

  Bool BlobAipsIO::isReadable() const
  {
    return itsIBuf != 0;
  }

  Bool BlobAipsIO::isWritable() const
  {
    return itsOBuf != 0;
  }

  Bool BlobAipsIO::isSeekable() const
  {
    return false;
  }

  Int64 BlobAipsIO::doSeek (Int64, ByteIO::SeekOption)
  {
    return 0;
  }

}

#endif
