//# TBB_Writer.h: Manage TBB StreamWriter objects, 1 per incoming station
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

#ifndef LOFAR_COBALT_OUTPUTPROC_TBBWRITER_H
#define LOFAR_COBALT_OUTPUTPROC_TBBWRITER_H 1

#include "TBB_Station.h"
#include "TBB_StreamWriter.h"

#include <map>

namespace LOFAR
{
  namespace Cobalt
  {

    class TBB_Writer
    {
      // Global H5 mutex. All HDF5 operations go under a single mutex, incl file creation:
      // we don't depend on the HDF5 lib being compiled with --thread-safe.
      Mutex itsH5Mutex; // used in ~Station(), so declared before itsStations below for proper destruction order

      // Usually, we handle only 1 station per writer, but users have requested to support multiple concurrently (still needed?).
      std::map<unsigned, SmartPtr<TBB_Station> > itsStations; // stationID -> SmartPtr<TBB_Station>
      Mutex itsStationsMutex;

      const Parset& itsParset;
      const std::map< uint32_t, double > itsAllSubbandCentralFreqs; // size: transient mode: 0, spectral mode: != 0
      const StationMetaDataMap& itsStationMetaDataMap;
      StationMetaData itsUnknownStationMetaData; // referred to for data from unknown stations (fallback)
      const std::string& itsOutDir;
      const unsigned itsNrSubbands;
      const std::size_t subbandSize;

      unsigned itsRunNr;

      std::vector<SmartPtr<TBB_StreamWriter> > itsStreamWriters;
      // Note: do not add vars here; leave itsStreamWriters last for safe thread destruction!

      // do not use
      TBB_Writer();
      TBB_Writer(const TBB_Writer& writer);
      TBB_Writer& operator=(const TBB_Writer& rhs);

    public:
    TBB_Writer(const std::vector<std::string>& inputStreamNames,
        const Parset& parset, const std::size_t subbandSize,
        const StationMetaDataMap& stationMetaDataMap, const std::string& outDir,
        const std::string& logPrefix, std::vector<int>& thrExitStatus);

      // Main thread
      time_t getTimeoutStampSec(unsigned streamWriterNr) const;

      // StreamWriter Output threads
      TBB_Station *getStation(const TBB_Header& header);
      std::string createNewTBB_H5Filename(const TBB_Header& header, const std::string& stationName);

      unsigned getSampleFreqMHz() const;
      const std::map< uint32_t, double >& getAllSubbandCentralFreqs() const;

    private:
      /**
       * Returns a @std::map that contains the central frequencies of used
       * bands only.
       * @param parset Parset for the incoming data.
       * @return A map that contains the central frequencies of the bands used
       * in the observation.
       */
      std::map< uint32_t, double > createAllSubbandCentralFreqs(const Parset& parset) const; // MHz
      static double subbandCentralFreq(unsigned subbandNr, unsigned nyquistZone, double sampleFreq);

      static std::string formatFilenameTimestamp(const struct timeval& tv, const char* output_format,
                                                 const char* output_format_secs, size_t output_size);
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

