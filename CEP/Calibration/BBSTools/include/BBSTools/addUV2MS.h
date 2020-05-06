//# addUV2MS.h: header file of addUV2MS tool
//# adds uv data from a (casa) MS file to a named column of another (LOFAR) MS
//#
//# Copyright (C) 2011
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
//# $Id: addUV2MS.h xxxx 2011-10-21 14:16:37Z duscha $


#ifndef LOFAR_BBSTOOLS_ADDUV2MS_H
#define LOFAR_BBSTOOLS_ADDUV2MS_H

#include <vector>
#include <string>
#include <map>
#include <casacore/casa/Arrays/Vector.h>
#include <synthesis/MeasurementEquations/Imager.h>          // casarest ft()

void parseOptions(const std::vector<std::string> &arguments,
                  std::string &msName,
                  casacore::Vector<casacore::String> &patchNames, 
                  unsigned int &nwplanes);
casacore::MDirection getPatchDirection(const std::string &patchName);
void addDirectionKeyword( casacore::Table LofarMS, 
                          const std::string &patchName);
void addChannelSelectionKeyword(casacore::Table &LofarTable, 
                                const std::string &columnName);
string createColumnName(const casacore::String &);
void removeExistingColumns( const std::string &MSfilename, 
                            const casacore::Vector<casacore::String> &patchNames);
void addImagerColumns (casacore::MeasurementSet& ms);
void addModelColumn ( casacore::MeasurementSet &ms, 
                      const casacore::String &dataManName);
casacore::Double getMSReffreq(const casacore::MeasurementSet &ms);
casacore::Double getMSChanwidth(const casacore::MeasurementSet &ms);
std::map<string, double>  patchFrequency(casacore::MeasurementSet &ms,
                                    const casacore::Vector<casacore::String> &patchNames);
bool validModelImage(const casacore::String &imageName, std::string &error);
unsigned int makeTempImages(const casacore::Vector<casacore::String> &patchNames, 
                            const std::string &prefix="tmp");
unsigned int removeTempImages(const casacore::Vector<casacore::String> &patchNames, 
                              const std::string &prefix="tmp");
double updateFrequency(const std::string &imageName, 
                      double reffreq);
void restoreFrequency(const std::map<std::string, 
                      double> &refFrequencies);
void getImageOptions( const std::string &patchName,
                      unsigned int &imSizeX, unsigned int &imSizeY, 
                      casacore::Quantity &cellSizeX, casacore::Quantity &cellSizeY, 
                      unsigned int &nchan, unsigned int &npol, std::string &stokes);

//--------------------------------------------------------------
// Function declarations (debug functions)
//
casacore::Vector<casacore::String> getColumnNames(const casacore::Table &table);
void showColumnNames(casacore::Table &table);
void usage(const std::string &);

void showVector(const std::vector<std::string> &v, const std::string &key="");

#endif
