//# SharedMemoryStream.h: 
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

#ifndef LOFAR_LCS_STREAM_SHARED_MEMORY_STREAM_H
#define LOFAR_LCS_STREAM_SHARED_MEMORY_STREAM_H

#if defined USE_THREADS

#include <Common/Thread/Mutex.h>
#include <Common/Thread/Semaphore.h>
#include <Stream/Stream.h>

namespace LOFAR {

class SharedMemoryStream : public Stream
{
  public:
    SharedMemoryStream(const std::string &annotation = "");
    virtual ~SharedMemoryStream();

    virtual size_t tryRead(void *ptr, size_t size);
    virtual size_t tryWrite(const void *ptr, size_t size);

    // these 2 throw a NotImplemented exception
    virtual size_t tryReadv(const struct iovec *iov, int iovcnt);
    virtual size_t tryWritev(const struct iovec *iov, int iovcnt);

  private:
    Mutex      readLock, writeLock;
    Semaphore  readDone, writePosted;
    const void *writePointer;
    size_t     readSize, writeSize;
};

} // namespace LOFAR

#endif
#endif
