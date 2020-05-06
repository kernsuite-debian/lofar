//# tPacketReader.cc
//# Copyright (C) 2013  ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
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

#include <string>
#include <omp.h>

#include <Common/LofarLogger.h>
#include <Stream/FileStream.h>
#include <Stream/SocketStream.h>

#include <CoInterface/RSP.h>
#include <CoInterface/OMPThread.h>
#include <InputProc/Station/PacketReader.h>

#include <UnitTest++.h>

using namespace LOFAR;
using namespace Cobalt;

void test(const std::string &filename, unsigned bitmode, unsigned nrPackets)
{
  FileStream fs(filename);

  PacketReader reader("", fs);

  struct RSP packet;

  // We should be able to read these packets
  for( size_t i = 0; i < nrPackets; ++i) {
    ASSERT( reader.readPacket(packet) );
    ASSERT( packet.bitMode() == bitmode );
    ASSERT( packet.clockMHz() == 200 );
  }

  // The file contains no more packets; test if readPacket survives
  // a few calls on the rest of the stream.
  for( size_t i = 0; i < 3; ++i) {
    try {
      ASSERT( !reader.readPacket(packet) );
    } catch (EndOfStreamException &ex) {
      // expected
    }
  }
}

TEST(16bit)
{
  test("tPacketReader.in_16bit", 16, 2);
}

TEST(8bit)
{
  test("tPacketReader.in_8bit",   8, 2);
}

TEST(recvmmsg_killable)
{
  SocketStream ss("localhost", 0, SocketStream::Protocol::UDP, SocketStream::Mode::Server, 0);
  PacketReader reader("", ss);
  bool success = false;

  OMPThreadSet packetReaderThread("recvmmsg_killable");

  OMPThread::init();

  #pragma omp parallel sections num_threads(2)
  {
    #pragma omp section
    {
      try {
        OMPThreadSet::ScopedRun sr(packetReaderThread);

        vector<struct RSP> packets(1024);

        // read packets -- will block as there is no sender
        reader.readPackets(packets);
      } catch(OMPThreadSet::CannotStartException &ex) {
        LOG_ERROR_STR("Killed reading thread too early. Fix test.");
      } catch(SystemCallException &ex) {
        LOG_INFO_STR("Caught exception: " << ex.what());

        if (ex.error == EINTR)
          success = true;
      }
    }

    #pragma omp section
    {
      sleep(1);

      packetReaderThread.killAll();
    }
  }

  CHECK(success);
}

int main()
{
  INIT_LOGGER("tPacketReader");

  return UnitTest::RunAllTests() > 0;
}

