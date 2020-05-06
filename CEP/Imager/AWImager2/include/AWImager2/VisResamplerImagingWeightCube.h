//# VisResampler.h: Convolutional AW resampler for LOFAR data
//# Copyright (C) 2011
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
//# $Id: VisResampler.h 28017 2014-01-23 13:01:00Z vdtol $

#ifndef LOFAR_LOFARFT_VISRESAMPLERIMAGINGWEIGHTCUBE_H
#define LOFAR_LOFARFT_VISRESAMPLERIMAGINGWEIGHTCUBE_H

#include <AWImager2/VisResampler.h>


namespace LOFAR { //# NAMESPACE LOFAR - BEGIN
namespace LofarFT {
  
class VisResamplerImagingWeightCube: public VisResampler
{
public:
  VisResamplerImagingWeightCube(): VisResampler()  {}
  virtual ~VisResamplerImagingWeightCube()                                    {}

  virtual VisibilityResamplerBase* clone()
  {return new VisResamplerImagingWeightCube(*this);}

  void copy(const VisResamplerImagingWeightCube& other)
  {VisResampler::copy(other); }

  // Re-sample the griddedData on the VisBuffer (a.k.a gridding).
  virtual void DataToGrid (
    casacore::Array<casacore::Complex>& griddedData, 
    VBStore& vbs,
    const casacore::Vector<casacore::uInt>& rows,
    casacore::Int rbeg, 
    casacore::Int rend,
    casacore::Matrix<casacore::Double>& sumwt,
    const casacore::Bool& dopsf, 
    CFStore& cfs)
  {
    DataToGridImpl_p(griddedData, vbs, rows, rbeg, rend, sumwt,dopsf,cfs);
  }
  
  virtual void DataToGrid (
    casacore::Array<casacore::DComplex>& griddedData, 
    VBStore& vbs,
    const casacore::Vector<casacore::uInt>& rows,
    casacore::Int rbeg, 
    casacore::Int rend,
    casacore::Matrix<casacore::Double>& sumwt,
    const casacore::Bool& dopsf, 
    CFStore& cfs)
  {
    DataToGridImpl_p(griddedData, vbs, rows, rbeg, rend, sumwt,dopsf,cfs);
  }

private:
  
  // Re-sample the griddedData on the VisBuffer (a.k.a de-gridding).
  //
  template <class T>
  void DataToGridImpl_p(casacore::Array<T>& griddedData, VBStore& vb,
                        const casacore::Vector<casacore::uInt>& rows,
                        casacore::Int rbeg, casacore::Int rend,
                        casacore::Matrix<casacore::Double>& sumwt,const casacore::Bool& dopsf,
                        CFStore& cfs);

};

} // end namespace LofarFT
} // end namespace LOFAR

#endif //
