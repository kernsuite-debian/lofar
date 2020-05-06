#!/usr/bin/env python3

# Copyright (C) 2015-2017
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: resource_assigner.py 1580 2015-09-30 14:18:57Z loose $

"""
RAtoOTDBTaskSpecificationPropagator gets a task to be scheduled in OTDB,
reads the info from the RA DB and sends it to OTDB in the correct format.
"""

import logging
import datetime
import time
import pprint
import traceback

from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

from lofar.sas.resourceassignment.ratootdbtaskspecificationpropagator.translator import RAtoOTDBTranslator
from lofar.sas.resourceassignment.common.specification import Specification

logger = logging.getLogger(__name__)


class RAtoOTDBPropagator():
    def __init__(self,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):
        """
        RAtoOTDBPropagator updates tasks in the OTDB after the ResourceAssigner is done with them.
        :param exchange: exchange on which the services listen (default: lofar)
        :param broker: Valid Qpid broker host (default: None, which means localhost)
        """

        self.radbrpc = RADBRPC.create(exchange=exchange, broker=broker)
        self.otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker)
        self.momrpc = MoMQueryRPC.create(exchange=exchange, broker=broker)
        self.translator = RAtoOTDBTranslator()

    def __enter__(self):
        """Internal use only. (handles scope 'with')"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Internal use only. (handles scope 'with')"""
        self.close()

    def open(self):
        """Open rpc connections to radb, OTDB and MoMQuery service"""
        self.radbrpc.open()
        self.otdbrpc.open()
        self.momrpc.open()

    def close(self):
        """Close rpc connections to radb, OTDB and MoMQuery service"""
        self.radbrpc.close()
        self.otdbrpc.close()
        self.momrpc.close()

    def doTaskApproved(self, otdb_id, mom_id):
        logger.info('doTaskApproved: otdb_id=%s' % (otdb_id,))
        if not otdb_id:
            logger.warning('doTaskApproved no valid otdb_id: otdb_id=%s' % (otdb_id,))
            return
        try:
            if not mom_id:
                logger.info('doTaskApproved no valid mom_id, we do nothing')
            else:
                mom_info = self.getMoMinfo(mom_id)
                logger.info('MOM info for mom_id=%s: %s' % (mom_id, mom_info.as_dict()))
                otdb_info = self.translator.CreateParset(otdb_id, None, None, mom_info)
                if otdb_info:
                    logger.info('Setting specification for otdb_id %s:\n' % (otdb_id,))
                    logger.info(pprint.pformat(otdb_info))
                    self.otdbrpc.taskSetSpecification(otdb_id, otdb_info)
        except Exception as e:
            logger.error('doTaskApproved: %s', traceback.format_exc())

    def doTaskConflict(self, otdb_id):
        logger.info('doTaskConflict: otdb_id=%s' % (otdb_id,))
        if not otdb_id:
            logger.warning('doTaskConflict no valid otdb_id: otdb_id=%s' % (otdb_id,))
            return
        try:
            self.otdbrpc.taskSetStatus(otdb_id, 'conflict')
        except Exception as e:
            logger.error('doTaskConflict: %s', traceback.format_exc())

    def doTaskError(self, otdb_id):
        logger.info('doTaskError: otdb_id=%s' % (otdb_id,))
        if not otdb_id:
            logger.warning('doTaskError no valid otdb_id: otdb_id=%s' % (otdb_id,))
            return
        try:
            self.otdbrpc.taskSetStatus(otdb_id, 'error')
        except Exception as e:
            logger.error('doTaskError: %s', traceback.format_exc())

    def doTaskScheduled(self, ra_id, otdb_id, mom_id):
        try:
            logger.info('doTaskScheduled: ra_id=%s otdb_id=%s mom_id=%s' % (ra_id, otdb_id, mom_id))
            if not otdb_id:
                logger.warning('doTaskScheduled no valid otdb_id: otdb_id=%s' % (otdb_id,))
                return
            ra_info = self.getRAinfo(ra_id)

            logger.info('RA info for ra_id=%s otdb_id=%s: %s' % (ra_id, otdb_id, ra_info))

            project_name = 'unknown'

            mom_info = self.getMoMinfo(mom_id)

            logger.info('MOM info for mom_id=%s: %s' % (mom_id, mom_info.as_dict()))

            if mom_id:
                #get mom project name
                try:
                    project = self.momrpc.getObjectDetails(mom_id)
                    logger.info(project)
                    project_name = "_".join(project[int(mom_id)]['project_name'].split())
                except Exception as e:
                    logger.error('Could not get project name from MoM for mom_id %s: %s' % (mom_id, str(e)))
                    logger.info("Using 'unknown' as project name.")
                    project_name = 'unknown'

            otdb_info = self.translator.CreateParset(otdb_id, ra_info, project_name, mom_info)

            self.setOTDBinfo(otdb_id, otdb_info, 'scheduled')
        except Exception as e:
            logger.error('doTaskScheduled: %s', traceback.format_exc())
            self.doTaskError(otdb_id) #FIXME should be to the RADB also or instead?

    def ParseStorageProperties(self, storage_claim):
        """input something like:
        {u'username':u'anonymous', u'status': u'claimed', u'resource_name':
        u'CEP4_storage:/data', u'user_id': -1, u'resource_type_id': 5, u'task_id': 6349,
        u'status_id': 1, u'resource_id': 117, u'session_id': 1, u'id': 339,
        u'claim_size': 24000, u'starttime': datetime.datetime(2016, 6, 10, 16, 8, 15),
        u'resource_type_name': u'storage', u'endtime': datetime.datetime(2016, 7, 11,
        16, 33, 15), u'properties': [{u'io_type_name': u'output', u'type_name':
        u'img_file_size', u'value': 1000, u'io_type_id': 0, u'type_id': 12, u'id': 808},
        {u'io_type_name': u'output', u'type_name': u'nr_of_img_files', u'value': 24,
        u'io_type_id': 0, u'type_id': 4, u'id': 809}, {u'io_type_name': u'input',
        u'type_name': u'nr_of_uv_files', u'value': 240, u'io_type_id': 1, u'type_id': 2,
        u'id': 810}, {u'io_type_name': u'input', u'type_name': u'uv_file_size',
        u'value': 43957416, u'io_type_id': 1, u'type_id': 10, u'id': 811}]}

        output something like:
        {'output_files': {'resource_name': u'CEP4_storage:/data', u'nr_of_im_files': 488,
                          u'nr_of_uv_files': 488, u'im_file_size': 1000, u'uv_file_size': 32500565}}
        """
        input_files = {}
        output_files = {}

        # FIXME This is very fragile code, mainly because we don't know if 'saps' are part of the input or output.
        # This should probably be redesigned, but might require changes in how RADB works.
        if 'saps' in storage_claim:
            has_input = False
            has_output = False
            saps = []
            for s in storage_claim['saps']:
                properties = {}
                for p in s['properties']:
                    if p['io_type_name'] == 'output':
                        properties[p['type_name']] = p['value']
                        has_output = True
                    if p['io_type_name'] == 'input':
                        properties[p['type_name']] = p['value']
                        has_input = True
                if has_input or has_output:
                    saps.append({'sap_nr' : s['sap_nr'], 'properties': properties})
            if has_input:
                if saps:
                    input_files['saps'] = saps
            if has_output:
                if saps:
                    output_files['saps'] = saps
        if 'properties' in storage_claim:
            for p in storage_claim['properties']:
                if p['io_type_name'] == 'output':
                    output_files[p['type_name']] = p['value']
                if p['io_type_name'] == 'input':
                    input_files[p['type_name']] = p['value']

        if input_files:
            input_files['resource_name']  = storage_claim['resource_name']
        if output_files:
            output_files['resource_name'] = storage_claim['resource_name']

        logger.info(pprint.pformat( (input_files, output_files) ))
        return input_files, output_files

    def getRAinfo(self, ra_id):
        info = {'storage': {'input': [], 'output': []}}

        task = self.radbrpc.getTask(ra_id)
        logger.debug('getRAinfo: task = %s', task)
        info["starttime"] = task["starttime"]
        info["endtime"]   = task["endtime"]
        info["status"]    = task["status"]
        info["type"]      = task["type"]
        info["cluster"]   = task["cluster"]

        claims = self.radbrpc.getResourceClaims(task_ids=ra_id, resource_type='storage',
                                                extended=True, include_properties=True)
        for claim in claims:
            input_files, output_files = self.ParseStorageProperties(claim)
            if input_files:
                info['storage']['input'].append(input_files)
            if output_files:
                info['storage']['output'].append(output_files)

        return info

    def getMoMinfo(self, mom_id):
        '''
        Creates a specification object and reads information from MoM
        (currently time restrictions and storagemanager from the misc field)
        :param mom_id:
        :return: RACommon specification object
        '''
        spec = Specification(self.otdbrpc, self.momrpc, self.radbrpc)
        spec.mom_id = mom_id
        spec.read_from_mom()
        return spec

    def setOTDBinfo(self, otdb_id, otdb_info, otdb_status):
        try:
            logger.info('Setting specification for otdb_id %s:\n' % (otdb_id,))
            logger.info(pprint.pformat(otdb_info))
            self.otdbrpc.taskSetSpecification(otdb_id, otdb_info)
            self.otdbrpc.taskPrepareForScheduling(otdb_id, otdb_info["LOFAR.ObsSW.Observation.startTime"],
                                                           otdb_info["LOFAR.ObsSW.Observation.stopTime"])
            logger.info('Setting status (%s) for otdb_id %s' % (otdb_status, otdb_id))
            self.otdbrpc.taskSetStatus(otdb_id, otdb_status)
        except Exception as e:
            logger.error(e)
            self.doTaskError(otdb_id) #FIXME should be to the RADB also or instead?
