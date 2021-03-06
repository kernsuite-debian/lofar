//#  Cache.cc: implementation of the Cache class
//#
//#  Copyright (C) 2002-2004
//#  ASTRON (Netherlands Foundation for Research in Astronomy)
//#  P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, softwaresupport@astron.nl
//#
//#  This program is free software; you can redistribute it and/or modify
//#  it under the terms of the GNU General Public License as published by
//#  the Free Software Foundation; either version 2 of the License, or
//#  (at your option) any later version.
//#
//#  This program is distributed in the hope that it will be useful,
//#  but WITHOUT ANY WARRANTY; without even the implied warranty of
//#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//#  GNU General Public License for more details.
//#
//#  You should have received a copy of the GNU General Public License
//#  along with this program; if not, write to the Free Software
//#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//#
//#  $Id$

#include <lofar_config.h>
#include <Common/LofarLogger.h>
#include <Common/LofarConstants.h>
#include <Common/LofarLocators.h>
#include <Common/lofar_bitset.h>
#include <Common/LofarBitModeInfo.h>

#include "StationSettings.h"
#include "Cache.h"
#include "Sequencer.h"

#include <APL/RTCCommon/PSAccess.h>

#include <blitz/array.h>
#include <fstream>

using namespace blitz;
using namespace LOFAR;
using namespace RSP;
using namespace RSP_Protocol;
using namespace RTC;

#define MAX_RCU_MODE 7

// default settings
// sdo_ss=295:330,331:366,367:402,403:438
blitz::Array<uint16, 2> str2blitz(const char* str, int max)
{
    string inputstring(str);
    char* start  = (char*)inputstring.c_str();
    char* end  = 0;
    bool  range  = false;
    long  prevval = 0;

    blitz::Array<uint16, 2> ss(4,36); // ss = subband select
    int bank_nr = 0;
    int sb_nr = 0;
    long i;

    ss = 0;
    while (start) {
        long val = strtol(start, &end, 10); // read decimal numbers
        start = (end ? (*end ? end + 1 : 0) : 0); // advance
        if (val >= max || val < 0) {
            LOG_WARN(formatString("Error: value %d out of range",val));
            ss = 0;
            return ss;
        }
        LOG_INFO_STR("val=" << val << "  prevval=" << prevval);
        if (end) {
            switch (*end) {
                case ',':
                case 0: {
                    if (range) {
                        if (0 == prevval && 0 == val) {
                            val = max - 1;
                        }
                        if (val < prevval) {
                            LOG_WARN("Error: invalid range specification");
                            ss = 0;
                            return ss;
                        }

                        for (i = prevval; i <= val; i++) {
                            //LOG_INFO(formatString("add value %d to ss(%d,%d)", i, bank_nr, sb_nr));
                            ss(bank_nr, sb_nr) = (uint16)i;
                            sb_nr++;
                            if (sb_nr >= 36) {
                                bank_nr++;
                                sb_nr = 0;
                            }
                        }
                    }
                    else {
                        ss(bank_nr, sb_nr) = (uint16)val;
                        sb_nr++;
                        if (sb_nr >= 36) {
                            bank_nr++;
                            sb_nr = 0;
                        }
                    }
                    range=false;
                } break;

                case ':': {
                    range=true;
                } break;

                default: {
                    LOG_WARN(formatString("Error: invalid character %c",*end));
                    ss = 0;
                    return ss;
                } break;
            } // switch
        } // if (end)
        prevval = val;
    } // while

    return (ss);
}


/**
 * Instance pointer for the Cache singleton class.
 */
Cache* Cache::m_instance = 0;

/**
 * CacheBuffer implementation
 */

CacheBuffer::CacheBuffer(Cache* cache) : m_cache(cache)
{
  // When the sample frequency (m_clock) is modified the RSP
  // board goes through a reset. For this reason we reset all
  // values in the cacht to default (using Cache::reset), but
  // the value of m_clock should not be reset. For that reason
  // it is initialized here separately outside reset().
  m_clock = GET_CONFIG("RSPDriver.DEFAULT_SAMPLING_FREQUENCY", i);

  reset(); // reset by allocating memory and settings default values

  // print sizes of the cache
  LOG_DEBUG_STR("m_beamletweights().size()            =" << m_beamletweights().size()     * sizeof(complex<int16>));
  LOG_DEBUG_STR("m_subbandselection.crosslets().size()=" << m_subbandselection.crosslets().size()   * sizeof(uint16));
  LOG_DEBUG_STR("m_subbandselection.beamlets().size() =" << m_subbandselection.beamlets().size()   * sizeof(uint16));
  LOG_DEBUG_STR("m_rcusettings().size()               =" << m_rcusettings().size()        * sizeof(uint8));
  LOG_DEBUG_STR("m_hbasettings().size()               =" << m_hbasettings().size()        * sizeof(uint8));
  LOG_DEBUG_STR("m_hbareadings().size()               =" << m_hbareadings().size()        * sizeof(uint8));
  LOG_DEBUG_STR("m_rsusettings().size()               =" << m_rsusettings().size()        * sizeof(uint8));
  LOG_DEBUG_STR("m_wgsettings().size()                =" << m_wgsettings().size()         * sizeof(WGSettings::WGRegisterType));
  LOG_DEBUG_STR("m_subbandstats().size()              =" << m_subbandstats().size()       * sizeof(uint16));
  LOG_DEBUG_STR("m_beamletstats().size()              =" << m_beamletstats().size()       * sizeof(double));
  LOG_DEBUG_STR("m_xcstats().size()                   =" << m_xcstats().size()            * sizeof(complex<double>));
  LOG_DEBUG_STR("m_systemstatus.board().size()        =" << m_systemstatus.board().size() * sizeof(EPA_Protocol::BoardStatus));
  LOG_DEBUG_STR("m_versions.bp().size()               =" << m_versions.bp().size()        * sizeof(EPA_Protocol::RSRVersion));
  LOG_DEBUG_STR("m_versions.ap().size()               =" << m_versions.ap().size()        * sizeof(EPA_Protocol::RSRVersion));
  LOG_DEBUG_STR("m_tdstatus.board().size()            =" << m_tdstatus.board().size()     * sizeof(EPA_Protocol::TDBoardStatus));
  LOG_DEBUG_STR("m_spustatus.subrack().size()         =" << m_spustatus.subrack().size()  * sizeof(EPA_Protocol::SPUBoardStatus));
  LOG_DEBUG_STR("m_tbbsettings().size()               =" << m_tbbsettings().size()        * sizeof(bitset<MEPHeader::N_SUBBANDS>));
  LOG_DEBUG_STR("m_bypasssettings().size()            =" << m_bypasssettings().size()     * sizeof(EPA_Protocol::DIAGBypass));
  LOG_DEBUG_STR("m_bypasssettings_bp().size()         =" << m_bypasssettings_bp().size()  * sizeof(EPA_Protocol::DIAGBypass));
  LOG_DEBUG_STR("m_rawDataBlock.size()                =" << ETH_DATA_LEN + sizeof (uint16));
  LOG_DEBUG_STR("m_SdsWriteBuffer.size()              =" << sizeof(itsSdsWriteBuffer));
  LOG_DEBUG_STR("m_SdsReadBuffer.size()               =" << sizeof(itsSdsReadBuffer));
  LOG_DEBUG_STR("m_latencys.size()                    =" << itsLatencys().size()          * sizeof(EPA_Protocol::RADLatency));
  LOG_DEBUG_STR("itsSwappedXY.size()                  =" << itsSwappedXY.size());
  LOG_DEBUG_STR("itsBitModeInfo.size()                =" << itsBitModeInfo().size()       * sizeof(EPA_Protocol::RSRBeamMode));
  LOG_DEBUG_STR("itsBitsPerSample.size()              =" << sizeof(itsBitsPerSample));
  LOG_DEBUG_STR("itsSDOModeInfo.size()                =" << itsSDOModeInfo().size()       * sizeof(EPA_Protocol::RSRSDOMode));
  LOG_DEBUG_STR("itsSDOSelection.size()               =" << itsSDOSelection.subbands().size() * sizeof(uint16));
  LOG_DEBUG_STR("itsSDOBitsPerSample.size()           =" << sizeof(itsSDOBitsPerSample));
  LOG_DEBUG_STR("itsPPSsyncDelays.size()              =" << sizeof(itsPPSsyncDelays));
  LOG_DEBUG_STR("itsFixedAttenuations.size()          =" << sizeof(itsFixedAttenuations));
  LOG_DEBUG_STR("itsAttenuationStepSize.size()        =" << sizeof(itsAttenuationStepSize));
  LOG_INFO_STR(formatString("CacheBuffer size = %d bytes",
	         m_beamletweights().size()
	       + m_subbandselection.crosslets().size()
	       + m_subbandselection.beamlets().size()
	       + m_rcusettings().size()
	       + m_hbasettings().size()
	       + m_hbareadings().size()
	       + m_rsusettings().size()
	       + m_wgsettings().size()
	       + m_subbandstats().size()
	       + m_beamletstats().size()
	       + m_xcstats().size()
	       + m_systemstatus.board().size()
	       + m_versions.bp().size()
	       + m_versions.ap().size()
	       + m_tdstatus.board().size()
	       + m_spustatus.subrack().size()
	       + m_tbbsettings().size()
	       + m_bypasssettings().size()
	       + m_bypasssettings_bp().size()
		   + ETH_DATA_LEN + sizeof(uint16)
		   + sizeof(itsSdsWriteBuffer)
		   + sizeof(itsSdsReadBuffer)
		   + itsLatencys().size()
           + itsSwappedXY.size()
           + itsBitModeInfo().size()
           + sizeof(itsBitsPerSample)
           + itsSDOModeInfo().size()
           + itsSDOSelection.subbands().size()
           + sizeof(itsBitsPerSample)
           + sizeof(itsPPSsyncDelays)
           + sizeof(itsFixedAttenuations)
           + sizeof(itsAttenuationStepSize)));
}

CacheBuffer::~CacheBuffer()
{
  m_beamletweights().free();
  m_subbandselection.crosslets().free();
  m_subbandselection.beamlets().free();
  m_rcusettings().free();
  m_hbasettings().free();
  m_hbareadings().free();
  m_rsusettings().free();
  m_wgsettings().free();
  m_wgsettings.waveforms().free();
  m_subbandstats().free();
  m_beamletstats().free();
  m_xcstats().free();
  m_systemstatus.board().free();
  m_versions.bp().free();
  m_versions.ap().free();
  m_tdstatus.board().free();
  m_spustatus.subrack().free();
  m_tbbsettings().free();
  m_bypasssettings().free();
  m_bypasssettings_bp().free();
  itsLatencys().free();
  itsBitModeInfo().free();
  itsSDOModeInfo().free();
  itsSDOSelection.subbands().free();
}

void CacheBuffer::reset(void)
{
	//
	// Initialize cache, allocating memory and setting default values
	//
	struct timeval tv;
	tv.tv_sec = 0; tv.tv_usec = 0;
	m_timestamp.set(tv);

    itsBitsPerSample = MAX_BITS_PER_SAMPLE;
    itsSDOBitsPerSample = MAX_BITS_PER_SAMPLE;

	m_beamletweights().resize( BeamletWeights::SINGLE_TIMESTEP,
	                           StationSettings::instance()->nrRcus(),
	                           MAX_NR_BM_BANKS,
	                           MEPHeader::N_BEAMLETS);
	m_beamletweights() = complex<int16>(25,36);
// TODO remove this code!!!
	for (int rcu = 0 ; rcu < StationSettings::instance()->nrRcus(); rcu++) {
		int16	value=0;
		for (int bank = 0; bank < (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE); bank++) {
			for (int beamlet = 0; beamlet < MEPHeader::N_BEAMLETS; beamlet++) {
				m_beamletweights()(0,rcu,bank,beamlet)=complex<int16>(value++,bank+10);
			}
		}
	}
//TODO

	m_subbandselection.crosslets().resize(StationSettings::instance()->nrRcus(),
	                                      (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE),
	                                      MEPHeader::N_LOCAL_XLETS );
	m_subbandselection.crosslets() = 0;
    m_subbandselection.beamlets().resize(StationSettings::instance()->nrRcus(),
                                         (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE),
                                         MEPHeader::N_BEAMLETS );
	m_subbandselection.beamlets() = 0;

	if (GET_CONFIG("RSPDriver.IDENTITY_WEIGHTS", i)) {
		// these weights ensure that the beamlet statistics
		// exactly match the subband statistics
		m_beamletweights() = complex<int16>(GET_CONFIG("RSPDriver.BF_GAIN", i), 0);

		//
		// Set default subband selection starting at RSPDriver.FIRST_SUBBAND
		//
		int		firstSubband = GET_CONFIG("RSPDriver.FIRST_SUBBAND", i);
		for (int rcu = 0; rcu < m_subbandselection.beamlets().extent(firstDim); rcu++) {
    		for (int bank = 0; bank < (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE); bank++) {
    			for (int lane = 0; lane < MEPHeader::N_SERDES_LANES; lane++) {
    				int	start(lane*(MEPHeader::N_BEAMLETS/MEPHeader::N_SERDES_LANES));
    				int stop (start + maxBeamletsPerRSP(itsBitsPerSample));
    				if (rcu==0) LOG_DEBUG_STR("start=" << start << ", stop=" << stop);
    				for (int sb = start; sb < stop; sb++) {
    					m_subbandselection.beamlets()(rcu, bank, sb) = (rcu%N_POL) + (sb*N_POL) + (firstSubband*2);
    				} // for sb
    			} // for lane
    		} // for bank
		} // for rcu
		LOG_DEBUG_STR("m_subbandsel(0): " << m_subbandselection.beamlets()(0, Range::all(), Range::all()));
	} // if identity_weights

	// initialize RCU settings
	m_rcusettings().resize(StationSettings::instance()->nrRcus());

	RCUSettings::Control rcumode;
	rcumode.setMode(RCUSettings::Control::MODE_OFF);
	m_rcusettings() = rcumode;

	// initialize HBA settings
	m_hbasettings().resize(StationSettings::instance()->nrRcus(), N_HBA_ELEM_PER_TILE);
	m_hbasettings() = 0; // initialize to 0
	m_hbareadings().resize(StationSettings::instance()->nrRcus(), N_HBA_ELEM_PER_TILE);
	m_hbareadings() = 0; // initialize to 0

	// RSU settings
	m_rsusettings().resize(StationSettings::instance()->nrRspBoards());
	RSUSettings::ResetControl 	rsumode;
	rsumode.setRaw(RSUSettings::ResetControl::CTRL_OFF);
	m_rsusettings() = rsumode;

	m_wgsettings().resize(StationSettings::instance()->nrRcus());
	WGSettings::WGRegisterType init;
	init.freq        = 0;
	init.phase       = 0;
	init.ampl        = 0;
	init.nof_samples = 0;
	init.mode = WGSettings::MODE_OFF;
	init.preset = WGSettings::PRESET_SINE;
	m_wgsettings() = init;

	m_wgsettings.waveforms().resize(StationSettings::instance()->nrRcus(), MEPHeader::N_WAVE_SAMPLES);
	m_wgsettings.waveforms() = 0;

	m_subbandstats().resize(StationSettings::instance()->nrRcus(), MEPHeader::N_SUBBANDS);
	m_subbandstats() = 0;

    // Number of cep streams -> in normal mode 4, in splitmode 8.
    int maxStreams = 8;
	m_beamletstats().resize((maxStreams/MEPHeader::N_SERDES_LANES) * N_POL,
	                        (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE) * MEPHeader::N_BEAMLETS);
	m_beamletstats() = 0;

	m_xcstats().resize(N_POL, N_POL, StationSettings::instance()->nrBlps(), StationSettings::instance()->nrBlps());
	m_xcstats() = complex<double>(0,0);

	// BoardStatus
	m_systemstatus.board().resize(StationSettings::instance()->nrRspBoards());
	BoardStatus boardinit;
	memset(&boardinit, 0, sizeof(BoardStatus));
	m_systemstatus.board() = boardinit;

	EPA_Protocol::RSRVersion versioninit = { { 0 }, 0, 0 };
	m_versions.bp().resize(StationSettings::instance()->nrRspBoards());
	m_versions.bp() = versioninit;
	m_versions.ap().resize(StationSettings::instance()->nrBlps());
	m_versions.ap() = versioninit;

	// TDBoardStatus
	m_tdstatus.board().resize(StationSettings::instance()->nrRspBoards());
	TDBoardStatus tdstatusinit;
	memset(&tdstatusinit, 0, sizeof(TDBoardStatus));
	tdstatusinit.unknown = 1;
	m_tdstatus.board() = tdstatusinit;

	// SPUBoardStatus
	int	nrSubRacks = StationSettings::instance()->maxRspBoards()/NR_RSPBOARDS_PER_SUBRACK;
	nrSubRacks += (StationSettings::instance()->maxRspBoards() % NR_RSPBOARDS_PER_SUBRACK == 0) ? 0 : 1;
	m_spustatus.subrack().resize(nrSubRacks);
	LOG_INFO_STR("Resizing SPU array to " << m_spustatus.subrack().size());
	SPUBoardStatus spustatusinit;
	memset(&spustatusinit, 0, sizeof(SPUBoardStatus));
	m_spustatus.subrack() = spustatusinit;

	// TBBSettings
	m_tbbsettings().resize(StationSettings::instance()->nrRcus());
	bitset<MEPHeader::N_SUBBANDS> bandsel;
	bandsel = 0;
	m_tbbsettings() = bandsel;

	// BypassSettings (AP's)
	LOG_INFO_STR("Resizing bypass array to: " << StationSettings::instance()->nrBlps());
    m_bypasssettings().resize(StationSettings::instance()->nrBlps());
	BypassSettings::Control	control;
	m_bypasssettings() = control;

    // BypassSettings (BP)
	LOG_INFO_STR("Resizing bypass array to: " << StationSettings::instance()->maxRspBoards());
    m_bypasssettings_bp().resize(StationSettings::instance()->maxRspBoards());
	BypassSettings::Control	controlbp;
    controlbp.setSDO(1);
	m_bypasssettings_bp() = controlbp;

	// clear rawdatablock
	itsRawDataBlock.address = 0;
	itsRawDataBlock.offset  = 0;
	itsRawDataBlock.dataLen = 0;
	memset(itsRawDataBlock.data, 0, RSP_RAW_BLOCK_SIZE);

	// clear SerdesBuffer
	itsSdsWriteBuffer.clear();
	for (int rsp = 0; rsp < MAX_N_RSPBOARDS; rsp++) {
		itsSdsReadBuffer[rsp].clear();
	}

	// clear I2C flag
	itsI2Cuser = NONE;

	// set Splitter not active
	itsSplitterActive = false;
	// set CEP port enabled
	itsCepEnabled0 = false;
	itsCepEnabled1 = false;

	// Latency status
	itsLatencys().resize(StationSettings::instance()->nrRspBoards());
	RADLatency radlatencyinit;
	memset(&radlatencyinit, 0, sizeof(RADLatency));
	itsLatencys() = radlatencyinit;
	itsSwappedXY.reset();

	// BitMode
	itsBitModeInfo().resize(StationSettings::instance()->nrRspBoards());
	RSRBeamMode bitmodeinfo;
	bitmodeinfo.bm_select = 0;
	bitmodeinfo.bm_max = 0;
	itsBitModeInfo() = bitmodeinfo;

    // SDO default Mode selection
    int sdo_mode = 0;
    int bits_per_sample = GET_CONFIG("RSPDriver.SDO_MODE", i);
    if      (bits_per_sample == 8) { sdo_mode = 1; }
    else if (bits_per_sample == 5) { sdo_mode = 2; }
    else if (bits_per_sample == 4) { sdo_mode = 3; }

	itsSDOModeInfo().resize(StationSettings::instance()->nrRspBoards());
	RSRSDOMode sdomodeinfo;
	sdomodeinfo.bm_select = sdo_mode;
	sdomodeinfo.bm_max = 3;
	itsSDOModeInfo() = sdomodeinfo;

    // SDO default subband selection
    itsSDOSelection.subbands().resize(StationSettings::instance()->nrRcus(),
                                     (MAX_BITS_PER_SAMPLE/MIN_BITS_PER_SAMPLE),
                                      MEPHeader::N_SDO_SUBBANDS);
    char select_str[64];
    blitz::Array<uint16, 2> select(4,36);
    strncpy(select_str, GET_CONFIG_STRING("RSPDriver.SDO_SS"), 64);
    select = str2blitz(select_str, 512);
    for (int rcu = 0; rcu < StationSettings::instance()->nrRcus(); rcu++) {
        for (int bank = 0; bank < (MAX_BITS_PER_SAMPLE / MIN_BITS_PER_SAMPLE); bank++) {
            itsSDOSelection.subbands()(rcu, bank, Range::all()) = 0;
            for (int sb = 0; sb < 36; sb++) {
                itsSDOSelection.subbands()(rcu, bank, sb) = (select(bank, sb) * 2) + (rcu % 2);
            } // for each subband
        } // for each bank
    }
    readPPSdelaySettings();

    itsAttenuationStepSize = 0.25;
    try { itsAttenuationStepSize = GET_CONFIG("RSPDriver.ATT_STEP_SIZE", f); }
	catch (APSException&) { LOG_INFO_STR("RSPDriver.ATT_STEP_SIZE not found"); }
    char key[40];
    itsFixedAttenuations.resize(MAX_RCU_MODE + 1);
    itsFixedAttenuations = 0.0;
    for (int rcumode = 1; rcumode <= MAX_RCU_MODE; rcumode++) {
        snprintf(key,  40, "RSPDriver.FIXED_ATT_MODE_%d", rcumode);
        itsFixedAttenuations(rcumode) = 0.0;
        try { itsFixedAttenuations(rcumode) = GET_CONFIG(key, f); }
        catch (APSException&) { LOG_INFO_STR(formatString("RSPDriver.FIXED_ATT_MODE_%d not found", rcumode)); }
    }
}


SerdesBuffer&	CacheBuffer::getSdsReadBuffer(int	rspBoardNr)
{
	ASSERTSTR(rspBoardNr >= 0 && rspBoardNr < MAX_N_RSPBOARDS,
				"RSPboard index out of range in getting serdesReadBuffer: " << rspBoardNr);
	return (itsSdsReadBuffer[rspBoardNr]);
}

void CacheBuffer::setTimestamp(const RTC::Timestamp& timestamp)
{
  m_timestamp = timestamp;
}

//
// readPPSdelaySettings()
//
void CacheBuffer::readPPSdelaySettings()
{
	if (m_clock == 0) {
        LOG_INFO_STR("Skip loading PPS delay settings, clock = 0 MHz");
        return;
    }
    ConfigLocator	CL;
    string	filename = (CL.locate(GET_CONFIG_STRING(formatString("RSPDriver.PPSdelayFile%u", (unsigned int)m_clock))));
	LOG_DEBUG_STR("Trying to load the PPS delay settings for " << m_clock << " MHz from file: " << filename);

	// setup default values first
	int	nrRspBoards = StationSettings::instance()->nrRspBoards();
    itsPPSsyncDelays.resize(nrRspBoards * NR_BLPS_PER_RSPBOARD);
    itsPPSsyncDelays = 0;

	ifstream	ppsFile;
	ppsFile.open(filename.c_str());
	if (!ppsFile.good()) {
		ppsFile.close();
		LOG_WARN_STR("File " << filename << " could not be opened, cannot synchronise PPS pulses");
		return;
	}

	// Skip comment lines
	string	line;
	getline(ppsFile, line);
	while (line != "" && ppsFile.peek() == '#') {
		getline(ppsFile, line);
	}

	// read values
	blitz::Array<int, 1> delayValues;
	ppsFile >> delayValues;
	ppsFile.close();

	// Check number if values read in
	if (delayValues.extent(firstDim) == nrRspBoards * NR_BLPS_PER_RSPBOARD) {
        itsPPSsyncDelays = delayValues;
	}
	else {
		LOG_ERROR_STR("File " << filename << " contains " << delayValues.extent(firstDim)
					  << " values, expected " << nrRspBoards * NR_BLPS_PER_RSPBOARD
					  << " values, WILL NOT USE THEM!");
	}
    std::ostringstream logStream;
    logStream << itsPPSsyncDelays(Range::all());
	LOG_INFO_STR(formatString("PPSsyncDelays=%s", logStream.str().c_str()));
}

//
// Cache implementation
//
Cache& Cache::getInstance()
{
	if (!m_instance) {
		m_instance = new Cache;
	}
	return (*m_instance);
}

Cache::Cache() : m_front(0), m_back(0)
{
	// initialize preset waveforms
	WGSettings::initWaveformPresets();

	m_front = new CacheBuffer(this); ASSERT(m_front);
	m_back = new CacheBuffer(this);  ASSERT(m_back);

	getState().init(StationSettings::instance()->nrRspBoards(),
					StationSettings::instance()->nrBlps(),
					StationSettings::instance()->nrRcus());

	// start by writing the correct clock setting
	Sequencer::getInstance().startSequence(Sequencer::SEQ_STARTUP);
}

Cache::~Cache()
{
	if (m_front) delete m_front;
	if (m_back) delete m_back;
}

void Cache::reset(void)
{
	m_front->reset();
	m_back->reset();
}

void Cache::swapBuffers()
{
	if (GET_CONFIG("RSPDriver.XC_FILL", i)) {
		// fill xcorr array by copying and taking complex conjugate of values mirrored in the diagonal
		Array<complex<double>, 4> xc(m_back->getXCStats()());
		firstIndex  i; secondIndex j; thirdIndex  k; fourthIndex  l;
		xc = where(xc(i,j,k,l)==complex<double>(0,0), conj(xc(j,i,l,k)), xc(i,j,k,l));
	}

	CacheBuffer *tmp = m_front;
	m_front = m_back;
	m_back  = tmp;
}

void Cache::resetI2Cuser()
{
	I2Cuser	busUser = NONE;
	if ((m_front->getI2Cuser() == HBA) && (!m_allstate.hbaprotocol().isMatchAll(RegisterState::CHECK))) {
		busUser = HBA;
	}
	else if ((m_front->getI2Cuser() == RCU_W) && (!m_allstate.rcuprotocol().isMatchAll(RegisterState::CHECK))) {
		busUser = RCU_W;
	}
	else if ((m_front->getI2Cuser() == RCU_R) && (!m_allstate.rcuread().isMatchAll(RegisterState::CHECK))) {
		busUser = RCU_R;
	}
	m_front->setI2Cuser(busUser);
	m_back->setI2Cuser (busUser);
	LOG_INFO_STR("new I2Cuser = " << ((busUser == NONE) ? "NONE" :
									 ((busUser == HBA) ? "HBA" :
									 ((busUser == RCU_R) ? "RCU_R" : "RCU_W"))));

}
