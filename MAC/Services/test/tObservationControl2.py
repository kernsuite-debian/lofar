import unittest

from unittest import mock
import os

from lofar.mac.ObservationControl2 import ObservationControlHandler
import lofar.mac.config as config


class TestObservationControlHandler(unittest.TestCase):
    pid1 = "1000"
    pid2 = "2000"

    sas_id = "100"

    def _run_side_effect(self, cmd):
        if cmd.startswith("ps -p %s" % self.pid1):
            return_value = mock.MagicMock
            return_value.stdout = self.sas_id
            return return_value
        elif cmd.startswith("ps -p %s" % self.pid2):
            return_value = mock.MagicMock
            return_value.stdout = self.sas_id + "10"
            return return_value
        elif cmd.startswith("pidof"):
            return_value = mock.MagicMock
            return_value.stdout = "%s %s" % (self.pid1, self.pid2)
            return return_value
        elif cmd.startswith("kill"):
            return_value = mock.MagicMock
            return_value.stdout = ""
            return return_value

    def setUp(self):
        fabric_connection_pathcher = mock.patch('lofar.mac.ObservationControl2.Connection')
        self.addCleanup(fabric_connection_pathcher.stop)
        self.fabric_connection_mock = fabric_connection_pathcher.start()
        self.fabric_connection_mock().run.side_effect = self._run_side_effect

        logger_patcher = mock.patch('lofar.mac.ObservationControl2.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        self.observation_control_handler = ObservationControlHandler()

    def test_abort_observation_task_should_run_pidof_ObservationControl(self):
        self.observation_control_handler._abort_observation_task(self.sas_id)

        self.fabric_connection_mock().run.assert_any_call('pidof ObservationControl')

    def test_abort_observation_tasks_should_run_ps_to_find_sas_id_on_command(self):
        self.observation_control_handler._abort_observation_task(self.sas_id)

        self.fabric_connection_mock().run.assert_any_call(
            "ps -p %s --no-heading -o command | awk -F[{}] '{ printf $2; }'" % self.pid1)
        self.fabric_connection_mock().run.assert_any_call(
            "ps -p %s --no-heading -o command | awk -F[{}] '{ printf $2; }'" % self.pid2)

    def test_abort_observation_task_should_run_kill_when_sas_id_matches(self):
        self.observation_control_handler._abort_observation_task(self.sas_id)

        self.fabric_connection_mock().run.assert_any_call('kill -SIGINT %s' % self.pid1)

    @mock.patch.dict(os.environ, {'LOFARENV': 'TEST'})
    def test_observation_control_should_select_test_host_if_lofar_environment_is_test(self):
        ObservationControlHandler()

        self.fabric_connection_mock.assert_called_with(config.TEST_OBSERVATION_CONTROL_HOST)

    @mock.patch.dict(os.environ, {'LOFARENV': 'PRODUCTION'})
    def test_observation_control_should_select_production_host_if_lofar_environment_is_production(
            self):
        ObservationControlHandler()

        self.fabric_connection_mock.assert_called_with(config.PRODUCTION_OBSERVATION_CONTROL_HOST)

    def test_observation_control_should_select_local_host_if_no_lofar_environment_is_set(self):
        ObservationControlHandler()

        self.fabric_connection_mock.assert_called_with("localhost")

    def test_abort_observation_task_should_return_false_on_unknown_sas_id(self):
        self.assertFalse(self.observation_control_handler._abort_observation_task("unknown"))

    def test_abort_observation_task_should_return_true_on_known_sas_id(self):
        self.assertTrue(self.observation_control_handler._abort_observation_task(self.sas_id))

    def test_abort_observation_task_should_log_call(self):
        self.observation_control_handler._abort_observation_task(self.sas_id)

        self.logger_mock.info.assert_any_call("trying to abort ObservationControl for SAS ID: %s",
                                              self.sas_id)

    def test_abort_observation_taks_should_log_the_kill(self):
        self.observation_control_handler._abort_observation_task(self.sas_id)

        self.logger_mock.info.assert_any_call(
            "Killing ObservationControl with PID: %s for SAS ID: %s", self.pid1, self.sas_id)

    def test_abort_observation_should_return_aborted_true_if_execute_returns_true(self):
        result = self.observation_control_handler.abort_observation(self.sas_id)

        self.assertTrue(result['aborted'])

    def test_abort_observation_should_return_aborted_false_if_execute_returns_false(self):
        self.fabric_connection_mock().run = mock.MagicMock()
        self.fabric_connection_mock().run.stdout = ""
        result = self.observation_control_handler.abort_observation(self.sas_id)

        self.assertFalse(result['aborted'])


if __name__ == "__main__":
    unittest.main()
