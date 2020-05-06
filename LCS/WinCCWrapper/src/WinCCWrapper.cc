//# Copyright (C) 2017
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR Software Suite.
//#
//# The LOFAR Software Suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published by
//# the Free Software Foundation, either version 3 of the License, or (at your
//# option) any later version.
//#
//# The LOFAR Software Suite is distributed in the hope that it will be
//# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
//# Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along with
//# The LOFAR Software Suite.  If not, see <http://www.gnu.org/licenses/>.

#include <StartDpInitSysMsg.hxx>
#include <IntegerVar.hxx>
#include <FloatVar.hxx>
#include <LongVar.hxx>
#include <TimeVar.hxx>
#include <DynVar.hxx>
#include <vector>
#include <Variable.hxx>

#include <condition_variable>
#include <mutex>
#include <queue>
#include <thread>

#include "WinCCWrapper.h"
#include "ConnectWaitForAnswer.h"

#include <boost/python.hpp>

namespace LOFAR {
    namespace WINCCWRAPPER {

using namespace std;

//! Each datapoint has a human readable name in the wincc database, but the actual value is stored in a sub-item. Append that to each set/get datapoint name.
static const string DP_SUFFIX = ":_original.._value";
//! This property refers to the last set time
static const string DP_SUFFIX_STIME = ":_original.._stime";


WinCCWrapper::WinCCWrapper(const std::string &project_name) :
  resources(project_name)
{
    manager = new WinCCManager();
}

WinCCWrapper::WinCCWrapper(const std::string &program_name, const std::string &project_name, const int num) :
  resources(program_name, project_name, num)
{
    manager = new WinCCManager();
}

void WinCCWrapper::run()
{
    manager->run();
}

void WinCCWrapper::exit()
{
    manager->exit();
}

void WinCCWrapper::connect_datapoints(const std::vector<std::string> &data_points)
{
    manager->connect_datapoints(data_points);
}

void WinCCWrapper::connect_datapoints_multi(const std::vector<std::string> &data_points)
{
    manager->connect_datapoints_multiple(data_points);
}

void WinCCWrapper::disconnect_datapoints(const std::vector<std::string> &data_points)
{
    manager->connect_datapoints(data_points);
}


void WinCCWrapper::wait_for_event(long sec, long microSec){
    manager->wait_for_event(sec, microSec);
}

void WinCCWrapper::set_connect_datapoints_callback(std::function<void(std::string name, std::string value)> callback)
{
    manager->set_connect_datapoints_callback(callback);
}

void WinCCWrapper::set_connect_datapoints_callback(std::function<void(std::map<std::string, std::string>)> callback)
{
    manager->set_connect_datapoints_callback(callback);
}

// set_datapoint
bool WinCCWrapper::set_datapoint(const std::string &name, int value, bool valid)
{
    IntegerVar variable{value};

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, boost::python::list &value, bool valid)
{
    DynVar variable(VariableType::INTEGER_VAR);

    for(int i = 0; i < boost::python::len(value); i++) {
       int boost_elem = boost::python::extract<int>(value[i]);
       IntegerVar elem{boost_elem};
       variable.append(elem);}
    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, boost::python::tuple &value, bool valid)
{
    // do a simple type conversion to a boost::python::list to access the 'append' method
    boost::python::list temp_list = boost::python::list(value);
    return set_datapoint(name, temp_list, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, std::vector<int> &value, bool valid)
{
    DynVar variable(VariableType::INTEGER_VAR);

    for(auto iter = value.cbegin(); iter != value.cend(); iter++) {
        IntegerVar elem{*iter};
        variable.append(elem);}
    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, long value, bool valid)
{
    LongVar variable{value};

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, float value, bool valid)
{
    FloatVar variable{value};

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, bool value, bool valid)
{
    BitVar variable{value};

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint(const std::string &name, std::string value, bool valid)
{
    TextVar variable{CharString(value.c_str())};

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

bool WinCCWrapper::set_datapoint_time(const std::string &name, time_t value, bool valid)
{
    TimeVar variable(0,0);
    variable.setSeconds(value);

    return manager->set_datapoint(name + DP_SUFFIX, variable, valid);
}

boost::any WinCCWrapper::get_datapoint_any (const std::string &name){
    boost::any datapoint_value;
    manager->get_datapoint_any(name + DP_SUFFIX, datapoint_value);
    return datapoint_value;
}

// get_datapoint
template <typename T>
bool WinCCWrapper::get_datapoint(const std::string &name, T &value)
{
    return manager->get_datapoint(name + DP_SUFFIX, value);
}

int WinCCWrapper::get_datapoint_int(const std::string &name)
{
    int value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

boost::python::list WinCCWrapper::get_datapoint_list(const std::string &name)
{
    boost::python::list value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

std::vector<int> WinCCWrapper::get_datapoint_vector(const std::string &name)
{
    std::vector<int> value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

long WinCCWrapper::get_datapoint_long(const std::string &name)
{
    long value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

float WinCCWrapper::get_datapoint_float(const std::string &name)
{
    float value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

bool WinCCWrapper::get_datapoint_bool(const std::string &name)
{
    bool value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

std::string WinCCWrapper::get_datapoint_string(const std::string &name)
{
    std::string value;
    if(get_datapoint(name, value))
        return value;
    throw std::runtime_error("Could not get datapoint");
}

time_t WinCCWrapper::get_datapoint_time(const std::string &name)
{
    struct tm value;
    if(get_datapoint(name, value))
        return mktime(&value);
    throw std::runtime_error("Could not get datapoint");
}

std::string WinCCWrapper::get_formatted_datapoint(const std::string &name){
    std::string value;
    if(manager->get_datapoint(name, value)){
        return value;
    }
    throw std::runtime_error("Could not get datapoint");
}

time_t WinCCWrapper::get_datapoint_set_time(const std::string &name){
    struct tm value;
    if(manager->get_datapoint(name + DP_SUFFIX_STIME, value))
        return mktime(&value);
    throw std::runtime_error("Could not get datapoint");
}

bool WinCCWrapper::set_datapoint_valid(const std::string &name)
{
    return manager->set_datapoint_valid(name + DP_SUFFIX);
}

bool WinCCWrapper::set_datapoint_invalid(const std::string &name)
{
    return manager->set_datapoint_invalid(name + DP_SUFFIX);
}

bool WinCCWrapper::set_datapoint_any(const std::string &name, boost::any value){
    return manager->set_datapoint_any(name + DP_SUFFIX, value);
}
    } // namespace WINCCWRAPPER
} // namespace LOFAR
