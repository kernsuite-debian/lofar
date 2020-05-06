#!/usr/bin/env python3
#
# Copyright (C) 2016
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
# $Id$
"""
Daemon that starts/stops pipelines based on their status in OTDB.

The execution chains are as follows:

-----------------------------
  Starting a pipeline
-----------------------------

[SCHEDULED]          -> PipelineControl schedules

                           runPipeline.sh <obsid>

                        and

                           setOTDBTreeStatus -o <obsid> -s aborted

                        using two SLURM jobs, guaranteeing that pipelineAborted.sh is
                        called in the following circumstances:

                          - runPipeline.sh wrapper cannot finish (bash bugs, etc)
                          - runPipeline.sh job is cancelled in the queue

                        State is set to [QUEUED].

(runPipeline.sh)     -> Calls
                          - state <- [ACTIVE]
                          - getParset
                          - (run pipeline)
                          - success:
                              - state <- [COMPLETING]
                              - (wrap up)
                              - state <- [FINISHED]
                          - failure:
                              - state <- [ABORTED]

(setOTDBTreeStatus)  -> Calls
                          - state <- [ABORTED]

-----------------------------
  Stopping a pipeline
-----------------------------

[ABORTED]            -> Cancels SLURM job associated with pipeline, causing
                        a cascade of job terminations of successor pipelines.
"""

from lofar.messaging import DEFAULT_BUSNAME, DEFAULT_BROKER, RPCException
from lofar.parameterset import PyParameterValue
from lofar.sas.otdb.OTDBBusListener import OTDBEventMessageHandler, OTDBBusListener
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.common import isProductionEnvironment
from lofar.common.subprocess_utils import communicate_returning_strings
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.sas.otdb.config import DEFAULT_OTDB_NOTIFICATION_SUBJECT

import subprocess
import pipes
import os
import re
from socket import getfqdn

import logging
logger = logging.getLogger(__name__)

# NDPPP seems to like to have 2 cores.
DEFAULT_NUMBER_OF_CORES_PER_TASK = 2
# This needs to match what's in SLURM
NUMBER_OF_NODES = 40
NUMBER_OF_CORES_PER_NODE = 24
# We /4 because we can then run 4 pipelines, and -2 to reserve cores for TBBwriter
DEFAULT_NUMBER_OF_TASKS = (NUMBER_OF_NODES // 4) * (NUMBER_OF_CORES_PER_NODE - 2) // DEFAULT_NUMBER_OF_CORES_PER_TASK


def runCommand(cmdline, input=None):
    logger.info("runCommand starting: %s", cmdline)

    # Start command
    proc = subprocess.Popen(
        cmdline,
        stdin=subprocess.PIPE if input else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True
    )

    # Feed input and wait for termination
    logger.debug("runCommand input: %s", input)
    stdout, _ = communicate_returning_strings(proc, input)
    logger.debug("runCommand output: %s", stdout)

    # Check exit status, bail on error
    if proc.returncode != 0:
        logger.warning("runCommand(%s) had exit status %s with output: %s", cmdline, proc.returncode, stdout)
        raise subprocess.CalledProcessError(proc.returncode, cmdline)

    # Return output
    return stdout.strip()


""" Prefix that is common to all parset keys, depending on the exact source. """
PARSET_PREFIX="ObsSW."


class Parset(dict):
    def predecessors(self):
        """ Extract the list of predecessor obs IDs from the given parset. """

        key = PARSET_PREFIX + "Observation.Scheduler.predecessors"
        strlist = PyParameterValue(str(self[key]), True).getStringVector()

        # Key contains "Lxxxxx" values, we want to have "xxxxx" only
        result = [int(list(filter(str.isdigit,x))) for x in strlist]

        return result

    def isObservation(self):
        return self[PARSET_PREFIX + "Observation.processType"] == "Observation"

    def isPipeline(self):
        return not self.isObservation()

    def processingCluster(self):
        return self[PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.clusterName"] or "CEP2"

    def processingPartition(self):
        result = self[PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.clusterPartition"] or "cpu"
        if '/' in result:
            logger.error('clusterPartition contains invalid value: %s. Defaulting clusterPartition to \'cpu\'', result)
            return 'cpu'
        return result

    def processingNumberOfCoresPerTask(self):
        result = int(self[PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.numberOfCoresPerTask"]) or None
        if not result:
            logger.warning('Invalid Observation.Cluster.ProcessingCluster.numberOfCoresPerTask: %s, defaulting to %i',
                        result, DEFAULT_NUMBER_OF_CORES_PER_TASK)
            result = DEFAULT_NUMBER_OF_CORES_PER_TASK
        return result

    def processingNumberOfTasks(self):
        """ Parse the number of nodes to allocate from
        "Observation.Cluster.ProcessingCluster.numberOfTasks" """

        result = int(self[PARSET_PREFIX +
                          "Observation.Cluster.ProcessingCluster.numberOfTasks"].strip()) or None

        # apply bound
        if not result or result <= 0 or result > NUMBER_OF_NODES * NUMBER_OF_CORES_PER_NODE:
            logger.warning('Invalid Observation.Cluster.ProcessingCluster.numberOfTasks: %s, defaulting to %s',
                            result, DEFAULT_NUMBER_OF_TASKS)
            result = DEFAULT_NUMBER_OF_TASKS

        return result

    @staticmethod
    def dockerRepository():
        return "nexus.cep4.control.lofar:18080"

    @staticmethod
    def defaultDockerImage():
        return "lofar-pipeline"

    @staticmethod
    def defaultDockerTag():
        if isProductionEnvironment():
            # "latest" refers to the current /production/ image
            return "latest"
        else:
            # test/dev environments want to use their specific version, since they
            # share images with the production environment
            return runCommand("docker-template", "${LOFAR_TAG}")

    def dockerImage(self):
        # Return the version set in the parset, and fall back to our own version.
        image = self[PARSET_PREFIX + "Observation.ObservationControl.PythonControl.softwareVersion"]

        if not image:
            image = self.defaultDockerImage()

        if ":" in image:
            return image

        # Insert our tag by default
        return "%s:%s" % (image, self.defaultDockerTag())

    def otdbId(self):
        return int(self[PARSET_PREFIX + "Observation.otdbID"])

    def description(self):
        return "%s - %s" % (self.get(PARSET_PREFIX + "Observation.Campaign.name", 'unknown'),
                            self.get(PARSET_PREFIX + "Observation.Scheduler.taskName", 'unknown'))
    

class Slurm(object):
    def __init__(self, headnode="head.cep4.control.lofar"):
        self.headnode = headnode

    def _runCommand(self, cmdline, input=None):
        cmdline = "ssh %s %s" % (self.headnode, cmdline)
        return runCommand(cmdline, input)

    def submit(self, jobName, cmdline, sbatch_params=None):
        if sbatch_params is None:
            sbatch_params = []

        script = """#!/bin/bash -v
    {cmdline}
    """.format(cmdline = cmdline)

        stdout = self._runCommand("sbatch --job-name=%s %s" % (jobName, " ".join(sbatch_params)), script)

        # Returns "Submitted batch job 3" -- extract ID
        match = re.search("Submitted batch job (\d+)", stdout)
        if not match:
            return None

        return match.group(1)

    def cancel(self, jobName):
        self._runCommand("scancel --jobname %s" % (jobName,))

    def isQueuedOrRunning(self, jobName):
        stdout = self._runCommand("sacct --starttime=2016-01-01 --noheader --parsable2 --format=jobid --name=%s --state=PENDING,CONFIGURING,RUNNING,RESIZING,COMPLETING,SUSPENDED" % (jobName,))

        return stdout != ""


class PipelineDependencies(object):
    class TaskNotFoundException(Exception):
        """ Raised when a task cannot be found in the RADB. """
        pass

    def __init__(self, exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER):
        self.rarpc = RADBRPC.create(exchange=exchange, broker=broker)
        logger.info('PipelineDependencies busname=%s', exchange)
        self.otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker)

    def open(self):
        self.rarpc.open()
        self.otdbrpc.open()

    def close(self):
        self.rarpc.close()
        self.otdbrpc.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def getState(self, otdb_id):
        """
          Return the status of a single `otdb_id'.
        """
        return self.otdbrpc.taskGetStatus(otdb_id=otdb_id)

    def getPredecessorStates(self, otdb_id):
        """
          Return a dict of {"sasid":"status"} pairs of all the predecessors of `otdb_id'.
        """
        radb_task = self.rarpc.getTask(otdb_id=otdb_id)

        if radb_task is None:
            raise PipelineDependencies.TaskNotFoundException("otdb_id %s not found in RADB" % (otdb_id,))

        predecessor_radb_ids = radb_task['predecessor_ids']
        predecessor_tasks = self.rarpc.getTasks(task_ids=predecessor_radb_ids)

        #get states from otdb in order to prevent race conditions between states in radb/otdb
        predecessor_otdb_ids = [t["otdb_id"] for t in predecessor_tasks]
        predecessor_states = { otdb_id:self.getState(otdb_id) for otdb_id in predecessor_otdb_ids }

        logger.debug("getPredecessorStates(%s) = %s", otdb_id, predecessor_states)

        return predecessor_states

    def getSuccessorIds(self, otdb_id):
        """
          Return a list of all the successors of `otdb_id'.
        """
        radb_task = self.rarpc.getTask(otdb_id=otdb_id)

        if radb_task is None:
            raise PipelineDependencies.TaskNotFoundException("otdb_id %s not found in RADB" % (otdb_id,))

        successor_radb_ids = radb_task['successor_ids']
        successor_tasks = self.rarpc.getTasks(task_ids=successor_radb_ids) if successor_radb_ids else []
        successor_otdb_ids = [t["otdb_id"] for t in successor_tasks]

        logger.debug("getSuccessorIds(%s) = %s", otdb_id, successor_otdb_ids)

        return successor_otdb_ids

    def canStart(self, otdbId):
        """
          Return whether `otdbId' can start, according to the status of the predecessors
          and its own status.
        """

        try:
            myState = self.getState(otdbId)
            predecessorStates = self.getPredecessorStates(otdbId)
        except PipelineDependencies.TaskNotFoundException as e:
            logger.error("canStart(%s): Error obtaining task states, not starting pipeline: %s", otdbId, e)
            return False

        startable = (myState == "scheduled" and all([x == "finished" for x in list(predecessorStates.values())]))
        logger.info("canStart(%s)? state = %s, predecessors = %s, canStart = %s", otdbId, myState, predecessorStates, startable)
        return startable

    def getTasks(self, task_status, task_type):
        return self.rarpc.getTasks(task_status=task_status, task_type=task_type)


class PipelineControlHandler( OTDBEventMessageHandler):
    def __init__(self, exchange, broker):
        super(PipelineControlHandler, self).__init__()

        logger.info('PipelineControl busname=%s', exchange)
        self.exchange = exchange
        self.otdbrpc = OTDBRPC.create(exchange=exchange, broker=broker)
        self.dependencies = PipelineDependencies(exchange=exchange, broker=broker)
        self.slurm = Slurm()

    def _setStatus(self, otdb_id, status):
        self.otdbrpc.taskSetStatus(otdb_id=otdb_id, new_status=status)

    def _getParset(self, otdbId):
        try:
            return Parset(self.otdbrpc.taskGetSpecification(otdb_id=otdbId)["specification"])
        except RPCException as e:
            # Parset not in OTDB, probably got deleted
            logger.error("Cannot retrieve parset of task %s: %s", otdbId, e)
            return None

    def start_handling(self):
        self.otdbrpc.open()
        self.dependencies.open()

        super(PipelineControlHandler, self).start_handling()

    def stop_handling(self):
        super(PipelineControlHandler, self).stop_handling()

        self.dependencies.close()
        self.otdbrpc.close()

    def check_scheduled_pipelines(self):
        try:
            logger.info("Checking for already scheduled pipelines...")

            scheduled_pipelines = self.dependencies.getTasks(task_status='scheduled',
                                                             task_type='pipeline')
            logger.info("Checking %s scheduled pipelines if they can start.",
                        len(scheduled_pipelines))

            for pipeline in scheduled_pipelines:
                logger.info("Checking if scheduled pipeline otdbId=%s can start.",
                            pipeline['otdb_id'])
                try:
                    otdbId = pipeline['otdb_id']
                    parset = self._getParset(otdbId)
                    if not parset or not self._shouldHandle(parset):
                        continue

                    # Maybe the pipeline can start already
                    if self.dependencies.canStart(otdbId):
                        self._startPipeline(otdbId, parset)
                    else:
                        logger.info("Job %s was set to scheduled, but cannot start yet.", otdbId)
                except Exception as e:
                  logger.error(e)
        except Exception as e:
          logger.error(e)

        logger.info("...finished checking for already scheduled pipelines.")

    @staticmethod
    def _shouldHandle(parset):
        try:
            if not parset.isPipeline():
                logger.info("Not processing tree: is not a pipeline")
                return False

            if parset.processingCluster() == "CEP2":
                logger.info("Not processing tree: is a CEP2 pipeline")
                return False
        except KeyError as e:
            # Parset not complete
            logger.error("Parset incomplete, ignoring: %s", e)
            return False

        return True

    @staticmethod
    def _jobName(otdbId):
        return str(otdbId)

    def _startPipeline(self, otdbId, parset):
        """
          Schedule "docker-runPipeline.sh", which will fetch the parset and run the pipeline within
          a SLURM job.
        """

        # Avoid race conditions by checking whether we haven't already sent the job
        # to SLURM. Our QUEUED status update may still be being processed.
        if self.slurm.isQueuedOrRunning(otdbId):
            logger.info("Pipeline %s is already queued or running in SLURM.", otdbId)
            return

        logger.info("***** START Otdb ID %s *****", otdbId)

        # Determine SLURM parameters
        sbatch_params = [
                         # Only run job if all nodes are ready
                         "--wait-all-nodes=1",

                         # Enforce the dependencies, instead of creating lingering jobs
                         "--kill-on-invalid-dep=yes",

                         # Annotate the job
                         "--comment=%s" % pipes.quote(pipes.quote(parset.description())),

                         # Lower priority to drop below inspection plots
                         "--nice=1000",

                         "--partition=%s" % parset.processingPartition(),
                         "--ntasks=%s" % parset.processingNumberOfTasks(),
                         "--cpus-per-task=%s" % parset.processingNumberOfCoresPerTask(),

                         # Define better places to write the output
                         os.path.expandvars("--output=/data/log/pipeline-%s-%%j.log" % (otdbId,)),
                         ]

        def setStatus_cmdline(status):
            return (
            "ssh {myhostname} '"
            "source {lofarroot}/lofarinit.sh && "
            "setOTDBTreeStatus -o {obsid} -s {status} -B {busname}"
            "'"
            .format(
            myhostname = getfqdn(),
            lofarroot = os.environ.get("LOFARROOT", ""),
            obsid = otdbId,
            status = status,
            busname = self.exchange,
            ))

        def getParset_cmdline():
            return (
            "ssh {myhostname} '"
            "source {lofarroot}/lofarinit.sh && "
            "getOTDBParset -o {obsid}'"
            .format(
            myhostname = getfqdn(),
            lofarroot = os.environ.get("LOFARROOT", ""),
            obsid = otdbId,
            ))


        try:
            logger.info("Handing over pipeline %s to SLURM", otdbId)

            # Schedule runPipeline.sh
            slurm_job_id = self.slurm.submit(self._jobName(otdbId),
            """
    # Run a command, but propagate SIGINT and SIGTERM
    function runcmd {{
    trap 'kill -s SIGTERM $PID' SIGTERM
    trap 'kill -s SIGINT  $PID' SIGINT
    
    "$@" &
    PID=$!
    wait $PID # returns the exit status of "wait" if interrupted
    wait $PID # returns the exit status of $PID
    CMDRESULT=$?
    
    trap - SIGTERM SIGINT
    
    return $CMDRESULT
    }}
    
    # print some info
    echo Running on $SLURM_NODELIST
    
    # notify OTDB that we're running
    runcmd {setStatus_active}
    
    # notify ganglia
    wget -O - -q "http://ganglia.control.lofar/ganglia/api/events.php?action=add&start_time=now&summary=Pipeline {obsid} ACTIVE&host_regex="

    # fetch parset
    runcmd {getParset} > {parset_file}
    
    # run the pipeline
    runcmd docker-run-slurm.sh --rm --net=host \
        -e LOFARENV={lofarenv} \
        -v $HOME/.ssh:$HOME/.ssh:ro \
        -e SLURM_JOB_ID=$SLURM_JOB_ID \
        -v /data:/data \
        {image} \
    runPipeline.sh -o {obsid} -c /opt/lofar/share/pipeline/pipeline.cfg.{cluster} -P {parset_dir} -p {parset_file}
    RESULT=$?
    
    # notify that we're tearing down
    runcmd {setStatus_completing}
    
    if [ $RESULT -eq 0 ]; then
        # wait for MoM to pick up feedback before we set finished status
        # AS: I increased this to 300 sec to be in line with the wait time after observation finished
        # and because we still note quite a lot of feedback issues in MoM
        runcmd sleep 300
    
        # if we reached this point, the pipeline ran succesfully
        runcmd {setStatus_finished}
    
        # notify ganglia
        wget -O - -q "http://ganglia.control.lofar/ganglia/api/events.php?action=add&start_time=now&summary=Pipeline {obsid} FINISHED&host_regex="
    else
        # If we are killed by the pipeline being set to aborted, we just went from aborted->completing
        # but our abort_trigger may already have been cancelled. Set the status here too to avoid lingering
        # in completing
        runcmd {setStatus_aborted}
    fi
    
    # report status back to SLURM
    echo "Pipeline exited with status $RESULT"
    exit $RESULT
        """.format(
                lofarenv = os.environ.get("LOFARENV", ""),
                obsid = otdbId,
                parset_dir = "/data/parsets",
                parset_file = "/data/parsets/Observation%s.parset" % (otdbId,),
                repository = parset.dockerRepository(),
                image = parset.dockerImage(),
                cluster = parset.processingCluster(),

                getParset = getParset_cmdline(),
                setStatus_active = setStatus_cmdline("active"),
                setStatus_completing = setStatus_cmdline("completing"),
                setStatus_finished = setStatus_cmdline("finished"),
                setStatus_aborted = setStatus_cmdline("aborted"),
            ),

            sbatch_params=sbatch_params
            )
            logger.info("Scheduled SLURM job %s for otdb_id=%s", slurm_job_id, otdbId)

            # Schedule pipelineAborted.sh
            logger.info("Scheduling SLURM job for pipelineAborted.sh")
            slurm_cancel_job_id = self.slurm.submit("%s-abort-trigger" % self._jobName(otdbId),
        """
    # notify OTDB
    {setStatus_aborted}
    
    # notify ganglia
    wget -O - -q "http://ganglia.control.lofar/ganglia/api/events.php?action=add&start_time=now&summary=Pipeline {obsid} ABORTED&host_regex="
        """
            .format(
                setStatus_aborted = setStatus_cmdline("aborted"),
                obsid = otdbId,
            ),

            sbatch_params=[
                "--partition=%s" % parset.processingPartition(),
                "--cpus-per-task=1",
                "--ntasks=1",
                "--dependency=afternotok:%s" % slurm_job_id,
                "--kill-on-invalid-dep=yes",
                "--requeue",
                "--output=/data/log/abort-trigger-%s.log" % (otdbId,),
            ]
            )
            logger.info("Scheduled SLURM job %s for abort trigger for otdb_id=%s", slurm_cancel_job_id, otdbId)

            logger.info("Handed over pipeline %s to SLURM, setting status to QUEUED", otdbId)
            self._setStatus(otdbId, "queued")
        except Exception as e:
            logger.error(str(e))
            self._setStatus(otdbId, "aborted")

    def _stopPipeline(self, otdbId):
        # Cancel corresponding SLURM job, but first the abort-trigger
        # to avoid setting ABORTED as a side effect.
        # to be cancelled as well.

        if not self.slurm.isQueuedOrRunning(otdbId):
            logger.info("_stopPipeline: Job %s not running", otdbId)
            return

        def cancel(jobName):
            logger.info("Cancelling job %s", jobName)
            self.slurm.cancel(jobName)

        jobName = self._jobName(otdbId)
        cancel("%s-abort-trigger" % jobName)
        cancel(jobName)

    def _startSuccessors(self, otdbId):
        try:
            successor_ids = self.dependencies.getSuccessorIds(otdbId)
        except PipelineDependencies.TaskNotFoundException as e:
            logger.error("_startSuccessors(%s): Error obtaining task successors, not starting them: %s", otdbId, e)
            return

        for s in successor_ids:
            parset = self._getParset(s)
            if not parset or not self._shouldHandle(parset):
                continue

            if self.dependencies.canStart(s):
                self._startPipeline(s, parset)
            else:
                logger.info("Job %s still cannot start yet.", otdbId)

    def onObservationScheduled(self, otdbId, modificationTime):
        parset = self._getParset(otdbId)
        if not parset or not self._shouldHandle(parset):
            return

        # Maybe the pipeline can start already
        if self.dependencies.canStart(otdbId):
            self._startPipeline(otdbId, parset)
        else:
            logger.info("Job %s was set to scheduled, but cannot start yet.", otdbId)

    def onObservationFinished(self, otdbId, modificationTime):
        """ Check if any successors can now start. """

        logger.info("Considering to start successors of %s", otdbId)
        self._startSuccessors(otdbId)

    def onObservationAborted(self, otdbId, modificationTime):
        parset = self._getParset(otdbId)
        if parset and not self._shouldHandle(parset): # stop jobs even if there's no parset
          return

        logger.info("***** STOP Otdb ID %s *****", otdbId)
        self._stopPipeline(otdbId)

        """
          More statusses we want to abort on.
        """
    onObservationDescribed = onObservationAborted
    onObservationApproved = onObservationAborted
    onObservationPrescheduled = onObservationAborted
    onObservationConflict = onObservationAborted
    onObservationHold = onObservationAborted


class PipelineControl(OTDBBusListener):
    """The OTDBBusListener is a normal BusListener listening specifically to EventMessages with OTDB notification subjects.
    It uses by default the OTDBEventMessageHandler to handle the EventMessages.
    If you want to implement your own behaviour, then derive a subclass of the OTDBEventMessageHandler, and inject that in this OTDBBusListener.
    See example at the top of this file.
    """
    def __init__(self, handler_type: PipelineControlHandler.__class__ = PipelineControlHandler,
                 handler_kwargs: dict = None,
                 exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER,
                 num_threads: int = 1):
        if not issubclass(handler_type, PipelineControlHandler):
            raise TypeError("handler_type should be a PipelineControlHandler subclass")

        if handler_kwargs is None:
            handler_kwargs = {"exchange": exchange, "broker": broker}

        super().__init__(handler_type=handler_type, handler_kwargs=handler_kwargs,
                                              exchange=exchange,
                                              num_threads=num_threads, broker=broker)

    def start_listening(self):
        # HACK: create a temporary extra handler which is not connected to this listener,
        # and hence not responding to incoming messages,
        # and use this extra handler to initially check all already scheduled pipelines
        with self._create_handler() as helper_handler:
            helper_handler.check_scheduled_pipelines()

        # everything has been check, now start_listening, and let the normal handlers respond to otdb events
        super().start_listening()





