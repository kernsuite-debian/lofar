//# TBB_Station.cc: TBB per-station routines
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

#include "TBB_Station.h"
#include <boost/format.hpp>

#ifdef basename // some glibc have this as a macro
#undef basename
#endif
#include <Common/SystemUtil.h>
#include <Common/LofarLogger.h>
#include <Common/LofarConstants.h>
#include "CommonLofarAttributes.h"

namespace LOFAR
{
  namespace Cobalt
  {

    using namespace std;

    TBB_Station::TBB_Station(const string& stationName, Mutex& h5Mutex, const Parset& parset,
                             const std::map < uint32_t, double >& allSubbandCentralFreqs,
                             const StationMetaData& stationMetaData, const string& h5Filename,
                             const std::size_t _subbandSize)
      : itsH5File(dal::TBB_File(h5Filename, dal::TBB_File::CREATE)),
        itsH5Mutex(h5Mutex),
        itsStation(itsH5File.station(stationName)),
        itsDipoles(MAX_RSPBOARDS /* = per station*/ * NR_RCUS_PER_RSPBOARD), // = 192 for int'l stations
        itsParset(parset),
        itsAllSubbandCentralFreqs(allSubbandCentralFreqs),
        itsStationMetaData(stationMetaData),
        itsH5Filename(h5Filename),
        subbandSize{_subbandSize}
    {
      LOG_INFO_STR("TBB: Created HDF5 file " << LOFAR::basename(h5Filename));

      writeCommonLofarAttributes(itsH5File, parset);
      initTBB_RootAttributesAndGroups(stationName);
    }

    TBB_Station::~TBB_Station()
    {
      /*
       * Apart from the main thread, also potentially (rarely) executed by an output thread on failed
       * to insert new TBB_Station object into an std::map. For the output thread case, do dc and slH5.
       */
      ScopedDelayCancellation dc;
      try {
        ScopedLock slH5(itsH5Mutex);
        if(doTransient() == true)
        {
            itsStation.nofDipoles().value = itsStation.dipoles().size();
        }
        else
        {
            itsStation.nofDipoles().value = itsStation.dipoleGroups().size();
        }

      } catch (exception& exc) { // dal::DALException or worse
        LOG_WARN_STR("TBB: failed to set station NOF_DIPOLES attribute: " << exc.what());
      }
    }

    void TBB_Station::processPayload(const TBB_Frame& frame)
    {
        LOG_DEBUG_STR("TBB_Station::processPayload for station "
            << static_cast< uint32_t >(frame.header.stationID));

      // Guard against bogus incoming rsp/rcu IDs with at().
      TBB_Dipole& dipole = itsDipoles.at(frame.header.rspID * NR_RCUS_PER_RSPBOARD + frame.header.rcuID);

      // Each dipole stream is sent to a single port (thread), so no need to grab a mutex here to avoid double init.
      if (!dipole.isInitialized()) {
        LOG_DEBUG_STR("TBB_Station::processPayload for station "
            << static_cast< uint32_t >(frame.header.stationID)
            << " dipole init");
        // Do pass a ref to the h5 mutex for when writing into the HDF5 file.
        dipole.init(frame.header, itsParset, itsStationMetaData,
            itsAllSubbandCentralFreqs, itsH5Filename, subbandSize,
            itsStation, itsH5Mutex);
      }

      if (doTransient()) {
        dipole.processTransientFrameData(frame);
      } else { // spectral mode
        LOG_DEBUG_STR("TBB_Station::processPayload in spectral mode for station "
            << static_cast< uint32_t >(frame.header.stationID));

        dipole.processSpectralFrameData(frame);
      }
    }

    bool TBB_Station::doTransient() const
    {
      return false; //assume subband for testing for now.
      //TODO: have proper test
      //return itsAllSubbandCentralFreqs.empty();
    }

    // The writer creates one HDF5 file per station, so create only one Station Group here.
    void TBB_Station::initTBB_RootAttributesAndGroups(const string& stName)
    {
      if (doTransient()) {
        itsH5File.operatingMode().value = "transient";
      } else {
        itsH5File.operatingMode().value = "spectral";
      }

      itsStation.create();
      itsH5File.nofStations().value = 1u;
      initStationGroup(itsStation, stName);

      // Trigger Group
      dal::TBB_Trigger tg(itsH5File.trigger());
      tg.create();
      initTriggerGroup(tg);
    }

    void TBB_Station::initStationGroup(dal::TBB_Station& st, const string& stName)
    {
      st.groupType().value = "StationGroup";
      st.stationName().value = stName;

      // Phase centers (named 'position(s)' here and there
      // For now, store 'LBA' or 'HBA' phase centers. TODO: Also store:
      // - LOFAR reference phase center (in another HDF5 group)
      // - if HBA_<any>, always store phase centers for HBA and also HBA0 & HBA1 (core stations)
      //   so CR and other TBB users can process in whatever way they want. (reqs new DAL)
      const string antFieldName = stName + itsParset.getString("Observation.antennaArray"); // LBA or HBA (not HBA0, HBA1)
      try {
        const vector<double> stPos = itsParset.position(antFieldName);
        if (stPos.size() != 3) {
          throw APSException("antenna field position vector must be of size 3 instead of " + stPos.size());
        }
        // TODO: is phaseReference, only LBA or HBA (not HBA0 or HBA1) atm
        st.stationPosition().create(stPos.size()).set(stPos);
        st.stationPositionUnit().value = "m";
        st.stationPositionFrame().value = itsParset.positionType();
      } catch (APSException& exc) {
        LOG_WARN_STR("TBB: failed to write antenna field phase centers: " << exc.text());
      }

      // digital beam(s)
      if (itsParset.settings.SAPs.size() > 0) { // TODO: adapt DAL, so we can write all digital beams instead of only SAP 0, analog too if tiles (HBA)
        vector<double> beamDir(2);
        beamDir[0] = itsParset.settings.SAPs[0].direction.angle1;
        beamDir[1] = itsParset.settings.SAPs[0].direction.angle2;
        st.beamDirection().create(beamDir.size()).set(beamDir);
        st.beamDirectionUnit().value = "m";
        st.beamDirectionFrame().value = itsParset.settings.SAPs[0].direction.type;
      }

      try {
        // Delay coefficients as applied by COBALT
        // For now, store avg of delay_x and delay_y as clock correction; HBA_DUAL modes get HBA_JOINED vals for the mo. TODO: Instead, store:
        // - all delay.x, delay.y, phase0.x, phase0.y (reqs new DAL), for:
        // - used array mode (for a HBA_DUAL mode this gives 2x the vals) plus if HBA_<any> all of: HBA_ZERO, HBA_ONE, HBA_JOINED (skip one if used array mode or if not contained in used mode) (only for proper freq band) (reqs new DAL)

        string antSet = itsParset.settings.antennaSet;
        if (antSet.find("HBA_DUAL") != string::npos) { // HBA_DUAL or HBA_DUAL_INNER
          antSet = "HBA_JOINED"; // current fmt has 1 attrib, so resort to this for the mo
        }
/*
        int afIdx = itsParset.settings.antennaFieldIndex(antFieldName); // NOTE: fails for HBA_DUAL modes
        if (afIdx == -1) { // TODO: have antennaFieldIndex() throw instead of return -1
          throw APSException("antenna field not found: " + antFieldName);
        }
        double delay_x = itsParset.settings.antennaFields[afIdx].delay.x;
        double delay_y = itsParset.settings.antennaFields[afIdx].delay.y;
        double phase_x = itsParset.settings.antennaFields[afIdx].phase.x;
        double phase_y = itsParset.settings.antennaFields[afIdx].phase.y;
*/
        double delay_x = itsParset.getDouble(str(boost::format("PIC.Core.%s.%s.%s.delay.X") % antFieldName % antSet % itsParset.settings.bandFilter)/*, 0.0*/);
        double delay_y = itsParset.getDouble(str(boost::format("PIC.Core.%s.%s.%s.delay.Y") % antFieldName % antSet % itsParset.settings.bandFilter)/*, 0.0*/);
        double clockCorr = 0.5 * (delay_x + delay_y); // TODO: remove this backwards compat, since nobody uses TBB clock corr yet
        st.clockOffset().value = clockCorr;
        st.clockOffsetUnit().value = "s";
      } catch (APSException& exc) {
        LOG_WARN_STR("TBB: failed to write antenna field delays and phase0 values: " << exc.text());
      }

      //st.nofDipoles.value is set at the end (destr)
    }

    void TBB_Station::initTriggerGroup(dal::TBB_Trigger& tg)
    {
      tg.groupType().value = "TriggerGroup";
      tg.triggerType().value = "Unknown";
      tg.triggerVersion().value = 0; // There is no trigger algorithm info available to us yet.

      // Trigger parameters (how to decide if there is a trigger; per obs)
      try {
        tg.paramCoincidenceChannels().value = itsParset.getInt   ("Observation.ObservationControl.StationControl.TBBControl.NoCoincChann");
        tg.paramCoincidenceTime().value = itsParset.getDouble("Observation.ObservationControl.StationControl.TBBControl.CoincidenceTime");
        tg.paramDirectionFit().value = itsParset.getString("Observation.ObservationControl.StationControl.TBBControl.DoDirectionFit");
        tg.paramElevationMin().value = itsParset.getDouble("Observation.ObservationControl.StationControl.TBBControl.MinElevation");
        tg.paramFitVarianceMax().value = itsParset.getDouble("Observation.ObservationControl.StationControl.TBBControl.MaxFitVariance");
        //itsParset.getString("Observation.ObservationControl.StationControl.TBBControl.ParamExtension");

        if (!doTransient()) {
          // add the spectral mode trigger parameters
          // TODO 20181127: - fill in these parameters according to the sources defined by StV
          //                - as agreed with Joern, these parameters should come from the parset fed to the datawriter. Joern, can you
          tg.triggerDispersionMeasure().value = 0;
          tg.triggerDispersionMeasureUnit().value = "not filled in";
          tg.time().value = std::vector<unsigned int>();
          tg.sampleNumber().value = std::vector<unsigned int>();
          tg.fitDirectionCoordinateSystem();
          tg.fitDirectionAngle1().value = 0;
          tg.fitDirectionAngle2().value = 0;
          tg.fitDirectionDistance().value = 0;
          tg.fitDirectionVariance().value = 0;
          tg.referenceFrequency().value = 0;
          tg.observatoryCoordinates().value = std::vector<double>();
          tg.observatoryCoordinatesCoordinateSystem().value = "not filled in";
          tg.triggerId().value = "not filled in";
          tg.additionalInfo().value = "not filled in";
        }

      } catch (APSException& exc) {
        LOG_WARN_STR("TBB: Failed to write trigger parameters: " << exc.text());
      }



      // Trigger data (per trigger)
      // N/A atm

      /*
       * It is very likely that the remaining (optional) attributes and the trigger alg
       * will undergo many changes. TBB user/science applications will have to retrieve and
       * set the remaining fields "by hand" for a while using e.g. DAL by checking and
       * specifying each attribute name presumed available.
       * Until it is clear what is needed and available, this cannot be standardized.
       *
       * If you add fields using parset getTYPE(), catch the possible APSException as above.
       */

    }

  } // namespace Cobalt
} // namespace LOFAR

