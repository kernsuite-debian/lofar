//# MSElementFailureColumns.h: provides easy access to MSElementFailure columns
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

#ifndef MSLOFAR_MSELEMENTFAILURECOLUMNS_H
#define MSLOFAR_MSELEMENTFAILURECOLUMNS_H

#include <casacore/casa/aips.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MCEpoch.h>
#include <casacore/measures/TableMeasures/ScalarMeasColumn.h>
#include <casacore/measures/TableMeasures/ScalarQuantColumn.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/casa/BasicSL/String.h>

namespace LOFAR {

  //# Forward Declaration
  class MSElementFailure;

  // This class provides read-only access to the columns in the MSElementFailure
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSElementFailureColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSElementFailureColumns(const MSElementFailure& msElementFailure);

    // The destructor does nothing special.
    ~ROMSElementFailureColumns();

    // Access to columns.
    // <group>
    const casacore::ROScalarColumn<casacore::Int>& antennaFieldId() const
      { return antennaFieldId_p; }
    const casacore::ROScalarColumn<casacore::Int>& elementIndex() const
      { return elementIndex_p; }
    const casacore::ROScalarColumn<casacore::Double>& time() const
      { return time_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& timeQuant() const 
      { return timeQuant_p; }
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& timeMeas() const
      { return timeMeas_p; }
    // </group>

    // Convenience function that returns the number of rows
    // in any of the columns.
    casacore::uInt nrow() const
      { return antennaFieldId_p.nrow(); }

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSElementFailureColumns();

    //# Attach this object to the supplied table.
    void attach (const MSElementFailure& msElementFailure);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSElementFailureColumns(const ROMSElementFailureColumns&);
    ROMSElementFailureColumns& operator=(const ROMSElementFailureColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::Int> antennaFieldId_p;
    casacore::ROScalarColumn<casacore::Int> elementIndex_p;
    casacore::ROScalarColumn<casacore::Double> time_p;

    //# Access to Quantum columns
    casacore::ROScalarQuantColumn<casacore::Double> timeQuant_p;

    //# Access to Quantum columns
    casacore::ROScalarMeasColumn<casacore::MEpoch> timeMeas_p;
  };


  // This class provides read/write access to the columns in the MSElementFailure
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSElementFailureColumns: public ROMSElementFailureColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSElementFailureColumns(MSElementFailure& msElementFailure);

    // The destructor does nothing special.
    ~MSElementFailureColumns();

    // Read-write access to required columns.
    // <group>
    casacore::ScalarColumn<casacore::Int>& antennaFieldId()
      { return antennaFieldId_p; }
    casacore::ScalarColumn<casacore::Int>& elementIndex()
      { return elementIndex_p; }
    casacore::ScalarColumn<casacore::Double>& time()
      { return time_p; }
    casacore::ScalarQuantColumn<casacore::Double>& timeQuant() 
      { return timeQuant_p; }
    casacore::ScalarMeasColumn<casacore::MEpoch>& timeMeas()
      { return timeMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSElementFailureColumns();

    //# Attach this object to the supplied table.
    void attach (MSElementFailure& msElementFailure);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSElementFailureColumns (const MSElementFailureColumns&);
    MSElementFailureColumns& operator= (const MSElementFailureColumns&);

    //# required columns
    casacore::ScalarColumn<casacore::Int> antennaFieldId_p;
    casacore::ScalarColumn<casacore::Int> elementIndex_p;
    casacore::ScalarColumn<casacore::Double> time_p;

    //# Access to Quantum columns
    casacore::ScalarQuantColumn<casacore::Double> timeQuant_p;

    //# Access to Quantum columns
    casacore::ScalarMeasColumn<casacore::MEpoch> timeMeas_p;
  };

} //# end namespace

#endif
