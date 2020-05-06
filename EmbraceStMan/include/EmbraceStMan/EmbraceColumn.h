//# EmbraceColumn.h: A Column in the EMBRACE Storage Manager
//# Copyright (C) 2009
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

#ifndef EMBRACE_EMBRACESTMAN_EMBRACECOLUMN_H
#define EMBRACE_EMBRACESTMAN_EMBRACECOLUMN_H


//# Includes
#include <EmbraceStMan/EmbraceStMan.h>
#include <Common/lofar_vector.h>
#include <casacore/tables/DataMan/StManColumn.h>
#include <casacore/measures/Measures/MeasFrame.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MBaseline.h>
#include <casacore/casa/Arrays/Vector.h>
#include <casacore/casa/Arrays/IPosition.h>
#include <casacore/casa/Containers/Block.h>
#include <casacore/casa/OS/Conversion.h>

namespace EMBRACE {

// <summary>
// A column in the EMBRACE Storage Manager.
// </summary>

// <use visibility=local>

// <reviewed reviewer="UNKNOWN" date="before2004/08/25" tests="tEmbraceStMan.cc">
// </reviewed>

// <prerequisite>
//# Classes you should understand before using this one.
//   <li> <linkto class=EmbraceStMan>EmbraceStMan</linkto>
// </prerequisite>

// <synopsis>
// For each column a specific Column class exists.
// </synopsis>

class EmbraceColumn : public casacore::StManColumn
{
public:
  explicit EmbraceColumn (EmbraceStMan* parent, int dtype)
    : StManColumn (dtype),
      itsParent   (parent)
  {}
  virtual ~EmbraceColumn();
  // Most columns are not writable (only DATA is writable).
  virtual casacore::Bool isWritable() const;
  // Set column shape of fixed shape columns; it does nothing.
  virtual void setShapeColumn (const casacore::IPosition& shape);
  // Prepare the column. By default it does nothing.
  virtual void prepareCol();
protected:
  EmbraceStMan* itsParent;
};

// <summary>ANTENNA1 column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class Ant1Column : public EmbraceColumn
{
public:
  explicit Ant1Column (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~Ant1Column();
  virtual void getIntV (casacore::uInt rowNr, casacore::Int* dataPtr);
};

// <summary>ANTENNA2 column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class Ant2Column : public EmbraceColumn
{
public:
  explicit Ant2Column (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~Ant2Column();
  virtual void getIntV (casacore::uInt rowNr, casacore::Int* dataPtr);
};

// <summary>TIME and TIME_CENTROID column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class TimeColumn : public EmbraceColumn
{
public:
  explicit TimeColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~TimeColumn();
  virtual void getdoubleV (casacore::uInt rowNr, casacore::Double* dataPtr);
private:
  casacore::Double itsValue;
};

// <summary>INTERVAL and EXPOSURE column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class IntervalColumn : public EmbraceColumn
{
public:
  explicit IntervalColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~IntervalColumn();
  virtual void getdoubleV (casacore::uInt rowNr, casacore::Double* dataPtr);
private:
  casacore::Double itsValue;
};

// <summary>All columns in the EMBRACE Storage Manager with value 0.</summary>
// <use visibility=local>
class ZeroColumn : public EmbraceColumn
{
public:
  explicit ZeroColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~ZeroColumn();
  virtual void getIntV (casacore::uInt rowNr, casacore::Int* dataPtr);
private:
  casacore::Int itsValue;
};

// <summary>All columns in the EMBRACE Storage Manager with value False.</summary>
// <use visibility=local>
class FalseColumn : public EmbraceColumn
{
public:
  explicit FalseColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~FalseColumn();
  virtual void getBoolV (casacore::uInt rowNr, casacore::Bool* dataPtr);
private:
  casacore::Bool itsValue;
};

// <summary>UVW column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class UvwColumn : public EmbraceColumn
{
public:
  explicit UvwColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~UvwColumn();
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArraydoubleV (casacore::uInt rowNr,
                                casacore::Array<casacore::Double>* dataPtr);
  virtual void prepareCol();
private:
  casacore::MDirection              itsPhaseDir;    //# could be SUN, etc.
  casacore::MDirection              itsJ2000Dir;    //# Phase dir in J2000
  casacore::MeasFrame               itsFrame;
  vector<casacore::MBaseline>       itsAntMB;
  vector<casacore::Vector<double> > itsAntUvw;
  casacore::Block<bool>             itsUvwFilled;
  int                           itsLastBlNr;
  bool                          itsCanCalc;     //# false = UVW cannot be calc.
};

// <summary>DATA column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class DataColumn : public EmbraceColumn
{
public:
  explicit DataColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~DataColumn();
  virtual casacore::Bool isWritable() const;
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArrayComplexV (casacore::uInt rowNr,
                                 casacore::Array<casacore::Complex>* dataPtr);
  virtual void putArrayComplexV (casacore::uInt rowNr,
                                 const casacore::Array<casacore::Complex>* dataPtr);
};

// <summary>FLAG column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class FlagColumn : public EmbraceColumn
{
public:
  explicit FlagColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~FlagColumn();
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArrayBoolV (casacore::uInt rowNr,
                              casacore::Array<casacore::Bool>* dataPtr);
};

// <summary>WEIGHT column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class WeightColumn : public EmbraceColumn
{
public:
  explicit WeightColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~WeightColumn();
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArrayfloatV (casacore::uInt rowNr,
                               casacore::Array<casacore::Float>* dataPtr);
};

// <summary>SIGMA column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class SigmaColumn : public EmbraceColumn
{
public:
  explicit SigmaColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~SigmaColumn();
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArrayfloatV (casacore::uInt rowNr,
                               casacore::Array<casacore::Float>* dataPtr);
};

// <summary>WEIGHT_SPECTRUM column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class WSpectrumColumn : public EmbraceColumn
{
public:
  explicit WSpectrumColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~WSpectrumColumn();
  virtual casacore::IPosition shape (casacore::uInt rownr);
  virtual void getArrayfloatV (casacore::uInt rowNr,
                               casacore::Array<casacore::Float>* dataPtr);
};

// <summary>FLAG_CATEGORY column in the EMBRACE Storage Manager.</summary>
// <use visibility=local>
class FlagCatColumn : public EmbraceColumn
{
public:
  explicit FlagCatColumn (EmbraceStMan* parent, int dtype)
    : EmbraceColumn(parent, dtype) {}
  virtual ~FlagCatColumn();
  virtual casacore::Bool isShapeDefined (casacore::uInt rownr);
  virtual casacore::IPosition shape (casacore::uInt rownr);
};


} //# end namespace

#endif
