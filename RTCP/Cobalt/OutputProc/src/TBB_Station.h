//# TBB_Station.h: TBB per-station routines
//# Copyright (C) 2012-2017  ASTRON (Netherlands Institute for Radio Astronomy)
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

#ifndef LOFAR_COBALT_OUTPUTPROC_TBBSTATION_H
#define LOFAR_COBALT_OUTPUTPROC_TBBSTATION_H 1

#include "TBB_Dipole.h"

namespace LOFAR
{
  namespace Cobalt
  {

    class TBB_Station
    {
      dal::TBB_File itsH5File;
      Mutex& itsH5Mutex;

      dal::TBB_Station itsStation;
      std::vector<TBB_Dipole> itsDipoles;
      const Parset& itsParset;
      const std::map< uint32_t, double >& itsAllSubbandCentralFreqs; // size: transient mode: 0, spectral mode: != 0
      const StationMetaData& itsStationMetaData;
      const std::string itsH5Filename;
      const std::size_t subbandSize;

      // do not use
      TBB_Station();
      TBB_Station(const TBB_Station& station);
      TBB_Station& operator=(const TBB_Station& rhs);

    public:
      // This constructor must be called with the h5Mutex already held.
      // The caller must still unlock after the return, the constructor does not use the passed ref to unlock.
            TBB_Station(const std::string& stationName, Mutex& h5Mutex,
                const Parset& parset,
                const std::map< uint32_t, double >& allSubbandCentralFreqs,
                const StationMetaData& stationMetaData,
                const std::string& h5Filename,
                const std::size_t subbandSize);
      ~TBB_Station();

      // Output threads
      void processPayload(const TBB_Frame& frame);

    private:
      bool doTransient() const;

      void initTBB_RootAttributesAndGroups(const std::string& stName);
      void initStationGroup(dal::TBB_Station& st, const std::string& stName);
      void initTriggerGroup(dal::TBB_Trigger& tg);
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

