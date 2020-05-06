//# tRSPRawSender.cc
//# Copyright (C) 2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#include <omp.h>

#include <Common/LofarLogger.h>
#include <GPUProc/Station/RSPRawSender.h>

using namespace LOFAR;
using namespace LOFAR::Cobalt;
using namespace std;

static bool doSender(void)
{
//TODO RSPRawSender sender(...);

  return true;
}

static bool doReceiver(void)
{

  return true;
}

static bool runTest(void)
{
  bool senderStatus;
  bool receiverStatus;

  // create sender and receiver in separate threads for easy testing
# pragma omp parallel sections num_threads(2)
  {
#   pragma omp section
    {
      senderStatus = doSender();
    }

#   pragma omp section
    {
      receiverStatus = doReceiver();
    }
  }

  return senderStatus && receiverStatus;
}

int main(void)
{
  INIT_LOGGER("tRSPRawSender");

  bool status = runTest();

  return !status;
}

