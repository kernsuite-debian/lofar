//# TBB_Dipole.h: TBB per-dipole routines to store incoming TBB data
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

#ifndef LOFAR_COBALT_OUTPUTPROC_TBBDIPOLE_H
#define LOFAR_COBALT_OUTPUTPROC_TBBDIPOLE_H 1

#include "TBB_Frame.h"
#include <vector>
#include <map>
#include <memory>
#include <boost/scoped_ptr.hpp>
#include <boost/crc.hpp>

#include <Common/Thread/Mutex.h>
#include <Stream/FileStream.h>
#include <CoInterface/Parset.h>
#include <CoInterface/SmartPtr.h> // when switching to C++11, replace SmartPtr with unique_ptr

#include <dal/lofar/TBB_File.h>   // https://github.com/nextgen-astrodata/DAL

namespace LOFAR
{
  namespace Cobalt
  {

    class TBB_Dipole
    {
      /*
       * Note: Users don't want 1 raw file per dipole.
       * But as long as LOFAR control doesn't provide dump duration or length in the parset, we cannot easily do any better.
       * Once LOFAR control supplies suitable parsets with ALL metadata, dumpInfo can be dumped...
       */
      boost::scoped_ptr<dal::TBB_DipoleCommon> itsDALDipole;
      inline dal::TBB_DipoleDataset* itsDipoleDataset() { return dynamic_cast<dal::TBB_DipoleDataset*>(itsDALDipole.get()); }
      inline dal::TBB_DipoleGroup* itsDipoleGroup() { return dynamic_cast<dal::TBB_DipoleGroup*>(itsDALDipole.get()); }

      std::map< uint32_t, double > itsAllSubbandCentralFreqs; // size: transient mode: 0, spectral mode: != 0

      std::string itsH5Filename;

      struct DumpInfo {
        SmartPtr<LOFAR::FileStream> itsRawFile;
        std::vector<dal::Range> itsFlagOffsets;
        uint64_t itsDatasetLen; // in values, including holes from missing data

        // These 2 fields are lazily initialized from the 1st received frame
        uint32_t itsTime0; // seconds
        union
        {
            // transient mode: sampleNr; spectral mode: sliceNr
            uint32_t itsSampleNr0;
            uint32_t itsSliceNr0;
        };
      };
      DumpInfo itsDumpInfo;

      time_t itsLastLogErrorTime;

      /*
       * Same truncated polynomial as standard crc32, but with:
       *   initial_remainder=0, final_xor_value=0, reflected_input=false, reflected_remainder_output=false
       * The boost::crc_optimal<> declarations precompute lookup tables,
       * so do not declare inside the checking routine. (Still, for every TBB_Dipole...)
       */
      boost::crc_optimal<32, 0x04C11DB7 /*, 0, 0, false, false*/> itsCrc32gen;

      // do not use
      TBB_Dipole& operator=(const TBB_Dipole& rhs);

    public:
      TBB_Dipole();
      TBB_Dipole(const TBB_Dipole& rhs); // do not use; only for TBB_Station std::vector<TBB_Dipole>(N) constr
      ~TBB_Dipole();


      // All TBB_Dipole objects are default constructed in a vector, so have init().
      void init(const TBB_Header& header, const Parset& parset,
          const StationMetaData& stationMetaData,
          const std::map< uint32_t, double >& allSubbandCentralFreqs,
          const std::string& h5Filename,
          const std::size_t subbandDataSizeInBytes, dal::TBB_Station& station,
          Mutex& h5Mutex);

      // Output threads
      bool isInitialized() const;

      void processTransientFrameData(const TBB_Frame& frame);
      void processSpectralFrameData(const TBB_Frame& frame);

    private:
        bool doTransient() const;
        void appendFlags(DumpInfo& di, size_t offset, size_t len);

      // initTBB_DipoleGroupOrDataset() must be called with the global h5Mutex held.
            void initTBB_DipoleGroupOrDataset(const TBB_Header& header,
                const Parset& parset, const StationMetaData& stationMetaData,
                const std::string& rawFilename, dal::TBB_Station& station);

        bool crc32tbb(const TBB_Payload* payload, size_t nTrSamples);

        /**
         * This structure is for book keeping of received sub-band data.
         * I create a std::map of this with key = sub-band number in @init where
         * it is read from the parset which sub-bands shall be expected and the
         * map is filled accordingly.  If the map does not have an entry for
         * a sub-band, that sub-band is not given in the parset.
         *
         * When a new sub-band frame is received it is checked if the map
         * @ref subBandBookKeeping contains an entry that has sub-band number
         * as key.  If not, the sub-band data is unexpected and the frame will
         * be discarded.
         *
         * If the map contains an entry for the sub-band and the entry's
         * @ref subBandBookKeeping.isInitialised value is false, then it is
         * assumed that the just received frame is the very first frame that
         * was ever sent for this sub-band and the entry will be set-up with
         * proper data (setting time0 and slice0 for example) and
         * @ref subBandBookKeeping.isInitialised will be set to true.
         *
         * Obviously the assumption above that the very first received frame for
         * a sub-band is the frame that contains time0 and slice0 is breaking
         * the whole concept that I do not care about the order in which frames
         * for a sub-band will arrive.  But hey, I have to start somewhere.
         *
         * From then on it is pretty simple.  Every time a new frame comes in
         * the data of the relevant map entry will be updated.  At some point
         * totalSizeInSamples == currentSizeInSamples will be true and the
         * sub-band data set is complete.  isComplete will be set true and any
         * future frame that contains more data for this sub-band will be
         * discarded.
         */
        struct SubBandBookKeeping
        {
            SubBandBookKeeping(std::size_t _bandNr, std::size_t subBandSize,
                double _centralFrequency):
                totalSubBandSizeInSamples{subBandSize},
                bandNr{_bandNr},
                centralFrequency{_centralFrequency},
                time0{0U},
                slice0{0U},
                currentSizeInSamples{0U},
                isComplete{false},
                isInitialised{false},
                dataSet{nullptr}
            {
            }

            std::size_t totalSubBandSizeInSamples;
            std::size_t bandNr;
            double centralFrequency;
            int64_t time0;
            uint32_t slice0;
            std::size_t currentSizeInSamples;
            bool isComplete;
            bool isInitialised;
            std::unique_ptr< dal::TBB_SubbandDataset > dataSet;
        };

        std::map< uint32_t, struct SubBandBookKeeping > subBandBookKeeping;

        enum TBB_Mode
        {
            TBB_MODE_TRANSIENT,
            TBB_MODE_SPECTRAL
        };
        TBB_Mode tbbMode;
    };

  } // namespace Cobalt
} // namespace LOFAR

#endif

