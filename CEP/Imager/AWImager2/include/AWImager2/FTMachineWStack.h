//# FTMachineWsplit.h: Definition for FTMachineWsplit
//#
//# Copyright (C) 2013
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
//# $Id: FTMachineSplitBeamWStack.h 31506 2015-04-17 13:42:47Z dijkema $

#ifndef LOFARFT_LOFARFTMACHINEWSPLIT_H
#define LOFARFT_LOFARFTMACHINEWSPLIT_H

#include <casacore/casa/Arrays/Array.h>
#include <casacore/casa/Arrays/ArrayMath.h>
#include <casacore/casa/Arrays/ArrayLogical.h>
#include <casacore/casa/Arrays/ArrayIO.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/casa/Arrays/Vector.h>
#include <casacore/casa/BasicSL/Complex.h>
#include <casacore/casa/Containers/Block.h>
#include <casacore/casa/OS/File.h>
#include <casacore/casa/OS/PrecTimer.h>
#include <casacore/casa/OS/Timer.h>

#include <casacore/images/Images/ImageInterface.h>
#include <casacore/lattices/Lattices/LatticeCache.h>
#include <casacore/lattices/Lattices/ArrayLattice.h>
#include <casacore/scimath/Mathematics/FFTServer.h>
#include <casacore/scimath/Mathematics/ConvolveGridder.h>
#include <msvis/MSVis/VisBuffer.h>
#include <synthesis/TransformMachines/FTMachine.h>

#include <AWImager2/VisResampler.h>
#include <AWImager2/ConvolutionFunction.h>
#include <AWImager2/CFStore.h>

namespace LOFAR {

// <summary>  An FTMachine for Gridded Fourier transforms </summary>

// <use visibility=export>

// <reviewed reviewer="" date="" tests="" demos="">

// <prerequisite>
//   <li> <linkto class=FTMachine>FTMachine</linkto> module
//   <li> <linkto class=SkyEquation>SkyEquation</linkto> module
//   <li> <linkto class=VisBuffer>VisBuffer</linkto> module
// </prerequisite>
//
// <etymology>
// FTMachine is a Machine for Fourier Transforms. FTMachineWsplit does
// Grid-based Fourier transforms.
// </etymology>
//
// <synopsis>
// The <linkto class=SkyEquation>SkyEquation</linkto> needs to be able
// to perform Fourier transforms on visibility data. FTMachineWsplit
// allows efficient Fourier Transform processing using a
// <linkto class=VisBuffer>VisBuffer</linkto> which encapsulates
// a chunk of visibility (typically all baselines for one time)
// together with all the information needed for processing
// (e.g. UVW coordinates).
//
// Gridding and degridding in FTMachineWsplit are performed using a
// novel sort-less algorithm. In this approach, the gridded plane is
// divided into small patches, a cache of which is maintained in memory
// using a general-purpose <linkto class=LatticeCache>LatticeCache</linkto> class. As the (time-sorted)
// visibility data move around slowly in the Fourier plane, patches are
// swapped in and out as necessary. Thus, optimally, one would keep at
// least one patch per baseline.
//
// A grid cache is defined on construction. If the gridded uv plane is smaller
// than this, it is kept entirely in memory and all gridding and
// degridding is done entirely in memory. Otherwise a cache of tiles is
// kept an paged in and out as necessary. Optimally the cache should be
// big enough to hold all polarizations and frequencies for all
// baselines. The paging rate will then be small. As the cache size is
// reduced below this critical value, paging increases. The algorithm will
// work for only one patch but it will be very slow!
//
// This scheme works well for arrays having a moderate number of
// antennas since the saving in space goes as the ratio of
// baselines to image size. For the ATCA, VLBA and WSRT, this ratio is
// quite favorable. For the VLA, one requires images of greater than
// about 200 pixels on a side to make it worthwhile.
//
// The FFT step is done plane by plane for images having less than
// 1024 * 1024 pixels on each plane, and line by line otherwise.
//
// The gridding and degridding steps are implemented in Fortran
// for speed. In gridding, the visibilities are added onto the
// grid points in the neighborhood using a weighting function.
// In degridding, the value is derived by a weight summ of the
// same points, using the same weighting function.
// </synopsis>
//
// <example>
// See the example for <linkto class=SkyModel>SkyModel</linkto>.
// </example>
//
// <motivation>
// Define an interface to allow efficient processing of chunks of
// visibility data
// </motivation>
//
// <todo asof="97/10/01">
// <ul> Deal with large VLA spectral line case
// </todo>

class FTMachineWsplit : public casacore::FTMachine {
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
//  FTMachineWsplit(casacore::Long cachesize, casacore::Int tilesize, casacore::CountedPtr<VisibilityResamplerBase>& visResampler,
//	  casacore::String convType="SF", casacore::Float padding=1.0, casacore::Bool usezero=casacore::True, casacore::Bool useDoublePrec=casacore::False);
  FTMachineWsplit(
    casacore::Long cachesize, 
    casacore::Int tilesize,  
    casacore::CountedPtr<casacore::VisibilityResamplerBase>& visResampler, 
    casacore::String convType, 
    const casacore::MeasurementSet& ms,
    casacore::Int nwPlanes,
    casacore::MPosition mLocation, 
    casacore::Float padding, 
    casacore::Bool usezero,
    casacore::Bool useDoublePrec, 
    double wmax,
    casacore::Int verbose,
    casacore::Int maxsupport,
    casacore::Int oversample,
    const casacore::String& imageName,
    const casacore::Matrix<casacore::Bool>& gridMuellerMask,
    const casacore::Matrix<casacore::Bool>& degridMuellerMask,
    casacore::Double refFreq,
    casacore::Bool use_Linear_Interp_Gridder,
    casacore::Bool use_EJones,
    int stepApplyElement,
    int applyBeamCode,
    casacore::Double pbCut,
    casacore::Bool predictFT,
    casacore::String psfOnDisk,
    casacore::Bool useMasksDegrid,
    casacore::Bool reallyDoPSF,
    casacore::Double uvMin,
    casacore::Double uvMax,
    casacore::Bool makeDirtyCorr,
    const casacore::Record& parameters);//,

  // Copy constructor
  FTMachineWsplit(const FTMachineWsplit &other);

  // Assignment operator
  FTMachineWsplit &operator=(const FTMachineWsplit &other);

  // Clone
  FTMachineWsplit* clone() const;


  ~FTMachineWsplit();
  
  virtual casacore::String name() const { return "FTMachineWsplit";};

  // Show the relative timings of the various steps.
  void showTimings (
    std::ostream&, 
    double duration) const;

  // Initialize transform to Visibility plane using the image
  // as a template. The image is loaded and Fourier transformed.
  void initializeToVis(
    casacore::ImageInterface<casacore::Complex>& image,
    const casacore::VisBuffer& vb);

  // Finalize transform to Visibility plane: flushes the image
  // cache and shows statistics if it is being used.
  void finalizeToVis();
  
  void getSplitWplanes(
    casacore::VisBuffer& vb, 
    casacore::Int row);
  
  void getTraditional(
    casacore::VisBuffer& vb, 
    casacore::Int row);
  
  void putSplitWplanesOverlap(
    const casacore::VisBuffer& vb, 
    casacore::Int row, 
    casacore::Bool dopsf,
    FTMachine::Type type);
  
  void putSplitWplanes(
    const casacore::VisBuffer& vb, 
    casacore::Int row, 
    casacore::Bool dopsf,
    FTMachine::Type type);
  
  void putTraditional(
    const casacore::VisBuffer& vb, 
    casacore::Int row, 
    casacore::Bool dopsf,
    FTMachine::Type type);
  
  // Initialize transform to Sky plane: initializes the image
  void initializeToSky(
    casacore::ImageInterface<casacore::Complex>& image,  
    casacore::Matrix<casacore::Float>& weight,
    const casacore::VisBuffer& vb);


  // Finalize transform to Sky plane: flushes the image
  // cache and shows statistics if it is being used. DOES NOT
  // DO THE FINAL TRANSFORM!
  void finalizeToSky();

  // Get actual coherence from grid by degridding
  void get(
    casacore::VisBuffer& vb, 
    casacore::Int row=-1);

  // Put coherence to grid by gridding.
  void put(
    const casacore::VisBuffer& vb, 
    casacore::Int row=-1, 
    casacore::Bool dopsf=casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);

  
  // Make the entire image
  void makeImage(casacore::FTMachine::Type type,
		 casacore::VisSet& vs,
		 casacore::ImageInterface<casacore::Complex>& image,
		 casacore::Matrix<casacore::Float>& weight);

  // Get the final image: do the Fourier transform and
  // grid-correct, then optionally normalize by the summed weights
  casacore::ImageInterface<casacore::Complex>& getImage(casacore::Matrix<casacore::Float>&, casacore::Bool normalize=casacore::True);

  // Get the average primary beam.
  virtual const casacore::Matrix<casacore::Float>& getAveragePB() const;

  // Get the spheroidal cut.
  const casacore::Matrix<casacore::Float>& getSpheroidCut() const
    { return itsConvFunc->getSpheroidCut(); }


  ///  virtual void normalizeImage(Lattice<casacore::Complex>& skyImage,
  ///			      const casacore::Matrix<casacore::Double>& sumOfWts,
  ///			      Lattice<casacore::Float>& sensitivityImage,
  ///			      casacore::Bool fftNorm)
  ///    {throw(AipsError("FTMachineWsplit::normalizeImage() called"));}

  void normalizeAvgPB();
  void normalizeAvgPB(
    casacore::ImageInterface<casacore::Complex>& inImage,
    casacore::ImageInterface<casacore::Float>& outImage);
    //
    // Make a sensitivity image (sensitivityImage), given the gridded
    // weights (wtImage).  These are related to each other by a
    // Fourier transform and normalization by the sum-of-weights
    // (sumWt) and normalization by the product of the 2D FFT size
    // along each axis.  If doFFTNorm=casacore::False, normalization by the FFT
    // size is not done.  If sumWt is not provided, normalization by
    // the sum of weights is also not done.
    //



  virtual void makeSensitivityImage(casacore::Lattice<casacore::Complex>&,
    casacore::ImageInterface<casacore::Float>&,
    const casacore::Matrix<casacore::Float>& =casacore::Matrix<casacore::Float>(),
    const casacore::Bool& = casacore::True) {}
      
  virtual void makeSensitivityImage(
    const casacore::VisBuffer& vb, 
    const casacore::ImageInterface<casacore::Complex>& imageTemplate,
    casacore::ImageInterface<casacore::Float>& sensitivityImage);

  inline virtual casacore::Float pbFunc(
    const casacore::Float& a, 
    const casacore::Float& limit)
  {if (abs(a) >= limit) return (a);else return 1.0;};
    
  inline virtual casacore::Complex pbFunc(
    const casacore::Complex& a, 
    const casacore::Float& limit)
  {if (abs(a)>=limit) return (a); else return casacore::Complex(1.0,0.0);};
    
  //
  // Given the sky image (Fourier transform of the visibilities),
  // sum of weights and the sensitivity image, this method replaces
  // the skyImage with the normalized image of the sky.
  //
  virtual void normalizeImage(
    casacore::Lattice<casacore::Complex>& skyImage,
    const casacore::Matrix<casacore::Double>& sumOfWts,
    casacore::Lattice<casacore::Float>& sensitivityImage,
    casacore::Bool fftNorm=casacore::True);
    
  virtual void normalizeImage(
    casacore::Lattice<casacore::Complex>& skyImage,
    const casacore::Matrix<casacore::Double>& sumOfWts,
    casacore::Lattice<casacore::Float>& sensitivityImage,
    casacore::Lattice<casacore::Complex>& sensitivitySqImage,
    casacore::Bool fftNorm=casacore::True);

  virtual casacore::ImageInterface<casacore::Float>& getSensitivityImage() {return *avgPB_p;}
  virtual casacore::Matrix<casacore::Double>& getSumOfWeights() {return sumWeight;};
  virtual casacore::Matrix<casacore::Double>& getSumOfCFWeights() {return sumCFWeight;};

  // Get the final weights image
  void getWeightImage(
    casacore::ImageInterface<casacore::Float>&, 
    casacore::Matrix<casacore::Float>&);

  // Save and restore the FTMachineWsplit to and from a record
  virtual casacore::Bool toRecord(
    casacore::String& error, 
    casacore::RecordInterface& outRec,
    casacore::Bool withImage=casacore::False);
  
  virtual casacore::Bool fromRecord(
    casacore::String& error, 
    const casacore::RecordInterface& inRec);

  // Can this FTMachine be represented by Fourier convolutions?
  virtual casacore::Bool isFourier() {return casacore::True;}

  virtual void setNoPadding(casacore::Bool nopad){noPadding_p=nopad;};

  virtual casacore::String name();

  //Cyr: The FTMachine has got to know the order of the Taylor term
  virtual void setMiscInfo(const casacore::Int qualifier){thisterm_p=qualifier;};
  
  virtual void ComputeResiduals(
    casacore::VisBuffer&vb, 
    casacore::Bool useCorrected);


  void makeConjPolMap(
    const casacore::VisBuffer& vb, 
    const casacore::Vector<casacore::Int> cfPolMap, 
    casacore::Vector<casacore::Int>& conjPolMap);

  void makeCFPolMap(
    const casacore::VisBuffer& vb, 
    const casacore::Vector<casacore::Int>& cfstokes, 
    casacore::Vector<casacore::Int>& polM);

  void setPsfOnDisk(casacore::String NamePsf){itsNamePsfOnDisk=NamePsf;}
  
  virtual casacore::String giveNamePsfOnDisk(){return itsNamePsfOnDisk;}
  
    // Arrays for non-tiled gridding (one per thread).
  
  void initGridThreads(
    vector< casacore::Array<casacore::Complex> >&  otherGriddedData, 
    vector< casacore::Array<casacore::DComplex> >&  otherGriddedData2);

  casacore::Matrix<casacore::Bool> giveMaskGrid()
  {
    return itsMaskGridCS;
  }

protected:
  vector< casacore::Array<casacore::Complex> >*  itsGriddedData;
  vector< casacore::Array<casacore::DComplex> >*  itsGriddedData2;
  mutable casacore::Matrix<casacore::Float> itsAvgPB;
  // Padding in FFT
  casacore::Float padding_p;
  casacore::Int thisterm_p;
  casacore::Double itsRefFreq;
  casacore::Bool itsPredictFT;
  double its_tot_time_grid;
  double its_tot_time_cf;
  double its_tot_time_w;
  double its_tot_time_el;
  double its_tot_time_tot;

  casacore::Matrix<casacore::Bool> itsMaskGridCS;
  casacore::String itsNamePsfOnDisk;
  vector< vector< vector < casacore::Matrix<casacore::Complex> > > > itsStackMuellerNew; 
  
  casacore::Int itsTotalStepsGrid;
  casacore::Int itsTotalStepsDeGrid;
  casacore::Bool itsMasksGridAllDone;
  casacore::Bool itsMasksAllDone;
  casacore::Bool itsAllAtermsDone;
  casacore::Bool its_UseMasksDegrid;
  casacore::Bool its_SingleGridMode;
  casacore::Bool its_makeDirtyCorr;
  casacore::uInt its_NGrids;

  casacore::Timer itsSeconds;
  //casacore::Float its_FillFactor;
  // Get the appropriate data pointer
  casacore::Array<casacore::Complex>* getDataPointer(const casacore::IPosition&, casacore::Bool);

  void ok();

  void init();

  // Is this record on Grid? check both ends. This assumes that the
  // ends bracket the middle
  casacore::Bool recordOnGrid(const casacore::VisBuffer& vb, casacore::Int rownr) const;

  // Image cache
  casacore::LatticeCache<casacore::Complex> * imageCache;

  // Sizes
  casacore::Long cachesize;
  casacore::Int  tilesize;

  // Gridder
  casacore::ConvolveGridder<casacore::Double, casacore::Complex>* gridder;

  casacore::Bool itsUseLinearInterpGridder;
  casacore::Bool itsUseWSplit;


  // Is this tiled?
  casacore::Bool isTiled;

  // Array lattice
  casacore::CountedPtr<casacore::Lattice<casacore::Complex> > arrayLattice;

  // Lattice. For non-tiled gridding, this will point to arrayLattice,
  //  whereas for tiled gridding, this points to the image
  casacore::CountedPtr<casacore::Lattice<casacore::Complex> > lattice;

  casacore::String convType;

  casacore::Float maxAbsData;

  // Useful IPositions
  casacore::IPosition centerLoc, offsetLoc;

  // Image Scaling and offset
  casacore::Vector<casacore::Double> uvScale, uvOffset;

  
  casacore::Array<casacore::Complex> its_stacked_GriddedData;
  casacore::Array<casacore::DComplex> its_stacked_GriddedData2;
  casacore::uInt itsNumCycle;
  

  //vector< casacore::Array<casacore::DComplex> > itsGriddedData2;
  vector< casacore::Matrix<casacore::Complex> > itsSumPB;
  vector< casacore::Matrix<casacore::Double> >  itsSumWeight;
  vector< double > itsSumCFWeight;


  ///casacore::Array<casacore::Complex>  griddedData;
  ///casacore::Array<casacore::DComplex> griddedData2;
  ///casacore::Matrix<casacore::Complex> itsSumPB;
  ///double itsSumWeight;

  casacore::Int priorCacheSize;

  // Grid/degrid zero spacing points?

  casacore::Bool usezero_p;

  //force no padding
  casacore::Bool noPadding_p;

  //Check if using put that avoids non-necessary reads
  casacore::Bool usePut2_p;

  //machine name
  casacore::String machineName_p;

  // Shape of the padded image
  casacore::IPosition padded_shape;

  casacore::Int convSampling;
    casacore::Float pbLimit_p;
    casacore::Int sensitivityPatternQualifier_p;
    casacore::String sensitivityPatternQualifierStr_p;
    casacore::Vector<casacore::Float> pbPeaks;
    casacore::Bool pbNormalized_p;
    // The average PB for sky image normalization
    //
    casacore::CountedPtr<casacore::ImageInterface<casacore::Float> > avgPB_p;
    casacore::CountedPtr<casacore::ImageInterface<casacore::Complex> > avgPBSq_p;

  LofarVisResampler visResamplers_p;

  casacore::Record       itsParameters;
  casacore::MeasurementSet itsMS;
  casacore::Int itsNWPlanes;
  double itsWMax;
  casacore::Double its_PBCut;
  int itsNThread;
  casacore::Bool its_Use_EJones;
  casacore::Double its_TimeWindow;
  //ofstream outFile;
  casacore::Bool its_Apply_Element;
  int its_ApplyBeamCode;
  casacore::Bool its_Already_Initialized;
  casacore::Bool                its_reallyDoPSF;
  casacore::Bool itsDonePB;
  casacore::Double itsUVmin;
  casacore::Double itsUVmax;
  casacore::CountedPtr<LofarConvolutionFunction> itsConvFunc;
  casacore::Vector<casacore::Int> ConjCFMap_p, CFMap_p;
  int itsVerbose;
  int itsMaxSupport;
  casacore::Int itsOversample;
  casacore::Vector< casacore::Double >    itsListFreq;
  casacore::String itsImgName;
  casacore::Matrix<casacore::Bool> itsGridMuellerMask;
  casacore::Matrix<casacore::Bool> itsDegridMuellerMask;
  double itsGriddingTime;
  double itsDegriddingTime;
  double itsCFTime;
  casacore::PrecTimer itsTotalTimer;
  casacore::PrecTimer itsCyrilTimer;

  double itsNextApplyTime;
  int itsCounterTimes;
  int itsStepApplyElement;
  double itsTStartObs;
  double itsDeltaTime;
  casacore::Array<casacore::Complex> itsTmpStackedGriddedData;
  casacore::Array<casacore::Complex> itsGridToDegrid;

  casacore::Vector<casacore::uInt> blIndex;
  vector<int> blStart, blEnd;
  casacore::Vector<casacore::Int> ant1;
  casacore::Vector<casacore::Int> ant2;

  void make_mapping(const casacore::VisBuffer& vb)
  {
  ant1 = vb.antenna1();
  ant2 = vb.antenna2();
    // Determine the baselines in the VisBuffer.
  int nrant = 1 + max(max(ant1), max(ant2));
  // Sort on baseline (use a baseline nr which is faster to sort).
  casacore::Vector<casacore::Int> blnr(nrant*ant1);
  blnr += ant2;  // This is faster than nrant*ant1+ant2 in a single line
  casacore::GenSortIndirect<casacore::Int>::sort (blIndex, blnr);
  // Now determine nr of unique baselines and their start index.
  blStart.reserve (nrant*(nrant+1)/2);
  blEnd.reserve   (nrant*(nrant+1)/2);
  casacore::Int  lastbl     = -1;
  casacore::Int  lastIndex  = 0;
  bool usebl      = false;
  bool allFlagged = true;
  const casacore::Vector<casacore::Bool>& flagRow = vb.flagRow();
  for (uint i=0; i<blnr.size(); ++i) {
    casacore::Int inx = blIndex[i];
    casacore::Int bl = blnr[inx];
    if (bl != lastbl) {
      // New baseline. Write the previous end index if applicable.

      if (usebl  &&  !allFlagged) {
	double Wmean(0.5*(vb.uvw()[blIndex[lastIndex]](2) + vb.uvw()[blIndex[i-1]](2)));
	double w0=abs(vb.uvw()[blIndex[lastIndex]](2));
	double w1=abs(vb.uvw()[blIndex[i-1]](2));
	double wMaxbl=std::max(w0,w1);
	if (wMaxbl <= itsWMax) {
	  //if (abs(Wmean) <= itsWMax) {
	  if (itsVerbose > 1) {
	    cout<<"using w="<<Wmean<<endl;
	  }
	  blStart.push_back (lastIndex);
	  blEnd.push_back (i-1);
	}
      }

      // Skip auto-correlations and high W-values.
      // All w values are close, so if first w is too high, skip baseline.
      usebl = false;

      if (ant1[inx] != ant2[inx]) {
	usebl = true;
      }
      lastbl=bl;
      lastIndex=i;
    }
    // Test if the row is flagged.
    if (! flagRow[inx]) {
      allFlagged = false;
    }
  }
  // Write the last end index if applicable.
  if (usebl  &&  !allFlagged) {
    double Wmean(0.5*(vb.uvw()[blIndex[lastIndex]](2) + vb.uvw()[blIndex[blnr.size()-1]](2)));
    double w0=abs(vb.uvw()[blIndex[lastIndex]](2));
    double w1=abs(vb.uvw()[blIndex[blnr.size()-1]](2));
    double wMaxbl=std::max(w0,w1);
    //if (abs(Wmean) <= itsWMax) {
    if (wMaxbl <= itsWMax) {
	//    if (abs(Wmean) <= itsWMax) {
      //if (itsVerbose > 1) {
	cout<<"...using w="<<Wmean<<endl;
	//}
      blStart.push_back (lastIndex);
      blEnd.push_back (blnr.size()-1);
    }
  }

  }

  vector<vector<casacore::uInt> > make_mapping_time(const casacore::VisBuffer& vb, casacore::uInt spw)
  {
    // Determine the baselines in the VisBuffer.
  ant1.assign(vb.antenna1());
  ant2.assign(vb.antenna2());
  const casacore::Vector<casacore::Double>& times = vb.timeCentroid();

  int nrant = 1 + max(max(ant1), max(ant2));
  // Sort on baseline (use a baseline nr which is faster to sort).
  casacore::Vector<casacore::Int> blnr(nrant*ant1);
  blnr += ant2;  // This is faster than nrant*ant1+ant2 in a single line
  casacore::GenSortIndirect<casacore::Int>::sort (blIndex, blnr);
  // Now determine nr of unique baselines and their start index.

  casacore::Float dtime(its_TimeWindow);
  vector<casacore::uInt> MapChunck;
  vector<vector<casacore::uInt> > Map;
  casacore::Double time0(times[0]);
  casacore::Int bl_now(blnr[blIndex[0]]);
  for(casacore::uInt RowNum=0; RowNum<blIndex.size();++RowNum){
    casacore::uInt irow=blIndex[RowNum];

    casacore::Double timeRow(times[irow]);

    double u=vb.uvw()[irow](0);
    double v=vb.uvw()[irow](1);
    double w=vb.uvw()[irow](2);
    double uvdistance=(0.001)*sqrt(u*u+v*v)/(2.99e8/itsListFreq[spw]);
    casacore::Bool cond0((uvdistance>itsUVmin)&(uvdistance<itsUVmax));
    casacore::Bool cond1(abs(w)<itsWMax);
    if(!(cond0&cond1)){continue;}

    if(((timeRow-time0)>dtime)|(blnr[irow]!=bl_now))
      {
	time0=timeRow;
	Map.push_back(MapChunck);
	MapChunck.resize(0);
	bl_now=blnr[irow];
      }
    MapChunck.push_back(irow);
    }
  Map.push_back(MapChunck);

  /* cout.precision(20); */
  /* for(casacore::uInt i=0; i<Map.size();++i) */
  /*   { */
  /*     for(casacore::uInt j=0; j<Map[i].size();++j) */
  /* 	{ */
  /* 	  casacore::uInt irow=Map[i][j]; */
  /* 	  cout<<i<<" "<<j<<" A="<<ant1[irow]<<","<<ant2[irow]<<" w="<<vb.uvw()[irow](2)<<" t="<<times[irow]<<endl; */
  /* 	} */
  /*   } */

  return Map;
     
  }

  vector<casacore::Int> WIndexMap;
  vector<casacore::uInt> TimesMap;
  //casacore::uInt itsSelAnt0;
  //casacore::uInt itsSelAnt1;
  casacore::Double its_t0;
  casacore::Double its_tSel0;
  casacore::Double its_tSel1;

  vector<vector<vector<casacore::uInt> > > make_mapping_time_W(const casacore::VisBuffer& vb, casacore::uInt spw)
  {
    // Determine the baselines in the VisBuffer.
  ant1.assign(vb.antenna1());
  ant2.assign(vb.antenna2());
  const casacore::Vector<casacore::Double>& times = vb.timeCentroid();
  if(its_t0<0.){its_t0=times[0];}
  WIndexMap.resize(0);

  int nrant = 1 + max(max(ant1), max(ant2));
  casacore::Vector<casacore::Int> WPCoord;
  WPCoord.resize(ant1.size());
  for(casacore::uInt irow=0;irow<WPCoord.size();++irow){
    WPCoord[irow]=itsConvFunc->GiveWindexIncludeNegative(vb.uvw()[irow](2),spw);
  }
  // Sort on baseline (use a baseline nr which is faster to sort).
  casacore::Vector<casacore::Int> blnr(ant2+nrant*ant1+nrant*nrant*(WPCoord+itsNWPlanes));
  //blnr += ant2;  // This is faster than nrant*ant1+ant2 in a single line
  casacore::GenSortIndirect<casacore::Int>::sort (blIndex, blnr);
  // Now determine nr of unique baselines and their start index.

  casacore::Float dtime(its_TimeWindow);
  vector<casacore::uInt> MapChunck;
  vector<vector<casacore::uInt> > MapW;
  vector<vector<vector<casacore::uInt> > > Map;
  casacore::Double time0(-1.);//times[blIndex[0]]);
  casacore::Int bl_now;//blnr[blIndex[0]]);
  casacore::Int iwcoord;//=WPCoord[blIndex[0]]-itsNWPlanes;

  for(casacore::uInt RowNum=0; RowNum<blIndex.size();++RowNum){
    casacore::uInt irow=blIndex[RowNum];
    //cout<<ant1[irow]<<" "<<ant2[irow]<<" "<<times[irow]<<" "<<WPCoord[irow]<<endl;
    
    double u=vb.uvw()[irow](0);
    double v=vb.uvw()[irow](1);
    double w=vb.uvw()[irow](2);
    double uvdistance=(0.001)*sqrt(u*u+v*v)/(2.99e8/itsListFreq[spw]);
    casacore::Bool cond0(((uvdistance>itsUVmin)&(uvdistance<itsUVmax)));
    casacore::Bool cond1(abs(w)<itsWMax);
    //casacore::Bool cond2(((ant1[irow]==8)&(ant2[irow]==0)));
    //if 
    //casacore::Bool cond2(((ant1[irow]==7)&(ant2[irow]==1)));
    casacore::Bool cond2(((ant1[irow]==5)&(ant2[irow]==40)));
    //casacore::Bool cond2((ant1[irow]==7));
    //casacore::Bool cond2((ant2[irow]==0));
    casacore::Double timeRow(times[irow]);
    casacore::Bool cond3((timeRow-its_t0)/60.>its_tSel0);
    casacore::Bool cond4((timeRow-its_t0)/60.<its_tSel1);
    casacore::Bool cond34(cond3&cond4);
    if(its_tSel0==-1.){cond34=true;}
    //if(!(cond0&cond1&cond2&cond34)){continue;}
    if(!(cond0&cond1&cond34)){continue;}

    if(time0==-1.){
      time0=timeRow;
      bl_now=blnr[irow];
      iwcoord=WPCoord[irow];
    }

    if(((timeRow-time0)>dtime)|(blnr[irow]!=bl_now))
      {
	time0=timeRow;
	MapW.push_back(MapChunck);
	MapChunck.resize(0);
	bl_now=blnr[irow];
      }
    if(WPCoord[irow]!=iwcoord){
      Map.push_back(MapW);
      MapW.resize(0);
      WIndexMap.push_back(iwcoord);
      iwcoord=WPCoord[irow];
    }
      
    MapChunck.push_back(irow);

    }
  MapW.push_back(MapChunck);
  WIndexMap.push_back(iwcoord);
  Map.push_back(MapW);


  /* for(casacore::uInt i=0; i<Map.size();++i) */
  /*   { */
  /*     for(casacore::uInt j=0; j<Map[i].size();++j) */
  /* 	{ */
  /* 	  for(casacore::uInt k=0; k<Map[i][j].size();++k) */
  /* 	    { */
  /* 	      casacore::uInt irow=Map[i][j][k]; */
  /* 	      cout<<i<<" "<<j<<" "<<k<<" A="<<ant1[irow]<<","<<ant2[irow]<<" w="<<vb.uvw()[irow](2)<<" windex="<<WIndexMap[i]<<" t="<<times[irow]<<endl; */
  /* 	    } */
  /* 	} */
  /*   } */

  /* for(casacore::uInt i=0; i<WIndexMap.size();++i) */
  /*   { */
  /*     cout<<" windex="<<WIndexMap[i]<<endl; */
  /*   } */

  return Map;
     


     /* } */
     /*  else { */
     /* 	casacore::Float dtime(its_TimeWindow); */
     /* 	casacore::Double time0(times[blIndex[blStart[i]]]); */

     /* 	vector<casacore::uInt> RowChunckStart; */
     /* 	vector<casacore::uInt> RowChunckEnd; */
     /* 	vector<vector< casacore::Float > > WsChunck; */
     /* 	vector< casacore::Float >          WChunck; */
     /* 	vector<casacore::Float> WCFforChunck; */
     /* 	casacore::Float wmin(1.e6); */
     /* 	casacore::Float wmax(-1.e6); */
     /* 	casacore::uInt NRow(blEnd[i]-blStart[i]+1); */
     /* 	casacore::Int NpixMax=0; */
     /* 	casacore::uInt WindexLast=itsConvFunc->GiveWindex(vbs.uvw()(2,blIndex[blStart[i]]),spw); */
     /* 	casacore::uInt Windex; */
     /* 	RowChunckStart.push_back(blStart[i]); */
     /* 	for(casacore::uInt Row=0; Row<NRow; ++Row){ */
     /* 	  casacore::uInt irow(blIndex[blStart[i]+Row]); */
     /* 	  casacore::Double timeRow(times[irow]); */
     /* 	  casacore::Int Npix1=itsConvFunc->GiveWSupport(vbs.uvw()(2,irow),spw); */
     /* 	  NpixMax=std::max(NpixMax,Npix1); */
     /* 	  casacore::Float w(vbs.uvw()(2,irow)); */
     /* 	  Windex=itsConvFunc->GiveWindex(vbs.uvw()(2,irow),spw); */

     /* 	  //if(WindexLast!=Windex) */
     /* 	  if((timeRow-time0)>dtime)//((WindexLast!=Windex)| */
     /* 	    { */
     /* 	      time0=timeRow; */
     /* 	      RowChunckEnd.push_back(blStart[i]+Row-1); */
     /* 	      WsChunck.push_back(WChunck); */
     /* 	      WChunck.resize(0); */
     /* 	      WCFforChunck.push_back((itsConvFunc->wScale()).center(WindexLast)); */
     /* 	      wmin=1.e6; */
     /* 	      wmax=-1.e6; */
     /* 	      if(Row!=(NRow-1)){ */
     /* 		RowChunckStart.push_back(blStart[i]+Row); */
     /* 	      } */
     /* 	      WindexLast=Windex; */
     /* 	    } */
	  
     /* 	  WChunck.push_back(w); */

     /* 	} */
     /* 	WsChunck.push_back(WChunck); */
     /* 	RowChunckEnd.push_back(blEnd[i]); */
     /* 	WCFforChunck.push_back((itsConvFunc->wScale()).center(Windex)); */
     /* 	casacore::uInt irow(blIndex[blEnd[i]]); */
     /* 	casacore::Int Npix1=itsConvFunc->GiveWSupport(vbs.uvw()(2,irow),spw); */
     /* 	NpixMax=std::max(NpixMax,Npix1); */
     /* 	// for(casacore::uInt chunk=0; chunk<RowChunckStart.size();++chunk){ */
     /* 	//   cout<<NRow<<" bl: "<<i<<" || Start("<<RowChunckStart.size()<<"): "<<RowChunckStart[chunk]<<" , End("<<RowChunckEnd.size()<<"): "<<RowChunckEnd[chunk] */
     /* 	//       <<" w="<< 0.5*(vbs.uvw()(2,blIndex[RowChunckEnd[chunk]])+vbs.uvw()(2,blIndex[RowChunckStart[chunk]])) */
     /* 	//       <<" size="<< WsChunck[chunk].size()<<" wCF="<< WCFforChunck[chunk]<<endl; */
	  
     /* 	//   // for(casacore::uInt iii=0; iii< WsChunck[chunk].size();++iii){ */
     /* 	//   //   cout<<WsChunck[chunk][iii]<<" "<<vbs.uvw()(2,blIndex[RowChunckEnd[chunk]]<<endl; */
     /* 	//   // } */

     /* 	// } */

	

     /* 	for(casacore::uInt chunk=0; chunk<RowChunckStart.size();++chunk){ */
     /* 	  casacore::Float WmeanChunk(0.5*(vbs.uvw()(2,blIndex[RowChunckEnd[chunk]])+vbs.uvw()(2,blIndex[RowChunckStart[chunk]]))); */
     /* 	  cout<<times[blIndex[RowChunckEnd[chunk]]]-times[blIndex[RowChunckStart[chunk]]]<<" "<<WmeanChunk<<endl; */
     /* 	  cfStore=  itsConvFunc->makeConvolutionFunction (ant1[ist], ant2[ist], timeChunk,//MaxTime, */
     /* 							  WmeanChunk, */
     /* 							//vbs.uvw()(2,blIndex[RowChunckEnd[chunk]]), */
     /* 							itsDegridMuellerMask, */
     /* 							true, */
     /* 							0.0, */
     /* 							itsSumPB[threadNum], */
     /* 							itsSumCFWeight[threadNum] */
     /* 							,spw,thisterm_p,itsRefFreq, */
     /* 							itsStackMuellerNew[threadNum], */
     /* 							  0);//NpixMax */
     /* 	//visResamplers_p.lofarGridToData_interp(vbs, itsGridToDegrid, */
     /* 	//				       blIndex, RowChunckStart[chunk], RowChunckEnd[chunk], cfStore, WsChunck[chunk], */
     /* 	//				       itsConvFunc->wStep(), WCFforChunck[chunk], itsConvFunc->wCorrGridder()); */
     /* 	visResamplers_p.lofarGridToData(vbs, itsGridToDegrid, */
     /* 					       blIndex, RowChunckStart[chunk], RowChunckEnd[chunk], cfStore); */
     /* 	} */

     /*  } */

  }

  double  itsSupport_Speroidal;

  vector<vector<vector<vector<casacore::uInt> > > > make_mapping_time_W_grid(const casacore::VisBuffer& vb, casacore::uInt spw)
  {
    // Determine the baselines in the VisBuffer.
  ant1.assign(vb.antenna1());
  ant2.assign(vb.antenna2());
  const casacore::Vector<casacore::Double>& times = vb.timeCentroid();
  if(its_t0<0.){its_t0=times[0];}
  WIndexMap.resize(0);
  casacore::Double recipWvl = itsListFreq[spw] / 2.99e8;

  int nrant = 1 + max(max(ant1), max(ant2));
  casacore::Vector<casacore::Int> WPCoord;
  WPCoord.resize(ant1.size());
  for(casacore::uInt irow=0;irow<WPCoord.size();++irow){
    WPCoord[irow]=itsConvFunc->GiveWindexIncludeNegative(vb.uvw()[irow](2),spw);
  }
  // Sort on baseline (use a baseline nr which is faster to sort).
  casacore::Vector<casacore::Int> blnr(ant2+nrant*ant1+nrant*nrant*(WPCoord+itsNWPlanes));
  //blnr += ant2;  // This is faster than nrant*ant1+ant2 in a single line
  casacore::GenSortIndirect<casacore::Int>::sort (blIndex, blnr);
  // Now determine nr of unique baselines and their start index.

  casacore::Float dtime(its_TimeWindow);
  vector<casacore::uInt> MapChunck;
  vector<vector<casacore::uInt> > MapW;
  vector<vector<vector<casacore::uInt> > > Map;

  vector<casacore::Int > xminBL;
  vector<vector<casacore::Int> > xminW;
  vector<casacore::Int > xmaxBL;
  vector<vector<casacore::Int> > xmaxW;
  vector<casacore::Int > yminBL;
  vector<vector<casacore::Int> > yminW;
  vector<casacore::Int > ymaxBL;
  vector<vector<casacore::Int> > ymaxW;

  casacore::Double time0(-1.);//times[blIndex[0]]);
  casacore::Int bl_now;//blnr[blIndex[0]]);
  casacore::Int iwcoord;//=WPCoord[blIndex[0]]-itsNWPlanes;

  float scaling(2.);
  float support((itsSupport_Speroidal-1)/2+1);
  casacore::Int xmin=2147483647;
  casacore::Int xmax=-2147483647;
  casacore::Int ymin=2147483647;
  casacore::Int ymax=-2147483647;

  for(casacore::uInt RowNum=0; RowNum<blIndex.size();++RowNum){
    casacore::uInt irow=blIndex[RowNum];
      
    double u=vb.uvw()[irow](0);
    double v=vb.uvw()[irow](1);
    double w=vb.uvw()[irow](2);
    double uvdistance=(0.001)*sqrt(u*u+v*v)/(2.99e8/itsListFreq[spw]);
    casacore::Bool cond0(((uvdistance>itsUVmin)&(uvdistance<itsUVmax)));
    casacore::Bool cond1(abs(w)<itsWMax);
    casacore::Bool cond2(((ant1[irow]==5)&(ant2[irow]==40)));
    casacore::Double timeRow(times[irow]);
    casacore::Bool cond3((timeRow-its_t0)/60.>its_tSel0);
    casacore::Bool cond4((timeRow-its_t0)/60.<its_tSel1);
    casacore::Bool cond34(cond3&cond4);
    if(its_tSel0==-1.){cond34=true;}
    if(!(cond0&cond1&cond34)){continue;}
    //if(!(cond0&cond1&cond34&cond2)){continue;}

    if(time0==-1.){
      time0=timeRow;
      bl_now=blnr[irow];
      iwcoord=WPCoord[irow];
    }

    if(((timeRow-time0)>dtime)|(blnr[irow]!=bl_now))
      {
	time0=timeRow;
	MapW.push_back(MapChunck);
	MapChunck.resize(0);
	
	xminBL.push_back(xmin);
	xmaxBL.push_back(xmax);
	yminBL.push_back(ymin);
	ymaxBL.push_back(ymax);

	xmin=2147483647;
	xmax=-2147483647;
	ymin=2147483647;
	ymax=-2147483647;

	bl_now=blnr[irow];
      }
    if(WPCoord[irow]!=iwcoord){
      Map.push_back(MapW);
      MapW.resize(0);
      
      xminW.push_back(xminBL);
      xminBL.resize(0);
      xmaxW.push_back(xmaxBL);
      xmaxBL.resize(0);
      yminW.push_back(yminBL);
      yminBL.resize(0);
      ymaxW.push_back(ymaxBL);
      ymaxBL.resize(0);

      WIndexMap.push_back(iwcoord);
      iwcoord=WPCoord[irow];
    }
      
    MapChunck.push_back(irow);
    
    casacore::Int xrow = int(u * uvScale(0) * recipWvl + uvOffset(0));
    casacore::Int yrow = int(v * uvScale(1) * recipWvl + uvOffset(1));
    if(xrow-support<xmin){xmin=xrow-support;};
    if(xrow+support>xmax){xmax=xrow+support;};
    if(yrow-support<ymin){ymin=yrow-support;};
    if(yrow+support>ymax){ymax=yrow+support;};

    }
  MapW.push_back(MapChunck);
  Map.push_back(MapW);
  xminBL.push_back(xmin);
  xmaxBL.push_back(xmax);
  yminBL.push_back(ymin);
  ymaxBL.push_back(ymax);
  xminW.push_back(xminBL);
  xmaxW.push_back(xmaxBL);
  yminW.push_back(yminBL);
  ymaxW.push_back(ymaxBL);

  WIndexMap.push_back(iwcoord);

  /* for(casacore::uInt i=0; i<Map.size();++i) */
  /*   { */
  /*     for(casacore::uInt j=0; j<Map[i].size();++j) */
  /* 	{ */
	  
  /* 	  for(casacore::uInt k=0; k<Map[i][j].size();++k) */
  /* 	    { */
  /* 	      casacore::uInt irow=Map[i][j][k]; */
  /* 	      cout<<"iw="<<i<<" ibl="<<j<<" imap="<<k<<" A="<<ant1[irow]<<","<<ant2[irow]<<" w="<<vb.uvw()[irow](2)<<" windex="<<WIndexMap[i]<<" t="<<times[irow]<<endl; */
  /* 	      double u=vb.uvw()[irow](0); */
  /* 	      double v=vb.uvw()[irow](1); */
  /* 	      casacore::Int xrow=int(float(u)*scaling); */
  /* 	      casacore::Int yrow=int(float(v)*scaling); */
  /* 	      cout<<"   "<<xminW[i][j]<<" ("<<xrow-support<<")"<<endl; */
  /* 	      cout<<"   "<<xmaxW[i][j]<<" ("<<xrow+support<<")"<<endl; */
  /* 	      cout<<"   "<<yminW[i][j]<<" ("<<yrow-support<<")"<<endl; */
  /* 	      cout<<"   "<<ymaxW[i][j]<<" ("<<yrow+support<<")"<<endl; */
  /* 	      cout<<" "<<endl; */
  /* 	    } */
  /* 	} */
  /*   } */

  //  ofstream outFile("output_grids.txt");

  vector<casacore::uInt> MapChunckOut;
  vector<vector<casacore::uInt> > MapWGridOut;
  vector<vector<vector<casacore::uInt> > > MapWOut;
  vector<vector<vector<vector<casacore::uInt> > > > MapOut;

  casacore::vector<casacore::IPosition > posBlock;

  for(casacore::uInt i=0; i<Map.size();++i)
    {
      MapWGridOut.resize(0);
      MapWOut.resize(0);
      casacore::Vector<casacore::Bool> done;
      done.resize(Map[i].size());
      done=false;
      casacore::Bool alldone(false);
      casacore::Bool cond_xmin,cond_xmax,cond_ymin,cond_ymax;
      casacore::uInt iblock(0);
      //MapWGridOut.push_back(Map[i][0]);

      posBlock.resize(0);
      casacore::IPosition pos(2,1,1);
      //pos(0)=i;
      //pos(1)=0;
      //posBlock.push_back(pos);

      //cout<<"  plane w="<<i<<" nbl_blocks="<< Map[i].size()<<endl;

      while(!alldone){
	
	for(casacore::uInt j=0; j<Map[i].size();++j)
	  {
	    // Find if baseline j has overlap with the current grid
	    if(done[j]==true){continue;}
	    casacore::Bool NoOverlap(true);
	    for(casacore::uInt jj=0; jj<MapWGridOut.size();++jj)
	      {
		cond_xmin=xminW[i][j]<=xmaxW[posBlock[jj](0)][posBlock[jj](1)];
		cond_xmax=xmaxW[i][j]>=xminW[posBlock[jj](0)][posBlock[jj](1)];
		cond_ymin=yminW[i][j]<=ymaxW[posBlock[jj](0)][posBlock[jj](1)]; 
		cond_ymax=ymaxW[i][j]>=yminW[posBlock[jj](0)][posBlock[jj](1)];
		casacore::Bool condIsOverlap(cond_xmin&&cond_xmax&&cond_ymin&&cond_ymax);
		if(condIsOverlap){
		  NoOverlap=false;
		  break;
		}
	      }
	    if(NoOverlap){
	      MapWGridOut.push_back(Map[i][j]);
	      done[j]=true;
	      pos(0)=i;
	      pos(1)=j;
	      posBlock.push_back(pos);
	    }
	  }
	
	alldone=true;
	for(casacore::uInt j=0; j<done.size();++j)
	  {
	    if(done[j]==false){alldone=false;break;}
	  }

	/* for(casacore::uInt iii=0; iii<MapWGridOut.size();++iii){ */
	/*   casacore::uInt icoord(posBlock[iii](0)); */
	/*   casacore::uInt jcoord(posBlock[iii](1)); */
	/*   outFile<<"   "<<i<<" "<<iblock<<" "<<xminW[icoord][jcoord]<<" "<<xmaxW[icoord][jcoord]<<" "<<yminW[icoord][jcoord]<<" "<<ymaxW[icoord][jcoord]<<endl; */
	/* } */

	posBlock.resize(0);
	MapWOut.push_back(MapWGridOut);
	MapWGridOut.resize(0);
	iblock+=1;
	

      }
      MapOut.push_back(MapWOut);
      MapWOut.resize(0);

    }

  /* for(casacore::uInt i=0; i<MapOut.size();++i){ */
  /*   for(casacore::uInt j=0; j<MapOut[i].size();++j){ */
  /*     casacore::uInt icoord(posBlock[iii](0)); */
  /*     casacore::uInt jcoord(posBlock[iii](1)); */
  /*     outFile<<"   "<<i<<" "<<iblock<<" "<<xminW[icoord][jcoord]<<" "<<xmaxW[icoord][jcoord]<<" "<<yminW[icoord][jcoord]<<" "<<ymaxW[icoord][jcoord]<<endl; */
  /*   } */
  /* } */

  return MapOut;

  }


  ///////////////////////////////////////

  FFTCMatrix  FFTMachine;

  void dofft(casacore::Matrix<casacore::Complex>& arr, bool direction)
{
  int sz(arr.nrow());
  int nthreads(OpenMP::maxThreads());

  if(direction==true)
  {
    FFTMachine.normalized_forward(arr.nrow(),arr.data(),nthreads, FFTW_MEASURE);
  }

  if(direction==false)
  {
    FFTMachine.normalized_backward(arr.nrow(),arr.data(),nthreads, FFTW_MEASURE);
  }

}

  ///////////////////////////////////////
  vector<FFTCMatrix>  VecFFTMachine;
  void dofftVec(casacore::Matrix<casacore::Complex>& arr, bool direction, int nth=0, int pol=0)
{
  int sz(arr.nrow());
  int nthreads(OpenMP::maxThreads());
  if(nth!=0){nthreads=nth;}

  if(direction==true)
  {
    VecFFTMachine[pol].normalized_forward(arr.nrow(),arr.data(),nthreads, FFTW_MEASURE);
  }

  if(direction==false)
  {
    VecFFTMachine[pol].normalized_backward(arr.nrow(),arr.data(),nthreads, FFTW_MEASURE);
  }

}




  ////////////////////////////////////////

  template <class T>
  void store (const casacore::DirectionCoordinate &dir, const casacore::Matrix<T> &data,
              const string &name)
  {
    //cout<<"Saving... "<<name<<endl;
    casacore::Vector<casacore::Int> stokes(1);
    stokes(0) = casacore::Stokes::I;
    casacore::CoordinateSystem csys;
    csys.addCoordinate(dir);
    csys.addCoordinate(casacore::StokesCoordinate(stokes));
    csys.addCoordinate(casacore::SpectralCoordinate(casacore::MFrequency::TOPO, 60e6, 1.0, 0.0, 60e6));
    casacore::PagedImage<T> im(casacore::TiledShape(casacore::IPosition(4, data.shape()(0), data.shape()(1), 1, 1)), csys, name);
    im.putSlice(data, casacore::IPosition(4, 0, 0, 0, 0));
  }

  template <class T>
  void store(const casacore::Matrix<T> &data, const string &name)
  {
    casacore::Matrix<casacore::Double> xform(2, 2);
    xform = 0.0;
    xform.diagonal() = 1.0;
    casacore::Quantum<casacore::Double> incLon((8.0 / data.shape()(0)) * casacore::C::pi / 180.0, "rad");
    casacore::Quantum<casacore::Double> incLat((8.0 / data.shape()(1)) * casacore::C::pi / 180.0, "rad");
    casacore::Quantum<casacore::Double> refLatLon(45.0 * casacore::C::pi / 180.0, "rad");
    casacore::DirectionCoordinate dir(casacore::MDirection::J2000, casacore::Projection(casacore::Projection::SIN),
                            refLatLon, refLatLon, incLon, incLat,
                            xform, data.shape()(0) / 2, data.shape()(1) / 2);
    store(dir, data, name);
  }

  template <class T>
  void store(const casacore::Cube<T> &data, const string &name)
  {
    casacore::Matrix<casacore::Double> xform(2, 2);
    xform = 0.0;
    xform.diagonal() = 1.0;
    casacore::Quantum<casacore::Double> incLon((8.0 / data.shape()(0)) * casacore::C::pi / 180.0, "rad");
    casacore::Quantum<casacore::Double> incLat((8.0 / data.shape()(1)) * casacore::C::pi / 180.0, "rad");
    casacore::Quantum<casacore::Double> refLatLon(45.0 * casacore::C::pi / 180.0, "rad");
    casacore::DirectionCoordinate dir(casacore::MDirection::J2000, casacore::Projection(casacore::Projection::SIN),
                            refLatLon, refLatLon, incLon, incLat,
                            xform, data.shape()(0) / 2, data.shape()(1) / 2);
    store(dir, data, name);
  }

  template <class T>
  void store(const casacore::DirectionCoordinate &dir, const casacore::Cube<T> &data,
             const string &name)
  {
//     AlwaysAssert(data.shape()(2) == 4, SynthesisError);
    //cout<<"Saving... "<<name<<endl;
    casacore::Vector<casacore::Int> stokes(4);
    stokes(0) = casacore::Stokes::XX;
    stokes(1) = casacore::Stokes::XY;
    stokes(2) = casacore::Stokes::YX;
    stokes(3) = casacore::Stokes::YY;
    casacore::CoordinateSystem csys;
    csys.addCoordinate(dir);
    csys.addCoordinate(casacore::StokesCoordinate(stokes));
    csys.addCoordinate(casacore::SpectralCoordinate(casacore::MFrequency::TOPO, 60e6, 0.0, 0.0, 60e6));
    casacore::PagedImage<T>
      im(casacore::TiledShape(casacore::IPosition(4, data.shape()(0), data.shape()(1), 4, 1)),
         csys, name);
    im.putSlice(data, casacore::IPosition(4, 0, 0, 0, 0));
  }
      /* template <class T> */
      /*   void store(const Cube<T> &data, const string &name) */
      /*   { */

      /*     CoordinateSystem csys; */
      /*     casacore::Matrix<casacore::Double> xform(2, 2); */
      /*     xform = 0.0; */
      /*     xform.diagonal() = 1.0; */
      /*     Quantum<casacore::Double> incLon((8.0 / data.shape()(0)) * C::pi / 180.0, "rad"); */
      /*     Quantum<casacore::Double> incLat((8.0 / data.shape()(1)) * C::pi / 180.0, "rad"); */
      /*     Quantum<casacore::Double> refLatLon(45.0 * C::pi / 180.0, "rad"); */
      /*     csys.addCoordinate(DirectionCoordinate(MDirection::J2000, Projection(Projection::SIN), */
      /*                        refLatLon, refLatLon, incLon, incLat, */
      /*                        xform, data.shape()(0) / 2, data.shape()(1) / 2)); */

      /*     casacore::Vector<casacore::Int> stokes(4); */
      /*     stokes(0) = Stokes::XX; */
      /*     stokes(1) = Stokes::XY; */
      /*     stokes(2) = Stokes::YX; */
      /*     stokes(3) = Stokes::YY; */
      /*     csys.addCoordinate(StokesCoordinate(stokes)); */
      /*     csys.addCoordinate(SpectralCoordinate(casacore::MFrequency::TOPO, 60e6, 0.0, 0.0, 60e6)); */

      /*     PagedImage<T> im(TiledShape(IPosition(4, data.shape()(0), data.shape()(1), 4, 1)), csys, name); */
      /*     im.putSlice(data, IPosition(4, 0, 0, 0, 0)); */
      /*   } */


};

} //# end namespace

#endif
