#!/usr/bin/env python3

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
#

from lofar.lta.ingest.client.ingestbuslistener import IngestEventMessageHandler, IngestEventMesssageBusListener
from lofar.lta.ingest.common.job import *
from lofar.messaging.config import DEFAULT_BUSNAME, DEFAULT_BROKER
from lofar.lta.ingest.common.config import INGEST_NOTIFICATION_PREFIX
from lofar.lta.ingest.server.config import DEFAULT_INGEST_SERVICENAME, DEFAULT_INGEST_INCOMING_JOB_SUBJECT, DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT
from lofar.lta.ingest.server.config import JOBS_DIR, MAX_NR_OF_RETRIES, FINISHED_NOTIFICATION_MAILING_LIST, FINISHED_NOTIFICATION_BCC_MAILING_LIST, DEFAULT_JOB_PRIORITY
from lofar.messaging import LofarMessage, CommandMessage, EventMessage, ToBus, RPCService, ServiceMessageHandler, AbstractMessageHandler, BusListener, adaptNameToEnvironment
from lofar.messaging.messagebus import nr_of_messages_in_queue
from lofar.common.util import humanreadablesize
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

import os
import os.path
import fnmatch
import shutil
import time
from random import random
from threading import RLock
from datetime import datetime, timedelta
from functools import cmp_to_key

import logging
from functools import reduce

logger = logging.getLogger()


class IngestJobManager:
    def __init__(self, exchange=DEFAULT_BUSNAME, jobs_dir=JOBS_DIR, max_num_retries=MAX_NR_OF_RETRIES, broker=DEFAULT_BROKER):
        self.__jobs_dir = jobs_dir
        self.__max_num_retries = max_num_retries
        self.__job_admin_dicts = {}
        self.__lock = RLock()
        self.__running = False

        self._tobus = ToBus(exchange=exchange, broker=broker)

        self.__running_jobs_log_timestamp = datetime.utcnow()
        self.__last_putStalledJobsBackToToDo_timestamp = datetime.utcnow()

    def quit(self):
        self.__running = False

    def run(self):
        self.__running = True

        # start with full jobs dir scan to retreive state from disk
        self.scanJobsdir()

        logger.info('starting listening for new jobs and notifications')

        incoming_jobs_listener = BusListener(IngestIncomingJobsHandler, {'job_manager': self},
                                             exchange=self._tobus.exchange, broker=self._tobus.broker,
                                             routing_key="%s.#" % DEFAULT_INGEST_INCOMING_JOB_SUBJECT)

        ingest_event_listener = IngestEventMesssageBusListener(IngestEventMessageHandlerForJobManager,
                                                               {'job_manager': self},
                                                               exchange=self._tobus.exchange, broker=self._tobus.broker)

        ingest_service = RPCService(DEFAULT_INGEST_SERVICENAME, IngestServiceMessageHandler, {'job_manager': self},
                                    exchange=self._tobus.exchange, broker=self._tobus.broker, num_threads=4)

        # open exchange connections...
        with incoming_jobs_listener, ingest_event_listener, ingest_service, self._tobus:
            # ... and run the event loop,
            # produce jobs to managed job queue for ingest transfer services
            # receive new jobs
            logger.info('starting to produce jobs')
            while self.__running:
                try:
                    # produce next jobs
                    self.produceNextJobsIfPossible()

                    # check if producing jobs are actually making progress
                    # maybe the ingest transfer server was shut down in the middle of a transer?
                    # the ingest transfer server is stateless, so it won't restart that job itself (by design)
                    # when transfering at very regular intervals progress updates are given
                    # so it is easy for us to detect here if the job is progressing or stalled (see onJobProgress)
                    self.__putStalledJobsBackToToDo()

                    # report on running jobs
                    if datetime.utcnow() - self.__running_jobs_log_timestamp > timedelta(seconds=30):
                        self.__running_jobs_log_timestamp = datetime.utcnow()
                        producing_jads = self.getJobAdminDicts(status=JobProducing)
                        if producing_jads:
                            if len(producing_jads) == 1:
                                logger.info('1 job is running')
                            else:
                                logger.info('%s jobs are running', len(producing_jads))

                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(e)
            logger.info('finished producing jobs')
        logger.info('finished listening for new jobs and notifications')

    def nrOfUnfinishedJobs(self):
        return len(self.getNotDoneJobAdminDicts())

    def nrOfJobs(self):
        return len(self.getJobAdminDicts())

    def getJobAdminDictsFromDisk(self, job_status=None, job_type=None, job_group_id=None, job_id=None):
        job_admin_dicts = []

        if job_status is None:
            for status in [JobToDo, JobRetry, JobFailed, JobHold, JobScheduled, JobProducing, JobProduced, JobRemoved]:
                job_admin_dicts += self.getJobAdminDictsFromDisk(job_status=status, job_type=job_type,
                                                                 job_group_id=job_group_id, job_id=job_id)
            return job_admin_dicts

        dir_path = self.jobDir(job_admin_dict=None, job_status=job_status, job_type=job_type, job_group_id=job_group_id)

        if not os.path.isdir(dir_path):
            return job_admin_dicts

        dir_paths = [dir_path]

        if job_status == JobToDo or job_status == JobRetry:
            dir_paths += IngestJobManager.getSubDirs(dir_path)

        for dp in dir_paths:
            try:
                job_admin_dicts_for_dir = []
                msg = 'scanning %s for job files' % dp
                if job_type:
                    msg += ' job_type=%s' % job_type
                if job_group_id:
                    msg += ' job_group_id=%s' % job_group_id
                if job_status:
                    msg += ' job_status=%s' % jobState2String(job_status)
                if job_id:
                    msg += ' job_id=%s' % job_id
                logger.info(msg)

                xml_files = [os.path.join(dp, f) for f in os.listdir(dp) if fnmatch.fnmatch(f, '*.xml')]

                logger.debug('found %d xml files in %s', len(xml_files), dp)

                if job_id:
                    # opening, parsing, and checking each file is very expensive
                    # if we are looking for a specifix job_id, then try to find quickly based on filename, and leave early when found.
                    # if not found this way, then just scan all files.
                    logger.info('quick scan for job_id: %s', job_id)
                    possible_xml_files_for_job_id = [f for f in xml_files if job_id in f]
                    logger.debug('possible_xml_files_for_job_id: %s', possible_xml_files_for_job_id)

                    for path in possible_xml_files_for_job_id:
                        with open(path) as file:
                            file_content = file.read()
                            job = parseJobXml(file_content)
                            logger.info('job %s \njob_id %s', job, job_id)
                            if job and job_id == job.get('JobId'):
                                job_admin_dict = {'path': path,
                                                    'job': job,
                                                    'job_xml': file_content,
                                                    'runs': {},
                                                    'created_at': datetime.fromtimestamp(os.lstat(path).st_ctime),
                                                    'updated_at': datetime.fromtimestamp(os.lstat(path).st_ctime)}

                                if job_status is not None:
                                    job_admin_dict['status'] = job_status

                                # found the specific file for this job_id, nothing more to search for, leave immediately
                                logger.info('quick scan for job_id returing %s', job_id, job_admin_dict)
                                return [job_admin_dict]

                for path in xml_files:
                    try:
                        with open(path) as file:
                            file_content = file.read()
                            job = parseJobXml(file_content)
                            if job:
                                if ((job_id and job_id == job.get('JobId')) or
                                    (job_id is None and job_group_id and job_group_id == job.get('job_group_id')) or
                                    (job_id is None and job_group_id is None)):
                                    job_admin_dict = {'path': path,
                                                      'job': job,
                                                      'job_xml': file_content,
                                                      'runs': {},
                                                      'created_at': datetime.fromtimestamp(os.lstat(path).st_ctime),
                                                      'updated_at': datetime.fromtimestamp(os.lstat(path).st_ctime)}

                                    if job_status is not None:
                                        job_admin_dict['status'] = job_status

                                    job_admin_dicts_for_dir.append(job_admin_dict)
                    except Exception as e:
                        logger.error(e)

                logger.info('read %d job files from %s', len(job_admin_dicts_for_dir), dp)
                job_admin_dicts += job_admin_dicts_for_dir
            except Exception as e:
                logger.error(e)

        if job_admin_dicts:
            logger.info('read %d job files from %s', len(job_admin_dicts), dir_path)
        return job_admin_dicts

    def jobStatusBaseDir(self, jobstatus):
        if jobstatus == JobToDo:
            return os.path.join(self.__jobs_dir, 'to_do')
        if jobstatus == JobRetry:
            return os.path.join(self.__jobs_dir, 'retry')
        if jobstatus == JobFailed:
            return os.path.join(self.__jobs_dir, 'failed')
        if jobstatus == JobHold:
            return os.path.join(self.__jobs_dir, 'on_hold')
        if jobstatus == JobScheduled:
            return os.path.join(self.__jobs_dir, 'scheduled')
        if jobstatus == JobProducing:
            return os.path.join(self.__jobs_dir, 'producing')
        if jobstatus == JobProduced:
            return os.path.join(self.__jobs_dir, 'done')
        if jobstatus == JobRemoved:
            return os.path.join(self.__jobs_dir, 'removed')
        return os.path.join(self.__jobs_dir, 'unknown')

    def jobStatusBaseDirs(self):
        return [self.jobStatusBaseDir(status) for status in [JobToDo, JobRetry, JobFailed, JobHold, JobScheduled,
                                                             JobProducing, JobProduced, JobRemoved]]

    def jobDir(self, job_admin_dict, job_status=None, job_type=None, job_group_id=None, retry_attempt=None):
        if job_admin_dict:
            return self.jobDir(job_admin_dict=None,
                               job_status=job_admin_dict['status'],
                               job_type=job_admin_dict['job'].get('Type', 'unknown'),
                               job_group_id=job_admin_dict['job'].get('job_group_id', 'unknown'),
                               retry_attempt=job_admin_dict.get('retry_attempt', 1))

        base_dir = self.jobStatusBaseDir(job_status)

        if job_status == JobRetry and retry_attempt != None:
            return os.path.join(base_dir, str(retry_attempt))
        elif job_status in [JobToDo, JobProduced, JobRemoved, JobFailed]:
            if job_type and job_group_id:
                group_dir = '%s_%s' % (job_type, job_group_id)
                return os.path.join(base_dir, group_dir)

        return base_dir

    def jobPath(self, job_admin_dict):
        dir = self.jobDir(job_admin_dict)
        filename = 'j%s.xml' % job_admin_dict['job']['JobId']
        path = os.path.join(dir, filename)
        return path

    def scanJobsdir(self):
        with self.__lock:
            logger.info('scanning jobs dirs in %s', self.__jobs_dir)

            for status in [JobToDo, JobScheduled, JobProducing, JobRetry]:
                job_admin_dicts = self.getJobAdminDictsFromDisk(job_status=status)

                for job_admin_dict in job_admin_dicts:
                    self.addNewJob(job_admin_dict, check_non_todo_dirs=False, add_old_jobs_from_disk=False)

                if job_admin_dicts:
                    logger.info('added %d existing %s jobs from disk', len(job_admin_dicts), jobState2String(status))

            # which (type, group_id) jobs were read
            # read the done jobs for these groups as well
            unique_type_groups = set([(jad['job']['Type'], jad['job'].get('job_group_id', 'unknown_group')) for jad in list(self.__job_admin_dicts.values())])

            if unique_type_groups:
                logger.info('scanning for done jobs for %s', unique_type_groups)

                for job_type, job_group_id in unique_type_groups:
                    for status in [JobFailed, JobProduced, JobRemoved]:
                        job_admin_dicts = self.getJobAdminDictsFromDisk(job_status=status, job_type=job_type, job_group_id=job_group_id)

                        for job_admin_dict in job_admin_dicts:
                            self.addNewJob(job_admin_dict, check_non_todo_dirs=False, add_old_jobs_from_disk=False)

                        if job_admin_dicts:
                            logger.info('added %d existing %s jobs for %s %s', len(job_admin_dicts), jobState2String(status), job_type, job_group_id)

            logger.info('finished scanning jobs in %s, found %s jobs', self.__jobs_dir, len(self.__job_admin_dicts))

    def addNewJob(self, job_admin_dict, check_non_todo_dirs=False, add_old_jobs_from_disk=False):
        with self.__lock:
            job_id = job_admin_dict['job']['JobId']
            job_group_id = job_admin_dict['job'].get('job_group_id')
            job_type = job_admin_dict['job']['Type']
            logger.info('adding new job %s in group %s %s with status %s',
                        job_id,
                        job_type,
                        job_group_id,
                        jobState2String(job_admin_dict.get('status', JobToDo)))


            if check_non_todo_dirs:
                # check if this job is already in memory
                matching_known_jads = []
                for status in [JobScheduled, JobProducing, JobFailed, JobProduced, JobRetry]:
                    matching_known_jads_for_status = self.getJobAdminDicts(job_group_id=job_group_id, status=status)
                    matching_known_jads_for_status_for_job_id = [jad for jad in matching_known_jads_for_status if jad['job']['JobId'] == job_id]

                    if matching_known_jads_for_status_for_job_id:
                        matching_known_jads += matching_known_jads_for_status_for_job_id
                    else:
                        logger.info("no jobs for job_id=%s group_id=%s status=%s found in memory.", job_id,
                                                                                                    job_group_id,
                                                                                                    jobState2String(status))

                        if not matching_known_jads_for_status:
                            logger.info("no jobs for group_id=%s status=%s found in memory. Checking disk...", job_group_id, jobState2String(status))
                            matching_known_jads_for_status = self.getJobAdminDictsFromDisk(job_status=status,
                                                                                        job_type=job_type,
                                                                                        job_group_id=job_group_id,
                                                                                        job_id=job_id)

                            logger.info("found %d jobs for group %s for status=%s on disk", len(matching_known_jads), job_group_id, jobState2String(status))

                            if matching_known_jads_for_status:
                                matching_known_jads += matching_known_jads_for_status


                # remove job from 'done' directories if present (this is a resubmitted job)
                for done_jad in matching_known_jads:
                    try:
                        logger.info('removing done job %s from %s because it is resubmitted', job_id, done_jad['path'])
                        os.remove(done_jad['path'])
                    except Exception as e:
                        logger.error('error while removing done job %s from %s: %s', job_id, done_jad['path'], e)

            self.__job_admin_dicts[job_id] = job_admin_dict
            if 'status' not in job_admin_dict:
                job_admin_dict['status'] = JobToDo

            if 'created_at' not in job_admin_dict:
                job_admin_dict['created_at'] = datetime.utcnow()

            job_admin_dict['updated_at'] = job_admin_dict['created_at']

            # store start- finish times per try in runs
            job_admin_dict['runs'] = {}

            # store new job
            todo_dir = self.jobDir(job_admin_dict)

            # create dir dir if not exists
            if not os.path.isdir(todo_dir):
                try:
                    os.makedirs(todo_dir)
                except OSError as e:
                    logger.error(e)

            if 'path' not in job_admin_dict or 'failed' not in job_admin_dict.get('path', ''):
                path = self.jobPath(job_admin_dict)
                job_admin_dict['path'] = path
                try:
                    if not os.path.exists(path):
                        logger.info('saving job %s on disk: %s', job_id, path)
                        with open(path, 'w') as file:
                            file.write(job_admin_dict['job_xml'])
                except Exception as e:
                    logger.error(e)
            else:
                job_dirname = os.path.dirname(job_admin_dict['path'])
                expected_dirname = self.jobDir(job_admin_dict)
                if job_dirname != expected_dirname:
                    # a new todo job should be located in the expected dir based on its status,
                    # it is not, so force it there
                    self.updateJobStatus(job_admin_dict['job']['JobId'], job_admin_dict['status'])

        if add_old_jobs_from_disk and job_group_id is not None:
            group_jads = self.getJobAdminDicts(job_group_id=job_group_id)
            group_jads = [jad for jad in group_jads if jad['job']['JobId'] != job_id]

            if not group_jads:
                logger.info('%s is the first new job of group %s, scanning disk for \'old\' jobs of this group.', job_id, job_group_id)
                jads_from_disk = self.getJobAdminDictsFromDisk(job_group_id=job_group_id, job_type=job_type)
                for jad in jads_from_disk:
                    if jad['job']['JobId'] != job_id:
                        logger.info('(re)adding job %s with status %s from group %s from disk',
                                    jad['job']['JobId'],
                                    jobState2String(jad.get('status')),
                                    jad['job']['job_group_id'])
                        self.__job_admin_dicts[jad['job']['JobId']] = jad

    def updateJobStatus(self, job_id, new_status, lta_site=None, message=None):
        with self.__lock:
            job_admin_dict = self.__job_admin_dicts.get(job_id)

            if not job_admin_dict:
                logger.error('updateJobStatus: unknown job %s with new status %s', job_id, jobState2String(new_status))
                return

            try:
                # update updated_at timestamp
                job_admin_dict['updated_at'] = datetime.utcnow()

                if new_status == JobProducing:
                    job_admin_dict['runs'][job_admin_dict.get('retry_attempt', 0)] = {}
                    job_admin_dict['runs'][job_admin_dict.get('retry_attempt', 0)]['started_at'] = datetime.utcnow()

                if new_status == JobProduced or new_status == JobTransferFailed:
                    try:
                        job_admin_dict['runs'][job_admin_dict.get('retry_attempt', 0)]['finished_at'] = datetime.utcnow()
                    except:
                        pass

                if lta_site:
                    job_admin_dict['lta_site'] = lta_site

                job_admin_dict['last_message'] = message

                current_status = job_admin_dict.get('status', JobToDo)

                if new_status == JobTransferFailed:
                    # special case for jobs which failed to transer, which will be retried
                    current_retry_attempt = job_admin_dict.get('retry_attempt', 0)
                    next_retry_attempt = current_retry_attempt + 1

                    if next_retry_attempt < self.__max_num_retries:
                        if message and 'not on disk' in message.lower():
                            logger.info('job %s transfer failed because source data was not on disk, not retrying anymore', job_id)
                            new_status = JobFailed
                        elif message and 'invalid sip' in message.lower():
                            logger.info('job %s transfer failed because the SIP is invalid, not retrying anymore, please fix SIP and resubmit job to ingest.', job_id)
                            new_status = JobFailed
                        else:
                            new_status = JobRetry
                            job_admin_dict['retry_attempt'] = next_retry_attempt
                            job_admin_dict['job']['last_retry_attempt'] = next_retry_attempt == (self.__max_num_retries-1)
                    else:
                        logger.info('job %s transfer failed %s times, not retrying anymore',
                                    job_id,
                                    job_admin_dict.get('retry_attempt', 0))
                        new_status = JobFailed

                if new_status != current_status:
                    # update the internal status
                    logger.info('updating job %s status from %s to %s%s',
                                job_id,
                                jobState2String(current_status),
                                jobState2String(new_status),
                                (' attempt #%d' % job_admin_dict.get('retry_attempt', 1))
                                if (new_status == JobRetry or current_status == JobRetry) else '')
                    job_admin_dict['status'] = new_status

                # move the job file to its new status directory
                # determine current and new paths
                current_path = job_admin_dict.get('path', '')
                new_path = self.jobPath(job_admin_dict)
                new_dirname = os.path.dirname(new_path)

                # create dir dir if not exists
                if not os.path.isdir(new_dirname):
                    try:
                        os.makedirs(new_dirname)
                    except OSError as e:
                        logger.error(e)

                if new_path != current_path:
                    # do actual file move
                    logger.debug('moving job file from %s to %s.', current_path, new_path)
                    shutil.move(current_path, new_path)
                    job_admin_dict['path'] = new_path

                    # nice cleanup of obsolete empty directories
                    try:
                        old_dirname = os.path.dirname(current_path)
                        if old_dirname.startswith(self.__jobs_dir) and len(os.listdir(old_dirname)) == 0:
                            if old_dirname not in self.jobStatusBaseDirs():
                                logger.info('removing empty jobs directory: %s', old_dirname)
                                os.rmdir(old_dirname)
                    except OSError as e:
                        logger.error(e)

                if new_status == JobRemoved or new_status == JobFailed:
                    # send notification
                    # this is (also) picked up by the ingestmomadapter
                    # which also sends a status update to MoM, including the last_message
                    if new_status == JobRemoved:
                        job_admin_dict['last_message'] = 'removed from queue'

                    self._sendNotification(job_admin_dict)

                # finally, remove job from interal admin jobs dict if finished
                if job_admin_dict['status'] in [JobProduced, JobFailed, JobRemoved]:
                    current_job_group_id = job_admin_dict['job'].get('job_group_id', 'unknown')
                    current_group_jads = self.getNotDoneJobAdminDicts(job_group_id=current_job_group_id)

                    if len(current_group_jads) == 0:
                        logger.info('all jobs in group %s are done', current_job_group_id)
                        self.sendJobGroupFinishedMail(current_job_group_id)

                        current_group_done_jads = self.getDoneJobAdminDicts(job_group_id=current_job_group_id)
                        logger.info('removing %s jobs of group %s from job management server memory',
                                    len(current_group_done_jads),
                                    current_job_group_id)

                        for jad in current_group_done_jads:
                            del self.__job_admin_dicts[jad['job']['JobId']]
                    else:
                        logger.info('%s jobs to do in group %s', len(current_group_jads), current_job_group_id)
            except Exception as e:
                logger.exception(str(e))
                logger.error("updateJobStatus(job_id=%s, new_status=%s, lta_site=%s, message=%s) %s",
                             job_id,
                             jobState2String(new_status),
                             lta_site,
                             message,
                             e)

    def _sendNotification(self, job_admin_dict):
        try:
            job = job_admin_dict['job']
            contentDict = {'job_id': job['JobId'],
                           'archive_id': job['ArchiveId'],
                           'project': job['Project'],
                           'type': job["Type"],
                           'dataproduct': job['DataProduct']}

            if 'ObservationId' in job:
                contentDict['otdb_id'] = job['ObservationId']

            if 'lta_site' in job_admin_dict:
                contentDict['lta_site'] = job_admin_dict['lta_site']

            if 'last_message' in job_admin_dict:
                contentDict['message'] = job_admin_dict['last_message']

            if 'job_group_id' in job_admin_dict:
                contentDict['export_id'] = job_admin_dict['job_group_id']

            status = jobState2String(job_admin_dict['status'])
            status = status[status.index('(') + 1:status.index(')')]

            msg = EventMessage(subject="%s.%s" % (INGEST_NOTIFICATION_PREFIX, status), content=contentDict)
            # remove message from queue's when not picked up within 48 hours,
            # otherwise mom might endlessly reject messages if it cannot handle them
            msg.ttl = 48 * 3600
            logger.info('Sending notification %s: %s' % (status, str(contentDict).replace('\n', ' ')))
            self._tobus.send(msg)

        except Exception as e:
            logger.error(str(e))

    def removeExportJob(self, export_group_id):
        logger.info('removing export job %s', export_group_id)
        job_admin_dicts = self.getJobAdminDicts(job_group_id=export_group_id)

        if job_admin_dicts:
            for jad in job_admin_dicts:
                self.updateJobStatus(jad['job']['JobId'], JobRemoved)

    def getExportIds(self):
        with self.__lock:
            return sorted(list(set([jad['job'].get('job_group_id', 'unknown_group') for jad in list(self.__job_admin_dicts.values())])))

    def __putStalledJobsBackToToDo(self):
        if datetime.utcnow() - self.__last_putStalledJobsBackToToDo_timestamp < timedelta(seconds=60):
            return

        logger.debug("checking stalled jobs...")

        with self.__lock:
            scheduled_jads = self.getJobAdminDicts(status=JobScheduled)
            stalled_scheduled_jads = [jad for jad in scheduled_jads
                                      if datetime.utcnow() - jad['updated_at'] >= timedelta(seconds=30)]

            for jad in stalled_scheduled_jads:
                logger.info('putting stalled scheduled job %s back to ToDo because it was not picked up in time by a transferservice', jad['job']['JobId'])
                self.updateJobStatus(jad['job']['JobId'], JobToDo)

            producing_jads = self.getJobAdminDicts(status=JobProducing)
            stalled_producing_jads = [jad for jad in producing_jads
                                      if datetime.utcnow() - jad['updated_at'] >= timedelta(minutes=10)]

            for jad in stalled_producing_jads:
                logger.info('putting stalled producing job %s back to ToDo because it did not make any progress during the last 10 min', jad['job']['JobId'])
                self.updateJobStatus(jad['job']['JobId'], JobToDo)

            self.__last_putStalledJobsBackToToDo_timestamp = datetime.utcnow()

        logger.debug("checked stalled jobs")

    def getNextJobToRun(self):
        '''get the next job to run.
        examine all 'to_do' and 'retry' jobs
        higher priority jobs always go first
        equal priority jobs will return 'to_do' jobs over 'retry' jobs
        'retry' jobs are sorted by least amount of retry attempts
        source load balancing: the more jobs transfer from a certain source host,
                               the less likely it is a next job will be for that source host as well
        '''

        # helper method to get the source host from the job's location
        def getSourceHost(job_admin_dict):
            try:
                host = job_admin_dict['job']['Location'].split(':')[0]
                if 'cep4' in host.lower() or 'cpu' in host.lower():
                    return 'localhost'
                return host
            except:
                return 'localhost'

        running_jads = self.getJobAdminDicts(status=JobProducing) + self.getJobAdminDicts(status=JobScheduled)
        running_hosts = {}
        for jad in running_jads:
            host = getSourceHost(jad)
            running_hosts[host] = running_hosts.get(host, 0) + 1

        with self.__lock:
            def getNextJobByStatus(status, min_age=None, exclude_job_group_ids=[]):

                def jad_compare_func(jad_a, jad_b):
                    # sort on priority first
                    if jad_a['job'].get('priority', DEFAULT_JOB_PRIORITY) != jad_b['job'].get('priority', DEFAULT_JOB_PRIORITY):
                        return jad_b['job'].get('priority', DEFAULT_JOB_PRIORITY) - jad_a['job'].get('priority', DEFAULT_JOB_PRIORITY)

                    # equal priorities, so sort on next sort criterion, the retry attempt
                    if jad_a['status'] == JobRetry and jad_b['status'] == JobRetry:
                        if jad_a.get('retry_attempt', 0) != jad_b.get('retry_attempt', 0):
                            return jad_b.get('retry_attempt', 0) - jad_a.get('retry_attempt', 0)

                    # equal retry_attempt, so sort on next sort criterion,
                    # jobs for which the number of running jobs on that host is lower
                    # (load balance the source hosts)
                    nrOfRunningJobsOnSourceHostA = running_hosts.get(getSourceHost(jad_a), 0)
                    nrOfRunningJobsOnSourceHostB = running_hosts.get(getSourceHost(jad_b), 0)

                    if nrOfRunningJobsOnSourceHostA != nrOfRunningJobsOnSourceHostB:
                        return nrOfRunningJobsOnSourceHostA - nrOfRunningJobsOnSourceHostB

                    # everything above equal? sort on next sort criterion, the group_id
                    if jad_a.get('job_group_id', 0) < jad_b.get('job_group_id', 0):
                        return -1
                    if jad_a.get('job_group_id', 0) > jad_b.get('job_group_id', 0):
                        return 1

                    # everything above equal? sort on next sort criterion, the dataproduct name,
                    # which in effect sorts on otdb id first, and then on subband
                    if jad_a.get('dataproduct', '') < jad_b.get('dataproduct', ''):
                        return -1
                    if jad_a.get('dataproduct', '') > jad_b.get('dataproduct', ''):
                        return 1

                    # everything above equal? sort on next sort criterion, the updated_at timestamp
                    # least recent updated_at job goes first
                    # if no updated_at timestamp available, use 'now'
                    now = datetime.utcnow()
                    if jad_a.get('updated_at', now) < jad_b.get('updated_at', now):
                        return -1
                    if jad_a.get('updated_at', now) > jad_b.get('updated_at', now):
                        return 1

                    # everything else equal? Then make it a FIFO queue by sorting on created_at timestamp
                    if jad_a['created_at'] < jad_b['created_at']:
                        return -1
                    if jad_a['created_at'] > jad_b['created_at']:
                        return 1

                    # TODO: we can add a lot of sort criteria in the future.
                    # For now, stick with FIFO and retry_attempt, after priority and source_host_load_balancing
                    return 0

                job_admin_dicts = self.getJobAdminDicts(status=status)

                # filter out priority 0 jobs (which are paused)
                job_admin_dicts = [jad for jad in job_admin_dicts if jad['job'].get('priority', 0) > 0]

                if min_age:
                    now = datetime.utcnow()
                    job_admin_dicts = [jad for jad in job_admin_dicts if now - jad['updated_at'] >= min_age]

                if exclude_job_group_ids:
                    # filter out jad's from exclude_job_group_ids
                    job_admin_dicts = [jad for jad in job_admin_dicts if 'job_group_id' not in jad['job'] or jad['job']['job_group_id'] not in exclude_job_group_ids]

                job_admin_dicts = sorted(job_admin_dicts, key=cmp_to_key(jad_compare_func))
                if job_admin_dicts:
                    logger.info('%s jobs with status %s waiting', len(job_admin_dicts), jobState2String(status))
                    return job_admin_dicts[0]
                return None

            # gather some average speed stats for running groups
            running_job_group_avg_speeds = {}
            running_job_group_ids = set([jad['job']['job_group_id'] for jad in running_jads if 'job_group_id' in jad['job']])
            for job_group_id in running_job_group_ids:
                # get last 10 finished jobs with an average_speed for this group to compute avg speed
                group_finished_jads = [jad for jad in self.getJobAdminDicts(job_group_id=job_group_id, status=[JobProduced]) if 'average_speed' in jad]
                group_finished_jads = sorted(group_finished_jads, key=lambda jad: jad['updated_at'])[-10:]
                if len(group_finished_jads) == 10:
                    running_job_group_avg_speeds[job_group_id] = sum(jad['average_speed'] for jad in group_finished_jads)/len(group_finished_jads)
                    logger.debug('average speed over last 10 transers for group %s = %s', job_group_id, humanreadablesize(running_job_group_avg_speeds[job_group_id], 'Bps'))

            # which job_group_ids are slow?
            # this is most likely caused by transfers of small files for which the overhead has a huge impact on the overall average transfer speed
            # thus, these slow_running_job_group_ids are not making optimal use of the available bandwidth
            # since we cannot start a huge amount of parallel transfers to increase the total used average bandwith
            slow_running_job_group_ids = [job_group_id for job_group_id,avg_speed in list(running_job_group_avg_speeds.items()) if avg_speed < 1.0e7]

            # randomize whether a slow job_group_id will produce the next job or not.
            # if not (and it is in the exclude_job_group_ids list), then the first available job from the rest of the groups is picked.
            # it is quite likely that the next group has larger files, thus will make better use of the available bandwith
            # the actual transfer speed of the next group will be measured as well, and if slow, it will be excluded once in a while as well.
            # The higher the job_group's priority, the bigger chance it has to be included, so high priority jobs will run faster overall.
            exclude_job_group_ids = [job_group_id for job_group_id in slow_running_job_group_ids
                                     if random() > self.getExportJobPriority(job_group_id) * 0.1111]

            # if there are job_group_ids to be excluded (for slow transfers) but there are no other group_ids to be exported,
            # then do not exclude anything
            if exclude_job_group_ids:
                all_group_ids = set(self.getExportIds())
                if set(exclude_job_group_ids) == all_group_ids:
                    exclude_job_group_ids = []
                else:
                    logger.info('excluding jobs from group(s) %s while determining the next job to run, because of their slow overall average speed', exclude_job_group_ids)

            # get the next job to run, both for JobToDo and JobRetry
            next_to_do_jad = getNextJobByStatus(JobToDo, exclude_job_group_ids=exclude_job_group_ids)
            next_retry_jad = getNextJobByStatus(JobRetry, timedelta(minutes=15) if next_to_do_jad else None)

            # limit the number of running jobs per source host if not localhost
            if next_to_do_jad and getSourceHost(next_to_do_jad) != 'localhost':
                if running_hosts.get(getSourceHost(next_to_do_jad), 0) > 1:
                    next_to_do_jad = None

            # limit the number of running jobs per source host if not localhost
            if next_retry_jad and getSourceHost(next_retry_jad) != 'localhost':
                if running_hosts.get(getSourceHost(next_retry_jad), 0) > 1:
                    next_retry_jad = None

            if next_to_do_jad and next_retry_jad:
                # if next_retry_jad has higher priority then next_to_do_jad, then return next_retry_jad
                if next_retry_jad['job'].get('priority', DEFAULT_JOB_PRIORITY) > next_to_do_jad['job'].get('priority', DEFAULT_JOB_PRIORITY):
                    return next_retry_jad

                # or if next_to_do_jad has higher priority then next_retry_jad, then return next_to_do_jad
                if next_to_do_jad['job'].get('priority', DEFAULT_JOB_PRIORITY) > next_retry_jad['job'].get('priority', DEFAULT_JOB_PRIORITY):
                    return next_to_do_jad

                # or if next_retry_jad is already waiting for over an hour, then return next_retry_jad
                if datetime.utcnow() - next_retry_jad['updated_at'] > timedelta(minutes=60):
                    return next_retry_jad

                # or if next_retry_jad is older than next_to_do_jad
                if next_retry_jad['updated_at'] > next_to_do_jad.get('updated_at', next_to_do_jad.get('created_at')):
                    return next_retry_jad

            if next_to_do_jad:
                # just return the next_to_do_jad
                return next_to_do_jad

            # in all other cases, return next_retry_jad (which might be None)
            return next_retry_jad

    def canProduceNextJob(self):
        # test if the managed_job_queue is empty enough, and if our administration agrees
        try:
            if len(self.getJobAdminDicts(status=JobScheduled)) > 0:
                return False

            # HACK: hardcoded queue name
            job_for_transfer_queue_name = adaptNameToEnvironment("lofar.queue.for.ingesttransferserver.BusListener.on.LTA.Ingest.job_for_transfer")
            return nr_of_messages_in_queue(job_for_transfer_queue_name, self._tobus.broker) == 0
        except Exception as e:
            logger.exception('canProduceNextJob: %s', e)
            if 'No active session' in str(e):
                logger.fatal('cannot connect to qpid broker. bailing out...')
                exit(1) # when running under supervisord, it will be restarted and the qpid connection usually works again.
        return True

    def produceNextJobsIfPossible(self):
        start_producing_timestamp = datetime.utcnow()
        while self.canProduceNextJob() and datetime.utcnow() - start_producing_timestamp < timedelta(seconds=5):
            job_admin_dict = self.getNextJobToRun()
            if not job_admin_dict:
                return

            if os.path.exists(job_admin_dict.get('path')):
                self.updateJobStatus(job_admin_dict['job']['JobId'], JobScheduled)

                msg = CommandMessage(content=job_admin_dict.get('job_xml'), subject=DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT, ttl=60)
                msg.priority = job_admin_dict['job'].get('priority', DEFAULT_JOB_PRIORITY)
                self._tobus.send(msg)
                logger.info('submitted job %s to exchange \'%s\' at %s', job_admin_dict['job']['JobId'], self._tobus.exchange, self._tobus.broker)
            else:
                job_id = job_admin_dict['job']['JobId']
                logger.warning('job file for %s is not on disk at %s anymore. removing job from todo list', job_id, job_admin_dict.get('path'))
                del self.__job_admin_dicts[job_id]

            # rate limit at 10 jobs/sec
            time.sleep(0.1)

    def onJobStarted(self, job_notification_dict):
        self.updateJobStatus(job_notification_dict.get('job_id'),
                             JobProducing,
                             job_notification_dict.get('lta_site'),
                             job_notification_dict.get('message'))

    def onJobFinished(self, job_notification_dict):
        job_id = job_notification_dict.get('job_id')

        # file_type might have changed to unspec for example
        if 'file_type' in job_notification_dict:
            with self.__lock:
                job_admin_dict = self.__job_admin_dicts.get(job_id)
                if job_admin_dict:
                    job_admin_dict['job']['file_type'] = job_notification_dict['file_type']

        try:
            if 'average_speed' in job_notification_dict:
                with self.__lock:
                    # keep track of average transfer speed
                    job_admin_dict = self.__job_admin_dicts.get(job_id)
                    if job_admin_dict:
                        job_average_speed = float(job_notification_dict['average_speed'])
                        job_admin_dict['average_speed'] = job_average_speed
        except Exception as e:
            #just continue
            logger.exception(str(e))

        self.updateJobStatus(job_notification_dict.get('job_id'),
                             JobProduced,
                             job_notification_dict.get('lta_site'),
                             job_notification_dict.get('message'))

    def onJobTransferFailed(self, job_notification_dict):
        self.updateJobStatus(job_notification_dict.get('job_id'),
                             JobTransferFailed,
                             job_notification_dict.get('lta_site'),
                             job_notification_dict.get('message'))

    def onJobProgress(self, job_notification_dict):
        # touch job
        # producing jobs which are untouched for 5min are put back to JobToDo
        self.updateJobStatus(job_notification_dict.get('job_id'),
                             JobProducing,
                             job_notification_dict.get('lta_site'),
                             job_notification_dict.get('message'))

    @staticmethod
    def getSubDirs(dir_path):
        dir_lists = [[os.path.join(root,dir) for dir in dirs if root==dir_path] for root, dirs, files in os.walk(dir_path) if dirs]
        if dir_lists:
            return reduce(lambda x, y: x + y, dir_lists)
        return []

    def getDoneJobAdminDicts(self, job_group_id=None):
        return self.getJobAdminDicts(job_group_id=job_group_id, status=[JobFailed, JobProduced, JobRemoved])

    def getNotDoneJobAdminDicts(self, job_group_id=None):
        return self.getJobAdminDicts(job_group_id=job_group_id, status=[JobToDo, JobScheduled, JobProducing, JobRetry])

    def getJobAdminDicts(self, job_group_id=None, status=None):
        with self.__lock:
            jads = [jad for jad in list(self.__job_admin_dicts.values())]

            if job_group_id != None:
                job_group_id = str(job_group_id)
                jads = [jad for jad in jads if str(jad['job'].get('job_group_id')) == job_group_id]

            if status != None:
                if isinstance(status, int):
                    jads = [jad for jad in jads if jad['status'] == status]
                else:
                    statuses = set(status)
                    jads = [jad for jad in jads if jad['status'] in statuses]

            return jads

    def getStatusReportDict(self):
        with self.__lock:
            export_ids = self.getExportIds()
            logger.info('getStatusReportDict export_ids: %s', export_ids)

            result = {}
            for export_id in export_ids:
                try:
                    finished_group_jads = self.getJobAdminDicts(job_group_id=export_id, status=JobProduced)
                    failed_group_jads = self.getJobAdminDicts(job_group_id=export_id, status=JobFailed)
                    removed_group_jads = self.getJobAdminDicts(job_group_id=export_id, status=JobRemoved)

                    done_group_jads = finished_group_jads + failed_group_jads + removed_group_jads
                    done_group_jobs = [jad['job'] for jad in done_group_jads]

                    current_group_jads = self.getNotDoneJobAdminDicts(job_group_id=export_id)
                    current_group_jobs = [jad['job'] for jad in current_group_jads]
                    all_group_jads = current_group_jads + done_group_jads
                    all_group_jobs = current_group_jobs + done_group_jobs

                    priority = min([job.get('priority', DEFAULT_JOB_PRIORITY) for job in current_group_jobs]) if current_group_jobs else 4
                    submitters = list(set([job['Submitter'] for job in all_group_jobs if 'Submitter' in job]))
                    projects = list(set([job['Project'] for job in all_group_jobs if 'Project' in job]))
                    lta_sites = list(set([jad['lta_site'] for jad in all_group_jads if 'lta_site' in jad]))

                    job_run_events = {}
                    for jad in all_group_jads:
                        for run in list(jad['runs'].values()):
                            if 'started_at' in run:
                                started_timestamp = run['started_at']

                                if started_timestamp not in job_run_events:
                                    job_run_events[started_timestamp] = 0

                                job_run_events[started_timestamp] += 1

                                if 'finished_at' in run:
                                    finished_timestamp = run['finished_at']

                                    if finished_timestamp not in job_run_events:
                                        job_run_events[finished_timestamp] = 0

                                    job_run_events[finished_timestamp] -= 1

                    all_run_timestamps = sorted(job_run_events.keys())
                    running_jobs_values = []
                    if all_run_timestamps:
                        prev_value = 0

                        for t in all_run_timestamps:
                            value = prev_value + job_run_events[t]
                            running_jobs_values.append(value)
                            prev_value = value

                    job_finised_events = {}
                    for jad in all_group_jads:
                        if jad['status'] == JobProduced or jad['status'] == JobFailed:
                            if jad['runs']:
                                final_run = max(jad['runs'].keys())

                                run = jad['runs'][final_run]
                                if 'started_at' in run and 'finished_at' in run:
                                    finished_timestamp = run['finished_at']

                                    if finished_timestamp not in job_finised_events:
                                        job_finised_events[finished_timestamp] = 0

                                    job_finised_events[finished_timestamp] += 1

                    finished_jobs_values = []
                    finished_timestamps = sorted(job_finised_events.keys())
                    for i, t in enumerate(finished_timestamps):
                        finished_jobs_values.append(i + 1)

                    result[export_id] = {'priority': priority,
                                         'submitters': submitters,
                                         'projects': projects,
                                         'lta_sites': lta_sites,
                                          'series': { 'running_jobs': { 'timestamps': all_run_timestamps, 'values': running_jobs_values },
                                                      'finished_jobs': { 'timestamps': finished_timestamps, 'values': finished_jobs_values }
                                                    },
                                          'jobs': { 'running': len(self.getJobAdminDicts(job_group_id=export_id, status=JobProducing)),
                                                    'to_do': len(self.getJobAdminDicts(job_group_id=export_id, status=JobToDo)),
                                                    'scheduled': len(self.getJobAdminDicts(job_group_id=export_id, status=JobScheduled)),
                                                    'retry': len(self.getJobAdminDicts(job_group_id=export_id, status=JobRetry)),
                                                  'finished': len(finished_group_jads),
                                                  'failed': len(failed_group_jads)}}
                except Exception as e:
                    logger.error(e)

            return result

    def setExportJobPriority(self, export_id, priority):
        priority = max(0, min(9, int(priority)))
        with self.__lock:
            jads = self.getJobAdminDicts(job_group_id=export_id)

            logger.info('updating the priority of %s jobs of export %s to level %s', len(jads), export_id, priority)

            for jad in jads:
                try:
                    # update local copy
                    jad['job']['priority'] = priority
                    # persist to disk
                    updatePriorityInJobFile(jad['path'], priority)
                except Exception as e:
                    logger.error(e)

    def getExportJobPriority(self, export_id):
        with self.__lock:
            job_group_id = str(export_id)
            for jad in list(self.__job_admin_dicts.values()):
                if str(jad['job'].get('job_group_id')) == job_group_id:
                    if 'priority' in jad['job']:
                        return jad['job']['priority']

        return DEFAULT_JOB_PRIORITY

    def getReport(self, job_group_id):
        with self.__lock:
            # still running/waiting jobs
            current_group_jads = self.getNotDoneJobAdminDicts(job_group_id=job_group_id)
            current_group_jobs = [jad['job'] for jad in current_group_jads]

            # done jobs
            finished_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobProduced)
            finished_group_jobs = [jad['job'] for jad in finished_group_jads]
            failed_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobFailed)
            failed_group_jobs = [jad['job'] for jad in failed_group_jads]
            removed_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobRemoved)
            removed_group_jobs = [jad['job'] for jad in removed_group_jads]

            done_group_jobs = finished_group_jobs + failed_group_jobs + removed_group_jobs
            all_group_jobs = current_group_jobs + done_group_jobs

            submitters = set([j['Submitter'] for j in all_group_jobs if 'Submitter' in j])
            projects = set([j['Project'] for j in all_group_jobs if 'Project' in j])

            report = ''

            header = """=== Report on ingest Export Job (%(id)s) ===
User(s): %(user)s
Project: %(project)s""" % {'id': job_group_id,
                           'user': ', '.join(submitters),
                           'project': ', '.join(projects)}

            report += header

            summary = """\n\n=== Summary ===
Total Files: %(total)i
  - Failed: %(failed)i
  - Success: %(done)i
    - Interferometer: %(corr)i
    - Beamformed: %(bf)i
    - SkyImages: %(img)i
    - Unspecified: %(unspec)i
    - Pulsar Pipeline: %(pulp)i""" % {'total': len(all_group_jobs),
                                      'done': len(finished_group_jobs),
                                      'corr': len([j for j in finished_group_jobs if j.get('file_type',-1) == FILE_TYPE_CORRELATED]),
                                      'bf': len([j for j in finished_group_jobs if j.get('file_type',-1) == FILE_TYPE_BEAMFORMED]),
                                      'img': len([j for j in finished_group_jobs if j.get('file_type',-1) == FILE_TYPE_IMAGE]),
                                      'unspec': len([j for j in finished_group_jobs if j.get('file_type',-1) == FILE_TYPE_UNSPECIFIED]),
                                      'pulp': len([j for j in finished_group_jobs if j.get('file_type',-1) == FILE_TYPE_PULP]),
                                      'failed': len(failed_group_jobs)}

            # TODO: generate lta link
            # try:
            # import mechanize
            # import json
            # browser = mechanize.Browser()
            # browser.set_handle_robots(False)
            # browser.addheaders = [('User-agent', 'Firefox')]

            # obs_ids = sorted(list(set(job.get('ObservationId', -1) for job in all_group_jobs)))

            # for obs_id in obs_ids:
            # response = browser.open('http://scu001.control.lofar:7412/rest/tasks/otdb/%s' % obs_id)

            # if response.code == 200:
            # task = json.loads(response.read())

            # except Exception as e:
            # logger.error(e)

            if removed_group_jobs:
                summary += '''\n\nTotal Removed before transfer: %s''' % (len(removed_group_jobs),)

            report += summary

            def file_listing_per_obs(jads, full_listing=False, dp_status_remark=''):
                jobs = [jad['job'] for jad in jads]
                obs_ids = sorted(list(set(job.get('ObservationId', -1) for job in jobs)))
                obs_jads_dict = {obs_id: [] for obs_id in obs_ids}

                for jad in jads:
                    obs_jads_dict[jad['job'].get('ObservationId', -1)].append(jad)

                listing = ''
                for obs_id in obs_ids:
                    obs_jads = obs_jads_dict[obs_id]
                    listing += 'otdb_id: %s - #dataproducts: %s\n' % (obs_id, len(obs_jads))

                if full_listing:
                    for obs_id in obs_ids:
                        obs_jads = obs_jads_dict[obs_id]
                        obs_jads = sorted(obs_jads, key=lambda jad: jad['job'].get('DataProduct'))
                        listing += '\notdb_id: %s - %s dataproducts listing\n' % (obs_id, dp_status_remark)

                        for jad in obs_jads:
                            listing += 'dataproduct: %s - archive_id: %s - location: %s' % (jad['job']['DataProduct'],
                                                                                            jad['job']['ArchiveId'],
                                                                                            jad['job'].get('Location'))

                            if jad.get('last_message'):
                                listing += ' - message: %s' % (jad['last_message'])
                            listing += '\n'

                return listing

            if current_group_jads:
                report += "\n\n==== Scheduled/Running files: =====\n"
                report += file_listing_per_obs(current_group_jads, False, 'scheduled/running')

            if finished_group_jads:
                report += "\n\n==== Finished files: =====\n"
                report += file_listing_per_obs(finished_group_jads, False, 'finished')

            if failed_group_jads:
                report += "\n\n==== Failed files: =====\n"
                report += file_listing_per_obs(failed_group_jads, True, 'failed')

            if removed_group_jads:
                report += "\n\n==== Removed jobs before transfer: =====\n"
                report += file_listing_per_obs(removed_group_jads, False, 'removed')

            return report

    def sendJobGroupFinishedMail(self, job_group_id):
        report = self.getReport(job_group_id)
        #replace forbidden quotes which mess up the cmdline mail call
        report = report.replace('\'', '').replace('\"', '').replace('<', '').replace('>', '')
        logger.info(report)

        mailing_list = list(FINISHED_NOTIFICATION_MAILING_LIST)

        finished_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobProduced)
        failed_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobFailed)
        removed_group_jads = self.getJobAdminDicts(job_group_id=job_group_id, status=JobRemoved)
        unfinished_group_jads = failed_group_jads + removed_group_jads

        done_group_jads = finished_group_jads + failed_group_jads + removed_group_jads
        done_group_jobs = [jad['job'] for jad in done_group_jads]
        submitters = [j['Submitter'] for j in done_group_jobs if 'Submitter' in j]
        extra_mail_addresses = [j['email'] for j in done_group_jobs if 'email' in j]

        try:
            if len(unfinished_group_jads) == 0:
                # only for successful ingests,
                # try to get the PI's email address for this export's projects
                # and add these to the extra_mail_addresses
                done_group_mom_jobs = [job for job in done_group_jobs if job.get('Type', '').lower() == 'mom']
                mom_export_ids = set([int(job['JobId'].split('_')[1]) for job in done_group_mom_jobs if 'JobId' in job])

                with MoMQueryRPC.create(exchange=self._tobus.exchange, broker=self._tobus.broker) as momrpc:
                    mom_objects_details = momrpc.getObjectDetails(mom_export_ids)
                    project_mom2ids = set(obj_details.get('project_mom2id') for obj_details in mom_objects_details.values())
                    project_mom2ids = [x for x in project_mom2ids if x is not None]

                    for project_mom2id in project_mom2ids:
                        project_details = momrpc.get_project_details(project_mom2id)
                        if project_details and 'pi_email' in project_details:
                            extra_mail_addresses.append(project_details['pi_email'])
                        if project_details and 'author_email' in project_details:
                            extra_mail_addresses.append(project_details['author_email'])

                if not extra_mail_addresses:
                    report += '\n\nCould not find any PI\'s/Contact-author\'s email address in MoM to sent this email to.'

        except Exception as e:
            msg = 'error while trying to get PI\'s/Contact-author\'s email address for %s: %s' % (job_group_id, e)
            logger.error(msg)
            report += '\n\n' + msg

        # submitters might contain comma seperated strings
        # join all sumbitterstrings in one long csv string, split it, and get the unique submitters
        submitters = list(set([s.strip() for s in ','.join(submitters).split(',') if '@' in s]))

        # do the same for extra_mail_addresses
        extra_mail_addresses = list(set([s.strip() for s in ','.join(extra_mail_addresses).split(',') if '@' in s]))

        mailing_list += submitters + extra_mail_addresses
        if mailing_list:
            # make it a csv list of addresses
            mailing_list_csv = ','.join(mailing_list)
            bcc_mailing_list_csv = ','.join(FINISHED_NOTIFICATION_BCC_MAILING_LIST)
            projects = set([j['Project'] for j in done_group_jobs if 'Project' in j])

            subject = "Ingest Export job %s of project %s " % (job_group_id, '/'.join(projects))
            if len(unfinished_group_jads) == 0:
                subject += 'finished successfully'
            elif removed_group_jads:
                if len(removed_group_jads) == len(done_group_jads):
                    subject += 'was removed completely before transfer'
                else:
                    subject += 'was removed partially before transfer'
            else:
                subject += 'finished with errors. %d/%d (%.1f%%) dataproducts did not transfer.' % (len(unfinished_group_jads),
                len(done_group_jads),
                100.0 * len(unfinished_group_jads) / len(done_group_jads))

            if os.system('echo "%s"|mailx -s "%s" %s %s' % (report,
                                                            subject,
                                                            '-b ' + bcc_mailing_list_csv if bcc_mailing_list_csv else '',
                                                            mailing_list_csv)) == 0:
                logger.info('sent notification email for export job %s to %s', job_group_id, mailing_list)
            else:
                logger.error('failed sending a notification email for export job %s to %s', job_group_id, mailing_list)
        else:
            logger.warning('no email recipients for sending notification email for export job %s', job_group_id)


class IngestServiceMessageHandler(ServiceMessageHandler):
    def __init__(self, job_manager: IngestJobManager):
        super(IngestServiceMessageHandler, self).__init__()
        # register some of the job_manager's methods for the service
        self.register_service_method('RemoveExportJob', job_manager.removeExportJob)
        self.register_service_method('SetExportJobPriority', job_manager.setExportJobPriority)
        self.register_service_method('GetStatusReport', job_manager.getStatusReportDict)
        self.register_service_method('GetReport', job_manager.getReport)
        self.register_service_method('GetExportIds', job_manager.getExportIds)


class IngestIncomingJobsHandler(AbstractMessageHandler):
    def __init__(self, job_manager: IngestJobManager):
        self._job_manager = job_manager
        super(IngestIncomingJobsHandler, self).__init__()

    def handle_message(self, msg: LofarMessage):
        if not isinstance(msg, CommandMessage):
            raise ValueError("%s: Ignoring non-CommandMessage: %s" % (self.__class__.__name__, msg))

        job = parseJobXml(msg.content)
        if job and job.get('JobId'):
            if msg.priority != None and msg.priority > job.get('priority', DEFAULT_JOB_PRIORITY):
                job['priority'] = msg.priority

            logger.info("received job from bus: %s", job)
            job_admin_dict = {'job': job, 'job_xml': msg.content}
            self._job_manager.addNewJob(job_admin_dict, check_non_todo_dirs=True, add_old_jobs_from_disk=True)

class IngestEventMessageHandlerForJobManager(IngestEventMessageHandler):
    def __init__(self, job_manager: IngestJobManager):
        self.onJobStarted = job_manager.onJobStarted
        self.onJobProgress = job_manager.onJobProgress
        self.onJobTransferFailed = job_manager.onJobTransferFailed
        self.onJobFinished = job_manager.onJobFinished
        super().__init__(['JobStarted', 'JobFinished', 'JobTransferFailed', 'TaskProgress', 'TaskFinished'])

def main():
    from optparse import OptionParser

    # make sure we run in UTC timezone
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run the ingest job management server')
    parser.add_option('-j', '--jobs_dir', dest='jobs_dir', type='string', default=JOBS_DIR, help='directory path where the jobs located on disk, default: %default')
    parser.add_option('-r', '--max_num_retries', dest='max_num_retries', type='int', default=MAX_NR_OF_RETRIES, help='maximum number of retries for a failing job, default: %default')
    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('-e', "--exchange", dest="exchange", type="string", default=DEFAULT_BUSNAME,
                      help="Name of the bus on the services listen. [default: %default]")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    logger.info('*****************************************')
    logger.info('Started IngestJobManager')
    logger.info('*****************************************')

    manager = IngestJobManager(exchange=options.exchange,
                               jobs_dir=options.jobs_dir,
                               max_num_retries=options.max_num_retries,
                               broker=options.broker)
    manager.run()

if __name__ == '__main__':
    main()

__all__ = ["IngestJobManager", "main"]
