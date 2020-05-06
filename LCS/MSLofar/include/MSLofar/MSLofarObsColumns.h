//# MSLofarObsColumns.h: provides easy access to LOFAR's MSObservation columns
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

#ifndef MSLOFAR_MSLOFAROBSCOLUMNS_H
#define MSLOFAR_MSLOFAROBSCOLUMNS_H

#include <casacore/ms/MeasurementSets/MSObsColumns.h>

namespace LOFAR {

  //# Forward Declaration
  class MSLofarObservation;

  // This class provides read-only access to the columns in the MSLofarObservation
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to worry about
  // getting those right. There is an access function for every predefined
  // column. Access to non-predefined columns will still have to be done with
  // explicit declarations.

  class ROMSLofarObservationColumns: public casacore::ROMSObservationColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    ROMSLofarObservationColumns(const MSLofarObservation& msLofarObservation);

    // The destructor does nothing special.
    ~ROMSLofarObservationColumns();

    // Access to columns.
    // <group>
    const casacore::ROScalarColumn<casacore::String>& projectTitle() const
      { return projectTitle_p; }
    const casacore::ROScalarColumn<casacore::String>& projectPI() const
      { return projectPI_p; }
    const casacore::ROArrayColumn<casacore::String>& projectCoI() const
      { return projectCoI_p; }
    const casacore::ROScalarColumn<casacore::String>& projectContact() const
      { return projectContact_p; }
    const casacore::ROScalarColumn<casacore::String>& observationId() const
      { return observationId_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationStart() const
      { return observationStart_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationEnd() const
      { return observationEnd_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyMax() const
      { return observationFrequencyMax_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyMin() const
      { return observationFrequencyMin_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyCenter() const
      { return observationFrequencyCenter_p; }
    const casacore::ROScalarColumn<casacore::Int>& subArrayPointing() const
      { return subArrayPointing_p; }
    const casacore::ROScalarColumn<casacore::Int>& nofBitsPerSample() const
      { return nofBitsPerSample_p; }
    const casacore::ROScalarColumn<casacore::String>& antennaSet() const
      { return antennaSet_p; }
    const casacore::ROScalarColumn<casacore::String>& filterSelection() const
      { return filterSelection_p; }
    const casacore::ROScalarColumn<casacore::Double>& clockFrequency() const
      { return clockFrequency_p; }
    const casacore::ROArrayColumn<casacore::String>& target() const
      { return target_p; }
    const casacore::ROScalarColumn<casacore::String>& systemVersion() const
      { return systemVersion_p; }
    const casacore::ROScalarColumn<casacore::String>& pipelineName() const
      { return pipelineName_p; }
    const casacore::ROScalarColumn<casacore::String>& pipelineVersion() const
      { return pipelineVersion_p; }
    const casacore::ROScalarColumn<casacore::String>& filename() const
      { return filename_p; }
    const casacore::ROScalarColumn<casacore::String>& filetype() const
      { return filetype_p; }
    const casacore::ROScalarColumn<casacore::Double>& filedate() const
      { return filedate_p; }
    // </group>

    // Access to Quantity columns
    // <group>
    const casacore::ROScalarQuantColumn<casacore::Double>& observationStartQuant() const 
      { return observationStartQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationEndQuant() const 
      { return observationEndQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyMaxQuant() const 
      { return observationFrequencyMaxQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyMinQuant() const 
      { return observationFrequencyMinQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& clockFrequencyQuant() const 
      { return clockFrequencyQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyCenterQuant() const 
      { return observationFrequencyCenterQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& filedateQuant() const 
      { return filedateQuant_p; }
    // </group>

    // Access to Measure columns
    // <group>
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& observationStartMeas() const 
      { return observationStartMeas_p; }
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& observationEndMeas() const 
      { return observationEndMeas_p; }
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& filedateMeas() const 
      { return filedateMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    ROMSLofarObservationColumns();

    //# Attach this object to the supplied table.
    void attach (const MSLofarObservation& msLofarObservation);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    ROMSLofarObservationColumns(const ROMSLofarObservationColumns&);
    ROMSLofarObservationColumns& operator=(const ROMSLofarObservationColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::String> projectTitle_p;
    casacore::ROScalarColumn<casacore::String> projectPI_p;
    casacore::ROArrayColumn<casacore::String>  projectCoI_p;
    casacore::ROScalarColumn<casacore::String> projectContact_p;
    casacore::ROScalarColumn<casacore::String> observationId_p;
    casacore::ROScalarColumn<casacore::Double> observationStart_p;
    casacore::ROScalarColumn<casacore::Double> observationEnd_p;
    casacore::ROScalarColumn<casacore::Double> observationFrequencyMax_p;
    casacore::ROScalarColumn<casacore::Double> observationFrequencyMin_p;
    casacore::ROScalarColumn<casacore::Double> observationFrequencyCenter_p;
    casacore::ROScalarColumn<casacore::Int>    subArrayPointing_p;
    casacore::ROScalarColumn<casacore::Int>    nofBitsPerSample_p;
    casacore::ROScalarColumn<casacore::String> antennaSet_p;
    casacore::ROScalarColumn<casacore::String> filterSelection_p;
    casacore::ROScalarColumn<casacore::Double> clockFrequency_p;
    casacore::ROArrayColumn<casacore::String>  target_p;
    casacore::ROScalarColumn<casacore::String> systemVersion_p;
    casacore::ROScalarColumn<casacore::String> pipelineName_p;
    casacore::ROScalarColumn<casacore::String> pipelineVersion_p;
    casacore::ROScalarColumn<casacore::String> filename_p;
    casacore::ROScalarColumn<casacore::String> filetype_p;
    casacore::ROScalarColumn<casacore::Double> filedate_p;
    //# Access to Quantum columns
    casacore::ROScalarQuantColumn<casacore::Double> observationStartQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> observationEndQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> observationFrequencyMaxQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> observationFrequencyMinQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> observationFrequencyCenterQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> clockFrequencyQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> filedateQuant_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MEpoch> observationStartMeas_p;
    casacore::ROScalarMeasColumn<casacore::MEpoch> observationEndMeas_p;
    casacore::ROScalarMeasColumn<casacore::MEpoch> filedateMeas_p;
  };


  // This class provides read/write access to the columns in the MSLofarObservation
  // Table. It does the declaration of all the Scalar and ArrayColumns with the
  // correct types, so the application programmer doesn't have to
  // worry about getting those right. There is an access function
  // for every predefined column. Access to non-predefined columns will still
  // have to be done with explicit declarations.

  class MSLofarObservationColumns: public casacore::MSObservationColumns
  {
  public:

    // Create a columns object that accesses the data in the specified Table.
    MSLofarObservationColumns(MSLofarObservation& msLofarObservation);

    // The destructor does nothing special.
    ~MSLofarObservationColumns();

    // Readonly access to columns.
    // <group>
    const casacore::ROScalarColumn<casacore::String>& projectTitle() const
      { return roProjectTitle_p; }
    const casacore::ROScalarColumn<casacore::String>& projectPI() const
      { return roProjectPI_p; }
    const casacore::ROArrayColumn<casacore::String>& projectCoI() const
      { return roProjectCoI_p; }
    const casacore::ROScalarColumn<casacore::String>& projectContact() const
      { return roProjectContact_p; }
    const casacore::ROScalarColumn<casacore::String>& observationId() const
      { return roObservationId_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationStart() const
      { return roObservationStart_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationEnd() const
      { return roObservationEnd_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyMax() const
      { return roObservationFrequencyMax_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyMin() const
      { return roObservationFrequencyMin_p; }
    const casacore::ROScalarColumn<casacore::Double>& observationFrequencyCenter() const
      { return roObservationFrequencyCenter_p; }
    const casacore::ROScalarColumn<casacore::Int>& subArrayPointing() const
      { return roSubArrayPointing_p; }
    const casacore::ROScalarColumn<casacore::Int>& nofBitsPerSample() const
      { return roNofBitsPerSample_p; }
    const casacore::ROScalarColumn<casacore::String>& antennaSet() const
      { return roAntennaSet_p; }
    const casacore::ROScalarColumn<casacore::String>& filterSelection() const
      { return roFilterSelection_p; }
    const casacore::ROScalarColumn<casacore::Double>& clockFrequency() const
      { return roClockFrequency_p; }
    const casacore::ROArrayColumn<casacore::String>& target() const
      { return roTarget_p; }
    const casacore::ROScalarColumn<casacore::String>& systemVersion() const
      { return roSystemVersion_p; }
    const casacore::ROScalarColumn<casacore::String>& pipelineName() const
      { return roPipelineName_p; }
    const casacore::ROScalarColumn<casacore::String>& pipelineVersion() const
      { return roPipelineVersion_p; }
    const casacore::ROScalarColumn<casacore::String>& filename() const
      { return roFilename_p; }
    const casacore::ROScalarColumn<casacore::String>& filetype() const
      { return roFiletype_p; }
    const casacore::ROScalarColumn<casacore::Double>& filedate() const
      { return roFiledate_p; }
    // </group>

    // Readonly access to Quantity columns
    // <group>
    const casacore::ROScalarQuantColumn<casacore::Double>& observationStartQuant() const 
      { return roObservationStartQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationEndQuant() const 
      { return roObservationEndQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyMaxQuant() const 
      { return roObservationFrequencyMaxQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyMinQuant() const 
      { return roObservationFrequencyMinQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& observationFrequencyCenterQuant() const 
      { return roObservationFrequencyCenterQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& clockFrequencyQuant() const 
      { return roClockFrequencyQuant_p; }
    const casacore::ROScalarQuantColumn<casacore::Double>& filedateQuant() const 
      { return roFiledateQuant_p; }
    // </group>

    // Readonly access to Measure columns
    // <group>
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& observationStartMeas() const 
      { return roObservationStartMeas_p; }
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& observationEndMeas() const 
      { return roObservationEndMeas_p; }
    const casacore::ROScalarMeasColumn<casacore::MEpoch>& filedateMeas() const 
      { return roFiledateMeas_p; }
    // </group>

    // Read/write access to columns.
    // <group>
    casacore::ScalarColumn<casacore::String>& projectTitle()
      { return rwProjectTitle_p; }
    casacore::ScalarColumn<casacore::String>& projectPI()
      { return rwProjectPI_p; }
    casacore::ArrayColumn<casacore::String>& projectCoI()
      { return rwProjectCoI_p; }
    casacore::ScalarColumn<casacore::String>& projectContact()
      { return rwProjectContact_p; }
    casacore::ScalarColumn<casacore::String>& observationId()
      { return rwObservationId_p; }
    casacore::ScalarColumn<casacore::Double>& observationStart()
      { return rwObservationStart_p; }
    casacore::ScalarColumn<casacore::Double>& observationEnd()
      { return rwObservationEnd_p; }
    casacore::ScalarColumn<casacore::Double>& observationFrequencyMax()
      { return rwObservationFrequencyMax_p; }
    casacore::ScalarColumn<casacore::Double>& observationFrequencyMin()
      { return rwObservationFrequencyMin_p; }
    casacore::ScalarColumn<casacore::Double>& observationFrequencyCenter()
      { return rwObservationFrequencyCenter_p; }
    casacore::ScalarColumn<casacore::Int>& subArrayPointing()
      { return rwSubArrayPointing_p; }
    casacore::ScalarColumn<casacore::Int>& nofBitsPerSample()
      { return rwNofBitsPerSample_p; }
    casacore::ScalarColumn<casacore::String>& antennaSet()
      { return rwAntennaSet_p; }
    casacore::ScalarColumn<casacore::String>& filterSelection()
      { return rwFilterSelection_p; }
    casacore::ScalarColumn<casacore::Double>& clockFrequency()
      { return rwClockFrequency_p; }
    casacore::ArrayColumn<casacore::String>& target()
      { return rwTarget_p; }
    casacore::ScalarColumn<casacore::String>& systemVersion()
      { return rwSystemVersion_p; }
    casacore::ScalarColumn<casacore::String>& pipelineName()
      { return rwPipelineName_p; }
    casacore::ScalarColumn<casacore::String>& pipelineVersion()
      { return rwPipelineVersion_p; }
    casacore::ScalarColumn<casacore::String>& filename()
      { return rwFilename_p; }
    casacore::ScalarColumn<casacore::String>& filetype()
      { return rwFiletype_p; }
    casacore::ScalarColumn<casacore::Double>& filedate()
      { return rwFiledate_p; }
    // </group>

    // Read/write access to Quantity columns
    // <group>
    casacore::ScalarQuantColumn<casacore::Double>& observationStartQuant() 
      { return rwObservationStartQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& observationEndQuant() 
      { return rwObservationEndQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& observationFrequencyMaxQuant() 
      { return rwObservationFrequencyMaxQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& observationFrequencyMinQuant() 
      { return rwObservationFrequencyMinQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& observationFrequencyCenterQuant() 
      { return rwObservationFrequencyCenterQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& clockFrequencyQuant() 
      { return rwClockFrequencyQuant_p; }
    casacore::ScalarQuantColumn<casacore::Double>& filedateQuant() 
      { return rwFiledateQuant_p; }
    // </group>

    // Read/write access to Measure columns
    // <group>
    casacore::ScalarMeasColumn<casacore::MEpoch>& observationStartMeas() 
      { return rwObservationStartMeas_p; }
    casacore::ScalarMeasColumn<casacore::MEpoch>& observationEndMeas() 
      { return rwObservationEndMeas_p; }
    casacore::ScalarMeasColumn<casacore::MEpoch>& filedateMeas() 
      { return rwFiledateMeas_p; }
    // </group>

  protected:
    //# Default constructor creates a object that is not usable. Use the attach
    //# function correct this.
    MSLofarObservationColumns();

    //# Attach this object to the supplied table.
    void attach(MSLofarObservation& msLofarObservation);

  private:
    //# Make the assignment operator and the copy constructor private to prevent
    //# any compiler generated one from being used.
    MSLofarObservationColumns(const MSLofarObservationColumns&);
    MSLofarObservationColumns& operator=(const MSLofarObservationColumns&);

    //# required columns
    casacore::ROScalarColumn<casacore::String> roProjectTitle_p;
    casacore::ROScalarColumn<casacore::String> roProjectPI_p;
    casacore::ROArrayColumn<casacore::String>  roProjectCoI_p;
    casacore::ROScalarColumn<casacore::String> roProjectContact_p;
    casacore::ROScalarColumn<casacore::String> roObservationId_p;
    casacore::ROScalarColumn<casacore::Double> roObservationStart_p;
    casacore::ROScalarColumn<casacore::Double> roObservationEnd_p;
    casacore::ROScalarColumn<casacore::Double> roObservationFrequencyMax_p;
    casacore::ROScalarColumn<casacore::Double> roObservationFrequencyMin_p;
    casacore::ROScalarColumn<casacore::Double> roObservationFrequencyCenter_p;
    casacore::ROScalarColumn<casacore::Int>    roSubArrayPointing_p;
    casacore::ROScalarColumn<casacore::Int>    roNofBitsPerSample_p;
    casacore::ROScalarColumn<casacore::String> roAntennaSet_p;
    casacore::ROScalarColumn<casacore::String> roFilterSelection_p;
    casacore::ROScalarColumn<casacore::Double> roClockFrequency_p;
    casacore::ROArrayColumn<casacore::String>  roTarget_p;
    casacore::ROScalarColumn<casacore::String> roSystemVersion_p;
    casacore::ROScalarColumn<casacore::String> roPipelineName_p;
    casacore::ROScalarColumn<casacore::String> roPipelineVersion_p;
    casacore::ROScalarColumn<casacore::String> roFilename_p;
    casacore::ROScalarColumn<casacore::String> roFiletype_p;
    casacore::ROScalarColumn<casacore::Double> roFiledate_p;
    //# Access to Quantum columns
    casacore::ROScalarQuantColumn<casacore::Double> roObservationStartQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roObservationEndQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roObservationFrequencyMaxQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roObservationFrequencyMinQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roObservationFrequencyCenterQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roClockFrequencyQuant_p;
    casacore::ROScalarQuantColumn<casacore::Double> roFiledateQuant_p;
    //# Access to Measure columns
    casacore::ROScalarMeasColumn<casacore::MEpoch> roObservationStartMeas_p;
    casacore::ROScalarMeasColumn<casacore::MEpoch> roObservationEndMeas_p;
    casacore::ROScalarMeasColumn<casacore::MEpoch> roFiledateMeas_p;
    //# required columns
    casacore::ScalarColumn<casacore::String> rwProjectTitle_p;
    casacore::ScalarColumn<casacore::String> rwProjectPI_p;
    casacore::ArrayColumn<casacore::String>  rwProjectCoI_p;
    casacore::ScalarColumn<casacore::String> rwProjectContact_p;
    casacore::ScalarColumn<casacore::String> rwObservationId_p;
    casacore::ScalarColumn<casacore::Double> rwObservationStart_p;
    casacore::ScalarColumn<casacore::Double> rwObservationEnd_p;
    casacore::ScalarColumn<casacore::Double> rwObservationFrequencyMax_p;
    casacore::ScalarColumn<casacore::Double> rwObservationFrequencyMin_p;
    casacore::ScalarColumn<casacore::Double> rwObservationFrequencyCenter_p;
    casacore::ScalarColumn<casacore::Int>    rwSubArrayPointing_p;
    casacore::ScalarColumn<casacore::Int>    rwNofBitsPerSample_p;
    casacore::ScalarColumn<casacore::String> rwAntennaSet_p;
    casacore::ScalarColumn<casacore::String> rwFilterSelection_p;
    casacore::ScalarColumn<casacore::Double> rwClockFrequency_p;
    casacore::ArrayColumn<casacore::String>  rwTarget_p;
    casacore::ScalarColumn<casacore::String> rwSystemVersion_p;
    casacore::ScalarColumn<casacore::String> rwPipelineName_p;
    casacore::ScalarColumn<casacore::String> rwPipelineVersion_p;
    casacore::ScalarColumn<casacore::String> rwFilename_p;
    casacore::ScalarColumn<casacore::String> rwFiletype_p;
    casacore::ScalarColumn<casacore::Double> rwFiledate_p;
    //# Access to Quantum columns
    casacore::ScalarQuantColumn<casacore::Double> rwObservationStartQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwObservationEndQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwObservationFrequencyMaxQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwObservationFrequencyMinQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwObservationFrequencyCenterQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwClockFrequencyQuant_p;
    casacore::ScalarQuantColumn<casacore::Double> rwFiledateQuant_p;
    //# Access to Measure columns
    casacore::ScalarMeasColumn<casacore::MEpoch> rwObservationStartMeas_p;
    casacore::ScalarMeasColumn<casacore::MEpoch> rwObservationEndMeas_p;
    casacore::ScalarMeasColumn<casacore::MEpoch> rwFiledateMeas_p;
  };

} //# end namespace

#endif
