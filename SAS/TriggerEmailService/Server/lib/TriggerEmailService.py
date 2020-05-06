#!/usr/bin/env python3
#
# Copyright (C) 2017
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
import os
import smtplib
import logging

from lofar.sas.TriggerEmailService.Templates import ABORTED_TEMPLATE_BODY, ABORTED_TEMPLATE_SUBJECT
from lofar.sas.TriggerEmailService.Templates import ACCEPTED_TEMPLATE_BODY, ACCEPTED_TEMPLATE_SUBJECT
from lofar.sas.TriggerEmailService.Templates import FINISHED_TEMPLATE_BODY, FINISHED_TEMPLATE_SUBJECT
from lofar.sas.TriggerEmailService.Templates import REJECTED_TEMPLATE_BODY, REJECTED_TEMPLATE_SUBJECT
from lofar.sas.TriggerEmailService.Templates import RECEIVED_TEMPLATE_BODY, RECEIVED_TEMPLATE_SUBJECT

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import timedelta, datetime
import time
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler
from lofar.common.util import waitForInterrupt
from lofar.messaging.messagebus import BusListener, AbstractMessageHandler
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.TriggerEmailService.common.config import DEFAULT_TRIGGER_NOTIFICATION_SUBJECT
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lxml import etree
from io import BytesIO
from re import findall
import socket

logger = logging.getLogger(__name__)


def email(recipients, subject, body, attachment, attachment_name):
    if "LOFARENV" in os.environ:
        lofar_environment = os.environ['LOFARENV']

        if lofar_environment == "PRODUCTION":
            recipients.append("sos@astron.nl")
            recipients.append("observer@astron.nl")

    hostname = socket.gethostname()
    sender = "lofarsys@" + hostname
    commaspace = ', '

    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain'))
    msg["Subject"] = subject
    msg["From"] = "LOFAR Science Operations & Support <sos@astron.nl>"
    msg["To"] = commaspace.join(recipients)

    if attachment:
        txt = MIMEText(attachment)
        txt.add_header('Content-Disposition', "attachment; filename= %s" % attachment_name)
        msg.attach(txt)

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()


class MoMIdError(Exception):
    pass


class OTDBTriggerListener(OTDBBusListener):
    def __init__(self, momquery_rpc=MoMQueryRPC(), exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        """
        TriggerNotificationListener listens on the lofar trigger message bus and emails when trigger
         gets submitted.
        :param exchange: valid message exchange address
        :param broker: valid broker host (default: None, which means localhost)
        """
        super(OTDBTriggerListener, self).__init__(handler_type=OTDBTriggerHandler,
                                                  handler_kwargs={'momquery_rpc': momquery_rpc},
                                                  exchange=exchange, broker=broker)


class OTDBTriggerHandler(OTDBEventMessageHandler):
    def __init__(self, momquery_rpc=MoMQueryRPC()):
        super().__init__()

        self.mom_rpc_client = momquery_rpc

    def start_handling(self):
        self.mom_rpc_client.open()
        super(OTDBTriggerHandler, self).start_handling()

    def stop_handling(self):
        self.mom_rpc_client.close()
        super(OTDBTriggerHandler, self).stop_handling()

    def onObservationAborted(self, otdb_id, _):
        self.when_trigger_send_email(otdb_id, ABORTED_TEMPLATE_SUBJECT, ABORTED_TEMPLATE_BODY)

    def onObservationScheduled(self, otdb_id, _):
        self.when_trigger_send_email(otdb_id, ACCEPTED_TEMPLATE_SUBJECT, ACCEPTED_TEMPLATE_BODY)

    def onObservationFinished(self, otdb_id, _):
        self.when_trigger_send_email(otdb_id, FINISHED_TEMPLATE_SUBJECT, FINISHED_TEMPLATE_BODY)

    def onObservationConflict(self, otdb_id, _):
        self.when_trigger_send_email(otdb_id, REJECTED_TEMPLATE_SUBJECT, REJECTED_TEMPLATE_BODY)

    def onObservationError(self, otdb_id, _):
        self.when_trigger_send_email(otdb_id, REJECTED_TEMPLATE_SUBJECT, REJECTED_TEMPLATE_BODY)

    def when_trigger_send_email(self, otdb_id, template_subject, template_body):
        try:
            mom_id, trigger_id = self._get_mom_and_trigger_id(otdb_id)

            if trigger_id:
                self._send_email(otdb_id, mom_id, trigger_id, template_subject, template_body)

        except MoMIdError:
            logger.error("Could not retrieve a mom_id for otdb_id: %s", otdb_id)

    def _get_mom_and_trigger_id(self, otdb_id):
        mom_id = self._try_get_mom_id(otdb_id)

        if not mom_id:
            raise MoMIdError

        trigger_id = self.mom_rpc_client.get_trigger_id(mom_id)['trigger_id']

        return mom_id, trigger_id

    def _try_get_mom_id(self, otdb_id):
        # sometimes we are too fast for MoM so we need to retry
        mom_id = None
        for _ in range(10):
            mom_id = self.mom_rpc_client.getMoMIdsForOTDBIds(otdb_id)[otdb_id]
            if mom_id:
                break
            time.sleep(3)
        return mom_id

    def _send_email(self, otdb_id, mom_id, trigger_id, template_subject, template_body):
        logger.info("Emailing otdb_id: %s, mom_id: %s, trigger_id: %s, template_subject: %s, template_body: %s",
                    otdb_id, mom_id, trigger_id, template_subject, template_body)

        subject, body = self._fill_template(otdb_id, mom_id, trigger_id, template_subject, template_body)
        recipients = self._get_recipients(mom_id)

        email(recipients, subject, body, None, "")

    def _fill_template(self, otdb_id, mom_id, trigger_id, template_subject, template_body):
        project = self.mom_rpc_client.getObjectDetails(mom_id)[mom_id]

        data = {
            "PROJECTNAME": project["project_name"], "TRIGGERID": trigger_id, "OBSSASID": otdb_id, "OBSMOMID": mom_id,
            "MOMLINK": "https://lofar.astron.nl/mom3/user/project/setUpMom2ObjectDetails.do?view="
                       "generalinfo&mom2ObjectId=%s" % project["object_mom2objectid"]
        }

        subject = template_subject % data
        body = template_body % data

        return subject, body

    def _get_recipients(self, mom_id):
        recipients = []

        project = self.mom_rpc_client.getObjectDetails(mom_id)[mom_id]

        emails = self.mom_rpc_client.get_project_details(project['project_mom2id'])
        for k, v in list(emails.items()):
            recipients.append(v)

        return recipients


class TriggerNotificationListener(BusListener):
    def __init__(self, momquery_rpc=MoMQueryRPC(), busname=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        """
        TriggerNotificationListener listens on the lofar trigger message bus and emails when trigger
        gets submitted.
        :param address: valid Qpid address (default: lofar.otdb.status)
        :param broker: valid Qpid broker host (default: None, which means localhost)
        """
        super(TriggerNotificationListener, self).__init__(
            handler_type=TriggerNotificationHandler, handler_kwargs={'momquery_rpc': momquery_rpc},
            exchange=busname, routing_key=DEFAULT_TRIGGER_NOTIFICATION_SUBJECT, broker=broker)


class TriggerNotificationHandler(AbstractMessageHandler):
    def __init__(self, momquery_rpc=MoMQueryRPC()):
        """
        TriggerNotificationHandler listens on the lofar trigger message bus and emails when trigger
        gets submitted.
        """
        super(TriggerNotificationHandler, self).__init__()
        self.mom_rpc_client = momquery_rpc

    def handle_message(self, msg):
        trigger_id = msg.content['trigger_id']
        project_name = msg.content['project']
        trigger_xml = msg.content['metadata']
        start_time, stop_time = self._get_observation_start_stop_times(trigger_xml)

        mom_id = self._get_mom_id(project_name)

        if mom_id:
            subject, body = self._fill_template(trigger_id, project_name, start_time, stop_time,
                                                RECEIVED_TEMPLATE_SUBJECT, RECEIVED_TEMPLATE_BODY)
            recipients = self._get_recipients(mom_id)

            email(recipients, subject, body, trigger_xml, "trigger.xml")
        else:
            logger.error("Trigger got entered for a non existing project: %s", project_name)

    def _get_mom_id(self, project_name):
        # todo add function to momqueryserivce for it (get mom2id for project name)
        mom_id = None

        projects = self.mom_rpc_client.getProjects()
        for project in projects:
            if project["name"] == project_name:
                mom_id = project["mom2id"]

        return mom_id

    def _get_recipients(self, mom_id):

        recipients = []

        emails = self.mom_rpc_client.get_project_details(mom_id)

        for k, v in list(emails.items()):
            recipients.append(v)

        return recipients

    def _get_observation_start_stop_times(self, trigger_xml):
        # for now we work with duration to get stop time
        doc = etree.parse(BytesIO(trigger_xml.encode('UTF-8')))

        start_times = doc.getroot().findall('specification/activity/observation/timeWindowSpecification/startTime')

        if start_times: # Not dwelling
            start_time = datetime.strptime(start_times[0].text, '%Y-%m-%dT%H:%M:%S')

            durations = doc.getroot().findall(
                'specification/activity/observation/timeWindowSpecification/duration/duration')

            duration = durations[0].text

            duration_seconds = self._iso8601_duration_as_seconds(duration)

            stop_time = start_time + timedelta(seconds=duration_seconds)

            return start_time, stop_time
        else: # Dwelling
            min_start_times = doc.getroot().findall('specification/activity/observation/timeWindowSpecification/minStartTime')

            min_start_time = datetime.strptime(min_start_times[0].text, '%Y-%m-%dT%H:%M:%S')

            max_end_times = doc.getroot().findall('specification/activity/observation/timeWindowSpecification/maxEndTime')

            max_end_time = datetime.strptime(max_end_times[0].text, '%Y-%m-%dT%H:%M:%S')

            return min_start_time, max_end_time


    def start_handling(self, **kwargs):
        self.mom_rpc_client.open()
        super(TriggerNotificationHandler, self).start_handling()

    def stop_handling(self):
        self.mom_rpc_client.close()
        super(TriggerNotificationHandler, self).stop_handling()

    def _fill_template(self, trigger_id, project_name, start_time, stop_time, template_subject, template_body):
        data = {
            "PROJECTNAME": project_name, "TRIGGERID": trigger_id, "STARTTIME": start_time, "ENDTIME": stop_time
        }

        subject = template_subject % data
        body = template_body % data

        return subject, body

    def _iso8601_duration_as_seconds(self, duration):
        if duration[0] != 'P':
            raise ValueError('Not an ISO 8601 Duration string')
        seconds = 0
        for i, item in enumerate(duration.split('T')):
            for number, unit in findall('(?P<number>\d+)(?P<period>S|M|H|D|W|Y)', item):
                number = int(number)
                this = 0
                if unit == 'Y':
                    this = number * 31557600  # 365.25
                elif unit == 'W':
                    this = number * 604800
                elif unit == 'D':
                    this = number * 86400
                elif unit == 'H':
                    this = number * 3600
                elif unit == 'M':
                    # ambiguity ellivated with index i
                    if i == 0:
                        this = number * 2678400  # assume 30 days
                    else:
                        this = number * 60
                elif unit == 'S':
                    this = number
                seconds += this
        return seconds


def main():
    with OTDBTriggerListener():
        with TriggerNotificationListener():
            waitForInterrupt()


if __name__ == '__main__':
    main()
