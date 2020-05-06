//# FTMachine.h: Definition for FTMachine
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
//# $Id$

#ifndef LOFAR_LOFARFT_FTMACHINE_H
#define LOFAR_LOFARFT_FTMACHINE_H

#include <AWImager2/DynamicObjectFactory.h>
#include <AWImager2/VisResampler.h>
#include <AWImager2/ConvolutionFunction.h>
#include <AWImager2/VisBuffer.h>
#include <Common/ParameterSet.h>
#include <synthesis/TransformMachines/FTMachine.h>
#include <msvis/MSVis/VisBuffer.h>
#include <casacore/casa/Arrays/Array.h>
#include <casacore/casa/Arrays/Vector.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/casa/Containers/SimOrdMap.h>
#include <casacore/casa/Containers/Block.h>
#include <casacore/casa/OS/Mutex.h>
#include <casacore/casa/OS/PrecTimer.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/images/Images/ImageInterface.h>
#include <casacore/scimath/Mathematics/ConvolveGridder.h>
#include <casacore/scimath/Mathematics/FFTServer.h>
#include <casacore/lattices/Lattices/LatticeCache.h>
#include <casacore/lattices/Lattices/ArrayLattice.h>

namespace LOFAR {
namespace LofarFT {
  
// <summary>  An FTMachine for Gridded Fourier transforms </summary>



class FTMachine : public casacore::FTMachine {
public:

  // Constructor: cachesize is the size of the cache in words
  // (e.g. a few million is a good number), tilesize is the
  // size of the tile used in gridding (cannot be less than
  // 12, 16 works in most cases), and convType is the type of
  // gridding used (SF is prolate spheriodal wavefunction,
  // and BOX is plain box-car summation). mLocation is
  // the position to be used in some phase rotations. If
  // mTangent is specified then the uvw rotation is done for
  // that location iso the image center.
  // <group>
//  LofarFTMachineOld(Long cachesize, Int tilesize, CountedPtr<VisibilityResamplerBase>& visResampler,
//	  String convType="SF", Float padding=1.0, Bool usezero=True, Bool useDoublePrec=False);
  
  enum domain 
  {
    IMAGE=0,
    UV
  };
  
  FTMachine(
    const casacore::MeasurementSet& ms, 
    const LOFAR::ParameterSet& parset);

  // Copy constructor
  FTMachine(const FTMachine &other);

  // Assignment operator
  FTMachine &operator=(const FTMachine &other);

  // Clone
  virtual FTMachine* clone() const = 0;
  
  // Clone
  // casacore::FTMachine declares the virtual clone method as cloneFTM
  virtual casacore::FTMachine* cloneFTM() {return clone();}


  ~FTMachine();
  
  // Show the relative timings of the various steps.
  void showTimings (std::ostream&, double duration) const;

  // Initialize transform to Visibility plane using the image
  // as a template. The image is loaded and Fourier transformed.
  virtual void initializeToVis(
    casacore::PtrBlock<casacore::ImageInterface<casacore::Float>* > &model_images, 
    casacore::Bool normalize);
  
  // Finalize transform to Visibility plane: flushes the image
  // cache and shows statistics if it is being used.
  void finalizeToVis();

  // Initialize transform to Sky plane: initializes the image
  
  virtual void initializeToSky(
    casacore::PtrBlock<casacore::ImageInterface<casacore::Float>* > &images,
    casacore::Bool doPSF);

  // Finalize transform to Sky plane: flushes the image
  // cache and shows statistics if it is being used. 
  // DOES *NOT* DO THE FINAL TRANSFORM!
  virtual void finalizeToSky();
  
  virtual void initializeResidual(
    casacore::PtrBlock<casacore::ImageInterface<casacore::Float>* > model_images,
    casacore::PtrBlock<casacore::ImageInterface<casacore::Float>* > images,
    casacore::Bool normalize);

  virtual void finalizeResidual();
  
  virtual void get(casacore::VisBuffer& vb, casacore::Int row=-1);
  virtual void get(VisBuffer& vb, casacore::Int row=-1)=0;

  virtual void put(
    const casacore::VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::Bool dopsf = casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);
  
  virtual void put(
    const VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::Bool dopsf = casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED)=0;

  virtual void residual(
    VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);
  
  // Make the entire image
  using casacore::FTMachine::makeImage;
  void makeImage(
    casacore::FTMachine::Type type,
    casacore::ROVisibilityIterator& vi,
    casacore::ImageInterface<casacore::Float>& image,
    casacore::Matrix<casacore::Float>& weight);

  // Get the final image: do the Fourier transform and
  // grid-correct, then optionally normalize by the summed weights
  virtual void getImages(
    casacore::Matrix<casacore::Float>& weights, 
    casacore::Bool normalize);
  
  // Get the average primary beam.
  virtual casacore::Matrix<casacore::Float> getAveragePB();

  // Get the spheroidal cut.
  virtual casacore::Matrix<casacore::Float> getSpheroidal();



  inline virtual casacore::Float pbFunc(
    const casacore::Float& a, 
    const casacore::Float& limit)
  {
    if (abs(a) >= limit) 
    {
      return (a);
    }
    else
    {
      return 1.0;
    };
  }
    
  inline virtual casacore::Complex pbFunc(
    const casacore::Complex& a, 
    const casacore::Float& limit)
  {
    if (abs(a)>=limit)
    {
      return (a);
    }
    else
    {
      return casacore::Complex(1.0,0.0);
    };
  }
    
  // Can this FTMachine be represented by Fourier convolutions?
  virtual casacore::Bool isFourier() 
  {
    return casacore::True;
  }

  virtual void setMiscInfo(const casacore::Int qualifier){(void)qualifier;};
  
  void getWeightImage(casacore::ImageInterface<casacore::Float>& weightImage, casacore::Matrix<casacore::Float>& weights);

  
  // pure virtual functions that we do not use, 
  // implementation only throws a not implemented exception
  
  virtual void initializeToVis(casacore::ImageInterface<casacore::Complex>& image, const casacore::VisBuffer& vb);
  virtual void initializeToSky(casacore::ImageInterface<casacore::Complex>& image, casacore::Matrix<casacore::Float>& weight, const casacore::VisBuffer& vb);
  
  virtual casacore::ImageInterface<casacore::Complex>& getImage(
    casacore::Matrix<casacore::Float>&, 
    casacore::Bool normalize = casacore::True);

  virtual void ComputeResiduals(
    casacore::VisBuffer&vb, 
    casacore::Bool useCorrected);

   
  
protected:
  
  virtual void initialize_model_grids(casacore::Bool normalize);
  
  void finalize_model_grids();

  void initialize_grids();

  void normalize(casacore::ImageInterface<casacore::Complex> &image, casacore::Bool normalize, casacore::Bool spheroidal);
  
  casacore::StokesCoordinate get_stokes_coordinates();
  
  // the images and model images are owned by SkyModel
  // can use a raw pointer here
  casacore::PtrBlock<casacore::ImageInterface<casacore::Float> *> itsModelImages; 
  casacore::PtrBlock<casacore::ImageInterface<casacore::Float>*> itsImages;

  // the complex images and complex model images are created locally
  // use a counted pointer to ensure proper desctruction  
  casacore::Block<casacore::CountedPtr<casacore::ImageInterface<casacore::Complex> > > itsComplexModelImages;
  casacore::Block<casacore::CountedPtr<casacore::ImageInterface<casacore::Complex> > > itsComplexImages;

  casacore::Block<casacore::Array<casacore::Complex> >  itsModelGrids;

  // Arrays for non-tiled gridding (one per thread).
  vector< casacore::Array<casacore::Complex> >  itsGriddedData;
  vector< casacore::Array<casacore::DComplex> > itsGriddedData2;
  domain itsGriddedDataDomain;

  casacore::Bool itsNormalizeModel;
  casacore::Int itsNX; 
  casacore::Int itsNY; 
  casacore::Int itsPaddedNX; 
  casacore::Int itsPaddedNY; 
  casacore::Int itsNPol; 
  casacore::Int itsNChan; 
  
  casacore::Bool itsUseDoubleGrid; 
  casacore::Vector<casacore::Int> itsChanMap;
  casacore::Vector<casacore::Int> itsPolMap;

  // Padding in FFT
  casacore::Float itsPadding;

  void ok();

  void init(const casacore::ImageInterface<casacore::Float> &image);

  // Is this record on Grid? check both ends. This assumes that the
  // ends bracket the middle
  casacore::Bool recordOnGrid(const casacore::VisBuffer& vb, casacore::Int rownr) const;

  // Image cache
  casacore::LatticeCache<casacore::Complex> * itsImageCache;

  casacore::CountedPtr<casacore::Lattice<casacore::Complex> > itsLattice;

  casacore::String itsConvType;

  casacore::Float itsMaxAbsData;

  // Useful IPositions
  casacore::IPosition itsCenterLoc;
  casacore::IPosition itsOffsetLoc;

  // Image Scaling and offset
  casacore::Vector<casacore::Double> itsUVScale;
  casacore::Vector<casacore::Double> itsUVOffset;

  vector< casacore::Matrix<casacore::Complex> > itsSumPB;
  vector< casacore::Matrix<casacore::Double> >  itsSumWeight;
  vector< double > itsSumCFWeight;
  mutable casacore::Matrix<casacore::Float> itsAveragePB;
  mutable casacore::Matrix<casacore::Float> itsSpheroidal;

  casacore::Int itsPriorCacheSize;

  //Check if using put that avoids non-necessary reads
  casacore::Bool itsUsePut2;

  LOFAR::ParameterSet itsParset;
  
  //machine name
  casacore::String itsMachineName;

  // Shape of the padded image
  casacore::IPosition itsPaddedShape;

  casacore::Int convSampling;
  casacore::Float pbLimit_p;
  casacore::Int sensitivityPatternQualifier_p;
  casacore::String sensitivityPatternQualifierStr_p;
  casacore::Vector<casacore::Float> pbPeaks;
  casacore::Bool pbNormalized_p;
  // The average PB for sky image normalization
  //
  casacore::CountedPtr<casacore::ImageInterface<casacore::Float> > itsAvgPBImage;
  casacore::CountedPtr<casacore::ImageInterface<casacore::Complex> > itsAvgPBSqImage;

  casacore::CountedPtr<VisResampler> itsVisResampler;
  virtual VisResampler* visresampler() {return &*itsVisResampler;}
  

  casacore::MeasurementSet itsMS;
  casacore::Int itsNWPlanes;
  double itsWMax;
  int itsNThread;
  int itsNGrid;

  casacore::CountedPtr<ConvolutionFunction> itsConvFunc;
  casacore::Vector<casacore::Int> itsConjCFMap;
  casacore::Vector<casacore::Int> itsCFMap;
  casacore::String itsBeamPath;
  int itsVerbose;
  int itsMaxSupport;
  casacore::Int itsOversample;
  casacore::String itsImageName;
//  casacore::Matrix<casacore::Bool> itsGridMuellerMask;
//  casacore::Matrix<casacore::Bool> itsDegridMuellerMask;
  double itsGriddingTime;
  double itsDegriddingTime;
  double itsCFTime;
  casacore::PrecTimer itsTotalTimer;
  
};

// Factory that can be used to generate new FTMachine objects.
// The factory is defined as a singleton.
typedef Singleton<DynamicObjectFactory<FTMachine*(const casacore::MeasurementSet& ms, const ParameterSet& parset)> > FTMachineFactory;


} //# end namespace LofarFT
} //# end namespace LOFAR

#endif
