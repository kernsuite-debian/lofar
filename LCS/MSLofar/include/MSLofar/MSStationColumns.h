//# MSStationColumns.h: provides easy access to MSStation columns
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
//# $Id$
//#
//# @author Ger van Diepen

#ifndef MSLOFAR_MSSTATIONCOLUMNS_H
#define MSLOFAR_MSSTATIONCOLUMNS_H

#include <casacore/casa/aips.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/casa/BasicSL/String.h>

namespace LOFAR {

  //# Forward Declaration
  class MSStation;

  // This class provides read-only access to the columns in the MSStation
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSStationColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSStationColumns(const MSStation& msStation);

    // The destructor does nothing special.
    ~ROMSStationColumns();

    // Access to columns.
    // <group>
    casacore::ROScalarColumn<casacore::String>& name()
      { return name_p; }
    casacore::ROScalarColumn<casacore::Int>& clockId()
      { return clockId_p; }
    casacore::ROScalarColumn<casacore::Bool>& flagRow()
      { return flagRow_p; }
    // </group>

    // Convenience function that returns the number of rows
    // in any of the columns.
    casacore::uInt nrow() const
      { return name_p.nrow(); }

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSStationColumns();

    //# Attach this object to the supplied table.
    void attach (const MSStation& msStation);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSStationColumns(const ROMSStationColumns&);
    ROMSStationColumns& operator=(const ROMSStationColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::String> name_p;
    casacore::ROScalarColumn<casacore::Int>    clockId_p;
    casacore::ROScalarColumn<casacore::Bool>   flagRow_p;
  };


  // This class provides read/write access to the columns in the MSStation
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSStationColumns: public ROMSStationColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSStationColumns(MSStation& msStation);

    // The destructor does nothing special.
    ~MSStationColumns();

    // Read-write access to required columns.
    // <group>
    casacore::ScalarColumn<casacore::String>& name()
      { return name_p; }
    casacore::ScalarColumn<casacore::Int>& clockId()
      { return clockId_p; }
    casacore::ScalarColumn<casacore::Bool>& flagRow()
      { return flagRow_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSStationColumns();

    //# Attach this object to the supplied table.
    void attach(MSStation& msStation);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSStationColumns(const MSStationColumns&);
    MSStationColumns& operator=(const MSStationColumns&);

    //# required columns
    casacore::ScalarColumn<casacore::String> name_p;
    casacore::ScalarColumn<casacore::Int>    clockId_p;
    casacore::ScalarColumn<casacore::Bool>   flagRow_p;

  };

} //# end namespace

#endif
