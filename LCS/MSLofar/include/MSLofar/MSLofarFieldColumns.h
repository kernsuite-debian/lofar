//# MSLofarFieldColumns.h: provides easy access to LOFAR's MSField columns
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

#ifndef MSLOFAR_MSLOFARFIELDCOLUMNS_H
#define MSLOFAR_MSLOFARFIELDCOLUMNS_H

#include <casacore/ms/MeasurementSets/MSFieldColumns.h>

namespace LOFAR {

  //# Forward Declaration
  class MSLofarField;

  // This class provides read-only access to the columns in the MSLofarField
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSLofarFieldColumns: public casacore::ROMSFieldColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSLofarFieldColumns(const MSLofarField& msLofarField);

    // The destructor does nothing special.
    ~ROMSLofarFieldColumns();

    // Access to columns.
    // <group>
    const casacore::ROArrayColumn<casacore::Double>& tileBeamDir() const
      { return tileBeamDir_p; }
    const casacore::ROScalarMeasColumn<casacore::MDirection>& tileBeamDirMeasCol() const
      { return tileBeamDirMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSLofarFieldColumns();

    //# Attach this object to the supplied table.
    void attach (const MSLofarField& msLofarField);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSLofarFieldColumns(const ROMSLofarFieldColumns&);
    ROMSLofarFieldColumns& operator=(const ROMSLofarFieldColumns&);

    //# required columns
    casacore::ROArrayColumn<casacore::Double> tileBeamDir_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MDirection> tileBeamDirMeas_p;
  };


  // This class provides read/write access to the columns in the MSLofarField
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSLofarFieldColumns: public casacore::MSFieldColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSLofarFieldColumns(MSLofarField& msLofarField);

    // The destructor does nothing special.
    ~MSLofarFieldColumns();

    // Read-write access to required columns.
    // <group>
    const casacore::ROArrayColumn<casacore::Double>& tileBeamDir() const
      { return roTileBeamDir_p; }
    casacore::ArrayColumn<casacore::Double>& tileBeamDir()
      { return rwTileBeamDir_p; }
    const casacore::ROScalarMeasColumn<casacore::MDirection>& tileBeamDirMeasCol() const
      { return roTileBeamDirMeas_p; }
    casacore::ScalarMeasColumn<casacore::MDirection>& tileBeamDirMeasCol()
      { return rwTileBeamDirMeas_p; }
    // </group>

    // Set the direction reference type for all direction columns.
    // This can only be done when the table has no rows.
    // Trying to do so at other times will throw an exception.
    void setDirectionRef(casacore::MDirection::Types ref);

    // Same as above, but the LOFAR_TILE_BEAM_DIR can have a different type.
    void setDirectionRef(casacore::MDirection::Types ref,
                         casacore::MDirection::Types tileBeamDirRef);

    // Set the direction offset for all direction columns.
    // This can only be done when the table has no rows.
    // Trying to do so at other times will throw an exception.
    ///  void setDirectionOffset(const MDirection& offset);

    // Same as above, but the LOFAR_TILE_BEAM_DIR can have a different offset.
    ///  void setDirectionOffset(const MDirection& offset,
    ///  const MDirection& tileBeamDirOffset);


  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSLofarFieldColumns();

    //# Attach this object to the supplied table.
    void attach(MSLofarField& msLofarField);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSLofarFieldColumns(const MSLofarFieldColumns&);
    MSLofarFieldColumns& operator=(const MSLofarFieldColumns&);

    //# required columns
    casacore::ROArrayColumn<casacore::Double> roTileBeamDir_p;
    casacore::ArrayColumn<casacore::Double>   rwTileBeamDir_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MDirection> roTileBeamDirMeas_p;
    casacore::ScalarMeasColumn<casacore::MDirection>   rwTileBeamDirMeas_p;
  };

} //# end namespace

#endif
