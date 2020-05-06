//#  tRCUCables.cc: test reading in the CableDelays.conf file.
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
#include "RCUCables.h"

using namespace LOFAR;

SUITE(RCUCables) {
    TEST(get_largest_delay) {
        // good file
        RCUCables RC1("tRCUCables.in_CableAtts", "tRCUCables.in_1");

        CHECK_CLOSE(0,       RC1.getLargestDelay(0), 0.001);
        CHECK_CLOSE(326.964, RC1.getLargestDelay(1), 0.001);
        CHECK_CLOSE(326.964, RC1.getLargestDelay(2), 0.001);
        CHECK_CLOSE(326.964, RC1.getLargestDelay(3), 0.001);
        CHECK_CLOSE(326.964, RC1.getLargestDelay(4), 0.001);
        CHECK_CLOSE(465.525, RC1.getLargestDelay(5), 0.001);
        CHECK_CLOSE(465.525, RC1.getLargestDelay(6), 0.001);
        CHECK_CLOSE(465.525, RC1.getLargestDelay(7), 0.001);
	}

    TEST(get_largest_attenuation) {
        // good file
        RCUCables RC1("tRCUCables.in_CableAtts", "tRCUCables.in_1");

        CHECK_CLOSE(0,      RC1.getLargestAtt(0), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getLargestAtt(1), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getLargestAtt(2), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getLargestAtt(3), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getLargestAtt(4), 0.01);
        CHECK_CLOSE(-8.35,  RC1.getLargestAtt(5), 0.01);
        CHECK_CLOSE(-9.7,   RC1.getLargestAtt(6), 0.01);
        CHECK_CLOSE(-10.18, RC1.getLargestAtt(7), 0.01);
    }

    TEST(get_delay) {
        // good file
        RCUCables RC1("tRCUCables.in_CableAtts", "tRCUCables.in_1");

        CHECK_CLOSE(0,       RC1.getDelay(5, 0), 0.001);
        CHECK_CLOSE(199.257, RC1.getDelay(5, 1), 0.001);
        CHECK_CLOSE(199.257, RC1.getDelay(5, 2), 0.001);
        CHECK_CLOSE(326.964, RC1.getDelay(5, 3), 0.001);
        CHECK_CLOSE(326.964, RC1.getDelay(5, 4), 0.001);
        CHECK_CLOSE(465.525, RC1.getDelay(5, 5), 0.001);
        CHECK_CLOSE(465.525, RC1.getDelay(5, 6), 0.001);
        CHECK_CLOSE(465.525, RC1.getDelay(5, 7), 0.001);
    }

    TEST(get_attenuation) {
        // good file
        RCUCables RC1("tRCUCables.in_CableAtts", "tRCUCables.in_1");

        CHECK_CLOSE(0,      RC1.getAtt(5, 0), 0.01);
        CHECK_CLOSE(-2.05,  RC1.getAtt(5, 1), 0.01);
        CHECK_CLOSE(-2.05,  RC1.getAtt(5, 2), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getAtt(5, 3), 0.01);
        CHECK_CLOSE(-3.32,  RC1.getAtt(5, 4), 0.01);
        CHECK_CLOSE(-8.35,  RC1.getAtt(5, 5), 0.01);
        CHECK_CLOSE(-9.7,   RC1.getAtt(5, 6), 0.01);
        CHECK_CLOSE(-10.18, RC1.getAtt(5, 7), 0.01);
	}

    TEST(missing_line_for_rcu_zero) {
        try {
            RCUCables RC2("tRCUCables.in_CableAtts", "tRCUCables.in_2");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }

    TEST(wrong_order_of_rcu_lines) {
        try {
            RCUCables RC3("tRCUCables.in_CableAtts", "tRCUCables.in_3");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }

    TEST(file_with_illegal_cable_lengths) {
        try {
            RCUCables RC4("tRCUCables.in_CableAtts", "tRCUCables.in_4");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }

    TEST(too_many_lines_in_file) {
        try {
            RCUCables RC5("tRCUCables.in_CableAtts", "tRCUCables.in_5");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }

    TEST(one_line_with_not_enough_arguments) {
        try {
            RCUCables RC6("tRCUCables.in_CableAtts", "tRCUCables.in_6");
            CHECK(false);
        }
        catch (Exception& ex) {
            // This should throw an exception. Good.
        }
    }
}

int main (int, char*    argv[])
{
    INIT_LOGGER(argv[0]);

    return UnitTest::RunAllTests() > 0;
}