//# LofarConvolutionFunction.h: Compute LOFAR convolution functions on demand.
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

#ifndef LOFARFT_LOFARCONVOLUTIONFUNCTION_H
#define LOFARFT_LOFARCONVOLUTIONFUNCTION_H

#include <AWImager2/LofarATerm.h>
#include <AWImager2/LofarWTerm.h>
#include <AWImager2/LofarCFStore.h>
#include <AWImager2/FFTCMatrix.h>
#include <Common/Timer.h>

#include <casacore/casa/Arrays/Cube.h>
#include <casacore/casa/Arrays/Matrix.h>
#include <casacore/casa/Arrays/MatrixMath.h>
#include <casacore/casa/Arrays/ArrayIter.h>
#include <casacore/casa/Arrays/ArrayMath.h>
#include <casacore/images/Images/PagedImage.h>
#include <casacore/casa/Utilities/Assert.h>
#include <casacore/casa/sstream.h>
#include <casacore/ms/MeasurementSets/MeasurementSet.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/coordinates/Coordinates/CoordinateSystem.h>
#include <casacore/coordinates/Coordinates/SpectralCoordinate.h>
#include <casacore/coordinates/Coordinates/StokesCoordinate.h>
#include <casacore/coordinates/Coordinates/DirectionCoordinate.h>
#include <casacore/casa/OS/PrecTimer.h>

#include <casacore/lattices/Lattices/ArrayLattice.h>
#include <casacore/lattices/LatticeMath/LatticeFFT.h>

namespace LOFAR
{

  // Functions to store a 2D or 3D array in an PagedImage file.
  template <class T>
  void store(const casacore::DirectionCoordinate &dir, const casacore::Matrix<T> &data, const string &name);

  template <class T>
  void store(const casacore::DirectionCoordinate &dir, const casacore::Cube<T> &data, const string &name);

  template <class T>
  void store(const casacore::Matrix<T> &data, const string &name);

  template <class T>
  void store(const casacore::Cube<T> &data, const string &name);


  class LofarConvolutionFunction
  {

  public:
    LofarConvolutionFunction(const casacore::IPosition& shape,    //# padded shape
                             const casacore::IPosition& imageShape,
                             const casacore::DirectionCoordinate& coordinates,
                             const casacore::MeasurementSet& ms,
                             casacore::uInt nW, 
                             double Wmax,
                             casacore::uInt oversample,
                             casacore::Int verbose,
                             casacore::Int maxsupport,
                             const casacore::String& imgName,
			     casacore::Bool Use_EJones,
			     casacore::Bool Apply_Element,
			     int ApplyBeamCode,
                             const casacore::Record& parameters,
			     vector< vector< vector < casacore::Matrix<casacore::Complex> > > > & StackMuellerNew
                            );
    //,
    //			     Int TaylorTerm,
    //			     Double RefFreq);

//      ~LofarConvolutionFunction ()
//      {
//      }


    // Show the relative timings of the various steps.
    void showTimings (std::ostream&, double duration, double timeCF) const;

    // Show percentage of value in total with 1 decimal.
    static void showPerc1 (std::ostream& os, double value, double total);

    // Compute and store W-terms and A-terms in the fourier domain
    void store_all_W_images();

    // Get the spheroidal cut.
    const casacore::Matrix<casacore::Float>& getSpheroidCut();
    casacore::Matrix<casacore::Float> getSpheroid(casacore::uInt npix);

    // Get the spheroidal cut from the file.
    static casacore::Matrix<casacore::Float> getSpheroidCut (const casacore::String& imgName);

    // Get the average PB from the file.
    static casacore::Matrix<casacore::Float> getAveragePB (const casacore::String& imgName);


    // Compute the fft of the beam at the minimal resolution for all antennas,
    // and append it to a map object with a (double time) key.
    void computeAterm(casacore::Double time);
    
    vector<casacore::Double> VecTimesAterm;
    
    void computeVecAterm(casacore::Double t0, casacore::Double t1, casacore::Double dt)
    {

      casacore::Double tmax(0.);
      for(casacore::uInt i=0; i<VecTimesAterm.size(); ++i){
	if(VecTimesAterm[i]>tmax){
	  tmax=VecTimesAterm[i];
	}
      }

      if(t0>tmax){
	double d = std::min(dt, t1-t0);
	for(casacore::Double tat=t0+d/2.;tat<t1; tat+=d)
	  {
	    computeAterm(tat);
	    VecTimesAterm.push_back(tat);
	  }
      }

    }

    casacore::Double GiveClosestTimeAterm(casacore::Double tat)
    {
      casacore::Double dtmin(1e30);
      casacore::Double tmin(0.);
      casacore::Double dt;
      for(casacore::uInt ind=0; ind <VecTimesAterm.size(); ++ind)
	{
	  dt=abs(tat-VecTimesAterm[ind]);
	  if(dt<dtmin){
	    tmin=VecTimesAterm[ind];
	    dtmin=dt;
	  }
	}
      return tmin;
    }

    // Compute the convolution function for all channel, for the polarisations
    // specified in the Mueller_mask matrix
    // Also specify weither to compute the Mueller matrix for the forward or
    // the backward step. A dirty way to calculate the average beam has been
    // implemented, by specifying the beam correcting to the given baseline
    // and timeslot.
    // RETURNS in a LofarCFStore: result[channel][Mueller row][Mueller column]
    LofarCFStore makeConvolutionFunction(casacore::uInt stationA, casacore::uInt stationB,
                                         casacore::Double time, casacore::Double w,
                                         const casacore::Matrix<bool>& Mask_Mueller,
                                         bool degridding_step,
                                         double Append_average_PB_CF,
                                         casacore::Matrix<casacore::Complex>& Stack_PB_CF,
                                         double& sum_weight_square,
					 casacore::Vector<casacore::uInt> ChanBlock, casacore::Int TaylorTerm, double RefFreq,
					 vector< vector < casacore::Matrix<casacore::Complex> > > & StackMuellerNew,
					 casacore::Int ImposeSupport, casacore::Bool UseWTerm);

    LofarCFStore makeConvolutionFunctionAterm(casacore::uInt stationA, casacore::uInt stationB,
                                         casacore::Double time, casacore::Double w,
                                         const casacore::Matrix<bool>& Mask_Mueller,
                                         bool degridding_step,
                                         double Append_average_PB_CF,
                                         casacore::Matrix<casacore::Complex>& Stack_PB_CF,
                                         double& sum_weight_square,
					 casacore::uInt spw, casacore::Int TaylorTerm, double RefFreq,
					 vector< vector < casacore::Matrix<casacore::Complex> > > & StackMuellerNew,
					 casacore::Int ImposeSupport);

    casacore::Int GiveWSupport(casacore::Double w, casacore::uInt spw);
    casacore::uInt GiveWindex(casacore::Double w, casacore::uInt spw);
    casacore::Int GiveWindexIncludeNegative(casacore::Double w, casacore::uInt spw);
    void initMeanWStepsGridder();
    casacore::Int FindNWplanes();

    casacore::Array<casacore::Complex>  ApplyElementBeam(casacore::Array<casacore::Complex> input_grid, casacore::Double time, casacore::uInt spw, const casacore::Matrix<bool>& Mask_Mueller_in, bool degridding_step);
    casacore::Array<casacore::Complex> ApplyElementBeam_Image(casacore::Array<casacore::Complex>& input_grid, casacore::Double timeIn, casacore::uInt spw, const casacore::Matrix<bool>& Mask_Mueller_in2, bool degridding_step);
    casacore::Array<casacore::Complex>  ApplyElementBeam2(casacore::Array<casacore::Complex>& input_grid, casacore::Double time, casacore::uInt spw, const casacore::Matrix<bool>& Mask_Mueller_in, bool degridding_step, casacore::Int UsedMask=-1);
    casacore::Array<casacore::Complex>  ApplyElementBeam3(casacore::Array<casacore::Complex>& input_grid, casacore::Double time, casacore::uInt spw, const casacore::Matrix<bool>& Mask_Mueller_in, bool degridding_step, vector< casacore::Array<casacore::Complex> >& gridsparalel, casacore::Int UsedMask);
    casacore::Array<casacore::Complex>  ApplyWterm(casacore::Array<casacore::Complex>& input_grid, casacore::uInt spw, bool degridding_step, casacore::Int w_index, vector< casacore::Array<casacore::Complex> >& gridsparalel, casacore::Int TnumMask, casacore::Int WnumMask);
    void ApplyWterm_Image(casacore::Array<casacore::Complex>& input_grid, casacore::Array<casacore::Complex>& output_grid, casacore::uInt spw, bool degridding_step, casacore::Int w_index);
    void ConvolveArrayArrayParallel( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				     const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel);
    void ConvolveArrayArrayParallel2( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel);
    void ConvolveArrayArrayParallel2( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel, casacore::Matrix<casacore::Bool> MaskIn);
    void ConvolveArrayArrayParallel3( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel);
    void ConvolveArrayArrayParallel3( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel, casacore::Matrix<casacore::Bool> MaskIn);
    void ConvolveArrayArrayParallel4( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel, casacore::Matrix<casacore::uShort> MaskIn);
    void ConvolveArrayArrayParallel4( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout, casacore::uInt polNum,
				      const casacore::Matrix<casacore::Complex>& ConvFunc, vector< casacore::Array<casacore::Complex> >&  GridsParallel, casacore::Matrix<casacore::uShort> MaskIn);
    void SumGridsOMP(casacore::Array<casacore::Complex>& grid, const vector< casacore::Array<casacore::Complex> >& GridToAdd0 );
    void SumGridsOMP(casacore::Array<casacore::Complex>& grid, const vector< casacore::Array<casacore::Complex> >& GridToAdd0 , casacore::uInt PolNumIn, casacore::uInt PolNumOut);
    void SumGridsOMP(casacore::Array<casacore::Complex>& grid, const casacore::Array<casacore::Complex> & GridToAdd0 , casacore::uInt PolNumIn, casacore::uInt PolNumOut);

    
    // Returns the average Primary Beam from the disk
    casacore::Matrix<float> Give_avg_pb();

    // Compute the average Primary Beam from the Stack of convolution functions
    casacore::Matrix<casacore::Float> Compute_avg_pb(casacore::Matrix<casacore::Complex> &Sum_Stack_PB_CF,
                                 double sum_weight_square);

    // Zero padding of a Cube
    casacore::Cube<casacore::Complex> zero_padding(const casacore::Cube<casacore::Complex>& Image, int Npixel_Out);

    // Zero padding of a Matrix
    casacore::Matrix<casacore::Complex> zero_padding(const casacore::Matrix<casacore::Complex>& Image, int Npixel_Out);
    casacore::Matrix<casacore::Complex> zero_padding(const casacore::Matrix<casacore::Complex>& Image, casacore::Matrix<casacore::Complex>& Image_Enlarged, bool tozero);

    

    // Get the W scale.
    const WScale& wScale() const
      { return m_wScale; }

    casacore::Float wStep()
      { return its_wStep; }
    vector<casacore::Complex> wCorrGridder()
      { return its_wCorrGridder; }

    vector<casacore::Complex> its_wCorrGridder;
    vector<casacore::Matrix< casacore::Complex > > its_wCorrGridderMatrix;
    casacore::Float its_wStep;
    casacore::Bool its_UseWSplit;

    vector< casacore::Matrix< casacore::Bool > > itsVectorMasksDegridElement;
    vector< vector< casacore::Matrix< casacore::Bool > > > itsVecMasks;
    vector< vector< casacore::Matrix< casacore::uShort > > > itsVecMasksNew;
    vector< vector< casacore::Matrix< casacore::uShort > > > itsVecMasksNewW;
    vector< casacore::Matrix< casacore::uShort > > itsVecMasksNewElement;
    casacore::uInt NBigChunks;
    
    void initStoreMasks()
    {
      NBigChunks=20;
      casacore::Int sizeVec(2*m_nWPlanes);
      itsVecMasks.resize(NBigChunks);
      for(casacore::uInt i=0; i<NBigChunks; ++i)
	{
	  itsVecMasks[i].resize(sizeVec);
	}
    }
    
    void initStoreMasksNew()
    {
      NBigChunks=20;
      casacore::Int sizeVec(2*m_nWPlanes);
      itsVecMasksNew.resize(NBigChunks);
      itsVecMasksNewW.resize(NBigChunks);
      itsVecMasksNewElement.resize(0);
      for(casacore::uInt i=0; i<NBigChunks; ++i)
	{
	  itsVecMasksNew[i].resize(sizeVec);
	  itsVecMasksNewW[i].resize(sizeVec);
	}
    }

    void MakeMaskDegrid( const casacore::Array<casacore::Complex>& gridin, casacore::Int NumMask)
    {

      casacore::String MaskName("JAWS_products/Mask" + casacore::String::toString(NumMask) + ".boolim");
      casacore::File MaskFile(MaskName);
      if(!MaskFile.exists()){
	//cout<<"... Making Masks ..."<<endl;
	casacore::Matrix<casacore::Bool> Mask(casacore::IPosition(2,gridin.shape()[0],gridin.shape()[0]),false);
	casacore::Matrix<casacore::Int> IntMask(casacore::IPosition(2,gridin.shape()[0],gridin.shape()[0]),false);
	int GridSize(gridin.shape()[0]);
	const casacore::Complex* inPtr = gridin.data();
	casacore::Bool* outPtr = Mask.data();
	for (int i=0; i<GridSize; ++i) {
	  for (int j=0; j<GridSize; ++j) {
	    if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	      (*(outPtr)) = true;
	    }
	    inPtr++;
	    outPtr++;
	  }
	}
	//itsVectorMasksDegridElement.push_back(Mask);
	
	store(Mask,MaskName);
	//cout<<"... Done Making Masks ..."<<endl;
      }
    }

    
    void MakeVectorMaskWplanes( const casacore::Array<casacore::Complex>& gridin, casacore::Int NumTime, casacore::Int NumWplane)
    {
      casacore::String MaskName("JAWS_products/Mask.T" + casacore::String::toString(NumTime) + ".W" + casacore::String::toString(NumWplane) + ".boolim");
      casacore::File MaskFile(MaskName);


      if(!MaskFile.exists()){
	//cout<<"... Making Masks ..."<<endl;
	casacore::Matrix<casacore::Bool> Mask(casacore::IPosition(2,gridin.shape()[0],gridin.shape()[0]),false);
	casacore::Matrix<casacore::Int> IntMask(casacore::IPosition(2,gridin.shape()[0],gridin.shape()[0]),false);
	int GridSize(gridin.shape()[0]);
	const casacore::Complex* inPtr = gridin.data();
	casacore::Bool* outPtr = Mask.data();
	for (int i=0; i<GridSize; ++i) {
	  for (int j=0; j<GridSize; ++j) {
	    if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	      (*(outPtr)) = true;
	    }
	    inPtr++;
	    outPtr++;
	  }
	}
	//itsVectorMasksDegridElement.push_back(Mask);
	store(Mask,MaskName);
	//cout<<"... Done Making Masks ..."<<endl;
      }
    }

    void MakeVectorMaskWplanesNew( const casacore::Array<casacore::Complex>& gridin, casacore::Int NumTime, casacore::Int NumWplane, casacore::Bool /*grid*/, casacore::Bool /*Element*/, casacore::Int MaskType)
    {
      //cout<<"make mask "<<grid<<endl;
      casacore::String MaskName;
      casacore::File MaskFile;
      if(MaskType==0){
	MaskName="JAWS_products/MaskGrid.T"+casacore::String::toString(NumTime)+".W"+casacore::String::toString(NumWplane)+".boolim";
	casacore::File MaskFilein(MaskName);
	MaskFile=MaskFilein;
	} 
      if(MaskType==1){
	MaskName="JAWS_products/MaskDeGrid.T"+casacore::String::toString(NumTime)+".W"+casacore::String::toString(NumWplane)+".boolim";
	casacore::File MaskFilein(MaskName);
	MaskFile=MaskFilein;
      }
      if(MaskType==2){
	MaskName="JAWS_products/MaskGrid.Element.T"+casacore::String::toString(NumTime)+".boolim";
	casacore::File MaskFilein(MaskName);
	MaskFile=MaskFilein;
      }

      if(!MaskFile.exists()){
    	casacore::Matrix<casacore::Int> IntMask(casacore::IPosition(2,gridin.shape()[0],gridin.shape()[0]),false);
    	int GridSize(gridin.shape()[0]);
    	const casacore::Complex* inPtr = gridin.data();
    	casacore::uInt Nnonzero(0);
    	for (int i=0; i<GridSize; ++i) {
    	  for (int j=0; j<GridSize; ++j) {
    	    if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
    	      Nnonzero+=1;
	    }
    	    inPtr++;
    	  }
	}
    	inPtr = gridin.data();
	Nnonzero=std::max(1,int(Nnonzero));
    	casacore::Matrix<casacore::uShort> Mask(casacore::IPosition(2,Nnonzero,2));
	Mask=0;
	casacore::uInt indec(0);
    	for (int i=0; i<GridSize; ++i) {
    	  for (int j=0; j<GridSize; ++j) {
    	    if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	      Mask(indec,0)=i;
	      Mask(indec,1)=j;
	      indec+=1;
	    }
    	    inPtr++;
    	  }
    	}
    	//itsVectorMasksDegridElement.push_back(Mask);
    	store(Mask,MaskName);
	if(MaskType==0){
	  itsVecMasksNew[NumTime][NumWplane+m_nWPlanes].reference (Mask);
	}
	if(MaskType==1){
	  itsVecMasksNewW[NumTime][NumWplane+m_nWPlanes].reference (Mask);
	}
	if(MaskType==2){
	  itsVecMasksNewElement.push_back(Mask);
	}
	
    	//cout<<"... Done Making Masks ... t="<<NumTime<<" w="<<NumWplane+m_nWPlanes<<" npix="<<Nnonzero<<endl;
      }
    }


    void Make_MuellerAvgPB(vector< vector< vector < casacore::Matrix<casacore::Complex> > > > & StackMueller, double sum_weight_square);

    casacore::Array< casacore::Complex > Correct_CC(casacore::Array< casacore::Complex > & ModelImage);


    casacore::Bool itsFilledVectorMasks;
      //vector< Matrix< Bool > > itsVectorMasksDegridElement;
    void ReadMaskDegrid()
    {
      casacore::Int NumMask(0);
      while(true){
	casacore::String MaskName("JAWS_products/Mask"+casacore::String::toString(NumMask)+".boolim");
	casacore::File MaskFile(MaskName);
	if(MaskFile.exists())
	  {
	    //cout<<"Reading:"<<MaskName<<endl;
	    casacore::PagedImage<casacore::Bool> pim(MaskName);
	    casacore::Array<casacore::Bool> arr = pim.get();
	    casacore::Matrix<casacore::Bool> Mask;
	    Mask.reference (arr.nonDegenerate(2));
	    itsVectorMasksDegridElement.push_back(Mask);
	    NumMask+=1;
	  }
	else
	  {
	    break;
	  }
      }
      itsFilledVectorMasks=true;
    }
      
    void ReadMaskDegridW()
    {
      initStoreMasks();
      casacore::Int Wc(0);
      for(casacore::uInt Tnum=0;Tnum<NBigChunks;++Tnum){
	for(casacore::uInt Wnum=0;Wnum<2*m_nWPlanes;++Wnum){
	
	  casacore::Int Wsearch(Wnum-m_nWPlanes);
	  casacore::String MaskName("JAWS_products/Mask.T"+casacore::String::toString(Tnum)+".W"+casacore::String::toString(Wsearch)+".boolim");
	  casacore::File MaskFile(MaskName);
	  if(MaskFile.exists())
	    {
	      casacore::PagedImage<casacore::Bool> pim(MaskName);
	      casacore::Array<casacore::Bool> arr = pim.get();
	      itsVecMasks[Tnum][Wnum].reference (arr.nonDegenerate(2));
	      //cout<<"  ... read t="<<Tnum<<" w="<<Wsearch<<" put at:"<<Wnum<<endl;
	      Wc+=1;
	    }
	}
      }
      itsFilledVectorMasks=true;
      
    }

    void ReadMaskDegridWNew()
    {
      //cout<<"...reading masks degrid"<<endl;
      casacore::Int Wc(0);
      initStoreMasksNew();

      /* MaskName="JAWS_products/MaskGrid.T"+String::toString(NumTime)+".W"+String::toString(NumWplane)+".boolim"; */
      /* MaskName="JAWS_products/MaskDeGrid.T"+String::toString(NumTime)+".W"+String::toString(NumWplane)+".boolim"; */
      /* MaskName="JAWS_products/MaskGrid.Element.T"+String::toString(NumTime)+".boolim"; */
      /* vector< vector< Matrix< uInt > > > itsVecMasksNew; */
      /* vector< vector< Matrix< uInt > > > itsVecMasksNewW; */
      /* vector< Matrix< uInt > > itsVecMasksNewElement; */

      for(casacore::uInt Tnum=0;Tnum<NBigChunks;++Tnum){
	for(casacore::uInt Wnum=0;Wnum<2*m_nWPlanes;++Wnum){
	
	  casacore::Int Wsearch(Wnum-m_nWPlanes);
	  casacore::String MaskName("JAWS_products/MaskGrid.T"+casacore::String::toString(Tnum)+".W"+casacore::String::toString(Wsearch)+".boolim");
	  casacore::File MaskFile(MaskName);
	  if(MaskFile.exists())
	    {
	      //cout<<".. reading "<<MaskName<<endl;
	      casacore::PagedImage<casacore::uShort> pim(MaskName);
	      casacore::Array<casacore::uShort> arr = pim.get();
	      itsVecMasksNew[Tnum][Wnum].reference (arr.nonDegenerate(2));
	      Wc+=1;
	    }
	  casacore::String MaskName2("JAWS_products/MaskDeGrid.T"+casacore::String::toString(Tnum)+".W"+casacore::String::toString(Wsearch)+".boolim");
	  casacore::File MaskFile2(MaskName);
	  if(MaskFile2.exists())
	    {
	      //cout<<".. reading "<<MaskName2<<endl;
	      casacore::PagedImage<casacore::uShort> pim(MaskName2);
	      casacore::Array<casacore::uShort> arr = pim.get();
	      itsVecMasksNewW[Tnum][Wnum].reference (arr.nonDegenerate(2));
	      Wc+=1;
	    }
	}
	casacore::String MaskName("JAWS_products/MaskGrid.Element.T"+casacore::String::toString(Tnum)+".boolim");
	casacore::File MaskFile(MaskName);
	if(MaskFile.exists())
	  {
	    //cout<<".. reading "<<MaskName<<endl;
	    casacore::PagedImage<casacore::uShort> pim(MaskName);
	    casacore::Array<casacore::uShort> arr = pim.get();
	    casacore::Matrix<casacore::uShort> Mask;
	    Mask.reference(arr.nonDegenerate(2));
	    itsVecMasksNewElement.push_back(Mask);
	  }

      }
      //cout<<"... deon reading masks degrid"<<endl;
      itsFilledVectorMasks=true;
      
    }
      
    casacore::Bool VectorMaskIsFilled(){return itsFilledVectorMasks;}
    
    void normalized_fft (casacore::Matrix<casacore::Complex>&, bool toFreq=true);
    void normalized_fft_parallel(casacore::Matrix<casacore::Complex> &im, bool toFreq=true);
    void normalized_fft (casacore::PrecTimer& timer, casacore::Matrix<casacore::Complex>&, bool toFreq=true);

    casacore::Vector< casacore::Double >    list_freq_spw;
    casacore::Vector< casacore::Double >    list_freq_chanBlock;
    casacore::Vector< casacore::uInt >      map_chan_chanBlock;
    casacore::Vector< casacore::uInt >      map_chanBlock_spw;
    vector<casacore::Vector< casacore::uInt > >     map_spw_chanBlock;
    casacore::Vector< casacore::uInt > map_chan_Block_buffer;
    casacore::uInt                m_nWPlanes;


  private:

    casacore::Matrix<casacore::Complex> give_normalized_fft_lapack(const casacore::Matrix<casacore::Complex> &im, bool toFreq=true)
      {
        casacore::Matrix<casacore::Complex> result(im.copy());
        casacore::ArrayLattice<casacore::Complex> lattice(result);
        casacore::LatticeFFT::cfft2d(lattice, toFreq);
        if(toFreq){
          result/=static_cast<casacore::Float>(result.shape()(0)*result.shape()(1));
        }
        else{
          result*=static_cast<casacore::Float>(result.shape()(0)*result.shape()(1));
        };
        return result;
      }

    casacore::MEpoch observationStartTime (const casacore::MeasurementSet &ms,
                                 casacore::uInt idObservation) const;

    // Estime spheroidal convolution function from the support of the fft
    // of the spheroidal in the image plane
    casacore::Double makeSpheroidCut();

    // Return the angular resolution required for making the image of the
    // angular size determined by coordinates and shape.
    // The resolution is assumed to be the same on both direction axes.
    casacore::Double estimateWResolution(const casacore::IPosition &shape,
                               casacore::Double pixelSize,
                               casacore::Double w) const;


    // Return the angular resolution required for making the image of the
    // angular size determined by coordinates and shape.
    // The resolution is assumed to be the same on both direction axes.
    casacore::Double estimateAResolution(const casacore::IPosition &shape,
                               const casacore::DirectionCoordinate &coordinates, double station_diam = 70.) const;

    // Apply a spheroidal taper to the input function.
    template <typename T>
    void taper (casacore::Matrix<T> &function) const
    {
//       AlwaysAssert(function.shape()[0] == function.shape()[1], casacore::SynthesisError);
      casacore::uInt size = function.shape()[0];
      casacore::Double halfSize = (size-1) / 2.0;
      casacore::Vector<casacore::Double> x(size);
      for (casacore::uInt i=0; i<size; ++i) {
        x[i] = spheroidal(abs(i - halfSize) / halfSize);
      }
      for (casacore::uInt i=0; i<size; ++i) {
        for (casacore::uInt j=0; j<size; ++j) {
          function(j, i) *= x[i] * x[j];
        }
      }
    }

    template <typename T>
    void taper_parallel (casacore::Matrix<T> &function) const
    {
//       AlwaysAssert(function.shape()[0] == function.shape()[1], SynthesisError);
      casacore::uInt size = function.shape()[0];
      casacore::Double halfSize = (size-1) / 2.0;
      casacore::Vector<casacore::Double> x(size);
      for (casacore::uInt i=0; i<size; ++i) {
        x[i] = spheroidal(abs(i - halfSize) / halfSize);
      }
      casacore::uInt j;
#pragma omp parallel
      {
#pragma omp for private(j) schedule(dynamic)
        for (casacore::uInt i=0; i<size; ++i) 
        {
          for (j=0; j<size; ++j) 
          {
            function(j, i) *= x[i] * x[j];
          }
        }
      }
    }


    // Linear interpolation
    template <typename T>
    casacore::Matrix< T > LinearInterpol(casacore::Matrix<T> ImageIn, casacore::Int  NpixOut)
      {
	casacore::Matrix<T> ImageOut(casacore::IPosition(2,NpixOut,NpixOut),0.);
	float d0(1./(NpixOut-1.));
	float d1(1./(ImageIn.shape()[0]-1.));
	float dd(d0/d1);
	float dx,dy,dxd,dyd,xin,yin;
	float onef(1.);
	for(casacore::Int i=0;i<(NpixOut);++i){
	  dxd=i*dd;
	  xin=floor(dxd);
	  dx=dxd-xin;
	  for(casacore::Int j=0;j<(NpixOut);++j){
	    dyd=j*dd;
	    yin=floor(dyd);
	    dy=dyd-yin;
	    ImageOut(i,j)=(onef-dx)*(onef-dy)*ImageIn(xin,yin) + (onef-dx)*(dy)*ImageIn(xin,yin+1) + (dx)*(onef-dy)*ImageIn(xin+1,yin) + (dx)*(dy)*ImageIn(xin+1,yin+1);
	  }
	}
	return ImageOut;
      }

    void Convolve(casacore::Matrix<casacore::Complex> gridin, casacore::Matrix<casacore::Complex> gridout, casacore::Matrix<casacore::Complex> ConvFunc){
      casacore::uInt Support(ConvFunc.shape()[0]);
      casacore::uInt GridSize(gridin.shape()[0]);
      casacore::uInt off(Support/2);
      for(casacore::uInt i=Support/2;i<GridSize-Support/2;++i){
	for(casacore::uInt j=Support/2;j<GridSize-Support/2;++j){
	  if((gridin(i,j))!=casacore::Complex(0.,0.)){
	    casacore::Complex val(gridin(i,j));
	    for(casacore::uInt ii=0;ii<Support;++ii){
	      for(casacore::uInt jj=0;jj<Support;++jj){
		gridout(i-off+ii,j-off+jj)+=ConvFunc(ii,jj)*val;
	      }
	    }
	  }
	}
      }
    }

    void ConvolveOpt(casacore::Matrix<casacore::Complex> gridin, casacore::Matrix<casacore::Complex> gridout, casacore::Matrix<casacore::Complex> ConvFunc){
      casacore::uInt Support(ConvFunc.shape()[0]);
      casacore::uInt GridSize(gridin.shape()[0]);
      casacore::uInt off(Support/2);

      casacore::Complex* __restrict__ gridInPtr = gridin.data();
      casacore::Complex* __restrict__ gridOutPtr = gridout.data();
      casacore::Complex* __restrict__ ConvFuncPtr = ConvFunc.data();

      for(casacore::uInt i=Support/2;i<GridSize-Support/2;++i){
	for(casacore::uInt j=Support/2;j<GridSize-Support/2;++j){
	  gridInPtr=gridin.data()+GridSize*i+j;
	  if (gridInPtr->real() != 0  ||  gridInPtr->imag() != 0) {//if((*gridInPtr)!=Complex(0.,0.)){
	    ConvFuncPtr = ConvFunc.data();
	    for(casacore::uInt jj=0;jj<Support;++jj){
	      for(casacore::uInt ii=0;ii<Support;++ii){
		gridOutPtr = gridout.data()+(j-off+jj)*GridSize+i-off+ii;
		(*gridOutPtr) += (*ConvFuncPtr)*(*gridInPtr);
		ConvFuncPtr++;//=ConvFunc.data()+Support*ii+jj;
	      }
	    }
	  }
	  //gridInPtr++;
	}
      }
      
    }

    void ConvolveGer( const casacore::Matrix<casacore::Complex>& gridin, casacore::Matrix<casacore::Complex>& gridout,
		      const casacore::Matrix<casacore::Complex>& ConvFunc)
    {
      casacore::uInt Support(ConvFunc.shape()[0]);
      casacore::uInt GridSize(gridin.shape()[0]);
      casacore::uInt off(Support/2);
      const casacore::Complex* inPtr = gridin.data() + off*GridSize + off;
      for (casacore::uInt i=0; i<GridSize-Support; ++i) {
	for (casacore::uInt j=0; j<GridSize-Support; ++j) {
	  if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	    const casacore::Complex* cfPtr = ConvFunc.data();
	    for (casacore::uInt ii=0; ii<Support; ++ii) {
	      casacore::Complex* outPtr = gridout.data() + (i+ii)*GridSize + j;
	      for (casacore::uInt jj=0; jj<Support; ++jj) {
		outPtr[jj] += *cfPtr++ * *inPtr;
	      }
	    }
	  }
	  inPtr++;
	}
	inPtr += Support;
      }
    }

    void ConvolveGerArray( const casacore::Array<casacore::Complex>& gridin, casacore::Int ConvPol, casacore::Matrix<casacore::Complex>& gridout,
			   const casacore::Matrix<casacore::Complex>& ConvFunc)
    {
      casacore::uInt Support(ConvFunc.shape()[0]);
      casacore::uInt GridSize(gridin.shape()[0]);
      casacore::uInt off(Support/2);

      const casacore::Complex* inPtr = gridin.data() + ConvPol*GridSize*GridSize + off*GridSize + off;
      for (casacore::uInt i=0; i<GridSize-Support; ++i) {
	for (casacore::uInt j=0; j<GridSize-Support; ++j) {
	  if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	    const casacore::Complex* cfPtr = ConvFunc.data();
	    for (casacore::uInt ii=0; ii<Support; ++ii) {
	      casacore::Complex* outPtr = gridout.data() + (i+ii)*GridSize + j;
	      for (casacore::uInt jj=0; jj<Support; ++jj) {
		outPtr[jj] += *cfPtr++ * *inPtr;
	      }
	    }
	  }
	  inPtr++;
	  }
	inPtr += Support;
      }
    }
    
    void ConvolveArrayArray( const casacore::Array<casacore::Complex>& gridin, casacore::Array<casacore::Complex>& gridout,
			   const casacore::Matrix<casacore::Complex>& ConvFunc)
    {
      int Support(ConvFunc.shape()[0]);
      int GridSize(gridin.shape()[0]);
      int off(Support/2);



      for(casacore::uInt ConvPol=0; ConvPol<gridin.shape()[2];++ConvPol){

	casacore::Int offPol(ConvPol*GridSize*GridSize);
	const casacore::Complex* inPtr = gridin.data() + ConvPol*GridSize*GridSize + off*GridSize + off;
	for (casacore::Int i=0; i<GridSize-Support; ++i) {
	  for (casacore::Int j=0; j<GridSize-Support; ++j) {
	    if (inPtr->real() != 0  ||  inPtr->imag() != 0) {
	      const casacore::Complex* cfPtr = ConvFunc.data();
	      for (casacore::Int ii=0; ii<Support; ++ii) {
		casacore::Complex* outPtr = gridout.data() + (i+ii)*GridSize + j +offPol;
		for (casacore::Int jj=0; jj<Support; ++jj) {
		  outPtr[jj] += *cfPtr++ * *inPtr;
		}
	      }
	    }
	    inPtr++;
	  }
	  inPtr += Support;
	}

      }
    }
    


    void ConvolveGerArrayMask( const casacore::Array<casacore::Complex>& gridin, casacore::Int ConvPol, casacore::Matrix<casacore::Complex>& gridout,
			       const casacore::Matrix<casacore::Complex>& ConvFunc, casacore::Int UsedMask)
    {
      casacore::uInt Support(ConvFunc.shape()[0]);
      casacore::uInt GridSize(gridin.shape()[0]);
      casacore::uInt off(Support/2);

      const casacore::Complex* inPtr = gridin.data() + ConvPol*GridSize*GridSize + off*GridSize + off;
      const casacore::Bool* MaskPtr = itsVectorMasksDegridElement[UsedMask].data() + off*GridSize + off;
      for (casacore::uInt i=0; i<GridSize-Support; ++i) {
	for (casacore::uInt j=0; j<GridSize-Support; ++j) {
	  if ((*MaskPtr)==true) {
	    const casacore::Complex* cfPtr = ConvFunc.data();
	    for (casacore::uInt ii=0; ii<Support; ++ii) {
	      casacore::Complex* outPtr = gridout.data() + (i+ii)*GridSize + j;
	      for (casacore::uInt jj=0; jj<Support; ++jj) {
		outPtr[jj] += *cfPtr++ * *inPtr;
	      }
	    }
	  }
	  MaskPtr++;
	  inPtr++;
	}
	inPtr += Support;
	MaskPtr += Support;
      }
    }
    
    
    
    // Linear interpolation
    template <typename T>
    casacore::Matrix< T > LinearInterpol2(casacore::Matrix<T> ImageIn, casacore::Int  NpixOut)
      {
	casacore::Matrix<T> ImageOut(casacore::IPosition(2,NpixOut,NpixOut),1e-7);
	int nd(ImageIn.shape()[0]);
	int ni(NpixOut);
	float off(-.5);//-(((1.+1./(nd-1.))-1.)/2.)*(nd-1));
	float a(nd/(ni-1.));//((1.+1./(nd-1.))/(ni-1.))*(nd-1));
	float dx,dy,dxd,dyd,xin,yin;
	float onef(1.);
	for(casacore::Int i=0;i<(NpixOut);++i){
	  dxd=i*a+off;
	  xin=floor(dxd);
	  dx=dxd-xin;
	  for(casacore::Int j=0;j<(NpixOut);++j){
	    dyd=j*a+off;
	    yin=floor(dyd);
	    dy=dyd-yin;
	    if((dxd<0)||((xin+1)>ImageIn.shape()[0]-1.)){continue;}
	    if((dyd<0)||((yin+1)>ImageIn.shape()[0]-1.)){continue;}
	    ImageOut(i,j)=(onef-dx)*(onef-dy)*ImageIn(xin,yin) + (onef-dx)*(dy)*ImageIn(xin,yin+1) + (dx)*(onef-dy)*ImageIn(xin+1,yin) + (dx)*(dy)*ImageIn(xin+1,yin+1);
	  }
	}
	/* store(ImageIn,"ImageIn.img"); */
	/* store(ImageOut,"ImageOut.img"); */
	/* assert(false); */
	return ImageOut;
      }

    void EstimateCoordShape(casacore::IPosition shape, casacore::DirectionCoordinate coordinate, double station_diameter=70.){
      coordinate = m_coordinates;
      casacore::Double aPixelAngSize = min(m_pixelSizeSpheroidal,
				 estimateAResolution(m_shape, m_coordinates, station_diameter));
      
      casacore::Double pixelSize = abs(m_coordinates.increment()[0]);
      casacore::Double imageDiameter = pixelSize * m_shape(0);
      casacore::Int nPixelsConv = imageDiameter / aPixelAngSize;
      if (nPixelsConv > itsMaxSupport) {
          nPixelsConv = itsMaxSupport;
      }
      // Make odd and optimal.
      nPixelsConv = FFTCMatrix::optimalOddFFTSize (nPixelsConv);
      aPixelAngSize = imageDiameter / nPixelsConv;

      shape=casacore::IPosition(2, nPixelsConv, nPixelsConv);
      casacore::Vector<casacore::Double> increment_old(coordinate.increment());
      casacore::Vector<casacore::Double> increment(2);
      increment[0] = aPixelAngSize*casacore::sign(increment_old[0]);
      increment[1] = aPixelAngSize*casacore::sign(increment_old[1]);
      coordinate.setIncrement(increment);
      casacore::Vector<casacore::Double> refpix(2, 0.5*(nPixelsConv-1));
      coordinate.setReferencePixel(refpix);
    }




    casacore::Double spheroidal(casacore::Double nu) const;






    template <typename T>
    casacore::uInt findSupport(casacore::Matrix<T> &function, casacore::Double threshold) const
    {
      ///      Double peak = abs(max(abs(function)));
      casacore::Double peak = max(amplitude(function));
      threshold *= peak;
      casacore::uInt halfSize = function.shape()[0] / 2;
      casacore::uInt x = 0;
      while (x < halfSize && abs(function(x, halfSize)) < threshold) {
        ++x;
      }
      return 2 * (halfSize - x);
    }


    //# Data members.
    casacore::Record       itsParameters;
    casacore::Array<casacore::Complex> its_output_grid_element;
    casacore::Matrix<casacore::Complex> its_ArrMatrix_out_element;
    casacore::IPosition           m_shape;
    casacore::DirectionCoordinate m_coordinates;
    WScale              m_wScale;
    LofarWTerm          m_wTerm;
    LofarATerm          m_aTerm;
    casacore::Double              m_maxW;
    casacore::Double              m_pixelSizeSpheroidal;
    casacore::uInt                m_nStations;
    casacore::uInt                m_oversampling;
    casacore::uInt                m_nChannelBlocks;
    casacore::uInt                m_NPixATerm;
    casacore::Double              m_refFrequency;
    casacore::uInt                m_maxCFSupport;
    vector<casacore::Double>      its_VectorThreadsSumWeights;

    //# Stack of the convolution functions for the average PB calculation
    casacore::Matrix<casacore::Complex>     Spheroid_cut;
    //# Stack of the convolution functions for the average PB calculation
    casacore::Matrix<casacore::Float>       Spheroid_cut_im;
    casacore::Matrix<casacore::Float>       Spheroid_cut_im_element;
    //# List of the ferquencies the CF have to be caluclated for
    vector< casacore::Matrix<casacore::Complex> > m_WplanesStore;
    //# Aterm_store[double time][antenna][channel]=Cube[Npix,Npix,4]
    map<casacore::Double, vector< vector< casacore::Cube<casacore::Complex> > > > m_AtermStore;
    map<casacore::Double, vector< vector< casacore::Cube<casacore::Complex> > > > m_AtermStore_element;
    map<casacore::Double, vector< vector< casacore::Cube<casacore::Complex> > > > m_AtermStore_station;
    //# Average primary beam
    casacore::Matrix<casacore::Float>       Im_Stack_PB_CF0;
    casacore::Int                 itsVerbose;
    casacore::Int                 itsMaxSupport;
    //    Int                 itsTaylorTerm;
    //Double              itsRefFreq;
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
    casacore::Double              itsTimeCF;
    casacore::Double              itsTimeCFpar;
    casacore::Double              itsTimeCFfft;
    unsigned long long  itsTimeCFcnt;
    casacore::Bool                its_Use_EJones;
    casacore::Bool                its_Apply_Element;
    casacore::Bool                its_NotApplyElement;
    casacore::Bool                its_NotApplyArray;
    casacore::uInt                its_MaxWSupport;
    casacore::uInt                its_count_time;
    mutable casacore::LogIO       m_logIO;
    casacore::Int                 its_ChanBlockSize;
    casacore::Matrix<casacore::Complex>     spheroid_cut_element_fft;
    vector< vector< casacore::Matrix< casacore::Complex > > > GridsMueller;
    casacore::LogIO &logIO() const
      {
        return m_logIO;
      }
  };



  //# =================================================
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
  void store (const casacore::DirectionCoordinate &dir, const casacore::Matrix<T> &data,
              const string &name)
  {
    //cout<<"Saving... "<<name<<endl;
    casacore::Vector<casacore::Int> stokes(1);
    stokes(0) = casacore::Stokes::I;
    casacore::CoordinateSystem csys;
    csys.addCoordinate(dir);
    csys.addCoordinate(casacore::StokesCoordinate(stokes));
    csys.addCoordinate(casacore::SpectralCoordinate(casacore::MFrequency::TOPO, 60e6, 0.0, 0.0, 60e6));
    casacore::PagedImage<T> im(casacore::TiledShape(casacore::IPosition(4, data.shape()(0), data.shape()(1), 1, 1)), csys, name);
    im.putSlice(data, casacore::IPosition(4, 0, 0, 0, 0));
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

} //# end namespace LOFAR

#endif
