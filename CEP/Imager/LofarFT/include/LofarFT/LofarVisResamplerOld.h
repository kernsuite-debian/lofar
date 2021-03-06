//# LofarVisResamplerOld.h: Convolutional AW resampler for LOFAR data
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

#ifndef LOFARFT_LOFARVISRESAMPLEROLD_H
#define LOFARFT_LOFARVISRESAMPLEROLD_H

#include <synthesis/MeasurementComponents/AWVisResampler.h>
#include <LofarFT/LofarCFStore.h>
#include <LofarFT/LofarVBStore.h>
//added
#include <LofarFT/LofarCFStore.h>

#include <casacore/casa/Logging/LogIO.h>
#include <casacore/casa/Logging/LogOrigin.h>
#include <casacore/casa/Arrays/Cube.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/casa/Arrays/ArrayIter.h>
#include <casacore/casa/Arrays/ArrayMath.h>
#include <casacore/images/Images/PagedImage.h>
#include <casacore/casa/Utilities/Assert.h>

#include <casacore/coordinates/Coordinates/CoordinateSystem.h>
#include <casacore/coordinates/Coordinates/SpectralCoordinate.h>
#include <casacore/coordinates/Coordinates/StokesCoordinate.h>

#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MeasConvert.h>
#include <casacore/measures/Measures/MCDirection.h>
#include <casacore/measures/Measures/MCPosition.h>
#include <casacore/ms/MeasurementSets/MSAntenna.h>
#if defined(HAVE_CASACORE)
#include <casacore/ms/MSSel/MSAntennaParse.h>
#include <casacore/ms/MSSel/MSSelection.h>
#else
#include <casacore/ms/MSSel/MSAntennaParse.h>
#include <casacore/ms/MSSel/MSSelection.h>
#endif
#include <casacore/ms/MeasurementSets/MSAntennaColumns.h>
#include <casacore/ms/MeasurementSets/MSDataDescription.h>
#include <casacore/ms/MeasurementSets/MSDataDescColumns.h>
#include <casacore/ms/MeasurementSets/MSField.h>
#include <casacore/ms/MeasurementSets/MSFieldColumns.h>
#include <casacore/ms/MeasurementSets/MSObservation.h>
#include <casacore/ms/MeasurementSets/MSObsColumns.h>
#include <casacore/ms/MeasurementSets/MSPolarization.h>
#include <casacore/ms/MeasurementSets/MSPolColumns.h>
#include <casacore/ms/MeasurementSets/MSSpectralWindow.h>
#include <casacore/ms/MeasurementSets/MSSpWindowColumns.h>
#include <casacore/measures/Measures/MeasTable.h>

#include <casacore/lattices/Lattices/ArrayLattice.h>
#if defined(HAVE_CASACORE)
#include <casacore/lattices/LatticeMath/LatticeFFT.h>
#else
#include <casacore/lattices/LatticeMath/LatticeFFT.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#include <casacore/casa/vector.h>
#include <casacore/casa/OS/Directory.h>

//=========


namespace LOFAR { //# NAMESPACE CASACORE - BEGIN

  class LofarVisResamplerOld: public AWVisResampler
  {
  public:
    LofarVisResamplerOld(): AWVisResampler()  {}
    virtual ~LofarVisResamplerOld()                                    {}

    virtual VisibilityResamplerBase* clone()
    {return new LofarVisResamplerOld(*this);}

    void copy(const LofarVisResamplerOld& other)
    {AWVisResampler::copy(other); }

    // Re-sample the griddedData on the VisBuffer (a.k.a gridding).
    void lofarDataToGrid (Array<Complex>& griddedData, LofarVBStore& vbs,
                          const Vector<uInt>& rows,
                          Int rbeg, Int rend,
                          Matrix<Double>& sumwt,
                          const Bool& dopsf, LofarCFStore& cfs)
    {DataToGridImpl_p(griddedData, vbs, rows, rbeg, rend, sumwt,dopsf,cfs);}
    void lofarDataToGrid (Array<DComplex>& griddedData, LofarVBStore& vbs,
                          const Vector<uInt>& rows,
                          Int rbeg, Int rend,
                          Matrix<Double>& sumwt,
                          const Bool& dopsf, LofarCFStore& cfs)
    {DataToGridImpl_p(griddedData, vbs, rows, rbeg, rend, sumwt,dopsf,cfs);}

    void lofarGridToData(LofarVBStore& vbs,
                         const Array<Complex>& grid,
                         const Vector<uInt>& rows,
                         Int rbeg, Int rend,
                         LofarCFStore& cfs);


    virtual void setCFMaps(const Vector<Int>& cfMap, const Vector<Int>& conjCFMap)
    {cfMap_p.assign(cfMap); conjCFMap_p.assign(conjCFMap);}

    void lofarComputeResiduals(LofarVBStore& vbs);

  void sgrid(Vector<Double>& pos, Vector<Int>& loc,
			     Vector<Int>& off, Complex& phasor,
			     const Int& irow, const Matrix<Double>& uvw,
			     const Double& dphase, const Double& freq,
			     const Vector<Double>& scale,
			     const Vector<Double>& offset,
                                const Vector<Float>& sampling);

    /*
  template <class T>
    void store2(const Matrix<T> &data, const string &name)
    {
      CoordinateSystem csys;

      Matrix<Double> xform(2, 2);
      xform = 0.0;
      xform.diagonal() = 1.0;
      Quantum<Double> incLon((8.0 / data.shape()(0)) * C::pi / 180.0, "rad");
      Quantum<Double> incLat((8.0 / data.shape()(1)) * C::pi / 180.0, "rad");
      Quantum<Double> refLatLon(45.0 * C::pi / 180.0, "rad");
      csys.addCoordinate(DirectionCoordinate(MDirection::J2000, Projection(Projection::SIN),
					     refLatLon, refLatLon, incLon, incLat,
					     xform, data.shape()(0) / 2, data.shape()(1) / 2));

      Vector<Int> stokes(1);
      stokes(0) = Stokes::I;
      csys.addCoordinate(StokesCoordinate(stokes));
      csys.addCoordinate(SpectralCoordinate(casacore::MFrequency::TOPO, 60e6, 0.0, 0.0, 60e6));

      PagedImage<T> im(TiledShape(IPosition(4, data.shape()(0), data.shape()(1), 1, 1)), csys, name);
      im.putSlice(data, IPosition(4, 0, 0, 0, 0));
    };
    */

  private:
    // Re-sample the griddedData on the VisBuffer (a.k.a de-gridding).
    //
    template <class T>
    void DataToGridImpl_p(Array<T>& griddedData, LofarVBStore& vb,
                          const Vector<uInt>& rows,
                          Int rbeg, Int rend,
			  Matrix<Double>& sumwt,const Bool& dopsf,
                          LofarCFStore& cfs);


    Vector<Int> cfMap_p, conjCFMap_p;
  };

} //# NAMESPACE CASACORE - END

#endif //
