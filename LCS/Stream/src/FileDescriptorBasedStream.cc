//# FileDescriptorBasedStream.cc: 
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

#include <Stream/FileDescriptorBasedStream.h>

#include <unistd.h>
#include <fcntl.h>

#include <Common/SystemCallException.h>
#include <Common/Thread/Cancellation.h>
#include <Common/LofarLogger.h>

namespace LOFAR {


FileDescriptorBasedStream::FileDescriptorBasedStream(int fd, const std::string &annotation) :
  Stream(annotation),
  fd(fd)
{
}

FileDescriptorBasedStream::~FileDescriptorBasedStream()
{
  if (fd >= 0) {
    int rv;
  
    {
      // Avoid close() throwing in the destructor,
      // as it is a cancellation point (see pthreads(7)).
      ScopedDelayCancellation dc;

      rv = ::close(fd);
    }
    if (rv < 0) {
      // Print error message similar to other failed system calls.
      try {
        THROW_SYSCALL("close");
      } catch (Exception &exc) {
        LOG_ERROR_STR(exc);
      }
    }
  }
}


size_t FileDescriptorBasedStream::tryRead(void *ptr, size_t size)
{
  ssize_t bytes = ::read(fd, ptr, size);
  
  if (bytes < 0)
    THROW_SYSCALL("read");

  if (bytes == 0) 
    throw EndOfStreamException("read", THROW_ARGS);

  return bytes;
}


size_t FileDescriptorBasedStream::tryWrite(const void *ptr, size_t size)
{
  ssize_t bytes = ::write(fd, ptr, size);

  if (bytes < 0)
    THROW_SYSCALL("write");

  return bytes;
}


size_t FileDescriptorBasedStream::tryReadv(const struct iovec *iov, int iovcnt)
{
  ssize_t bytes = ::readv(fd, iov, iovcnt);

  if (bytes < 0)
    THROW_SYSCALL("readv");

  return bytes;
}


size_t FileDescriptorBasedStream::tryWritev(const struct iovec *iov, int iovcnt)
{
  ssize_t bytes = ::writev(fd, iov, iovcnt);

  if (bytes < 0)
    THROW_SYSCALL("writev");

  return bytes;
}


void FileDescriptorBasedStream::sync()
{
  if (::fsync(fd) < 0)
    THROW_SYSCALL("fsync");
}


int FileDescriptorBasedStream::fcntl(int cmd)
{
  int rv = ::fcntl(fd, cmd);

  if (rv < 0)
    THROW_SYSCALL("fcntl");

  return rv;
}


int FileDescriptorBasedStream::fcntl(int cmd, int arg)
{
  int rv = ::fcntl(fd, cmd, arg);

  if (rv < 0)
    THROW_SYSCALL("fcntl");

  return rv;
}

} // namespace LOFAR
