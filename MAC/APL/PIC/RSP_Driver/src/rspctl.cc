//#
//#  rspctl.cc: command line interface to the RSPDriver
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
//#

#include <lofar_config.h>
#include <Common/LofarLogger.h>
#include <Common/lofar_bitset.h>
#include <Common/hexdump.h>
#include <Common/Exception.h>

#include <MACIO/MACServiceInfo.h>
#include <GCF/TM/GCF_Scheduler.h>

#include <APL/RSP_Protocol/RSP_Protocol.ph>
#include <APL/RSP_Protocol/EPA_Protocol.ph>

#include <APL/RTCCommon/PSAccess.h>

#include <iostream>
#include <Common/lofar_sstream.h>
#include <sys/time.h>
#include <string.h>
#include <blitz/array.h>
#include <getopt.h>
#include <complex>

#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <set>

#include <netinet/in.h>

#include <APL/RTCCommon/gnuplot_i.h>

#include "rspctl.h"

#define xtod(c) ((c>='0' && c<='9') ? c-'0' : ((c>='A' && c<='F') ? \
								c-'A'+10 : ((c>='a' && c<='f') ? c-'a'+10 : 0)))

int rspctl_exit_code = EXIT_SUCCESS;

namespace LOFAR {
	using namespace RSP_Protocol;
	using namespace EPA_Protocol;
	using namespace GCF::TM;
	namespace rspctl {
	using namespace std;
	using namespace blitz;
	using namespace EPA_Protocol;
	using namespace RSP_Protocol;
//	using namespace RSP;
	using namespace RTC;

// Use a terminate handler that can produce a backtrace.
Exception::TerminateHandler t(Exception::terminate);

// declare class constants
double WGCommand::AMPLITUDE_SCALE = (1.0 * ((uint32)(1 << 11)-1) / (uint32)(1 << 11)) * (uint32)(1 << 31);

// local funtions
static void usage(bool);

// getting real or sent hba values
static bool realDelays = false;

// Constants
#define BITSOFBYTE 8


//
// Some handy macro's to iterate of RSP boards
//
#define BOARD_ITERATOR_BEGIN \
do { \
	int boardin = 0; \
	for (int boardout = 0; boardout < get_ndevices(); boardout++) { \
		if (mask[boardout])

#define BOARD_ITERATOR_NEXT boardin++

#define BOARD_ITERATOR_END } } while(0)

//
// Sample frequency, as received from the RSPDriver
//
#define DEFAULT_SAMPLE_FREQUENCY 160.0e6
double  gSampleFrequency = DEFAULT_SAMPLE_FREQUENCY;
bool    g_getclock       = false;
bool    gSplitterOn      = false;
bool    gHasSplitter     = false;
bool    gHasAartfaac     = false;
bool    gClockChanged    = false;
bool    gBitmodeChanged  = false;
bool    gSplitterChanged = false;

#define PAIR 2

/*
 * Function to convert the complex semi-floating point representation used by the
 * EPA firmware to a complex<double>.
 */
inline complex<double> convert_to_amplphase(complex<double> val)
{
	double phase     = 0.0;
	double amplitude = real(val)*real(val) + imag(val)*imag(val);

	if (amplitude > 0.0) {
		amplitude = 12 + 5*log10(amplitude); // adjust scaling to allow comparison to subband statistics
	}

	phase = atan2(imag(val), real(val)) * 180 / M_PI;

	if (phase < 0) {
		phase += 360;
	}

	return complex<double>(amplitude, phase);
}
BZ_DECLARE_FUNCTION_RET(convert_to_amplphase, complex<double>)

inline complex<double> convert_to_amplphase_from_int16(complex<int16> int16val)
{
	// scale and convert from int16 to double in range (-1,1]
	complex<double> cdval = complex<double>((double)real(int16val)/(1<<14),
						(double)imag(int16val)/(1<<14));

	//
	// r   = amplitude
	// phi = angle
	// a   = real part of complex weight
	// b   = imaginary part of complex weight
	//
	// a + ib = r * e^(i * phi)
	// r   = sqrt(a^2 + b^2)
	// phi = atan(b/a)
	//

	return complex<double>(::sqrt(real(cdval)*real(cdval) + imag(cdval)*imag(cdval)),
				((::atan(imag(cdval) / real(cdval))) / M_PI) * 180.0);
}
BZ_DECLARE_FUNCTION_RET(convert_to_amplphase_from_int16, complex<double>)

inline double blitz_abs(complex<double> val)
{
	return sqrt(val.real()*val.real() + val.imag()*val.imag());
}
BZ_DECLARE_FUNCTION_RET(blitz_abs, double)

inline double blitz_angle(complex<double> val)
{
	return atan(val.imag() / val.real()) * 180.0 / M_PI;
}
BZ_DECLARE_FUNCTION_RET(blitz_angle, double)

WeightsCommand::WeightsCommand(GCFPortInterface& port, const int bitsPerSample) :
	Command			(port),
	m_type		    (WeightsCommand::COMPLEX),
	itsStage		(0),
	itsBitsPerSample(bitsPerSample)
{
}

void WeightsCommand::send()
{
	switch (itsStage) {
	//if (getMode())
	//{
	case 0: {
		// GET
		RSPGetweightsEvent getweights;

		getweights.timestamp = Timestamp(0,0);
		getweights.rcumask   = getRCUMask();
		getweights.cache     = true;

		m_rspport.send(getweights);
	} break;

	//else
	case 1: {
		// SET
		RSPSetweightsEvent   setweights;
		setweights.timestamp = Timestamp(0,0);
		setweights.rcumask   = getRCUMask();
		logMessage(cerr,formatString("rcumask.count()=%d",setweights.rcumask.count()));

		int nBanks = (MAX_BITS_PER_SAMPLE / itsBitsPerSample);
		setweights.weights().resize(1, setweights.rcumask.count(), nBanks, maxBeamletsPerBank(itsBitsPerSample));

		//bitset<maxBeamlets(bitsPerSample)> beamlet_mask = getBEAMLETSMask();
		boost::dynamic_bitset<> beamlet_mask = getBEAMLETSMask(itsBitsPerSample);

		// -1 < m_value <= 1
		setweights.weights() = itsWeights;
		int rcunr = 0;
		int max_beamlets = maxBeamlets(itsBitsPerSample);
		bool multiple_values = (m_values.size() > 1);
		for (int rcu = 0; rcu < MAX_RCUS; rcu++) {
			if (setweights.rcumask.test(rcu)) {
				std::list<complex<double>>::iterator itr = m_values.begin();
				for (int beamlet = 0; beamlet < max_beamlets; beamlet++) {
					if (beamlet_mask.test(beamlet)) {
                            			if(itr != m_values.end()) {
							complex<double> value = *itr;
							value *= (1<<14); // -.99999 should become -16383 and 1 should become 16384
							int plane = beamlet / maxBeamletsPerBank(itsBitsPerSample);
							int beamletnr = beamlet % maxBeamletsPerBank(itsBitsPerSample);
							setweights.weights()(0,rcunr,plane,beamletnr) = complex<int16>((int16)value.real(), (int16)value.imag());
							//setweights.weights()(0,rcunr,plane,beamletnr) = complex<int16>(10+plane, beamletnr); // for testing
							if(multiple_values) { // advance value if we have multiple values otherwise use the single value for all beamlets
								itr++;
							}
						}
						else {
							logMessage(cerr,formatString("Error: not enough complex numbers for the amount of beamlets"));
							rspctl_exit_code = EXIT_FAILURE;
						}
					}
				} // beamlet
				rcunr++;
			}
		} // rcu
		m_rspport.send(setweights);
	} break;

	default:
		break;
	}
}

GCFEvent::TResult WeightsCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETWEIGHTSACK: {
			RSPGetweightsackEvent ack(e);
			bitset<MAX_RCUS> mask = getRCUMask();
			int nPlanes = (MAX_BITS_PER_SAMPLE / itsBitsPerSample);
			itsWeights.resize(1, mask.count(), nPlanes, maxBeamletsPerBank(itsBitsPerSample));
			itsWeights = complex<int16>(0,0);
			itsWeights = ack.weights();

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_GETWEIGHTS command failed.");
				rspctl_exit_code = EXIT_FAILURE;
				GCFScheduler::instance()->stop();
				return status;
			}


			if (getMode()) {
				if (WeightsCommand::COMPLEX == m_type) {
					int rcuin = 0;
					for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
						if (mask[rcuout]) {
							std::ostringstream logStream;
							logStream << ack.weights()(0, rcuin++, Range::all(), Range::all());
							logMessage(cout,formatString("RCU[%2d].weights=%s", rcuout,logStream.str().c_str()));
						}
					}
				} else {
					blitz::Array<complex<double>, 4> ackweights;
					ackweights.resize(ack.weights().shape());

					// convert to amplitude and angle
					ackweights = convert_to_amplphase_from_int16(ack.weights());

					int rcuin = 0;
					for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
						if (mask[rcuout]) {
							std::ostringstream logStream;
							logStream << ackweights(0, rcuin++, Range::all(), Range::all());
							logMessage(cout,formatString("RCU[%2d].weights=%s", rcuout,logStream.str().c_str()));
						}
					}
				}

				GCFScheduler::instance()->stop();
				return status;
			} else {
				itsStage = 1;
				send();
			}
		} break;

		case RSP_SETWEIGHTSACK:
		{
			RSPSetweightsackEvent ack(e);

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_SETWEIGHTS command failed.");
				rspctl_exit_code = EXIT_FAILURE;
			}
			GCFScheduler::instance()->stop();
			return status;
		} break;

		default:
			status = GCFEvent::NOT_HANDLED;
			GCFScheduler::instance()->stop();
			return status;
			break;
	}
	return status;

}

SubbandsCommand::SubbandsCommand(GCFPortInterface& port, const int bitsPerSample) :
	Command		    (port),
	m_type		    (0),
	itsBitsPerSample(bitsPerSample)
{
}

void SubbandsCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetsubbandsEvent getsubbands;

		getsubbands.timestamp = Timestamp(0,0);
		getsubbands.rcumask   = getRCUMask();
		getsubbands.cache     = true;
		getsubbands.type      = m_type;

		m_rspport.send(getsubbands);
	}
	else {
		// SET
		RSPSetsubbandsEvent   setsubbands;
		setsubbands.timestamp = Timestamp(0,0);
		setsubbands.rcumask   = getRCUMask();
		setsubbands.subbands.setType(m_type);

	    logMessage(cerr,formatString("rcumask.count()=%d",setsubbands.rcumask.count()));

        if (static_cast<int>(m_subbandlist.size()) > maxBeamlets(itsBitsPerSample)) {
            logMessage(cerr,"Error: too many subbands selected");
			rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}

        int nPlanes = (MAX_BITS_PER_SAMPLE / itsBitsPerSample);

		// if only 1 subband selected, apply selection to all
		switch (m_type) {
			case SubbandSelection::BEAMLET: {
				if (1 == m_subbandlist.size()) {
					setsubbands.subbands.beamlets().resize(1, nPlanes, maxBeamletsPerBank(itsBitsPerSample));
					std::list<int>::iterator it = m_subbandlist.begin();
					setsubbands.subbands.beamlets() = (*it);
				} else {
					setsubbands.subbands.beamlets().resize(1, nPlanes, maxBeamletsPerBank(itsBitsPerSample));
                    setsubbands.subbands.beamlets() = 0;
					int i = 0;
					int max_beamlets = maxBeamlets(itsBitsPerSample);
					std::list<int>::iterator it;
					for (it = m_subbandlist.begin(); it != m_subbandlist.end(); it++, i++) {
						if (i >= max_beamlets) {
							break;
						}
						int plane = i / maxBeamletsPerBank(itsBitsPerSample);
						int subbandnr = i % maxBeamletsPerBank(itsBitsPerSample);
						setsubbands.subbands.beamlets()(0, plane, subbandnr) = (*it);
					}
#if 0
		for (; i < maxBeamlets(bitsPerSample); i++) {
			setsubbands.subbands.beamlets()(0, Range::all(), i) = 0;
		}
#endif
				}
			}
			break;

    		case SubbandSelection::XLET: {
    			setsubbands.subbands.crosslets().resize(1, 1, 1);
    			std::list<int>::iterator it = m_subbandlist.begin();
    			setsubbands.subbands.crosslets() = (*it);
			}
			break;

		default:
			logMessage(cerr,"Error: invalid subbandselection type");
			rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
			break;
		}

		m_rspport.send(setsubbands);
	}
}

GCFEvent::TResult SubbandsCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETSUBBANDSACK: {
			RSPGetsubbandsackEvent ack(e);
			bitset<MAX_RCUS> mask = getRCUMask();

			std::ostringstream msg;
			msg << "getsubbandsack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS == ack.status) {
				int rcuin = 0;
				for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
					if (mask[rcuout]) {
						std::ostringstream logStream;
						if (SubbandSelection::BEAMLET == m_type) {
							logStream << ack.subbands.beamlets()(rcuin++, Range::all(), Range::all());
							logMessage(cout,formatString("RCU[%2d].subbands=%s", rcuout,logStream.str().c_str()));
						} else {
						    logStream << ack.subbands.crosslets()(rcuin++, Range::all(), Range::all());
							logMessage(cout,formatString("RCU[%2d].xcsubbands=%s", rcuout,logStream.str().c_str()));
						}
					}
				}
			}
			else {
				logMessage(cerr,"Error: RSP_GETSUBBANDS command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		case RSP_SETSUBBANDSACK: {
			RSPSetsubbandsackEvent ack(e);

			std::ostringstream msg;
			msg << "setsubbandsack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_SETSUBBANDS command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
			break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

RCUCommand::RCUCommand(GCFPortInterface& port) : Command(port)
{
}

void RCUCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetrcuEvent   getrcu;
		getrcu.timestamp = Timestamp(0,0);
		getrcu.rcumask   = getRCUMask();
		getrcu.cache     = false;

		m_rspport.send(getrcu);
	}
	else {
		// SET
		RSPSetrcuEvent   setrcu;
		setrcu.timestamp = Timestamp(0,0);
		setrcu.rcumask   = getRCUMask();

		setrcu.settings().resize(1);
		setrcu.settings()(0) = m_control;

		for (int i = 0; i < setrcu.settings().extent(firstDim); i++) {
			printf("control(%d) =0x%08x\n", i, setrcu.settings()(i).getRaw());
			printf("modified(%d)=0x%08x\n", i, setrcu.settings()(i).getModified());
		}

		m_rspport.send(setrcu);
	}
}

GCFEvent::TResult RCUCommand::ack(GCFEvent& e)
{
	switch (e.signal) {
		case RSP_GETRCUACK: {
			RSPGetrcuackEvent ack(e);
			bitset<MAX_RCUS> mask = getRCUMask();

			if (ack.status == RSP_SUCCESS) {
				int rcuin = 0;
				for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
					if (mask[rcuout]) {
						logMessage(cout,formatString("RCU[%2d].control=0x%08x => %s, mode:%d, delay=%02d, att=%02d",
							rcuout,
							ack.settings()(rcuin).getRaw(),
							(ack.settings()(rcuin).getRaw() & 0x80) ? " ON" : "OFF",
							ack.settings()(rcuin).getMode(),
							ack.settings()(rcuin).getDelay(),
							ack.settings()(rcuin).getAttenuation()));
							rcuin++;
					}
				}
			}
			else {
				logMessage(cerr,"Error: RSP_GETRCU command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		case RSP_SETRCUACK: {
			RSPSetrcuackEvent ack(e);
			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_SETRCU command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
	break;
	} // switch

	GCFScheduler::instance()->stop();

	return GCFEvent::HANDLED;
}

// Easy command set most settings with one command
ModeCommand::ModeCommand(GCFPortInterface& port) :
    Command  (port),
    itsMode  (0),
    itsClock (0),
    itsStage (0)
{
}

void ModeCommand::send()
{
    switch (itsStage) {
        case 0: {
            RSPGetclockEvent   getclock;
            getclock.timestamp = Timestamp(0,0);
            getclock.cache     = true;
            m_rspport.send(getclock);
        } break;

        case 1: {
            RSPSetclockEvent   setclock;
            setclock.timestamp = Timestamp(0,0);
            if (itsClock == 160)
                setclock.clock = 200;
            else
                setclock.clock = 160;
            m_rspport.send(setclock);
            logMessage(cout, formatString("Set clock to %dMHz", setclock.clock));
        } break;

        case 2: {
            RSPSetrcuEvent   setrcu;
            setrcu.timestamp = Timestamp(0,0);
            setrcu.rcumask   = getRCUMask();

            setrcu.settings().resize(1);

            setrcu.settings()(0).setMode((RCUSettings::Control::RCUMode)itsMode);
            logMessage(cout,formatString("Set rcumode to %d", itsMode));

            if (itsMode > 0) {
                setrcu.settings()(0).setEnable(true);
                logMessage(cout, "Enable inputs from RCU's");
            } else {
                setrcu.settings()(0).setEnable(false);
                logMessage(cout, "Disable inputs from RCU's");
            }
            m_rspport.send(setrcu);
        } break;

        case 3: {
            RSPSetbypassEvent request;

            request.timestamp = Timestamp(0,0);
            request.rcumask   = getRCUMask();
            request.settings().resize(1);
            bool siOn;
            if (itsMode == 5) {
                logMessage(cout, "Enable Spectral inversion");
                siOn = true;
            }
            else {
                logMessage(cout, "Disable Spectral inversion");
                siOn = false;
            }
            request.settings()(0).setXSI(siOn);
            request.settings()(0).setYSI(siOn);

            m_rspport.send(request);
        } break;

        case 4: {
            RSPSethbaEvent   sethba;
            sethba.timestamp = Timestamp(0,0);
            sethba.rcumask   = getRCUMask();
            sethba.settings().resize(sethba.rcumask.count(), N_HBA_ELEM_PER_TILE);
            sethba.settings() = 0; // discharge hba elements for one second.
            logMessage(cout, "Discharge HBA elements for 1 second");
            m_rspport.send(sethba);
        } break;

        case 5: {
            RSPSethbaEvent   sethba;
            sethba.timestamp = Timestamp(0,0);
            sethba.rcumask   = getRCUMask();
            sethba.settings().resize(sethba.rcumask.count(), N_HBA_ELEM_PER_TILE);
            sethba.settings() = 253;
            logMessage(cout, "Set HBA delays to 253");
            m_rspport.send(sethba);
        } break;

    }
}

GCFEvent::TResult ModeCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

    switch (e.signal) {
        case RSP_GETCLOCKACK: {
            RSPGetclockackEvent ack(e);
            if (RSP_SUCCESS != ack.status) {
                if (ack.status == RSP_BUSY) {
                    logMessage(cerr,"Error: driver busy.");
                    rspctl_exit_code = EXIT_FAILURE;
                    GCFScheduler::instance()->stop();
                }
                else {
                    logMessage(cerr,"Error: RSP_GETCLOCK command failed.");
                    rspctl_exit_code = EXIT_FAILURE;
                    GCFScheduler::instance()->stop();
                }
            }
            else {
                itsClock = ack.clock;
                logMessage(cout,formatString("Sample frequency: clock=%dMHz", ack.clock));

                ++itsStage;
                if ((itsClock == 160) && (itsMode == 6))
                    ++itsStage;  // No clock change needed

                if ((itsClock == 200) && (itsMode != 6))
                    ++itsStage;  // No clock change needed
                send();
            }
        } break;

        case RSP_SETCLOCKACK: {
            RSPSetclockackEvent ack(e);
            if (RSP_SUCCESS != ack.status) {
                if (ack.status == RSP_BUSY) {
                    logMessage(cerr,"Error: clock NOT set, driver busy.");
                    rspctl_exit_code = EXIT_FAILURE;
                    GCFScheduler::instance()->stop();
                }
                else {
                    logMessage(cerr,"Error: RSP_SETCLOCK command failed.");
                    rspctl_exit_code = EXIT_FAILURE;
                    GCFScheduler::instance()->stop();
                }
            }
            logMessage(cout,"Wait 30 seconds until clock is changed");
            sleep(30);
            ++itsStage;
            send();
        } break;

		case RSP_SETRCUACK: {
			RSPSetrcuackEvent ack(e);
			if (ack.status != RSP_SUCCESS) {
				logMessage(cerr,"Error: RSP_SETRCU command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
                GCFScheduler::instance()->stop();
			}
            ++itsStage;
            send();
		} break;

        case RSP_SETBYPASSACK: {
            RSPSetbypassackEvent ack(e);

            std::ostringstream msg;
            msg << "setSIack.timestamp=" << ack.timestamp;
            logMessage(cout, msg.str());

            if (ack.status != RSP_SUCCESS) {
                logMessage(cerr, "Error: RSP_SETSI command failed.");
                rspctl_exit_code = EXIT_FAILURE;
                GCFScheduler::instance()->stop();
            }

            if (itsMode < 5) {
                GCFScheduler::instance()->stop();
            }
            else {
                logMessage(cout,formatString("rcumode > 5 (%d), send hba delay", itsMode));
                ++itsStage;
                send();
            }
        } break;

        case RSP_SETHBAACK: {
            RSPSethbaackEvent ack(e);
            if (ack.status != RSP_SUCCESS) {
                logMessage(cerr,"Error: RSP_SETHBA command failed.");
                rspctl_exit_code = EXIT_FAILURE;
            }
            if (itsStage < 5) {
                sleep(1);
                ++itsStage;
                send();
            }
            else {
                GCFScheduler::instance()->stop();
            }
        } break;

        default: {
            status = GCFEvent::NOT_HANDLED;
        } break;

    } // switch

	return status;
}

// Swap X Y on RCU
SWAPXYCommand::SWAPXYCommand(GCFPortInterface& port) : Command(port)
{
}

void SWAPXYCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetswapxyEvent   getswapxy;
		getswapxy.timestamp = Timestamp(0,0);
		getswapxy.cache     = true;

		m_rspport.send(getswapxy);
	}
	else {
		// SET
		RSPSetswapxyEvent   setswapxy;
		setswapxy.timestamp = Timestamp(0,0);
		setswapxy.antennamask   = getANTENNAMask();
		setswapxy.swapxy    = getSwapXY();

		logMessage(cout,formatString("antennamask.count()=%d", setswapxy.antennamask.count()));
		m_rspport.send(setswapxy);
	}
}

GCFEvent::TResult SWAPXYCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETSWAPXYACK: {
			RSPGetswapxyackEvent ack(e);

			std::ostringstream msg;
			msg << "setswapxyack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());
			msg.seekp(0);

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_GETSWAPXY command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
				break;
			}

			// print swap settings
			for (int ant = 0; ant < get_ndevices(); ant++) {
				if (getANTENNAMask().test(ant)) {
					cout << formatString("ANTENNA[%02u].xy= ", ant);
					// if antenna is set in mask, xy is swapped
					if (ack.antennamask.test(ant)) {
						cout << "swapped";
					}
					else {
						cout << "straight";
					}
					cout << endl;
				}
			}
		}
		break;

		case RSP_SETSWAPXYACK: {
			RSPSetswapxyackEvent ack(e);

			std::ostringstream msg;
			msg << "setswapxyack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_SETSWAPXY command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

// Set bitmode
BitmodeCommand::BitmodeCommand(GCFPortInterface& port) : Command(port)
{
}

void BitmodeCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetbitmodeEvent   getbitmode;
		getbitmode.timestamp = Timestamp(0,0);
		getbitmode.cache     = true;

		m_rspport.send(getbitmode);
	}
	else {
		// SET
		RSPSetbitmodeEvent   setbitmode;
		setbitmode.timestamp       = Timestamp(0,0);
		setbitmode.rspmask         = getRSPMask();
		setbitmode.bits_per_sample = bitmode();
		m_rspport.send(setbitmode);
	}
}

GCFEvent::TResult BitmodeCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETBITMODEACK: {
			RSPGetbitmodeackEvent ack(e);

			std::ostringstream msg;
			msg << "setbitmodeack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());
			msg.seekp(0);

			if (ack.status != RSP_SUCCESS) {
				logMessage(cerr, "Error: RSP_GETBitMode command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
				break;
			}

			// print bitmode settings
			cout << "board  :version :mode\n";
			for (int rsp = 0; rsp < get_ndevices(); rsp++) {
				if (getRSPMask().test(rsp)) {
					switch (ack.bitmode_version[rsp]) {
				    case 0:
				        cout << formatString("RSP[%02u]: 16     : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    case 1:
				        cout << formatString("RSP[%02u]: 16/8   : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    case 2:
				        cout << formatString("RSP[%02u]: 16/8/4 : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    default: break;
					}
				}
			}
		}
		break;

		case RSP_SETBITMODEACK: {
			RSPSetbitmodeackEvent ack(e);

			std::ostringstream msg;
			msg << "setbitmodeack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_SETBitMode command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

// set subbands
SDOCommand::SDOCommand(GCFPortInterface& port) :
	Command		    (port),
	itsBitsPerSample(0)
{
}

void SDOCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetsdoEvent getsdo;

		getsdo.timestamp = Timestamp(0,0);
		getsdo.rcumask   = getRCUMask();
		getsdo.cache     = true;

		m_rspport.send(getsdo);
	}
	else {
        if (itsBitsPerSample == 0) {
            RSPGetsdomodeEvent   getsdomode;
            getsdomode.timestamp = Timestamp(0,0);
            getsdomode.cache     = true;

            m_rspport.send(getsdomode);
        }
        else{
            // SET
            RSPSetsdoEvent   setsdo;
            setsdo.timestamp = Timestamp(0,0);
            setsdo.rcumask   = getRCUMask();

            logMessage(cerr,formatString("rcumask.count()=%d",setsdo.rcumask.count()));

            int MAX_SDO_SUBBANDS_PER_PLANE = 36;
            int MAX_SDO_PLANES             = 4;
            int MAX_SDO_SUBBANDS           = MAX_SDO_SUBBANDS_PER_PLANE * MAX_SDO_PLANES;

            if (static_cast<int>(itsSubbandlist.size()) > MAX_SDO_SUBBANDS) {
                logMessage(cerr,formatString("Error: too many subbands selected max=%d", MAX_SDO_SUBBANDS));
			    rspctl_exit_code = EXIT_FAILURE;
                exit(EXIT_FAILURE);
            }

            setsdo.subbands.subbands().resize(1, MAX_SDO_PLANES, MAX_SDO_SUBBANDS_PER_PLANE);
            setsdo.subbands.subbands() = 0;
            // if only 1 subband selected, apply selection to all
            if (1 == itsSubbandlist.size()) {
                std::list<int>::iterator it = itsSubbandlist.begin();
                setsdo.subbands.subbands() = (*it);
            } else {
                int i = 0;
                std::list<int>::iterator it;
                for (it = itsSubbandlist.begin(); it != itsSubbandlist.end(); it++, i++) {
                    if (i >= MAX_SDO_SUBBANDS) {
                        break;
                    }
                    int plane = i / MAX_SDO_SUBBANDS_PER_PLANE;
                    int subbandnr = i % MAX_SDO_SUBBANDS_PER_PLANE;
                    setsdo.subbands.subbands()(0, plane, subbandnr) = (*it);
                }
    #if 0
                for (; i < MAX_SDO_SUBBANDS; i++) {
                    setsdo.subbands.subbands()(0, Range::all(), i) = 0;
                }
    #endif
            }
            m_rspport.send(setsdo);
        }
    }
}

GCFEvent::TResult SDOCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
        case RSP_GETSDOMODEACK: {
            RSPGetsdomodeackEvent ack(e);
            int n_bits_per_sample = MIN_BITS_PER_SAMPLE;
            for (int i = 0; i < (get_ndevices() / 8); i++) {
                n_bits_per_sample = (ack.bits_per_sample[i] > n_bits_per_sample) ? ack.bits_per_sample[i] : n_bits_per_sample;
            }
            logMessage(cout,formatString("bits per sample=%d",  n_bits_per_sample));
            itsBitsPerSample = n_bits_per_sample;
            send(); // bits per sample received get selected subbands.
        } break;

        case RSP_GETSDOACK: {
			RSPGetsdoackEvent ack(e);
			bitset<MAX_RCUS> mask = getRCUMask();

			std::ostringstream msg;
			msg << "getsdoack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS == ack.status) {
				int rcuin = 0;
				for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
					if (mask[rcuout]) {
						std::ostringstream logStream;
                        logStream << ack.subbands.subbands()(rcuin++, Range::all(), Range::all());
                        logMessage(cout,formatString("RCU[%2d].subbands=%s", rcuout,logStream.str().c_str()));
					}
				}
			}
			else {
				logMessage(cerr,"Error: RSP_GETSDO command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		case RSP_SETSDOACK: {
			RSPSetsdoackEvent ack(e);

			std::ostringstream msg;
			msg << "setsdoack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_SETSDO command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
			break;
	}

    if (e.signal != RSP_GETSDOMODEACK) {
        GCFScheduler::instance()->stop();
    }

	return status;
}

// Set SDO bitmode
SDOmodeCommand::SDOmodeCommand(GCFPortInterface& port) : Command(port)
{
}

void SDOmodeCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetsdomodeEvent   getsdomode;
		getsdomode.timestamp = Timestamp(0,0);
		getsdomode.cache     = true;

		m_rspport.send(getsdomode);
	}
	else {
		// SET
		RSPSetsdomodeEvent   setsdomode;
		setsdomode.timestamp       = Timestamp(0,0);
		setsdomode.rspmask         = getRSPMask();
		setsdomode.bits_per_sample = sdomode();
		m_rspport.send(setsdomode);
	}
}

GCFEvent::TResult SDOmodeCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETSDOMODEACK: {
			RSPGetsdomodeackEvent ack(e);

			std::ostringstream msg;
			msg << "setsdomodeack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());
			msg.seekp(0);

			if (ack.status != RSP_SUCCESS) {
				logMessage(cerr, "Error: RSP_GETSDOMode command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
				break;
			}

			// print sdomode settings
			cout << "board  :version :mode\n";
			for (int rsp = 0; rsp < get_ndevices(); rsp++) {
				//cout << formatString("RSP=%d, mode=%d, bits=%d\n", rsp, ack.bitmode_version[rsp], ack.bits_per_sample[rsp]);
                if (getRSPMask().test(rsp)) {
					switch (ack.bitmode_version[rsp]) {
				    case 0:
				        cout << formatString("RSP[%02u]: 16       : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    case 1:
				        cout << formatString("RSP[%02u]: 16/8     : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    case 2:
				        cout << formatString("RSP[%02u]: 16/8/5   : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
                    case 3:
				        cout << formatString("RSP[%02u]: 16/8/5/4 : %2d\n", rsp, ack.bits_per_sample[rsp]);
				        break;
				    default: break;
					}
				}
			}
		}
		break;

		case RSP_SETSDOMODEACK: {
			RSPSetsdomodeackEvent ack(e);

			std::ostringstream msg;
			msg << "setsdomodeack.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_SETSDOMode command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

HBACommand::HBACommand(GCFPortInterface& port) : Command(port)
{
}

void HBACommand::send()
{
	if (getMode()) {
		// GET
		if (realDelays) {
			RSPReadhbaEvent   readhba;
			readhba.timestamp = Timestamp(0,0);
			readhba.rcumask   = getRCUMask();
			readhba.cache     = true;

			m_rspport.send(readhba);
		}
		else {
			RSPGethbaEvent   gethba;
			gethba.timestamp = Timestamp(0,0);
			gethba.rcumask   = getRCUMask();
			gethba.cache     = false;

			m_rspport.send(gethba);
		}
	}
	else { // SET
		// Note: also accept the 'set'-form for the readHBA command
		//       why bother the user if we know what he realy ment
		RSPSethbaEvent   sethba;
		sethba.timestamp = Timestamp(0,0);
		sethba.rcumask   = getRCUMask();

		sethba.settings().resize(sethba.rcumask.count(), N_HBA_ELEM_PER_TILE);

		if (1 == m_delaylist.size()) {
			std::list<int>::iterator it = m_delaylist.begin();
			sethba.settings() = (*it);
		}
		else {
			// clear first
			sethba.settings() = 0;

			int i = 0;
			std::list<int>::iterator it;
			for (it = m_delaylist.begin(); it != m_delaylist.end(); it++, i++) {
				if (i >= N_HBA_ELEM_PER_TILE)
					break;
				sethba.settings()(Range::all(), i) = (*it);
			}
		}
#if 0
		for (int i = 0; i < sethba.settings().extent(firstDim); i++) {
			printf("delays(%d)=", i);
			cout << sethba.settings()(i) << endl;
		}
#endif
		m_rspport.send(sethba);
	}
}

GCFEvent::TResult HBACommand::ack(GCFEvent& e)
{
	switch (e.signal) {
	case RSP_GETHBAACK: {
		RSPGethbaackEvent ack(e);
		bitset<MAX_RCUS> mask = getRCUMask();

		cout << "settings().shape()=" << ack.settings().shape() << endl;

		if (RSP_SUCCESS == ack.status) {
			int hbain = 0;
			for (int hbaout = 0; hbaout < get_ndevices(); hbaout++) {
				if (mask[hbaout]) {
					cout << formatString("HBA[%2d].delays=", hbaout);
					for (int i = 0; i < N_HBA_ELEM_PER_TILE; i++) {
						cout << formatString(" %3d", (int)(ack.settings()(hbain, i)));
					}
					cout << endl;
					hbain++;
				}
			}
		}
		else {
			logMessage(cerr,"Error: RSP_GETHBA command failed.");
		    rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	case RSP_READHBAACK: {
		RSPReadhbaackEvent ack(e);
		bitset<MAX_RCUS> mask = getRCUMask();

		cout << "settings().shape()=" << ack.settings().shape() << endl;

		if (RSP_SUCCESS == ack.status) {
			int hbain = 0;
			for (int hbaout = 0; hbaout < get_ndevices(); hbaout++) {
				if (mask[hbaout]) {
					cout << formatString("HBA[%2d].real delays=", hbaout);
					for (int i = 0; i < N_HBA_ELEM_PER_TILE; i++) {
						if ((int)(ack.settings()(hbain, i)) == 255) {
							cout << " ???";
						}
						else  {
							cout << formatString(" %3d", (int)(ack.settings()(hbain, i)));
						}
					}
					cout << endl;
					hbain++;
				}
			}
		}
		else {
			logMessage(cerr,"Error: RSP_READHBA command failed.");
		    rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	case RSP_SETHBAACK: {
		RSPSethbaackEvent ack(e);
		if (RSP_SUCCESS != ack.status) {
			logMessage(cerr,"Error: RSP_SETHBA command failed.");
		    rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;
	}

	GCFScheduler::instance()->stop();

	return (GCFEvent::HANDLED);
}

//
// RSUCommand
//
RSUCommand::RSUCommand(GCFPortInterface& port) : Command(port)
{
}

void RSUCommand::send()
{
	if (getMode()) {
		// GET not supported
		logMessage(cerr, "Error: RSUCommand GET not supported");
		rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	else {
		// SET
		RSPSetrsuEvent   setrsu;
		setrsu.timestamp = Timestamp(0,0);
		setrsu.rspmask   = getRSPMask();

		setrsu.settings().resize(1);
		setrsu.settings()(0) = m_control;

		for (int i = 0; i < setrsu.settings().extent(firstDim); i++) {
			printf("control(%d)=0x%08x\n", i, setrsu.settings()(i).getRaw());
		}

		m_rspport.send(setrsu);
	}
}

GCFEvent::TResult RSUCommand::ack(GCFEvent& e)
{
	switch (e.signal) {
#if 0
		case RSP_GETRSUACK: {
			RSPGetrsuackEvent ack(e);
			bitset<MAX_RCUS> mask = getRCUMask();

			if (RSP_SUCCESS == ack.status) {
				int boardin = 0;
				for (int boardout = 0; boardout < get_ndevices(); boardout++) {

					if (mask[boardout]) {
						logMessage(cout,formatString("RSU[%2d].control=0x%08x",boardout, ack.settings()(boardin++).getRaw()));
					}
				}
			}
			else {
				logMessage(cerr,"Error: RSP_GETRSU command failed.");
				rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;
#endif
		case RSP_SETRSUACK: {
			RSPSetrsuackEvent ack(e);
			if (RSP_SUCCESS != ack.status) {
                if (ack.status == RSP_BUSY) {
                    logMessage(cerr,"Error: rsu NOT set, driver busy.");
					rspctl_exit_code = EXIT_FAILURE;
                }
                else {
                    logMessage(cerr,"Error: RSP_SETRSU command failed.");
					rspctl_exit_code = EXIT_FAILURE;
                }

			}
		}
	}

	GCFScheduler::instance()->stop();

	return GCFEvent::HANDLED;
}

//
// ClockCommand
//
ClockCommand::ClockCommand(GCFPortInterface& port) : Command(port)
{
}

void ClockCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetclockEvent   getclock;
		getclock.timestamp = Timestamp(0,0);
		getclock.cache     = true;

		// set flag to tell SubClockCommand to
		// terminate after receiving RSP_GETCLOCKACK
		g_getclock         = true;

		m_rspport.send(getclock);
	}
	else {
		// SET
		RSPSetclockEvent   setclock;
		setclock.timestamp = Timestamp(0,0);
		setclock.clock     = m_clock;

		m_rspport.send(setclock);
	}
}

GCFEvent::TResult ClockCommand::ack(GCFEvent& e)
{
	if (e.signal == RSP_GETCLOCKACK) {
		RSPGetclockackEvent ack(e);
		if (RSP_SUCCESS != ack.status) {
			if (ack.status == RSP_BUSY) {
                logMessage(cerr,"Error: driver busy.");
			    rspctl_exit_code = EXIT_FAILURE;
            }
            else {
                logMessage(cerr,"Error: RSP_GETCLOCK command failed.");
                rspctl_exit_code = EXIT_FAILURE;
            }
		}
		else {
			gSampleFrequency = 1.0e6 * ack.clock;
			logMessage(cout,formatString("Sample frequency: clock=%dMHz", ack.clock));
		}
	}
	else if (e.signal == RSP_SETCLOCKACK) {
		RSPSetclockackEvent ack(e);
		if (RSP_SUCCESS != ack.status) {
			if (ack.status == RSP_BUSY) {
                logMessage(cerr,"Error: clock NOT set, driver busy.");
			    rspctl_exit_code = EXIT_FAILURE;
            }
            else {
                logMessage(cerr,"Error: RSP_SETCLOCK command failed.");
			    rspctl_exit_code = EXIT_FAILURE;
            }
		}
	}

	GCFScheduler::instance()->stop();
	return GCFEvent::HANDLED;
}

//
// SubClockCommand
//
SubClockCommand::SubClockCommand(GCFPortInterface& port) : Command(port)
{
}

void SubClockCommand::send()
{
	if (getMode()) {
		// Get current clock setting
		RSPGetclockEvent   getclock;

		getclock.timestamp = Timestamp(0,0);
		getclock.cache     = true; // get value from cache

		m_rspport.send(getclock);
	}
	else {
		// SET not supported
		logMessage(cerr, "SubClockCommand: SET not supported");
	    rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
}

GCFEvent::TResult SubClockCommand::ack(GCFEvent& e)
{
	switch (e.signal) {
	case RSP_GETCLOCKACK: {
		RSPGetclockackEvent ack(e);
		if (RSP_SUCCESS == ack.status) {
			gSampleFrequency = 1.0e6 * ack.clock;
			if (g_getclock) {
				logMessage(cout,formatString("Sample frequency: clock=%dMHz", ack.clock));
				GCFScheduler::instance()->stop();
			} else {
				LOG_DEBUG(formatString("Received initial sample frequency: clock=%dMHz", ack.clock));

				// Subscribe to updates from now on
				RSPSubclockEvent subclock;
				subclock.timestamp = Timestamp(0,0);
				subclock.period = 1; // check for change every second

				m_rspport.send(subclock);
			}
		}
		else {
			logMessage(cerr,"Error: RSP_GETCLOCK command failed.");
	    	rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	case RSP_SUBCLOCKACK: {
		RSPSubclockackEvent ack(e);
		if (RSP_SUCCESS != ack.status) {
			logMessage(cerr,"Error: RSP_UPDCLOCK command failed.");
	    	rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
	}
	break;

	case RSP_UPDCLOCK: {
		RSPUpdclockEvent upd(e);
		if (RSP_SUCCESS == upd.status) {
			logMessage(cout,formatString("Received new sample frequency: clock=%dMHz", upd.clock));
			gSampleFrequency = 1.0e6 * upd.clock;
		}
		else {
			logMessage(cerr,"Error: RSP_UPDCLOCK command failed.");
	    	rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	default:
		return GCFEvent::NOT_HANDLED;
	break;
	}

	return GCFEvent::HANDLED;
}

//
// TD status
//
TDStatusCommand::TDStatusCommand(GCFPortInterface& port) :
	Command(port),
	m_board()
{
}

void TDStatusCommand::send()
{
	if (getMode()) { // GET
		RSPGettdstatusEvent   gettdstatus;
		gettdstatus.timestamp = Timestamp(0,0);
		gettdstatus.rspmask   = getRSPMask();
		gettdstatus.cache     = true;

		m_rspport.send(gettdstatus);
	}
	else { // SET
		logMessage(cerr,"Setting tdstatus not yet allowed");
	}
}

GCFEvent::TResult TDStatusCommand::ack(GCFEvent& event)
{
	if (RSP_GETTDSTATUSACK == event.signal) {
		RSPGettdstatusackEvent ack(event);
		bitset<MAX_N_RSPBOARDS> mask = getRSPMask();

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr,"Error: RSP_GETSTATUS command failed.");
		}
		else {
			logMessage(cout,formatString("RSP |   10MHz input | output clock | PPS input | PLL 160MHZ | PLL 200MHz | V3.3 | V5.0 | Temperature"));
			BOARD_ITERATOR_BEGIN {
				TDBoardStatus& boardstatus = ack.tdstatus.board()(boardin);
				if (boardstatus.invalid) {
					logMessage(cout,formatString(" %2d | Not controlling the TD board", boardout));
				}
				else {
					if (boardstatus.unknown) {
						logMessage(cout,formatString(" %2d |      %3s      |      %3s     |    %3s    | %10s | %10s | %4.1f | %4.1f | %2d",
								boardout,
								"?", "?", "?", "?", "?", 0, 0, 0));
					}
					else {
						logMessage(cout,formatString(" %2d |      %3s      |      %3d     |    %3s    | %10s | %10s | %4.1f | %4.1f | %2d",
								boardout,
								(boardstatus.input_10MHz  ? "SMA" : "INF"),
								(boardstatus.output_clock ? 200   : 160),
								(boardstatus.pps_input    ? "INF" : "SMA"),
								(boardstatus.pll_160MHz_locked ? "LOCKED" : "not locked"),
								(boardstatus.pll_200MHz_locked ? "LOCKED" : "not locked"),
								(boardstatus.v3_3 * 3.3) / 192.0,
								(boardstatus.v2_5 * 5.0) / 192.0,
								boardstatus.temperature));
					}
				}
				BOARD_ITERATOR_NEXT;
			}
			BOARD_ITERATOR_END;
		}
	}

	GCFScheduler::instance()->stop();
	return GCFEvent::HANDLED;
}

TBBCommand::TBBCommand(GCFPortInterface& port) : Command(port), m_type(0)
{
}

void TBBCommand::send()
{
	if (getMode()) {
		// GET
		RSPGettbbEvent   gettbb;
		gettbb.timestamp = Timestamp(0,0);
		gettbb.rcumask   = getRCUMask();
		gettbb.cache     = true;

		m_rspport.send(gettbb);
	}
	else {
		// SET
		RSPSettbbEvent   settbb;
		settbb.timestamp = Timestamp(0,0);
		settbb.rcumask   = getRCUMask();

		logMessage(cout,formatString("rcumask.count()=%d", settbb.rcumask.count()));

		// if only 1 subband selected, apply selection to all
		switch (m_type) {
			case TRANSIENT: {
				settbb.settings().resize(1);
				settbb.settings()(0).reset();
			}
			break;

			case SUBBANDS: {
				settbb.settings().resize(1);
				settbb.settings()(0).reset();

				std::list<int>::iterator it;
				for (it = m_subbandlist.begin(); it != m_subbandlist.end(); it++) {
					if ((*it) >= MAX_SUBBANDS) {
						continue;
					}
					settbb.settings()(0).set(*it);
				}
				logMessage(cout, formatString("tbbbandsel.count()=%d ", settbb.settings()(0).count()));
			}
			break;

			default:
				logMessage(cerr, "Error: invalid tbbmode type");
	    		rspctl_exit_code = EXIT_FAILURE;
				exit(EXIT_FAILURE);
			break;
		} // switch

	m_rspport.send(settbb);
	}
}

GCFEvent::TResult TBBCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETTBBACK: {
			RSPGettbbackEvent ack(e);

			std::ostringstream msg;
			msg << "settbback.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());
			msg.seekp(0);

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_GETTBB command failed.");
	    		rspctl_exit_code = EXIT_FAILURE;
				break;
			}

			// print settings
			int rcuin = 0;
			for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
				if (getRCUMask()[rcuout]) {
					cout << formatString("RCU[%02u].tbbsettings= ", rcuout);
					if (ack.settings()(rcuin).count() == 0) {
						cout << "transient";
					}
					else {
						for (unsigned int ilong = 0; ilong < ack.settings()(0).size()/(sizeof(uint32) * BITSOFBYTE); ilong++) {
							cout << formatString("%08lx ", htonl((ack.settings()(rcuin) & bitset<MAX_SUBBANDS>(0xFFFFFFFF)).to_uint32()));
							ack.settings()(rcuin) >>= sizeof(uint32)*BITSOFBYTE;
						}
					}
					cout << endl;

					rcuin++;
				}
			}
		}
		break;

		case RSP_SETTBBACK: {
			RSPSettbbackEvent ack(e);

			std::ostringstream msg;
			msg << "settbback.timestamp=" << ack.timestamp;
			logMessage(cout, msg.str());

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr, "Error: RSP_SETTBB command failed.");
	    		rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

//
// SICommand
//
SICommand::SICommand(GCFPortInterface& port) : Command(port), m_siOn(false)
{
}

void SICommand::send()
{
	if (getMode()) {
		// GET
		RSPGetbypassEvent request;

		request.timestamp = Timestamp(0,0);
		request.rcumask   = getRCUMask();
		request.cache     = true;

		m_rspport.send(request);
	}
	else {
		// SET
		RSPSetbypassEvent request;

		request.timestamp = Timestamp(0,0);
		request.rcumask   = getRCUMask();
		request.settings().resize(1);
		request.settings()(0).setXSI(m_siOn);
		request.settings()(0).setYSI(m_siOn);

		logMessage(cout,formatString("bypassSetting  =%02X", request.settings()(0).getAsUint16()));

		m_rspport.send(request);
	}
}

GCFEvent::TResult SICommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case RSP_GETBYPASSACK: {
		RSPGetbypassackEvent ack(e);

		std::ostringstream msg;
		msg << "getSIack.timestamp=" << ack.timestamp;
		logMessage(cout, msg.str());
		msg.seekp(0);

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_GETSI command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			break;
		}

		// user made a selection? Only show the selection.
		if (getRCUMask().count() != (uint) get_ndevices()) {
			int rcuin = 0;
			for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
				if (getRCUMask()[rcuout]) {
					if (rcuout % 2 == 0) { // X-pol?
						cout << formatString("RCU[%03d].si=%s\n", rcuout, ack.settings()(rcuin).getXSI() ? "on":"off");
					}
					else {
						cout << formatString("RCU[%03d].si=%s\n", rcuout, ack.settings()(rcuin).getYSI() ? "on":"off");
					}
					rcuin++; // there is a setting for every rcu!
				}
			}
			break;
		}

		// no selection made. Show all settings in a nice matrix.
		int rcusPerBoard = 8; // !!!
		for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {
			if (rcuout % rcusPerBoard == 0) {
				cout << formatString("\nBoard[%02d]:", rcuout / rcusPerBoard);
			}
			bool isOn = (rcuout % 2 == 0) ? ack.settings()(rcuout).getXSI() :
													ack.settings()(rcuout).getYSI();
			if (isOn) {
				cout << formatString("%3d ", rcuout);
			}
			else {
				cout << "  . ";
			}
		}
		cout << endl;
	}
	break;

	case RSP_SETBYPASSACK: {
		RSPSetbypassackEvent ack(e);

		std::ostringstream msg;
		msg << "setSIack.timestamp=" << ack.timestamp;
		logMessage(cout, msg.str());

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_SETSI command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

//
// SDOenableCommand
//
SDOenableCommand::SDOenableCommand(GCFPortInterface& port) : Command(port), m_sdoOn(false)
{
}

void SDOenableCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetbypassEvent request;

		request.timestamp = Timestamp(0,0);
		request.rcumask   = getRCUMask();
		request.cache     = true;

		m_rspport.send(request);
	}
	else {
		// SET
		RSPSetbypassEvent request;

		request.timestamp = Timestamp(0,0);
		request.rcumask   = getRCUMask();
		request.settings().resize(1);
		request.settings()(0).setSDO(m_sdoOn);

		logMessage(cout,formatString("bypassSetting  =%02X", request.settings()(0).getAsUint16()));

		m_rspport.send(request);
	}
}

GCFEvent::TResult SDOenableCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case RSP_GETBYPASSACK: {
		RSPGetbypassackEvent ack(e);

		std::ostringstream msg;
		msg << "getSIack.timestamp=" << ack.timestamp;
		logMessage(cout, msg.str());
		msg.seekp(0);

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_GETSDO command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			break;
		}

		// no selection made. Show all settings in a nice matrix.
		int rcusPerBoard = 8; // !!!
		for (int rcu = 0; rcu < get_ndevices(); rcu += rcusPerBoard) {
			cout << formatString("\nBoard[%02d].sdo=%s", rcu/rcusPerBoard, ack.settings()(rcu).getSDO() ? "on":"off");
		}
		cout << endl;
	}
	break;

	case RSP_SETBYPASSACK: {
		RSPSetbypassackEvent ack(e);

		std::ostringstream msg;
		msg << "setSIack.timestamp=" << ack.timestamp;
		logMessage(cout, msg.str());

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_SETSDOENABLE command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}

//
// DataStreamCommand
//
DataStreamCommand::DataStreamCommand(GCFPortInterface& port) : Command(port), itsStream0On(true), itsStream1On(true)
{
}

void DataStreamCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetdatastreamEvent request;

		request.timestamp = Timestamp(0,0);
		//request.rcumask   = getRSPMask();
		request.cache     = true;

		m_rspport.send(request);
	}
	else {
		// SET
		RSPSetdatastreamEvent request;

		request.timestamp = Timestamp(0,0);
		//request.rcumask   = getRSPMask();
		request.switch_on0 = itsStream0On;
		request.switch_on1 = gSplitterOn ? itsStream1On : false;

		if (itsStream1On && !gSplitterOn) {
			logMessage(cerr,"Error: Splitter is off, second datastream cannot be turned on!");
	   		rspctl_exit_code = EXIT_FAILURE;
		}
		if (gHasSplitter) {
			logMessage(cout,formatString("set datastream 0:%s 1:%s", request.switch_on0?"on":"off", request.switch_on1?"on":"off"));
		}
		else {
			logMessage(cout,formatString("set datastream %s", request.switch_on0?"on":"off"));
		}

		m_rspport.send(request);
	}
}

GCFEvent::TResult DataStreamCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case RSP_GETDATASTREAMACK: {
		RSPGetdatastreamackEvent ack(e);

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_GETDATASTREAM command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			break;
		}
		if (gHasSplitter) {
			cout << formatString("Datastream to CEP switched 0:%s 1:%s\n", ack.switch_on0?"on":"off", ack.switch_on1?"on":"off");
		}
		else {
			cout << formatString("Datastream to CEP switched %s\n", ack.switch_on0?"on":"off");
		}
	}
	break;

	case RSP_SETDATASTREAMACK: {
		RSPSetdatastreamackEvent ack(e);

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr, "Error: RSP_SETDATASTREAM command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
		}
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	GCFScheduler::instance()->stop();

	return status;
}


//
// RegisterStateCommand
//
RegisterStateCommand::RegisterStateCommand(GCFPortInterface& port) :
	Command(port), m_subscriptionhandle(0)
{
}

void RegisterStateCommand::send()
{
	if (getMode()) {
		// GET == SUBSCRIBE
		RSPSubregisterstateEvent subregstate;
		subregstate.timestamp = Timestamp(0,0);
		subregstate.period    = 1; // once every second

		m_rspport.send(subregstate);
	}
	else {
		// SET not supported
		logMessage(cerr, "Error: RegisterStateCommand: SET not supported");
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
}

GCFEvent::TResult RegisterStateCommand::ack(GCFEvent& e)
{
	if (RSP_SUBREGISTERSTATEACK == e.signal) {
		RSPSubregisterstateackEvent ack(e);
		if (RSP_SUCCESS != ack.status) {
			logMessage(cerr,"Error: RSP_UPDREGISTERSTATE command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
	}

	if (RSP_UPDREGISTERSTATE != e.signal) return GCFEvent::NOT_HANDLED;

	RSPUpdregisterstateEvent upd(e);

	if (RSP_SUCCESS == upd.status) {
		std::ostringstream logStream;
		logStream << "registerstate update at " << upd.timestamp << endl;
		upd.state.print(logStream, gHasAartfaac);
		logMessage(cout,logStream.str());
	}
	else {
		logMessage(cerr, "Error: register state update failed.");
	   	rspctl_exit_code = EXIT_FAILURE;
	}

	return GCFEvent::HANDLED;
}

void RegisterStateCommand::stop()
{
	if (getMode()) {
		// UNSUBSCRIBE
		RSPUnsubregisterstateEvent unsubregstate;
		unsubregstate.handle = m_subscriptionhandle;
		m_rspport.send(unsubregstate);
	}
}

//
// SPU status
//
SPUStatusCommand::SPUStatusCommand(GCFPortInterface& port) :
	Command(port),
	itsSPUs()
{
}

// send()
void SPUStatusCommand::send()
{
	// check mode
	if (!getMode()) {
		logMessage(cerr,"Setting SPUstatus is not possible");
	   	rspctl_exit_code = EXIT_FAILURE;
		return;
	}

	// construct message
	RSPGetspustatusEvent   getspustatus;
	getspustatus.timestamp = Timestamp(0,0);
	getspustatus.cache     = true;

	// and send it.
	m_rspport.send(getspustatus);
}

// ack()
GCFEvent::TResult SPUStatusCommand::ack(GCFEvent& event)
{
	if (event.signal == RSP_GETSPUSTATUSACK) {
		RSPGetspustatusackEvent ack(event);

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr,"Error: RSP_GETSPUSTATUS command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
		}
		else {
			logMessage(cout,"Subrack | RCU 5.0V | LBA 8.0V | HBA 48V | SPU 3.3V | Temperature");
			int  nrSubracks = ack.spustatus.subrack().size();
			for (int sr = 0; sr < nrSubracks; sr++) {
				SPUBoardStatus&  SPUstat = ack.spustatus.subrack()(sr);
				if (SPUstat.temperature == 255) {
					logMessage(cout,formatString("   %2d   |      ?   |      ?   |     ?   |      ?   |  ?", sr));
				}
				else {
					logMessage(cout,formatString("   %2d   |    %4.1f  |    %4.1f  |   %4.1f  |    %4.1f  | %2d",
						sr,
						(SPUstat.v2_5 * 1.0) * 2.5  / 192.0 * 2.0,
						(SPUstat.v3_3 * 1.0) * 3.3  / 192.0 * 3.0,
						(SPUstat.v12  * 1.0) * 12.0 / 192.0 * 4.01,
						(SPUstat.vcc  * 1.0) * 5.0  / 192.0,
						SPUstat.temperature));
				}
			}
		}
	}

	GCFScheduler::instance()->stop();
	return (GCFEvent::HANDLED);
}
//
// RawBlock
//
RawBlockCommand::RawBlockCommand(GCFPortInterface& port):
	Command(port),
	itsRSPboard(0),
	itsAddress(0),
	itsOffset(0),
	itsDataLen(0)
{
	memset (&itsData[0], 0, RSP_RAW_BLOCK_SIZE);
}

// send()
void RawBlockCommand::send()
{
	// read mode?
	if (getMode()) {
		// construct message
		RSPGetblockEvent rbCmd;
		rbCmd.timestamp  = Timestamp(0,0);
		rbCmd.boardID    = itsRSPboard;
		rbCmd.address    = itsAddress;
		rbCmd.offset     = itsOffset;
		rbCmd.dataLen    = itsDataLen;
		// and send it.
		m_rspport.send(rbCmd);
		return;
	}

	// write block
	RSPSetblockEvent rbCmd;
	rbCmd.timestamp  = Timestamp(0,0);
	rbCmd.boardID    = itsRSPboard;
	rbCmd.address    = itsAddress;
	rbCmd.offset     = itsOffset;
	rbCmd.dataLen    = itsDataLen;
	memcpy(rbCmd.data, itsData, itsDataLen);
	// and send it.
	m_rspport.send(rbCmd);

}

// ack(event)
GCFEvent::TResult RawBlockCommand::ack(GCFEvent& event)
{
	switch (event.signal) {
	case RSP_GETBLOCKACK: {
		RSPGetblockackEvent ack(event);
		LOG_DEBUG(formatString("RAWBLOCKREAD:board=%d, status=%d, dataLen=%d", ack.boardID, ack.status, ack.dataLen));
		if (ack.status != RSP_SUCCESS) {
			cerr << "Error: readBlock command failed, code = " << ack.status << endl;
		}
		else {
			// show result to the user
			hexdump (ack.data, ack.dataLen);
			// TODO write to file
		}
	}
	break;

	case RSP_SETBLOCKACK: {
		RSPSetblockackEvent ack(event);
		LOG_DEBUG(formatString("RAWBLOCKWRITE:board:%d, status=%d", ack.boardID, ack.status));
		if (ack.status != RSP_SUCCESS) {
			cerr << "Error: writeBlock command failed, code = " << ack.status << endl;
		}
	}
	break;

	default:
		cerr << "Unknown answer return while reading or writing a datablock" << endl;
	}

	GCFScheduler::instance()->stop();
	return (GCFEvent::HANDLED);
}

// setAddressInfo(RSPboard, address, offset)
void RawBlockCommand::setAddressInfo(uint16 RSPboard, uint32 address, uint16 offset)
{
	itsRSPboard = RSPboard;
	itsAddress  = address;
	itsOffset   = offset;
}

// setDataInfo(filename, datalen, dataPtr)
void RawBlockCommand::setDataInfo (const string& filename, uint16 dataLen, uint8* dataPtr)
{
	if (filename.empty()) {
		itsDataLen = dataLen > RSP_RAW_BLOCK_SIZE ? RSP_RAW_BLOCK_SIZE : dataLen;
		if (dataPtr) {  // Note: for 'reads' the dataPtr = 0
			memcpy (&itsData[0], dataPtr, dataLen);
			cout << dataLen << " bytes of data in command" << endl;
		}
		return;
	}

	// TODO: add code for using a file
}

// getAddressInfo(RSPboard, address, offset)
void RawBlockCommand::getAddressInfo(uint16* RSPboard, uint32* address, uint16* offset)
{
	*RSPboard = itsRSPboard;
	*address  = itsAddress;
	*offset   = itsOffset;
}

// getDataInfo(filename, datalen, dataPtr)
void RawBlockCommand::getDataInfo(const string& filename, uint16* datalen, uint8** dataHandle)
{
	if (filename.empty()) {
		*datalen    = itsDataLen;
		*dataHandle = &itsData[0];
		return;
	}
	// TODO: add code for using a file
}

//
// Splitter
//
SplitterCommand::SplitterCommand(GCFPortInterface& port) :
	Command(port)
{
}

// send()
void SplitterCommand::send()
{
	// check mode
	if (getMode()) {
		RSPGetsplitterEvent rspEvent;
		rspEvent.timestamp  = Timestamp(0,0);
		m_rspport.send(rspEvent);
		return;
	}

	// construct message
	RSPSetsplitterEvent rspEvent;
	rspEvent.timestamp  = Timestamp(0,0);
	rspEvent.switch_on  = state();

	// and send it.
	m_rspport.send(rspEvent);
}

// ack()
GCFEvent::TResult SplitterCommand::ack(GCFEvent& event)
{
	switch (event.signal) {
	case RSP_SETSPLITTERACK: {
			RSPSetsplitterackEvent ack(event);
			if (ack.status != RSP_SUCCESS) {
				logMessage(cerr,"Error: RSP_SETSPLITTER command failed.");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
			else {
				logMessage(cerr, "Set splitter successful");
			}
		}
		break;

	case RSP_GETSPLITTERACK: {
			RSPGetsplitterackEvent ack(event);
			if (ack.status != RSP_SUCCESS) {
				logMessage(cerr,"Error: RSP_GETSPLITTER command failed.");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
			else {
				for (int rsp = 0; rsp < get_ndevices(); rsp++) {
					logMessage(cerr, formatString("RSP[%2d]: %s", rsp, ack.splitter.test(rsp) ? "ON" : "OFF"));
				}
			}
		}
		break;
	}

	GCFScheduler::instance()->stop();
	return (GCFEvent::HANDLED);
}

//
// Weights
//
WGCommand::WGCommand(GCFPortInterface& port) :
	Command(port),
	m_mode(0),
	m_phase(0),
	itsFrequency(0),
	m_amplitude((uint32)round(AMPLITUDE_SCALE))
{
	LOG_DEBUG_STR("amplitude=" << m_amplitude);
}

void WGCommand::send()
{
	if (getMode()) {
		// GET
		RSPGetwgEvent   wgget;
		wgget.timestamp = Timestamp(0,0);
		wgget.rcumask   = getRCUMask();
		wgget.cache     = true;
		m_rspport.send(wgget);
	}
	else {
		// SET
		RSPSetwgEvent   wgset;
		wgset.timestamp = Timestamp(0,0);
		wgset.rcumask   = getRCUMask();
		wgset.settings().resize(1);

		wgset.settings()(0).freq        = (uint32)round(itsFrequency * ((uint64)1 << 32) / gSampleFrequency);
		wgset.settings()(0).phase       = m_phase;
		wgset.settings()(0).ampl        = m_amplitude;
		wgset.settings()(0).nof_samples = MEPHeader::N_WAVE_SAMPLES;

		if (wgset.settings()(0).freq < 1e-6) {
			wgset.settings()(0).mode = WGSettings::MODE_OFF;
		}
		else  { /* frequency ok */
			if (m_mode == 0) { /* forget to set mode? assume calc mode */
				wgset.settings()(0).mode        = WGSettings::MODE_CALC;
				wgset.settings()(0).nof_samples = MEPHeader::N_WAVE_SAMPLES;
			}
		else {
				wgset.settings()(0).mode        = m_mode;
				wgset.settings()(0).nof_samples = MEPHeader::N_WAVE_SAMPLES;
			}
		}
		wgset.settings()(0).preset = 0; // or one of PRESET_[SINE|SQUARE|TRIANGLE|RAMP]

		m_rspport.send(wgset);
	}
}

GCFEvent::TResult WGCommand::ack(GCFEvent& e)
{
	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
		case RSP_GETWGACK: {
			RSPGetwgackEvent ack(e);

			if (RSP_SUCCESS == ack.status) {

				// print settings
				bitset<MAX_RCUS> mask = getRCUMask();
				int rcuin = 0;
				for (int rcuout = 0; rcuout < get_ndevices(); rcuout++) {

					if (mask[rcuout]) {
						logMessage(cout,formatString("RCU[%02u].wg=[freq=%11u, phase=%3u(%5.3f), ampl=%11u, nof_samples=%6u, mode=%3u]",
										rcuout,
										ack.settings()(rcuin).freq,
										ack.settings()(rcuin).phase,
										(double)ack.settings()(rcuin).phase / 256 * 2 * M_PI,
										ack.settings()(rcuin).ampl,
										ack.settings()(rcuin).nof_samples,
										ack.settings()(rcuin).mode));
						rcuin++;
					}
				}
			}
			else {
				logMessage(cerr,"Error: RSP_GETWG command failed.");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		case RSP_SETWGACK: {
			RSPSetwgackEvent ack(e);

			if (RSP_SUCCESS != ack.status) {
				logMessage(cerr,"Error: RSP_SETWG command failed.");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		}
		break;

		default:
			status = GCFEvent::NOT_HANDLED;
			break;
	}
	LOG_INFO("WGCommand success");

	GCFScheduler::instance()->stop();

	return status;
}

StatusCommand::StatusCommand(GCFPortInterface& port) :
	Command(port),
	m_board()
{
}

void StatusCommand::send()
{
	if (getMode()) { // GET
		RSPGetstatusEvent   getstatus;
		getstatus.timestamp = Timestamp(0,0);
		getstatus.rspmask   = getRSPMask();
		getstatus.cache     = true;

		m_rspport.send(getstatus);
	}
	else { // SET
		logMessage(cerr,"Setting status not yet allowed");
	   	rspctl_exit_code = EXIT_FAILURE;
	}
}

GCFEvent::TResult StatusCommand::ack(GCFEvent& event)
{
	switch (event.signal) {

	case RSP_GETSTATUSACK: {

		RSPGetstatusackEvent ack(event);
		bitset<MAX_N_RSPBOARDS> mask = getRSPMask();

		if (ack.status != RSP_SUCCESS) {
			logMessage(cerr,"Error: RSP_GETSTATUS command failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			break;
		}

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] 1.2 V: %3.2f , 2.5 V: %3.2f, 3.3 V: %3.2f", boardout,
						(2.5/192.0) * board.rsp.voltage_1_2,
						(3.3/192.0) * board.rsp.voltage_2_5,
						(5.0/192.0) * board.rsp.voltage_3_3));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;


		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] PCB_temp: %2d , BP_temp: %2d, "
						"Temp AP0: %3d , AP1: %3d , AP2: %3d , AP3: %3d",
						boardout,
						board.rsp.pcb_temp, board.rsp.bp_temp,
						board.rsp.ap0_temp, board.rsp.ap1_temp,
						board.rsp.ap2_temp, board.rsp.ap3_temp));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] BP_clock: %3d", boardout, board.rsp.bp_clock));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] Ethernet nr frames: %d , nr errors: %d , last error: %d",
						boardout,
						board.eth.nof_frames, board.eth.nof_errors,
						board.eth.last_error));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] MEP sequencenr: %d , error: %d",
						boardout,
						board.mep.seqnr, board.mep.error));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] Errors ri: %5d ,  rcuX: %5d ,  rcuY: %5d,   lcu: %5d,    cep: %5d",
						boardout,
						board.diag.ri_errors, board.diag.rcux_errors,
						board.diag.rcuy_errors, board.diag.lcu_errors,
						board.diag.cep_errors));
			logMessage(cout,formatString("RSP[%2d]    serdes: %5d , ap0ri: %5d , ap1ri: %5d, ap2ri: %5d , ap3ri: %5d",
						boardout,
						board.diag.serdes_errors, board.diag.ap0_ri_errors,
						board.diag.ap1_ri_errors, board.diag.ap2_ri_errors,
						board.diag.ap3_ri_errors));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] Sync         diff      count    samples     slices", boardout));
			for (int blp = 0; blp < 4; blp++) {
				BSStatus* bs= &(board.ap0_sync)+blp;
				logMessage(cout,formatString("RSP[%2d]     %d: %10u %10u %10u %10u",
							boardout, blp, bs->ext_count, bs->sync_count,
							bs->sample_offset, bs->slice_count));
			}
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout,formatString("RSP[%2d] RCUStatus   pllX       pllY  overflowX  overflowY", boardout));
			for (int ap = 0; ap < 4; ap++) {
				RCUStatus* as= &(board.blp0_rcu)+ap;
				logMessage(cout,formatString("RSP[%2d]     %d: %10d %10d %10d %10d",
							boardout, ap, as->pllx, as->plly,
							as->nof_overflowx, as->nof_overflowy));
			}
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		const char* trig[] = {
			"Board Reset",                   // 0x0
			"User reconfiguration request",  // 0x1
			"User reset request",            // 0x2
			"Invalid index",                 // 0x3
			"Watchdog timer timeout"         // 0x4
		};

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout, formatString("RSP[%2d] RSU Status:", boardout));
			logMessage(cout, formatString("RSP[%2d]     Trigger: %s", boardout,
						(board.cp_status.trig <= 0x4 ? trig[board.cp_status.trig] : "Invalid")));
			logMessage(cout, formatString("RSP[%2d]     Image  : %s", boardout,
						(board.cp_status.im ? "Application image" : "Factory image")));
			logMessage(cout, formatString("RSP[%2d]     FPGA   : %s", boardout,
						(board.cp_status.fpga ? "AP was reconfigured" : "BP was reconfigured")));
			logMessage(cout, formatString("RSP[%2d]     Result : %s", boardout,
						(board.cp_status.fpga ? "ERROR" : "OK")));
			logMessage(cout, formatString("RSP[%2d]     Status : %s", boardout,
						(board.cp_status.rdy ? "DONE" : "IN PROGRESS")));
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus& board = ack.sysstatus.board()(boardin);
			logMessage(cout, formatString("RSP[%2d] ADO Status adc_offset_x  adc_offset_y (in LS bits)", boardout));
			for (int ap = 0; ap < 4; ap++) {
				ADOStatus* as= &(board.blp0_adc_offset)+ap;
				BSStatus*  bs= &(board.ap0_sync)+ap;
				logMessage(cout, formatString("RSP[%2d]     %d:         %10d    %10d",
							boardout, ap,
							(bs->slice_count > 0 ? as->adc_offset_x / (int32)bs->slice_count / 4 : 0),
							(bs->slice_count > 0 ? as->adc_offset_y / (int32)bs->slice_count / 4 : 0)));
			}
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

		BOARD_ITERATOR_BEGIN {
			BoardStatus&	board = ack.sysstatus.board()(boardin);
			logMessage(cout, formatString("RSP[%2d] RAD Status        Align    Sync     CRC     Frame cnt", boardout));
			RADStatus* rs = &(board.ri);
			logMessage(cout, formatString("RSP[%2d]              ri:      _   %5s   %5s     %9d",
							boardout,
							(rs->sync ? "OK" : "ERROR"),
							(rs->brc ? "ERROR" : "OK"),
							rs->cnt ));
			for (int ap = 0; ap < 8; ap++) {
				RADStatus* rs = &(board.lane0_crosslet)+ap;
				logMessage(cout, formatString("RSP[%2d] lane%d %9s:  %5s   %5s   %5s     %9d",
							boardout, (ap / 2),
							((ap % 2) == 0 ? "crosslets" : "beamlets"),
							(rs->align == 0 ? "OK" : "ERROR"),
							(rs->sync == 1 ? "OK" : "ERROR"),
							(rs->brc == 0 ? "OK" : "ERROR"),
							rs->cnt ));
			}
            if (gHasAartfaac) {
                for (int ap = 0; ap < 4; ap++) {
                    RADStatus* rs = &(board.lane0_subband)+ap;
                    logMessage(cout, formatString("RSP[%2d] lane%d %9s:  %5s   %5s   %5s     %9d",
                                boardout, ap,
                                "subbands",
                                (rs->align == 0 ? "OK" : "ERROR"),
                                (rs->sync == 1 ? "OK" : "ERROR"),
                                (rs->brc == 0 ? "OK" : "ERROR"),
                                rs->cnt ));
                }
            }
			BOARD_ITERATOR_NEXT;
		} BOARD_ITERATOR_END;

	}
		break;
	}

	GCFScheduler::instance()->stop();
	return GCFEvent::HANDLED;
}

StatisticsBaseCommand::StatisticsBaseCommand(GCFPortInterface& port) : Command(port),
	m_subscriptionhandle(0),
	m_duration(0),
	m_endTime(),
	m_integration(1),
	m_nseconds(0),
	m_directory(""),
	m_file(0)
{
}

StatisticsCommand::StatisticsCommand(GCFPortInterface& port, const int bitsPerSample) : StatisticsBaseCommand(port),
	m_type			(Statistics::SUBBAND_POWER),
	m_stats			(),
	itsBitsPerSample(bitsPerSample)
{
}

void StatisticsCommand::send()
{
	if (getMode()) {
		if(m_directory.length()>0) {
			logMessage(cout,formatString("Dumping statistics in %s",m_directory.c_str()));
		}
		else {
			char cwd[PATH_MAX];
			logMessage(cout,formatString("Dumping statistics in %s",getcwd(cwd,PATH_MAX)));
		}

		// SUBSCRIBE
		RSPSubstatsEvent   substats;
		substats.timestamp = Timestamp(0,0);
		substats.rcumask   = getRCUMask();
		substats.period    = 1;
		substats.type      = m_type;
		substats.reduction = SUM;

		m_rspport.send(substats);
	}
	else {
		// SET
		logMessage(cerr,"Error: set mode not support for option '--statistics'");
	   	rspctl_exit_code = EXIT_FAILURE;
		GCFScheduler::instance()->stop();
	}
}

void StatisticsCommand::stop()
{
	if (getMode()) {
		// UNSUBSCRIBE
		RSPUnsubstatsEvent unsubstats;
		unsubstats.handle  = m_subscriptionhandle;
		m_rspport.send(unsubstats);
	}
}

void StatisticsCommand::capture_statistics(Array<double, 2>& stats, const Timestamp& timestamp)
{
	if (sum(m_stats.shape()) != sum(stats.shape())) {
		gBitmodeChanged = true;
	}

	if (gBitmodeChanged) {		// force start at new cycle
		m_nseconds = 0;
	}

	if (m_nseconds == 0) {
		// initialize values array
		m_stats.resize(stats.shape());
		m_stats = 0.0;
	}
	else {
		if ( sum(stats.shape()) != sum(m_stats.shape()) ) {
			logMessage(cerr, "Error: statistics shape mismatch");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
	}

	if (m_integration > 1) {
		m_stats += stats;
	} else {
		m_stats = stats;
	}
	m_nseconds++; // advance to next second

	if (0 == (int32)m_nseconds % m_integration) {
		if (m_integration > 1) {
			m_stats /= m_integration;
		}

		LOG_DEBUG_STR("statistics update at " << timestamp);

		if (m_duration == 0) {
			//cout << m_stats << endl;
			plot_statistics(m_stats, timestamp);
		}
		else {
			dump_statistics(m_stats, timestamp);

			Timestamp timeNow;
			timeNow.setNow();

			if(m_nseconds >= m_duration) {
				logMessage(cout,"Statistics capturing successfully ended.");
				stop();
				GCFScheduler::instance()->stop();
			}
		}

		m_stats = 0.0; //reset statistics
	}
}

void StatisticsCommand::plot_statistics(Array<double, 2>& stats, const Timestamp& timestamp)
{
	static gnuplot_ctrl* handle = 0;
	static gnuplot_ctrl* handle2 = 0;

	int x_range      = stats.extent(secondDim);
	int n_firstIndex = stats.extent(firstDim);
	bitset<MAX_RCUS> mask = getRCUMask();
	char plotcmd[256];
	int startrcu;
	int stoprcu;

	// initialize the freq array
	//firstIndex i;

#if 0
	if (handle && gClockChanged) {
		gnuplot_close(handle);
		handle = 0;
		if (handle2) {
			gnuplot_close(handle2);
			handle2 = 0;
		}
		gClockChanged = false;
	}
#endif

	if (!handle) {
		handle = gnuplot_init();
		if (!handle) return;

		gnuplot_cmd(handle, "set grid x y\n");
		gnuplot_cmd(handle, "set ylabel \"dB\"\n");
		gnuplot_cmd(handle, "set yrange [0:160]\n");

		switch (m_type) {
			case Statistics::SUBBAND_POWER:
				gnuplot_cmd(handle, "set xlabel \"Frequency (Hz)\"\n");
				gnuplot_cmd(handle, "set xrange [0:%f]\n", gSampleFrequency / 2.0);
				break;
			case Statistics::BEAMLET_POWER:
				gnuplot_cmd(handle, "set xlabel \"Beamlet index\"\n");
				gnuplot_cmd(handle, "set xrange [0:%d]\n", x_range);
				break;
		}
	}


	time_t seconds = timestamp.sec();
	if (gSplitterOn) {
		strftime(plotcmd, 255, "set title \"Ring 0 %s - %a, %d %b %Y %H:%M:%S  %z\"\n", gmtime(&seconds));
	}
	else {
		strftime(plotcmd, 255, "set title \"%s - %a, %d %b %Y %H:%M:%S  %z\"\n", gmtime(&seconds));
	}

	// Redefine xrange when clock changed.
	if (gClockChanged && (m_type == Statistics::SUBBAND_POWER)) {
		gnuplot_cmd(handle, "set xrange [0:%f]\n", gSampleFrequency / 2.0);
	}

	// Redefine xrange when bitmode changed.
	if (gBitmodeChanged && (m_type == Statistics::BEAMLET_POWER)) {
		gnuplot_cmd(handle, "set xrange [0:%d]\n", x_range);
	}

	gnuplot_cmd(handle, plotcmd);

	gnuplot_cmd(handle, "plot ");
	// splot devices
	int count = 0;

	startrcu = 0;
	if (m_type == Statistics::SUBBAND_POWER) {
    	if (gSplitterOn) {
    		stoprcu = get_ndevices() / 2;
    	}
    	else {
    		stoprcu = get_ndevices();
    	}
    }
    else {
        stoprcu = get_ndevices() / 2;
    }

	for (int rcuout = startrcu; rcuout < stoprcu; rcuout++) {
		if (mask[rcuout]) {
			if (count > 0)
				gnuplot_cmd(handle, ",");
			count++;

			switch (m_type) {
				case Statistics::SUBBAND_POWER:
					gnuplot_cmd(handle, "\"-\" using (%.1f/%.1f*$1):(10*log10($2)) title \"(RCU=%d)\" with steps ",
					gSampleFrequency, x_range*2.0, rcuout);
					break;
				case Statistics::BEAMLET_POWER:
					gnuplot_cmd(handle, "\"-\" using (1.0*$1):(10*log10($2)) title \"Beamlet Power (%c)\" with steps ",
					(rcuout%2?'Y':'X'));
					break;
				default:
					logMessage(cerr,"Error: invalid m_type");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
					break;
			}
		}
	}
	//stats = stats + 1; // too show zeros in log10()
	gnuplot_cmd(handle, "\n");
	gnuplot_write_matrix(handle, stats(Range(0, count-1), Range::all()));

	// if splitter is now OFF but the second screen is still shown, remove this window
	if (handle2 && !gSplitterOn) {
		gnuplot_close(handle2);
		handle2=0;
	}

	// if Splitter is active plot another graphics
	if (gSplitterOn) {
		startrcu = get_ndevices() / 2;
		stoprcu = get_ndevices();
        int rcuCount = 0;
		for (int rcuout = startrcu; rcuout < stoprcu; rcuout++) {
			if (mask[rcuout]) {
			    rcuCount++;
			}
		}
		if (rcuCount > 0) {
    		if (!handle2) {
    			handle2 = gnuplot_init();
    			if (!handle2) return;

    			gnuplot_cmd(handle2, "set grid x y\n");
    			gnuplot_cmd(handle2, "set ylabel \"dB\"\n");
    			gnuplot_cmd(handle2, "set yrange [0:160]\n");

    			switch (m_type) {
    				case Statistics::SUBBAND_POWER:
    					gnuplot_cmd(handle2, "set xlabel \"Frequency (Hz)\"\n");
    					gnuplot_cmd(handle2, "set xrange [0:%f]\n", gSampleFrequency / 2.0);
    					break;
    				case Statistics::BEAMLET_POWER:
    					gnuplot_cmd(handle2, "set xlabel \"Beamlet index\"\n");
    					gnuplot_cmd(handle2, "set xrange [0:%d]\n", x_range);
    					break;
    			}
    		}

    		time_t seconds = timestamp.sec();
    		strftime(plotcmd, 255, "set title \"Ring 1 %s - %a, %d %b %Y %H:%M:%S  %z\"\n", gmtime(&seconds));

    		// Redefine xrange when clock changed.
    		if (gClockChanged && (m_type == Statistics::SUBBAND_POWER)) {
    			gnuplot_cmd(handle2, "set xrange [0:%f]\n", gSampleFrequency / 2.0);
    		}

    		// Redefine xrange when bitmode changed.
    		if (gBitmodeChanged && (m_type == Statistics::BEAMLET_POWER)) {
    			gnuplot_cmd(handle2, "set xrange [0:%d]\n", x_range);
    		}

    		gnuplot_cmd(handle2, plotcmd);

    		gnuplot_cmd(handle2, "plot ");
    		// splot devices
    		int count = 0;

    		startrcu = get_ndevices() / 2;
    		stoprcu = get_ndevices();

    		for (int rcuout = startrcu; rcuout < stoprcu; rcuout++) {
    			if (mask[rcuout]) {
    				if (count > 0)
    					gnuplot_cmd(handle2, ",");
    				count++;

    				switch (m_type) {
    					case Statistics::SUBBAND_POWER:
    						gnuplot_cmd(handle2, "\"-\" using (%.1f/%.1f*$1):(10*log10($2)) title \"(RCU=%d)\" with steps ",
    						gSampleFrequency, x_range*2.0, rcuout);
    						break;
    					case Statistics::BEAMLET_POWER:
    						gnuplot_cmd(handle2, "\"-\" using (1.0*$1):(10*log10($2)) title \"Beamlet Power (%c)\" with steps ",
    						(rcuout%2?'Y':'X'));
    						break;
    					default:
    						logMessage(cerr,"Error: invalid m_type");
	   						rspctl_exit_code = EXIT_FAILURE;
    						exit(EXIT_FAILURE);
    						break;
    				}
    			}
    		}
    		gnuplot_cmd(handle2, "\n");
  		    gnuplot_write_matrix(handle2, stats(Range((n_firstIndex/2),(n_firstIndex/2)+count-1), Range::all()));
    	}
	}
}

void StatisticsCommand::dump_statistics(Array<double, 2>& stats, const Timestamp& timestamp)
{
	bitset<MAX_RCUS> mask = getRCUMask();

	int result_device=0;
	for (int deviceout = 0; deviceout < get_ndevices(); deviceout++) {
		if (mask[deviceout]) {
			char timestring[256];
			time_t seconds = timestamp.sec();
			strftime(timestring, 255, "%Y%m%d_%H%M%S", gmtime(&seconds));
			char fileName[PATH_MAX];

			LOG_INFO_STR("dumping statistics at " << timestring);

			switch (m_type) {
				case Statistics::SUBBAND_POWER:
					snprintf(fileName, PATH_MAX, "%s%s_sst_rcu%03d.dat", m_directory.c_str(), timestring, deviceout);
					break;
				case Statistics::BEAMLET_POWER:
					snprintf(fileName, PATH_MAX, "%s%s_bst_%02d%s.dat", m_directory.c_str(), timestring, deviceout/2, deviceout%2?"Y":"X");
					break;

				default:
					logMessage(cerr,"Error: invalid m_type");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
					break;
			}

			cerr << "shape(stats)=" << stats(result_device, Range::all()).shape() << endl;

			FILE* file = getFile(deviceout,fileName);
			if (stats.extent(secondDim)
					!= (int)fwrite(stats(result_device, Range::all()).data(), sizeof(double), stats.extent(secondDim), file)) {
				logMessage(cerr,formatString("Error: unable to write to file %s",fileName));
	   			rspctl_exit_code = EXIT_FAILURE;
				exit(EXIT_FAILURE);
			}
			result_device++;
		}
	}
}

GCFEvent::TResult StatisticsCommand::ack(GCFEvent& e)
{
	if (e.signal == RSP_SUBSTATSACK) {
		RSPSubstatsackEvent ack(e);

		if (RSP_SUCCESS != ack.status) {
			logMessage(cerr,"Error: failed to subscribe to statistics");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}

		return GCFEvent::HANDLED;
	}

	if (e.signal != RSP_UPDSTATS)
		return GCFEvent::NOT_HANDLED;

	RSPUpdstatsEvent upd(e);

	if (RSP_SUCCESS == upd.status) {
		capture_statistics(upd.stats(),upd.timestamp);
	}
	else {
		logMessage(cerr,"Error: statistics update failed.");
	   	rspctl_exit_code = EXIT_FAILURE;
	}

	return GCFEvent::HANDLED;
}

XCStatisticsCommand::XCStatisticsCommand(GCFPortInterface& port) : StatisticsBaseCommand(port),
										m_stats(), m_xcangle(false)
{
}

void XCStatisticsCommand::send()
{
	if (getMode()) {
		if(m_directory.length()>0) {
			logMessage(cout,formatString("Dumping statistics in %s",m_directory.c_str()));
		}
		else {
			char cwd[PATH_MAX];
			logMessage(cout,formatString("Dumping statistics in %s",getcwd(cwd,PATH_MAX)));
		}

		// SUBSCRIBE
		RSPSubxcstatsEvent subxcstats;

		subxcstats.timestamp = Timestamp(0,0);

		// increase update period when dumping to screen (gnuplot), otherwise gnuplot can't keep up
		// period != 1 breaks integration, but we accept that for gnuplot output
		subxcstats.period = (m_duration == 0 ? 4 : 1);

		m_rspport.send(subxcstats);
	}
	else {
		// SET
		logMessage(cerr,"Error: set mode not support for option '--xcstatistics'");
	   	rspctl_exit_code = EXIT_FAILURE;
		GCFScheduler::instance()->stop();
	}
}

void XCStatisticsCommand::stop()
{
	if (getMode()) {
		// UNSUBSCRIBE
		RSPUnsubxcstatsEvent unsubxcstats;
		unsubxcstats.handle = m_subscriptionhandle;
		m_rspport.send(unsubxcstats);
	}
}

void XCStatisticsCommand::capture_xcstatistics(Array<complex<double>, 4>& stats, const Timestamp& timestamp){

	if (0 == m_nseconds) {
		// initialize values array
		m_stats.resize(stats.shape());
		m_stats = 0.0;
	}
	else {
		if ( sum(stats.shape()) != sum(m_stats.shape()) ) {
			logMessage(cerr, "Error: xcstatistics shape mismatch");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
	}

	if (m_integration > 0) {
		m_stats += stats;
	} else {
		m_stats = stats;
	}
	m_nseconds++; // advance to next second

	if (0 == (int32)m_nseconds % m_integration) {
		if (m_integration > 0) {
			m_stats /= m_integration;
		}

		LOG_DEBUG_STR("xcstatistics update at " << timestamp);

		if(m_duration == 0) {
			plot_xcstatistics(m_stats, timestamp);
		}
		else {
			dump_xcstatistics(m_stats, timestamp);

			Timestamp timeNow;
			timeNow.setNow();
			if(timeNow >= m_endTime) {
				logMessage(cout,"XCStatistics capturing successfully ended.");
				stop();
				GCFScheduler::instance()->stop();
			}
		}

		m_stats = 0.0; //reset statistics
	}
}

void XCStatisticsCommand::plot_xcstatistics(Array<complex<double>, 4>& xcstats, const Timestamp& timestamp)
{
	static gnuplot_ctrl* handle = 0;

	Array<double, 2> thestats;
	thestats.resize(xcstats.extent(firstDim) * xcstats.extent(thirdDim), xcstats.extent(secondDim) * xcstats.extent(fourthDim));

	blitz::Array<complex<double>, 4> apstats;
	apstats.resize(m_stats.shape());
	apstats = convert_to_amplphase(m_stats);


	if (!m_xcangle) {
		for (int i = 0; i < thestats.extent(firstDim); i++) {
			for (int j = 0; j < thestats.extent(secondDim); j++) {
				thestats(i,j) = apstats(i % 2, j % 2, i/2, j/2).real();
			}
		}
	}
	else {
		for (int i = 0; i < thestats.extent(firstDim); i++) {
			for (int j = 0; j < thestats.extent(secondDim); j++) {
				thestats(i,j) = apstats(i % 2, j % 2, i/2, j/2).imag();
			}
		}
	}

	int n_ant = thestats.extent(firstDim);

	if (!handle) {
		handle = gnuplot_init();
		if (!handle)
			return;
	}

	char plotcmd[256];
	time_t seconds = timestamp.sec();
	strftime(plotcmd, 255, "set title \"%s - %a, %d %b %Y %H:%M:%S  %z\"\n", gmtime(&seconds));

	gnuplot_cmd(handle, plotcmd);

	gnuplot_cmd(handle, "plot \"-\" binary array=%dx%d format='%%double' with image\n", n_ant, n_ant);

    // already log taken in convert_to_amplphase function
	//if (!m_xcangle) {
	//	thestats = 10.0*log(thestats)/log(10.0);
	//}

	if (thestats.size() != fwrite(thestats.data(), sizeof(double), thestats.size(), handle->gnucmd)) {
		logMessage(cerr, "Failed to write to gnuplot.");
	   	rspctl_exit_code = EXIT_FAILURE;
	}
}

void XCStatisticsCommand::dump_xcstatistics(Array<complex<double>, 4>& stats, const Timestamp& timestamp)
{
	Array<complex<double>, 2> thestats;

	thestats.resize(stats.extent(firstDim) * stats.extent(thirdDim),
			stats.extent(secondDim) * stats.extent(fourthDim));

	for (int i = 0; i < thestats.extent(firstDim); i++) {
		for (int j = 0; j < thestats.extent(secondDim); j++) {
			thestats(i,j) = stats(i % 2, j % 2, i/2, j/2);
		}
	}

	char timestring[256];
	time_t seconds = timestamp.sec();
	strftime(timestring, 255, "%Y%m%d_%H%M%S", gmtime(&seconds));
	char fileName[PATH_MAX];
	snprintf(fileName, PATH_MAX, "%s%s_xst.dat", m_directory.c_str(), timestring);
	FILE* file = getFile(0,fileName);

	if (thestats.size()
			!= fwrite(thestats.data(), sizeof(complex<double>),
					thestats.size(), file)) {
		logMessage(cerr,formatString("Error: unable to write to file %s",fileName));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
}

GCFEvent::TResult XCStatisticsCommand::ack(GCFEvent& e)
{
	if (e.signal == RSP_SUBXCSTATSACK) {
		RSPSubxcstatsackEvent ack(e);

		if (RSP_SUCCESS != ack.status) {
			logMessage(cerr,"Error: failed to subscribe to xcstatistics");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		else {
			m_subscriptionhandle = ack.handle;
		}

		return GCFEvent::HANDLED;
	}

	if (e.signal != RSP_UPDXCSTATS)
		return GCFEvent::NOT_HANDLED;

	RSPUpdxcstatsEvent upd(e);

	if (RSP_SUCCESS == upd.status) {
#if 0
		Range r1, r2;
		if (!getRSPRange2(r1, r2)) {
			logMessage(cerr, "Error: RSP range selection must have exactly 4 numbers");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		Array<complex<double>, 4> selection = upd.stats()(Range::all(), Range::all(), r1, r2).copy();
		capture_xcstatistics(selection, upd.timestamp);
#else
		capture_xcstatistics(upd.stats(), upd.timestamp);
#endif
	}

	return GCFEvent::HANDLED;
}

VersionCommand::VersionCommand(GCFPortInterface& port) : Command(port)
{
}

void VersionCommand::send()
{
	RSPGetversionEvent getversion;

	getversion.timestamp = Timestamp(0,0);
	getversion.cache = true;

	m_rspport.send(getversion);
}

GCFEvent::TResult VersionCommand::ack(GCFEvent& e)
{
	RSPGetversionackEvent ack(e);

	if (RSP_SUCCESS == ack.status) {
		for (int rsp=0; rsp < get_ndevices(); rsp++) {
			logMessage(cout,formatString("RSP[%2d] RSP version = %d, BP version = %d.%d, AP version = %d.%d",
						rsp,
						ack.versions.bp()(rsp).rsp_version,
						ack.versions.bp()(rsp).fpga_maj,
						ack.versions.bp()(rsp).fpga_min,
						ack.versions.ap()(rsp).fpga_maj,
						ack.versions.ap()(rsp).fpga_min));
		}
	}
	else {
		logMessage(cerr,"Error: RSP_GETVERSION command failed.");
	   	rspctl_exit_code = EXIT_FAILURE;
	}
	GCFScheduler::instance()->stop();

	return GCFEvent::HANDLED;
}

// show latency of the ring and all lanes
LatencyCommand::LatencyCommand(GCFPortInterface& port) : Command(port)
{
}

void LatencyCommand::send()
{
	RSPGetlatencyEvent getlatency;

	getlatency.timestamp = Timestamp(0,0);
	getlatency.cache = true;

	m_rspport.send(getlatency);
}

GCFEvent::TResult LatencyCommand::ack(GCFEvent& e)
{
	RSPGetlatencyackEvent ack(e);

	if (RSP_SUCCESS == ack.status) {
		logMessage(cout,"                Ring   Xlet3  Xlet2  Xlet1  Xlet0  Blet3  Blet2  Blet1  Blet0");
		for (int rsp=0; rsp < get_ndevices(); rsp++) {
			logMessage(cout,formatString("RSP[%2d] latency %5d  %5d  %5d  %5d  %5d  %5d  %5d  %5d  %5d",
										rsp,
										ack.latencys()(rsp).ring,
										ack.latencys()(rsp).crosslet_lane3,
										ack.latencys()(rsp).crosslet_lane2,
										ack.latencys()(rsp).crosslet_lane1,
										ack.latencys()(rsp).crosslet_lane0,
										ack.latencys()(rsp).beamlet_lane3,
										ack.latencys()(rsp).beamlet_lane2,
										ack.latencys()(rsp).beamlet_lane1,
										ack.latencys()(rsp).beamlet_lane0 ));
		}
	}
	else {
		logMessage(cerr,"Error: RSP_GETLATENCY command failed.");
	   	rspctl_exit_code = EXIT_FAILURE;
	}
	GCFScheduler::instance()->stop();

	return GCFEvent::HANDLED;
}

TestableRSPCtl::TestableRSPCtl(string name, int argc, char** argv) :
    RSPCtl(name, argc, argv),
	m_argc           (argc),
	m_argv           (argv)
{
}

TestableRSPCtl::~TestableRSPCtl()
{
}

Command* TestableRSPCtl::getCommand()
{
    return parse_options(m_argc, m_argv);
}

//
// RSPCtl()
//
RSPCtl::RSPCtl(string name, int argc, char** argv) :
	GCFTask((State)&RSPCtl::initial, name),
	itsCommand       (0),
	m_nrcus          (0),
	m_nrspboards     (0),
	itsNantennas     (0),
	itsNbitsPerSample(MAX_BITS_PER_SAMPLE),
	m_argc           (argc),
	m_argv           (argv),
	m_instancenr     (-1),
	itsNeedClockOnce (false),
	itsNeedClock     (false),
	itsNeedSplitter  (false),
	m_subclock       (*itsRSPDriver)
{
	registerProtocol(RSP_PROTOCOL, RSP_PROTOCOL_STRINGS);

	itsRSPDriver = new GCFTCPPort(*this, MAC_SVCMASK_RSPDRIVER, GCFPortInterface::SAP, RSP_PROTOCOL);
	ASSERTSTR(itsRSPDriver, "Cannot allocate port to RSPDriver");
}

//
// ~RSPCtl()
//
RSPCtl::~RSPCtl()
{
	if (itsCommand)
		delete itsCommand;
}

int RSPCtl::getExitCode()
{
	return rspctl_exit_code;
}

//
// initial(event, port)
//
GCFEvent::TResult RSPCtl::initial(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("initial:" << eventName(e) << "@" << port.getName());

	switch(e.signal) {
	case F_INIT:
	break;

	case F_ENTRY: {
		if (m_argc == 1) {
			usage(false);
			exit(EXIT_FAILURE);
		}

		// setup a connection with the RSPDriver
		if (!itsRSPDriver->isConnected()) {
			itsRSPDriver->autoOpen(3,0,1); // try 3 times at 1 second interval
		}
	}
	break;

	case F_DISCONNECTED: {
		LOG_DEBUG_STR("Cannot connect to the RSPDriver. Is it running?");
		GCFScheduler::instance()->stop();
	}
	break;

	case F_CONNECTED: {
		// get the number of rcu's and RSP's because we need that for some commands.
		if (itsRSPDriver->isConnected()) {
			RSPGetconfigEvent getconfig;
			itsRSPDriver->send(getconfig);
		}
	}
	break;

	case RSP_GETCONFIGACK: {
		RSPGetconfigackEvent ack(e);
		m_nrcus        = ack.n_rcus;
		itsNantennas   = ack.n_rcus / N_POL;
		m_nrspboards   = ack.n_rspboards;
		m_maxrspboards = ack.max_rspboards;
		gHasSplitter   = ack.hasSplitter;
		gHasAartfaac   = ack.hasAartfaac;
		LOG_DEBUG_STR(formatString("n_rcus     =%d",m_nrcus));
		LOG_DEBUG_STR(formatString("n_rspboards=%d of %d",  m_nrspboards, m_maxrspboards));
		RSPGetbitmodeEvent	getBitmode;
		itsRSPDriver->send(getBitmode);
	}
	break;

	case RSP_GETBITMODEACK: {
		RSPGetbitmodeackEvent	ack(e);
		// bitmode can be configured per RSPboard (although never used). Use highest value of the boards
		// because that is supported by all.
		itsNbitsPerSample = MIN_BITS_PER_SAMPLE;
		for (int i = 0; i < m_nrspboards; i++) {
			itsNbitsPerSample = (ack.bits_per_sample[i] > itsNbitsPerSample) ? ack.bits_per_sample[i] : itsNbitsPerSample;
		}
		LOG_DEBUG_STR(formatString("bits/sample=%d",  itsNbitsPerSample));

		// connected to RSPDriver, parse the arguments
		if (!(itsCommand = parse_options(m_argc, m_argv))) {
			logMessage(cerr,"Warning: no command specified.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		if (itsNeedClockOnce) {
			TRAN(RSPCtl::getClock);
		}
		else if (itsNeedClock) {
			TRAN(RSPCtl::sub2Clock);
		}
		else if (itsNeedSplitter) {
			TRAN(RSPCtl::sub2Splitter);
		}
		else {
			TRAN(RSPCtl::doCommand);
		}
	}
	break;

	default:
		return(GCFEvent::NOT_HANDLED);
	}

	return (GCFEvent::HANDLED);
}

//
// getClock(event, port)
//
GCFEvent::TResult RSPCtl::getClock(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("getClock:" << eventName(e) << "@" << port.getName());

	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case F_ENTRY: {
		logMessage(cerr, "Getting the clockvalue");
		RSPGetclockEvent getEvent;
		getEvent.timestamp = Timestamp(0,0);
		itsRSPDriver->send(getEvent);
	}
	break;

	case RSP_GETCLOCKACK: {
		RSPGetclockackEvent  answer(e);
		if (answer.status != RSP_SUCCESS) {
			logMessage(cerr, "Getting the clock failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		logMessage(cerr, formatString("Current clockvalue is %d Mhz", answer.clock));
		gSampleFrequency = 1.0e6 * answer.clock;

		if (itsNeedSplitter) {
			TRAN(RSPCtl::sub2Splitter);
		}
		else if (itsNeedBitmode) {
			TRAN(RSPCtl::sub2Bitmode);
		}
		else {
			TRAN(RSPCtl::doCommand);
		}
	}
	break;

	case F_DISCONNECTED: {
		port.close();
		logMessage(cerr,formatString("Error: port '%s' disconnected.",port.getName().c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	return status;
}


//
// sub2Clock(event, port)
//
GCFEvent::TResult RSPCtl::sub2Clock(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("sub2Clock:" << eventName(e) << "@" << port.getName());

	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case F_ENTRY: {
		logMessage(cerr, "Taking subscription on the clockvalue");
		RSPSubclockEvent subEvent;
		subEvent.timestamp = Timestamp(0,0);
		subEvent.period = 1; // check for change every second
		itsRSPDriver->send(subEvent);
		// after receiving the clock update execute the actual requested command
	}
	break;

	case RSP_SUBCLOCKACK: {
		RSPSubclockackEvent  answer(e);
		if (answer.status != RSP_SUCCESS) {
			logMessage(cerr, "Subscription on the clock failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
	}
	break;

	case RSP_UPDCLOCK: {
		RSPUpdclockEvent  answer(e);
		gSampleFrequency = 1.0e6 * answer.clock;
		logMessage(cerr, formatString("Current clockvalue is %d Mhz", answer.clock));

		if (itsNeedSplitter) {
			TRAN(RSPCtl::sub2Splitter);
		}
		else if (itsNeedBitmode) {
			TRAN(RSPCtl::sub2Bitmode);
		}
		else {
			TRAN(RSPCtl::doCommand);
		}
	}
	break;

	case F_DISCONNECTED: {
		port.close();
		logMessage(cerr,formatString("Error: port '%s' disconnected.",port.getName().c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	return status;
}

//
// sub2Splitter(event, port)
//
GCFEvent::TResult RSPCtl::sub2Splitter(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("sub2Splitter:" << eventName(e) << "@" << port.getName());

	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case F_ENTRY: {
		logMessage(cerr, "Taking subscription on the state of the splitter");
		RSPSubsplitterEvent subEvent;
		subEvent.timestamp = Timestamp(0,0);
		subEvent.period = 1; // check for change every second
		itsRSPDriver->send(subEvent);
	}
	break;

	case RSP_SUBSPLITTERACK: {
		RSPSubsplitterackEvent answer(e);
		if (answer.status != RSP_SUCCESS) {
			logMessage(cerr, "Subscription on the splitter-state failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		// wait for update event
	}
	break;

	case RSP_UPDSPLITTER: {
		RSPUpdsplitterEvent  updateEvent(e);
		gSplitterOn = updateEvent.splitter[0];
		logMessage(cerr, formatString("The splitter is currently %s", gSplitterOn ? "ON" : "OFF"));
		if (itsNeedBitmode) {
			TRAN(RSPCtl::sub2Bitmode);
		}
		else {
			TRAN(RSPCtl::doCommand);
		}
	}
	break;

	case F_DISCONNECTED: {
		port.close();
		logMessage(cerr,formatString("Error: port '%s' disconnected.",port.getName().c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	return status;
}

//
// sub2Bitmode(event, port)
//
GCFEvent::TResult RSPCtl::sub2Bitmode(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("sub2Bitmode:" << eventName(e) << "@" << port.getName());

	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case F_ENTRY: {
		logMessage(cerr, "Taking subscription on the bitmode");
		RSPSubbitmodeEvent subEvent;
		subEvent.timestamp = Timestamp(0,0);
		subEvent.period = 1; // check for change every second
		itsRSPDriver->send(subEvent);
	}
	break;

	case RSP_SUBBITMODEACK: {
		RSPSubbitmodeackEvent answer(e);
		if (answer.status != RSP_SUCCESS) {
			logMessage(cerr, "Subscription on the bitmode failed.");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		}
		// wait for update event
	}
	break;

	case RSP_UPDBITMODE: {
		RSPUpdbitmodeEvent  update(e);
		itsNbitsPerSample = MIN_BITS_PER_SAMPLE;
		for (int i = 0; i < m_nrspboards; i++) {
			itsNbitsPerSample = (update.bits_per_sample[i] > itsNbitsPerSample) ?
								 update.bits_per_sample[i] : itsNbitsPerSample;
		}
		logMessage(cerr, formatString("The bitmode is currently %d", itsNbitsPerSample));
		TRAN(RSPCtl::doCommand);
	}
	break;

	case F_DISCONNECTED: {
		port.close();
		logMessage(cerr,formatString("Error: port '%s' disconnected.",port.getName().c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	break;

	default:
		status = GCFEvent::NOT_HANDLED;
		break;
	}

	return status;
}

//
// doCommand(event, port)
//
GCFEvent::TResult RSPCtl::doCommand(GCFEvent& e, GCFPortInterface& port)
{
	LOG_DEBUG_STR ("doCommand:" << eventName(e) << "@" << port.getName());

	GCFEvent::TResult status = GCFEvent::HANDLED;

	switch (e.signal) {
	case F_ENTRY: {
		itsCommand->send();
	}
	break;

	case F_DISCONNECTED: {
		port.close();
		logMessage(cerr,formatString("Error: port '%s' disconnected.",port.getName().c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		exit(EXIT_FAILURE);
	}
	break;

	case RSP_GETRCUACK:
	case RSP_SETRCUACK:
	case RSP_SETRSUACK:
	case RSP_GETSTATSACK:
	case RSP_SUBSTATSACK:
	case RSP_UPDSTATS:
	case RSP_SUBXCSTATSACK:
	case RSP_UPDXCSTATS:
	case RSP_GETVERSIONACK:
	case RSP_GETSUBBANDSACK:
	case RSP_SETSUBBANDSACK:
	case RSP_SETWEIGHTSACK:
	case RSP_GETWEIGHTSACK:
	case RSP_GETWGACK:
	case RSP_SETWGACK:
	case RSP_SETCLOCKACK:
	case RSP_GETSTATUSACK:
	case RSP_GETTDSTATUSACK:
	case RSP_SUBREGISTERSTATEACK:
	case RSP_UPDREGISTERSTATE:
	case RSP_SETHBAACK:
	case RSP_GETHBAACK:
	case RSP_READHBAACK:
	case RSP_SETTBBACK:
	case RSP_GETTBBACK:
	case RSP_GETBYPASSACK:
	case RSP_SETBYPASSACK:
	case RSP_GETSPUSTATUSACK:
	case RSP_GETBLOCKACK:
	case RSP_SETBLOCKACK:
	case RSP_SETSPLITTERACK:
	case RSP_GETSPLITTERACK:
	case RSP_GETCLOCKACK:
	case RSP_GETLATENCYACK:
	case RSP_SETDATASTREAMACK:
	case RSP_GETDATASTREAMACK:
	case RSP_SETSWAPXYACK:
	case RSP_GETSWAPXYACK:
	case RSP_SETBITMODEACK:
	case RSP_GETBITMODEACK:
    case RSP_SETSDOMODEACK:
	case RSP_GETSDOMODEACK:
    case RSP_SETSDOACK:
	case RSP_GETSDOACK:

		status = itsCommand->ack(e); // handle the acknowledgement
		gClockChanged = false;
		gBitmodeChanged = false;
		gSplitterChanged = false;
	break;

	case RSP_UPDCLOCK: {
		RSPUpdclockEvent  answer(e);
		gSampleFrequency = 1.0e6 * answer.clock;
		gClockChanged = true;
		logMessage(cerr, formatString("NOTE: The clockvalue changed to %d Mhz", answer.clock));
	}
	break;

	case RSP_UPDSPLITTER: {
		RSPUpdsplitterEvent  updateEvent(e);
		gSplitterOn = updateEvent.splitter[0];
		gSplitterChanged = true;
		logMessage(cerr, formatString("NOTE: The splitter switched to %s", gSplitterOn ? "ON" : "OFF"));
	}
	break;

	case RSP_UPDBITMODE: {
		RSPUpdbitmodeEvent  update(e);
		itsNbitsPerSample = MIN_BITS_PER_SAMPLE;
		for (int i = 0; i < m_nrspboards; i++) {
			itsNbitsPerSample = (update.bits_per_sample[i] > itsNbitsPerSample) ?
								 update.bits_per_sample[i] : itsNbitsPerSample;
		}
		gBitmodeChanged = true;
		logMessage(cerr, formatString("NOTE: The bitmode switched to %d", itsNbitsPerSample));
	}
	break;

	default:
		logMessage(cerr,formatString("Error: unhandled event %s.", eventName(e).c_str()));
	   	rspctl_exit_code = EXIT_FAILURE;
		GCFScheduler::instance()->stop();
		break;
	}

	return status;
}

//
// usage()
//
static void usage(bool exportMode)
{
	cout << "rspctl usage:" << endl;
	cout << endl;
	cout << "--- RCU control ----------------------------------------------------------------------------------------------" << endl;
	cout << "rspctl --rcu                        [--select=<set>]  # show current rcu control setting" << endl;
	cout << "rspctl --rcu=0x00000000             [--select=<set>]  # set the rcu control registers" << endl;
	cout << "  mask       value    " << endl;
	cout << "  0x0000007F INPUT_DELAY  Sample delay for the data from the RCU." << endl;
	cout << "  0x00000080 INPUT_ENABLE Enable RCU input." << endl;
	cout << endl;
	cout << "  0x00000100 LBL-EN       supply LBL antenna on (1) or off (0)" << endl;
	cout << "  0x00000200 LBH-EN       sypply LBH antenna on (1) or off (0)" << endl;
	cout << "  0x00000400 HB-EN        supply HB on (1) or off (0)" << endl;
	cout << "  0x00000800 BANDSEL      low band (1) or high band (0)" << endl;
	cout << "  0x00001000 HB-SEL-0     HBA filter selection" << endl;
	cout << "  0x00002000 HB-SEL-1     HBA filter selection" << endl;
	cout << "                Options : HBA-SEL-0 HBA-SEL-1 Function" << endl;
	cout << "                            0          0      210-270 MHz" << endl;
	cout << "                            0          1      170-230 MHz" << endl;
	cout << "                            1          0      110-190 MHz" << endl;
	cout << "                            1          1      all off" << endl;
	cout << "  0x00004000 VL-EN        low band supply on (1) or off (0)" << endl;
	cout << "  0x00008000 VH-EN        high band supply on (1) or off (0)" << endl;
	cout << endl;
	cout << "  0x00010000 VDIG-EN      ADC supply on (1) or off (0)" << endl;
	cout << "  0x00020000 LBL-LBH-SEL  LB input selection 0=LBL, 1=LBH" << endl;
	cout << "  0x00040000 LB-FILTER    LB filter selection" << endl;
	cout << "                           0    10-90 MHz" << endl;
	cout << "                           1    30-80 MHz" << endl;
	cout << "  0x00080000 ATT-CNT-4    on (1) is  1dB attenuation" << endl;
	cout << "  0x00100000 ATT-CNT-3    on (1) is  2dB attenuation" << endl;
	cout << "  0x00200000 ATT-CNT-2    on (1) is  4dB attenuation" << endl;
	cout << "  0x00300000 ATT-CNT-1    on (1) is  8dB attenuation" << endl;
	cout << "  0x00800000 ATT-CNT-0    on (1) is 16dB attenuation" << endl;
	cout << endl;
	cout << "  0x01000000 PRSG         pseudo random sequence generator on (1), off (0)" << endl;
	cout << "  0x02000000 RESET        on (1) hold board in reset" << endl;
	cout << "  0x04000000 SPEC_INV     Enable spectral inversion (1) if needed. see --specinv" << endl;
	cout << "  0x08000000 TBD          reserved" << endl;
	cout << "  0xF0000000 RCU VERSION  RCU version, read-only" << endl;
	cout << endl;
	cout << "rspctl [ --rcumode        |" << endl;
	cout << "         --rcuprsg        |" << endl;
	cout << "         --rcureset       |" << endl;
	cout << "         --rcuattenuation |" << endl;
	cout << "         --rcudelay       |" << endl;
	cout << "         --rcuenable      |" << endl;
	cout << "       ]+ [--select=<set>] # control RCU by combining one or more of these options with RCU selection" << endl;
	cout << endl;
	cout << "       --rcumode=[0..7] # set the RCU in a specific mode" << endl;
	cout << "         Possible values: 0 = OFF" << endl;
	cout << "                          1 = LBL 10MHz HPF 0x00017900" << endl;
	cout << "                          2 = LBL 30MHz HPF 0x00057900" << endl;
	cout << "                          3 = LBH 10MHz HPF 0x00037A00" << endl;
	cout << "                          4 = LBH 30MHz HPF 0x00077A00" << endl;
	cout << "                          5 = HB 110-190MHz 0x0007A400" << endl;
	cout << "                          6 = HB 170-230MHz 0x00079400" << endl;
	cout << "                          7 = HB 210-270MHz 0x00078400" << endl;
	cout << "       --rcuprsg[=0]             # turn psrg on (or off)" << endl;
	cout << "       --rcureset[=0]            # hold rcu in reset (or take out of reset)" << endl;
	cout << "       --rcuattenuation=[0..31]  # set the RCU attenuation (steps of 0.25dB)" << endl;
	cout << "       --rcudelay=[0..127]       # set the delay for rcu's (steps of 5ns or 6.25ns)" << endl;
	cout << "       --rcuenable[=0]           # enable (or disable) input from RCU's" << endl;
	cout << endl;
	cout << "rspctl --specinv[=0] [--select=<set>] # enable (or disable) spectral inversion" << endl;

    cout << "rspctl --mode=[0..7] [--select=<set>] # set rcumode in a specific mode" << endl;
    cout << "                                      # enable(or disable) input from RCU's" << endl;
    cout << "                                      # enable(or disable) spectral inversion" << endl;
    cout << "                                      # set the hbadelays to 253" << endl;

	cout << endl;
	cout << "--- Signalprocessing -----------------------------------------------------------------------------------------" << endl;
	cout << "rspctl --weights                    [--select=<set>]  # get weights as complex values" << endl;
	cout << "  Example --weights --select=1,2,4:7 or --select=1:3,5:7" << endl;
	cout << "rspctl --weights=value.re[,value.im][--select=<set>][--beamlets=<set>] # set weights as complex value" << endl;
	cout << "OR     --weights=\"(value.re,value.im)(value.re,value.im)\" [--select=<set>][--beamlets=<set>] # set multiple weights" << endl;
    cout << "   as complex value for the same amount of selected beamlets" << endl;
	cout << "rspctl --aweights                   [--select=<set>]  # get weights as power and angle (in degrees)" << endl;
	cout << "rspctl --aweights=amplitude[,angle] [--select=<set>]  # set weights as amplitude and angle (in degrees)" << endl;
	cout << "rspctl --subbands                   [--select=<set>]  # get subband selection" << endl;
	cout << "rspctl --subbands=<set>             [--select=<set>]  # set subband selection" << endl;
	cout << "  Example --subbands sets: --subbands=0:39 or --select=0:19,40:59" << endl;
	cout << "rspctl --xcsubband                                    # get the subband selection for cross correlation" << endl;
	cout << "rspctl --xcsubband=<int>                              # set the subband to cross correlate" << endl;
	cout << "rspctl --wg                         [--select=<set>]  # get waveform generator settings" << endl;
	cout << "rspctl --wg=freq [--phase=..] [--amplitude=..] [--select=<set>]  # set waveform generator settings" << endl;
	cout << endl;
	cout << "--- Status info ----------------------------------------------------------------------------------------------" << endl;
	cout << "rspctl --version             [--select=<set>]  # get version information" << endl;
	cout << "rspctl --status              [--select=<set>]  # get status of RSP boards" << endl;
	cout << "rspctl --tdstatus            [--select=<set>]  # get status of TDS boards" << endl;
	cout << "rspctl --spustatus           [--select=<set>]  # get status of SPU board" << endl;
	cout << "rspctl --realdelays[=<list>] [--select=<set>]  # get the installed 16 delays of one or more HBA's" << endl;
	cout << "rspctl --regstate                              # show update status of all registers once every second" << endl;
	cout << "rspctl --latency                               # show latency of ring and all lanes" << endl;
	cout << endl;
	cout << "--- Statistics -----------------------------------------------------------------------------------------------" << endl;
	cout << "rspctl --statistics[=(subband|beamlet)]        # get subband (default) or beamlet statistics" << endl;
	cout << "             [--select=<set>]                  #" << endl;
	cout << "             [--duration=<seconds>]            #" << endl;
	cout << "             [--integration=<seconds>]         #" << endl;
	cout << "             [--directory=<directory>]         #" << endl;
	cout << "rspctl [--xcangle] --xcstatistics  [--select=first,second] # get crosscorrelation statistics (of pair of RSP boards)" << endl;
	cout << "             [--duration=<seconds>]            #" << endl;
	cout << "             [--integration=<seconds>]         #" << endl;
	cout << "             [--directory=<directory>]         #" << endl;
	cout << endl;
	cout << "--- Miscellaneous --------------------------------------------------------------------------------------------" << endl;
	cout << "rspctl --clock[=<int>]                         # get or set the clock frequency of clocks in MHz" << endl;
	cout << "rspctl --rspclear           [--select=<set>]   # clear FPGA registers on RSPboard" << endl;
	cout << "rspctl --hbadelays[=<list>] [--select=<set>]   # set or get the 16 delays of one or more HBA's" << endl;
	cout << "rspctl --tbbmode[=transient | =subbands,<set>] # set or get TBB mode, 'transient' or 'subbands', if subbands then specify subband set" << endl;
	if (gHasSplitter) {
        cout << "rspctl --splitter[=0|1]                        # set or get the status of the Serdes splitter" << endl;
    }
    cout << "rspctl --datastream[=0|1|2|3]                  # set or get the status of data stream to cep" << endl;
	cout << "rspctl --swapxy[=0|1] [--select=<set>]         # set or get the status of xy swap, 0=normal, 1=swapped" << endl;
	cout << "rspctl --bitmode[=4|8|16]                      # set or get the number of bits per sample" << endl;
	cout << endl;
    if (gHasAartfaac) {
        cout << "--- Subband Data Output (SDO) --------------------------------------------------------------------------------" << endl;
        cout << "rspctl --sdoenable[=0|1]                       # enable (or disable) sdo output" << endl;
        cout << "rspctl --sdomode[=4|5|8|16]                    # set or get the number of bits per sample" << endl;
        cout << "rspctl --sdo                 [--select=<set>]  # get sdo selection" << endl;
        cout << "rspctl --sdo=<set>           [--select=<set>]  # set sdo selection" << endl;
    }
    if (exportMode) {
	cout << endl;
	cout << "--- Raw register control -------------------------------------------------------------------------------------" << endl;
	cout << " ### WARNING: to following commands may crash the RSPboard when used wrong! ###" << endl;
	cout << "rspctl --readblock=RSPboard,hexAddress,offset,datalength    # read datalength bytes from given address" << endl;
//	cout << "rspctl --readblock=RSPboard,hexAddress,offset,filename      # read datalength bytes from given address" << endl;
//	cout << "         Data is written to the file in binairy format." << endl;
	cout << endl;
	cout << "rspctl --writeblock=RSPboard,hexAddress,offset,hexData      # write data to given address" << endl;
//	cout << "         HexData must start with '0x'." << endl;
//	cout << "rspctl --writeblock=RSPboard,hexAddress,offset,filename     # write data to given address" << endl;
//	cout << "         When filecontents starts with 0x is it read as hexdata," << endl;
//	cout << "         otherwise the file is treated as a binairy file." << endl;
	cout << "In all cases the maximum number of databytes is " << RSP_RAW_BLOCK_SIZE << endl;
	cout << "Address order: BLPID, RSP, PID, REGID" << endl;
	cout << endl;
	}
}

Command* RSPCtl::parse_options(int argc, char** argv)
{
	Command*   command   = 0;
	RCUCommand*   rcumodecommand = 0;
	HBACommand*   hbacommand  = 0;
	list<int> select;
	list<int> beamlets;

	bool  xcangle = false;

	// select all by default
	select.clear();
	for (int i = 0; i < MAX_RCUS; ++i)
		select.push_back(i);

	beamlets.clear();
	int max_beamlets = maxBeamlets(itsNbitsPerSample);
	for (int i = 0; i < max_beamlets; ++i)
		beamlets.push_back(i);

	optind = 0; // reset option parsing
	//opterr = 0; // no error reporting to stderr
	static struct option long_options[] = {
		{ "aweights",       optional_argument, 0, 'a' },
		{ "beamlets",       required_argument, 0, 'b' },
		{ "clock",          optional_argument, 0, 'c' },
		{ "duration",       required_argument, 0, 'd' },
		{ "rcureset",       optional_argument, 0, 'e' },
		{ "wg",             optional_argument, 0, 'g' },
		{ "help",           no_argument,       0, 'h' },
		{ "integration",    required_argument, 0, 'i' },
		{ "sdo",            optional_argument, 0, 'j' },
		{ "sdomode",        optional_argument, 0, 'k' },
        { "select",         required_argument, 0, 'l' },
		{ "rcumode",        required_argument, 0, 'm' },
		{ "rcuattenuation", required_argument, 0, 'n' },
		{ "swapxy",         optional_argument, 0, 'o' },
		{ "rcuprsg",        optional_argument, 0, 'p' },
		{ "status",         no_argument,       0, 'q' },
		{ "rcu",            optional_argument, 0, 'r' },
		{ "subbands",       optional_argument, 0, 's' },
		{ "statistics",     optional_argument, 0, 't' },
		{ "version",        no_argument,       0, 'v' },
		{ "weights",        optional_argument, 0, 'w' },
		{ "xcstatistics",   no_argument,       0, 'x' },
		{ "rcudelay",       required_argument, 0, 'y' },
		{ "xcsubband",      optional_argument, 0, 'z' },

		{ "amplitude",      required_argument, 0, 'A' },
		{ "xcangle",        no_argument,       0, 'B' },
		{ "rspclear",       optional_argument, 0, 'C' },
		{ "directory"  ,    required_argument, 0, 'D' },
		{ "rcuenable",      optional_argument, 0, 'E' },
		{ "wgmode",         required_argument, 0, 'G' },
		{ "hbadelays",      optional_argument, 0, 'H' },
		{ "specinv",        optional_argument, 0, 'I' },
		{ "sdoenable",      optional_argument, 0, 'J' },
		{ "bitmode",        optional_argument, 0, 'K' },
		{ "latency",        no_argument,       0, 'L' },
		{ "mode",           required_argument, 0, 'M' },
		{ "phase",          required_argument, 0, 'P' },
		{ "tdstatus",       no_argument,       0, 'Q' },
		{ "realdelays",     optional_argument, 0, 'R' },
		{ "regstate",       no_argument,       0, 'S' },
		{ "tbbmode",        optional_argument, 0, 'T' },
		{ "spustatus",      no_argument, 	   0, 'V' },
		{ "expert",         no_argument, 	   0, 'X' },
		{ "datastream",     optional_argument, 0, 'Y' },
		{ "splitter",       optional_argument, 0, 'Z' },
		{ "readblock",      required_argument, 0, '1' },
		{ "writeblock",     required_argument, 0, '2' },
		{ 0, 0, 0, 0 },
	};

	realDelays = false;
	while (1) {
		int option_index = 0;
		int c = getopt_long(argc, argv, "a::b:c::d:e::g::hi:j::k::l:m:n:o::p::qr::s::t::vw::xy:z::A:BC::D:E::G:H::I::J::K::LM:P:QR::ST::VXY::Z::1:2:", long_options, &option_index);

		if (c == -1) // end of argument list reached?
			break;

		switch (c) {
		case 'l': // --select
			if (optarg) {
				if (!command || 0 == command->get_ndevices()) {
					logMessage(cerr,"Error: 'command' argument should come before --select argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				select = utility::strtolist(optarg, command->get_ndevices());
				if (select.empty()) {
					logMessage(cerr,"Error: invalid or missing '--select' option");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
			}
			else {
				logMessage(cerr,"Error: option '--select' requires an argument");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		break;

		case 'b': // --beamlets
			if (optarg) {
				if (!command || 0 == command->get_ndevices()) {
					logMessage(cerr,"Error: 'command' argument should come before --beamlets argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				beamlets = utility::strtolist(optarg, maxBeamlets(itsNbitsPerSample));
				if (beamlets.empty()) {
					logMessage(cerr,"Error: invalid or missing '--beamlets' option");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
			}
			else {
				logMessage(cerr,"Error: option '--beamlets' requires an argument");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		break;

		case 'w': // --weights
		{
			if (command)
				delete command;
			WeightsCommand* weightscommand = new WeightsCommand(*itsRSPDriver, itsNbitsPerSample);
			weightscommand->setType(WeightsCommand::COMPLEX);
			command = weightscommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				weightscommand->setMode(false);
                std::list<std::complex<double>> weights;

                if(optarg[0] == '(') {
                     weights = utility::strtocomplexlist(optarg);
                     if (weights.empty()) {
                         logMessage(cerr,"Error: invalid or missing '--weights' option");
                         rspctl_exit_code = EXIT_FAILURE;
                         exit(EXIT_FAILURE);
                     }
                }
                else {
                    double re = 0.0, im = 0.0;
                    int numitems = sscanf(optarg, "%lf,%lf", &re, &im);
                    if (numitems == 0 || numitems == EOF) {
                        logMessage(cerr,"Error: invalid weights value. Should be of the format "
                                   "'--weights=value.re[,value.im]' where value is a floating point value in the range (-1,1].");
                        rspctl_exit_code = EXIT_FAILURE;
                        exit(EXIT_FAILURE);
                    }
                    weights.push_back(complex<double>(re,im));
                }
				weightscommand->setValues(weights);
			}
		}
		break;

		case 'a': // --aweights
		{
			if (command)
				delete command;
			WeightsCommand* weightscommand = new WeightsCommand(*itsRSPDriver, itsNbitsPerSample);
			weightscommand->setType(WeightsCommand::ANGLE);
			command = weightscommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				weightscommand->setMode(false);
				double amplitude = 0.0, angle = 0.0;
				int numitems = sscanf(optarg, "%lf,%lf", &amplitude, &angle);
				if (numitems == 0 || numitems == EOF) {
					logMessage(cerr,"Error: invalid aweights value. Should be of the format "
					"'--weights=amplitude[,angle]' where angle is in degrees.");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}

				if (angle < -180.0 || angle > 180.0) {
					logMessage(cerr, "Error: invalid angle, should be between -180 < angle < 180.0.");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}

				//weightscommand->setValue(complex<double>(amplitude * ::cos(angle), amplitude * ::sin(angle)));
                std::list<std::complex<double>> weights;
                weights.push_back(amplitude * exp(complex<double>(0,angle / 180.0 * M_PI)));
				weightscommand->setValues(weights);
			}
		}
		break;

		case 's': // --subbands
		{
			if (command)
				delete command;
			SubbandsCommand* subbandscommand = new SubbandsCommand(*itsRSPDriver, itsNbitsPerSample);
			subbandscommand->setType(SubbandSelection::BEAMLET);
			command = subbandscommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				subbandscommand->setMode(false);
				list<int> subbandlist = utility::strtolist(optarg, MAX_SUBBANDS);
				if (subbandlist.empty()) {
					logMessage(cerr,"Error: invalid or empty '--subbands' option");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				subbandscommand->setSubbandList(subbandlist);
			}
		}
		break;

		case 'r': // --rcu
		{
			if (command)
				delete command;
			RCUCommand* rcucommand = new RCUCommand(*itsRSPDriver);
			command = rcucommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				rcucommand->setMode(false);
				unsigned long controlopt = strtoul(optarg, 0, 0);
				if (controlopt > 0xFFFFFFFF) {
					logMessage(cerr,"Error: option '--rcu' parameter must be < 0xFFFFFFFF");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}

				rcucommand->control().setRaw((uint32)controlopt);
			}
		}
		break;

		case 'm': // --rcumode
		case 'p': // --rcuprsg
		case 'e': // --rcureset
		case 'n': // --rcuattenuation
		case 'y': // --rcudelay
		case 'E': // --rcuenable
		{
			// instantiate once, then reuse to add control bits
			if (!rcumodecommand) {
				if (command)
					delete command;
				rcumodecommand = new RCUCommand(*itsRSPDriver);
			}

			command = rcumodecommand;
			command->set_ndevices(m_nrcus);

			if ('m' == c || 'n' == c || 'y' == c) {
				if (!optarg) {
					logMessage(cerr,"Error: option requires an argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
			}

			rcumodecommand->setMode(false);
			unsigned long controlopt = 0;

			switch (c) {
			case 'm': // --rcumode
				controlopt = strtoul(optarg, 0, 0);
				if (controlopt >= 8) {
					logMessage(cerr,"Error: --rcumode value should be < 8");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				rcumodecommand->control().setMode((RCUSettings::Control::RCUMode)controlopt);
			break;

			case 'p': // --rcuprsg
				if (optarg && !strncmp(optarg, "0", 1)) {
					rcumodecommand->control().setPRSG(false);
				} else {
					rcumodecommand->control().setPRSG(true);
				}
			break;

			case 'e': // --rcureset
				if (optarg && !strncmp(optarg, "0", 1)) {
					rcumodecommand->control().setReset(false);
				} else {
					rcumodecommand->control().setReset(true);
				}
			break;

			case 'n': // --rcuattenuation
				controlopt = strtoul(optarg, 0, 0);
				if (controlopt > 31) {
					logMessage(cerr,"Error: --rcuattenuation value should be <= 31");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				rcumodecommand->control().setAttenuation((uint8)controlopt);
			break;

			case 'y': // --rcudelay
				controlopt = strtoul(optarg, 0, 0);
				if (controlopt > 127) {
					logMessage(cerr,"Error: --rcudelay value should be <= 127");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				rcumodecommand->control().setDelay((uint8)controlopt);
			break;

			case 'E': // --rcuenable
				if (optarg && !strncmp(optarg, "0", 1)) {
					rcumodecommand->control().setEnable(false);
				} else {
					rcumodecommand->control().setEnable(true);
				}
			break;
			} // switch

		}
		break;

		case 'o': // swapxy
		{
			if (command)
				delete command;
			SWAPXYCommand* swapxycommand = new SWAPXYCommand(*itsRSPDriver);
			command = swapxycommand;

			command->set_ndevices(itsNantennas);
			select.clear();
			for (int i = 0; i < itsNantennas; ++i) {
				select.push_back(i);
			}

			if (optarg) {
				swapxycommand->setMode(false);
				if (!strncmp(optarg, "0", 1)) {
					swapxycommand->setSwapXY(false);
				} else {
					swapxycommand->setSwapXY(true);
				}
			}
		} break;

		case 'g': // --wg
		{
			if (command)
				delete command;
			WGCommand* wgcommand = new WGCommand(*itsRSPDriver);
			command = wgcommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				wgcommand->setMode(false);
				double frequency = atof(optarg);
				if ( frequency < 0 ) {
					logMessage(cerr,"Error: option '--wg' parameter must be > 0");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
//    wgcommand->setFrequency(frequency, gSampleFrequency);
				wgcommand->setFrequency(frequency);
				itsNeedClockOnce = true;
			}
		}
		break;

		case 'G': // --wgmode
		{
			if (optarg) {
				int mode = atoi(optarg);
				if (mode != 0 && mode != 1 && mode != 3 && mode != 5) {
					logMessage(cerr,"Error: option '--wgmode' parameter must be 0,1,3 or 5");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				WGCommand* wgcommand = dynamic_cast<WGCommand*>(command);
				wgcommand->setWaveMode(mode);
			}
		}
		break;

		case 'P': // --phase
		{
			if (optarg) {
				double phase = atof(optarg);
				if (phase < 0 || phase > (M_PI * 2.0)) {
					logMessage(cerr,"Error: option '--phase' parameter must be between 0 and 2 pi");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				WGCommand* wgcommand = dynamic_cast<WGCommand*>(command);
				wgcommand->setPhase((uint8)((phase / (2 * M_PI)) * (1 << 8)));
			}
		}
		break;

		case 'A':  // --amplitude
		{
			if (optarg) {
				double amplitude = atof(optarg);
				if (amplitude > 2.0 || amplitude < 0.0) {
					logMessage(cerr, "Error: option '--amplitude' paramter must be >= 0 and <= 1.0");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				WGCommand *wgcommand = dynamic_cast<WGCommand*>(command);
				wgcommand->setAmplitude(amplitude);
			}
		}
		break;

		case 'q' : // --status
		{
			if (command)
				delete command;
			StatusCommand* statuscommand = new StatusCommand(*itsRSPDriver);
			command = statuscommand;

			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'Q': // --tdstatus
		{
			if (command)
				delete command;
			TDStatusCommand* tdstatuscommand = new TDStatusCommand(*itsRSPDriver);
			command = tdstatuscommand;
			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'V': // --spustatus
		{
			if (command)
				delete command;
			SPUStatusCommand* spustatuscommand = new SPUStatusCommand(*itsRSPDriver);
			command = spustatuscommand;
			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'Z': // --splitter
		{
			if (command)
				delete command;
			SplitterCommand* splitterCommand = new SplitterCommand(*itsRSPDriver);
			command = splitterCommand;
			command->set_ndevices(m_nrspboards);
			if (optarg) {
				splitterCommand->setMode(false); // true=get,false=set
				splitterCommand->state(atoi(optarg));
			}

		}
		break;

		case 'K': // --bitmode
		{
			if (command)
				delete command;
			BitmodeCommand* bitmodecommand = new BitmodeCommand(*itsRSPDriver);
			command = bitmodecommand;

			command->set_ndevices(m_nrspboards);
			select.clear();
			for (int i = 0; i < m_nrspboards; ++i) {
				select.push_back(i);
			}

			if (optarg) {
				bitmodecommand->setMode(false);
				unsigned long bitmode = strtoul(optarg, 0, 0);
				if (bitmode != 4 && bitmode != 8 && bitmode != 16) {
					logMessage(cerr, formatString("Error: bitmode value can only be 4, 8 or 16, not %d", bitmode));
	   				rspctl_exit_code = EXIT_FAILURE;
				}
				bitmodecommand->bitmode(bitmode);
			}
		} break;

        case 'j': // --sdo
		{
			if (command)
				delete command;
			SDOCommand* sdocommand = new SDOCommand(*itsRSPDriver);
			command = sdocommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				sdocommand->setMode(false);
				list<int> subbandlist = utility::strtolist(optarg, MAX_SUBBANDS);
				if (subbandlist.empty()) {
					logMessage(cerr,"Error: invalid or empty '--sdo' option");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				sdocommand->setSubbandList(subbandlist);
			}
		}
		break;

        case 'k': // --sdomode
		{
			if (command)
				delete command;
			SDOmodeCommand* sdomodecommand = new SDOmodeCommand(*itsRSPDriver);
			command = sdomodecommand;

			command->set_ndevices(m_nrspboards);
			select.clear();
			for (int i = 0; i < m_nrspboards; ++i) {
				select.push_back(i);
			}

			if (optarg) {
				sdomodecommand->setMode(false);
				unsigned long sdomode = strtoul(optarg, 0, 0);
				if (sdomode != 4 && sdomode != 5 && sdomode != 8 && sdomode != 16) {
					logMessage(cerr, formatString("Error: sdomode value can only be 4, 5, 8 or 16, not %d", sdomode));
	   				rspctl_exit_code = EXIT_FAILURE;
				}
				sdomodecommand->sdomode(sdomode);
			}
		} break;
		case 't': // --statistics
		{
			if (command)
				delete command;
			StatisticsCommand* statscommand = new StatisticsCommand(*itsRSPDriver, itsNbitsPerSample);
			command = statscommand;

			command->set_ndevices(m_nrcus);

            itsNeedSplitter = true;

			if (optarg) {
				if (!strcmp(optarg, "subband")) {
					statscommand->setType(Statistics::SUBBAND_POWER);
				} else if (!strcmp(optarg, "beamlet")) {
				    // 2 = number of cep streams, normal 1, in splitted mode 2
					command->set_ndevices(2 * N_POL);
					statscommand->setType(Statistics::BEAMLET_POWER);
					itsNeedBitmode  = true;
				} else {
					logMessage(cerr, formatString("Error: invalid statistics type %s", optarg));
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
			}
			itsNeedClock = true;
		}
		break;

		case 'B':
		{
			xcangle = true;
		}
		break;

		case 'x': // -- xcstatistics
		{
			if (command)
				delete command;
			XCStatisticsCommand* xcstatscommand = new XCStatisticsCommand(*itsRSPDriver);
			xcstatscommand->setAngle(xcangle);
			command = xcstatscommand;
			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'z': // -- xcsubbands
		{
			if (command)
				delete command;
			SubbandsCommand* subbandscommand = new SubbandsCommand(*itsRSPDriver, itsNbitsPerSample);
			subbandscommand->setType(SubbandSelection::XLET);
			command = subbandscommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				subbandscommand->setMode(false);

				int subband = atoi(optarg);

				if (subband < 0 || subband >= MAX_SUBBANDS) {
					logMessage(cerr,formatString("Error: argument to --xcsubband out of range, value must be >= 0 and < %d",MAX_SUBBANDS));
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}

				list<int> subbandlist;
				for (int rcu = 0; rcu < m_nrcus / N_POL; rcu++) {
					subbandlist.push_back(subband);
				}
				subbandscommand->setSubbandList(subbandlist);
			}
		}
		break;

		case 'c': // --clock
		{
			if (command)
				delete command;
			ClockCommand* clockcommand = new ClockCommand(*itsRSPDriver);
			command = clockcommand;

			command->set_ndevices(m_nrspboards);

			if (optarg) {
				clockcommand->setMode(false);
				double clock = atof(optarg);
				if ( 0 != (uint32)clock && 160 != (uint32)clock && 200 != (uint32)clock) {
					logMessage(cerr,"Error: option '--clocks' parameter must be 0 (off), 160 (MHz) or 200 (MHz)");
	   				rspctl_exit_code = EXIT_FAILURE;
					delete command;
					return 0;
				}
				clockcommand->setClock((uint32)clock);
			}
		}
		break;

		case 'C': // --rspclear
		{
			if (command)
				delete command;
			RSUCommand* rsucommand = new RSUCommand(*itsRSPDriver);
			command = rsucommand;
			command->set_ndevices(m_nrspboards);

			rsucommand->setMode(false); // is a SET command
			rsucommand->control().setClear(true);
		}
		break;

		case 'S': // --regstate
		{
			if (command)
				delete command;
			RegisterStateCommand* regstatecommand = new RegisterStateCommand(*itsRSPDriver);
			command = regstatecommand;
		}
		break;

		case 'v': // --version
		{
			if (command)
				delete command;
			VersionCommand* versioncommand = new VersionCommand(*itsRSPDriver);
			command = versioncommand;
			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'R':  // --realdelays
			realDelays = true;
			// no break!!!
		case 'H':  // --hbadelays
		{
			if (!hbacommand) {
				if (command)
					delete command;
				hbacommand = new HBACommand(*itsRSPDriver);
			}

			command = hbacommand;
			command->set_ndevices(m_nrcus);

			if (optarg) {
				hbacommand->setMode(false); // set the HBA delays
				hbacommand->setDelayList(utility::strtolist(optarg, (uint8)-1));
			}
		}
		break;

		case 'T': // --tbbmode  .
		{
			if (command)
				delete command;
			TBBCommand* tbbcommand = new TBBCommand(*itsRSPDriver);
			command = tbbcommand;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				tbbcommand->setMode(false);
				if (!strcmp(optarg, "transient")) {
					tbbcommand->setType(TBBCommand::TRANSIENT);
				} else if (!strncmp(optarg, "subbands", strlen("subbands"))) {
					tbbcommand->setType(TBBCommand::SUBBANDS);

					char* liststring = strchr(optarg, ',');
					liststring++; // skip the ,
					if (liststring && *liststring) {
                        list<int> subbandlist = utility::strtolist(liststring, MAX_SUBBANDS);
						if (subbandlist.empty()) {
							logMessage(cerr,"Error: missing or invalid subband set '--tbbmode=subbands' option");
	   						rspctl_exit_code = EXIT_FAILURE;
							exit(EXIT_FAILURE);
						}
						tbbcommand->setSubbandSet(subbandlist);
					} else {
						logMessage(cerr,"Error: missing or invalid subband set '--tbbmode=subbands' option");
	   					rspctl_exit_code = EXIT_FAILURE;
					}
				} else {
					logMessage(cerr, formatString("Error: invalid statistics type %s", optarg));
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
			}
		}
		break;

		case 'L': // --latency
		{
			if (command)
				delete command;
			LatencyCommand* latencyCmd = new LatencyCommand(*itsRSPDriver);
			command = latencyCmd;

			command->set_ndevices(m_nrspboards);
		}
		break;

		case 'I': // --spectral Inversion
		{
			if (command)
				delete command;
			SICommand* specInvCmd = new SICommand(*itsRSPDriver);
			command = specInvCmd;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				specInvCmd->setMode(false);
				specInvCmd->setSI(strncmp(optarg, "0", 1));
			}
		}
		break;

        case 'J': // --sdoenable
		{
			if (command)
				delete command;
			SDOenableCommand* sdoEnableCmd = new SDOenableCommand(*itsRSPDriver);
			command = sdoEnableCmd;

			command->set_ndevices(m_nrcus);

			if (optarg) {
				sdoEnableCmd->setMode(false);
				sdoEnableCmd->setEnable(strncmp(optarg, "0", 1));
			}
		}
		break;

		case 'Y': // --datastream
		{
			if (command)
				delete command;
			DataStreamCommand* datastreamCmd = new DataStreamCommand(*itsRSPDriver);
			command = datastreamCmd;

			command->set_ndevices(m_nrspboards);

			if (optarg) {
				datastreamCmd->setMode(false);
				datastreamCmd->setStream(0,atoi(optarg)%2);
				datastreamCmd->setStream(1,atoi(optarg)/2);
				itsNeedSplitter = true;
			}
		}
		break;

		case 'h': // --help
			usage(false);
			exit(EXIT_FAILURE);
		break;

		case 'X': // --export help
			usage(true);
			exit(EXIT_FAILURE);
		break;

		case 'd': // --duration
			if (optarg) {
				if (!command || 0 == command->get_ndevices()) {
					logMessage(cerr,"Error: 'command' argument should come before --duration argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				StatisticsBaseCommand* statisticsBaseCommand = dynamic_cast<StatisticsBaseCommand*>(command);
				if (statisticsBaseCommand == 0) {
					logMessage(cerr,"Error: 'duration' argument can not be used in conjunction with the specified command");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				statisticsBaseCommand->setDuration(atoi(optarg));
			}
			else {
				logMessage(cerr,"Error: option '--duration' requires an argument");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		break;

		case 'i': // -- integration
			if (optarg) {
				if (!command || 0 == command->get_ndevices()) {
					logMessage(cerr,"Error: 'command' argument should come before --integration argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				StatisticsBaseCommand* statisticsBaseCommand = dynamic_cast<StatisticsBaseCommand*>(command);
				if (statisticsBaseCommand == 0) {
					logMessage(cerr,"Error: 'integration' argument can not be used in conjunction with the specified command");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				statisticsBaseCommand->setIntegration(atoi(optarg));
			}
			else {
				logMessage(cerr,"Error: option '--integration' requires an argument");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		break;

		case 'D': // -- directory
			if (optarg) {
				if (!command || 0 == command->get_ndevices()) {
					logMessage(cerr,"Error: 'command' argument should come before --directory argument");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				StatisticsBaseCommand* statisticsBaseCommand = dynamic_cast<StatisticsBaseCommand*>(command);
				if (statisticsBaseCommand == 0) {
					logMessage(cerr,"Error: 'directory' argument can not be used in conjunction with the specified command");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				statisticsBaseCommand->setDirectory(optarg);
			}
			else {
				logMessage(cerr,"Error: option '--directory' requires an argument");
	   			rspctl_exit_code = EXIT_FAILURE;
			}
		break;

        case 'M': { // mode
            if (!optarg) {
                logMessage(cerr,"Error: option requires an argument");
                rspctl_exit_code = EXIT_FAILURE;
                return 0;
            }
            int mode = atoi(optarg);
            if (mode < 0 || mode > 7) {
                logMessage(cerr,"Error: wrong mode must be in range 0..7");
                rspctl_exit_code = EXIT_FAILURE;
                return 0;
            }

            ModeCommand* modecommand = new ModeCommand(*itsRSPDriver);
            command = modecommand;
            command->set_ndevices(m_nrcus);

            modecommand->setReceiverMode(mode);
            //itsNeedClockOnce = true;
        } break;

		case '1':  // readblock=RSPboard,hexAddress,offset,(datalen|filename)
		case '2': {  // writeblock=RSPboard,hexAddress,offset,(datalen|filename)
			// allocate the right command
			if (command) {
				delete (command);
			}
			RawBlockCommand* rbCmd = new RawBlockCommand(*itsRSPDriver);
			command = rbCmd;
			rbCmd->setMode(c == '1');

			// we definitely need arguments
			if (!optarg) {
				usage(false);
				logMessage(cerr, "Need arguments for dataBlock");
	   			rspctl_exit_code = EXIT_FAILURE;
				exit(EXIT_FAILURE);
			}

			// try to parse the arguments
			uint32 rspBoard;
			uint32 address;
			uint32 offset;
			uint32 dataLen;
			char dataStr[4096];
			char addrStr[1024];
			if (c == '1') { // read block
				int numItems = sscanf(optarg, "%u,%[0-9A-Fa-f],%u,%u", &rspBoard, &addrStr[0], &offset, &dataLen);
				if (numItems != 4) {
					logMessage(cerr, "Need 4 arguments: rspBoardNr, hexAddress, offset, datalen");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
			}
			else { // write block has different fourth parameter.
				int numItems = sscanf(optarg, "%u,%[0-9A-Fa-f],%u,%s", &rspBoard, &addrStr[0], &offset, &dataStr[0]);
				if (numItems != 4) {
					logMessage(cerr, "Need 4 arguments: rspBoardNr, hexAddress, offset, hexData");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				if (strlen(dataStr) % 1) {
					logMessage(cerr, "Datastring must have an even number of characters");
	   				rspctl_exit_code = EXIT_FAILURE;
					exit(EXIT_FAILURE);
				}
				dataLen = strlen(dataStr) / 2;
			}

			// minor checking on the arguments.
			if (rspBoard > (uint32)m_nrspboards || dataLen == 0 || dataLen > (uint32)RSP_RAW_BLOCK_SIZE) {
				cerr <<  "Range error" << endl;
				cerr <<  "RSPboard: 0.." << m_nrspboards << endl;
				cerr <<  "Datalength: 1.." << RSP_RAW_BLOCK_SIZE << endl;
				exit(EXIT_FAILURE);
			}

			// convert addrString to address value (reverse order on intel)
			if (strlen(addrStr) != 8) {
				logMessage(cerr, "Address string must have 8 characters");
	   			rspctl_exit_code = EXIT_FAILURE;
				exit(EXIT_FAILURE);
			}
			address = 0;
			for (int i = 3; i >= 0; i--) {
				address = (address << 8) + (uint8)(xtod(addrStr[i*2])<<4 | xtod(addrStr[i*2+1]));
			}

			// write the usersetttings to the command.
			rbCmd->setAddressInfo(rspBoard, address, offset);
			if (c == '1') {  // read block
				rbCmd->setDataInfo("", dataLen, 0);
			}
			else {
				// Transfer dataStr to databuffer
				uint8 databuf[2048];
				for (uint16 i = 0; i < dataLen; i++) {
					databuf[i] = (uint8)(xtod(dataStr[i*2])<<4 | xtod(dataStr[i*2+1]));
				}
				rbCmd->setDataInfo("", dataLen, &databuf[0]);
			}
		}
		break;


		case '?':
		default:
			logMessage(cerr, "Error: invalid option");
	   		rspctl_exit_code = EXIT_FAILURE;
			exit(EXIT_FAILURE);
		break;
		}
		}

	if (command) {
		command->setSelect(select);
		command->setBeamlets(beamlets);
	}

	return (command);
}

void utility::logMessage(ostream& stream, const string& message) {
  stream << message << endl;
}

std::list<complex<double>> utility::strtocomplexlist(const char* str)
{
  std::string input_string(str);
  list<complex<double>> result;

  char*  start  = (char*)input_string.c_str();
  char*  end    = 0;
  bool   pair   = false;
  bool   img    = false;
  double first  = 0;
  double second = 0;

  while(start) {
    double val = strtod(start, &end); // read decimal numbers
	start = (end ? (*end ? end + 1 : 0) : 0); // advance
    if(end) {
      switch(*end) {
      case 0:
        break;
      case ',':
        if(pair) {
          first = val;
          img = true;
        }
        break;
      case '(':
        pair = true;
        break;
      case ')':
        if(img) {
            second = val;
        }
        else {
          first = val;
        }
        
        result.push_back(std::complex<double>(first, second));
        pair = false;
        img = false;
        first = 0;
        second = 0;
        break;
      default:
        logMessage(cerr,formatString("Error: invalid character %c",*end));
        rspctl_exit_code = EXIT_FAILURE;
        result.clear();
        return result;
        break;
      } // switch
    } // if (end)
  }
  
  return result;
}

std::list<int> utility::strtolist(const char* str, int max)
{
	string inputstring(str);
	char* start  = (char*)inputstring.c_str();
	char* end  = 0;
	bool  range  = false;
	long  prevval = 0;
	list<int> resultset;

	resultset.clear();

	while (start) {
		long val = strtol(start, &end, 10); // read decimal numbers
		start = (end ? (*end ? end + 1 : 0) : 0); // advance
		if (val >= max || val < 0) {
			logMessage(cerr,formatString("Error: value %d out of range",val));
	   		rspctl_exit_code = EXIT_FAILURE;
			resultset.clear();
			return resultset;
		}

		if (end) {
			switch (*end) {
			case ',':
			case 0: {
				if (range) {
					if (0 == prevval && 0 == val) {
						val = max - 1;
					}
					if (val < prevval) {
						logMessage(cerr,"Error: invalid range specification");
	   					rspctl_exit_code = EXIT_FAILURE;
						resultset.clear();
						return resultset;
					}
					for (long i = prevval; i <= val; i++)
						resultset.push_back(i);
					}
					else {
						resultset.push_back(val);
					}
					range=false;
				}
				break;

			case ':':
				range=true;
				break;

			default:
				logMessage(cerr,formatString("Error: invalid character %c",*end));
	   			rspctl_exit_code = EXIT_FAILURE;
				resultset.clear();
				return resultset;
				break;
			} // switch
		} // if (end)
		prevval = val;
	} // while

	return (resultset);
}

void RSPCtl::logMessage(ostream& stream, const string& message)
{
	if(itsCommand != 0) {
		itsCommand->logMessage(stream,message);
	}
	else {
		stream << message << endl;
	}
}

	} // namespace rspctl
} // namespace LOFAR

