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

#include <sstream>

#include <StartDpInitSysMsg.hxx>

#include "WinCCManager.h"
#include "ConnectWaitForAnswer.h"
#include <DrvManager.hxx>
#include <PeriphAddr.hxx>
#include <AbstractHWMapper.hxx>
#include <BitVar.hxx>
#include <TimeVar.hxx>
#include <Variable.hxx>
#include <IntegerVar.hxx>
#include <LongVar.hxx>
#include <TextVar.hxx>
#include <DynVar.hxx>
#include <DynPtrArray.hxx>
#include <Resources.hxx>
#include <cassert>
#include <vector>
#include <boost/python.hpp>

#include <Manager.hxx>
#include <DpElement.hxx>
#include <DpIdentification.hxx>
#include <DpIdentificationResultType.hxx>
#include <boost/any.hpp>
#include <exceptions.h>

namespace LOFAR {
    namespace WINCCWRAPPER {

using namespace std;

volatile bool WinCCManager::doExit = false;

WinCCManager::WinCCManager() :
    Manager(ManagerIdentifier(API_MAN, Resources::getManNum()))
{
    init();
}

void WinCCManager::init()
{
    // First connect to Data manager.
    // We want Typecontainer and Identification so we can resolve names
    // This call succeeds or the manager will exit
    connectToData(StartDpInitSysMsg::TYPE_CONTAINER | StartDpInitSysMsg::DP_IDENTIFICATION);

    // While we are in STATE_INIT we are initialized by the Data manager
    while (getManagerState() == STATE_INIT)
    {
        // Wait max. 1 second in select to receive next message from data.
        // It won't take that long...
        long sec=1, usec=0;
        dispatch(sec, usec);
    }

    // We are now in STATE_ADJUST and can connect to Event manager
    // This call will succeed or the manager will exit
    connectToEvent();
}

void WinCCManager::connect_datapoints(const std::vector<std::string> &dataPoints)
{
    for(vector<string>::const_iterator it = dataPoints.begin(); it != dataPoints.end(); it++)
    {
        DpIdentList  dpList;
        DpIdentifier dpIdConnect;

        if (Manager::getId(it->c_str(), dpIdConnect) == PVSS_FALSE)
        {
            // This name was unknown
            ErrHdl::error(ErrClass::PRIO_SEVERE,
                          ErrClass::ERR_PARAM,
                          ErrClass::UNEXPECTEDSTATE,
                          "PublishManager",
                          "connect_datapoints",
                          CharString("Datapoint ") + CharString(it->c_str()) +
                          CharString(" missing"));
        }
        else
        {
            dpList.append(dpIdConnect);
            // We give the dpConnect a nice naked pointer because it will delete it when the manager stops.
            HotLinkWaitForAnswer* wait = new ConnectWaitForAnswer();
            Manager::dpConnect(dpList, wait);
        }
    }
}

void WinCCManager::connect_datapoints_multiple(const std::vector<std::string> &dataPoints)
{

    DpIdentList  dpList;
    for(vector<string>::const_iterator it = dataPoints.begin(); it != dataPoints.end(); it++)
    {
        DpIdentifier dpIdConnect;

        if (Manager::getId(it->c_str(), dpIdConnect) == PVSS_FALSE)
        {
            // This name was unknown
            ErrHdl::error(ErrClass::PRIO_SEVERE,
                          ErrClass::ERR_PARAM,
                          ErrClass::UNEXPECTEDSTATE,
                          "PublishManager",
                          "connect_datapoints",
                          CharString("Datapoint ") + CharString(it->c_str()) +
                          CharString(" missing"));
        }
        else
        {
            dpList.append(dpIdConnect);

        }
    }
    // We give the dpConnect a nice naked pointer because it will delete it when the manager stops.
    HotLinkWaitForAnswer* wait = new ConnectWaitForAnswer(true);
    Manager::dpConnect(dpList, wait);
}


void WinCCManager::disconnect_datapoints(const std::vector<std::string> &dataPoints)
{
    for(vector<string>::const_iterator it = dataPoints.begin(); it != dataPoints.end(); it++)
    {
        DpIdentifier dpIdConnect;

        if (Manager::getId(it->c_str(), dpIdConnect) == PVSS_FALSE)
        {
            // This name was unknown
            ErrHdl::error(ErrClass::PRIO_SEVERE,
                          ErrClass::ERR_PARAM,
                          ErrClass::UNEXPECTEDSTATE,
                          "PublishManager",
                          "connect_datapoints",
                          CharString("Datapoint ") + CharString(it->c_str()) +
                          CharString(" missing"));
        }
        else
        {
            // We give the dpConnect a nice naked pointer because it will delete it when the manager stops.
            HotLinkWaitForAnswer* wait = new ConnectWaitForAnswer();
            Manager::dpDisconnect(dpIdConnect, wait);
        }
    }
}

bool WinCCManager::set_datapoint(const std::string &name, const Variable &value, bool valid)
{
    //reuse the set_datapoint_validity, and explicitly set the value to the given value
    return set_datapoint_validity(name, valid, &value);
}


// request the query (async). is called by _get_query which makes it blocking (synchronous) by waiting for the answer.
bool WinCCManager::request_query_result(const std::string &query, PVSSulong & identifier)
{
    HotLinkWaitForAnswer* wait = new ConnectWaitForAnswer();
    return (PVSS_TRUE == Manager::dpQuery(query.c_str(), identifier, wait));
}

// request the datapoint (async). is called by _get_datapoint which makes it blocking (synchronous) by waiting for the answer.
bool WinCCManager::request_datapoint(const std::string &name)
{
    DpIdentifier dpId;

    if (Manager::getId(name.c_str(), dpId) == PVSS_FALSE)
    {
        // This name was unknown.
        ErrHdl::error(ErrClass::PRIO_SEVERE,
                      ErrClass::ERR_PARAM,
                      ErrClass::UNEXPECTEDSTATE,
                      "WinCCManager",
                      "get_datapoint",
                      CharString("Datapoint ") + CharString(name.c_str()) +
                      CharString(" missing"));
        return false;
    }

    HotLinkWaitForAnswer* wait = new ConnectWaitForAnswer();
    return (PVSS_TRUE == Manager::dpGet(dpId, wait));
}

void WinCCManager::handle_get(const std::string &name, Variable *&value)
{
    values[name] = value;
}

bool WinCCManager::has_received_variable(const std::string &name)
{
    std::map<string, Variable*>::iterator it;

    it = values.find(name);

    return (it != values.end());
}

bool WinCCManager::get_received_variable(const std::string &name, Variable *&value)
{
    assert(value == nullptr);

    std::map<string, Variable*>::iterator it;

    it = values.find(name);

    if(it != values.end())
    {
        value = it->second;
        values.erase(it);
        return true;
    }

    return false;
}

bool WinCCManager::wait_for_received_variable(const std::string &name, unsigned long msec_timeout)
{
    clock_t start_time = clock();

    long sec=0, usec=10000;

    while(!has_received_variable(name)) {
        dispatch(sec, usec);

        clock_t now = clock();
        unsigned long elapsed = (1000*(now-start_time))/(CLOCKS_PER_SEC);
        if(elapsed >= msec_timeout) {
            ErrHdl::error(ErrClass::PRIO_SEVERE,
                          ErrClass::ERR_PARAM,
                          ErrClass::UNEXPECTEDSTATE,
                          "WinCCManager",
                          "wait_for_received_variable",
                          CharString("timeout while waiting for requested datapoint ") + CharString(name.c_str()));

            return false;
        }
    }
    return true;
}


bool WinCCManager::get_datapoint_variable(const std::string &name, Variable *&variable_value)
{
    assert(variable_value == nullptr);

    //sometimes the Manager prepends text to the name in its answers
    //so make sure we use the correct name from the manager by looking up the dpId...
    DpIdentifier dpId;
    if (Manager::getId(name.c_str(), dpId) == PVSS_FALSE)
    {
        // This name was unknown.
        ErrHdl::error(ErrClass::PRIO_SEVERE,
                      ErrClass::ERR_PARAM,
                      ErrClass::UNEXPECTEDSTATE,
                      "WinCCManager",
                      "get_datapoint",
                      CharString("Datapoint ") + CharString(name.c_str()) +
                      CharString(" missing"));
        return false;
    }

    //...and then reverse lookup the manager's verion of the name
    CharString man_dp_name = "";
    Manager::getName(dpId, man_dp_name); //should always succeed as we just received the dpId from the manager

    std::string the_name(man_dp_name.c_str());
    if(request_datapoint(the_name))
    {
        if(wait_for_received_variable(the_name, 1000)) {
            if(get_received_variable(the_name, variable_value)) {
                return true;
            }
        }
    }

    return false;
}

//use template specialization to have a compile time switch
//to convert a Variable of unknown internal type to a typed value
//return the internally created converted_var, so it can be deleted in _get_datapoint
template <typename Tval>
Variable::ConvertResult convert(Variable *var, Tval &value, Variable *&converted_var);

template <>
Variable::ConvertResult convert(Variable *var, boost::python::list& value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::DYNINTEGER_VAR, converted_var);

    if(Variable::ConvertResult::OK == cr)
    {
        DynVar *dv = (DynVar*)converted_var;

        for(unsigned int i = 0; i < dv->getNumberOfItems(); i++) {
            Variable *elem = dv->getAt(i);
            if(elem->inherits(VariableType::INTEGER_VAR)) {
                value.append(((IntegerVar*)elem)->getValue());
            }
            else
                return Variable::ConvertResult::CONV_NOT_DEFINED;
        }
    }
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, std::vector<int> &value, Variable *&converted_var)
{

    Variable::ConvertResult cr = var->convert(VariableType::DYNINTEGER_VAR, converted_var);

    if(Variable::ConvertResult::OK == cr)
    {
        DynVar *dv = (DynVar*)converted_var;
        value.resize(dv->getNumberOfItems());

        for(unsigned int i = 0; i < dv->getNumberOfItems(); i++) {
            Variable *elem = dv->getAt(i);
            if(elem->inherits(VariableType::INTEGER_VAR)) {
                value[i] = ((IntegerVar*)elem)->getValue();
            }
            else
                return Variable::ConvertResult::CONV_NOT_DEFINED;
        }
    }
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, int &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::INTEGER_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr)
        value = ((IntegerVar*)converted_var)->getValue();
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, long &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::LONG_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr)
        value = ((LongVar*)converted_var)->getValue();
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, float &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::FLOAT_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr)
        value = ((FloatVar*)converted_var)->getValue();
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, bool &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::BIT_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr)
        value = ((BitVar*)converted_var)->getValue();

    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, std::string &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::TEXT_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr)
        value = ((TextVar*)converted_var)->getString().c_str();
    return cr;
}

template <>
Variable::ConvertResult convert(Variable *var, struct tm &value, Variable *&converted_var)
{
    Variable::ConvertResult cr = var->convert(VariableType::TIME_VAR, converted_var);
    if(Variable::ConvertResult::OK == cr) {
        time_t time_val = ((TimeVar*)converted_var)->getSeconds();
        struct tm *tmp_tm;
        tmp_tm = gmtime(&time_val);
        value = *tmp_tm;
    }

    return cr;
}

boost::any convert_any(Variable * variable, boost::any & value){
    Variable * converted_variable{nullptr};
    switch(variable->isA()){
        case VariableType::INTEGER_VAR:{
            int casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::FLOAT_VAR: {
            float casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::TEXT_VAR: {
            std::string casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::LONG_VAR:{
            // Find the wincc guy who though this out
            long casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::BIT_VAR: {
            bool casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::TIME_VAR: {
            time_t casted_variable;
            convert(variable, casted_variable, converted_variable);
            value = casted_variable;

            break;
        }
        case VariableType::ANYTYPE_VAR: {
            const AnyTypeVar * converted_var{static_cast<AnyTypeVar*>(variable)};
            convert_any(converted_var->getVar(), value);
            break;
        }
        case VariableType::DPIDENTIFIER_VAR: {
            value = std::string{variable->formatValue().c_str()};
            break;
        }
        default:
            CharString value_str = variable->formatValue();
            std::cerr<<value_str;
            std::cerr<<"Datapoint type still not supported:  "<<std::hex<<variable->isA()<<std::endl;
            value = std::string{value_str.c_str()};
    }

    if(converted_variable != nullptr) delete converted_variable;
    return true;
}

//internal generic method to get the typed (Tval) value of a datapoint
//used by the public strictly typed methods
template <typename Tval>
bool WinCCManager::_get_datapoint(const std::string &name, Tval &value)
{
    Variable *var = NULL;
    if(get_datapoint_variable(name, var))
    {
        VariablePtr converted_var = NULL;
        Variable::ConvertResult cr = convert(var, value, converted_var);
        if(Variable::ConvertResult::OK == cr || Variable::ConvertResult::OUT_OF_RANGE == cr)
        {
            delete converted_var;  //delete it, since it was a newly created variable in var->convert
            delete var;  //delete it, since it was a cloned variable created in get_datapoint_variable
            return (Variable::ConvertResult::OK == cr);
        }
        delete var;  //delete it, since it was a cloned variable created in get_datapoint_variable
    }

    return false;
}

bool convert_to_vector2(Variable * variable, std::vector<std::vector<std::string>> & result){
    if(variable->isA(VariableType::DYN_VAR)){
        const DynVar * rows{static_cast<DynVar *>(variable)};
        for(DynPtrArrayIndex i=0; i < rows->getNumberOfItems(); i++){
            const DynVar * row{static_cast<DynVar *>(rows->getAt(i))};
            std::vector<std::string> * current_row{new std::vector<std::string>{}};
            Variable * column{static_cast<DynVar *>(row->getNext())};
            while(column){
                current_row->push_back(column->formatValue().c_str());
                column = static_cast<DynVar *>(row->getNext());
            }
            result.push_back(*current_row);
            row = static_cast<DynVar *>(rows->getNext());
        }
        return true;
    }
    return false;
}

//internal generic method to query a set of WinCC data points. Since the type is not previously know
bool WinCCManager::get_query(const std::string &query, std::vector<std::vector<std::string>> & result){
    Variable * variable_value = nullptr;
    PVSSulong identifier;
    if(request_query_result(query, identifier))
    {
        std::string identifier_str{std::to_string(identifier)};
        if(wait_for_received_variable(identifier_str, 1000)) {
            if(get_received_variable(identifier_str, variable_value)) {
                convert_to_vector2(variable_value, result);
                return true;
            }
        }
    }

    return false;
}

//below, a few strictly type methods for get_datapoint are defined
//they just call the templated _get_datapoint, so why not just use the one and only templated method?
//because with these strictly type methods, we force the compiler to define the methods for these types
//so they can be found when called from a dynamicaly type language like python.
//see the WinCCWrapper_boost_python file.
bool WinCCManager::get_datapoint(const std::string &name, int &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, long &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, float &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, bool &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, std::string &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, struct tm &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, boost::python::list &value)
{
    return _get_datapoint(name, value);
}

bool WinCCManager::get_datapoint(const std::string &name, std::vector<int> &value)
{
    return _get_datapoint(name, value);
}


bool WinCCManager::set_datapoint_validity(const std::string &name, bool validity, const Variable *value)
{
    DpIdentifier dpId;

    if (Manager::getId(name.c_str(), dpId) == PVSS_FALSE)
    {
        // This name was unknown.
        ErrHdl::error(ErrClass::PRIO_SEVERE,
                      ErrClass::ERR_PARAM,
                      ErrClass::UNEXPECTEDSTATE,
                      "WinCCManager",
                      "set_datapoint_validity",
                      CharString("Datapoint ") + CharString(name.c_str()) +
                      CharString(" missing"));
        return false;
    }

    //determine if we need to use the given value, or get the last known value
    Variable *last_known_value = NULL;
    if(value == NULL) {
        //obtain last known value, needs to be deleted later
        get_datapoint_variable(name, last_known_value);
    }

    if(value != NULL || last_known_value != NULL)
    {
        TimeVar now;
        BitVec infoBits;
        if(!validity) {
            infoBits.set(DriverBits::DRV_INVALID);
            infoBits.set(DriverBits::DRV_VALID_INVALID);
        }

        // get VariableType from DpIdentifier
        //   assign values
        VariableType dpId_VariableType;
        DpElementType dpId_ElementType;

        DpIdentification temp_dpId;  // make a temp dpId to use the 'getElementType' method
        DpIdentificationResult dir = temp_dpId.getElementType(dpId, dpId_ElementType);

        //   check that the dpIdResult is OK
        if(DpIdentificationResult::DpIdentOK == dir) {
            dpId_VariableType = DpElement::getVariableType(dpId_ElementType);
        }
        else {
            return false;
        }

        // check that the VariableType of the datapoint identifier matches the VariableType of the value given.
        // if not, convert value to the appropriate datapoint type
        if (value->isA() != dpId_VariableType){

            VariablePtr converted_var = NULL;
            Variable::ConvertResult cr = value->convert(dpId_VariableType, converted_var);

            // if conversion succeeds, send the converted var
            if(Variable::ConvertResult::OK == cr) {
                DrvManager *drvman = DrvManager::getSelfPtr();
                drvman ->sendVCMsg(dpId, converted_var!=NULL ? *converted_var : *last_known_value, now, infoBits);
                delete converted_var;  //delete it, since it was a newly created variable in var->convert
            }

            // Either 'out_of_bounds' error or 'conv_not_defined' error in converting
            else {
                delete converted_var;  //delete it, since it was a newly created variable in var->convert
                return false;
            }
        }

        // no need for conversion
        else {
            DrvManager *drvman = DrvManager::getSelfPtr();
            drvman ->sendVCMsg(dpId, value!=NULL ? *value : *last_known_value, now, infoBits);
        }

        //process, wait max 10 ms
        long sec=0, usec=10000;
        dispatch(sec, usec);

        if(last_known_value != NULL) {
            //we obtained the last known value...
            //delete it, since it was a cloned variable created in get_datapoint_variable
            delete last_known_value;
        }
        return true;
    }
    return false;
}


void WinCCManager::run()
{
    // Let Manager handle SIGINT and SIGTERM (Ctrl+C, kill)
    // Manager::sigHdl will call virtual function Manager::signalHandler
    signal(SIGINT,  Manager::sigHdl);
    signal(SIGTERM, Manager::sigHdl);

    // Now loop until we are finished
    while ( true )
    {
        // Exit flag set ?
        if (doExit)
            return;

        //process, wait max 100 ms
        long sec=0, usec=100000;
        dispatch(sec, usec);
    }
}

void WinCCManager::wait_for_event(long sec, long microSec){
    dispatch(sec, microSec);
}

void WinCCManager::exit()
{
    Manager::exit(0);
}

void WinCCManager::handle_hotlink(const std::string &name, const std::string &value)
{
    if(callback)
    {
        callback(name, value);
    }
}

void WinCCManager::handle_hotlink(const std::map<std::string, std::string> & values)
{
    if(callback_multi)
    {
        callback_multi(values);
    }
}

void WinCCManager::signalHandler(int sig)
{
    if ((sig == SIGINT) || (sig == SIGTERM))
    {
        WinCCManager::doExit = true;
    }
    else
    {
        Manager::signalHandler(sig);
    }
}

bool WinCCManager::set_datapoint_any(const std::string &datapoint_name, const boost::any &value){
    Variable * variable{nullptr};

    if(get_datapoint_variable(datapoint_name, variable)){
        switch(variable->isA()){
            case VariableType::INTEGER_VAR: {
                    IntegerVar converted_value{boost::any_cast<int>(value)};
                    set_datapoint(datapoint_name, converted_value);
                    break;
                }
            case VariableType::FLOAT_VAR: {
                    FloatVar converted_value{boost::any_cast<float>(value)};
                    set_datapoint(datapoint_name, converted_value);
                    break;
                }
            case VariableType::TEXT_VAR: {
                    TextVar converted_value{CharString(boost::any_cast<std::string>(value).c_str())};
                    set_datapoint(datapoint_name, converted_value);
                    break;
                }
            case VariableType::LONG_VAR:{
                    LongVar converted_value{boost::any_cast<long>(value)};
                    set_datapoint(datapoint_name, converted_value);

                    break;
                }
            case VariableType::BIT_VAR: {
                    BitVar converted_value{boost::any_cast<bool>(value)};
                    set_datapoint(datapoint_name, converted_value);

                    break;
                }
            case VariableType::TIME_VAR: {
                    TimeVar converted_value(0,0);
                    converted_value.setSeconds(boost::any_cast<time_t>(value));
                    set_datapoint(datapoint_name, converted_value);

                    break;
                }
            default:
                std::cerr<<"Datapoint type still not supported:  "<<std::hex<<variable->isA()<<std::endl;
                return false;
        }
    }else{
        return false;
    }

    return true;
}

bool WinCCManager::get_datapoint_any(const std::string &datapoint_name, boost::any & value){
    // Yeah I know... WinCC API is getting a &* to allocate the memory space...
    Variable * variable{nullptr};
    bool returnValue{true};

    if(!get_datapoint_variable(datapoint_name, variable)){
        // This name was unknown.
        ErrHdl::error(ErrClass::PRIO_SEVERE,
                      ErrClass::ERR_PARAM,
                      ErrClass::UNEXPECTEDSTATE,
                      Resources::getProgName(),
                      "get_datapoint",
                      CharString("Datapoint ") + CharString(datapoint_name.c_str()) +
                      CharString(" missing"));
        throw DatapointNameNotFound{datapoint_name};
    }

    convert_any(variable, value);

    if(variable != nullptr) delete variable;

    return returnValue;

}

    } // namespace WINCCWRAPPER
} // namespace LOFAR

