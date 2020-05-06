//# MSMriterFile.h: raw file writer implementation of MSWriter
//# Copyright (C) 2009-2013  ASTRON (Netherlands Institute for Radio Astronomy)
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

#ifndef LOFAR_STORAGE_MSWRITERFILE_H
#define LOFAR_STORAGE_MSWRITERFILE_H

// O_DIRECT gave us bad performance on CEP4. Compare:
/*

root@cpu01 ~]# dd if=/dev/zero of=/data/test/throughput.dd bs=104857600 count=10 oflag=direct
10+0 records in
10+0 records out
1048576000 bytes (1.0 GB) copied, 60.8431 s, 17.2 MB/s

[root@cpu01 ~]# dd if=/dev/zero of=/data/test/throughput.dd bs=104857600 count=10
10+0 records in
10+0 records out
1048576000 bytes (1.0 GB) copied, 0.879391 s, 1.2 GB/s

*/
//#define USE_O_DIRECT

#ifdef USE_O_DIRECT
#include "FastFileStream.h"
#else
#include <Stream/FileStream.h>
#endif

#include <string>

#include <Common/Thread/Mutex.h>
#include <CoInterface/StreamableData.h>
#include "MSWriter.h"

namespace LOFAR
{
  namespace Cobalt
  {


    class MSWriterFile : public MSWriter
    {
    public:
      /*
       * Write data to the provided file name.
       *
       * Any parent directories are automatically created.
       */
      MSWriterFile(const std::string &msName);
      ~MSWriterFile();

      virtual void write(StreamableData *data);

      virtual size_t getDataSize();

    protected:
#ifdef USE_O_DIRECT
      FastFileStream itsFile;
#else
      FileStream itsFile;
#endif

      /* create a directory as well as all its parent directories */
      static void recursiveMakeDir(const string &dirname, const string &logPrefix);

    private:
      static Mutex makeDirMutex;

      static void makeDir(const string &dirname, const string &logPrefix);
    };


  }
}

#endif

