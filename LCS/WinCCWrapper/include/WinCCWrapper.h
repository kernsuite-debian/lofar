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

#ifndef WINCCSERVICES_WINCC_WRAPPER_H
#define WINCCSERVICES_WINCC_WRAPPER_H

#include <string>
#include <boost/variant.hpp>
#include <vector>
#include <ctime>
#include <functional>

#include "WinCCResources.h"
#include "WinCCManager.h"

#include <boost/python.hpp>
#include <boost/any.hpp>

namespace LOFAR {
    namespace WINCCWRAPPER {

/*! The WinCCWrapper provides a simple API to set/get datapoints in a wincc database via a running wincc instance.
 */
class WinCCWrapper
{
public:
    //! default constructor
    WinCCWrapper(const std::string &project_name);

    //! default constructor
    WinCCWrapper(const std::string &program_name, const std::string &project_name, const int num);
    //! disconnect from the running wincc instance.
    void exit();
    //! connect to the running wincc instance.
    void run();

    //! subscribe for changes on this list of datapoints. Whenever any of these datapoints changes value, the callback function from set_connect_datapoints_callback is called with the changed datapoint name and value.
    void connect_datapoints(const std::vector<std::string> &data_points);
    //! subscribe for changes on this list of datapoints. Whenever any of these datapoints changes value, the callback function from set_connect_datapoints_callback is called with all the specified values.
    void connect_datapoints_multi(const std::vector<std::string> &data_points);

    //! unsubscribe for changes on the given list of datapoints.
    void disconnect_datapoints(const std::vector<std::string> &data_points);
    //! provide your callback function which is called whenever any of the connected datapoints is changed.
    void set_connect_datapoints_callback(std::function<void(std::string name, std::string value)> callback);
    //! provide your callback function which is called whenever any of the connected datapoints is changed. It returns all the specified datapoints even if only one changes.
    void set_connect_datapoints_callback(std::function<void(std::map<std::string, std::string>)> callback);

    //! set the datapoint with given name to the given int value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, int value, bool valid=true);
    //! set the datapoint with given name to the given boost::python::list value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, boost::python::list &value, bool valid=true);
    //! set the datapoint with given name to the given boost::python::tuple value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, boost::python::tuple &value, bool valid=true);
    //! set the datapoint with given name to the given std::vector<int> value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, std::vector<int> &value, bool valid=true);

    //! set the datapoint with given name to the given long value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, long value, bool valid=true);
    //! set the datapoint with given name to the given float value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, float value, bool valid=true);
    //! set the datapoint with given name to the given bool value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, bool value, bool valid=true);
    //! set the datapoint with given name to the given string value, mark it valid/invalid, returns true upon success.
    bool set_datapoint(const std::string &name, std::string value, bool valid=true);
    //! set the datapoint with given name to the given time_t value, mark it valid/invalid, returns true upon success.
    bool set_datapoint_time(const std::string &name, time_t value, bool valid=true);

    bool set_datapoint_any(const std::string &name, boost::any value);
    //! mark the datapoint with given name valid.
    bool set_datapoint_valid(const std::string &name);
    //! mark the datapoint with given name invalid.
    bool set_datapoint_invalid(const std::string &name);

    //! provide the boost::any for the given datapoint name
    boost::any get_datapoint_any (const std::string &name);
    //! get the datapoint with the given name and return it as an int value if possible, otherwise an exception is raised.
    int get_datapoint_int(const std::string &name);
    //! get the datapoint with the given name and return it as a long value if possible, otherwise an exception is raised.
    long get_datapoint_long(const std::string &name);
    //! get the datapoint with the given name and return it as a float value if possible, otherwise an exception is raised.
    float get_datapoint_float(const std::string &name);
    //! get the datapoint with the given name and return it as a bool value if possible, otherwise an exception is raised.
    bool get_datapoint_bool(const std::string &name);
    //! get the datapoint with the given name and return it as a string value if possible, otherwise an exception is raised.
    std::string get_datapoint_string(const std::string &name);
    //! get the datapoint with the given name and return it as a time_t value if possible, otherwise an exception is raised.
    time_t get_datapoint_time(const std::string &name);
    //! get the datapoint with the given name and return it as a boost::python::list value if possible, otherwise an exception is raised.
    boost::python::list get_datapoint_list(const std::string &name);
    //! get the datapoint last set time
    time_t get_datapoint_set_time(const std::string &name);
    //! get the datapoint with the given name and return it as a std::vector<int> value if possible, otherwise an exception is raised.
    //! this method is used in the WinCCGet test
    std::vector<int> get_datapoint_vector(const std::string &name);
    //! get the datapoint with the given name and return it as a std::vector<std::string> value.
    std::vector<std::string> get_datapoint_vector_string(const std::string &name);

    std::string get_formatted_datapoint(const std::string &name);
    void wait_for_event(long sec, long microSec);
private:
    // get_datapoint
    template <typename T>
    bool get_datapoint(const std::string &name, T &value);

    WinCCResources resources;
    WinCCManager* manager;
};

    } // namespace WINCCWRAPPER
} // namespace LOFAR

#endif
