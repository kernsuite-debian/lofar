//# StringStream.cc: 
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

#include <Stream/StringStream.h>
#include <Common/Thread/Cancellation.h>

#include <cstring>


namespace LOFAR {

StringStream::~StringStream()
{
  close();
}


size_t StringStream::tryRead(void *ptr, size_t size)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

// NOTE: still wrong for !USE_THREADS and wrt less than size bytes avail and stringstream error vs EndOfStreamException, but !USE_THREADS is obsolete anyway. Need CondVar instead of Semaphore and drop !USE_THREADS.
#ifdef USE_THREADS
  if (!dataWritten.down(size)) {
    ScopedLock sl(itsMutex);
    size_t avail = dataWritten.getValue();
    if (avail == 0) // size > 0
      THROW(EndOfStreamException, "Stream has been closed");

    size = avail;
    dataWritten.down(size);

    itsBuffer.read(static_cast<char*>(ptr), size);

    return size;
  }
#endif

  {
    ScopedLock sl(itsMutex);
    itsBuffer.read(static_cast<char*>(ptr), size);
  }

  return size;
}


size_t StringStream::tryWrite(const void *ptr, size_t size)
{
  Cancellation::point(); // keep behaviour consistent with real I/O streams

  {
    ScopedLock sl(itsMutex);
    itsBuffer.write(static_cast<const char*>(ptr), size);
  }

#ifdef USE_THREADS
  dataWritten.up(size);
#endif

  return size;
}


size_t StringStream::tryReadv(const struct iovec *iov, int iovcnt)
{
  Cancellation::point(); // keep behaviour consistent with non-null streams

  size_t size = 0;

  for (int i = 0; i < iovcnt; i++) {
    size += iov[i].iov_len;
  }

// NOTE: still wrong for !USE_THREADS and wrt less than size bytes avail and stringstream error vs EndOfStreamException, but !USE_THREADS is obsolete anyway. Need CondVar instead of Semaphore and drop !USE_THREADS.
#ifdef USE_THREADS
  if (!dataWritten.down(size)) {
    ScopedLock sl(itsMutex);
    // stream closed and avail < size
    size_t avail = dataWritten.getValue();
    if (avail == 0) // size > 0
      THROW(EndOfStreamException, "Stream has been closed");

    size = avail;
    dataWritten.down(size);

    for (int i = 0; i < iovcnt && avail > 0; i++) {
      size_t len = avail < iov[i].iov_len ? avail : iov[i].iov_len;
      itsBuffer.read(static_cast<char*>(iov[i].iov_base), len);
      avail -= len;
    }

    return size;
  }
#endif

  {
    ScopedLock sl(itsMutex);
    for (int i = 0; i < iovcnt; i++) {
      itsBuffer.read(static_cast<char*>(iov[i].iov_base), iov[i].iov_len);
    }
  }

  return size;
}


size_t StringStream::tryWritev(const struct iovec *iov, int iovcnt)
{
  Cancellation::point(); // keep behaviour consistent with non-null streams

  size_t size = 0;

  {
    ScopedLock sl(itsMutex);
    for (int i = 0; i < iovcnt; i++) {
      itsBuffer.write(static_cast<const char*>(iov[i].iov_base), iov[i].iov_len);
      size += iov[i].iov_len;
    }
  }

#ifdef USE_THREADS
  dataWritten.up(size);
#endif

  return size;
}


void StringStream::close()
{
#ifdef USE_THREADS
  dataWritten.noMore();
#endif
}

} // namespace LOFAR
