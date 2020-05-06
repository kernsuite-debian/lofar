//# Stream.h: 
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

#ifndef LOFAR_LCS_STREAM_STREAM_H
#define LOFAR_LCS_STREAM_STREAM_H

#include <cstddef>
#include <sys/uio.h>
#include <string>

#include <Common/Exception.h>


namespace LOFAR {

class Stream
{
  public:
    Stream(const std::string &annotation = "");
    virtual ~Stream();

    virtual size_t tryRead(void *ptr, size_t size) = 0;
    void	   read(void *ptr, size_t size); // does not return until all bytes are read

    virtual size_t tryWrite(const void *ptr, size_t size) = 0;
    void	   write(const void *ptr, size_t size); // does not return until all bytes are written

    virtual size_t tryReadv(const struct iovec *iov, int iovcnt) = 0;
    virtual size_t tryWritev(const struct iovec *iov, int iovcnt) = 0;

    std::string    readLine(); // excludes '\n'

    virtual void   sync();

    virtual std::string description() const = 0; // returns a description of the stream (like the filename for a FileStream, the address for a SocketStream, etc)

    /* set/get free-form annotation for this stream.
     * Particularly useful for annotating a stream for logging.
     */
    const std::string &getAnnotation() const { return annotation; }
    void setAnnotation(const std::string &_annotation) { annotation = _annotation; }

protected:
    // optional free-form text field for annotation about this stream (for logging/debugging)
    std::string annotation;
};

EXCEPTION_CLASS(EndOfStreamException, LOFAR::Exception);

} // namespace LOFAR

#endif
