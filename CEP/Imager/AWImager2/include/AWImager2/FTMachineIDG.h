//# FTMachineSimpleWB.h: Definition for FTMachineSimple
//# Copyright (C) 1996,1997,1998,1999,2000,2002
//# Associated Universities, Inc. Washington DC, USA.
//#
//# This library is free software; you can redistribute it and/or modify it
//# under the terms of the GNU Library General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or (at your
//# option) any later version.
//#
//# This library is distributed in the hope that it will be useful, but WITHOUT
//# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
//# License for more details.
//#
//# You should have received a copy of the GNU Library General Public License
//# along with this library; if not, write to the Free Software Foundation,
//# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning AIPS++ should be adressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//#
//# $Id: FTMachineSimpleWB.h 28512 2014-03-05 01:07:53Z vdtol $

#ifndef LOFAR_LOFARFT_FTMACHINEIDG_H
#define LOFAR_LOFARFT_FTMACHINEIDG_H

#include <AWImager2/FTMachine.h>

#include <idg/XEON/Proxies.h>

namespace LOFAR {
namespace LofarFT {

class VisBuffer;  
  
class FTMachineIDG : public FTMachine {
public:
  static const casacore::String theirName;

  FTMachineIDG(
    const casacore::MeasurementSet& ms, 
    const ParameterSet& parset);

  virtual ~FTMachineIDG();
  
  // Copy constructor
  FTMachineIDG(const FTMachineIDG &other);

  // Assignment operator
  FTMachineIDG &operator=(const FTMachineIDG &other);

  // Clone
  FTMachineIDG* clone() const;

  virtual casacore::String name() const { return theirName;}

  virtual casacore::Matrix<casacore::Float> getAveragePB();
//   virtual casacore::Matrix<casacore::Float> getSpheroidal();
  
  // Get actual coherence from grid by degridding
  virtual void get(VisBuffer& vb, casacore::Int row=-1);
  
  // Put coherence to grid by gridding.
  virtual void put(
    const VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::Bool dopsf = casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);

  virtual void residual(
    VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);
  
protected:

  virtual void initialize_model_grids(casacore::Bool normalize);

  virtual void getput(
    VisBuffer& vb, 
    casacore::Int row=-1, 
    casacore::Bool doget = casacore::True,
    casacore::Bool doput = casacore::True,    
    casacore::Bool dopsf = casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);
    
  casacore::CountedPtr<Xeon> itsProxy;


  // Get the appropriate data pointer
  casacore::Array<casacore::Complex>* getDataPointer(const casacore::IPosition&, casacore::Bool);

  // Gridder
  casacore::String convType;

  casacore::Float maxAbsData;

  // Useful IPositions
  casacore::IPosition centerLoc;
  casacore::IPosition offsetLoc;


  // Shape of the padded image
  casacore::IPosition padded_shape;

  casacore::Int convSampling;
  casacore::Float pbLimit_p;
  int itsNThread;
  casacore::Int itsRefFreq;
  casacore::Float itsTimeWindow;

private:
  
  std::string itsCompiler;
  std::string itsCompilerFlags;

};

} //# end namespace LofarFT
} //# end namespace LOFAR

#endif
