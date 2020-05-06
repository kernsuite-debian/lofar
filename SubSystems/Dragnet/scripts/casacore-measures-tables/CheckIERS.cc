// CheckIERS program to find age of IERS tables.
//
// $Id$
//
// Program CheckIERS checks the last entry in the IERSpredict table and 
// compares this with the current day (all in MJD).
// The predict table should have entries for the coming period. If it only has
// entries in the past, the table is outdated.
//
// Usage: CheckIERS dir=<root dir of IERS tables>
// 
// Options: all: age of last entry in all IERS tables
//          verbose: Show readable text, instead of just numbers
//
// The root directory is default set to /localhome/IERS; the 
// default location for the IERS tables is in directory 'geodetic' under
// the IERS root directory. 
//
// If only the age of the table must be extracted, parse the output of this 
// program like this:
//
// > CheckIERS | tail -1 | awk '{print $6}'
//
// Author: A.P. Schoenmakers
//

#include <iostream>
#include <casacore/casa/Exceptions.h>
#include <casacore/casa/Inputs/Input.h>
#include <casacore/tables/Tables.h>
#include <casacore/casa/OS/Time.h>

using namespace casacore;

int main(int argc, char *argv[]) {
  try
  {
    Input inputs;
    inputs.version("");
    inputs.create("dir","/localhome/IERS","root dir of IERS (default: /localhome/IERS)","String");
    inputs.create("table","IERSpredict","IERS table to check","String");
    inputs.create("verbose","False","Verbose output","Bool","verbose");
    inputs.create("all","False","Use all IERS tables","Bool","all");
    inputs.readArguments(argc, argv);
    
    String dir = inputs.getString("dir");    
    String table = inputs.getString("table");
    Bool verbose = inputs.getBool("verbose");
    Bool all_tables = inputs.getBool("all");
    std::vector<String> tables;
    if (all_tables == True) {
      tables.push_back("IERSeop2000");
      tables.push_back("IERSeop97");
      tables.push_back("IERSpredict2000");
      tables.push_back("IERSpredict");
    } else {
      tables.push_back(table);
    }

    for (std::vector<String>::iterator it = tables.begin() ; it != tables.end(); ++it) {
      String fullname = dir + "/geodetic/" + *it;

      if (verbose) cout << "Checking table " << fullname << endl;
      Table ierstable(fullname);
    
      uint lastLine = ierstable.nrow();
      //cout << "Number of lines: " << lastLine << endl; 

      ROTableColumn MJDcol(ierstable,"MJD"); 

      int eopMJD = (int)MJDcol.asdouble(lastLine-1); 
      Time curMJDtime;
      int curMJD = (int)curMJDtime.modifiedJulianDay();
      if (verbose) {
	cout << "Current MJD is          : " << curMJD << endl;
	cout << "Last MJD in " << *it << " : " <<  eopMJD << endl;
	cout << "Nr of days remaining: " << eopMJD - curMJD << endl;
      } else {
	cout << eopMJD - curMJD << endl;
      }
    }
  }
  catch(AipsError& err)
    {
      cerr << "Aips++ error detected: " << err.getMesg() << endl;
      return 1;
    };
  
}
