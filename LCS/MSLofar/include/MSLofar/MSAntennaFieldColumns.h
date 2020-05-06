//# MSAntennaFieldColumns.h: provides easy access to MSAntennaField columns
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

#ifndef MSLOFAR_MSANTENNAFIELDCOLUMNS_H
#define MSLOFAR_MSANTENNAFIELDCOLUMNS_H

#include <casacore/casa/aips.h>
#include <casacore/measures/Measures/MPosition.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/TableMeasures/ArrayMeasColumn.h>
#include <casacore/measures/TableMeasures/ArrayQuantColumn.h>
#include <casacore/measures/TableMeasures/ScalarMeasColumn.h>
#include <casacore/measures/TableMeasures/ScalarQuantColumn.h>
#include <casacore/tables/Tables/ArrayColumn.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/casa/BasicSL/String.h>

namespace LOFAR {

  //# Forward Declaration
  class MSAntennaField;

  // This class provides read-only access to the columns in the MSAntennaField
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSAntennaFieldColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSAntennaFieldColumns(const MSAntennaField& msAntennaField);

    // The destructor does nothing special.
    ~ROMSAntennaFieldColumns();

    // Access to columns.
    // <group>
    const casacore::ROScalarColumn<casacore::Int>& antennaId() const
      { return antennaId_p; }
    const casacore::ROScalarColumn<casacore::String>& name() const
      { return name_p; }
    const casacore::ROArrayColumn<casacore::Double>& position() const
      { return position_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& positionQuant() const 
      { return positionQuant_p; }
    const casacore::ROScalarMeasColumn<casacore::MPosition>& positionMeas() const 
      { return positionMeas_p; }
    const casacore::ROArrayColumn<casacore::Double>& coordinateAxes() const
      { return coordinateAxes_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& coordinateaxesQuant() const 
      { return coordinateAxesQuant_p; }
    const casacore::ROArrayColumn<casacore::Double>& elementOffset() const
      { return elementOffset_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& elementOffsetQuant() const 
      { return elementOffsetQuant_p; }
    const casacore::ROArrayColumn<casacore::Int>& elementRCU() const
      { return elementRCU_p; }
    const casacore::ROArrayColumn<casacore::Bool>& elementFlag() const
      { return elementFlag_p; }
    const casacore::ROScalarColumn<casacore::Double>& tileRotation() const
      { return tileRotation_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& tileRotationQuant() const 
      { return tileRotationQuant_p; }
    const casacore::ROArrayColumn<casacore::Double>& tileElementOffset() const
      { return tileElementOffset_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& tileElementOffsetQuant() const 
      { return tileElementOffsetQuant_p; }
    // </group>

    // Convenience function that returns the number of rows
    // in any of the columns.
    casacore::uInt nrow() const
      { return antennaId_p.nrow(); }

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSAntennaFieldColumns();

    //# Attach this object to the supplied table.
    void attach (const MSAntennaField& msAntennaField);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSAntennaFieldColumns(const ROMSAntennaFieldColumns&);
    ROMSAntennaFieldColumns& operator=(const ROMSAntennaFieldColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::Int> antennaId_p;
    casacore::ROScalarColumn<casacore::String> name_p;
    casacore::ROArrayColumn<casacore::Double> position_p;
    casacore::ROArrayColumn<casacore::Double> coordinateAxes_p;
    casacore::ROArrayColumn<casacore::Double> elementOffset_p;
    casacore::ROArrayColumn<casacore::Int> elementRCU_p;
    casacore::ROArrayColumn<casacore::Bool> elementFlag_p;
    casacore::ROScalarColumn<casacore::Double> tileRotation_p;
    casacore::ROArrayColumn<casacore::Double> tileElementOffset_p;

    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MPosition> positionMeas_p;

    //# Access to Quantum columns
    casacore::ROArrayQuantColumn<casacore::Double> positionQuant_p;
    casacore::ROArrayQuantColumn<casacore::Double> coordinateAxesQuant_p;
    casacore::ROArrayQuantColumn<casacore::Double> elementOffsetQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> tileRotationQuant_p;
    casacore::ROArrayQuantColumn<casacore::Double> tileElementOffsetQuant_p;
  };


  // This class provides read/write access to the columns in the MSAntennaField
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSAntennaFieldColumns: public ROMSAntennaFieldColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSAntennaFieldColumns(MSAntennaField& msAntennaField);

    // The destructor does nothing special.
    ~MSAntennaFieldColumns();

    // Read-write access to required columns.
    // <group>
    casacore::ScalarColumn<casacore::Int>& antennaId()
      { return antennaId_p; }
    casacore::ScalarColumn<casacore::String>& name()
      { return name_p; }
    casacore::ArrayColumn<casacore::Double>& position()
      { return position_p; }
    casacore::ArrayQuantColumn<casacore::Double>& positionQuant() 
      { return positionQuant_p; }
    casacore::ScalarMeasColumn<casacore::MPosition>& positionMeas() 
      { return positionMeas_p; }
    casacore::ArrayColumn<casacore::Double>& coordinateAxes()
      { return coordinateAxes_p; }
    casacore::ArrayQuantColumn<casacore::Double>& coordinateaxesQuant() 
      { return coordinateAxesQuant_p; }
    casacore::ArrayColumn<casacore::Double>& elementOffset()
      { return elementOffset_p; }
    casacore::ArrayQuantColumn<casacore::Double>& elementOffsetQuant()
      { return elementOffsetQuant_p; }
    casacore::ArrayColumn<casacore::Int>& elementRCU()
      { return elementRCU_p; }
    casacore::ArrayColumn<casacore::Bool>& elementFlag()
      { return elementFlag_p; }
    casacore::ScalarColumn<casacore::Double>& tileRotation()
      { return tileRotation_p; }
    casacore::ScalarQuantColumn<casacore::Double>& tileRotationQuant() 
      { return tileRotationQuant_p; }
    casacore::ArrayColumn<casacore::Double>& tileElementOffset()
      { return tileElementOffset_p; }
    casacore::ArrayQuantColumn<casacore::Double>& tileElementOffsetQuant() 
      { return tileElementOffsetQuant_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSAntennaFieldColumns();

    //# Attach this object to the supplied table.
    void attach(MSAntennaField& msAntennaField);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSAntennaFieldColumns(const MSAntennaFieldColumns&);
    MSAntennaFieldColumns& operator=(const MSAntennaFieldColumns&);

    //# required columns
    casacore::ScalarColumn<casacore::Int> antennaId_p;
    casacore::ScalarColumn<casacore::String> name_p;
    casacore::ArrayColumn<casacore::Double> position_p;
    casacore::ArrayColumn<casacore::Double> coordinateAxes_p;
    casacore::ArrayColumn<casacore::Double> elementOffset_p;
    casacore::ArrayColumn<casacore::Int> elementRCU_p;
    casacore::ArrayColumn<casacore::Bool> elementFlag_p;
    casacore::ScalarColumn<casacore::Double> tileRotation_p;
    casacore::ArrayColumn<casacore::Double> tileElementOffset_p;

    //# Access to Measure columns
    casacore::ScalarMeasColumn<casacore::MPosition> positionMeas_p;

    //# Access to Quantum columns
    casacore::ArrayQuantColumn<casacore::Double> positionQuant_p;
    casacore::ArrayQuantColumn<casacore::Double> coordinateAxesQuant_p;
    casacore::ArrayQuantColumn<casacore::Double> elementOffsetQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> tileRotationQuant_p;
    casacore::ArrayQuantColumn<casacore::Double> tileElementOffsetQuant_p;
  };

} //# end namespace

#endif
