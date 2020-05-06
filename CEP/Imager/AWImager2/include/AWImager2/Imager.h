//# LofarImager.h: Imager for LOFAR data correcting for DD effects
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
//#
//# @author Ger van Diepen <diepen at astron dot nl>

#ifndef LOFAR_LOFARFT_IMAGER_H
#define LOFAR_LOFARFT_IMAGER_H

#include <AWImager2/FTMachine.h>
#include <AWImager2/VisibilityIterator.h>
#include <AWImager2/VisImagingWeight.h>
#include <synthesis/MeasurementEquations/Imager.h>
#include <Common/ParameterSet.h>
#include <casacore/casa/Containers/Record.h>


namespace LOFAR {
namespace LofarFT {
  
  // @brief Imager for LOFAR data correcting for DD effects

  class Imager : public casacore::Imager
  // TODO
  // override Imager::operator= to copy LofarImager data members
  // override Imager::defaults to set lofar_imwgt_p
  // override Imager::filter
  
  {
  public:

    // Construct from the Imager object.
    explicit Imager (casacore::MeasurementSet&,
                     LOFAR::ParameterSet& parset);

    virtual ~Imager();

    // Create the LofarFTMachine and fill ft_p in the parent.
    virtual casacore::Bool createFTMachine();

    virtual void setSkyEquation();

    virtual void makeVisSet(
      casacore::MeasurementSet& ms, 
      casacore::Bool compress, 
      casacore::Bool mosaicOrder);
    
    // Get the average primary beam.
    const casacore::Matrix<casacore::Float>& getAveragePB() const
    { 
      return itsFTMachine->getAveragePB();
    }

    // Get the spheroidal cut.
    const casacore::Matrix<casacore::Float>& getSpheroidal() const
    { 
      return itsFTMachine->getSpheroidal();
    }
    
    casacore::Bool makeimage(const casacore::String& type, const casacore::String& image);


    // Show the relative timings of the various steps.
    void showTimings (std::ostream&, double duration) const;
    
    casacore::Bool restoreImages(const casacore::Vector<casacore::String>& restored, casacore::Bool modresiduals=casacore::True);

  virtual casacore::Bool checkCoord(const casacore::CoordinateSystem& coordsys, 
                          const casacore::String& imageName); 
    
    
  casacore::Record initClean(
    const casacore::String& algorithm,
    const casacore::Int niter,
    const casacore::Float gain,
    const casacore::Quantity& threshold,
    const casacore::Vector<casacore::String>& model, 
    const casacore::Vector<casacore::Bool>& fixed,
    const casacore::String& complist,
    const casacore::Vector<casacore::String>& mask,
    const casacore::Vector<casacore::String>& restored,
    const casacore::Vector<casacore::String>& residual,
    const casacore::Vector<casacore::String>& psf = casacore::Vector<casacore::String>(0),
    const casacore::Bool firstrun=true);

  casacore::Record doClean(const casacore::Bool firstrun=true);
    
  void initPredict(const casacore::Vector<casacore::String>& modelNames);
  void predict();
  
  casacore::Bool set_imaging_weight(const ParameterSet& parset);
  
  private:
    //# Data members.
    ParameterSet    &itsParset;
    FTMachine*       itsFTMachine;
    vector<casacore::Array<casacore::Complex> >  itsGridsParallel;
    vector<casacore::Array<casacore::DComplex> > itsGridsParallel2;
    VisibilityIterator*    lofar_rvi_p;
    casacore::CountedPtr<VisImagingWeight> lofar_imwgt_p;
    casacore::Vector<casacore::String> itsPSFNames;

    
};

} //# end namespace LofarFT
} //# end namespace LOFAR

#endif
