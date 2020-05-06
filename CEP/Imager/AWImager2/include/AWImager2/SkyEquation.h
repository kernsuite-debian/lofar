//# SkyEquation.h: SkyEquation definition
//# Copyright (C) 2007
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
//# $Id: $
#ifndef LOFAR_LOFARFT_SKYEQUATION_H
#define LOFAR_LOFARFT_SKYEQUATION_H

#include <synthesis/MeasurementEquations/SkyEquation.h>

//Forward
namespace casacore 
{    
  class ROVisibilityIterator;
  template <class T> class ImageInterface;
  template <class T> class TempImage;
  template <class T> class SubImage;
  template <class T> class Block;
}

namespace LOFAR { //# NAMESPACE LOFAR - BEGIN
namespace LofarFT { //# NAMESPACE LOFAR - BEGIN
  
class FTMachine;
class VisibilityIterator;
class VisBuffer;

class SkyEquation : public casacore::SkyEquation
{
  public:
  //Read only iterator...hence no scratch col
  SkyEquation(
    casacore::SkyModel& sm, 
    VisibilityIterator& vi, 
    FTMachine& ft, 
    casacore::ComponentFTMachine& cft, 
    casacore::Bool noModelCol = casacore::False);

  virtual ~SkyEquation();
  
  virtual void predict(
    casacore::Bool incremental = casacore::False, 
    casacore::MS::PredefinedColumns Type = casacore::MS::MODEL_DATA);
  
  virtual void gradientsChiSquared(casacore::Bool incremental, casacore::Bool commitModel=casacore::False);

  void makeApproxPSF(casacore::PtrBlock<casacore::ImageInterface<casacore::Float> * >& psfs);

  private:

  casacore::Block<casacore::CountedPtr<casacore::FTMachine> > ftm_p;
  casacore::Block<casacore::CountedPtr<casacore::FTMachine> > iftm_p;

  FTMachine * itsFTMachine;
  VisibilityIterator * rvi_p;
  VisibilityIterator * wvi_p;
};

} //# NAMESPACE LOFARFT
} //# NAMESPACE LOFAR 

#endif
