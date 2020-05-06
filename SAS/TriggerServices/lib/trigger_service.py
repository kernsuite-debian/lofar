#!/usr/bin/env python3

# trigger_handler.py
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


from io import BytesIO
from lxml import etree
from datetime import datetime, timedelta

from lofar.messaging import ServiceMessageHandler, RPCService, DEFAULT_BROKER, DEFAULT_BUSNAME, EventMessage, ToBus
from lofar.common.util import waitForInterrupt
from lofar.common.lcu_utils import stationname2hostname, hostname2stationname

from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.specificationservices.specification_service_rpc import SpecificationRPC
from lofar.specificationservices.validation_service_rpc import ValidationRPC
from lofar.specificationservices.translation_service_rpc import TranslationRPC

from lofar.mac.tbb.tbb_freeze import freeze_tbb

from .task_info_cache import TaskInfoCache
from .config import *

from lofar.sas.TriggerEmailService.common.config import DEFAULT_TRIGGER_NOTIFICATION_SUBJECT

from lofar.triggerservices.voevent_listener import VOEventListenerInterface
import lofar.triggerservices.voevent_decider
from lofar.mac.tbb.tbb_util import parse_parset_from_voevent
from lofar.mac.tbbservice.client.tbbservice_rpc import TBBRPC
from lofar.mac.tbb.tbb_set_storage import create_mapping


import dateutil.parser
import time


import logging
logger = logging.getLogger(__name__)

momqueryrpc = MoMQueryRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)
validationrpc = ValidationRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)
specificationrpc = SpecificationRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)
translationrpc = TranslationRPC.create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER)

def _auth_allows_triggers(project):
    response = momqueryrpc.allows_triggers(project)
    return response['allows']


def _quota_allows_triggers(project):
    response = momqueryrpc.get_trigger_quota(project)
    if response['used_triggers'] < response['allocated_triggers']:
        return True
    else:
        return False


def _validate_trigger(trigger_xml):
    response = validationrpc.validate_trigger_specification(trigger_xml)
    if not response["valid"]:
        msg = "Got invalid trigger XML"
        logger.error(msg)
        raise Exception(msg+" -> " + response["error"])


def _add_trigger(username, hostname, projectname, metadata):
    logger.info("Adding trigger")
    response = momqueryrpc.add_trigger(username,hostname ,projectname,metadata)
    trigger_id = response['row_id']
    _send_notification(username,  hostname, projectname, trigger_id, metadata)
    return trigger_id


def _get_project_priority(project):
    logger.info("Getting project priority for project"+ str(project))
    response = momqueryrpc.get_project_priority(project)
    prio = response['priority']
    #prio = 1
    return prio


def _add_specification(user, lofar_xml):
    logger.info("Sending spec to specification service")
    specificationrpc.add_specification(user, lofar_xml)


def _translate_trigger_to_specification(trigger_xml, trigger_id, job_priority):
    logger.info("translating trigger to spec")
    response = translationrpc.trigger_to_specification(trigger_xml, trigger_id, job_priority)
    spec = response.get("specification")
    return spec


def _send_notification(user, host, project, trigger_id, metadata):
    try:
        content={ "user": user,
                  "host": host,
                  "project": project,
                  "trigger_id": trigger_id,
                  "metadata": metadata
        }
        msg = EventMessage(subject=DEFAULT_TRIGGER_NOTIFICATION_SUBJECT, content=content)
        with ToBus(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER) as notification_bus:
            notification_bus.send(msg)
    except Exception as err:
        logger.error("Could not send notification ->" + str(err))


def _parse_project_id(trigger_xml):
    doc = etree.parse(BytesIO(trigger_xml.encode('utf-8')))
    ref = doc.find("projectReference")
    #return ref.find("identifier").find("identifier").text
    return ref.find("ProjectCode").text


class TriggerServiceMessageHandler(ServiceMessageHandler):

    def __init__(self):
        # handle QPID messages
        super(TriggerServiceMessageHandler, self).__init__()

        self.service2MethodMap = {
            'handle_trigger': self.handle_trigger,
            }

    def start_handling(self):
        momqueryrpc.open()
        validationrpc.open()
        specificationrpc.open()
        translationrpc.open()
        super().start_handling()


    def stop_handling(self):
        momqueryrpc.close()
        validationrpc.close()
        specificationrpc.close()
        translationrpc.close()
        super().stop_handling()

    def handle_trigger(self, user, host, trigger_xml):
        logger.info("Handling trigger from user -> "+str(user))
        trigger_id = None

        _validate_trigger(trigger_xml)
        logger.info("Trigger XML is valid")

        project = _parse_project_id(trigger_xml)
        logger.debug('project is -> ' + str(project))
        priority = _get_project_priority(project)
        logger.debug('project priority is ->' + str(priority))

        if _auth_allows_triggers(project):
            logger.info("trigger is authorized")
            if _quota_allows_triggers(project):
                logger.info("trigger quota allows adding to trigger and specification")
                trigger_id = _add_trigger(str(user), host, project, trigger_xml) # todo: How to determine hostname from Qpid message?
                logger.debug("Trigger was assigned id -> "+str(trigger_id))
                lofar_xml = _translate_trigger_to_specification(trigger_xml, trigger_id, priority)
                logger.debug("Lofar specification is valid!")
                _add_specification(user, lofar_xml)
            else:
                msg = "Trigger quota exceeded!"
                logger.error(msg)
                raise Exception(msg)
        else:
            msg = "Trigger authorization failed!"
            logger.error(msg)
            raise Exception(msg)

        logger.info("trigger handling done. -> "+str(trigger_id))
        return {"trigger-id": str(trigger_id)} # todo: Design document asks to return the specification status. Does that make sense and is it obtainable at all?

def _get_current_tbbtype():
    """
    :return: string with current tbb operation mode
    """
    # todo!
    # No idea how to do that without actually asking anyone?
    # Have a thread permanently requesting updates on these things to keep the current state updated?

    # This is probably a must-have for the initial implementation, so not making any assumptions here.
    # I think Sander wants to be able to poll for this, so we should add a function to the tbb service, and then call
    # that service from here, I guess.
    # 20190111 JS: add the polling to the TaskInfoCache for fast lookup
    return 'subband'


# todo: move this somewhere is can be commonly used
def translate_arrival_time_to_frequency(reference_time, reference_frequency, dm, target_frequency=200):
    """
    For a signal with specified dm, which has arrival time original_time at original_frequency, determine the arrival
    time at target_frequency.

    :param original_time: timestamp in seconds since epoch as float
    :param original_frequency: frequency in Mhz as integer
    :param target_frequency: frequency in Mhz as integer
    :param dm: dispersion measure in pc/cm^3 as integer
    :return: arrival time of the original signal at target frequency as float
    """
    dm_constant = 4.148808e3  # MHz^2 pc^-1 cm^3 sec
    delay = dm * dm_constant * (1.0/target_frequency**2 - 1.0/reference_frequency**2) # sec
    target_time = reference_time + delay
    logger.info('Delay is %s seconds. DM is %s.' % (delay, dm))
    logger.info('Arrival time @ %6s Mhz: %11.2f | %s' % (reference_frequency, reference_time, time.ctime(reference_time)))
    logger.info('Arrival time @ %6s Mhz: %11.2f | %s' % (target_frequency, target_time, time.ctime(target_time)))
    return target_time


class ALERTHandler(VOEventListenerInterface):
    """
    This class implements the VOEventListenerInterface in order to receive VO events for the ALERT project.
    """
    def __init__(self, broker_host='127.0.0.1', broker_port=8099, filter_for=None):
        self._cache = TaskInfoCache()
        super(ALERTHandler, self).__init__(broker_host, broker_port, filter_for)

    def start_listening(self, blocking=False):
        self._cache.start_handling()
        super(ALERTHandler, self).start_listening(blocking=blocking)

    def stop_listening(self):
        self._cache.stop_handling()
        super(ALERTHandler, self).stop_listening()

    def handle_event(self, voevent_xml, voevent_etree):
        if voevent_xml is None or voevent_etree is None:
            logger.warning("skipping empty vo_event")
            return

        identifier = voevent_etree.attrib['ivorn']
        logger.info('Handling new ALERT event %s...' % identifier)
        try:
            logger.info('%s' % voevent_xml)

            # check if trigger is allowed to be accepted(marshal permissions etc,)
            # Note: So we first have to interpret the event at this stage already just to get the actual time when the
            # freeze should happen so we can check if the event should be accepted...?
            # Meh. I'd prefer this to happen in the recipe, so that we can separate the marshaling from the handling.
            # Anyway, here we go:
            parset = parse_parset_from_voevent(voevent_xml)
            dm = float(parset['Observation.TBB.TBBsetting.triggerDispersionMeasure'])
            triggerid = parset['Observation.TBB.TBBsetting.triggerId']
            reference_frequency = float(parset['Observation.TBB.TBBsetting.referenceFrequency'])
            timestr = parset['Observation.TBB.TBBsetting.time']
            reference_time = time.mktime(dateutil.parser.parse(timestr).timetuple())  # convert time string to seconds
            centertime = translate_arrival_time_to_frequency(reference_time, reference_frequency, dm, target_frequency=200)
            duration = DEFAULT_TBB_DUMP_DURATION  # tbb can hold this many seconds
            starttime = centertime - duration / 2.0
            stoptime = centertime + duration / 2.0

            # convert float starttime to second and nanosecond component
            # todo: Do we need higher precision up to here? Investigate!
            #    ...We agreed to try this out first, but it could be problematic fr use cases with extremely short recordings.
            stoptime_sec, stoptime_nsec = ("%.9f" % stoptime).split(".")
            stoptime_sec = int(stoptime_sec)
            stoptime_nsec = int(stoptime_nsec)

            if self._tbb_trigger_is_acceptable(stoptime):
                logger.info('ALERT event %s passed system pre-flight checks' % triggerid)

                # check if trigger is acceptable for PI
                decider = lofar.triggerservices.voevent_decider.ALERTDecider()
                if decider.is_acceptable(voevent_etree):
                    logger.info('ALERT event %s passed science pre-flight checks' % triggerid)
                    # _send_notification('ALERT Broker', ALERT_BROKER_HOST, self.project, triggerid, voevent_xml)  # todo: do we want that? do we want it on same bus?
                    logger.info('ALERT event %s is accepted. Initiating TBB dump: starttime %s, duration %ssec, dm %s' % (triggerid, starttime, duration, dm))
                    available_stations = self._determine_station_lists()['available']
                    lcus = [stationname2hostname(station) for station in available_stations]
                    lcu_str = ','.join(lcus)

                    # do a fast direct freeze call here, so the boards still contain data for this event.
                    # if we freeze via rpc/service calls, that takes time, so we might loose precious data from the buffers.
                    freeze_tbb(lcu_str, dm, stoptime_sec, stoptime_nsec)

                    # initiate the dumping via an rpc call to the tbbservice which takes care of all bookkeeping.
                    with TBBRPC.create() as rpc:
                        rpc.do_tbb_subband_dump(starttime, duration, dm, DEFAULT_TBB_PROJECT, triggerid, available_stations, DEFAULT_TBB_SUBBANDS, DEFAULT_TBB_BOARDS, DEFAULT_TBB_CEP_NODES, voevent_xml, stoptime=stoptime)
                else:
                    raise Exception('ALERT event %s rejected by science pre-flight checks!' % triggerid)
            else:
                raise Exception('ALERT event %s rejected by system pre-flight checks!' % triggerid)

        except Exception as ex:
            logger.exception("An error occurred while handling ALERT event %s: %s" % (identifier, ex))
            raise

        logger.info('...done handling ALERT event %s...' % identifier)

    def _tbb_trigger_is_acceptable(self, stoptime):
        """
        Perform permission and system checks to determine whether we can actually perform a triggered TBB dump for the given project.

        :param stoptime: the stoptime in seconds since Epoch as float
        :return: True if acceptable, else False
        """
        try:
            project_info = self._cache.get_project_info(DEFAULT_TBB_PROJECT)
        except KeyError:
            logger.warning("Unknown project '%s'. TBB Trigger is not authorized.", DEFAULT_TBB_PROJECT)
            return False

        # Is the project allowed to trigger?
        if project_info['allow_triggers']:
            logger.info('TBB Trigger is authorized for project %s', DEFAULT_TBB_PROJECT)
        else:
            logger.warning('TBB Trigger is not authorized for project %s', DEFAULT_TBB_PROJECT)
            return False

        # Are we allowed another trigger from the project's quota?
        # TODO: update num_used_triggers in mom when the TBB alert trigger is done
        if project_info['num_used_triggers'] < project_info['num_allowed_triggers']:
            logger.info('Trigger quota allows TBB freeze/dump for project %s: num_used_triggers=%s num_allowed_triggers=%s',
                        DEFAULT_TBB_PROJECT, project_info['num_used_triggers'], project_info['num_allowed_triggers'])
        else:
            logger.warning('Trigger quota exceeded for project %s: num_used_triggers=%s num_allowed_triggers=%s',
                           DEFAULT_TBB_PROJECT, project_info['num_used_triggers'], project_info['num_allowed_triggers'])
            return False

        # Correct TBB mode?
        if _get_current_tbbtype() != DEFAULT_TBB_ALERT_MODE:
            logger.warning('TBB is currently in mode %s. Needed is mode %s.', _get_current_tbbtype(), DEFAULT_TBB_ALERT_MODE)
            return False
        else:
            logger.info('TBB is in correct operational mode: %s' % DEFAULT_TBB_ALERT_MODE)

        # Any running observations?
        #TODO: make stoptime a datetime instance everywhere  JK: We may have to generally switch to sec, nsec int tuple instead, because of representation error!
        active_tasks = self._cache.get_active_tasks(datetime(1970, 1, 1) + timedelta(seconds=stoptime), 'observation')
        if active_tasks:
            otdb_ids = sorted([t.radb_task['otdb_id'] for t in active_tasks])
            logger.info('Observation(s) %s is/are running at time %s', otdb_ids, stoptime)
        else:
            logger.warning('No observations running at %s, so TBB\'s are not recording', stoptime)
            return False

        station_lists = self._determine_station_lists()

        if len(station_lists['available']) > 0:
            logger.info('Enough TBB stations available: %s', station_lists['available'])
        else:
            logger.warning('No TBB stations available. requested=%s active=%s', station_lists['requested'], station_lists['active'])
            return False

        # all prerequisites are met.
        return True

    def _determine_station_lists(self):
        # TODO: implement and use a get_stations_at_timestamp(stoptime) instead
        # ...also, the use hostname2stationname to upper the case here is quite hacky...
        active_stations = [hostname2stationname(x) for x in self._cache.get_stations()]
        requested_stations = [hostname2stationname(x) for x in DEFAULT_TBB_STATIONS]
        active_tbb_stations = list(set(requested_stations) & set(active_stations))

        return {'requested': requested_stations, 'active': active_stations, 'available': active_tbb_stations}


def main():

    with RPCService(service_name=TRIGGER_SERVICENAME,
                    handler_type=TriggerServiceMessageHandler,
                    exchange=DEFAULT_BUSNAME,
                    num_threads=4):
        # next to RT events, also (independently) handle vo events
        with ALERTHandler(broker_host=ALERT_BROKER_HOST, broker_port=ALERT_BROKER_PORT, filter_for=ALERT_PACKET_TYPE_FILTER) as alert_handler:
            waitForInterrupt()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    main()
