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
# $Id: specification.py 1580 2015-09-30 14:18:57Z loose $

"""
This is a class to manage and manipulate Task specifications and sync them between OTDB, MoM and RADB.
This should probably be refactored further into a Task class, Estimates, Specification and ResouceClaims classes owned
by/properties of the task.
The current class is a mix of backward compatible dicts in internal_dict, specfication info and methods, and Task
properties and methods.
"""

from lofar.parameterset import parameterset
from datetime import datetime, timedelta
from lofar.common.datetimeutils import parseDatetime
from lofar.sas.resourceassignment.resourceassigner.schedulechecker import movePipelineAfterItsPredecessors
from lofar.common.postgres import PostgresDBQueryExecutionError

import pprint

import logging
logger = logging.getLogger(__name__)

""" Prefix that is common to all parset keys, when we get a parset from OTDBRPC. """
INPUT_PREFIX = "ObsSW."
""" Prefix that is common to all parset keys, when we need to write a parset to OTDB """
OUTPUT_PREFIX = "LOFAR.ObsSW."

# TODO This class can use a more OO approach, it currenly exposes quite a bit of its internals and depends a bit
# on the user of the class to enforce consistency. Given the time available, this will need to be done in a further
# refactoring.
# TODO There are lot's of hardcoded OTDB key strings and values in here.
# TODO Maybe all/most the static methods should log what they're doing and no longer be static?
# TODO We can do more direct updating of OTDB and MoM from here, especially the MoM sytem spec.


class Specification:
    def __init__(self, otdbrpc, momquery, radb):
        """Right now we internally represent a subset of a virtual instrument tree in OTDB and manipulate parset type
        specifications. Therefore we need an otdbid. At some point the OTDB dependency can hopefully be replaced with
        a proper virtual instrument model, when LOFAR is less dependent on MoM and OTDB and the Scheduler.

        :param otdbrpc: rpc to talk to otdb
        :param momquery:  rpc to query MoM
        :param radb: RADB or RADBRPC instance

        In practice we need all 3 RPCs as we do consistency checking between the three databases for things like Cluster
        names.
        """
        self.otdbrpc  = otdbrpc
        self.radb = radb
        self.momquery = momquery

        # I have not implemented getter/setter functions for most, maybe in a further refactor if it seems to be useful
        # otherwise it might just be code noise?
        self.internal_dict = {} # TODO: Needs a better name?
        self.predecessors  = [] # list of specification instances
        self.successor_ids = [] # list of successor Identifiers
        self.otdb_id    = None # Task Id in OTDB
        self.mom_id     = None # Task Id in MoM
        self.radb_id    = None # Task Id in RADB
        self.trigger_id = None # Id of trigger is this was specified in a trigger
        self.type       = None # Task type in RADB
        self.subtype    = None # Task type in RADB
        self.status     = None # Task status, as used in OTDB/MoM.
        self.storagemanager = None

        #Inputs for the scheduler
        self.min_starttime = None
        #self.max_starttime = None # We return this from calculate_dwell_values
        self.max_endtime   = None
        self.min_duration  = timedelta(0)
        self.max_duration  = timedelta(0)

        #actual starttime, endtime, duration
        self.starttime     = None
        self.endtime       = None
        self.duration      = timedelta(0)

        self.cluster       = None # Will need to be a dict in the future to know which type of data goes where.

    @staticmethod
    def parse_timedelta(input_value):
        '''
        translates int/float input to a timedelate. None input (and 'None' strings) will be translated to timedelta(0)
        '''
        if input_value is None:
            return timedelta(0)
        elif input_value == "None":
            return timedelta(0)
        elif input_value == "None":
            return timedelta(0)
        elif isinstance(input_value, int):
            return timedelta(seconds=input_value)
        elif isinstance(input_value, float):
            return timedelta(seconds=input_value)
        else:
            return input_value  # todo: maybe raise an Exception instead?

    @staticmethod
    def parse_datetime(input_value):
        '''
        translates a datetime string to a datetime object, 'None' strings will be translates to actual None.
        '''
        if input_value == "None":
            # todo: should we translate to a reasonable default datetuime like with timedelta?
            return None
        elif input_value == "None":
            return None
        elif isinstance(input_value, str):
            return parseDatetime(input_value)
        else:
            return input_value # todo: maybe raise an Exception instead?

    def as_dict(self):
        """"Mostly a serialization function to make a qpid message and for backward compatibility with old functions.

        :return Dict that represents the class and any predecessors.
        """
        result = dict()
        result["otdb_id"]       = self.otdb_id
        result["mom_id"]        = self.mom_id
        result["task_id"]       = self.radb_id
        result["trigger_id"]    = self.trigger_id
        result["status"]        = self.status
        result["task_type"]     = self.type
        result["task_subtype"]  = self.subtype
        result["starttime"]     = str(self.starttime)
        result["endtime"]       = str(self.endtime)
        result["duration"]      = self.duration.total_seconds()
        result["min_starttime"] = str(self.min_starttime)
        result["max_endtime"]   = str(self.max_endtime)
        result["min_duration"]  = str(self.min_duration)
        result["max_duration"]  = str(self.max_duration)
        result["cluster"]       = self.cluster
        result["specification"] = self.internal_dict
        result["specification"]["Observation.startTime"] = str(self.starttime) #TODO set/update these somewhere else?
        result["specification"]["Observation.stopTime"] = str(self.endtime)
        result["predecessors"]  = []
        for p in self.predecessors:
            result["predecessors"].append(p.as_dict())
        result["successors"] = self.successor_ids
        result["storagemanager"] = self.storagemanager
        result["specification"]["storagemanager"] = self.storagemanager # To have the ResourceEstimator find it
        return result

    def from_dict(self, input_dict):
        """"Mostly a serialization function to read from a qpid message.

        :param input_dict: Serialized version of a Specification and any predecessors.
        """
        self.otdb_id       = input_dict["otdb_id"]
        self.mom_id        = input_dict.get("mom_id")
        self.radb_id       = input_dict["task_id"]
        self.trigger_id    = input_dict.get("trigger_id")
        self.status        = input_dict["status"]
        self.type          = input_dict["task_type"]
        self.subtype       = input_dict.get("task_subtype")
        self.starttime     = Specification.parse_datetime(input_dict.get("starttime"))
        self.endtime       = Specification.parse_datetime(input_dict.get("endtime"))
        self.duration      = Specification.parse_timedelta(input_dict.get("duration"))
        self.min_starttime = Specification.parse_datetime(input_dict.get("min_starttime"))
        self.max_endtime   = Specification.parse_datetime(input_dict.get("max_endtime"))
        self.min_duration  = Specification.parse_timedelta(input_dict.get("min_duration"))
        self.max_duration  = Specification.parse_timedelta(input_dict.get("max_duration"))
        self.cluster       = input_dict.get("cluster")
        self.internal_dict = input_dict.get("specification", {})
        self.predecessors  = []
        for p in input_dict.get("predecessors",[]):
            spec = Specification(self.otdbrpc, self.momquery, self.radb)
            spec.from_dict(p)
            self.predecessors.append(spec)
        self.successor_ids = input_dict.get("successors",[])
        self.storagemanager = input_dict.get("storagemanager")

    def isObservation(self):
        """:return if the Specification is for an observation."""
        return self.type.lower() == "observation"

    def isPipeline(self):
        """:return if the Specification is for an pipeline."""
        return self.type.lower() == "pipeline"

    def isUnmovable(self):
        """The start time of reservations and maintenance tasks are allowed to lie in the past.
        :return if it's a reservation or maintenance"""
        return self.type in ['reservation', 'maintenance']

    def isMovable(self):
        return not self.isUnmovable()

    def isTriggered(self):
        """:return if the Specification was created by a trigger"""
        return self.trigger_id is not None

    def validate(self):
        pass # Not implemented

    def from_xml(self):
        pass # Not implemented

# ========================= MoM related methods =======================================================================

    def read_time_restrictions_from_mom(self):
        """
        Read the time restrictions from mom and, if present, write values to corresponding instance variables
        """
        try:
            time_restrictions = self.momquery.get_trigger_time_restrictions(self.mom_id)
            logger.info("Received time_restrictions from MoM: %s", time_restrictions)
            if time_restrictions:
                if "minStartTime" in time_restrictions:
                    self.min_starttime = Specification.parse_datetime(time_restrictions["minStartTime"])
                if "maxDuration" in time_restrictions:
                    self.max_duration = Specification.parse_timedelta(time_restrictions["maxDuration"])
                if "minDuration" in time_restrictions:
                    self.min_duration = Specification.parse_timedelta(time_restrictions["minDuration"])
                if "maxEndTime" in time_restrictions:
                    self.max_endtime = Specification.parse_datetime(time_restrictions["maxEndTime"])
                # todo: why is the trigger_id part of this response? This is a time restrictions query.
                # todo: We should at least call a generic query 'get_misc', but it's probably better to have
                # todo: specific queries (there is a get_trigger_id) to make the transition easier when this
                # todo: works against a service where these things are implemented properly.
                if "trigger_id" in time_restrictions:
                    self.trigger_id = time_restrictions["trigger_id"]
                    logger.info('Found a task mom_id=%s with a trigger_id=%s', self.mom_id, self.trigger_id)

        except Exception as e:
            logger.exception("read_time_restrictions_from_mom: " + str(e), exc_info=True)
            self.set_status("error")

    def read_storagemanager_from_mom(self):
        """
        Read the storagemanager from mom and, if present, write the value to the corresponding instance variable
        """
        try:
            # set storagemanager from misc
            storagemanager = self.momquery.get_storagemanager(self.mom_id)
            if storagemanager:
                self.storagemanager = storagemanager
                logger.info("Found a task mom_id=%s with storagemanager=%s from MoM",
                                 self.mom_id, self.storagemanager)
        except KeyError as ke:
            # set default
            # logger.exception("read_storagemanager_from_mom: " + str(ke), exc_info=False)
            logger.info("Storagemanager not found in MoM")
            # If the key exists in the VIC tree in OTDB, we use that instead if read_from_otdb has been called.

        except Exception as e:
            # unexpected error (no entry for momid)
            logger.exception("read_storagemanager_from_mom: " + str(e), exc_info=True)
            self.set_status("error")


    def read_from_mom(self):
        """"Read specification values from the MoM database, mostly the misc field time restrictions
        Tries to set min_starttime, max_endtime, min_duration, max_duration, if the Specification has a mom_id

        Please be aware of potential race conditions if the mom-otdb-adapter hasn't updated MoM yet after changes in
        OTDB. Don't read values from MoM that originate or might have more recent values in OTDB.
        """
        if self.mom_id:
            # We might need more than the misc field in the future.
            # Right now we assume start/end times from OTDB always have priority for example.
            self.read_time_restrictions_from_mom()
            self.read_storagemanager_from_mom()
        else:
            logger.info("This task does not have a mom_id.")

# ========================= parset/OTDB related methods =======================================================================

    @staticmethod
    def _OTDB_to_RA_task_types(otdb_task_type, otdb_task_subtype):
        """Translation table for task types: OTDB (type,subtype) -> RADB (type,subtype)

        :param otdb_task_type: task type from OTDB
        :param otdb_task_subtype: task subtype from OTDB

        :return tuple (type, subtype) of translated types
        """
        #TODO maybe imaging pipeline msss should not be handled separately any more?
        OTDB_to_RADB_type_translation_table = {
            ("Observation", "Beam Observation"): ("observation", "bfmeasurement"),
            ("Observation", "Interferometer"): ("observation", "interferometer"),
            ("Observation", "TBB (piggyback)"): ("observation", "tbbmeasurement"),
            ("Observation", "TBB (standalone)"): ("observation", "tbbmeasurement"),
            ("Pipeline", "Averaging Pipeline"): ("pipeline", "averaging pipeline"),
            ("Pipeline", "Calibration Pipeline"): ("pipeline", "calibration pipeline"),
            ("Pipeline", "Imaging Pipeline"): ("pipeline", "imaging pipeline"),
            ("Pipeline", "Imaging Pipeline MSSS"): ("pipeline", "imaging pipeline msss"),
            ("Pipeline", "Long Baseline Pipeline"): ("pipeline", "long baseline pipeline"),
            ("Pipeline", "Pulsar Pipeline"): ("pipeline", "pulsar pipeline"),
            ("MAINTENANCE", ""): ("reservation", "maintenance"),
            ("RESERVATION", ""): ("reservation", "project"),
        }
        return OTDB_to_RADB_type_translation_table[(otdb_task_type, otdb_task_subtype)]

    @staticmethod
    def _resourceIndicatorsFromParset(radb_type, radb_subtype, parset, PARSET_PREFIX):
        """ Extract the parset keys that are required for resource assignment.
        Mostly gets used in the ResourceEstimator. The internal_dict should probably be refactored out at some point.

        :param radb_type: task type in RADB format
        :param radb_subtype: task subtype in RADB format
        :param parset: parameterset for the task
        :param PARSET_PREFIX: Prefix to be ommitted from the output

        :return A dict with the OTDB keys as keys without the PARSET_PREFIX, and the values as values,
        converted to int, bool, float, list (for vectors)
        """

        subset = {}

        def add(key, conversion=parameterset.getString, prefix=PARSET_PREFIX):
            """ Add the given key to our subset selection, using an optional
                conversion. """
            if parset.isDefined(prefix + key):
                subset[key] = conversion(parset, prefix + key)

        """ Some conversion functions for common parameter-value types."""
        def as_strvector(_parset, key):
            return _parset.getStringVector(key, True)

        def as_intvector(_parset, key):
            return _parset.getIntVector(key, True)

        def as_bool(_parset, key):
            return _parset.getBool(key)

        def as_int(_parset, key):
            return _parset.getInt(key)

        def as_float(_parset, key):
            return _parset.getDouble(key)

        # =====================================
        # Parset meta info
        # =====================================
        add("Version.number", as_int, prefix="")

        # =====================================
        # Maintenance/reservation settings
        # =====================================
        if radb_type in ["maintenance","reservation"]:
            add("Observation.VirtualInstrument.stationList", as_strvector)
            #add("Observation.startTime")
            #add("Observation.stopTime")

        # =====================================
        # Observation settings
        # =====================================
        if radb_type == "observation":
            #add("Observation.momID")
            add("Observation.sampleClock", as_int)
            add("Observation.nrBitsPerSample", as_int)
            add("Observation.antennaSet")
            add("Observation.VirtualInstrument.stationList", as_strvector)
            #add("Observation.startTime")
            #add("Observation.stopTime")

            add("Observation.nrBeams", as_int)

            nrSAPs = subset.get("Observation.nrBeams", 0)
            for sap in range(0, nrSAPs):
                add("Observation.Beam[%d].subbandList" % (sap,), as_intvector)

            # =====================================
            # Correlator settings
            # =====================================
            add("Observation.DataProducts.Output_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Output_Correlated.storageClusterName")
            add("Observation.DataProducts.Output_Correlated.identifications", as_strvector)
            add("Observation.ObservationControl.OnlineControl.Cobalt.Correlator.integrationTime", as_float)
            add("Observation.ObservationControl.OnlineControl.Cobalt.Correlator.nrChannelsPerSubband", as_int)

            # =====================================
            # Beamformer settings
            # =====================================
            add("Observation.DataProducts.Output_IncoherentStokes.enabled", as_bool)
            add("Observation.DataProducts.Output_IncoherentStokes.storageClusterName")
            add("Observation.DataProducts.Output_IncoherentStokes.identifications", as_strvector)
            add("Observation.DataProducts.Output_CoherentStokes.enabled", as_bool)
            add("Observation.DataProducts.Output_CoherentStokes.storageClusterName")
            add("Observation.DataProducts.Output_CoherentStokes.identifications", as_strvector)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.flysEye", as_bool)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.nrChannelsPerSubband", as_int) # only needed to determine Cobalt.blockSize
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.subbandsPerFile", as_int)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.timeIntegrationFactor", as_int)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.CoherentStokes.which")
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.nrChannelsPerSubband", as_int) # only needed to determine Cobalt.blockSize
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.subbandsPerFile", as_int)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.timeIntegrationFactor", as_int)
            add("Observation.ObservationControl.OnlineControl.Cobalt.BeamFormer.IncoherentStokes.which")
            for sap in range(0, nrSAPs):
                add("Observation.Beam[%d].nrTabRings" % (sap,), as_int)

                add("Observation.Beam[%d].nrTiedArrayBeams" % (sap,), as_int)
                nrTABs = subset.get("Observation.Beam[%d].nrTiedArrayBeams" % (sap,), 0)
                for tab in range(0, nrTABs):
                    add("Observation.Beam[%d].TiedArrayBeam[%d].coherent" % (sap,tab), as_bool)

        # =====================================
        # Pipeline settings
        # =====================================
        if radb_type == "pipeline" and radb_subtype in ["averaging pipeline", "calibration pipeline"]:
            # Calibrator / Averaging pipelines
            add("Observation.DataProducts.Output_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Output_Correlated.storageClusterName")
            add("Observation.DataProducts.Output_Correlated.identifications", as_strvector)
            add("Observation.DataProducts.Output_InstrumentModel.enabled", as_bool)
            add("Observation.DataProducts.Output_InstrumentModel.storageClusterName")
            add("Observation.DataProducts.Output_InstrumentModel.identifications", as_strvector)
            add("Observation.DataProducts.Input_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Input_Correlated.identifications", as_strvector)
            add("Observation.DataProducts.Input_InstrumentModel.enabled", as_bool)
            add("Observation.DataProducts.Input_InstrumentModel.identifications", as_strvector)
            # NOTE: currently these are the only pipelines that use these DPPP keys
            # Other pipelines are modelled to possibly do these steps as well, but currently no Default Templates exist
            add("Observation.ObservationControl.PythonControl.DPPP.demixer.freqstep", as_int)
            add("Observation.ObservationControl.PythonControl.DPPP.demixer.timestep", as_int)
            # Note: hould not actually be used in the ResourceAssinger as the value is stored in
            # Specification.storagemanager using get_storagemanager_from_parset
            #add("Observation.ObservationControl.PythonControl.DPPP.storagemanager.name")

        if radb_type == "pipeline" and radb_subtype in ["imaging pipeline", "imaging pipeline msss"]:
            # Imaging pipeline
            add("Observation.DataProducts.Output_SkyImage.enabled", as_bool)
            add("Observation.DataProducts.Output_SkyImage.storageClusterName")
            add("Observation.DataProducts.Output_SkyImage.identifications", as_strvector)
            add("Observation.DataProducts.Input_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Input_Correlated.identifications", as_strvector)
            add("Observation.ObservationControl.PythonControl.Imaging.slices_per_image")
            add("Observation.ObservationControl.PythonControl.Imaging.subbands_per_image")
            # Note: hould not actually be used in the ResourceAssinger as the value is stored in
            # Specification.storagemanager using get_storagemanager_from_parset
            #add("Observation.ObservationControl.PythonControl.DPPP.storagemanager.name")

        if radb_type == "pipeline" and radb_subtype == "long baseline pipeline":
            # Long-baseline pipeline
            add("Observation.DataProducts.Output_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Output_Correlated.storageClusterName")
            add("Observation.DataProducts.Output_Correlated.identifications", as_strvector)
            add("Observation.DataProducts.Input_Correlated.enabled", as_bool)
            add("Observation.DataProducts.Input_Correlated.identifications", as_strvector)
            add("Observation.ObservationControl.PythonControl.LongBaseline.subbandgroups_per_ms", as_int)
            add("Observation.ObservationControl.PythonControl.LongBaseline.subbands_per_subbandgroup", as_int)
            # Note: hould not actually be used in the ResourceAssinger as the value is stored in
            # Specification.storagemanager using get_storagemanager_from_parset
            #add("Observation.ObservationControl.PythonControl.DPPP.storagemanager.name")

        if radb_type == "pipeline" and radb_subtype == "pulsar pipeline":
            # Pulsar pipeline
            add("Observation.DataProducts.Output_Pulsar.enabled", as_bool)
            add("Observation.DataProducts.Output_Pulsar.storageClusterName")
            add("Observation.DataProducts.Output_Pulsar.identifications", as_strvector)
            add("Observation.DataProducts.Input_CoherentStokes.enabled", as_bool)
            add("Observation.DataProducts.Input_CoherentStokes.identifications", as_strvector)
            add("Observation.DataProducts.Input_IncoherentStokes.enabled", as_bool)
            add("Observation.DataProducts.Input_IncoherentStokes.identifications", as_strvector)

        return subset

    def get_predecessor_ids_from_parset(self, parset, PARSET_PREFIX):
        """Extract the list of predecessor obs IDs from the given parset.

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :return: list of dicts {"source": <source>, "id": int}
        where <source> in "otdb", "mom", "other"
        """

        predecessors = parset.getStringVector(PARSET_PREFIX + "Observation.Scheduler.predecessors", True)

        # Key contains values starting with 'S' = Scheduler, 'L'/'T' = OTDB, 'M' = MoM
        # 'S' we can probably ignore? Might be only internal in the Scheduler?
        result = []
        for p in predecessors:
            try: # Made the source a string for readability, but it's not efficient
                if p.startswith('M'):
                    result.append({'source': 'mom', 'id': int(p[1:])})
                elif p.startswith('L') or p.startswith('T'):
                    result.append({'source': 'otdb', 'id': int(p[1:])})
                else: # 'S'
                    logger.info("found a predecessor ID I can't handle: %s", p)
                    result.append({'source': 'other', 'id': int(p[1:])})
            except ValueError:
                logger.warning("found a predecessor ID that I can't parse %s", p)

        return result

    @staticmethod
    def _get_task_types_from_parset(parset, PARSET_PREFIX):
        """ Reads the task types from a parset and convers them to RADB types.

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :return: type, subtype
        """
        otdb_task_type = parset.getString(PARSET_PREFIX + "Observation.processType")
        otdb_task_subtype = parset.getString(PARSET_PREFIX + "Observation.processSubtype")
        _type, _subtype = Specification._OTDB_to_RA_task_types(otdb_task_type, otdb_task_subtype)

        return _type, _subtype

    def _get_mom_id_from_parset(self, parset, PARSET_PREFIX):
        """ Reads the mom_id from a parset.

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :return: mom_id as int if found, otherwise None
        """
        # NOTE: Implemented this way to avoid race condition when asking MoM as the mom-otdb-adapter might
        # not have heard that the task is on approved and might still be on approved pending in MoM.
        # mom_ids = self.momquery.getMoMIdsForOTDBIds([otdb_id])
        # So we get the parset for all tasks we receive and try to find a mom_id in there.
        try:
            mom_id = int(parset.getString(PARSET_PREFIX + "Observation.momID"))
        except (ValueError, KeyError, RuntimeError):  # TODO figure out why this gives a RuntimeError not the other two
            mom_id = None
        if mom_id: # moving this to a higher level method seemed to clutter things, so this is not a staticmethod
            logger.info('Found mom_id %s for otdb_id %s', mom_id, self.otdb_id)
        else:
            logger.info('Did not find a mom_id for task otdb_id=%s', self.otdb_id)
            mom_id = None # 0 can have been returned?

        return mom_id

    @staticmethod
    def _get_start_and_end_times_from_parset(parset, PARSET_PREFIX):
        """
        Extract the start and end times from a parset

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :return: start_time, end_time. start_time and end_time are returned as None when they were not
                 specified, or where specified in a wrong format.
        """

        try:
            start_time = parseDatetime(parset.getString(PARSET_PREFIX + 'Observation.startTime'))
        except (ValueError, KeyError, RuntimeError): #TODO figure out why this gives a RuntimeError not the other two
            # Too bad no valid start time is specified!
            start_time = None

        try:
            end_time = parseDatetime(parset.getString(PARSET_PREFIX + 'Observation.stopTime'))
        except (ValueError, KeyError, RuntimeError): #TODO figure out why this gives a RuntimeError not the other two
            # Too bad no valid end time is specified!
            end_time = None

        return start_time, end_time

    @staticmethod
    def _get_duration_from_parset(parset, PARSET_PREFIX):
        """
        Preferably use the duration specified by the parset. If that's not available return None

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :returns the obtained duration or None
        """

        try:
            duration = timedelta(seconds=parset.getInt(PARSET_PREFIX + 'Observation.Scheduler.taskDuration'))
        except (ValueError, KeyError, RuntimeError): #TODO figure out why this gives a RuntimeError not the other two
            duration = timedelta(0)
        return duration

    @staticmethod
    def _get_storagemanager_from_parset(parset, PARSET_PREFIX):
        """
        Preferably use the storagemanger specified by the parset. If that's not available return None.

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :returns the obtained storagemanger or None
        """

        try:
            storagemanger = parset.getString(PARSET_PREFIX + 'Observation.ObservationControl.PythonControl.DPPP.storagemanager.name')
            # TODO: At some point the value should probably be validated but no validation implemented as there
            # is no good source of valid values. Things are scattered in XML gen and OTDB and such.
        except (ValueError, KeyError, RuntimeError): #TODO RuntimeError copied from get_duration_from_parset?
            storagemanger = None
        return storagemanger

    def _get_parset_from_OTDB(self):
        """Obtain parset based on self.otdb_id and convert dict to parameterset object

        :return parameterset
        """

        parset = parameterset(self.otdbrpc.taskGetSpecification(otdb_id=self.otdb_id)['specification'])
        logger.info('Reading parset from OTDB for task %i was successful' % self.otdb_id)
        logger.debug("parset [%s]: %s" % (self.otdb_id, pprint.pformat(parset.dict())))

        return parset

    def read_from_otdb(self, otdb_id):
        """read_from_otdb will retrieve a parset from OTDB and parse its values into the properies of the Specification

        :param otdb_id: VIC tree id in OTDB
        :return: list of predecessor ids for recursive searching of Specifications this task depends on
        """
        logger.info('Start reading values from OTDB for task %i' % otdb_id)
        self.otdb_id = otdb_id
        # otdbrpc.taskGetStatus not used, assumed that status is set, using self.set_status
        try:
            parset = self._get_parset_from_OTDB()
            self.type, self.subtype = Specification._get_task_types_from_parset(parset, INPUT_PREFIX)
            self.internal_dict = Specification._resourceIndicatorsFromParset(self.type, self.subtype, parset, INPUT_PREFIX)
            self.starttime, self.endtime = Specification._get_start_and_end_times_from_parset(parset, INPUT_PREFIX)
            self.duration = Specification._get_duration_from_parset(parset, INPUT_PREFIX)
            self.mom_id = self._get_mom_id_from_parset(parset, INPUT_PREFIX)
            self.cluster = self.get_cluster_name(parset, INPUT_PREFIX)
            #Gets a default storagemanager from OTDB, possibly overridden in a later call to read_from_mom()
            self.storagemanager = self._get_storagemanager_from_parset(parset, INPUT_PREFIX)
            predecessor_ids = self.get_predecessor_ids_from_parset(parset, INPUT_PREFIX)
        except Exception as e:
            logger.exception(e)
            logger.error("Problem parsing specification for otdb_id=%s", otdb_id)
            self.set_status("error") #Not catching an exception here
            return []
        logger.info('Reading values from OTDB for task %i was successful' % otdb_id)
        logger.info('type: %s subtype: %s starttime: %s endtime: %s duration: %s mom_id: %s cluster: %s predecessors: %s',
                         self.type, self.subtype, self.starttime, self.endtime, self.duration, self.mom_id, self.cluster, predecessor_ids)

        return predecessor_ids

    def convert_id_to_otdb_ids(self, id, id_source):
        """Makes sure that identifier id from source id_source (mom, otdb) is an otdb_id

        :param id: int
        :param id_source: "mom", "otdb", "other"
        :return: otdb_id as int or None
        """
        if id_source == "other":
            otdb_id = None
        elif id_source == "mom":
            otdb_id = self.otdbrpc.taskGetIDs( mom_id=id )['otdb_id']
        elif id_source == "otdb":
            otdb_id = id
        else:
            raise ValueError("Error in understanding id_source %s (id %s)" % (id_source, id))
        return otdb_id

    def read_from_OTDB_with_predecessors(self, id, id_source, found_specifications):
        """Recursively read the VIC Tree and it's predecessors from OTDB and update properties to match

        :param id: Identifier in either MoM or OTDB
        :param id_source: "otdb", "mom", "other", where other gets ignored
        :param found_specifications: list of Specifications we've found already and don't need to query for again.
        """
        logger.info("Processing ID %s from %s" % (id, id_source))
        otdb_id = self.convert_id_to_otdb_ids(id, id_source)

        logger.info("Processing OTDB ID %s", otdb_id)

        # obtain parset and parse it to update our properties
        predecessors = self.read_from_otdb(otdb_id)
        # add it to our cache
        found_specifications[otdb_id] = self

        logger.info("Processing predecessors")
        for predecessor in predecessors:
            pred_otdb_id = self.convert_id_to_otdb_ids(predecessor['id'], predecessor['source'])
            if not pred_otdb_id:
                continue
            if pred_otdb_id in found_specifications:
                self.predecessors.append(found_specifications[pred_otdb_id])
            else:
                spec = Specification(self.otdbrpc, self.momquery, self.radb)
                spec.read_from_OTDB_with_predecessors(pred_otdb_id, "otdb", found_specifications)
                self.predecessors.append(spec) #TODO this needs a try/except somewhere?
        logger.info("Done reading from OTDB with predecessors")

    def get_cluster_name(self, parset, PARSET_PREFIX):
        """
        Determines the name of the cluster to which to store the task's output - if it produces output at all that is.

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :returns The name of the output cluster, or an empty string if none is applicable
        :raises Exception if the storage cluster required by the task is unknown to the system/RADB
        """

        cluster_name = None
        if self.isMovable():  # non reservation or maintenance
            # Only assign resources for task output to known clusters
            cluster_name_set = Specification._get_storage_cluster_names_from_parset(parset, PARSET_PREFIX)
            logger.info("Found cluster names in parset: %s", cluster_name_set)

            if str() in cluster_name_set or len(cluster_name_set) != 1:
                # Empty set or name is always an error.
                # TODO: To support >1 cluster per task is not implemented
                # self.radbrpc.insertOrUpdateSpecificationAndTask() as called below and the radb would need to take >1
                # cluster name/ Also, there is only 1 processingClusterName in the parset, but we do not always want to
                # pipeline process all obs outputs, or not on 1 cluster
                logger.error(
                    'clusterNameSet must have a single non-empty name for all enabled DataProducts, but is: %s' %
                    cluster_name_set
                )
            else:  # reservation or maintenance
                cluster_name = cluster_name_set.pop()

                # Retrieve known cluster names (not all may be a valid storage target, but we cannot know...)
                known_cluster_set = {cluster['name'] for cluster in
                                     self.radb.getResourceGroupNames('cluster')}
                if cluster_name not in known_cluster_set:
                    raise Exception("skipping resource assignment for task with cluster name '" + cluster_name +
                                    "' not in known clusters " + str(known_cluster_set)) #TODO better error
                # else:
                #     #TODO Is this still a bug?
                #     # fix for MoM bug introduced before NV's holiday
                #     # MoM sets ProcessingCluster.clusterName to CEP2 even when inputxml says CEP4
                #     # so, override it here if needed, and update to otdb
                #     processing_cluster_name = parset.getString(
                #         PARSET_PREFIX + 'Observation.Cluster.ProcessingCluster.clusterName',
                #         '')
                #     if processing_cluster_name != cluster_name:
                #         logger.info(
                #             'overwriting and uploading processingClusterName to otdb from \'%s\' to \'%s\' '
                #             'for otdb_id=%s', processing_cluster_name, cluster_name, self.otdb_id)
                #         self.otdbrpc.taskSetSpecification(
                #             self.otdb_id,
                #             {'LOFAR.ObsSW.Observation.Cluster.ProcessingCluster.clusterName': cluster_name}
                #         )

        return cluster_name

    @staticmethod
    def _get_storage_cluster_names_from_parset(parset, PARSET_PREFIX):
        """
        Get the storage cluster names for all enabled output data product types in parset

        :param parset: parameterset
        :param PARSET_PREFIX: Fixed prefix that's to be added to the used OTDB keys

        :raises Exception if an enabled output data product type has no storage cluster name specified.
        :returns set of cluster names
        """
        cluster_names = set()

        keys = ['Output_Correlated',
                'Output_IncoherentStokes',
                'Output_CoherentStokes',
                'Output_InstrumentModel',
                'Output_SkyImage',
                'Output_Pulsar']
        for key in keys:
            if parset.getBool(PARSET_PREFIX + 'Observation.DataProducts.%s.enabled' % key, False):
                # may raise; don't pass default arg
                name = parset.getString(PARSET_PREFIX + 'Observation.DataProducts.%s.storageClusterName' % key)
                cluster_names.add(name)

        return cluster_names

    def _store_changed_start_and_end_times_to_otdb(self, start_time, end_time, duration, otdb_id):
        """
        Stores the modified start/end times to the OTDB

        :param start_time: the task's start time
        :param end_time:  the task's end time
        :param duration: the task's duration
        :param otdb_id: the task's OTDB ID
        """

        logger.info('uploading auto-generated start/end time  (%s, %s) to otdb for otdb_id=%s',
                    start_time, end_time, otdb_id)

        self.otdbrpc.taskSetSpecification(self.otdb_id,
            {OUTPUT_PREFIX + 'Observation.startTime': start_time.strftime('%Y-%m-%d %H:%M:%S'),
             OUTPUT_PREFIX + 'Observation.stopTime': end_time.strftime('%Y-%m-%d %H:%M:%S'),
             OUTPUT_PREFIX + 'Observation.Scheduler.taskDuration': str(duration.total_seconds())
            }
        )

# =========================================== Start/End time, duration =================================================
#TODO test if this also works again for non-triggered observations

    def _get_maximum_predecessor_end_time(self):
        """
        Determine the highest end time of all predecessors

        :return: the maximum predecessor end time found, or None in case no predecessors are specified
        """

        predecessor_end_times = [spec.endtime for spec in self.predecessors]
        if predecessor_end_times:
            return max(predecessor_end_times)
        return None

    def _push_back_start_time_to_not_overlap_predecessors(self, start_time):
        """
        Determines a new start time for a task when the current start time of that task overlaps with its
        predecessors.

        :param start_time: the task's start time

        :return: The updated start time
        """

        pushed_back_start_time = start_time

        # Make sure the start time lies past the end time of the task's predecessors
        max_predecessor_end_time = self._get_maximum_predecessor_end_time()
        if max_predecessor_end_time and max_predecessor_end_time > start_time:
            pushed_back_start_time = max_predecessor_end_time + timedelta(minutes=3)

        return pushed_back_start_time

    def update_start_end_times(self):
        """
        Get the start time and end time of the main task modified such that (a) there's a period of 3 minutes between
        tasks and (b) the start time and end time are actually in the future.

        If the start time lies in the past or is not specified it is set to 3 minutes from the current time. The new end
        time in that case is calculated using the specified duration or, if that is not specified, from the original
        difference between start and end time. When a duration can't be determined the end time will be set to 1 hour
        after the start time.

        :returns 2-tuple (start_time, end_time)
        """
        # TODO: 1a: don't fix this crap here. Bad start/stop time has to go to error, like any other bad spec part.
        # TODO: 1b: make this into a method which does not modify this instance, but returns a new Specification
        # TODO: 1b: instance with proper *times.
        # TODO: 2: fix this way too complicated if/else tree

        if self.isMovable(): # not maintenance and reservation
            shift = timedelta(seconds=0)
            starttime = self.starttime
            intial_duration = self.duration

            if not intial_duration:
                intial_duration = timedelta(hours=1)
            if self.endtime and self.starttime:
                intial_duration = self.endtime - self.starttime

            # Make sure the start time lies in the future and doesn't overlap with any predecessors
            now = datetime.utcnow()
            min_allowed_starttime = now + timedelta(minutes=3)

            if not self.starttime or self.starttime < min_allowed_starttime:
                starttime = min_allowed_starttime
            starttime = self._push_back_start_time_to_not_overlap_predecessors(starttime)
            if self.starttime:
                shift = starttime - self.starttime
            self.starttime = starttime

            # If minStartTime and maxEndTime are specified (by a trigger) they take precedence
            if self.min_starttime:
                if self.min_starttime < min_allowed_starttime:
                    dwell_shift = min_allowed_starttime - self.min_starttime
                    self.min_starttime = min_allowed_starttime
                    if self.max_endtime:
                        self.max_endtime = self.max_endtime + dwell_shift
            else:
                self.min_starttime = max(min_allowed_starttime, self.starttime)

            self.starttime = self.min_starttime

            if self.max_endtime:
                # self.min_starttime has already been checked and corrected
                if self.max_endtime <= self.min_starttime:
                    self.max_endtime = self.min_starttime + intial_duration
            else:
                self.max_endtime = self.min_starttime + intial_duration

            # TODO Not happy with this min/maxDuration, what to do if duration is not None but they are set?
            if not self.duration:
                if self.max_duration:
                    self.duration = self.max_duration
                elif self.min_duration:
                    self.duration = self.min_duration

            # Check if duration and endtime have values
            if not self.duration and not self.endtime:
                self.duration = timedelta(hours=1)
                # check duration between min_duration and max_duration
                if self.max_duration:
                    self.duration = min(self.duration, self.max_duration)
                if self.min_duration:
                    self.duration = max(self.duration, self.min_duration)
                self.endtime = self.starttime + self.duration
                logger.warning('Setting default duration of %s for otdb_id=%s', self.duration, self.otdb_id)
            elif not self.endtime:
                self.endtime = self.starttime + self.duration
            self.endtime  = self.endtime + shift
            self.duration = self.endtime - self.starttime

            if self.isPipeline():
                # check duration between min_duration and max_duration
                if self.max_duration:
                    self.duration = min(self.duration, self.max_duration)
                if self.min_duration:
                    self.duration = max(self.duration, self.min_duration)

            if shift:
                logger.warning('Shifted otdb_id=%s by %s to new start/end time (%s, %s)',
                                    self.otdb_id, shift, self.starttime, self.endtime)

        else:  # maintenance and reservation
            if not self.starttime or not self.endtime:
                raise ValueError("Start and end times are not set for otdb_id=%s where we can't change them."
                                 % self.otdb_id)
            self.duration = self.endtime - self.starttime

        self._store_changed_start_and_end_times_to_otdb(self.starttime, self.endtime, self.duration, self.otdb_id)
        # TODO self._store_changed_start_and_end_times_to_mom(self.starttime, self.endtime, self.duration, self.otdb_id)

    # TODO maybe use min_duration, max_duration if specified? DwellScheduler can't use them right now?
    def calculate_dwell_values(self, start_time, duration, min_starttime, max_endtime):
        """ Use any specified min_starttime/max_endtime to calculate the min_starttime/max_starttime. All timestamps are in
        datetime format

        :param start_time:      Task fixed start time
        :param end_time:        Task fixed end time
        :param min_starttime:   Task minimum start time
        :param max_endtime:     Task maximum end time

        :return: 3-tuple (min_starttime, max_starttime, duration)
        """
        if not start_time or not duration or not min_starttime or not max_endtime:
            raise ValueError("To calculate dwell values, all inputs need to be set: start: %s duration: %s min: %s max: %s" %
                             (start_time, duration, min_starttime, max_endtime))
        # Calculate the effective dwelling time
        max_duration = max_endtime - min_starttime

        if max_duration < timedelta(minutes=0):
            raise ValueError('task max_duration %s should not be smaller than 0' % (max_duration,))

        if duration > max_duration:
            raise ValueError('task duration %s is larger than max_duration %s from dwelling start/end time' % (duration, max_duration))

        dwell_time = max_duration - duration

        # Calculate min/max starttime
        min_starttime = min(start_time, min_starttime)
        max_starttime = min_starttime + dwell_time
        return min_starttime, max_starttime, duration

# =========================================== RADB related methods =======================================================

    #TODO we might need read_from_radb_with_predecessors in the future
    def read_from_radb(self, radb_id):
        """The returned task is from "SELECT * from resource_allocation.task_view tv" with start/endtime
        converted to a datetime. This only reads a few values from the RADB, not the whole specification.

        :return: task dict (radb_id, mom_id, otdb_id, status_id, type_id, specification_id, status, type,
        starttime, endtime, duration, cluster) or None
        """
        #TODO maybe this should read the spec as well? Can especially start/end times be updated outside of here?
        task = self.radb.getTask(radb_id)  # if radb_id is not None else None
        if task: #TODO what is the exact structure of task see schedulerchecker 47
            self.radb_id  = task["id"] # Should be the same as radb_id, but self.radb_id might not yet be set
            self.mom_id   = task["mom_id"]
            self.otdb_id  = task["otdb_id"]
            self.status   = task["status"]
            self.type     = task["type"]
            self.duration = timedelta(seconds = task["duration"])
            self.cluster  = task.get("cluster", "CEP4")
            #we don't seem to need specification_id?
            logger.info("Read task from RADB: %s", task)
            return task
        else:
            return None

    def insert_into_radb(self):
        """
        Tries to inserts the task's specification into RADB along with any of its predecessors and successors.

        :return: task dict (radb_id, mom_id, otdb_id, status_id, type_id, specification_id, status, type,
        starttime, endtime, duration, cluster) or None

        :raises Exception if a task can't be inserted into RADB
        """

        self._check_has_status_owned_by_RA()

        self.radb_id = self._insert_main_task()

        task = self.read_from_radb(self.radb_id)

        self._link_predecessors_to_task_in_radb()
        self._link_successors_to_task_in_radb()

        logger.info('Successfully inserted main task and its predecessors and successors into RADB: task=%s', task)

        return task

    def _check_has_status_owned_by_RA(self):
        """
        Verifies if a task can actually be assigned by looking at its status. Raises an exception if the task is not
        assignable.

        :raises Exception if it isn't owned by RA
        """

        assignable_task_states = ['approved', 'prescheduled', 'error']
        if self.status in assignable_task_states:
            logger.info('Task otdb_id=%s with status \'%s\' is assignable' % (self.otdb_id, self.status))
        else:
            assignable_task_states_str = ', '.join(assignable_task_states)
            logger.warn('Task otdb_id=%s with status \'%s\' is not assignable. Allowed statuses are %s' %
                        (self.otdb_id, self.status, assignable_task_states_str))

            message = "Unsupported status '%s' of task with OTDB ID: %s" % (self.status, self.otdb_id)
            raise Exception(message) #TODO more specific exception type?

    def set_status(self, new_status):
        """
        Updates a task's status in RADB.

        :param new_status: the new status to set the task to in RADB

        :raises Exception if updating RADB fails
        """
        self.status = new_status
        # TODO Check on RADB_ID should be done differently
        if new_status in ('conflict', 'error', 'scheduled'):
            logger.info('Setting status for task_id=%s, status=%s' % (self.radb_id, new_status))
            # another service sets the parset spec in OTDB, and updated otdb task status to scheduled, which is then
            # synced back to RADB
            if self.radb_id:
                self.radb.updateTask(self.radb_id, task_status=new_status)
            # TODO what? else:
            #    self.radbrpc.updateTaskStatusForOtdbId(self.otdb_id, 'error')
        #TODO, see if we move _send_task_status_notification from resource_assigner to here?
        #Now it's really opaque to users that this should be called

    def _insert_main_task(self):
        """
        Inserts the main task and its specification into the RADB. Any existing specification and task with same
        otdb_id will be deleted automatically.

        :return: task_id of the inserted task
        :raises Exception if there's an unforeseen problem while inserting the task and its specifications into RADB
        """

        logger.info(
            'insertSpecification mom_id=%s, otdb_id=%s, status=%s, task_type=%s, start_time=%s, end_time=%s '
            'cluster=%s' % (self.mom_id, self.otdb_id, self.status, self.type, self.starttime, self.endtime, self.cluster)
        )
        result = self.radb.insertOrUpdateSpecificationAndTask(self.mom_id, self.otdb_id, self.status, self.type, self.starttime,
                                                              self.endtime, str(self.as_dict()), self.cluster, commit=True) #TODO use internal_dict?

        specification_id = result['specification_id'] # We never seem to need this again
        task_id = result['task_id']
        logger.info('inserted/updated specification (id=%s) and task (id=%s)' % (specification_id, task_id))
        return task_id

    def _link_predecessors_to_task_in_radb(self):
        """
        Links a task to its predecessors in RADB
        """
        #TODO how to keep the predecessors in MoM and in OTDB in sync here? Does it matter?

        predecessor_ids = self.momquery.getPredecessorIds(self.mom_id)
        if str(self.mom_id) not in predecessor_ids or not predecessor_ids[str(self.mom_id)]:
            logger.info('no predecessors for otdb_id=%s mom_id=%s', self.otdb_id, self.mom_id)
            return
        predecessor_mom_ids = predecessor_ids[str(self.mom_id)]

        logger.info('processing predecessor mom_ids=%s for mom_id=%s otdb_id=%s', predecessor_mom_ids, self.mom_id, self.otdb_id)

        for predecessor_mom_id in predecessor_mom_ids:
            # check if the predecessor needs to be linked to this task
            predecessor_task = self.radb.getTask(mom_id=predecessor_mom_id)
            if predecessor_task:
                # do Specification-class bookkeeping (stupid, because all info is in the radb already)
                predecessor_keys = [p.radb_id for p in self.predecessors]
                if predecessor_task['id'] not in predecessor_keys:
                    logger.info('connecting predecessor task with mom_id=%s otdb_id=%s to its successor with mom_id=%s '
                                'otdb_id=%s', predecessor_task['mom_id'], predecessor_task['otdb_id'], self.mom_id,
                                self.otdb_id)
                    pred_spec = Specification(self.otdbrpc, self.momquery, self.radb)
                    pred_spec.read_from_radb(predecessor_task['id'])
                    self.predecessors.append(pred_spec)  # TODO this needs a try/except somewhere?


                # do radb task-predecessor bookkeeping if needed
                try:
                    task = self.radb.getTask(self.radb_id)
                    if predecessor_task['id'] not in task['predecessor_ids']:
                        self.radb.insertTaskPredecessor(self.radb_id, predecessor_task['id'])
                except PostgresDBQueryExecutionError as e:
                    # task was already connected to predecessor. Log and continue.
                    if 'task_predecessor_unique' in str(e):
                        logger.info('predecessor task with mom_id=%s otdb_id=%s was already connected to its successor with mom_id=%s otdb_id=%s',
                                    predecessor_task['mom_id'], predecessor_task['otdb_id'],
                                    self.mom_id, self.otdb_id)
                    else:
                        raise
            else:
                # Occurs when setting a pipeline to prescheduled while a predecessor has e.g. never been beyond
                # approved, which is in principle valid. The link in the radb will be made later via processSuccessors()
                # below. Alternatively, a predecessor could have been deleted.
                logger.warning('could not find predecessor task with mom_id=%s in radb for task otdb_id=%s',
                               predecessor_mom_id, self.otdb_id)

    def _link_successors_to_task_in_radb(self):
        """
        Links a task to its successors in RADB
        """
        #FIXME Not sure if this works, as self.successor_ids might not be set outside of here

        successor_ids = self.momquery.getSuccessorIds(self.mom_id)
        if str(self.mom_id) not in successor_ids or not successor_ids[str(self.mom_id)]:
            logger.info('no successors for otdb_id=%s mom_id=%s', self.otdb_id, self.mom_id)
            return
        successor_mom_ids = successor_ids[str(self.mom_id)]

        logger.info('processing successor mom_ids=%s for mom_id=%s otdb_id=%s', successor_mom_ids, self.mom_id,
                    self.otdb_id)

        for successor_mom_id in successor_mom_ids:
            # check if the successor needs to be linked to this task
            successor_task = self.radb.getTask(mom_id=successor_mom_id)
            if successor_task:
                if successor_task['id'] not in self.successor_ids:
                    logger.info(
                        'connecting successor task with mom_id=%s otdb_id=%s to its predecessor with mom_id=%s'
                        ' otdb_id=%s', successor_task['mom_id'], successor_task['otdb_id'], self.mom_id, self.otdb_id
                    )
                    self.successor_ids.append(successor_task['id'])

                # do radb task-successor bookkeeping if needed
                try:
                    task = self.radb.getTask(self.radb_id)
                    if successor_task['id'] not in task['successor_ids']:
                        self.radb.insertTaskPredecessor(successor_task['id'], self.radb_id)
                except PostgresDBQueryExecutionError as e:
                    # task was already connected to predecessor. Log and continue.
                    if 'task_predecessor_unique' in str(e):
                        logger.info('successor task with mom_id=%s otdb_id=%s was already connected to its predecessor with mom_id=%s otdb_id=%s',
                                    successor_task['mom_id'], successor_task['otdb_id'],
                                    self.mom_id, self.otdb_id)
                    else:
                        raise

                movePipelineAfterItsPredecessors(successor_task, self.radb)
            else:
                # Occurs when settings a obs or task to prescheduled while a successor has e.g. not yet been beyond
                # approved, which is quite normal. The link in the radb will be made later via processPredecessors()
                # above. Alternatively, a successor could have been deleted.
                logger.warning('could not find successor task with mom_id=%s in radb for task otdb_id=%s',
                               successor_mom_id, self.otdb_id)
