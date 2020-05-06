//# ATermLofar.h: Compute the LOFAR beam response on the sky.
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
//# $Id: LOFARATerm.h 18046 2011-05-19 20:58:40Z diepen $

#ifndef LOFAR_LOFARFT_ATERMLOFAR_H
#define LOFAR_LOFARFT_ATERMLOFAR_H

#include <AWImager2/ATerm.h>
#include <AWImager2/DynamicObjectFactory.h>

#include <Common/lofar_vector.h>
#include <Common/lofar_string.h>
#include <Common/LofarTypes.h>
#include <ParmDB/ParmFacade.h>
#include <StationResponse/Station.h>
#include <casacore/casa/Arrays/Array.h>
#include <casacore/casa/Containers/Record.h>
#include <casacore/measures/Measures/MDirection.h>
#include <casacore/measures/Measures/MEpoch.h>
#include <casacore/measures/Measures/MPosition.h>

namespace casacore
{
  class DirectionCoordinate;
  class MeasurementSet;
}

namespace LOFAR {
namespace LofarFT {

class ATermLofar : public ATerm
{
public:
  ATermLofar(const casacore::MeasurementSet &ms, const ParameterSet& parset, bool read_stations=true);
  
  virtual ~ATermLofar() {};

  virtual Polarization::Type image_polarization() const {return Polarization::LINEAR;}

  void setDirection(const casacore::DirectionCoordinate &coordinates, const casacore::IPosition &shape);
  
  void setEpoch(const casacore::MEpoch &epoch);

    /*!
     *  \brief Compute an ITRF direction vector for each pixel at the given
     *  epoch. This map can then be used to call any of the evaluate* functions.
     *
     *  \param coordinates Sky coordinate system definition.
     *  \param shape Number of points along the RA and DEC axis.
     *  \param epoch Time for which to compute the ITRF coordinates.
     *  \param position0 Station beam former reference position (phase reference).
     *  \param station0 Station beam former reference direction (pointing).
     *  \param tile0 Tile beam former reference direction (pointing).
     */
  ITRFDirectionMap
  makeDirectionMap(const casacore::DirectionCoordinate &coordinates,
    const casacore::IPosition &shape,
    const casacore::MEpoch &epoch) const;

  // Compute the LOFAR station response for the given station. This includes
  // the effects of paralactic rotation, the dual dipole LOFAR antenna, the
  // tile beam former (HBA only), and the station beam former.
  //
  // The freq argument is a list of frequencies at which the response will be
  // evaluated. The reference argument is a list of station beam former
  // reference frequencies. The normalize argument, when set to true, causes
  // the response to be multiplied by the inverse of the response at the
  // central pixel.
  virtual vector<casacore::Cube<casacore::Complex> > evaluate(
    uint idStation,
    const casacore::Vector<casacore::Double> &freq,
    const casacore::Vector<casacore::Double> &reference, 
    bool normalize = false)
    const;

  // Compute the array factor for the given station and polarization (0 = X,
  // 1 = Y).
  //
  // The freq argument is a list of frequencies at which the array factor will
  // be evaluated. The reference argument is a list of station beam former
  // reference frequencies. The normalize argument, when set to true, causes
  // the response to be multiplied by the inverse of the array factor at the
  // central pixel.
    
  virtual vector<casacore::Matrix<casacore::Complex> > evaluateStationScalarFactor(
    uint idStation,
    uint idPolarization,
    const casacore::Vector<casacore::Double> &freq,
    const casacore::Vector<casacore::Double> &freq0, 
    bool normalize = false)
    const;

  virtual vector<casacore::Matrix<casacore::Complex> > evaluateArrayFactor(
    uint idStation,
    uint idPolarization,
    const casacore::Vector<casacore::Double> &freq,
    const casacore::Vector<casacore::Double> &freq0, 
    bool normalize = false)
    const;

  // Compute the LOFAR element response for the given station and antenna
  // field. This includes the effects of paralactic rotation and the dual
  // dipole LOFAR antenna.
  //
  // The freq argument is a list of frequencies at which the response will be
  // evaluated. The normalize argument, when set to true, causes the response
  // to be multiplied by the inverse of the response at the central pixel.
  virtual vector<casacore::Cube<casacore::Complex> > evaluateElementResponse(
    uint idStation,
    uint idField,
    const casacore::Vector<casacore::Double> &freq, 
    bool normalize = false) const;

  virtual casacore::Cube<casacore::DComplex> evaluateIonosphere(
    const uint station,
    const casacore::Vector<casacore::Double> &freq) const;

protected:
  
  void initParmDB(const casacore::String &parmdbname);
  double get_parmvalue( const casacore::Record &parms, const string &parmname );

  casacore::Record itsParmValues;
  
  vector<StationResponse::Station::ConstPtr>  itsStations;
  const casacore::DirectionCoordinate *itsDirectionCoordinates;
  const casacore::IPosition       *itsShape;
  casacore::MPosition                             itsPosition0;
  casacore::MDirection                            itsStation0, itsTile0;
  
  ITRFDirectionMap      itsITRFDirectionMap;
  
  // state variables for ionosphere
  casacore::Bool                 itsApplyBeam;
  casacore::Bool                 itsApplyIonosphere;
  LOFAR::BBS::ParmFacade     *itsPDB;
  double itsTime;
  double itsR0;
  double itsBeta;
  double itsHeight;
  casacore::Vector<casacore::String>   itsCal_pp_names;
  casacore::Matrix<casacore::Double> itsCal_pp;
  casacore::Vector<casacore::Double> itsTec_white;
  casacore::Int itsVerbose;
};

} // namespace LofarFT
} // namespace LOFAR

#endif
