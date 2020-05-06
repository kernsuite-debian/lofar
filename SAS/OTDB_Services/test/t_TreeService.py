#!/usr/bin/env python3
#coding: iso-8859-15
#
# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: Backtrace.cc 31468 2015-04-13 23:26:52Z amesfoort $
"""
RPC functions that allow access to (VIC) trees in OTDB.

TaskSpecificationRequest: get the specification(parset) of a tree as dict.
KeyUpdateCommand        : function to update the value of multiple (existing) keys.
StatusUpdateCommand     : finction to update the status of a tree.
"""

from lofar.sas.otdb.TreeService import create_service
from lofar.messaging import TemporaryExchange, RPCClient, BusListenerJanitor
from lofar.sas.otdb.testing.otdb_common_testing import OTDBTestInstance

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

with OTDBTestInstance('t_TreeService.in.unittest_db.dump.gz') as test_db:
    def do_rpc_catch_exception(exc_text, rpc_instance, method_name, arg_dict):
        try:
            print("** Executing {0}({1})...".format(method_name, arg_dict))
            rpc_instance.execute(method_name=method_name, **arg_dict)
            raise Exception("Expected an exception {0}, didn't get any".format(exc_text))
        except Exception:
            print("Caught expected exception {0}".format(exc_text))
        print("======")

    def do_rpc(rpc_instance, method_name, arg_dict):
        print("** Executing {0}({1})...".format(method_name, arg_dict))
        answer = rpc_instance.execute(method_name=method_name, **arg_dict)
        print("result =", answer)
        print("======")
        return answer

    with TemporaryExchange(__name__) as tmp_exchange:
        exchange = tmp_exchange.address

        with BusListenerJanitor(create_service(exchange=exchange, dbcreds=test_db.dbcreds)) as service:

            with RPCClient(service_name=service.service_name, exchange=exchange, timeout=10) as otdbRPC:    # Existing: otdb_id:1099268, mom_id:353713
                do_rpc(otdbRPC, "TaskGetIDs", {'OtdbID': 1099268, 'MomID': 353713 })
                do_rpc(otdbRPC, "TaskGetIDs", {'OtdbID': 1099268, 'MomID': 5 })
                do_rpc(otdbRPC, "TaskGetIDs", {'OtdbID': 1099268, 'MomID': None })
                do_rpc(otdbRPC, "TaskGetIDs", {'OtdbID': 5, 'MomID': 353713 })
                do_rpc_catch_exception('', otdbRPC, "TaskGetIDs", {'OtdbID': 5, 'MomID': 5 })
                do_rpc_catch_exception('', otdbRPC, "TaskGetIDs", {'OtdbID': 5, 'MomID': None })
                do_rpc(otdbRPC, "TaskGetIDs", {'OtdbID': None, 'MomID': 353713 })
                do_rpc_catch_exception('', otdbRPC, "TaskGetIDs", {'OtdbID': None, 'MomID': 5 })
                do_rpc_catch_exception('', otdbRPC, "TaskGetIDs", {'OtdbID': None, 'MomID': None })

                do_rpc(otdbRPC, "GetDefaultTemplates", {})

                do_rpc(otdbRPC, "SetProject",
                       {'name':"Taka Tuka Land", "title":"Adventure movie", "pi":"Pippi",
                        "co_i":"Mr.Nelson", "contact":"Witje"})

                do_rpc(otdbRPC, "TaskCreate", {'OtdbID':1099268, 'TemplateName':'BeamObservation', 'Specification': {'state':'finished'}})
                do_rpc(otdbRPC, "TaskCreate", {'MomID':353713,   'TemplateName':'BeamObservation', 'Specification': {'state':'finished'}})
                do_rpc_catch_exception('on non-exsisting campaign', otdbRPC, "TaskCreate",
                                       {'MomID':998877,   'TemplateName':'BeamObservation',
                                        'CampaignName':'No such campaign', 'Specification': {'state':'finished'}})
                do_rpc(otdbRPC, "TaskCreate", {'MomID':998877,   'TemplateName':'BeamObservation',
                                     'CampaignName':'Taka Tuka Land', 'Specification': {'state':'finished'}})
                data = do_rpc(otdbRPC, "TaskCreate", {'MomID':12345, 'TemplateName':'BeamObservation', 'Specification': {'state':'finished'}})
                new_tree1 = data['MomID']
                data = do_rpc(otdbRPC, "TaskCreate", {'MomID':54321, 'TemplateName':'BeamObservation', 'Specification': {'state':'finished'}})
                new_tree2= data['MomID']

                do_rpc(otdbRPC, "TaskPrepareForScheduling", {'MomID':new_tree1})   # template
                do_rpc(otdbRPC, "TaskPrepareForScheduling", {'MomID':new_tree1})   # now a VIC tree
                do_rpc(otdbRPC, "TaskPrepareForScheduling",
                       {'MomID':new_tree1, 'StartTime':'2016-03-01 12:00:00',
                        'StopTime':'2016-03-01 12:34:56'})
                do_rpc_catch_exception("on invalid stoptime", otdbRPC,
                                       "TaskPrepareForScheduling",
                                       {'MomID':new_tree1, 'StartTime':'2016-03-01 12:00:00',
                                        'StopTime':'2016'})

                do_rpc(otdbRPC, "TaskDelete", {'MomID':new_tree2})

                do_rpc(otdbRPC, "TaskGetSpecification", {'OtdbID':1099269})  # PIC
                do_rpc(otdbRPC, "TaskGetSpecification", {'OtdbID':1099238})	  # Template
                do_rpc(otdbRPC, "TaskGetSpecification", {'OtdbID':1099266})	  # VIC
                do_rpc_catch_exception('on non-existing treeID', otdbRPC,
                                       "TaskGetSpecification", {'OtdbID':5}) # Non existing

                # PIC
                do_rpc(otdbRPC, "TaskSetStatus",
                       {'OtdbID':1099269, 'NewStatus':'finished', 'UpdateTimestamps':True})
                # Template
                do_rpc(otdbRPC, "TaskSetStatus",
                       {'OtdbID':1099238, 'NewStatus':'finished', 'UpdateTimestamps':True})
                # VIC
                do_rpc(otdbRPC, "TaskSetStatus",
                       {'OtdbID':1099266, 'NewStatus':'finished', 'UpdateTimestamps':True})

                # Nonexisting tree
                do_rpc_catch_exception('on invalid treeID', otdbRPC,
                                       "TaskSetStatus",
                                       {'OtdbID':10, 'NewStatus':'finished',
                                        'UpdateTimestamps':True})

                # VIC tree: invalid status
                do_rpc_catch_exception('on invalid status', otdbRPC, "TaskSetStatus",
                                       {'OtdbID':1099266, 'NewStatus':'what_happend',
                                        'UpdateTimestamps':True})
                # Set PIC back to active...
                do_rpc(otdbRPC, "TaskSetStatus",
                       {'OtdbID':1099269, 'NewStatus':'active', 'UpdateTimestamps':True})


                do_rpc(otdbRPC, "GetStations", {})

                # VIC tree: valid
                do_rpc(otdbRPC, "TaskSetSpecification",
                       {'OtdbID':1099266,
                       'Specification':
                           {'LOFAR.ObsSW.Observation.ObservationControl.PythonControl.pythonHost':
                                'NameOfTestHost'}})
                # Template tree: not supported yet
                do_rpc(otdbRPC, "TaskSetSpecification", {'OtdbID':1099238,
                       'Specification':{'LOFAR.ObsSW.Observation.Scheduler.priority':'0.1'}})
                # PIC tree: not supported yet
                do_rpc_catch_exception('on invalid treetype (PIC)', otdbRPC,
                                       "TaskSetSpecification",
                                       {'OtdbID':1099269,
                                        'Specification':{'LOFAR.PIC.Core.CS001.status_state':'50'}})
                # Non exsisting tree
                do_rpc_catch_exception('on invalid treeID', otdbRPC,
                                       "TaskSetSpecification",
                                       {'OtdbID':10,
                                        'Specification':
                                            {'LOFAR.ObsSW.Observation.ObservationControl.PythonControl.pythonHost':'NameOfTestHost'}})
                # VIC tree: wrong key
                do_rpc_catch_exception('on invalid key', otdbRPC, "TaskSetSpecification", {'OtdbID':1099266,
                       'Specification':{'LOFAR.ObsSW.Observation.ObservationControl.PythonControl.NoSuchKey':'NameOfTestHost'}})

