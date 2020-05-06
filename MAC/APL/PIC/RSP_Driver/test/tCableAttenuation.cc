//#  tCableAttenuation.cc: test reading in the attenuation.conf file.
//#
//#  Copyright (C) 2009
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

//# Always #include <lofar_config.h> first!
#include <lofar_config.h>

//# Includes
#include <UnitTest++.h>
#include <Common/LofarLogger.h>
#include <Common/lofar_bitset.h>
#include <Common/lofar_map.h>
#include <Common/hexdump.h>
#include "CableAttenuation.h"

using namespace LOFAR;

SUITE(CableAttenuation) {

    TEST(legal_length) {
        // good file
        CableAttenuation CA1("tCableAttenuation.in_1");
        // good length
        CHECK_EQUAL(true, CA1.isLegalLength( 50));
        CHECK_EQUAL(true, CA1.isLegalLength( 80));
        CHECK_EQUAL(true, CA1.isLegalLength(130));
        // bad length
        CHECK_EQUAL(false, CA1.isLegalLength( 60));
    }

    TEST(missing_line_for_rucmode_zero) {
        try {
            CableAttenuation CA2("tCableAttenuation.in_2");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }

    TEST(lines_in_wrong_order) {
        try {
            CableAttenuation CA3("tCableAttenuation.in_3");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw and exception. Good.
        }
    }

    TEST(too_few_mode_lines) {
        try {
            CableAttenuation CA4("tCableAttenuation.in_4");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw and exception. Good.
        }
    }

    TEST(too_many_mode_lines) {
        try {
            CableAttenuation CA5("tCableAttenuation.in_5");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw and exception. Good.
        }
    }

    TEST(missing_parameters_on_line) {
        try {
            CableAttenuation CA6("tCableAttenuation.in_6");
            CHECK(false);
        }
        catch (Exception& ex) {
            LOG_INFO_STR("Expected exception:" << ex.what());
        }
    }
}

int main (int, char*    argv[])
{
    INIT_LOGGER(argv[0]);

    return UnitTest::RunAllTests() > 0;
}