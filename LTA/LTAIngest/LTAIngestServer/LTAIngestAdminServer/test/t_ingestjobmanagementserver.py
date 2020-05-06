#!/usr/bin/env python3

import unittest
import uuid
import datetime
import os, os.path
import tempfile
import shutil
from threading import Thread
import fnmatch
import time
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

from lofar.messaging.messagebus import TemporaryExchange, TemporaryQueue
from lofar.messaging.messages import CommandMessage, EventMessage
from lofar.messaging.messagelogger import MessageLogger

import lofar.lta.ingest.server.config as ingest_config

testname = 'TEST_INGESTJOBMANAGEMENTSERVER_%s' % uuid.uuid1().hex[:6]

with TemporaryExchange(testname+"_bus") as tmp_bus:
    logger.info(tmp_bus.address)

    with TemporaryQueue(testname, exchange=tmp_bus.address, routing_key="%s.#" % ingest_config.DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT) as tmp_job_queue, \
         MessageLogger(exchange=tmp_bus.address, remove_content_newlines=True): # use messagelogger to log what is sent over the bus for reference.

        ingest_config.JOBS_DIR = os.path.join(tempfile.gettempdir(), testname, 'jobs')
        ingest_config.FINISHED_NOTIFICATION_MAILING_LIST = ''
        ingest_config.MAX_NR_OF_RETRIES = 3

        from lofar.lta.ingest.server.ingestjobmanagementserver import IngestJobManager
        from lofar.lta.ingest.common.job import *

        manager = None
        manager_thread = None
        exit_code = 0

        try:
            # create some 'to do' job files for group 999999999
            for i in range(3):
                testfile_path = os.path.join(ingest_config.JOBS_DIR, 'to_do', 'testjob_%s.xml' % i)
                logger.info('creating test jobfile: %s', testfile_path)
                createJobXmlFile(testfile_path, 'test-project', 999999999, 888888888, 'L888888888_SB00%s_uv.MS'%i, 777777777+i, 'somehost:/path/to/dp')
                time.sleep(0.1) # need to sleep so the files have different timestamps and are read from old to new

            # create some 'failed/done' job files for another group 666666666
            # these will not be transfered, but are just sitting there, and should not interfere (which is what we'll test)
            for i in range(4):
                testfile_path = os.path.join(ingest_config.JOBS_DIR,
                                             'failed' if i%2==0 else 'done',
                                             'MoM_666666666',
                                             'testjob_%s.xml' % i)
                logger.info('creating test jobfile: %s', testfile_path)
                createJobXmlFile(testfile_path, 'test-project', 666666666, 555555555, 'L888888888_SB00%s_uv.MS'%i, 444444444+i, 'somehost:/path/to/dp')
                time.sleep(0.1) # need to sleep so the files have different timestamps and are read from old to new

            with tmp_job_queue.create_frombus() as test_consumer, tmp_bus.create_tobus() as test_notifier:

                def sendNotification(event, job_id, message=None, percentage_done=None, export_id=None):
                    content = { 'job_id': job_id }
                    if message:
                        content['message'] = message
                    if percentage_done:
                        content['percentage_done'] = percentage_done
                    if export_id:
                        content['export_id'] = export_id
                    event_msg = EventMessage(subject="%s.%s" % (ingest_config.INGEST_NOTIFICATION_PREFIX, event),
                                             content=content)
                    logger.info('sending test event message on %s subject=%s content=%s',
                                test_notifier.exchange, event_msg.subject, event_msg.content)
                    test_notifier.send(event_msg)

                def receiveJobForTransfer():
                    msg = test_consumer.receive(timeout=1)

                    if msg and isinstance(msg, CommandMessage):
                        job = parseJobXml(msg.content)
                        if job and job.get('JobId'):
                            logger.info("test consumer (stub-ingesttransferservcer) received job on queue: %s", job)
                        return job
                    return None

                def sendJobFileToManager(jobfile_path):
                    try:
                        with tmp_bus.create_tobus() as bus:
                            with open(jobfile_path) as file:
                                file_content = file.read()
                                msg = CommandMessage(content=file_content, subject=ingest_config.DEFAULT_INGEST_INCOMING_JOB_SUBJECT)
                                bus.send(msg)
                                logger.info('submitted jobfile %s to exchange %s', jobfile_path, bus.exchange)
                    except Exception as e:
                        logger.error('sendJobFileToManager error: %s', e)


                # by starting the job manager, all job files in the non-finished dirs will be scanned and picked up.
                manager = IngestJobManager(exchange=tmp_bus.address)
                manager_thread = Thread(target=manager.run)
                manager_thread.daemon = True
                manager_thread.start()

                assert manager.nrOfUnfinishedJobs() == 3, 'expected 3 jobs unfinished before any job was started'
                assert manager.nrOfJobs() == 3, 'expected 3 jobs in total before any job was started'

                #mimick receiving and transferring of jobs
                #check the status of the manager for correctness
                job1 = receiveJobForTransfer()
                logger.info("jobs: %s", job1)

                assert job1['JobId'] == 'A_999999999_777777777_L888888888_SB000_uv.MS', 'unexpected job %s' % job1['JobId']
                sendNotification('JobStarted', job1['JobId'], export_id=job1['job_group_id'])
                time.sleep(1.0) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 3, 'expected 3 jobs unfinished after 1st job was started'

                sendNotification('JobProgress', job1['JobId'], percentage_done=25, export_id=job1['job_group_id'])
                time.sleep(1.0) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 3, 'expected 3 jobs unfinished after 1st job made progress'

                #just finish normally
                sendNotification('JobFinished', job1['JobId'], export_id=job1['job_group_id'])

                time.sleep(1.0) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'


                #2nd job will fail one transfer before completing
                job2 = receiveJobForTransfer()
                assert job2['JobId'] == 'A_999999999_777777778_L888888888_SB001_uv.MS', 'unexpected job %s' % job2['JobId']
                sendNotification('JobStarted', job2['JobId'], export_id=job2['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[0] == 1'

                # let job2 fail
                sendNotification('JobTransferFailed', job2['JobId'], message='something went wrong (intentionally for this test)', export_id=job2['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'

                #the 2nd job failed, so did not finish, and will be retried later
                #the next received job should be the 3rd job
                job3 = receiveJobForTransfer()
                assert job3['JobId'] == 'A_999999999_777777779_L888888888_SB002_uv.MS', 'unexpected job %s' % job3['JobId']
                sendNotification('JobStarted', job3['JobId'], export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'


                #3rd job will fail all the time
                sendNotification('JobTransferFailed', job3['JobId'], message='something went wrong (intentionally for this test)', export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'


                #receive again, 2nd and 3rd job are going to be retried
                #this should be the 2nd job
                job2 = receiveJobForTransfer()
                assert job2['JobId'] == 'A_999999999_777777778_L888888888_SB001_uv.MS', 'unexpected job %s' % job2['JobId']
                sendNotification('JobStarted', job2['JobId'], export_id=job2['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #keep job2 running while we process job3
                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'
                assert 1 == report['series']['running_jobs']['values'][6], 'expected running jobs series[6] == 1'


                #only 3rd job is unfinished, and job2 is running
                job3 = receiveJobForTransfer()
                assert job3['JobId'] == 'A_999999999_777777779_L888888888_SB002_uv.MS', 'unexpected job %s' % job3['JobId']
                sendNotification('JobStarted', job3['JobId'], export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'
                assert 1 == report['series']['running_jobs']['values'][6], 'expected running jobs series[6] == 1'
                assert 2 == report['series']['running_jobs']['values'][7], 'expected running jobs series[7] == 2'

                #3rd job will fail again
                sendNotification('JobTransferFailed', job3['JobId'], message='something went wrong (intentionally for this test)', export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 2, 'expected 2 jobs unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 1 == report['jobs']['finished'], 'expected 1 job finished'
                assert 1 == len(report['series']['finished_jobs']['values']), 'expected 1 job in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'
                assert 1 == report['series']['running_jobs']['values'][6], 'expected running jobs series[6] == 1'
                assert 2 == report['series']['running_jobs']['values'][7], 'expected running jobs series[7] == 2'
                assert 1 == report['series']['running_jobs']['values'][8], 'expected running jobs series[8] == 1'


                # in the mean time, finish job2 normally
                sendNotification('JobFinished', job2['JobId'], export_id=job2['job_group_id'])

                #one job to go
                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 1, 'expected 1 job unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 2 == report['jobs']['finished'], 'expected 2 jobs finished'
                assert 2 == len(report['series']['finished_jobs']['values']), 'expected 2 jobs in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 2 == report['series']['finished_jobs']['values'][1], 'expected finished jobs series[1] == 2'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'
                assert 1 == report['series']['running_jobs']['values'][6], 'expected running jobs series[6] == 1'
                assert 2 == report['series']['running_jobs']['values'][7], 'expected running jobs series[7] == 2'
                assert 1 == report['series']['running_jobs']['values'][8], 'expected running jobs series[8] == 1'
                assert 0 == report['series']['running_jobs']['values'][9], 'expected running jobs series[9] == 0'


                #still 3rd job is still unfinished, final retry
                job3 = receiveJobForTransfer()
                assert job3['JobId'] == 'A_999999999_777777779_L888888888_SB002_uv.MS', 'unexpected job %s' % job3['JobId']
                sendNotification('JobStarted', job3['JobId'], export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 1, 'expected 1 job unfinished'

                #check report
                report = manager.getStatusReportDict()[999999999]
                assert 2 == report['jobs']['finished'], 'expected 2 jobs finished'
                assert 2 == len(report['series']['finished_jobs']['values']), 'expected 2 jobs in finished jobs series'
                assert 1 == report['series']['finished_jobs']['values'][0], 'expected finished jobs series[0] == 1'
                assert 2 == report['series']['finished_jobs']['values'][1], 'expected finished jobs series[1] == 2'
                assert 1 == report['series']['running_jobs']['values'][0], 'expected running jobs series[0] == 1'
                assert 0 == report['series']['running_jobs']['values'][1], 'expected running jobs series[1] == 0'
                assert 1 == report['series']['running_jobs']['values'][2], 'expected running jobs series[2] == 1'
                assert 0 == report['series']['running_jobs']['values'][3], 'expected running jobs series[3] == 0'
                assert 1 == report['series']['running_jobs']['values'][4], 'expected running jobs series[4] == 1'
                assert 0 == report['series']['running_jobs']['values'][5], 'expected running jobs series[5] == 0'
                assert 1 == report['series']['running_jobs']['values'][6], 'expected running jobs series[6] == 1'
                assert 2 == report['series']['running_jobs']['values'][7], 'expected running jobs series[7] == 2'
                assert 1 == report['series']['running_jobs']['values'][8], 'expected running jobs series[8] == 1'
                assert 0 == report['series']['running_jobs']['values'][9], 'expected running jobs series[9] == 0'
                assert 1 == report['series']['running_jobs']['values'][10], 'expected running jobs series[10] == 1'

                #3rd job will fail again
                sendNotification('JobTransferFailed', job3['JobId'], message='something went wrong (intentionally for this test)', export_id=job3['job_group_id'])

                #3rd job should have failed after 3 retries
                #no more jobs to go
                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout
                assert manager.nrOfUnfinishedJobs() == 0, 'expected 0 jobs unfinished'

                #there should be no more reports, cause the job group 999999999 is finished as a whole
                #and is removed from the manager at this point
                reports = manager.getStatusReportDict()
                assert 0 == len(reports), 'expected 0 reports'
                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout

                jobgroup_999999999_failed_dir = os.path.join(ingest_config.JOBS_DIR, 'failed', 'MoM_999999999')
                failed_jobgroup_999999999_files = [os.path.join(jobgroup_999999999_failed_dir, f) for f in
                                                   os.listdir(jobgroup_999999999_failed_dir)
                                                   if fnmatch.fnmatch(f, '*_999999999_*.xml*')]

                assert 1 == len(failed_jobgroup_999999999_files), '1 and only 1 failed file expected for job_group 999999999'
                for file in failed_jobgroup_999999999_files:
                    sendJobFileToManager(file)

                time.sleep(1.0)

                assert manager.nrOfUnfinishedJobs() == 1, 'expected 1 jobs unfinished'
                assert manager.nrOfJobs() == 3, 'expected 3 jobs' #1 to_do/scheduled, 2 done
                assert len(manager.getJobAdminDicts(status=JobToDo) + manager.getJobAdminDicts(status=JobScheduled)) == 1, 'expected 1 todo/scheduled jobs'
                assert len(manager.getJobAdminDicts(status=JobProduced)) == 2, 'expected 2 done jobs'

                # this time, start and finish job3 normally
                job3 = receiveJobForTransfer()
                assert job3['JobId'] == 'A_999999999_777777779_L888888888_SB002_uv.MS', 'unexpected job %s' % job3['JobId']
                sendNotification('JobStarted', job3['JobId'], export_id=job3['job_group_id'])
                sendNotification('JobFinished', job3['JobId'], export_id=job3['job_group_id'])

                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout

                #there should be no more reports, cause the job group 999999999 is finished as a whole
                #and is removed from the manager at this point
                reports = manager.getStatusReportDict()
                assert 0 == len(reports), 'expected 0 reports'
                assert manager.nrOfUnfinishedJobs() == 0, 'expected 0 jobs unfinished'
                time.sleep(1.5) #TODO: should not wait fixed amount of time, but poll for expected output with a timeout

                manager.quit()
                manager_thread.join()

        except Exception as e:
            logger.exception(e)
            exit_code = 1
        finally:
            if manager:
                manager.quit()
                manager_thread.join()

            if os.path.exists(ingest_config.JOBS_DIR):
                shutil.rmtree(ingest_config.JOBS_DIR)

exit(exit_code)
