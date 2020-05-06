//# tMeasurementSetFormat.cc: Test program for class MeasurementSetFormat
//# Copyright (C) 2011-2013  ASTRON (Netherlands Institute for Radio Astronomy)
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
#include <cstdio>

#include <Common/LofarLogger.h>
#include <Common/Exception.h>
#include <OutputProc/MeasurementSetFormat.h>

#include <casacore/casa/IO/RegularFileIO.h>
#include <casacore/tables/Tables.h>
#include <UnitTest++.h>
#include <boost/format.hpp>

using namespace LOFAR;
using namespace LOFAR::Cobalt;
using namespace casacore;
using namespace std;

// Define handler that tries to print a backtrace.
Exception::TerminateHandler t(Exception::terminate);

// create a MS using settings for subband 0 from a parset
void createMS(const string &parsetName, const string &msName)
{
  Parset parset(parsetName);
  MeasurementSetFormat msf(parset);
  msf.addSubband(msName, 0);

  // Also create the data file, otherwise it is not a true table.
  RegularFileIO file(String(msName + "/table.f0data"),
                     ByteIO::New);
}

string getMeasInfoRef(const string &msName)
{
  TableDesc desc;
  Table::getLayout(desc, msName);
  ColumnDesc &col(desc.rwColumnDesc("UVW"));
  TableRecord rec = col.keywordSet().asRecord("MEASINFO");

  String ref;
  rec.get("Ref", ref);

  return ref;
}

TEST(J2000)
{
  const string parsetName = "tMeasurementSetFormat.parset-j2000";
  const string msName = "tMeasurementSetFormat_tmp-j2000.MS";

  LOG_DEBUG_STR("Testing " << parsetName);
  createMS(parsetName, msName);

  CHECK_EQUAL("J2000", getMeasInfoRef(msName));
}

TEST(SUN)
{
  const string parsetName = "tMeasurementSetFormat.parset-sun";
  const string msName = "tMeasurementSetFormat_tmp-sun.MS";

  LOG_DEBUG_STR("Testing " << parsetName);
  createMS(parsetName, msName);

  CHECK_EQUAL("SUN", getMeasInfoRef(msName));
}


int main()
{
  INIT_LOGGER("tMeasurementSetFormat");

  return UnitTest::RunAllTests() > 0;
}

