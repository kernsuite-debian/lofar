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
//# $Id$

#ifndef LOFAR_LOFARFT_VISRESAMPLER_H
#define LOFAR_LOFARFT_VISRESAMPLER_H

#include <synthesis/TransformMachines/AWVisResampler.h>
#include <AWImager2/CFStore.h>
#include <AWImager2/VBStore.h>

namespace LOFAR { //# NAMESPACE LOFAR - BEGIN
namespace LofarFT {
  
class VisResampler: public casacore::AWVisResampler
{
public:
  VisResampler(): AWVisResampler()  {}
  virtual ~VisResampler()                                    {}

//   virtual VisibilityResamplerBase* clone() = 0;
// 
//   void copy(const VisResampler& other)
//   {AWVisResampler::copy(other); }
//   
  void set_chan_map(const casacore::Vector<casacore::Int> &map);

  void set_chan_map_CF(const casacore::Vector<casacore::Int> &map);

  // Re-sample the griddedData on the VisBuffer (a.k.a gridding).
  virtual void DataToGrid (
    casacore::Array<casacore::Complex>& griddedData, 
    const VBStore& vbs,
    const casacore::Vector<casacore::uInt>& rows,
    casacore::Int rbeg, 
    casacore::Int rend,
    casacore::Matrix<casacore::Double>& sumwt,
    const casacore::Bool& dopsf, 
    CFStore& cfs) {};
  
  virtual void DataToGrid (
    casacore::Array<casacore::DComplex>& griddedData, 
    const VBStore& vbs,
    const casacore::Vector<casacore::uInt>& rows,
    casacore::Int rbeg, 
    casacore::Int rend,
    casacore::Matrix<casacore::Double>& sumwt,
    const casacore::Bool& dopsf, 
    CFStore& cfs) {};

  virtual void GridToData(
    VBStore& vbs,
    const casacore::Array<casacore::Complex>& grid,
    const casacore::Vector<casacore::uInt>& rows,
    casacore::Int rbeg, 
    casacore::Int rend,
    CFStore& cfs) {};

  void ComputeResiduals(VBStore& vbs);

  void sgrid(
    casacore::Vector<casacore::Double>& pos, 
    casacore::Vector<casacore::Int>& loc,
    casacore::Vector<casacore::Int>& off, 
    casacore::Complex& phasor,
    const casacore::Int& irow, 
    const casacore::Matrix<casacore::Double>& uvw,
    const casacore::Double& dphase, 
    const casacore::Double& freq,
    const casacore::Vector<casacore::Double>& scale,
    const casacore::Vector<casacore::Double>& offset,
    const casacore::Vector<casacore::Float>& sampling);

protected:
  casacore::Vector<casacore::Int> itsChanMap;
  casacore::Vector<casacore::Int> itsChanMapCF;
    
};

} // end namespace LofarFT
} // end namespace LOFAR

#endif //
