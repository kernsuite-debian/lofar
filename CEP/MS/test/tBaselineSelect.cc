//# tBaselineSelect.cc: Test for class BaselineSelect
//#
//# Copyright (C) 2010
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
//#  $Id: tBaselineSelect.cc 34753 2016-06-20 10:43:42Z schaap $

//# Includes
#include <MS/BaselineSelect.h>
#include <Common/LofarLogger.h>

#include <measures/Measures/MPosition.h>
#include <measures/Measures/MeasTable.h>
#include <casa/Arrays/ArrayIO.h>
#include <casa/BasicSL/STLIO.h>
#include <iostream>

using namespace LOFAR;
using namespace casa;
using namespace std;

void testTemp()
{
  Vector<String> names(5);
  names[0] = "CS013HBA0";
  names[1] = "CS013HBA1";
  names[2] = "CS014HBA0";
  names[3] = "RS015";
  names[4] = "DE013";
  Vector<Int> a1(15);
  Vector<Int> a2(15);
  int inx=0;
  for (int i=0; i<5; ++i) {
    for (int j=i; j<5; ++j) {
      a1[inx] = i;
      a2[inx] = j;
      inx++;
    }
  }
  vector<MPosition> pos(5);
  ASSERT (MeasTable::Observatory (pos[0], "WSRT"));
  ASSERT (MeasTable::Observatory (pos[1], "WSRT"));
  ASSERT (MeasTable::Observatory (pos[2], "LOFAR"));
  ASSERT (MeasTable::Observatory (pos[3], "WSRT"));
  ASSERT (MeasTable::Observatory (pos[4], "LOFAR"));
  // Try a few selection strings.
  cout << BaselineSelect::convert (names, pos, a1, a2, "CS013HBA[01]", cout);
  cout << BaselineSelect::convert (names, pos, a1, a2, "CS013HBA[23]", cout);
  cout << BaselineSelect::convert (names, pos, a1, a2, "CS*&&[CR]S*", cout);
  cout << BaselineSelect::convert (names, pos, a1, a2, "<10000", cout);
}

int main(int argc, char* argv[])
{
  try {
    if (argc == 1) {
      testTemp();
    } else if (argc < 3) {
      cout << "Run as:  tBaselineSelect msname expr" << endl;
      return 0;
    } else {
      cout << BaselineSelect::convert (argv[1], argv[2], cout);
    }
  } catch (exception& x) {
    cout << "Unexpected expection: " << x.what() << endl;
    return 1;
  }
  return 0;
}
