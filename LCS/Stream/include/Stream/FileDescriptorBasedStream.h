//# FileDescriptorBasedStream.h: 
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

#ifndef LOFAR_LCS_STREAM_FILE_DESRIPTOR_BASED_STREAM_H
#define LOFAR_LCS_STREAM_FILE_DESRIPTOR_BASED_STREAM_H

#include <Stream/Stream.h>


namespace LOFAR {

class FileDescriptorBasedStream : public Stream
{
  public:
    FileDescriptorBasedStream(int fd = -1, const std::string &annotation = "");
    virtual	   ~FileDescriptorBasedStream();

    virtual size_t tryRead(void *ptr, size_t size);
    virtual size_t tryWrite(const void *ptr, size_t size);

    virtual size_t tryReadv(const struct iovec *iov, int iovcnt);
    virtual size_t tryWritev(const struct iovec *iov, int iovcnt);

    virtual void   sync();

    // Apart from int, fcntl can also be called with an arg of type struct flock *, or struct f_owner_ex *
    int            fcntl(int cmd);
    int            fcntl(int cmd, int arg);


    int		   fd;

    virtual std::string description() const { return "fd=" + std::to_string(fd); }
};

} // namespace LOFAR

#endif
