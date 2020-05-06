#!/usr/bin/env python3

# lofarxml_to_momxml_translator.py
#
# Copyright (C) 2017
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

#
# This translator will create a MoM-compatible document from a LofarSpec
#
# Basic approach:
# - It parses relations on the Lofar spec and creates a base document with a folder hierarchy for MoM
# - It moves some basic info from the Lofar spec to the MoM document
# - For each activity
#   -  elements are moved/renamed where nested differently in MoM
#   -  some elements need further conversion, like clock/stations, which is handled in the code
#   -  elements unknown to MoM are encoded as json and placed in a <misc> element.
#   -  the mom-compatible activity / item is placed in the folder hierarchy
#
# Disclaimer: Want to change something? Before you tumble down this rabbit hole: Grab a coffee. (Make it strong.)
#
# TODO: The translation does not have full coverage at the moment. This stuff is still missing:
# TODO:
# TODO: Calibrator pipelines (Doesn't handle InstrumentModels and topology).
# TODO: Pulsar pipelines.
# TODO: TBB observations.
# TODO: Probably Imaging and LongBaseline pipelines.

from json import dumps, loads
from collections import OrderedDict
from lxml import etree
from xmljson import Parker
import re
import datetime

from .config import VALIDATION_SERVICENAME
from .validation_service_rpc import ValidationRPC
from .specification_service import _parse_relation_tree, make_key, _parse_project_code
from lofar.common.xmlparse import parse_xml_string_or_bytestring
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

from io import BytesIO
import logging

__version__ = '0.43'
__author__ = "Joern Kuensemoeller"
__changedBy__ = "Joern Kuensemoeller"

logger = logging.getLogger(__name__)

validationrpc = ValidationRPC.create(DEFAULT_BUSNAME, DEFAULT_BROKER)

# ------------------------
# -> For moving elements:

# these types of activity are translateable
ACTIVITY_TYPES = ["observation", "pipeline", "measurement"]  # "ingest", "cleanup"] <- how to translate these?

# items in MOM_ACTIVITY_ATTRIBUTE_MAPPING that are abstract.
# the activityname in these will be replaced by the specific type as per xsi:type attribute in the Mom namepace,
# preserving the rest. e.g. 'pipelineAttributes' -> 'averagingPipelineAttributes'
#
# (Note from the dev: sorry for the complicated mechanism, but the type of the activity is specified as xsi:type...
# ...while this does not work for the attributes element, which is specifically named after the type. So simply...
# ---mapping all of them is not possible.)
ABSTRACT_MOM_ELEMENTS = ["pipelineAttributes", "measurementAttributes"]

# The following mapping describes what has to be put somewhere else for mom.
# If the element in the dict key exists, it is moved to the element defined in value and renamed if
# Notes:
# - ! Order matters - This needs to be an ordered dict so the item sequence in the destination is not messed up!
# - Only the first occurence of nodes are moved, so the paths should be unique for each activity.
# - Path root in the key is the lofar spec activity element, and paths in the value are rooted in the item element
# - '::' is separator, since '.' or '/' don't work due to occurrence in namespace uri

# todo: check whether this can be simplified with xpath.
MOM_ACTIVITY_ATTRIBUTE_MAPPING = OrderedDict([
    ("triggerId::identifier", "trigger_id"),
    #
    ## Observations
    #
    ("observation::timeWindowSpecification::minStartTime",
     "timeWindow::minStartTime"),
    ("observation::timeWindowSpecification::maxEndTime",
     "timeWindow::maxEndTime"),
    ("observation::timeWindowSpecification::duration::minimumDuration",
     "timeWindow::minDuration"),
    ("observation::timeWindowSpecification::duration::maximumDuration",
     "timeWindow::maxDuration"),
    # ---
    # This works nice for a single non-Custom stationset, but this is better solved elsewhere specifically:
    #("observation::stationSelectionSpecification::stationSelection::stationSet",
    # "stationSelection::resourceGroup"),
    #("observation::stationSelectionSpecification::stationSelection::minimumConstraint",
    # "stationSelection::min"),
    # ---
    ("observation::instrument",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::instrument"),
    ("observation::defaultTemplate",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::defaultTemplate"),
    ("observation::tbbPiggybackAllowed",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::tbbPiggybackAllowed"),
    ("observation::aartfaacPiggybackAllowed",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::aartfaacPiggybackAllowed"),
    ("observation::correlatedData",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::correlatedData"),
    ("observation::filteredData",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::filteredData"),
    ("observation::beamformedData",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::beamformedData"),
    ("observation::coherentStokesData",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::coherentStokesData"),
    ("observation::incoherentStokesData",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::incoherentStokesData"),
    ("observation::antenna",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::antenna"),
    ("observation::clock",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::clock"),
    ("observation::instrumentFilter",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::instrumentFilter"),
    ("observation::integrationInterval",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::integrationInterval"),
    ("observation::channelsPerSubband",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::channelsPerSubband"),
    ("observation::coherentDedisperseChannels", # todo: probably old BlueGene and no longer needed
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::coherentDedisperseChannels"),
    ("observation::tiedArrayBeams", # todo: probably old BlueGene and no longer needed, will give default hints in the UI
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::tiedArrayBeams"),
    ("observation::stokes",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::stokes"),
    ("observation::flysEye",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::tiedArrayBeams::flyseye"),
    # all stationsets should've been converted to misc beforehand. This moves the only remaining 'custom' stationset to where MoM looks for it:
    ("observation::stationSelectionSpecification::stationSelection::stationSet",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::stationSet"),
    ("observation::stationSelectionSpecification::stationSelection::stations",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::stations"),
    ("observation::timeWindowSpecification::timeFrame",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::timeFrame"),
    ("observation::timeWindowSpecification::startTime",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::startTime"),
    ("observation::timeWindowSpecification::endTime",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::endTime"),
    ("observation::timeWindowSpecification::duration::duration",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::duration"),
    ("observation::bypassPff", # todo: probably old BlueGene and no longer needed
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::bypassPff"),
    ("observation::enableSuperterp",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::enableSuperterp"),
    ("observation::numberOfBitsPerSample",
     "observation::{http://www.astron.nl/MoM2-Lofar}observationAttributes::userSpecification::numberOfBitsPerSample"),
    #
    ##  Pipelines
    #
    # !!! Note: When attributes are shared between pipeline types, they appear once here, but have to appear in correct
    #      ...position for all pipelines! Only defaultTemplate is currently shared and it's in the beginning everywhere.
    #
    # shared amongst pipelines:
    ("pipeline::defaultTemplate", "pipeline::pipelineAttributes::defaultTemplate"),
    # averaging pipeline:
    ("pipeline::demixingParameters", "pipeline::pipelineAttributes::demixingParameters"),
    ("pipeline::bbsParameters", "pipeline::pipelineAttributes::bbsParameters"),
    ("pipeline::flaggingStrategy", "pipeline::pipelineAttributes::flaggingStrategy"),
    ("pipeline::frequencyIntegrationStep", "pipeline::pipelineAttributes::frequencyIntegrationStep"),
    ("pipeline::timeIntegrationStep", "pipeline::pipelineAttributes::timeIntegrationStep"),
    # imaging pipeline:
    ("pipeline::imagerIntegrationTime", "pipeline::pipelineAttributes::imagerIntegrationTime"),
    # pulsar pipeline:
    ("pipeline::_2bf2fitsExtraOpts", "pipeline::pipelineAttributes::_2bf2fitsExtraOpts"),
    ("pipeline::_8bitConversionSigma", "pipeline::pipelineAttributes::_8bitConversionSigma"),
    ("pipeline::decodeNblocks", "pipeline::pipelineAttributes::decodeNblocks"),
    ("pipeline::decodeSigma", "pipeline::pipelineAttributes::decodeSigma"),
    ("pipeline::digifilExtraOpts", "pipeline::pipelineAttributes::digifilExtraOpts"),
    ("pipeline::dspsrExtraOpts", "pipeline::pipelineAttributes::dspsrExtraOpts"),
    ("pipeline::dynamicSpectrumTimeAverage", "pipeline::pipelineAttributes::dynamicSpectrumTimeAverage"),
    ("pipeline::nofold", "pipeline::pipelineAttributes::nofold"),
    ("pipeline::nopdmp", "pipeline::pipelineAttributes::nopdmp"),
    ("pipeline::norfi", "pipeline::pipelineAttributes::norfi"),
    ("pipeline::prepdataExtraOpts", "pipeline::pipelineAttributes::prepdataExtraOpts"),
    ("pipeline::prepfoldExtraOpts", "pipeline::pipelineAttributes::prepfoldExtraOpts"),
    ("pipeline::prepsubbandExtraOpts", "pipeline::pipelineAttributes:prepsubbandExtraOpts"),
    ("pipeline::pulsar", "pipeline::pipelineAttributes::pulsar"),
    ("pipeline::rawTo8bit", "pipeline::pipelineAttributes:rawTo8bit"),
    ("pipeline::rfifindExtraOpts", "pipeline::pipelineAttributes::rfifindExtraOpts"),
    ("pipeline::rrats", "pipeline::pipelineAttributes::rrats"),
    ("pipeline::singlePulse", "pipeline::pipelineAttributes::singlePulse"),
    ("pipeline::skipDsps", "pipeline::pipelineAttributes::skipDsps"),
    ("pipeline::skipDynamicSpectrum", "pipeline::pipelineAttributes::skipDynamicSpectrum"),
    ("pipeline::skipPrepfold", "pipeline::pipelineAttributes::skipPrepfold"),
    ("pipeline::tsubint", "pipeline::pipelineAttributes::tsubint"),
    #
    ## Measurements
    #
    # BeamMeasurement
    ("measurement::measurementType", "measurement::measurementAttributes::measurementType"),
    ("measurement::targetName", "measurement::measurementAttributes::specification::targetName"),
    ("measurement::ra", "measurement::measurementAttributes::specification::ra"),
    ("measurement::ra", "measurement::measurementAttributes::specification::ra"),
    ("measurement::dec", "measurement::measurementAttributes::specification::dec"),
    ("measurement::equinox", "measurement::measurementAttributes::specification::equinox"),
    ("measurement::duration", "measurement::measurementAttributes::specification::duration"),
    ("measurement::subbandsSpecification", "measurement::measurementAttributes::specification::subbandsSpecification"),
    ("measurement::tiedArrayBeams", "measurement::measurementAttributes::specification::tiedArrayBeams"),
    # todo: If used, LofarBeamMeasurementSpecificationAttributesType requires more items!
    # todo: add other measurements? Currently not defined on LofarBase.xsd, so these cannot occur...
])

# -----------
# -> For encoding new stuff (that's too fancy for MoM) in the misc field:

# These activity types can carry a misc element for extraspec.
# Measurements do not have that, but have to have a parent observation that has.
ACTIVITIES_WITH_MOM_EXTRASPECS = ['observation', 'pipeline']

# These specification elements are to be recoded for MoM as json
# Note: This happens after nodes are moved according to mapping, so restructure/rename first the way this is required
#       ...on the misc field and add the parent items of what's to encode here.
MOM_ACTIVITY_EXTRASPECS = [
    "trigger_id",
    "priority",
    "qualityOfService",
    "timeWindow",
    "stationSelection",  # <- stationSelectionSpecification is parsed prior and placed there in correct format
    # "pipeline..." # no pipeline time constraints...?
]

# ----------------
# -> For removing lefovers that MoM doesn't understand.

# These elements should simply be removed before exporting the mom xml because they are not understood by MoM
# (any important info should be moved out of here earlier, others may be safe to remove.
MOM_ACTIVITY_REMOVABLE_ELEMENTS = [
    'observation::timeWindowSpecification',
    'observation::stationSelectionSpecification',
]


#--------------------
# Topology
#
dptopologytypes = {
    "BFDataProduct_CoherentStokes": 'cs',
    "BFDataProduct_IncoherentStokes": 'is',# <-- todo: csis support not implemented
    "UVDataProduct": 'uv', # <-- todo: InstrumentModel
    #"TBBDataProduct": 'tbb',  # <-- todo: tbb currently not implemented in MoM
    #"PixelMapDataProduct": '',  # <-- todo:  pixelmap currently not implemented fully in MoM
    "SkyImageDataProduct": 'si', # <-- MoM doens't really care I tihnk? check
    "PulsarDataProduct": 'pu' # <-- MoM doens't really care I tihnk? check
}

class LofarXmlToMomXmlTranslator():

    def _find_or_create_subelement(self, element, name, index=None):
        """
        returns element child with given name. Creates it if not present.
        """

        sub = element.find(str(name))
        if sub is None:
            # create it
            if index is not None:
                sub = etree.Element(name)
                element.insert(index, sub)
            else:
                sub = etree.SubElement(element, name)
        return sub

    def _jsonify(self, xml):
        """
        converts xml string to json string
        """
        bf = Parker(dict_type=OrderedDict)
        data = bf.data(etree.fromstring(xml))
        json = dumps(data)
        return json


    def _parse_entities(self, spec):
        """
        returns lookup dictionaries for entity relations
        """

        entities = spec.findall('entity')
        inputentities = {}   # activity identifier -> list of entity identifiers
        outputentities = {}   # activity identifier -> list of entity identifiers
        entitytypes = None   # entity identifier -> entity type name
        entityclusterelems = None  # entity identifier -> <storageCluster> element/subtree
        entityproducers = {} # entitiy identifier -> activity identifier
        entityusers = {} # entitiy identifier -> activity identifier

        if entities is not None:
            producer = [(x.find("entity"), x.find("activity")) for x in spec.findall("relation") if
                               x.find("type").text == "producer"]
            user = [(x.find("entity"), x.find("activity")) for x in spec.findall("relation") if
                        x.find("type").text == "user"]

            for (entity_id, activity_id) in producer:
                outputentities.setdefault(make_key(activity_id), []).append(make_key(entity_id))
                entityproducers[make_key(entity_id)] = make_key(activity_id)

            for (entity_id, activity_id) in user:
                inputentities.setdefault(make_key(activity_id), []).append(make_key(entity_id))
                entityusers[make_key(entity_id)] = make_key(activity_id)

            entitytypes = {make_key(entity.find("temporaryIdentifier")): entity.find('dataproductType').text
                           for entity in entities}

            entityclusterelems = {make_key(entity.find("temporaryIdentifier")): entity.find('storageCluster')
                              for entity in entities}

        return inputentities, outputentities, entitytypes, entityclusterelems, entityproducers, entityusers

    def _create_foldertree_in_momproject(self, spec, mom_project):
        """
        Parses the relations in the LOFAR specs and creates the folder hiararchy in the given MoM project
        Returns a dict to look up the folder element that is meant to contain an activity (identifier is key).
        Returns a dict to look up the assigned groupid of activities (for use in topology)
        Returns a dict to look up the assigned myid of measurements/observations (for use in topology)
        """
        try:
            activityfolders, parentfolders, foldernames = _parse_relation_tree(spec)

            containers = spec.findall('container')
            momfolders = {}  # holds elements, not keys!
            activityparents = {}  # holds elements, not keys!
            folder_topologygroup = {}
            activity_topologygroup = {}
            added_folders = []

            # populate folder element dictionary. folder identifier is key
            counter = 0
            for container in containers:
                key = make_key(container.find("temporaryIdentifier"))
                folder = container.find('folder')
                momfolder = etree.Element('{http://www.astron.nl/MoM2-Lofar}folder')
                for child in folder.getchildren():
                    momfolder.append(child)
                    updateelem = container.find("addToExistingContainer")
                    if updateelem is not None:
                        momfolder.attrib["update_folder"] = updateelem.text
                momfolders[key] = momfolder
                counter += 1
                folder_topologygroup[key] = 'B' + str(counter)

            # create folder hierarchy
            for activikey in list(activityfolders.keys()):
                key = activityfolders[activikey]
                activityparents[activikey] = momfolders[key]
                activity_topologygroup[activikey] = folder_topologygroup[key]
                activity_topologygroup[activikey] = folder_topologygroup[key]

                # recursively walk towards root to determine what subtree requires creation:
                to_add = []
                while key is not None:
                    if key in added_folders:
                        break  # already there, so create the children up to here only
                    to_add.append(key)
                    if key in list(parentfolders.keys()):
                        key = parentfolders[key]
                    else:
                        break

                # create towards activity and create the missing folder hierarchy:
                for key in reversed(to_add):

                    # create folder
                    folder = momfolders[key]
                    if key in parentfolders:
                        parent = momfolders[parentfolders[key]]
                    else:
                        parent = mom_project

                    children = self._find_or_create_subelement(parent, "children")
                    index = len(children.getchildren())
                    item = etree.SubElement(children, "item")
                    item.append(folder)
                    if 'index' not in item.attrib:
                        item.attrib['index'] = str(index)
                    added_folders.append(key)

                    # In the templates I see:
                    # folder topology is generally '0' or the index, topology_parent is true on inner folders
                    topology = index  # "[header] [groupid] [myid] [slice]"   # Is 0 some magic number here?
                    if key not in parentfolders:
                        istopparent = False
                    else:
                        istopparent = True

                    tindex = 0  # where to insert in parent
                    folder.attrib['topology_parent'] = str(istopparent).lower()
                    intop = folder.find('topology')
                    intopstr = None
                    if intop is not None:
                        intopstr = intop.text
                        folder.remove(intop)
                    top = self._find_or_create_subelement(folder, 'topology', tindex)
                    if intopstr is not None:
                        top.text = intopstr   # todo: should the spec override what it auto-determined?
                    else:
                        top.text = topology

            # Not only containers can contain children, but also observations.
            # Determine measurement -> parent observation mapping.
            observation_measurement = [(x.find("parent"), x.find("child")) for x in spec.findall("relation")
                                       if x.find("type").text == "observation-measurement"]
            observation_acts = [x for x in spec.findall('activity') if x.find('observation') is not None]
            observations = {}

            for obs_act in observation_acts:
                key = make_key(obs_act.find("temporaryIdentifier"))
                observations[key] = obs_act.find('observation')

            # measurements share group ID with the observation and the obs' parent folder
            # measurements share myid with the parent observation.
            mcounter = 1
            activity_topologymyid = {}
            for (obs_id, measurement_id) in observation_measurement:
                key = make_key(obs_id)
                measurekey = make_key(measurement_id)
                obskey = make_key(obs_id)
                activityparents[measurekey] = observations[key]
                activity_topologygroup[measurekey] = activity_topologygroup[key]
                if obskey in activity_topologymyid:
                    activity_topologymyid[measurekey] = activity_topologymyid[obskey]
                else:
                    activity_topologymyid[measurekey] = str(mcounter)
                    activity_topologymyid[obskey] = str(mcounter)
                    mcounter += 1

            return activityparents, activity_topologygroup, activity_topologymyid

        except Exception as err:
            logger.error("Error occurred while creating folder hierarchy -> " + str(err))
            raise

    def _create_topology(self, header = None, groupid = None, myid = None, slice = None, function = None, sap = None, dptype = None):
        """
        Returns a topology string based on provided information. Most of these are not actually parsed, according to
        documentation, so we may fill in anything as long as the result is unique. It seems ok to leave items blank.
        (No idea how a potential parser would determine which ones are missing, it seems completely ambiguous...)

        I don't make use of header and slice, actually, and use the others as follows:
        groupid: unique id per folder B[index], used by everything in there
        myid: unique id per observation, used by related measurements / pipelines as well
        function: 'T' for obs/measurements, 'P[index]' for pipelines
        sap: using child index, assuming observation only has measurements as children
        dptype: According to dataproduct type

        ---

        The documentation provides the following:

        header: "mom_msss_" (for MSSS), "mom_" (for non-MSSS) | not actually used as far as I can tell
        groupid: "[folderId]" (MSSS), "M[momId]" (non-MSSS), "G[folderId]" (non-MSSS) | topology_parent="true" allows to have MoM-ID of some 'main folder' to be added here automagically | some of this may be parsed by MoM
        myid: "M[momId]" | to make it unique if not otherwise | apparently not actually parsed
        slice: MSSS slice | Not actually parsed, but predecessors need to have same value here
        function: "C" (calibrator), "T" (Target), "P1,P2,P3,P4,PX,PY,PZ" (Pipelne), "CT" (Calibration and Target), "CP" (Calibration Pipelne), "IP" (Imaging Pipelne), "X" (unknown) | Parsed by MoM
        sap = "SAP"XXX[".dps"] | Measurement; with suffix a measurement entity / dataproduct
        dptype = ".uv" (correlated data), ".bf" (beamformed data) - no longer used,  ".cs" (coherent stokes data), ".is" (incoherent stokes data), ".csis" (coherent stokes and incoherent stokes data), ".im" (instrument model), ".si" (sky image), ".pu" (pulsar data) | marked red, so probably parsed somewhere, but no indication where

        The examples in the docs then have something contradictory like this:

        B0.1.CPT.dps.im <-- where B0 is block zero, 1 is the index of the calibration pipeline (CPT) of which we have an instrument model entity here.
        I assume CPT should be CP, and the '.dps' seems to be linked ot the dptype, not sap. That's apparently wrong, but pretty clear.
        The 'B0' and '1' do not really fit (n)either semantically or in the documented naming scheme. Probably 'B0' is group ID and '1' is a myid in wrong format.
        If it were only the example, I wouldn't say anything, but this seems to be the format used in the templates. Maybe these examples are actually for an
        extra XML topology scheme that gets translated to the documented values in MoM?


        full (but contradictory) documentation in the wiki:
        https://www.astron.nl/lofarwiki/doku.php?id=mom3:topology
        """

        topology = '.'.join([_f for _f in [header, groupid, myid, slice, function, sap, dptype] if _f])

        return topology

    def _mommify(self, activity, projectcode):
        """
        Turns a LOFAR activity to a MoM compatible version.
        The groupid is required for thetopology, measurements also require the activity_index.
        The projectcode is put on observations for some reason but is not available on the LofarSpec activity.
        Returns an item element containing nested MoM observation/pipeline
        """
        act = None
        for activitytype in ACTIVITY_TYPES:  # look for all possible activities
            act = activity.find(activitytype)
            if act is not None:

                # convert the very specific bits. Should happen before the mapping as attribute is moved!

                # We change the measurement type to one that fits the one we use in MoM.
                # The type name changed because it was not correct or is misleading.
                if "{http://www.w3.org/2001/XMLSchema-instance}type" in act.attrib:
                    t = act.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"]
                    if t.split(':')[1] == "SAPMeasurement":
                        newt = t.split(':')[0] + ':' + "BFMeasurement"
                        act.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] = newt

                        # infer missing elements that MoM requires  # todo: is that necessary?
                        nameelem = act.find('name')
                        if nameelem is not None and act.find('targetName') is None:
                            etree.SubElement(act, 'targetName').text = nameelem.text
                        if act.find('duration') is None:
                            etree.SubElement(act, 'duration').text = 'PT0S'  # todo: can we determine a reasonable value?

                # clock:
                for clock in act.findall('clock'):
                    atts = clock.attrib
                    mode = str(clock.text) + " " + str(atts.pop('units'))
                    atts['mode'] = mode
                    clock.text = None

                # convert status value to status-specific elements for MoM
                statuselem = activity.find('status')
                if statuselem is not None:
                    newstatuselem = etree.SubElement(act, "currentStatus")
                    momstatus = "{http://www.astron.nl/MoM2}"+statuselem.text+'Status'
                    etree.SubElement(newstatuselem, momstatus)

                # duplicate observation name and project code in attributes. At least the project code is probably
                # ignored and it's not clear why it is in there. But existing XML has it defined, so I stay consistent
                # here just to be sure..
                if activitytype == 'observation':
                        atts = self._find_or_create_subelement(act,
                                                               "{http://www.astron.nl/MoM2-Lofar}observationAttributes")
                        obsname = act.find('name')
                        if obsname is not None:
                            etree.SubElement(atts, 'name').text = obsname.text
                        if projectcode is not None:
                            etree.SubElement(atts, 'projectName').text = projectcode

                # stations:
                # Note: we place stuff in temporary locations first and handle the final placement with the mechanism
                # that is used for all other items as well (like misc encoding etc...). The reason is that the final
                # destination is e.g. dependent on what kind of activity this is, and I don't want to replicate that
                # logic.
                for selection in act.findall('stationSelectionSpecification/stationSelection'):
                        station_set = selection.find("stationSet")
                        if station_set.text == "Custom":
                            stations = selection.xpath("stations/station")
                            for station in stations:
                                stationname = station.find("name").text
                                # create new stationSelection element <- picked up by extraspec encoding
                                newselection = etree.SubElement(activity, 'stationSelection')
                                etree.SubElement(newselection, 'resourceGroup').text = stationname
                                etree.SubElement(newselection, 'min').text = '1'
                                # change formatting for mom
                                station.remove(station.find('name'))
                                station.attrib['name'] = (stationname)
                                station.text = None    # <-- will create self-closing tags, "" for extra closing tag
                            # but: leave it here <- will be placed on userSpecs later
                            # move to activity:
                            #activity.append(station_set)
                            #activity.append(selection.find('stations'))
                        else:
                            selection.find("minimumConstraint").tag = 'min'
                            selection.find("stationSet").tag = 'resourceGroup'
                            activity.append(selection)

                # Abstract types with xsi:type attributes are used for pipelines and measurements.
                # On the example mom xml I have, there is e.g. an element pipelineAttributes for all types,
                # But on the XSDs this IS type specific, e.g. averagingPipelineAttributes (Yaay!)
                # --> So, determine the specific type (if xsi:type present) and use the "camelCase+Type" name for the
                # element instead.:
                momtype = None
                momtype_cc = None
                try:
                    if "{http://www.w3.org/2001/XMLSchema-instance}type" in act.attrib:
                        t = act.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"]
                        momtype = t.split(':')[1]
                        momtype_cc = momtype[:2].lower() + momtype[2:]
                except ValueError as err:
                    logger.error("Could not determine a more specific MoM type from type attribute for the activity -> "
                                 + str(activitytype) + "  " + str(err))
                # momtype/_cc should now be present for pipelines/measurements but not observations

                # restructure elements according to mapping.:
                for src, dst in list(MOM_ACTIVITY_ATTRIBUTE_MAPPING.items()):
                    src_node = activity
                    for s in src.split('::'):
                        src_node = src_node.find(s)
                        if src_node is None:
                            break
                    if src_node is None:  # -> attribute not found
                        continue

                    dst_node = activity
                    dst_path = dst.split('::')[:-1]
                    dst_tag = dst.split('::')[-1]
                    for d in dst_path:
                        if d in ABSTRACT_MOM_ELEMENTS:  # replace abstract elements from Mapping by
                            d = d.replace(activitytype, "{http://www.astron.nl/MoM2-Lofar}" + str(momtype_cc))
                        if d is not "":
                            dst_node = self._find_or_create_subelement(dst_node, d)
                        else:
                            logger.warn("Ignoring empty string in mapping. -> " + str(dst))

                    src_node.getparent().remove(src_node)
                    if src_node.tag != dst_tag:
                        src_node.tag = dst_tag
                    dst_node.append(src_node)

                if activitytype in ACTIVITIES_WITH_MOM_EXTRASPECS:
                    # jsonify new specs that MoM does not know about and put them as json in misc element:
                    if momtype_cc is not None:  # -> not an obs
                        # use the specific type if present (pipelines/measurements)
                        atts = self._find_or_create_subelement(act, "{http://www.astron.nl/MoM2-Lofar}"
                                                          + str(momtype_cc) + "Attributes")
                        # todo: check if misc is in userspec for measurements, it does not seem true for pipelines...?!
                        # userspec = self._find_or_create_subelement(atts,'userSpecification', 0) # goes in beginning here
                        misc = self._find_or_create_subelement(atts, "misc", 0)
                    else:
                        atts = self._find_or_create_subelement(act, "{http://www.astron.nl/MoM2-Lofar}"
                                                          + str(activitytype) + "Attributes")
                        userspec = self._find_or_create_subelement(atts, 'userSpecification')
                        misc = self._find_or_create_subelement(userspec, "misc")
                    json = self._encode_mom_extraspecs(activity)
                    misc.text = json
                else:
                    self._encode_mom_extraspecs(activity)  # remove extraspec elements, but ignore the returned json

                # clean up / remove what MoM does not know
                self._remove_removable_elements(activity)

                # create MoM compatible element, namespace, and xsi:type
                item = etree.Element("item")
                momact = etree.SubElement(item, "{http://www.astron.nl/MoM2-Lofar}" + str(activitytype))
                if momtype:
                    # set an xsi:type according to the one on the lofar spec actvity
                    momact.attrib["{http://www.w3.org/2001/XMLSchema-instance}type"] = "lofar:" + str(momtype) + "Type"
                    # todo: better look up namespace identifier from nsmap.
                for child in act.getchildren():
                    # move stuff to new mom element
                    momact.append(child)

                return item, activitytype

        raise Exception("Cannot translate activity for MoM! -> " + str(ACTIVITY_TYPES)
                        + " not found in " + str(activity.getchildren()))

    def _isoduration_to_seconds(self, isoduration):
            comp = re.compile('P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+[.]?\d*)S)?)?')
            durdict = comp.match(isoduration).groupdict()

            td = datetime.timedelta(
                days=int(durdict['days'] or 0) +
                     (int(durdict['months'] or 0) * 30) +
                     (int(durdict['years'] or 0) * 365),
                hours=int(durdict['hours'] or 0),
                minutes=int(durdict['minutes'] or 0),
                seconds=int(durdict['seconds'] or 0))

            return td.total_seconds()


    def _encode_mom_extraspecs(self, activity):
        """
        encodes extra specs on an activity element as json
        return the json string
        """
        try:
            # move extraspec elements from activity to new element tree
            # we do not want to move the entire subtree to not harm any other existing elements, so we try to locate the
            # extraspec elements and if present, move them to a recreated tree structure that is then encoded in json
            extraspecelement = etree.Element("extraspec")  # temporarily holds data for misc
            for extraspec in MOM_ACTIVITY_EXTRASPECS:
                elements = extraspec.split("::")
                source = activity
                target = extraspecelement
                prevelement = None
                for element in elements:
                    # walk orginal tree to the latest child:
                    source = source.find(element)  # update reference
                    if source is None:
                        break
                    # on-the-fly create parents in new element tree, update reference:
                    if prevelement:
                        if target.find(prevelement) is None:
                            target = etree.SubElement(target, prevelement)
                        else:
                            target = target.find(prevelement)
                    prevelement = element
                if source is not None:
                    # move _all_ elements with that name, e.g. needed for stationSelection
                    sources = source.getparent().findall(source.tag)
                    for source in sources:
                        # move the child element to the parent element that was last created in the new tree:
                        source.getparent().remove(source)
                        target.append(source)

                        # find duration elements and convert iso to int.
                        # We are only covering elements and forst level subelements here, traverse further if needed
                        convertelems = []
                        convertelems.append(source)
                        convertelems.extend(source.getchildren())
                        for elem in convertelems:
                            if 'duration' in elem.tag.lower():
                                seconds = self._isoduration_to_seconds(elem.text)
                                elem.text = str(int(seconds)) # do not cast to int to get double here


            # Jsonify extraspec tree and add to misc element on the original activity element.
            json = self._jsonify(etree.tostring(extraspecelement))
            # json = dumps(loads(json)['extraspec'])  # remove parent element
            return json
        except Exception as err:
            logger.error("Error while encoding MoM extraspecs -> " + str(err))
            raise

    def _remove_removable_elements(self, momact):
        """
        removes elements from the mom specification that are not understood by MoM. Make sure to copy important info
        elsewhere (e.g. encode in misc) beforehand.
        """
        for elementpath in MOM_ACTIVITY_REMOVABLE_ELEMENTS:
            elementnames = elementpath.split("::")
            element = momact
            for elementname in elementnames:
                element = element.find(elementname)  # walk to leaf
                if element is None:
                    break
            if element is not None:
                element.getparent().remove(element)

    def translate_lofarspec_to_momspec(self, spec_xml):

        # Parse specification
        parser = etree.XMLParser(remove_blank_text=True)  # <-- prevent that prettyprinting breaks
        spectree = parse_xml_string_or_bytestring(spec_xml, parser=parser).getroot()

        nsmap = {"lofar": "http://www.astron.nl/MoM2-Lofar",
                 "mom2": "http://www.astron.nl/MoM2",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

        # create new document with correct namespace for Mom
        momspec = etree.Element("{http://www.astron.nl/MoM2-Lofar}project",
                                nsmap = nsmap)

        # translate general items
        projectcode = _parse_project_code(spectree)

        etree.SubElement(momspec, 'version').text = __version__

        temp = etree.SubElement(momspec, 'template')
        etree.SubElement(temp, 'description').text = 'Translated by ' + __name__ + ' version ' + __version__
        temp.attrib['author'] = __author__
        temp.attrib['changedBy'] = __changedBy__
        temp.attrib['version'] = __version__

        etree.SubElement(momspec, 'name').text = projectcode

        # create folder hierarchy
        activityparents, activity_topologygroup, activity_topologymyid = self._create_foldertree_in_momproject(spectree, momspec)

        # get input/output dataproducts
        indps, outdps, dptypes, dpclusterelems, dpproducers, dpusers = self._parse_entities(spectree)
        topologies = {}  # stores topologies for reference

        # add all activities and their related dataproducts to corresponding folder
        activities = spectree.findall('activity')
        for activity in activities:
            # determine destination folder for activity
            key = (activity.find('temporaryIdentifier').find('source').text,
                   activity.find('temporaryIdentifier').find('identifier').text)

            if key not in activityparents:
                logger.debug("No key " + str(key) + " in " + str(activityparents))
                raise Exception("No parent for key " + str(key))

            # Determine parent element (folder/obs) to hold this activity
            parent = activityparents[key]

            # Determine element index
            children = self._find_or_create_subelement(parent, "children")
            index = len(children.findall('item'))

            # restructure activity in MoM-comprehensible form
            item, activitytype = self._mommify(activity, projectcode)
            item.attrib["index"] = str(index)
            momact = item.getchildren()[0]

            # Add the mommified item to it's parent
            children.append(item)

            # Some activities, like observations, can also serve as containers for measurements.
            # While all the containers are set up separately, we have to now update the reference to point to the new
            # mommified parent activity, should it change at this step, so the child activity can be added to it.
            # -> We then refer to a {MoM-Lofar}observation we just added.
            # Note: This is probably super inefficient, but will have to do for now.
            for atype in ACTIVITY_TYPES:
                old_act = activity.find(atype)
                if old_act in list(activityparents.values()):
                    new_act = item.find("{http://www.astron.nl/MoM2-Lofar}" + str(atype))
                    if new_act is not None:
                        for k, v in list(activityparents.items()):
                            if v == old_act:
                                activityparents[k] = new_act
                    else:
                        raise Exception('Could not update mommified activity reference ->' + str(atype))

            # topology
            sap = None
            function = None
            myid = None
            if activitytype == "pipeline":
                function = 'P' + str(index)  # <-- assuming they are in same folder
                akey = key
                while akey in list(indps.keys()):  # find root observation
                    akey = dpproducers[indps[akey][0]]
                myid = activity_topologymyid[akey]
            elif activitytype == "observation":
                function = 'T'  # we ignore the different possible types here for simplicity, parse twinrelations to handle this properly
                myid = activity_topologymyid[key]
            elif activitytype == "measurement":
                function = 'T'  # we ignore the different possible types here for simplicity, parse twinrelations to handle this properly
                sap = "SAP" + str(index).zfill(3)  # <- assuming they are in same folder
                myid = activity_topologymyid[key]

            groupid = activity_topologygroup[key]
            topology = self._create_topology(
                groupid=groupid,
                myid=myid,
                function=function,
                sap=sap
            )

            tindex = 0  # where to insert
            act = momact
            if act.find(
                    'name') is not None and activitytype != 'pipeline':  # <- sequence is different for pipelines for some reason
                tindex = tindex + 1
            if act.find('description') is not None and activitytype != 'pipeline':
                tindex = tindex + 1
            self._find_or_create_subelement(act, "topology", tindex).text = topology
            topologies[key] = topology

            # Add Dataproducts to activity in MoM tree
            predecessors = []
            if key in list(indps.keys()):
                # The XSDs allow fully defining these with storageCluster etc, but MoM seems to expect an emty element with a single topology attribute
                # todo maybe we can share some code here with outdps
                indpkeys = indps[key]
                rdpelem = etree.SubElement(momact, "usedDataProducts")
                # todo: I think this should be actually populated after outdps were added for all activities. This currently relies on sequential occurence in XML
                dpindex = 0
                for indpkey in indpkeys:
                    dpitem = etree.SubElement(rdpelem, "item")
                    dpitem.attrib["index"] = str(dpindex)
                    dpindex = dpindex + 1
                    dptype = dptypes[indpkey]
                    dptype1 = dptype.split('_')[0]   # is/cs are both bf
                    dptype_cc = dptype1[:2].lower() + dptype1[2:]  # camelCase
                    indpelem = etree.SubElement(dpitem, "{http://www.astron.nl/MoM2-Lofar}" + dptype_cc)
                    indpelem.attrib["topology"] = topologies[indpkey]

                    # recursively determine predecessors of dataproduct and all dependencies:
                    def _get_predecessors(dpkey):
                        preds = []
                        preds.append(dpproducers[dpkey])
                        if dpproducers[dpkey] in list(indps.keys()):
                            for pdpkey in indps[dpproducers[dpkey]]:
                                preds.extend(_get_predecessors(pdpkey))
                        return preds

                    # append dataproduct's predecessors
                    predecessors.extend(_get_predecessors(indpkey))

            if key in list(outdps.keys()):
                outdpkeys = outdps[key]
                rdpelem = etree.SubElement(momact, "resultDataProducts")
                dpindex = 0
                for outdpkey in outdpkeys:
                    dpitem = etree.SubElement(rdpelem, "item")
                    dpitem.attrib["index"] = str(dpindex)
                    dpindex = dpindex + 1
                    dptype = dptypes[outdpkey]
                    dptype1 = dptype.split('_')[0]   # is/cs are both bf
                    dptype_cc = dptype1[:2].lower() + dptype1[2:] # camelCase
                    outdpelem = etree.SubElement(dpitem, "{http://www.astron.nl/MoM2-Lofar}"+dptype_cc)
                    dptopology = dptopologytypes[dptype]
                    topology = self._create_topology(
                        groupid=groupid,
                        myid=myid,
                        function=function,
                        sap=sap,
                        dptype="dps." + dptopology
                    )
                    name = topology
                    etree.SubElement(outdpelem, "name").text = name
                    etree.SubElement(outdpelem, "topology").text = topology
                    etree.SubElement(outdpelem, "status").text = "no_data"  # <-- todo: is this actually required?
                    outdpelem.append(dpclusterelems[outdpkey])
                    topologies[outdpkey] = topology

            if predecessors is not None and len(predecessors) > 0:
                pre_topologies = [topologies[predecessor] for predecessor in predecessors]
                # For some reason, the observation is referenced here, not for the measurement that produced the data.
                # Removing SAP identifier should result in observations topology, use of set removes duplicates:
                pre_topologies = list(set([pretop.split('.SAP')[0] for pretop in pre_topologies]))
                self._find_or_create_subelement(act, "predecessor_topology", tindex + 1).text = ','.join(pre_topologies)



    # create MoM Specification XML
        momspec_xml = etree.tostring(momspec, pretty_print=True, method='xml')

        return momspec_xml
