//# CFStore.h: Definition of the CFStore class
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
//# $Id: $

#ifndef LOFAR_LOFARFT_CFSTORE_H
#define LOFAR_LOFARFT_CFSTORE_H

#include <AWImager2/CFDefs.h>
#include <synthesis/TransformMachines/SynthesisError.h>
#include <casacore/coordinates/Coordinates/CoordinateSystem.h>
#include <casacore/casa/Logging/LogIO.h>
#include <casacore/casa/Logging/LogSink.h>
#include <casacore/casa/Logging/LogOrigin.h>
#include <casacore/casa/Utilities/CountedPtr.h>
#include <casacore/images/Images/ImageInterface.h>
#include <msvis/MSVis/VisBuffer.h>
#include <casacore/casa/Arrays/Matrix.h>

namespace LOFAR {
namespace LofarFT {

class CFStore
{
public:

  CFStore();

  CFStore(const casacore::CountedPtr<CFDefs::CFType>& dataPtr,
          casacore::CoordinateSystem& cs, 
          casacore::Vector<casacore::Float>& samp,
          casacore::Vector<casacore::Int>& xsup, 
          casacore::Vector<casacore::Int>& ysup, 
          casacore::Int maxXSup, 
          casacore::Int maxYSup,
          casacore::Quantity PA, 
          casacore::Int mosPointing,
          casacore::Bool conjugated = casacore::False);

  CFStore(const casacore::CountedPtr<CFDefs::CFTypeVec>& dataPtr,
          casacore::CoordinateSystem& cs, 
          casacore::Vector<casacore::Float>& samp,
          casacore::Vector<casacore::Int>& xsup, 
          casacore::Vector<casacore::Int>& ysup, 
          casacore::Int maxXSup, 
          casacore::Int maxYSup,
          casacore::Quantity PA, 
          casacore::Int mosPointing,
          casacore::Bool conjugated = casacore::False);

  ~CFStore() {};

  CFStore& operator=(const CFStore& other);
  
  void show(const char *Mesg=NULL, casacore::ostream &os=casacore::cerr);
  
  casacore::Bool isNull() {return itsData.null();}
  
  casacore::Bool isConjugated() {return itsConjugated;}
  
  void set(const CFStore& other);

  void set(CFDefs::CFType *dataPtr,
           casacore::CoordinateSystem& cs, 
           casacore::Vector<casacore::Float>& samp,
           casacore::Vector<casacore::Int>& xsup, 
           casacore::Vector<casacore::Int>& ysup, 
           casacore::Int maxXSup, 
           casacore::Int maxYSup,
           casacore::Quantity PA, 
           const casacore::Int mosPointing=0,
           casacore::Bool conjugated = casacore::False);

  void set(CFDefs::CFTypeVec *dataPtr,
           casacore::CoordinateSystem& cs, 
           casacore::Vector<casacore::Float>& samp,
           casacore::Vector<casacore::Int>& xsup,
           casacore::Vector<casacore::Int>& ysup, 
           casacore::Int maxXSup, 
           casacore::Int maxYSup,
           casacore::Quantity PA, 
           const casacore::Int mosPointing=0,
           casacore::Bool conjugated=casacore::False);

  void resize(casacore::Int nw, 
              casacore::Bool retainValues=casacore::False);
  
  void resize(casacore::IPosition imShape, 
              casacore::Bool retainValues=casacore::False);

  CFDefs::CFTypeVec& vdata() {return *itsVData;}
  casacore::Vector<casacore::Float>& sampling() {return itsSampling;}
  casacore::Vector<casacore::Int>& xSupport() {return itsXSupport;}
  casacore::Vector<casacore::Int>& ySupport() {return itsYSupport;}
  
  
  casacore::CountedPtr<CFDefs::CFType> itsData;
  casacore::CountedPtr<CFDefs::CFTypeReal> itsRData;
  casacore::CountedPtr<CFDefs::CFTypeVec> itsVData;
  casacore::CoordinateSystem itsCoordSys;
  casacore::Vector<casacore::Float> itsSampling;
  casacore::Vector<casacore::Int> itsXSupport;
  casacore::Vector<casacore::Int> itsYSupport;
  casacore::Int itsMaxXSupport;
  casacore::Int itsMaxYSupport;
  casacore::Quantity itsPA;
  casacore::Int itsMosPointingPos;
  casacore::Bool itsConjugated;
};

} //# NAMESPACE LofarFT - END
} //# NAMESPACE LOFAR - END

#endif
