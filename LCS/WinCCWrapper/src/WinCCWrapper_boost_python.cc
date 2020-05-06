//# Copyright (C) 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR Software Suite.
//#
//# The LOFAR Software Suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published by
//# the Free Software Foundation, either version 3 of the License, or (at your
//# option) any later versions
//#
//# The LOFAR Software Suite is distributed in the hope that it will be
//# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
//# Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along with
//# The LOFAR Software Suite.  If not, see <http://www.gnu.org/licenses/>.

#include <boost/python.hpp>
#include "WinCCWrapper.h"
#include <vector>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>

BOOST_PYTHON_MODULE(pywincc)
{
    using namespace boost::python;
    using namespace LOFAR::WINCCWRAPPER;

    bool (WinCCWrapper::*set_datapoint_int)(const std::string&, int, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_list)(const std::string&, boost::python::list&, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_tuple)(const std::string&, boost::python::tuple&, bool) = &WinCCWrapper::set_datapoint;
    // the set_datapoint_vector method is used in the WinCCGet and WinCCSet tests
    bool (WinCCWrapper::*set_datapoint_vector)(const std::string&, std::vector<int>&, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_long)(const std::string&, long, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_float)(const std::string&, float, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_bool)(const std::string&, bool, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_string)(const std::string&, std::string, bool) = &WinCCWrapper::set_datapoint;
    bool (WinCCWrapper::*set_datapoint_time)(const std::string&, time_t, bool) = &WinCCWrapper::set_datapoint_time;
    bool (WinCCWrapper::*set_datapoint_valid)(const std::string&) = &WinCCWrapper::set_datapoint_valid;
    bool (WinCCWrapper::*set_datapoint_invalid)(const std::string&) = &WinCCWrapper::set_datapoint_invalid;

    // define the conversion between std::vector<int> and boost::python::list
    class_<std::vector<int>>("VectorIterable")
      .def(vector_indexing_suite<std::vector<int>>())
    ;

    class_<WinCCWrapper>("WinCCWrapper", init<const std::string&>())
        .def("set_datapoint_int", set_datapoint_int)
        .def("set_datapoint_list", set_datapoint_list)
        // define the "set_datapoint_list" method once more to accept a tuple instead of a list
        .def("set_datapoint_list", set_datapoint_tuple)
        .def("set_datapoint_vector", set_datapoint_vector)
        .def("set_datapoint_long", set_datapoint_long)
        .def("set_datapoint_float", set_datapoint_float)
        .def("set_datapoint_bool", set_datapoint_bool)
        .def("set_datapoint_string", set_datapoint_string)
        .def("set_datapoint_time", set_datapoint_time)
        .def("set_datapoint", set_datapoint_float) // 'common'/'generic' set_datapoint python method just calls set_datapoint_float
        .def("set_datapoint_valid", set_datapoint_valid)
        .def("set_datapoint_invalid", set_datapoint_invalid)
        .def("get_datapoint_int", &WinCCWrapper::get_datapoint_int)
        .def("get_datapoint_list", &WinCCWrapper::get_datapoint_list)
        .def("get_datapoint_vector", &WinCCWrapper::get_datapoint_vector)
        .def("get_datapoint_long", &WinCCWrapper::get_datapoint_long)
        .def("get_datapoint_float", &WinCCWrapper::get_datapoint_float)
        .def("get_datapoint_bool", &WinCCWrapper::get_datapoint_bool)
        .def("get_datapoint_string", &WinCCWrapper::get_datapoint_string)
        .def("get_datapoint_time", &WinCCWrapper::get_datapoint_time)
        .def("get_datapoint", &WinCCWrapper::get_datapoint_float) // 'common'/'generic' get_datapoint python method just calls get_datapoint_float
    ;
}

