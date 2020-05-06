#ifndef SinglePacketCepTestCmd_h_
#define SinglePacketCepTestCmd_h_
//#  -*- mode: c++ -*-
//#
//#  SinglePacketCepTestCmd.h
//#
//#  Copyright (C) 2018
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


#include <Common/LofarTypes.h>
#include "Command.h"


namespace  LOFAR
{
    namespace MACIO
    {
        class GCFEvent;
    }

    namespace GCF
    {
        namespace TM
        {
            class GCFPortInterface;
        }
    }

    namespace TBB
    {
        class TbbSettings;


        class SinglePacketCepTestCmd: public Command
        {
            public:
            /// Constructor for a SinglePacketCepTestCmd object.
            SinglePacketCepTestCmd();

            /// Destructor for SinglePacketCepTestCmd.
            virtual ~SinglePacketCepTestCmd();

            virtual bool isValid(LOFAR::MACIO::GCFEvent& event);

            virtual void saveTbbEvent(LOFAR::MACIO::GCFEvent& event);

            virtual void sendTpEvent();

            virtual void saveTpAckEvent(LOFAR::MACIO::GCFEvent& event);

            virtual void sendTbbAckEvent(
                LOFAR::GCF::TM::GCFPortInterface* clientport);


            private:
            LOFAR::TBB::TbbSettings* TS;
        };
    } // end TBB namespace
} // end LOFAR namespace
#endif /* SinglePacketCepTestCmd_h_ */
