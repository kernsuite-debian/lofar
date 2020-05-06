//# MSLofarAntennaColumns.h: provides easy access to LOFAR's MSAntenna columns
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

#ifndef MSLOFAR_MSLOFARANTENNACOLUMNS_H
#define MSLOFAR_MSLOFARANTENNACOLUMNS_H

#include <casacore/ms/MeasurementSets/MSAntennaColumns.h>

namespace LOFAR {

  //# Forward Declaration
  class MSLofarAntenna;

  // This class provides read-only access to the columns in the MSLofarAntenna
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSLofarAntennaColumns: public casacore::ROMSAntennaColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSLofarAntennaColumns(const MSLofarAntenna& msLofarAntenna);

    // The destructor does nothing special.
    ~ROMSLofarAntennaColumns();

    // Access to columns.
    // <group>
    const casacore::ROScalarColumn<casacore::Int>& stationId() const
      { return stationId_p; }
    const casacore::ROArrayColumn<casacore::Double>& phaseReference() const
      { return phaseReference_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& phaseReferenceQuant() const 
      { return phaseReferenceQuant_p; }
    const casacore::ROScalarMeasColumn<casacore::MPosition>& phaseReferenceMeas() const 
      { return phaseReferenceMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSLofarAntennaColumns();

    //# Attach this object to the supplied table.
    void attach (const MSLofarAntenna& msLofarAntenna);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSLofarAntennaColumns(const ROMSLofarAntennaColumns&);
    ROMSLofarAntennaColumns& operator=(const ROMSLofarAntennaColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::Int> stationId_p;
    casacore::ROArrayColumn<casacore::Double> phaseReference_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MPosition> phaseReferenceMeas_p;
    //# Access to Quantum columns
    casacore::ROArrayQuantColumn<casacore::Double> phaseReferenceQuant_p;
  };


  // This class provides read/write access to the columns in the MSLofarAntenna
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSLofarAntennaColumns: public casacore::MSAntennaColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSLofarAntennaColumns(MSLofarAntenna& msLofarAntenna);

    // The destructor does nothing special.
    ~MSLofarAntennaColumns();

    // Read-write access to required columns.
    // <group>
    const casacore::ROScalarColumn<casacore::Int>& stationId() const
      { return roStationId_p; }
    casacore::ScalarColumn<casacore::Int>& stationId()
      { return rwStationId_p; }
    const casacore::ROArrayColumn<casacore::Double>& phaseReference() const
      { return roPhaseReference_p; }
    casacore::ArrayColumn<casacore::Double>& phaseReference()
      { return rwPhaseReference_p; }
    const casacore::ROArrayQuantColumn<casacore::Double>& phaseReferenceQuant() const 
      { return roPhaseReferenceQuant_p; }
    casacore::ArrayQuantColumn<casacore::Double>& phaseReferenceQuant()
      { return rwPhaseReferenceQuant_p; }
    const casacore::ROScalarMeasColumn<casacore::MPosition>& phaseReferenceMeas() const
      { return roPhaseReferenceMeas_p; }
    casacore::ScalarMeasColumn<casacore::MPosition>& phaseReferenceMeas()
      { return rwPhaseReferenceMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSLofarAntennaColumns();

    //# Attach this object to the supplied table.
    void attach(MSLofarAntenna& msLofarAntenna);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSLofarAntennaColumns(const MSLofarAntennaColumns&);
    MSLofarAntennaColumns& operator=(const MSLofarAntennaColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::Int> roStationId_p;
    casacore::ScalarColumn<casacore::Int>   rwStationId_p;
    casacore::ROArrayColumn<casacore::Double> roPhaseReference_p;
    casacore::ArrayColumn<casacore::Double>   rwPhaseReference_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MPosition> roPhaseReferenceMeas_p;
    casacore::ScalarMeasColumn<casacore::MPosition>   rwPhaseReferenceMeas_p;
    //# Access to Quantum columns
    casacore::ROArrayQuantColumn<casacore::Double> roPhaseReferenceQuant_p;
    casacore::ArrayQuantColumn<casacore::Double>   rwPhaseReferenceQuant_p;
  };

} //# end namespace

#endif
