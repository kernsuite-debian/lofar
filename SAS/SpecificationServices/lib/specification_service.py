#!/usr/bin/env python3

# specification_service.py
#
# Copyright (C) 2015
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

from collections import OrderedDict
from io import BytesIO

from lofar.common.util import waitForInterrupt
# TODO: mom.importxml uses old messaging interface
from lofar.messagebus.message import MessageContent
from lofar.messaging import RPCService, DEFAULT_BUSNAME, DEFAULT_BROKER, ServiceMessageHandler
from lofar.messagebus.messagebus import ToBus as ToBusOld
from lofar.messagebus.message import MessageContent as MessageContentOld
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.specificationservices.translation_service_rpc import TranslationRPC
from lofar.specificationservices.validation_service_rpc import ValidationRPC
from lofar.common.xmlparse import parse_xml_string_or_bytestring
from .config import SPECIFICATION_SERVICENAME, MOMIMPORTXML_BUSNAME, MOMIMPORTXML_BROKER

permitted_activities = ["observation", "pipeline", "measurement"]
permitted_statuses = ["opened", "approved"]

from lofar.messagebus import messagebus
messagebus.IGNORE_LOFARENV = True # Needed to prevent test prepending to mom.importxml queue name

import logging

logger = logging.getLogger(__name__)


def make_key(element):
    source = element.find("source").text
    identifier = element.find("identifier").text
    return (source, identifier)


def _parse_relation_tree(spec):
    """
    returns lookup dictionaries for folder relations and names.
    """
    # note: this is shared functionality with translation service.
    # todo: Expose as service method? This requires conversion to xml again...

    containers = spec.findall('container')
    folder_activity = [(x.find("parent"), x.find("child")) for x in spec.findall("relation") if
                       x.find("type").text == "folder-activity"]
    folder_folder = [(x.find("parent"), x.find("child")) for x in spec.findall("relation") if
                     x.find("type").text == "folder-folder"]

    # Instead of normal dict we use an OrderedDict in order to be able to influence the output element order (through
    # input order of folder-activity relations). The generator in the constructor creates a sorted list, so this is
    # rather similar to a standard dict comprehension.
    foldernames = OrderedDict((make_key(container.find("temporaryIdentifier")),
                               container.find('folder').find('name').text) for container in
                              containers)
    parentfolders = OrderedDict(
        (make_key(folder_id), make_key(parentfolder_id)) for (parentfolder_id, folder_id) in
        folder_folder)
    activityfolders = OrderedDict(
        (make_key(activity_id), make_key(folder_id)) for (folder_id, activity_id) in
        folder_activity)

    # check completeness
    for folder in list(activityfolders.values()):
        while folder is not None:
            if folder not in list(foldernames.keys()):
                raise Exception("Reference to missing container? (%s)" % (folder,))
            if folder not in list(parentfolders.keys()):
                break
            else:
                folder = parentfolders[folder]

    return activityfolders, parentfolders, foldernames


def _parse_project_code(spec):
    projectref = spec.find('projectReference')
    if projectref is not None:
        projectcode = projectref.find('ProjectCode')
        if projectcode is not None:
            return projectcode.text
    raise Exception('No project code found!')


def _parse_activity_paths(spec):
    """
    Parses relations on a lofar spec elementtree and returns a dict to lookup the path to the containing folder by
    a given activity identifier. Paths are slash separated with project identifier as root.
    """

    project = _parse_project_code(spec)
    paths = {}

    activityfolders, parentfolders, foldernames = _parse_relation_tree(spec)

    for activikey in list(activityfolders.keys()):
        folder = activityfolders[activikey]
        path = ""
        while folder is not None:
            if folder in list(foldernames.keys()):
                path = foldernames[folder] + "/" + path
            else:
                raise Exception("No folder name for key: " + str(folder))
            if folder in list(parentfolders.keys()):
                folder = parentfolders[folder]
            else:
                break
        path = "/" + project + "/" + path
        paths[activikey] = path

    for key in list(paths.keys()):
        logger.debug("Activity path -> %s --> %s", key, paths[key])
    return paths


class SpecificationHandler(ServiceMessageHandler):

    def __init__(self, **kwargs):
        super(SpecificationHandler, self).__init__()
        self.momqueryrpc = MoMQueryRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)
        self.validationrpc = ValidationRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)
        self.specificationtranslationrpc = TranslationRPC.create(exchange=DEFAULT_BUSNAME,
                                                                 broker=DEFAULT_BROKER)

    def add_specification(self, user, lofar_xml):
        logger.info("got specification from user %s", user)
        logger.debug("LOFAR-XML: %s", lofar_xml)

        self._validate_lofarspec(lofar_xml)
        logger.info("lofar xml validates!")

        self._check_specification(user, lofar_xml)
        logger.info("lofar xml check successful!")

        mom_xml = self._lofarxml_to_momxml(lofar_xml)
        self._validate_momspec(mom_xml)
        logger.info("mom xml validates!")

        self._add_spec_to_mom(mom_xml)
        logger.info("Fired and forgot to mom.importXML")

    def get_specification(self, user, id):
        logger.info("getting spec of id %s", id)
        with self.momqueryrpc:
            response = self.momqueryrpc.get_trigger_spec(user, id)
        return response

    def _check_specification(self, user, lofar_xml):
        """
        Performs some checks to make sure the specification meets some criteria before we accespt it.
        E.g. activities have to be in new folders
        """

        doc = parse_xml_string_or_bytestring(lofar_xml)
        spec = doc.getroot()

        if spec.tag != "{http://www.astron.nl/LofarSpecification}specification":
            raise Exception("Unexpected root element: ", spec.tag)

        activity_paths = _parse_activity_paths(spec)
        for path in list(activity_paths.values()):
            if self._folderExists(path):
                raise Exception("Innermost folder already exists: " + path)

        project = _parse_project_code(spec)
        if not self._isActive(project):
            raise Exception("Project is not active: " + str(project))

        activities = spec.findall('activity')
        for activity in activities:
            key = (activity.find("temporaryIdentifier").find("source").text,
                   activity.find("temporaryIdentifier").find("identifier").text)
            if not key in list(activity_paths.keys()):
                # allow measurements, which are activities, but not contained in folders by definition!
                # todo: check, is this what we want? Or do we have to do attional checks,
                # todo: e.g. that the obs-measurement relation and the parent obs exists?
                if not activity.find("measurement") is not None:
                    raise Exception("Specified action has to be in folder: " + str(key))
            jobtype = None
            for action in permitted_activities:
                if activity.find(action) is not None:
                    jobtype = action
                    break
                logger.warning("!!! %s not found...", action)
            if jobtype is None:
                raise Exception("Specified activity is not permitted: " + str(key) + " -> " + str(
                    permitted_activities)
                                + " not found in " + str(activity.getchildren()))
            status = activity.find("status")
            if status is None:
                raise Exception("Activity has no status: " + str(key))
            if status.text not in permitted_statuses:
                raise Exception(
                    "Specified activity is not going to permitted status: " + str(key) + " -> '"
                    + str(status.text) + "' not in " + str(permitted_statuses))

            # measurements require observation permissions
            if jobtype == "measurement":
                jobtype = "observation"

            self._authenticateAction(str(user), str(project), str(jobtype), str(status.text))

    def _isActive(self, project):
        logger.debug("Checking if project is active: %s", project)
        with self.momqueryrpc:
            response = self.momqueryrpc.isProjectActive(project)  # todo mock this for testing
            return response['active']

    def _folderExists(self, path):
        logger.debug("Checking if path exists -> %s", path)
        with self.momqueryrpc:
            response = self.momqueryrpc.folderExists(path)  # todo mock this for testing
            return response["exists"]

    def _authenticateAction(self, user, project, jobtype, state):
        logger.debug(
            "Authenticate action -> %s, %s, %s, %s", user, project, jobtype, state)
        with self.momqueryrpc:
            response = self.momqueryrpc.authorized_add_with_status(user, project, jobtype,
                                                                   state)  # todo mock this for testing
            return response['authorized']

    def _validate_lofarspec(self, lofar_xml):
        with self.validationrpc:
            response = self.validationrpc.validate_specification(lofar_xml)
            if not response["valid"]:
                raise Exception("Invalid specification: %s", response["error"])

    def _validate_momspec(self, mom_xml):
        with self.validationrpc:
            response = self.validationrpc.validate_mom_specification(mom_xml)
            if not response["valid"]:
                raise Exception("Invalid MoM specification: %s" % response["error"])

    def _add_spec_to_mom(self, mom_xml):
        logger.info("about to send mom_xml: %s", mom_xml)

        # Construct message payload using old-style (MessageBus) message format
        msg = MessageContentOld()
        msg.protocol = "mom.importxml"
        msg.from_ = "specification_service"
        msg.summary = "Translated LOFAR specifications"
        msg.momid = -1
        msg.sasid = -1

        # prepare payload in xml to have a %s which can be filled in with plain xml in the qmsg below...
        # MoM needs enters around the payload to avoid "Content not allowed in prolog" error
        msg.payload = "\n%s\n"

        # convert to qpid message (which is a proton message nowadays)
        qmsg = msg.qpidMsg()
        # and inject the mom_xml in the message xml
        qmsg.body = qmsg.body % (mom_xml, )

        with ToBusOld(queue=MOMIMPORTXML_BUSNAME,
                      broker=MOMIMPORTXML_BROKER) as momimportxml_bus:
            momimportxml_bus.send(qmsg)

            logger.debug("Send specs to MOM: %s", mom_xml)

    def _lofarxml_to_momxml(self, lofarxml):
        logger.debug("Translating LOFAR spec to MoM spec")
        with self.specificationtranslationrpc:
            response = self.specificationtranslationrpc.specification_to_momspecification(lofarxml)
            return response["mom-specification"]


def create_service(busname=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
    return RPCService(SPECIFICATION_SERVICENAME,
                      SpecificationHandler,
                      exchange=busname,
                      broker=broker)


def main():
    with create_service():
        waitForInterrupt()
