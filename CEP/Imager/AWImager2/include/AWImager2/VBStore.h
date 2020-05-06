// -*- C++ -*-
//# VBStore.h: Definition of the VBStore class
//# Copyright (C) 1997,1998,1999,2000,2001,2002,2003
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
//# Correspondence concerning AIPS++ should be addressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//# $Id: $

#ifndef LOFAR_LOFARFT_VBSTORE_H
#define LOFAR_LOFARFT_VBSTORE_H
#include <synthesis/TransformMachines/Utils.h>

namespace LOFAR {
namespace LofarFT {

  class VBStore
  {
  public:
    VBStore() : itsDoPSF(casacore::False) {};
    ~VBStore() {};
    
    casacore::Int nRow() const             {return itsNRow;}
    void nRow(casacore::Int nrow)     {itsNRow = nrow;}
    
    casacore::Int beginRow()  const        {return itsBeginRow;}
    void beginRow(casacore::Int beginrow) {itsBeginRow = beginrow;}
    
    casacore::Int endRow() const           {return itsEndRow;}
    void endRow(casacore::Int endrow)  {itsEndRow = endrow;}

    casacore::Bool dopsf() const           {return itsDoPSF;}
    void dopsf(casacore::Bool do_psf)       {itsDoPSF = do_psf;}

    const casacore::Vector<casacore::uInt>& selection() const      {return itsSelection;};
    
    const casacore::Matrix<casacore::Double>& uvw() const          {return itsUVW;}
    void uvw(const casacore::Matrix<casacore::Double>& v)     {itsUVW.reference(v);}
    
    const casacore::Vector<casacore::Bool>& rowFlag() const        {return itsRowFlag;}
    void rowFlag(const casacore::Vector<casacore::Bool>& v)   {itsRowFlag.reference(v);}
    
    const casacore::Cube<casacore::Bool>& flagCube() const         {return itsFlagCube;}
    void flagCube(const casacore::Cube<casacore::Bool>& v)    {itsFlagCube.reference(v);}
    
    const casacore::Matrix<casacore::Float>& imagingWeight() const {return itsImagingWeight;}
    void imagingWeight(const casacore::Matrix<casacore::Float>&  v)  {itsImagingWeight.reference(v);}
    
    const casacore::Cube<casacore::Float>& imagingWeightCube() const {return itsImagingWeightCube;}
    void imagingWeightCube(const casacore::Cube<casacore::Float>&  v)  {itsImagingWeightCube.reference(v);}
    
    casacore::Cube<casacore::Complex>& visCube()        {return itsVisCube;}
    const casacore::Cube<casacore::Complex>& visCube() const       {return itsVisCube;}
    void visCube(casacore::Cube<casacore::Complex>& viscube) {itsVisCube.reference(viscube);}

    casacore::Cube<casacore::Complex>& modelVisCube() {return itsModelVisCube;}
    void modelVisCube(casacore::Cube<casacore::Complex>& modelviscube)    {itsModelVisCube.reference(modelviscube);}

    const casacore::Vector<casacore::Double>& freq() const         {return itsFreq;}
    void freq(const casacore::Vector<casacore::Double>& v)    {itsFreq.reference(v);}

    void reference(const VBStore& other)
    {
      itsNRow = other.itsNRow;  
      itsBeginRow = other.itsBeginRow; 
      itsEndRow = other.itsEndRow;
      itsDoPSF = other.itsDoPSF;

      itsSelection.reference(other.itsSelection);
      itsUVW.reference(other.itsUVW);
      itsRowFlag.reference(other.itsRowFlag);
      itsFlagCube.reference(other.itsFlagCube);
      itsImagingWeight.reference(other.itsImagingWeight);
      itsFreq.reference(other.itsFreq);
      itsVisCube.reference(other.itsVisCube);
      itsModelVisCube.reference(other.itsModelVisCube);
    }

  private:
    
    casacore::Int itsNRow;
    casacore::Int itsBeginRow;
    casacore::Int itsEndRow;
    casacore::Matrix<casacore::Double> itsUVW;
    casacore::Vector<casacore::uInt> itsSelection;
    casacore::Vector<casacore::Bool> itsRowFlag;
    casacore::Cube<casacore::Bool> itsFlagCube;
    casacore::Matrix<casacore::Float> itsImagingWeight;
    casacore::Cube<casacore::Float> itsImagingWeightCube;
    casacore::Cube<casacore::Complex> itsVisCube;
    casacore::Cube<casacore::Complex> itsModelVisCube;
    casacore::Vector<casacore::Double> itsFreq;
    casacore::Bool itsDoPSF;
  };

} // end namespace LofarFT
} // end namespace LOFAR

#endif
