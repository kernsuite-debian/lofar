//# TBB_Writer.cc: Write TBB data into an HDF5 file
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

#include <lofar_config.h>

#include "TBB_Writer.h"

#include <map>
#include <cmath>
#include <cerrno>
#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>
#include <boost/format.hpp>

#include <Common/LofarLogger.h>

#include <dal/lofar/StationNames.h>

#define TBB_TRANSIENT_MODE                      1
#define TBB_SPECTRAL_MODE                       2

namespace LOFAR
{
  namespace Cobalt
  {

    using namespace std;

    TBB_Writer::TBB_Writer(const vector<string>& inputStreamNames, const Parset& parset,
        const std::size_t _subbandSize,
        const StationMetaDataMap& stationMetaDataMap,
        const string& outDir, const string& logPrefix,
        vector<int>& thrExitStatus):
        itsParset(parset),
        itsAllSubbandCentralFreqs(createAllSubbandCentralFreqs(parset)),
        itsStationMetaDataMap(stationMetaDataMap),
        itsOutDir(outDir),
        itsNrSubbands(parset.getUint32Vector("Observation.TBB.TBBsetting.subbandList", true).size()),
        subbandSize{_subbandSize},
        itsRunNr(0)
    {
      itsUnknownStationMetaData.available = false;

      itsStreamWriters.reserve(inputStreamNames.size());
      for (unsigned i = 0; i < inputStreamNames.size(); i++) {
        itsStreamWriters.push_back(SmartPtr<TBB_StreamWriter>(new TBB_StreamWriter(*this,
            inputStreamNames[i], logPrefix, thrExitStatus.at(2 * i), thrExitStatus.at(2 * i + 1))));
      }
    }

    std::map< uint32_t, double > TBB_Writer::createAllSubbandCentralFreqs(const Parset& parset) const
    {
      std::map< uint32_t, double > centralFreqs;

      int operatingMode = parset.getInt("Observation.TBB.TBBsetting.operatingMode", 0);
      if (operatingMode == TBB_SPECTRAL_MODE) {
        vector<unsigned> tbbSubbandList(parset.getUint32Vector("Observation.TBB.TBBsetting.subbandList", true));
        size_t nrSubbands = tbbSubbandList.size();
        if (nrSubbands == 0 || nrSubbands > MAX_TBB_SPECTRAL_SUBBANDS) {
          throw APSException("TBB: spectral mode selected, but empty or too long Observation.TBB.TBBsetting.subbandList");
        }
        std::sort  (tbbSubbandList.begin(), tbbSubbandList.end());
        std::unique(tbbSubbandList.begin(), tbbSubbandList.end());
        if (nrSubbands != tbbSubbandList.size()) {
          throw APSException("TBB: duplicate subband numbers in Observation.TBB.TBBsetting.subbandList");
        }
        if (tbbSubbandList.back() >= RSP_NR_SUBBANDS) { // sorted, so checking last value suffices
          throw APSException("TBB: subband number out of range [0, 512) in Observation.TBB.TBBsetting.subbandList");
        }

        unsigned nyquistZone = parset.settings.nyquistZone();
        unsigned sampleFreq = parset.settings.clockMHz;
        for(const auto subBandNumber: tbbSubbandList)
        {
            centralFreqs.insert(std::make_pair(subBandNumber,
                subbandCentralFreq(subBandNumber, nyquistZone, sampleFreq)));
        }
      } else if (operatingMode != TBB_TRANSIENT_MODE) {
        throw APSException("TBB: invalid Observation.TBB.TBBsetting.operatingMode");
      }

      return centralFreqs;
    }

    double TBB_Writer::subbandCentralFreq(unsigned subbandNr, unsigned nyquistZone, double sampleFreq)
    {
      return (nyquistZone - 1 + static_cast< double >(subbandNr) / RSP_NR_SUBBANDS) * sampleFreq * 0.5;
    }

    TBB_Station *TBB_Writer::getStation(const TBB_Header& header)
    {
      ScopedLock sl(itsStationsMutex); // protect against insert below
      map<unsigned, SmartPtr<TBB_Station> >::iterator stIt(itsStations.find(header.stationID));
      if (stIt != itsStations.end()) {
        LOG_DEBUG_STR("TBB_Writer::getStation: found known station for id "
            << static_cast< uint32_t >(header.stationID));

        return stIt->second.get(); // common case
      }

      // Create new station with HDF5 file and station HDF5 group.
      string stationName = dal::stationIDToName(header.stationID);
      string h5Filename = createNewTBB_H5Filename(header, stationName);
      StationMetaDataMap::const_iterator stMdIt(itsStationMetaDataMap.find(header.stationID));
      // If not found, station is not participating in the observation. Should not happen, but don't panic.
      const StationMetaData& stMetaData = stMdIt == itsStationMetaDataMap.end() ? itsUnknownStationMetaData : stMdIt->second;

      SmartPtr<TBB_Station> station;
      {
        ScopedLock slH5(itsH5Mutex);
        station = new TBB_Station(stationName, itsH5Mutex, itsParset,
            itsAllSubbandCentralFreqs, stMetaData, h5Filename, subbandSize);
      }

      LOG_DEBUG_STR("TBB_Writer::getStation: returning new station for id "
          << static_cast< uint32_t >(header.stationID));
      return itsStations.insert(make_pair(header.stationID, station)).first->second.get();
    }

    string TBB_Writer::createNewTBB_H5Filename(const TBB_Header& header, const string& stationName)
    {
      // Use the recording time of the first (received) frame as timestamp.
      struct timeval tv{header.time, 0L};
      unsigned long usecNr{0UL};
      if(itsAllSubbandCentralFreqs.empty() == true)
      {
          // transient mode
          usecNr = header.sampleNr; // we use an uncorrected sampleNr on 200 MHz clock if 'time & 1', but ok for filenames
          tv.tv_usec = static_cast< unsigned long >(
              round(static_cast< double >(usecNr) / header.sampleFreq ));
      }
      else
      {
          // spectral mode
          // This is the slice number!
          usecNr = header.bandSliceNr >> TBB_SLICE_NR_SHIFT;

          tv.tv_usec = std::lround(
              static_cast< double >(usecNr) / header.sampleFreq
                  * SPECTRAL_TRANSFORM_SIZE);
      }

      // Generate the output filename, because for TBB it is not in the parset.
      // From LOFAR-USG-ICD005 spec named "LOFAR Data Format ICD File Naming Conventions", by A. Alexov et al.
      const char output_format[] = "D%Y%m%dT%H%M"; // without secs
      const char output_format_secs[] = "%06.3fZ"; // total width of ss.sss is 6
      const char output_format_example[] = "DYYYYMMDDTHHMMSS.SSSZ";
      const string triggerDateTime = formatFilenameTimestamp(tv, output_format, output_format_secs,
                                                             sizeof(output_format_example));
      const string typeExt("tbb.h5");
      string h5Filename = str(boost::format("%sL%u_%s_%s_%s") % itsOutDir % itsParset.settings.observationID %
                              stationName % triggerDateTime % typeExt);

      // If the file already exists, add a run nr and retry. (might race and doesn't check .raw, but good enough)
      // If >1 stations per node, start at the prev run nr if any (hence itsRunNr).
      if (itsRunNr == 0) {
        if (::access(h5Filename.c_str(), F_OK) != 0 && errno == ENOENT) { // TODO: access(2) is wrong: it tests real instead of effective uid/gid (idem below)
          // Does not exist (or broken dir after all, or dangling sym link...). Try this one.
          return h5Filename;
        } else { // exists, inc run number
          itsRunNr = 1;
        }
      }

      size_t pos = h5Filename.size() - typeExt.size();
      string runNrStr = str(boost::format("R%03u_") % itsRunNr);
      h5Filename.insert(pos, runNrStr);
      while (itsRunNr < 1000 && ( ::access(h5Filename.c_str(), F_OK) == 0 || errno != ENOENT )) {
        itsRunNr += 1;
        runNrStr = str(boost::format("R%03u_") % itsRunNr);
        h5Filename.replace(pos, runNrStr.size(), runNrStr);
      }
      if (itsRunNr == 1000) { // run number is supposed to fit in 3 digits
        throw StorageException("failed to generate new .h5 filename after trying 1000 filenames.");
      }

      return h5Filename;
    }

    // The output_format is without seconds. The output_size is including the terminating NUL char.
    string TBB_Writer::formatFilenameTimestamp(const struct timeval& tv, const char* output_format,
                                               const char* output_format_secs, size_t output_size)
    {
      struct tm tm;
      ::gmtime_r(&tv.tv_sec, &tm);
      double secs = tm.tm_sec + tv.tv_usec / 1000000.0;

      vector<char> date(output_size);

      size_t nwritten = ::strftime(&date[0], output_size, output_format, &tm);
      if (nwritten == 0) {
        date[0] = '\0';
      }
      (void)::snprintf(&date[0] + nwritten, output_size - nwritten, output_format_secs, secs);

      return string(&date[0]);
    }

    unsigned TBB_Writer::getSampleFreqMHz() const
    {
      return itsParset.settings.clockMHz;
    }

    const std::map< uint32_t, double>& TBB_Writer::getAllSubbandCentralFreqs() const
    {
      return itsAllSubbandCentralFreqs;
    }

    time_t TBB_Writer::getTimeoutStampSec(unsigned streamWriterNr) const
    {
      return itsStreamWriters.at(streamWriterNr)->getTimeoutStampSec();
    }

  } // namespace Cobalt
} // namespace LOFAR

