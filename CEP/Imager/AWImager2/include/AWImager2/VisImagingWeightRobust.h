//# VisImagingWeightRobust.h: Calculate Imaging Weights for a buffer from weight
//# Copyright (C) 2009
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
//# $Id$

#ifndef LOFAR_LOFARFT_VISIMAGINGWEIGHTROBUST_H
#define LOFAR_LOFARFT_VISIMAGINGWEIGHTROBUST_H

#include <casacore/casa/aips.h>
#include <casacore/casa/BasicSL/Complex.h>
#include <casacore/casa/Quanta/Quantum.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <AWImager2/VisImagingWeight.h>

namespace casacore
{
  class ROVisibilityIterator;
  class VisBuffer;
  template<class T> class Vector;
}

namespace LOFAR { //# NAMESPACE LOFAR - BEGIN
namespace LofarFT { //# NAMESPACE LOFAR - BEGIN

class VisImagingWeightRobust : public VisImagingWeight

{
  
public:
      
VisImagingWeightRobust(
  casacore::ROVisibilityIterator& vi, 
  const casacore::String& rmode, 
  const casacore::Quantity& noise,
  casacore::Double robust, 
  casacore::Int nx, 
  casacore::Int ny,
  const casacore::Quantity& cellx, 
  const casacore::Quantity& celly,
  casacore::Int uBox = 0, 
  casacore::Int vBox = 0,
  casacore::Bool multiField = casacore::False);

virtual void weight(
  casacore::Cube<casacore::Float>& imagingWeight, 
  const casacore::VisBuffer& vb) const;

private:
  casacore::Float itsF2;
  casacore::Float itsD2;
  casacore::Int itsNX;
  casacore::Int itsNY;
  casacore::Int itsUOrigin;
  casacore::Int itsVOrigin;
  casacore::Float itsUScale;
  casacore::Float itsVScale;
  
  casacore::Matrix<casacore::Float> itsWeightMap;
  
};
  
} //end namespace LofarFT
} //end namespace LOFAR

#endif // LOFAR_LOFARFT_VISIMAGINGWEIGHTROBUST_H
