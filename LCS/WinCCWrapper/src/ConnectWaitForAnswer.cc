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

#include "ConnectWaitForAnswer.h"
#include "WinCCManager.h"

namespace LOFAR {
  namespace WINCCWRAPPER {

using namespace std;

ConnectWaitForAnswer::ConnectWaitForAnswer(const bool handle_multi): HotLinkWaitForAnswer{}, multi{handle_multi}{

}

ConnectWaitForAnswer::ConnectWaitForAnswer(): HotLinkWaitForAnswer{}{

}

void ConnectWaitForAnswer::hotLinkCallBack(DpMsgAnswer &answer)
{
    const std::string answer_id{std::to_string(answer.getAnswerId())};
    for (AnswerGroup *grpPtr = answer.getFirstGroup(); grpPtr; grpPtr = answer.getNextGroup())
    {
        if (grpPtr->getError())
        {
            cout <<grpPtr->getError()->toString()<< endl;
        }
        else
        {
            for (DpVCItem * item = grpPtr->getFirstItem(); item; item = grpPtr->getNextItem())
            {
                Variable *varPtr = item->getValuePtr();

                if(varPtr)
                {
                    string name = get_datapoint_name(item);
                    if(name.compare("") == 0) name += answer_id;

                    Variable *value = varPtr->clone(); //WinCCManager should delete cloned pointer

    	            ((WinCCManager *) Manager::getManPtr())->handle_get(name, value);
                }
            }
        }
    }
}

void ConnectWaitForAnswer::hotLinkCallBack(DpHLGroup &group)
{
    if(multi){
        handle_multi(group);
    }else{
        handle_one_by_one(group);
    }
}
void ConnectWaitForAnswer::handle_one_by_one(DpHLGroup &group)
{
    for (DpVCItem *item = group.getFirstItem(); item; item = group.getNextItem())
    {
        handle_group_item(item);
    }
}

void ConnectWaitForAnswer::handle_multi(DpHLGroup &group)
{

    std::map<std::string, std::string> values;
    for (DpVCItem *item = group.getFirstItem(); item; item = group.getNextItem())
    {
        Variable *varPtr = item->getValuePtr();

        if (varPtr){
            const string name = get_datapoint_name(item);
            const string value = varPtr->formatValue().c_str();

            values[name] = value;
        }
    }
    ((WinCCManager *) Manager::getManPtr())->handle_hotlink(values);
}


void ConnectWaitForAnswer::handle_group_item(const DpVCItem* const item)
{
    Variable *varPtr = item->getValuePtr();

    if (varPtr)
    {
        string name = get_datapoint_name(item);

        string value = varPtr->formatValue().c_str();

    	((WinCCManager *) Manager::getManPtr())->handle_hotlink(name, value);
    }
}

std::string ConnectWaitForAnswer::get_datapoint_name(const DpVCItem* const item)
{
    DpIdentifier dpIdentifier = item->getDpIdentifier();

    CharString name = "";

    Manager::getName(dpIdentifier, name);

    return name.c_str();
}

  } // namespace WINCCWRAPPER
} // namespace LOFAR
