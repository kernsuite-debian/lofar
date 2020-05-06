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

#ifndef WINCCSERVICES_WINCC_MANAGER_H
#define WINCCSERVICES_WINCC_MANAGER_H

#include <string>
#include <vector>
#include <ctime>
#include <functional>
#include <mutex>
#include <condition_variable>

#include <Manager.hxx>
#include <Variable.hxx>

#include <boost/python.hpp>
#include <boost/any.hpp>

namespace LOFAR {
    namespace WINCCWRAPPER {

/*! The WinCCManager derives from the Manager class from the WinCC_OA API and defines a simplified API for setting/getting datapoints and connecting to datapoint changes. This class is used by the WinCCWrapper class, and is not intended to be used externally.*/
class WinCCManager : public Manager
{
public:
    //! default constructor
    WinCCManager();
    //! run the manager, connect to the running wincc instance.
    void run();
    //! exit the manager, disconnect from the running wincc instance.
    void exit();

    //! subscribe for changes on this list of datapoints. Whenever any of these datapoints changes value, the callback function from set_connect_datapoints_callback is called with the changed datapoint name and value.
    void connect_datapoints(const std::vector<std::string> &data_points);
    //! subscribe for changes on this list of datapoints. Whenever any of these datapoints change all the values from these datapoints gets returned in one call.
    void connect_datapoints_multiple(const std::vector<std::string> &data_points);
    //! unsubscribe for changes on this list of datapoints.
    void disconnect_datapoints(const std::vector<std::string> &data_points);
    //! provide your callback function which is called whenever any of the connected datapoints is changed.
    void set_connect_datapoints_callback(std::function<void(std::string name, std::string value)> callback_functor) {callback = callback_functor;};
    //! provide your callback function which is called whenever any of the connected datapoints is changed.
    void set_connect_datapoints_callback(std::function<void(std::map<std::string, std::string>)> callback_functor) {callback_multi = callback_functor;};


    //! set the datapoint with given name to the given value, returns true upon success.
    /*! set the datapoint with given name to the given value
     * The value can take any plain datatype, like int, long, float, etc.
     * Indicate wheter this value is valid or not (by default true)
     * returns true upon success.
     * */
    bool set_datapoint(const std::string &name, const Variable &value, bool valid=true);
    //! get the datapoint with the given name and return it's int value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, int &value);
    //! get the datapoint with the given name and return it's long value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, long &value);
    //! get the datapoint with the given name and return it's float value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, float &value);
    //! get the datapoint with the given name and return it's bool value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, bool &value);
    //! get the datapoint with the given name and return it's string value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, std::string &value);
    //! get the datapoint with the given name and return it's tm value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, struct tm &value);
    //! get the datapoint with the given name and return it's boost::python::list value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, boost::python::list &value);
    //! get the datapoint with the given name and return it's std::vector<int> value in parameter value. returns true upon success.
    bool get_datapoint(const std::string &name, std::vector<int> &value);
    //! get the datapoint with a any type
    bool get_datapoint_any(const std::string &datapoint_name, boost::any &value);
    //! set the datapoint with a any type
    bool set_datapoint_any(const std::string &datapoint_name, const boost::any &value);
    //! mark the datapoint with given name valid. returns true upon success.
    bool set_datapoint_valid(const std::string &name) { return set_datapoint_validity(name, true, nullptr); }
    //! mark the datapoint with given name invalid. returns true upon success.
    bool set_datapoint_invalid(const std::string &name) { return set_datapoint_validity(name, false, nullptr); }
    //! set the datapoint with given name valid/invalid. returns true upon success.
    bool set_datapoint_validity(const std::string &name, bool validity, const Variable *value=nullptr);

    bool get_query(const std::string &query, std::vector<std::vector<std::string>> & result);
    //! handle signals to exit nicely
    virtual void signalHandler(int sig);

    void wait_for_event(long sec, long microSec);

private:
    void init();

    friend class ConnectWaitForAnswer;

    void handle_hotlink(const std::string &name, const std::string &value);
    void handle_hotlink(const std::map<std::string, std::string> &);

    void handle_get(const std::string &name, Variable *&value);

    bool request_datapoint(const std::string &name);

    bool request_query_result(const std::string &query, PVSSulong & identifier);
    template <typename Tval>
    bool _get_datapoint(const std::string &name, Tval &value);

    template <typename Tval>
    bool _get_datapoint(const std::string &name, Tval *value);


    bool get_datapoint_variable(const std::string &name, Variable *&value);

    bool has_received_variable(const std::string &name);
    bool get_received_variable(const std::string &name, Variable *&value);
    bool wait_for_received_variable(const std::string &name, unsigned long msec_timeout=10000);

    volatile static bool doExit;
    std::function<void(std::string name, std::string value)> callback;
    std::function<void(std::map<std::string, std::string>)> callback_multi;
    std::mutex mtx;
    std::condition_variable cv;
    std::map<std::string, Variable *> values;
};

    } // namespace WINCCWRAPPER
} // namespace LOFAR

#endif
