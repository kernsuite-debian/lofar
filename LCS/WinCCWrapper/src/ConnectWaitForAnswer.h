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

#ifndef CONNECT_WAIT_FOR_ANSWER_H
#define CONNECT_WAIT_FOR_ANSWER_H

#include <string>

#include <HotLinkWaitForAnswer.hxx>
#include <DpMsgAnswer.hxx>
#include <DpHLGroup.hxx>

namespace LOFAR {
    namespace WINCCWRAPPER {

class ConnectWaitForAnswer : public HotLinkWaitForAnswer
{
public:
    ConnectWaitForAnswer();
    ConnectWaitForAnswer(const bool handle_multi);
    using HotLinkWaitForAnswer::hotLinkCallBack;
    virtual void hotLinkCallBack(DpMsgAnswer &answer);
    virtual void hotLinkCallBack(DpHLGroup &group);
private:
    bool multi;
    void handle_one_by_one(DpHLGroup &group);
    void handle_multi(DpHLGroup &group);
    void handle_group_item(const DpVCItem* const item);
    std::string get_datapoint_name(const DpVCItem* const item);

};

    } // namespace WINCCWRAPPER
} // namespace LOFAR

#endif
