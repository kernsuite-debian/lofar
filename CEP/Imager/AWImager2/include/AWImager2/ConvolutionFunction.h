//# ConvolutionFunction.h: Compute LOFAR convolution functions on demand.
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
//# $Id$

#ifndef LOFAR_LOFARFT_CONVOLUTIONFUNCTION_H
#define LOFAR_LOFARFT_CONVOLUTIONFUNCTION_H

#include <AWImager2/ATerm.h>
#include <AWImager2/WTerm.h>
#include <AWImager2/CFStore.h>
#include <AWImager2/FFTCMatrix.h>
#include <Common/Timer.h>
#include <Common/ParameterSet.h>

#include <casacore/casa/Arrays/Cube.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/casa/Arrays/MatrixMath.h>
#include <casacore/casa/Arrays/ArrayIter.h>
#include <casacore/casa/Arrays/ArrayMath.h>
#include <casacore/images/Images/PagedImage.h>
#include <casacore/casa/Utilities/Assert.h>
#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/coordinates/Coordinates/CoordinateSystem.h>
#include <casacore/coordinates/Coordinates/SpectralCoordinate.h>
#include <casacore/coordinates/Coordinates/StokesCoordinate.h>
#include <casacore/coordinates/Coordinates/DirectionCoordinate.h>
#include <casacore/casa/OS/PrecTimer.h>

namespace LOFAR {
namespace LofarFT {

class ConvolutionFunction
{

public:
  
  typedef ATerm::Polarization Polarization; 
  
  ConvolutionFunction(
    const casacore::MeasurementSet& ms,
    double wmax,
    casacore::uInt oversample,
    casacore::Int verbose,
    casacore::Int maxsupport,
    ParameterSet& parset);

  void init(
    const casacore::IPosition& shape,
    const casacore::DirectionCoordinate& coordinates,
    const casacore::String& imgName);

  virtual ~ConvolutionFunction () {};
  
  Polarization::Type image_polarization() const;

  // set frequency channels, creates itsChanMap
  casacore::Vector<casacore::Int> set_frequency(const casacore::Vector<casacore::Double> &frequency);
  
  // Show the relative timings of the various steps.
  void showTimings (std::ostream&, double duration, double timeCF) const;

  // Show percentage of value in total with 1 decimal.
  static void showPerc1 (std::ostream& os, double value, double total);

  // Compute and store W-terms and A-terms in the fourier domain
  void store_all_W_images();

//   // Get the spheroidal cut.
//   const casacore::Matrix<casacore::Float>& getSpheroidCut();

  // Get the spheroidal cut from the file.
  static casacore::Matrix<casacore::Float> getSpheroidCut (const casacore::String& imgName);

  // Get the average PB from the file.
  static casacore::Matrix<casacore::Float> getAveragePB (const casacore::String& imgName);


  // Compute the fft of the beam at the minimal resolution for all antennas,
  // and append it to a map object with a (double time) key.
  void computeAterm(casacore::Double time);

//   void computeElementBeam(const casacore::DirectionCoordinate &coordinates, const casacore::IPosition &shape, casacore::Double time);
  void computeElementBeam(casacore::Double time);

  // Compute the convolution function for all channel, for the polarisations
  // specified in the Mueller_mask matrix
  // Also specify weither to compute the Mueller matrix for the forward or
  // the backward step. A dirty way to calculate the average beam has been
  // implemented, by specifying the beam correcting to the given baseline
  // and timeslot.
  // RETURNS in a LofarCFStore: result[channel][Mueller row][Mueller column]

  virtual CFStore makeConvolutionFunction(
    casacore::uInt stationA, 
    casacore::uInt stationB,
    casacore::Double time, 
    casacore::Double w,
    const casacore::Matrix<casacore::Float> &sum_weight,
    const vector<bool> &channel_selection,
    double w_offset);

  // Returns the average Primary Beam from the disk
  casacore::Matrix<float> give_avg_pb();

  // Compute the average Primary Beam from the Stack of convolution functions
  casacore::Matrix<casacore::Float> getAveragePB();
  
  casacore::Matrix<casacore::Float> getSpheroidal();

  casacore::Matrix<casacore::Float> getSpheroidalCF();

  // Zero padding of a Cube
  casacore::Cube<casacore::Complex> zero_padding(
    const casacore::Cube<casacore::Complex>& Image, 
    int npixel_out);

  // Zero padding of a Matrix
  casacore::Matrix<casacore::Complex> zero_padding(
    const casacore::Matrix<casacore::Complex>& Image, 
    int npixel_out);

  // Get the W scale.
  const WScale& wScale() const
    { return itsWScale; }
    
  casacore::Vector< casacore::Double > &get_frequency_list()
    {return itsFrequencyList;}

  void applyWterm(casacore::Array<casacore::Complex>& grid, double w);

  void applyElementBeam(casacore::Array<casacore::Complex>& grid, casacore::Bool conjugate = casacore::False);
  
  // Get the reference frequency
  const casacore::Double refFrequency() const
  { return itsRefFrequency;}
  
  casacore::Double get_w_from_support(casacore::Int support = 0) const;


protected:
  
  casacore::Matrix<casacore::Float> itsSumCF;
  casacore::Float itsSumWeight;
  
  casacore::Int itsSupportCF;
  casacore::Matrix<casacore::Float> itsAveragePB;
  casacore::Matrix<casacore::Float> itsSpheroidal;
  casacore::Matrix<casacore::Float> itsSpheroidalCF;
  casacore::Cube<casacore::Complex> itsElementBeam;

  void FindNWplanes();
  
  void normalized_fft (
    casacore::Matrix<casacore::Complex>&, 
    bool toFreq=true);
  
  void normalized_fft (
    casacore::PrecTimer& timer, 
    casacore::Matrix<casacore::Complex>&, bool toFreq=true);

  casacore::MEpoch observationStartTime(
    const casacore::MeasurementSet &ms,
    casacore::uInt idObservation) const;

  casacore::Double observationReferenceFreq(
    const casacore::MeasurementSet &ms,
    casacore::uInt idDataDescription);

  // Estime spheroidal convolution function from the support of the fft
  // of the spheroidal in the image plane
  casacore::Double makeSpheroidCut();

  // Return the angular resolution required for making the image of the
  // angular size determined by coordinates and shape.
  // The resolution is assumed to be the same on both direction axes.
  casacore::Double estimateWResolution(
    const casacore::IPosition &shape,
    casacore::Double pixelSize,
    casacore::Double w) const;

  // Return the angular resolution required for making the image of the
  // angular size determined by coordinates and shape.
  // The resolution is assumed to be the same on both direction axes.
  casacore::Double estimateAResolution(
    const casacore::IPosition &shape,
    const casacore::DirectionCoordinate &coordinates) const;



  //# Data members.
  casacore::IPosition           itsShape;
  casacore::DirectionCoordinate itsCoordinates;
  WScale                    itsWScale;
  WTerm                     itsWTerm;
  casacore::CountedPtr<ATerm>   itsATerm;
  casacore::Double              itsMaxW;
  casacore::Double              itsPixelSizeSpheroidal;
  casacore::uInt                itsNWPlanes;
  casacore::uInt                itsNStations;
  casacore::uInt                itsOversampling;
  casacore::uInt                itsNChannel;
  casacore::Double              itsRefFrequency;
  //# Stack of the convolution functions for the average PB calculation
  casacore::Matrix<casacore::Complex>     itsSpheroid_cut;
  //# Stack of the convolution functions for the average PB calculation
  casacore::Matrix<casacore::Float>       itsSpheroid_cut_im;
  //# List of the ferquencies the CF have to be caluclated for
  casacore::Vector< casacore::Double >    itsFrequencyList;
  casacore::Vector< casacore::Int >      itsChanMap;
  vector< casacore::Matrix<casacore::Complex> > itsWplanesStore;
  //# Aterm_store[double time][antenna][channel]=Cube[Npix,Npix,4]
  map<casacore::Double, vector< vector< casacore::Cube<casacore::Complex> > > > itsAtermStore;
  //# Average primary beam
  casacore::Matrix<casacore::Float>       itsIm_Stack_PB_CF0;
  casacore::Int                 itsVerbose;
  casacore::Int                 itsMaxSupport;
  casacore::String              itsImgName;
  vector<FFTCMatrix>  itsFFTMachines;
  casacore::Double              itsTimeW;
  casacore::Double              itsTimeWpar;
  casacore::Double              itsTimeWfft;
  unsigned long long  itsTimeWcnt;
  casacore::Double              itsTimeA;
  casacore::Double              itsTimeApar;
  casacore::Double              itsTimeAfft;
  unsigned long long  itsTimeAcnt;
  casacore::Double              itsTimeCFpar;
  casacore::Double              itsTimeCFfft;
  unsigned long long  itsTimeCFcnt;
  casacore::Int                 itsChan_block_size;
};


} //# end namespace LofarFT
} //# end namespace LOFAR

#endif
