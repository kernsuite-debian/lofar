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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#

"""
"""

import logging
from datetime import datetime, timedelta
import os
import time
import socket
import getpass
import pprint
from threading import Thread, Lock
from lofar.messaging import ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME, BusListener, AbstractMessageHandler
from lofar.messaging import LofarMessage, CommandMessage, EventMessage
from lofar.common import isProductionEnvironment
from lofar.common import dbcredentials
from lofar.common.datetimeutils import totalSeconds
from lofar.common.util import humanreadablesize
from lofar.lta.ingest.server.config import DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT, INGEST_NOTIFICATION_PREFIX
from lofar.lta.ingest.server.config import MAX_NR_OF_JOBS, MAX_USED_BANDWITH_TO_START_NEW_JOBS, NET_IF_TO_MONITOR
from lofar.lta.ingest.server.config import TRANSFER_TIMEOUT
from lofar.lta.ingest.common.job import *
from lofar.lta.ingest.server.ingestpipeline import IngestPipeline
from lofar.lta.ingest.client.rpc import IngestRPC
from lofar.lta.ingest.server.ltaclient import *
from lofar.lta.ingest.server.momclient import *
import psutil

logger = logging.getLogger(__name__)

def _getBytesSent():
    try:
        # try to sum the summed traffic of all interfaces in NET_IF_TO_MONITOR
        counters = psutil.net_io_counters(True)
        if all(interface in counters for interface in NET_IF_TO_MONITOR):
            return sum(counters[interface].bytes_sent for interface in NET_IF_TO_MONITOR)

        # not all interfaces found... return total bytes_sent
        return psutil.net_io_counters(False).bytes_sent
    except Exception as e:
        logger.warning("Cannot get network interface info: %s", e)
        return 0

class IngestTransferServer:
    def __init__(self,
                 exchange = DEFAULT_BUSNAME,
                 mom_credentials = None,
                 lta_credentials = None,
                 user = None,
                 broker = None,
                 max_nr_of_parallel_jobs = MAX_NR_OF_JOBS):
        self.user = user
        if not self.user:
            self.user = getpass.getuser()

        self.mom_credentials = mom_credentials
        self.lta_credentials = lta_credentials
        self.event_bus = ToBus(exchange=exchange, broker = broker)
        self.max_nr_of_parallel_jobs = max_nr_of_parallel_jobs

        self.__running_jobs = {}
        self.__lock = Lock()
        self.__prev_bytes_sent = _getBytesSent()
        self.__prev_bytes_sent_timestamp = datetime.utcnow()
        self.__prev_used_bandwidth = 0.0
        self.__running_jobs_log_timestamp = datetime.utcnow()

    def start_job(self, job_dict):
        if not self.enoughResourcesAvailable():
            raise ResourceWarning("Not enough resources available to start new job: %s" % job_dict)

        job_id = job_dict['JobId']

        if job_id in self.__running_jobs:
            raise ValueError('job %s is already running. Discarding this new job copy, and keeping the current one running...' % job_id)

        def threaded_pipeline_func(job):
            logger.info('starting job %s in the background', job_id)
            with LTAClient(self.lta_credentials.user, self.lta_credentials.password) as ltaClient, \
                 MoMClient(self.mom_credentials.user, self.mom_credentials.password) as momClient:
                jobPipeline = IngestPipeline(job, momClient, ltaClient,
                                             exchange = self.event_bus.exchange,
                                             broker = self.event_bus.broker,
                                             user = self.user)
                with self.__lock:
                    self.__running_jobs[job_id]['pipeline'] = jobPipeline

                jobPipeline.run()

        with self.__lock:
            thread = Thread(target = threaded_pipeline_func,
                            args = [job_dict],
                            name="transfer_thread_%s"%(job_id,))
            thread.daemon = True
            self.__running_jobs[job_id] = { 'thread':thread }
            thread.start()

    def __clearFinishedJobs(self):
        try:
            with self.__lock:
                finished_job_ids = [job_id for job_id, job_thread_dict in list(self.__running_jobs.items()) if not job_thread_dict['thread'].is_alive()]

                for job_id in finished_job_ids:
                    logger.info('removing finished job %s', job_id)
                    del self.__running_jobs[job_id]
        except Exception as e:
            logger.error('__clearFinishedJobs: %s', e)

    def enoughResourcesAvailable(self):
        try:
            now = datetime.utcnow()
            bytes_sent = _getBytesSent()

            if bytes_sent >= self.__prev_bytes_sent:    # bytes_sent might wrap around zero
                # compute current speed in Gbps
                speed = 8 * (bytes_sent - self.__prev_bytes_sent) / totalSeconds(now - self.__prev_bytes_sent_timestamp)

                # running average for used_bandwidth
                used_bandwidth = 0.5 * speed + 0.5 * self.__prev_used_bandwidth

                logger.debug("resources: current used_bandwidth = %s", humanreadablesize(used_bandwidth, 'bps'))

                # store for next iteration
                self.__prev_bytes_sent = bytes_sent
                self.__prev_bytes_sent_timestamp = now
                self.__prev_used_bandwidth = used_bandwidth

                # only start new jobs if we have some bandwith available
                # note that this is a 'soft' limit.
                # we cannot control the actual bandwith used by the running transfers
                # we can only not start new jobs if we already exceed the MAX_USED_BANDWITH_TO_START_NEW_JOBS
                if used_bandwidth > MAX_USED_BANDWITH_TO_START_NEW_JOBS:
                    logger.warning('resources: not enough bandwith available to start new jobs, using %s, max %s' %
                                         (humanreadablesize(used_bandwidth, 'bps'),
                                          humanreadablesize(MAX_USED_BANDWITH_TO_START_NEW_JOBS, 'bps')))
                    return False
            else:
                # wrapped around 0, just store for next iteration, do not compute anything
                self.__prev_bytes_sent = bytes_sent
                self.__prev_bytes_sent_timestamp = now

            # only start new jobs if we have some cpu time available
            idle_cpu_percentage = psutil.cpu_times_percent().idle
            logger.debug("resources: current idle_cpu_percentage = %s%%", idle_cpu_percentage)
            if idle_cpu_percentage < 5:
                logger.warning('resources: not enough cpu power available to start new jobs, cpu_idle %s%%' %
                                     idle_cpu_percentage)
                return False

            # only start new jobs if system load is not too high
            short_load_avg = os.getloadavg()[0]
            cpu_count = psutil.cpu_count()
            allowed_load = 1.5 * cpu_count
            logger.debug("resources: current short term load = %s #cpu's = %s allowed_load = %s", short_load_avg, cpu_count, allowed_load)
            if short_load_avg > allowed_load:
                logger.warning('resources: system load too high (%s > %s), cannot start new jobs' %
                                     (short_load_avg,
                                      allowed_load))
                return False

            # only allow 1 job at the time if swapping
            swap_memory_percentage = psutil.swap_memory().percent
            logger.debug("resources: current swap_memory_percentage = %s%%", swap_memory_percentage)
            if swap_memory_percentage > 5 and len(self.__running_jobs) > 0:
                logger.warning('resources: system swapping. not enough memory available to start new jobs')
                return False

            # only start new jobs if number of processes is not too high
            try:
                current_user = getpass.getuser()
                current_user_procs = [p for p in psutil.process_iter() if p.username() == current_user]
                current_num_user_procs = len(current_user_procs)
                allowed_num_user_procs = 64 * cpu_count

                logger.debug("resources: current num_user_procs = %s allowed_num_user_procs = %s", current_num_user_procs, allowed_num_user_procs)

                if current_num_user_procs > allowed_num_user_procs:
                    logger.warning('resources: number of processes by %s too high (%s > %s), cannot start new jobs' %
                                        (current_user,
                                        current_num_user_procs,
                                        allowed_num_user_procs))
                    return False
            except Exception as e:
                logger.exception(e)
                pass

            # limit total number of parallel transferring jobs to self.max_nr_of_parallel_jobs
            with self.__lock:
                starting_threads = [job_thread_dict['thread'] for job_thread_dict in list(self.__running_jobs.values()) if 'pipeline' not in job_thread_dict]
                pipelines = [job_thread_dict['pipeline'] for job_thread_dict in list(self.__running_jobs.values()) if 'pipeline' in job_thread_dict]
                initializing_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_INITIALIZING]
                transferring_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_TRANSFERRING]
                finalizing_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_FINALIZING]

                num_busy_transfers = len(starting_threads) + len(initializing_pipelines) + len(transferring_pipelines)
                num_finalizing_transfers = len(finalizing_pipelines)

                logger.debug("resources: current num_busy_transfers = %s num_finalizing_transfers = %s max_nr_of_parallel_jobs = %s",
                             num_busy_transfers, num_finalizing_transfers, self.max_nr_of_parallel_jobs)

                if num_busy_transfers >= self.max_nr_of_parallel_jobs:
                    logger.warning('resources: already running %d parallel jobs (#starting=%d, #transferring=%d) limiting the total number of transferring jobs to %d' %
                                        (len(self.__running_jobs),
                                         len(initializing_pipelines) + len(starting_threads),
                                         len(transferring_pipelines),
                                         self.max_nr_of_parallel_jobs))
                    return False

                if num_finalizing_transfers >= 2 * self.max_nr_of_parallel_jobs:
                    logger.warning('resources: already waiting for %d jobs to finish (updating status/SIP to MoM and LTA). not starting new jobs until some jobs finished...' %
                                        (len(finalizing_pipelines),))
                    return False

        except Exception as e:
            logger.exception("error while checking for available resources: %s", e)

            num_running_jobs = len(self.__running_jobs)
            if num_running_jobs <= 4:
                logger.info("running %d jobs, assuming we can run 1 more: ", num_running_jobs)
                return True
            else:
                logger.warning("already running %d jobs, assuming for safety we cannot run more jobs...", num_running_jobs)
                return False

        return True

    def run(self):
        with self.event_bus:
            while True:
                try:
                    self.__clearFinishedJobs()

                    with self.__lock:
                        starting_threads = [job_thread_dict['thread'] for job_thread_dict in list(self.__running_jobs.values()) if 'pipeline' not in job_thread_dict]
                        pipelines = [job_thread_dict['pipeline'] for job_thread_dict in list(self.__running_jobs.values()) if 'pipeline' in job_thread_dict]
                        initializing_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_INITIALIZING]
                        transferring_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_TRANSFERRING]
                        finalizing_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_FINALIZING]
                        finished_pipelines = [pipeline for pipeline in pipelines if pipeline.status == IngestPipeline.STATUS_FINISHED]
                        log_interval = 5 if self.__running_jobs else 60

                    if datetime.utcnow() - self.__running_jobs_log_timestamp > timedelta(seconds=log_interval):
                        status_log_line = "status: running %s jobs: #starting=%d, #transferring=%d, #finalizing=%d, #finished=%d, bandwith used on network interface(s) %s %s (%s), load=%.1f" % (len(self.__running_jobs),
                               len(initializing_pipelines) + len(starting_threads),
                               len(transferring_pipelines),
                               len(finalizing_pipelines),
                               len(finished_pipelines),
                               NET_IF_TO_MONITOR,
                               humanreadablesize(self.__prev_used_bandwidth, 'bps'),
                               humanreadablesize(self.__prev_used_bandwidth / 8, 'Bps'),
                               os.getloadavg()[0])

                        logger.info(status_log_line)
                        self.__running_jobs_log_timestamp = datetime.utcnow()

                        msg = EventMessage(subject = "%s.%s" % (INGEST_NOTIFICATION_PREFIX, 'TransferServiceStatus'),
                                            content = { 'ingest_server': socket.gethostname(),
                                                        'message' : status_log_line })
                        msg.ttl = 3600    # remove message from queue's when not picked up within 1 hours
                        self.event_bus.send(msg)

                    time.sleep(5)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(e)

class IngestJobsForTransferHandler(AbstractMessageHandler):
    def __init__(self, transfer_server: IngestTransferServer):
        self._transfer_server = transfer_server
        super(IngestJobsForTransferHandler, self).__init__()

    def before_receive_message(self):
        while not self._transfer_server.enoughResourcesAvailable():
            logger.info("Waiting for resources to become available before receiving a new job...")
            time.sleep(10)

    def handle_message(self, msg: LofarMessage):
        if not isinstance(msg, CommandMessage):
            raise ValueError("%s: Ignoring non-CommandMessage: %s" % (self.__class__.__name__, msg))

        job = parseJobXml(msg.content)
        if job and job.get('JobId'):
            logger.info("received job from bus: %s", job)
            self._transfer_server.start_job(job)

            # sleep a little
            # so jobs have a little time to start consuming resources
            # this limits the numer of jobs that can be started to 1000 starts per minute
            # it does not limit the total number of parallel jobs
            # that is limited dynamically by enoughResourcesAvailable
            # and by the hard limit self.max_nr_of_parallel_jobs
            time.sleep(0.1)


def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser("%prog [options]",
                          description = 'runs the ingest transfer server which picks up as many jobs as it can handle from the given --ingest_job_queuename and tranfers the dataproducts to the LTA, updates the LTA catalogue, and updates MoM')
    parser.add_option('-b', '--broker', dest = 'broker', type = 'string',
                      default = DEFAULT_BROKER,
                      help = 'Address of the qpid broker, default: %default')
    parser.add_option("-p", "--max_nr_of_parallel_jobs", dest = "max_nr_of_parallel_jobs", type = "int",
                      default = MAX_NR_OF_JOBS,
                      help = "Name of the job queue. [default: %default]")
    parser.add_option('-e', '--exchange', dest = 'exchange', type = 'string', default = DEFAULT_BUSNAME, help = 'Name of the common bus exchange on the broker, default: %default')
    parser.add_option("-u", "--user", dest = "user", type = "string", default = getpass.getuser(), help = "username for to login on data source host, [default: %default]")
    parser.add_option("-l", "--lta_credentials", dest = "lta_credentials", type = "string",
                      default = 'LTA' if isProductionEnvironment() else 'LTA_test',
                      help = "Name of lofar credentials for lta user/pass (see ~/.lofar/dbcredentials) [default=%default]")
    parser.add_option("-m", "--mom_credentials", dest = "mom_credentials", type = "string",
                      default = 'MoM_site' if isProductionEnvironment() else 'MoM_site_test',
                      help = "Name of credentials for MoM user/pass (see ~/.lofar/dbcredentials) [default=%default]")
    parser.add_option('-V', '--verbose', dest = 'verbose', action = 'store_true', help = 'verbose logging')
    (options, args) = parser.parse_args()

    logging.basicConfig(format = '%(asctime)s %(levelname)s %(message)s',
                        level = logging.DEBUG if options.verbose else logging.INFO)

    logger.info('*****************************************')
    logger.info('Started ingest server on host %s', socket.gethostname())
    logger.info('*****************************************')

    logger.info("environment:")
    for k in sorted(os.environ):
        logger.info("%s=%s", k, os.environ[k])
    logger.info('*****************************************')

    ltacreds = dbcredentials.DBCredentials().get(options.lta_credentials)
    momcreds = dbcredentials.DBCredentials().get(options.mom_credentials)

    transfer_server = IngestTransferServer(exchange = options.exchange,
                                           broker = options.broker,
                                           mom_credentials = momcreds,
                                           lta_credentials = ltacreds,
                                           max_nr_of_parallel_jobs = options.max_nr_of_parallel_jobs)

    incoming_jobs_listener = BusListener(IngestJobsForTransferHandler, {'transfer_server': transfer_server},
                                         exchange=options.exchange, routing_key="%s.#" % DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT)

    with incoming_jobs_listener:
        transfer_server.run()

if __name__ == '__main__':
    main()

__all__ = ['main']
