//# MeasurementSetFormat.cc: Creates required infrastructure for
//# a LofarStMan MeasurementSet.
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

#include <lofar_config.h>

#include "MeasurementSetFormat.h"

#include <fstream>
#include <iostream>
#include <algorithm>
#include <cstdlib>

#if defined __linux__
#include <linux/limits.h>
#endif

#include <casacore/tables/Tables/TableDesc.h>
#include <casacore/tables/Tables/SetupNewTab.h>
#include <casacore/tables/Tables/Table.h>
#include <casacore/tables/Tables/TableLock.h>
#include <casacore/tables/Tables/TableRecord.h>
#include <casacore/tables/Tables/ScaColDesc.h>
#include <casacore/tables/Tables/ArrColDesc.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/tables/Tables/ArrayColumn.h>
//#include <casacore/tables/DataMan/StandardStMan.h>
#include <casacore/casa/Arrays/Array.h>
#include <casacore/casa/Arrays/ArrayMath.h>
#include <casacore/casa/Arrays/ArrayIO.h>
#include <casacore/casa/Arrays/ArrayLogical.h>
#include <casacore/casa/Containers/BlockIO.h>
#include <casacore/casa/OS/RegularFile.h>
#include <casacore/casa/Utilities/Assert.h>
#include <casacore/casa/IO/RegularFileIO.h>
#include <casacore/casa/IO/RawIO.h>
#include <casacore/casa/IO/CanonicalIO.h>
#include <casacore/casa/OS/HostInfo.h>
#include <casacore/casa/Exceptions/Error.h>
#include <casacore/casa/iostream.h>
#include <casacore/casa/sstream.h>
#include <casacore/casa/BasicSL/Constants.h>

#include <casacore/ms/MeasurementSets.h>

#include <MSLofar/MSLofar.h>
#include <MSLofar/MSLofarField.h>
#include <MSLofar/MSLofarAntenna.h>
#include <MSLofar/MSLofarObservation.h>
#include <MSLofar/MSLofarAntennaColumns.h>
#include <MSLofar/MSLofarFieldColumns.h>
#include <MSLofar/MSLofarObsColumns.h>
#include <MSLofar/BeamTables.h>
#include <LofarStMan/LofarStMan.h>
#include <CoInterface/Exceptions.h>
#include <Common/LofarLocators.h>
#include <Common/Timer.h>
#include <OutputProc/Package__Version.h>


using namespace casacore;

namespace LOFAR
{
  namespace Cobalt
  {

    NSTimer creationTimer("MeasurementSet creation", true, true);
    Mutex MeasurementSetFormat::sharedMutex;


    // unix time to mjd time (in seconds instead of days)
    static double toMJDs( double time )
    {
      // 40587 modify Julian day number = 00:00:00 January 1, 1970, GMT
      return 40587.0 * 24 * 60 * 60 + time;
    }


    MeasurementSetFormat::MeasurementSetFormat(const Parset &ps, unsigned alignment)
      :
      itsPS(ps),
      stationNames(itsPS.mergedStationNames()),
      antPos(itsPS.positions()),
      itsNrAnt(stationNames.size()),
      itsMS(0),
      itsAlignment(alignment)
    {
      if (itsPS.nrTabStations() > 0) {
        ASSERTSTR(antPos.size() == itsPS.nrTabStations(),
                  antPos.size() << " == " << itsPS.nrTabStations());
      } else {
        ASSERTSTR(antPos.size() == itsPS.settings.antennaFields.size(),
                  antPos.size() << " == " << itsPS.settings.antennaFields.size());
      }

      itsStartTime = toMJDs(itsPS.settings.startTime);

      itsTimeStep = itsPS.settings.correlator.integrationTime();
      itsNrTimes = itsPS.settings.correlator.nrIntegrations;
    }


    MeasurementSetFormat::~MeasurementSetFormat()
    {
      ScopedLock scopedLock(sharedMutex);

      itsMS = 0;
    }


    void MeasurementSetFormat::addSubband(const string MSname, unsigned subband)
    {
      ScopedLock scopedLock(sharedMutex);
      NSTimer::StartStop ss(creationTimer);

      /// Create the MeasurementSet with all required
      /// tables. Note that the MS object is destroyed immediately.
      createMSTables(MSname, subband);
      /// Next make a metafile which describes the raw datafile we're
      /// going to write
      createMSMetaFile(MSname, subband);

      // Release itsMS, we don't need it anymore
      itsMS = 0;
    }


    void MeasurementSetFormat::createMSTables(const string &MSname, unsigned subband)
    {
      try {
        int subarray = itsPS.settings.subbands[subband].SAP;
        string directionType = itsPS.settings.SAPs[subarray].direction.type;

        TableDesc td = MS::requiredTableDesc();
        MS::addColumnToDesc(td, MS::DATA, 2);
        MS::addColumnToDesc(td, MS::WEIGHT_SPECTRUM, 2);
        // Set the reference frame of UVW to J2000.
        // Note it must be done here, because the UVW column in the MS is readonly
        // (because LofarStMan is used).
        {

          ColumnDesc &col(td.rwColumnDesc("UVW"));
          TableRecord rec = col.keywordSet().asRecord("MEASINFO");
          rec.define("Ref", directionType);
          col.rwKeywordSet().defineRecord("MEASINFO", rec);
        }

        SetupNewTable newtab(MSname, td, Table::New);

        LofarStMan lofarstman;
        newtab.bindAll(lofarstman);

        // MSLofar() constructor needs a NEW table, to avoid checks
        // for subtables that aren't yet there.
        itsMS = new MSLofar(newtab);
        itsMS->createDefaultSubtables(Table::New);

        Block<MPosition> antMPos(itsNrAnt);

        try {
          for (unsigned i = 0; i < itsNrAnt; i++) {
            antMPos[i] = MPosition(MVPosition(antPos[i][0],
                                              antPos[i][1],
                                              antPos[i][2]),
                                   MPosition::ITRF);
          }
        } catch (AipsError &ex) {
          LOG_FATAL_STR("AipsError: " << ex.what());
        }

        fillAntenna(antMPos);
        fillFeed();
        fillField(subarray);
        fillPola();
        fillDataDesc();
        fillSpecWindow(subband);
        fillObs(subarray);
        fillHistory();
        fillProcessor();
        fillState();
        fillPointing(subarray);

        try {
          // Use ConfigLocator to locate antenna configuration files.
          ConfigLocator configLocator;
          // Add static meta data path from parset at the front for regression testing.
          string staticMetaDataDir =
            itsPS.isDefined("Cobalt.OutputProc.StaticMetaDataDirectory")
            ? itsPS.getString("Cobalt.OutputProc.StaticMetaDataDirectory", "")
            : itsPS.getString("OLAP.Storage.StaticMetaDataDirectory", "");
          if (!staticMetaDataDir.empty()) {
            configLocator.addPathAtFront(staticMetaDataDir);
          }
          LOG_DEBUG_STR("Config locator search path: " << 
                        configLocator.getPath());
          // Fill the tables containing the beam info.
          BeamTables::fill(*itsMS,
                           itsPS.settings.antennaSet,
                           configLocator.locate("AntennaSets.conf"),
                           configLocator.locate("StaticMetaData"),
                           configLocator.locate("StaticMetaData"));
        } catch (LOFAR::AssertError &ex) {
          LOG_ERROR_STR("Failed to add beam tables: " << ex);
        }
      } catch (AipsError &ex) {
        THROW(StorageException, "AIPS/CASA error: " << ex.getMesg());
      }

      // Flush the MS to make sure all tables are written
      itsMS->flush();
      // Delete the MS object, since we don't need it anymore
    }


    void MeasurementSetFormat::fillAntenna(const Block<MPosition>& antMPos)
    {
      // Determine constants for the ANTENNA subtable.
      casacore::Vector<Double> antOffset(3);
      antOffset = 0;
      casacore::Vector<Double> phaseRef(3);

      // Fill the ANTENNA subtable.
      MSLofarAntenna msant = itsMS->antenna();
      MSLofarAntennaColumns msantCol(msant);
      msant.addRow (itsNrAnt);

      for (unsigned i = 0; i < itsNrAnt; i++) {
        msantCol.name().put(i, stationNames[i]);
        msantCol.stationId().put(i, 0);
        msantCol.station().put(i, "LOFAR");
        msantCol.type().put(i, "GROUND-BASED");
        msantCol.mount().put(i, "X-Y");
        msantCol.positionMeas().put(i, antMPos[i]);
        msantCol.offset().put(i, antOffset);
        msantCol.dishDiameter().put(i, 0);
        vector<double> psPhaseRef =
          itsPS.getDoubleVector("PIC.Core." + stationNames[i] + ".phaseCenter");
        ASSERTSTR(psPhaseRef.size() == 3,
                  "phaseCenter in parset of station " << stationNames[i]);
        std::copy(psPhaseRef.begin(), psPhaseRef.end(), phaseRef.begin());
        msantCol.phaseReference().put(i, phaseRef);
        msantCol.flagRow().put(i, False);
      }

      msant.flush();
    }


    void MeasurementSetFormat::fillFeed()
    {
      // Determine constants for the FEED subtable.
      unsigned nRec = 2;
      casacore::Matrix<Double> feedOffset(2,nRec);
      feedOffset = 0;
      casacore::Matrix<Complex> feedResponse(nRec,nRec);
      feedResponse = Complex(0.0,0.0);

      for (unsigned rec = 0; rec < nRec; rec++)
        feedResponse(rec,rec) = Complex(1.0, 0.0);

      casacore::Vector<String> feedType(nRec);
      feedType(0) = "X";
      feedType(1) = "Y";
      casacore::Vector<Double> feedPos(3);
      feedPos = 0.0;
      casacore::Vector<Double> feedAngle(nRec);
      feedAngle = -C::pi_4;                  // 0 for parallel dipoles

      // Fill the FEED subtable.
      MSFeed msfeed = itsMS->feed();
      MSFeedColumns msfeedCol(msfeed);
      msfeed.addRow(itsNrAnt);

      for (unsigned i = 0; i < itsNrAnt; i++) {
        msfeedCol.antennaId().put(i, i);
        msfeedCol.feedId().put(i, 0);
        msfeedCol.spectralWindowId().put(i, -1);
        msfeedCol.time().put(i, itsStartTime + itsNrTimes * itsTimeStep / 2.);
        msfeedCol.interval().put(i, itsNrTimes * itsTimeStep);
        msfeedCol.beamId().put(i, -1);
        msfeedCol.beamOffset().put(i, feedOffset);
        msfeedCol.polarizationType().put(i, feedType);
        msfeedCol.polResponse().put(i, feedResponse);
        msfeedCol.position().put(i, feedPos);
        msfeedCol.receptorAngle().put(i, feedAngle);
        msfeedCol.numReceptors().put(i, 2);
      }

      msfeed.flush();
    }


    void MeasurementSetFormat::fillField(unsigned subarray)
    {
      // Beam direction
      MVDirection radec(Quantity(itsPS.settings.SAPs[subarray].direction.angle1, "rad"),
                        Quantity(itsPS.settings.SAPs[subarray].direction.angle2, "rad"));
      MDirection::Types beamDirectionType;
      if (!MDirection::getType(beamDirectionType, itsPS.settings.SAPs[subarray].direction.type))
        THROW(StorageException, "Beam direction type unknown: " << itsPS.settings.SAPs[subarray].direction.type);
      MDirection indir(radec, beamDirectionType);
      casacore::Vector<MDirection> outdir(1);
      outdir(0) = indir;

      // AnaBeam direction type
      MDirection::Types anaBeamDirectionType;
      if (itsPS.settings.anaBeam.enabled)
        if (!MDirection::getType(anaBeamDirectionType, itsPS.settings.anaBeam.direction.type))
          THROW(StorageException, "Beam direction type unknown: " << itsPS.settings.anaBeam.direction.type);


      // ScSupp fills Observation.Beam[x].target, sometimes with field codes, sometimes with pointing names.
      // Use it here to write FIELD CODE.
      casacore::String ctarget(itsPS.settings.SAPs[subarray].target);

      // Put the direction into the FIELD subtable.
      MSLofarField msfield = itsMS->field();
      MSLofarFieldColumns msfieldCol(msfield);

      uInt rownr = msfield.nrow();

      // Set refframe for MS direction columns to be able to write non-J2000 refframe coords.
      ASSERT(rownr == 0); // can only set directionType on first row, so only one field per MeasurementSet for now
      if (itsPS.settings.anaBeam.enabled)
        msfieldCol.setDirectionRef(beamDirectionType, anaBeamDirectionType);
      else
        msfieldCol.setDirectionRef(beamDirectionType);

      msfield.addRow();
      msfieldCol.name().put(rownr, "BEAM_" + String::toString(subarray));
      msfieldCol.code().put(rownr, ctarget);
      msfieldCol.time().put(rownr, itsStartTime);
      msfieldCol.numPoly().put(rownr, 0);

      msfieldCol.delayDirMeasCol().put(rownr, outdir);
      msfieldCol.phaseDirMeasCol().put(rownr, outdir);
      msfieldCol.referenceDirMeasCol().put(rownr, outdir);

      msfieldCol.sourceId().put(rownr, -1);
      msfieldCol.flagRow().put(rownr, False);

      if (itsPS.settings.anaBeam.enabled) {
        // Analog beam direction
        MVDirection radec_AnaBeamDirection(Quantity(itsPS.settings.anaBeam.direction.angle1, "rad"),
                                           Quantity(itsPS.settings.anaBeam.direction.angle2, "rad"));
        MDirection anaBeamDirection(radec_AnaBeamDirection, anaBeamDirectionType);
        msfieldCol.tileBeamDirMeasCol().put(rownr, anaBeamDirection);
      } else {
        msfieldCol.tileBeamDirMeasCol().put(rownr, outdir(0));
      }
    }


    void MeasurementSetFormat::fillPola()
    {
      const unsigned npolarizations = itsPS.settings.nrCrossPolarisations();

      MSPolarization mspol = itsMS->polarization();
      MSPolarizationColumns mspolCol(mspol);
      uInt rownr = mspol.nrow();
      casacore::Vector<Int> corrType(npolarizations);
      corrType(0) = Stokes::XX;

      if (npolarizations == 2) {
        corrType(1) = Stokes::YY;
      } else if (npolarizations == 4) {
        corrType(1) = Stokes::XY;
        corrType(2) = Stokes::YX;
        corrType(3) = Stokes::YY;
      }

      casacore::Matrix<Int> corrProduct(2, npolarizations);

      for (unsigned i = 0; i < npolarizations; i++) {
        corrProduct(0,i) = Stokes::receptor1(Stokes::type(corrType(i)));
        corrProduct(1,i) = Stokes::receptor2(Stokes::type(corrType(i)));
      }

      // Fill the columns.
      mspol.addRow();
      mspolCol.numCorr().put(rownr, npolarizations);
      mspolCol.corrType().put(rownr, corrType);
      mspolCol.corrProduct().put(rownr, corrProduct);
      mspolCol.flagRow().put(rownr, False);
      mspol.flush();
    }


    void MeasurementSetFormat::fillDataDesc()
    {
      MSDataDescription msdd = itsMS->dataDescription();
      MSDataDescColumns msddCol(msdd);

      msdd.addRow();

      msddCol.spectralWindowId().put(0, 0);
      msddCol.polarizationId().put(0, 0);
      msddCol.flagRow().put(0, False);

      msdd.flush();
    }


    void MeasurementSetFormat::fillObs(unsigned subarray)
    {
      // Get start and end time.
      casacore::Vector<Double> timeRange(2);
      timeRange[0] = itsStartTime;
      timeRange[1] = itsStartTime + itsNrTimes * itsTimeStep;

      // Get minimum and maximum frequency.
      vector<double> freqs(itsPS.settings.subbands.size());
      for(size_t sb = 0; sb < itsPS.settings.subbands.size(); ++sb)
         freqs[sb] = itsPS.settings.subbands[sb].centralFrequency;

      ASSERT( freqs.size() > 0 );

      double minFreq = *std::min_element( freqs.begin(), freqs.end() );
      double maxFreq = *std::max_element( freqs.begin(), freqs.end() );

      const size_t nchan = itsPS.settings.correlator.nrChannels;

      if( nchan > 1 ) {
        // 2nd PPF shifts frequencies downwards by half a channel
        const double width = itsPS.settings.correlator.channelWidth;

        minFreq -= 0.5 * nchan * width;
        maxFreq -= 0.5 * nchan * width;
      }

      casacore::Vector<String> corrSchedule(1);
      corrSchedule = "corrSchedule";

      vector<string> targets(itsPS.getStringVector
                               ("Observation.Beam[" + String::toString(subarray) + "].target", vector<string>(), true));
      casacore::Vector<String> ctargets(targets.size());

      for (uint i = 0; i < targets.size(); ++i)
        ctargets[i] = targets[i];

      vector<string> cois(itsPS.getStringVector("Observation.Campaign.CO_I", vector<string>(), true));
      casacore::Vector<String> ccois(cois.size());

      for (uint i = 0; i < cois.size(); ++i)
        ccois[i] = cois[i];

      double releaseDate = timeRange(1) + 365.25 * 24 * 60 * 60;

      MSLofarObservation msobs = itsMS->observation();
      MSLofarObservationColumns msobsCol(msobs);

      msobs.addRow();

      msobsCol.telescopeName().put(0, "LOFAR");
      msobsCol.timeRange().put(0, timeRange);
      msobsCol.observer().put(0, "unknown");
      msobsCol.scheduleType().put(0, "LOFAR");
      msobsCol.schedule().put(0, corrSchedule);
      msobsCol.project().put(0, itsPS.getString("Observation.Campaign.name", ""));
      msobsCol.releaseDate().put(0, releaseDate);
      msobsCol.flagRow().put(0, False);
      msobsCol.projectTitle().put(0, itsPS.getString("Observation.Campaign.title", ""));
      msobsCol.projectPI().put(0,  itsPS.getString("Observation.Campaign.PI", ""));
      msobsCol.projectCoI().put(0, ccois);
      msobsCol.projectContact().put(0, itsPS.getString("Observation.Campaign.contact", ""));
      msobsCol.observationId().put(0, String::toString(itsPS.settings.observationID));
      msobsCol.observationStart().put(0, timeRange[0]);
      msobsCol.observationEnd().put(0, timeRange[1]);
      msobsCol.observationFrequencyMaxQuant().put(0, Quantity(maxFreq, "Hz"));
      msobsCol.observationFrequencyMinQuant().put(0, Quantity(minFreq, "Hz"));
      msobsCol.observationFrequencyCenterQuant().put(0, Quantity(0.5 * (minFreq + maxFreq), "Hz"));
      msobsCol.subArrayPointing().put(0, subarray);
      msobsCol.nofBitsPerSample().put(0, itsPS.nrBitsPerSample());
      msobsCol.antennaSet().put(0, itsPS.settings.antennaSet);
      msobsCol.filterSelection().put(0, itsPS.settings.bandFilter);
      msobsCol.clockFrequencyQuant().put(0, Quantity(itsPS.settings.clockHz(), "Hz"));
      msobsCol.target().put(0, ctargets);
      msobsCol.systemVersion().put(0, Version::getInfo<OutputProcVersion>("OutputProc",
                                                                          "brief"));
      msobsCol.pipelineName().put(0, String());
      msobsCol.pipelineVersion().put(0, String());
      msobsCol.filename().put(0, Path(itsMS->tableName()).baseName());
      msobsCol.filetype().put(0, "uv");
      msobsCol.filedate().put(0, timeRange[0]);

      msobs.flush();
    }

    void MeasurementSetFormat::fillSpecWindow(unsigned subband)
    {
      const double refFreq = itsPS.settings.subbands[subband].centralFrequency;
      const size_t nchan = itsPS.settings.correlator.nrChannels;
      const double chanWidth = itsPS.settings.correlator.channelWidth;
      const double totalBW = nchan * chanWidth;
      const double channel0freq = itsPS.channel0Frequency(subband, nchan);

      casacore::Vector<double> chanWidths(nchan, chanWidth);
      casacore::Vector<double> chanFreqs(nchan);
      indgen (chanFreqs, channel0freq, chanWidth);

      MSSpectralWindow msspw = itsMS->spectralWindow();
      MSSpWindowColumns msspwCol(msspw);

      msspw.addRow();

      msspwCol.numChan().put(0, nchan);
      msspwCol.name().put(0, "SB-" + String::toString(subband));
      msspwCol.refFrequency().put(0, refFreq);
      msspwCol.chanFreq().put(0, chanFreqs);

      msspwCol.chanWidth().put(0, chanWidths);
      msspwCol.measFreqRef().put(0, MFrequency::TOPO);
      msspwCol.effectiveBW().put(0, chanWidths);
      msspwCol.resolution().put(0, chanWidths);
      msspwCol.totalBandwidth().put(0, totalBW);
      msspwCol.netSideband().put(0, 0);
      msspwCol.ifConvChain().put(0, 0);
      msspwCol.freqGroup().put(0, 0);
      msspwCol.freqGroupName().put(0, "");
      msspwCol.flagRow().put(0, False);

      // Remove a few keywords from the MEASINFO, because old CASA cannot
      // deal with them since Dirk Petry added type Undefined.
      MSLofar::removeMeasKeys (msspw, "REF_FREQUENCY");
      MSLofar::removeMeasKeys (msspw, "CHAN_FREQ");

      msspw.flush();
    }


    void MeasurementSetFormat::fillHistory()
    {
      Table histtab(itsMS->keywordSet().asTable("HISTORY"));
      histtab.reopenRW();
      ScalarColumn<double> time        (histtab, "TIME");
      ScalarColumn<int>    obsId       (histtab, "OBSERVATION_ID");
      ScalarColumn<String> message     (histtab, "MESSAGE");
      ScalarColumn<String> application (histtab, "APPLICATION");
      ScalarColumn<String> priority    (histtab, "PRIORITY");
      ScalarColumn<String> origin      (histtab, "ORIGIN");
      ArrayColumn<String>  parms       (histtab, "APP_PARAMS");
      ArrayColumn<String>  cli         (histtab, "CLI_COMMAND");

      // Put all parset entries in a Vector<String>.
      casacore::Vector<String> appvec;
      casacore::Vector<String> clivec;
      appvec.resize (itsPS.size());
      casacore::Array<String>::contiter viter = appvec.cbegin();
      for (ParameterSet::const_iterator iter = itsPS.begin(); iter != itsPS.end(); ++iter, ++viter) {
        *viter = iter->first + '=' + iter->second.get();
      }
      uint rownr = histtab.nrow();
      histtab.addRow();
      time.put        (rownr, Time().modifiedJulianDay() * 24. * 3600.);
      obsId.put       (rownr, 0);
      message.put     (rownr, "parameters");
      application.put (rownr, "COBALT2");
      priority.put    (rownr, "NORMAL");
      origin.put      (rownr, Version::getInfo<OutputProcVersion>("OutputProc", "full"));
      parms.put       (rownr, appvec);
      cli.put         (rownr, clivec);
    }

    void MeasurementSetFormat::fillProcessor()
    {
      MSProcessor msproc = itsMS->processor();
      MSProcessorColumns msprocCol(msproc);
      // Fill the columns
      msproc.addRow();
      msprocCol.type().put (0, "CORRELATOR");
      msprocCol.subType().put (0, "LOFAR-COBALT2");
      msprocCol.typeId().put (0, -1);
      msprocCol.modeId().put (0, -1);
      msprocCol.flagRow().put (0, False);
      msproc.flush();
    }

    void MeasurementSetFormat::fillState()
    {
      MSState msstate = itsMS->state();
      MSStateColumns msstateCol(msstate);
      // Fill the columns
      msstate.addRow();
      msstateCol.sig().put (0, True);
      msstateCol.ref().put (0, False);
      msstateCol.cal().put (0, 0.);
      msstateCol.load().put (0, 0.);
      msstateCol.subScan().put (0, 0);
      msstateCol.obsMode().put (0, "");
      msstateCol.flagRow().put (0, False);
      msstate.flush();
    }

    void MeasurementSetFormat::fillPointing(unsigned subarray)
    {
      // Beam direction
      MVDirection radec(Quantity(itsPS.settings.SAPs[subarray].direction.angle1, "rad"),
                        Quantity(itsPS.settings.SAPs[subarray].direction.angle2, "rad"));
      MDirection::Types beamDirectionType;
      if (!MDirection::getType(beamDirectionType, itsPS.settings.SAPs[subarray].direction.type))
        THROW(StorageException, "Beam direction type unknown: " << itsPS.settings.SAPs[subarray].direction.type);
      MDirection indir(radec, beamDirectionType);

      casacore::Vector<MDirection> outdir(1);
      outdir(0) = indir;

      // ScSupp fills Observation.Beam[x].target, sometimes with field codes, sometimes with pointing names.
      // Use it here to write POINTING NAME.
      casacore::String ctarget(itsPS.settings.SAPs[subarray].target);

      // Fill the POINTING subtable.
      MSPointing mspointing = itsMS->pointing();
      MSPointingColumns mspointingCol(mspointing);

      uInt rownr = mspointing.nrow();
      // Set refframe for MS direction columns to be able to write non-J2000 refframe coords.
      ASSERT(rownr == 0); // can only set directionType on first row, so only one field per MeasurementSet for now
      mspointingCol.setDirectionRef(beamDirectionType);

      mspointing.addRow(itsNrAnt);
      for (unsigned i = 0; i < itsNrAnt; i++) {
        mspointingCol.antennaId().put(i, i);
        mspointingCol.time().put(i, itsStartTime + itsNrTimes * itsTimeStep / 2.);
        mspointingCol.interval().put(i, itsNrTimes * itsTimeStep);
        mspointingCol.name().put(i, ctarget);
        mspointingCol.numPoly().put(i, 0);
        mspointingCol.timeOrigin().put(i, itsStartTime);
        mspointingCol.directionMeasCol().put(i, outdir);
        mspointingCol.targetMeasCol().put(i, outdir);
        mspointingCol.tracking().put(i, true); // not tracking N/A w/ current obs software
      }

      mspointing.flush();
    }


    void MeasurementSetFormat::createMSMetaFile(const string &MSname, unsigned subband)
    {
      (void) subband;

      Block<Int> ant1(itsPS.nrBaselines());
      Block<Int> ant2(itsPS.nrBaselines());
      uInt inx = 0;
      uInt nStations = itsPS.nrTabStations() > 0 ? itsPS.nrTabStations() : itsPS.settings.antennaFields.size();

      for (uInt i = 0; i < nStations; ++i) {
        for (uInt j = 0; j <= i; ++j) {
          if (LofarStManVersion == 2) {
            // switch order of stations to fix write of complex conjugate data in V1
            ant1[inx] = i;
            ant2[inx] = j;
            ++inx;
          } else {
            ant1[inx] = j;
            ant2[inx] = i;
            ++inx;
          }
        }
      }

      string filename = MSname + "/table.f0meta";

      AipsIO aio(filename, ByteIO::New);
      aio.putstart("LofarStMan", LofarStManVersion);
      aio << ant1 << ant2
          << itsStartTime
          << itsPS.settings.correlator.integrationTime()
          << itsPS.settings.correlator.nrChannels
          << itsPS.settings.nrCrossPolarisations()
          << static_cast<double>(itsPS.settings.correlator.nrSamplesPerIntegration())
          << itsAlignment
          << false; // isBigEndian
      if (LofarStManVersion > 1) {
        const size_t integrationSteps = itsPS.settings.correlator.nrSamplesPerIntegration();
        const uInt itsNrBytesPerNrValidSamples =
          integrationSteps < 256 ? 1 :
          integrationSteps < 65536 ? 2 :
          4;
        aio << itsNrBytesPerNrValidSamples;
      }
      aio.close();
    }


  } // namespace Cobalt
} // namespace LOFAR

