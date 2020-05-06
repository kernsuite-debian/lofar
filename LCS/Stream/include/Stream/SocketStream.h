//# SocketStream.h: 
//#
//# Copyright (C) 2008, 2015-2017
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

#ifndef LOFAR_LCS_STREAM_SOCKET_STREAM_H
#define LOFAR_LCS_STREAM_SOCKET_STREAM_H

#include <ctime>
#include <sys/uio.h> // struct iovec
#include <string>
#include <vector>

#include <Common/LofarTypes.h>
#include <Common/Exception.h>
#include <Stream/FileDescriptorBasedStream.h>

namespace LOFAR {

class SocketStream : public FileDescriptorBasedStream
{
  public:
    enum Protocol {
      TCP, UDP
    };

    enum Mode {
      Client, Server
    };

    SocketStream(const std::string &hostname, uint16 _port, Protocol, Mode,
                 time_t deadline = 0, bool doAccept = true, const std::string &bind_local_iface = "", const std::string &annotation = "");
    virtual ~SocketStream();

    FileDescriptorBasedStream *detach();

    void    reaccept(time_t deadline = 0); // only for TCP server socket

    size_t  getReadBufferSize() const;
    void    setReadBufferSize(size_t size) const;

    const Protocol protocol;
    const Mode mode;

    /*
     * Send message(s). Note: only for UDP client socket!
     *   @bufBase contains all messages to be sent. It may have gaps, but all of the same size.
     *   @msgSize indicates the (common) size of each individual message. @msgSize <= @msgBufSize must hold.
     *   @msgBufSize indicates the size of the buffer of each message, aka distance between the
     *     start of two consecutive messages. Typically, same as @msgSize, unless a gap is not to be send.
     *   @sentMsgSizes length indicates the (maximum) number of messages to send.
     *     Note: the Linux sendmmsg(2) man page indicates this is capped to UIO_MAXIOV (1024).
     *     The actually sent sizes per message will be written into this argument.
     *   @flags: passed to sendmsg(2)/sendmmsg(2). For some of our cases, we want to always pass MSG_CONFIRM.
     * Returns the number of messages sent if ok, or throws on syscall error.
     */
    unsigned sendmmsg( void *bufBase, size_t msgSize, size_t msgBufSize,
                       std::vector<unsigned> &sentMsgSizes, int flags ) const;

    /*
     * Receive message(s). Note: only for UDP server socket!
     *   @bufBase is large enough to store all to be received messages
     *   @maxMsgSize indicates the max size of each individual message
     *   @recvdMsgSizes length indicates the maximum number of messages to receive.
     *     The actually received sizes per message will be written into this argument.
     * Returns the number of messages received if ok, or throws on syscall error
     */
    unsigned recvmmsg( void *bufBase, size_t maxMsgSize,
                       std::vector<unsigned> &recvdMsgSizes ) const;

    // Allow individual recv()/send() calls to last for 'timeout' seconds before returning EAGAIN (or EWOULDBLOCK)
    void setTimeout(double timeout);

    std::string getHostname() const { return hostname; }
    uint16 getPort() const { return port; }

    virtual std::string description() const;

  private:
    const std::string hostname;
    uint16 port;
    int listen_sk;
    std::string local_iface;

    void accept(time_t timeout);
};

EXCEPTION_CLASS(TimeOutException, LOFAR::Exception);

} // namespace LOFAR

#endif
