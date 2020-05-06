#!/usr/bin/env python3

import time

from lofar.mac.PipelineControl import *
from lofar.sas.otdb.config import DEFAULT_OTDB_NOTIFICATION_SUBJECT, DEFAULT_OTDB_SERVICENAME
from lofar.sas.resourceassignment.resourceassignmentservice.config import \
    DEFAULT_RADB_SERVICENAME as DEFAULT_RAS_SERVICENAME
from lofar.messaging import ServiceMessageHandler, TemporaryQueue, RPCService, EventMessage,\
    TemporaryExchange, BusListenerJanitor

import subprocess
import unittest
from unittest.mock import patch
import datetime

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def setUpModule():
    pass


def tearDownModule():
    pass


class TestRunCommand(unittest.TestCase):
    def test_basic(self):
        """ Test whether we can run a trivial command. """
        runCommand("true")

    def test_invalid_command(self):
        """ Test whether an invalid command produces an error. """
        with self.assertRaises(subprocess.CalledProcessError):
            runCommand("invalid-command")

    def test_shell(self):
        """ Test whether the command is parsed by a shell. """
        runCommand("true --version")

    def test_output(self):
        """ Test whether we catch the command output correctly. """
        output = runCommand("echo yes")
        self.assertEqual(output, "yes")

    def test_input(self):
        """ Test whether we can provide input. """
        output = runCommand("cat -", "yes")
        self.assertEqual(output, "yes")


class TestPipelineControlClassMethods(unittest.TestCase):
    def test_shouldHandle(self):
        """ Test whether we filter the right OTDB trees. """

        logger.warning('TEST_SHOULDHANDLE')

        trials = [{"type": "Observation", "cluster": "CEP2", "shouldHandle": False},
                  {"type": "Observation", "cluster": "CEP4", "shouldHandle": False},
                  {"type": "Observation", "cluster": "foo", "shouldHandle": False},
                  {"type": "Observation", "cluster": "", "shouldHandle": False},
                  {"type": "Pipeline", "cluster": "CEP2", "shouldHandle": False},
                  {"type": "Pipeline", "cluster": "CEP4", "shouldHandle": True},
                  {"type": "Pipeline", "cluster": "foo", "shouldHandle": True},
                  {"type": "Pipeline", "cluster": "", "shouldHandle": False},
                  ]

        for t in trials:
            parset = {"ObsSW.Observation.processType": t["type"],
                      "ObsSW.Observation.Cluster.ProcessingCluster.clusterName": t["cluster"]}
            self.assertEqual(PipelineControlHandler._shouldHandle(Parset(parset)), t["shouldHandle"])

        logger.warning('END TEST_SHOULDHANDLE')


class MockRAService(ServiceMessageHandler):
    """
        Fakes RAService calls.

        For each job, radb_id = otdb_id + 1000 to detect misplaced ids.
    """
    def __init__(self, predecessors, status):
        super(MockRAService, self).__init__()

        self.service2MethodMap = {
            "GetTask":  self.GetTask,
            "GetTasks": self.GetTasks,
        }

        self.predecessors = predecessors
        self.successors = {x: [s for s in predecessors if x in predecessors[s]]
                           for x in predecessors}
        self.status = status

    def GetTask(self, id, mom_id, otdb_id, specification_id):
        logger.info("***** GetTask(%s) *****", otdb_id)

        return {
          'status': self.status[otdb_id],

          'predecessor_ids': [1000 + x for x in self.predecessors[otdb_id]],
          'successor_ids':   [1000 + x for x in self.successors[otdb_id]],

          'starttime': datetime.datetime.utcnow(),
          'endtime': datetime.datetime.utcnow(),
        }

    def GetTasks(self, lower_bound, upper_bound, task_ids, task_status, task_type, mom_ids,
                 otdb_ids, cluster):
        logger.info("***** GetTasks(%s) *****", task_ids)

        if task_ids is None:
            # Used on startup to check which tasks are at scheduled
            return []

        return [{
          'otdb_id': t - 1000,
          'status': self.status[t - 1000],

          'starttime': datetime.datetime.utcnow(),
          'endtime': datetime.datetime.utcnow(),
        } for t in task_ids]


# ================================
# Global state to manipulate
# ================================

otdb_predecessors = {}
otdb_status = {}


class MockOTDBService(ServiceMessageHandler):
    def __init__(self, notification_bus):
        """
            notification_bus: bus to send state changes to
        """
        super(MockOTDBService, self).__init__()

        self.notification_bus = notification_bus

    def TaskGetSpecification(self, OtdbID):
        logger.info("***** TaskGetSpecification(%s) *****", OtdbID)

        return {
            "TaskSpecification": {
                "Version.number": "1",
                PARSET_PREFIX + "Observation.otdbID": str(OtdbID),
                PARSET_PREFIX + "Observation.processType":
                    ("Observation" if OtdbID == 4 else "Pipeline"),
                PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.clusterName": "CEP4",
                PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.clusterPartition": "cpu",
                PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.numberOfCoresPerTask": "2",
                PARSET_PREFIX + "Observation.Cluster.ProcessingCluster.numberOfTasks": "110",
            }}

    def TaskSetStatus(self, OtdbID, NewStatus, UpdateTimestamps):
        logger.info("***** TaskSetStatus(%s,%s) *****", OtdbID, NewStatus)

        global otdb_status
        otdb_status[OtdbID] = NewStatus

        # Broadcast the state change
        content = {"treeID": OtdbID,
                   "state": NewStatus,
                   "time_of_change": datetime.datetime.utcnow()}
        msg = EventMessage(subject=DEFAULT_OTDB_NOTIFICATION_SUBJECT, content=content)
        self.notification_bus.send(msg)

        return {'OtdbID': OtdbID, 'MomID': None, 'Success': True}

    def TaskGetStatus(self, otdb_id):
        logger.info("***** TaskGetStatus(%s) *****", otdb_id)
        return {'OtdbID': otdb_id, 'status': otdb_status.get(otdb_id, 'unknown')}


class TestPipelineDependencies(unittest.TestCase):
    def setUp(self):
        # Create a random bus
        self.tmp_queue = TemporaryQueue(__class__.__name__)
        self.tmp_queue.open()
        self.addCleanup(self.tmp_queue.close)

        self.notification_bus = self.tmp_queue.create_tobus()
        self.notification_bus.open()
        self.addCleanup(self.notification_bus.close)

        # ================================
        # Global state to manipulate
        # ================================

        global otdb_predecessors
        otdb_predecessors = {
          1: [2, 3, 4],
          2: [3],
          3: [],
          4: [],
        }

        global otdb_status
        otdb_status = {
            1: "scheduled",  # cannot start, since predecessor 2 hasn't finished
            2: "scheduled",  # can start, since predecessor 3 has finished
            3: "finished",
            4: "scheduled",  # can start, because no predecessors
            }

        # Setup mock otdb service
        service = RPCService(service_name=DEFAULT_OTDB_SERVICENAME,
                             handler_type=MockOTDBService,
                             handler_kwargs={"notification_bus": self.notification_bus})
        service.start_listening()
        self.addCleanup(service.stop_listening)

        # ================================
        # Setup mock ra service
        #
        # Note that RA IDs are the same as
        # OTDB IDs + 1000 in this test.
        # ================================

        service = RPCService(service_name=DEFAULT_RAS_SERVICENAME,
                             handler_type=MockRAService,
                             handler_kwargs={"predecessors": otdb_predecessors,
                                             "status": otdb_status})
        service.start_listening()
        self.addCleanup(service.stop_listening)

    def testGetState(self):
        with PipelineDependencies() as pipelineDependencies:
            self.assertEqual(pipelineDependencies.getState(1), "scheduled")
            self.assertEqual(pipelineDependencies.getState(2), "scheduled")
            self.assertEqual(pipelineDependencies.getState(3), "finished")
            self.assertEqual(pipelineDependencies.getState(4), "scheduled")

    def testPredecessorStates(self):
        with PipelineDependencies() as pipelineDependencies:
            self.assertEqual(pipelineDependencies.getPredecessorStates(1),
                             {2: "scheduled", 3: "finished", 4: "scheduled"})
            self.assertEqual(pipelineDependencies.getPredecessorStates(3), {})

    def testSuccessorIds(self):
        with PipelineDependencies() as pipelineDependencies:
            self.assertEqual(pipelineDependencies.getSuccessorIds(1), [])
            self.assertEqual(pipelineDependencies.getSuccessorIds(3), [1, 2])

    def testCanStart(self):
        with PipelineDependencies() as pipelineDependencies:
            self.assertEqual(pipelineDependencies.canStart(1), False)
            self.assertEqual(pipelineDependencies.canStart(2), True)
            self.assertEqual(pipelineDependencies.canStart(3), False)
            self.assertEqual(pipelineDependencies.canStart(4), True)


class TestPipelineControl(unittest.TestCase):
    def setUp(self):
        self.temp_exchange = TemporaryExchange(__class__.__name__ )
        self.temp_exchange.open()
        self.addCleanup(self.temp_exchange.close)

        self.notification_bus = self.temp_exchange.create_tobus()
        self.notification_bus.open()
        self.addCleanup(self.notification_bus.close)

        # Patch SLURM
        class MockSlurm(object):
            def __init__(self):
                self.scheduled_jobs = {}

            def submit(self, job_name, *args, **kwargs):
                logger.info("Schedule SLURM job '%s': %s, %s", job_name, args, kwargs)

                self.scheduled_jobs[job_name] = (args, kwargs)

                # Return fake job ID
                return "42"

            def isQueuedOrRunning(self, otdb_id):
                return str(otdb_id) in self.scheduled_jobs

        self.mock_slurm = MockSlurm()
        patcher = patch('lofar.mac.PipelineControl.Slurm')
        patcher.start().return_value = self.mock_slurm
        self.addCleanup(patcher.stop)

        # Catch functions to prevent running executables
        patcher = patch('lofar.mac.PipelineControl.Parset.dockerImage')
        patcher.start().return_value = "lofar-pipeline:trunk"
        self.addCleanup(patcher.stop)

        # ================================
        # Global state to manipulate
        # ================================

        global otdb_predecessors
        otdb_predecessors = {
            1: [2, 3, 4],
            2: [3],
            3: [],
            4: [],
        }

        global otdb_status
        otdb_status = {
            1: "prescheduled",
            2: "prescheduled",
            3: "prescheduled",
            4: "prescheduled",
        }

        service = RPCService(service_name=DEFAULT_OTDB_SERVICENAME,
                             exchange=self.temp_exchange.address,
                             handler_type=MockOTDBService,
                             handler_kwargs={"notification_bus": self.notification_bus})
        service.start_listening()
        self.addCleanup(service.stop_listening)

        # ================================
        # Setup mock ra service
        # ================================

        service = RPCService(service_name=DEFAULT_RAS_SERVICENAME,
                             exchange=self.temp_exchange.address,
                             handler_type=MockRAService,
                             handler_kwargs={"predecessors": otdb_predecessors,
                                             "status": otdb_status})
        service.start_listening()
        self.addCleanup(service.stop_listening)

    def _wait_for_status(self, otdb_id, expected_status, timeout=5):
        start = datetime.datetime.utcnow()

        while True:
            if otdb_status[otdb_id] == expected_status:
                break

            time.sleep(0.25)
            self.assertGreater(datetime.timedelta(seconds=timeout),
                               datetime.datetime.utcnow() - start,
                               "Timeout while waiting for expected status")

    def testNoPredecessors(self):
        """
          Request to start a simulated obsid 3, with the following predecessor tree:

            3 requires nothing
        """
        with BusListenerJanitor(PipelineControl(exchange=self.temp_exchange.address)):
            with OTDBRPC.create(exchange=self.temp_exchange.address) as otdb_rpc:
                # Send fake status update
                otdb_rpc.taskSetStatus(otdb_id=3, new_status="scheduled")

                # Wait for pipeline to be queued
                self._wait_for_status(3, "queued")

                # Check if job was scheduled
                self.assertIn("3", self.mock_slurm.scheduled_jobs)
                self.assertIn("3-abort-trigger", self.mock_slurm.scheduled_jobs)

    def testPredecessors(self):
        """
          Request to start a simulated obsid 1, with the following predecessor tree:

            1 requires 2, 3, 4
            2 requires 3
            4 is an observation
        """
        with BusListenerJanitor(PipelineControl(exchange=self.temp_exchange.address)):
            with OTDBRPC.create(exchange=self.temp_exchange.address) as otdb_rpc:
                # Send fake status update
                otdb_rpc.taskSetStatus(otdb_id=1, new_status="scheduled")

                # Message should not arrive, as predecessors havent finished
                with self.assertRaises(AssertionError):
                    self._wait_for_status(1, "queued")

                # Finish predecessors
                otdb_rpc.taskSetStatus(otdb_id=2, new_status="finished")
                otdb_rpc.taskSetStatus(otdb_id=3, new_status="finished")
                otdb_rpc.taskSetStatus(otdb_id=4, new_status="finished")

                # Wait for pipeline to be queued
                self._wait_for_status(1, "queued")

                # Check if job was scheduled
                self.assertIn("1", self.mock_slurm.scheduled_jobs)
                self.assertIn("1-abort-trigger", self.mock_slurm.scheduled_jobs)


if __name__ == "__main__":
    unittest.main()
