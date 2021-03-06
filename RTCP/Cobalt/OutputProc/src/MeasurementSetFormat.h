//# MeasurementSetFormat.h: defines the format of the RAW datafile
//# Copyright (C) 2009-2013  ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
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

#ifndef LOFAR_STORAGE_MEASUREMENT_SET_FORMAT_H
#define LOFAR_STORAGE_MEASUREMENT_SET_FORMAT_H

#include <string>
#include <vector>

#include <Common/LofarTypes.h>
#include <Common/Thread/Mutex.h>
#include <MSLofar/MSLofar.h>
#include <CoInterface/Parset.h>
#include <CoInterface/SmartPtr.h>
#include <CoInterface/OutputTypes.h> //for LofarStManVersion

#include <casacore/casa/aips.h>
#include <casacore/casa/Utilities/DataType.h>
#include <casacore/casa/Arrays/IPosition.h>

/*
 * LofarStMan supports multiple versions of the MS, with the following
 * differences in the data on disk:
 *
 * MS version    visibilities    antenna order     support for
 *                               (baseline = 1,2)  bytes/weight
 * -------------------------------------------------------------
 *  1            conjugated      1,2               2
 *  2            conjugated      2,1               1,2,4
 *  3            normal          1,2               1,2,4
 *
 * For a description of the meta-data tables, see
 *
 * http://www.lofar.org/operations/lib/exe/fetch.php?media=public:documents:ms2_description_for_lofar_2.08.00.pdf
 */

//# Forward Declarations
namespace casacore
{
  class MPosition;
  template<class T>
  class Block;
}


namespace LOFAR
{
  namespace Cobalt
  {

    class MeasurementSetFormat
    {
    public:
      MeasurementSetFormat(const Parset &, uint32 alignment = 1);
      ~MeasurementSetFormat();

      void addSubband(const std::string MSname, unsigned subband);

      // casacore/measurementset mutex
      static Mutex sharedMutex;

    private:
      const Parset &itsPS;

      const std::vector<std::string> stationNames;
      const MultiDimArray<double,2>  antPos;

      const unsigned itsNrAnt;
      uint32 itsNrTimes;

      double itsStartTime;
      double itsTimeStep;


      SmartPtr<MSLofar> itsMS;

      const uint32 itsAlignment;

      void createMSTables(const std::string &MSname, unsigned subband);
      void createMSMetaFile(const std::string &MSname, unsigned subband);

      void fillFeed();
      void fillAntenna(const casacore::Block<casacore::MPosition>& antMPos);
      void fillField(unsigned subarray);
      void fillPola();
      void fillDataDesc();
      void fillSpecWindow(unsigned subband);
      void fillObs(unsigned subarray);
      void fillHistory();
      void fillProcessor();
      void fillState();
      void fillPointing(unsigned subarray);
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

