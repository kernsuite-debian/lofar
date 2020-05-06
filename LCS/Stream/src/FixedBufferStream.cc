//# FixedBufferStream.cc: 
//#
//# Copyright (C) 2008, 2017
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

#include <Stream/FixedBufferStream.h>
#include <Common/Thread/Cancellation.h>

#include <cstring>
#include <boost/format.hpp>

using boost::format;

namespace LOFAR {


FixedBufferStream::FixedBufferStream(char *buffer, size_t size)
:
  itsEnd(buffer + size),
  itsHead(buffer)
{
}


FixedBufferStream::~FixedBufferStream()
{
}


size_t FixedBufferStream::tryRead(void *ptr, size_t size)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

  if (size == 0)
    return 0;

  size_t numBytes = std::min<size_t>(size, itsEnd - itsHead);

  if (numBytes == 0)
    THROW(EndOfStreamException, "No space left in buffer");

  memcpy(ptr, itsHead, numBytes);
  itsHead += numBytes;

  return numBytes;
}


size_t FixedBufferStream::tryWrite(const void *ptr, size_t size)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

  if (size == 0)
    return 0;

  size_t numBytes = std::min<size_t>(size, itsEnd - itsHead);

  if (numBytes == 0)
    THROW(EndOfStreamException, "No space left in buffer");

  memcpy(itsHead, ptr, numBytes);
  itsHead += numBytes;

  return numBytes;
}


size_t FixedBufferStream::tryReadv(const struct iovec *iov, int iovcnt)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

  size_t nread = 0;

  for (int i = 0; i < iovcnt; i++) {
    if (iov[i].iov_len <= (size_t)(itsEnd - itsHead)) {
      memcpy(iov[i].iov_base, itsHead, iov[i].iov_len);
      itsHead += iov[i].iov_len;
      nread += iov[i].iov_len;
    } else {
      if (itsEnd - itsHead == 0) {
        if (nread == 0) // to be read > 0
          THROW(EndOfStreamException, "No space left in buffer");
      } else {
        memcpy(iov[i].iov_base, itsHead, itsEnd - itsHead);
        itsHead = itsEnd;
        nread += itsEnd - itsHead;
      }
      break;
    }
  }

  return nread;
}


size_t FixedBufferStream::tryWritev(const struct iovec *iov, int iovcnt)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

  size_t nwritten = 0;

  for (int i = 0; i < iovcnt; i++) {
    if (iov[i].iov_len <= (size_t)(itsEnd - itsHead)) {
      memcpy(itsHead, iov[i].iov_base, iov[i].iov_len);
      itsHead += iov[i].iov_len;
      nwritten += iov[i].iov_len;
    } else {
      if (itsEnd - itsHead == 0) {
        if (nwritten == 0) // to be written > 0
          THROW(EndOfStreamException, "No space left in buffer");
      } else {
        memcpy(itsHead, iov[i].iov_base, itsEnd - itsHead);
        itsHead = itsEnd;
        nwritten += itsEnd - itsHead;
      }
      break;
    }
  }

  return nwritten;
}

size_t FixedBufferStream::size() const {
  return static_cast<size_t>(itsEnd-itsHead);
}

std::string FixedBufferStream::description() const {
  return str(boost::format("char[%d]@%x") % size() % static_cast<void*>(itsHead));
}

} // namespace LOFAR
