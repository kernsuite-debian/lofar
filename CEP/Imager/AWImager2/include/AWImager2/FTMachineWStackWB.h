//# FTMachineWStackWB.h: Definition for FTMachineSimple
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
//# $Id: FTMachineSimpleWB.h 28512 2014-03-05 01:07:53Z vdtol $

#ifndef LOFAR_LOFARFT_FTMACHINEWSTACKWB_H
#define LOFAR_LOFARFT_FTMACHINEWSTACKWB_H

#include <AWImager2/FTMachine.h>
#include <AWImager2/VisResamplerWB.h>

namespace LOFAR {
namespace LofarFT {

class VisBuffer;  
  
class FTMachineWStackWB : public FTMachine {
public:
  static const casacore::String theirName;

  FTMachineWStackWB(
    const casacore::MeasurementSet& ms, 
    const ParameterSet& parset);

  virtual ~FTMachineWStackWB();
  
  // Copy constructor
  FTMachineWStackWB(const FTMachineWStackWB &other);

  // Assignment operator
  FTMachineWStackWB &operator=(const FTMachineWStackWB &other);

  // Clone
  FTMachineWStackWB* clone() const;

  virtual casacore::String name() const { return theirName;}
  
  // Get actual coherence from grid by degridding
  virtual void get(casacore::VisBuffer& vb, casacore::Int row=-1);
  virtual void get(VisBuffer& vb, casacore::Int row=-1);


  // Put coherence to grid by gridding.
  using casacore::FTMachine::put;

  virtual void put(
    const VisBuffer& vb, 
    casacore::Int row = -1, 
    casacore::Bool dopsf = casacore::False,
    casacore::FTMachine::Type type = casacore::FTMachine::OBSERVED);
  
protected:

  virtual void initialize_model_grids(casacore::Bool normalize);
  
  // Get the appropriate data pointer
  casacore::Array<casacore::Complex>* getDataPointer(const casacore::IPosition&, casacore::Bool);

  // Gridder
  casacore::String convType;

  casacore::Float maxAbsData;

  // Useful IPositions
  casacore::IPosition centerLoc;
  casacore::IPosition offsetLoc;


  // Shape of the padded image
  casacore::IPosition padded_shape;

  casacore::Int convSampling;
  casacore::Float pbLimit_p;
  casacore::Bool itsSplitBeam;
  int itsNThread;
  casacore::Int itsRefFreq;
  casacore::Float itsTimeWindow;
  
  casacore::CountedPtr<VisResamplerWB> itsVisResampler;
  virtual VisResampler* visresampler() {return &*itsVisResampler;}

private:
  
  struct Chunk
  {
    int start;
    int end;
    double time;
    double w;
    casacore::Matrix<casacore::Float> sum_weight;
    vector<int> wplane_map;
  };
  
  struct VisibilityMap
  {
    VisibilityMap() : max_w_plane(0) {}
    vector<Chunk> chunks;
    casacore::Vector<casacore::uInt> baseline_index_map;
    int max_w_plane;
  };

  VisibilityMap make_mapping(
    const VisBuffer& vb, 
    const casacore::Vector< casacore::Double > &frequency_list_CF,
    double dtime,
    double w_step);

  bool put_on_w_plane(
    const VisBuffer &vb,
    const VBStore &vbs,
    const casacore::Vector<casacore::Double> &lsr_frequency,
    vector< casacore::Array<casacore::Complex> >  &w_plane_grids,
    const VisibilityMap &v,
    int w_plane,
    double w_offset, 
    bool dopsf);
  
};

} //# end namespace LofarFT
} //# end namespace LOFAR

#endif
