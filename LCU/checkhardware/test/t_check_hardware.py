import unittest
import os
from mock import MagicMock, patch, call
import sys
import logging
import subprocess
import signal
import atexit
import time

logger = logging.getLogger(__name__)
 
# mock out check for existing log directory on script import as module
os.access = MagicMock(return_value=True)

# mock out modules with relative imports (that only work with the namespace when executed as a script)
# FIXME: make sure that absolute imports are ok and don't break things in production.
# FIXME: ...Then fix the implementation and remove this mock so we can test those modules.
with patch.dict('sys.modules', **{
    'checkhardware_lib': MagicMock(),
    'checkhardware_lib.data': MagicMock(),
    'checkhardware_lib.rsp': MagicMock(),
    'cable_reflection': MagicMock(),
    'logging': MagicMock(),
}):
    # import these here so we can before mock out checks on station environment
    import lofar.lcu.checkhardware.check_hardware as check_hardware
    from lofar.lcu.checkhardware.checkhardware_lib import TestSettings, ParameterSet
    check_hardware.logger = logger   # override logger to handle logging output here


class TestCheckHardware(unittest.TestCase):

    def setUp(self):
        logger.info(">>>---> %s <---<<<" % self._testMethodName)

        # mock exit call to not actually exit the test
        os._exit = MagicMock()
        # we don't want to actually call anything
        check_hardware.check_call = MagicMock()

        self.elem_settings_no_testsignal = ParameterSet()
        self.elem_settings_no_testsignal.parset = {'spurious': {'min-peak-pwr': '3.0',
                                                                'passband': '1:511'},
                                                   'rf': {'negative-deviation': '-24.0',
                                                          'subbands': '105',
                                                          'min-sb-pwr': '65.0',
                                                          'positive-deviation': '12.0'},
                                                   'noise': {'negative-deviation': '-3.0',
                                                             'max-difference': '1.5',
                                                             'positive-deviation': '1.5',
                                                             'passband': '1:511'},
                                                   'oscillation': {'min-peak-pwr': '6.0',
                                                                   'passband': '1:511'}}

        self.elem_settings_testsignal = ParameterSet()
        self.elem_settings_testsignal.parset = {'spurious': {'min-peak-pwr': '3.0',
                                                             'passband': '1:511'},
                                                'rf': {'negative-deviation': '-24.0',
                                                       'subbands': '105',
                                                       'min-sb-pwr': '65.0',
                                                       'positive-deviation': '12.0'},
                                                'noise': {'negative-deviation': '-3.0',
                                                          'max-difference': '1.5',
                                                          'positive-deviation': '1.5',
                                                          'passband': '1:511'},
                                                'testsignal': {'start-cmd': 'echo set config 56.0 -10 | nc ncu 8093',
                                                               'stop-cmd': 'echo bye | nc ncu 8093'},
                                                'oscillation': {'min-peak-pwr': '6.0',
                                                                'passband': '1:511'}}

        self.elem_settings_testsignal_with_status = ParameterSet()
        self.elem_settings_testsignal_with_status.parset = {'spurious': {'min-peak-pwr': '3.0',
                                                                         'passband': '1:511'},
                                                            'rf': {'negative-deviation': '-24.0',
                                                                   'subbands': '105',
                                                                   'min-sb-pwr': '65.0',
                                                                   'positive-deviation': '12.0'},
                                                            'noise': {'negative-deviation': '-3.0',
                                                                      'max-difference': '1.5',
                                                                      'positive-deviation': '1.5',
                                                                      'passband': '1:511'},
                                                            'testsignal': {'start-cmd': 'echo set config 56.0 -10 | nc ncu 8093',
                                                                           'stop-cmd': 'echo bye | nc ncu 8093',
                                                                           'status-cmd': "echo 'Frequency: 56 MHz Power level: -10 dBm RF: ON'",
                                                                           'ok-status': "Frequency: 56 MHz Power level: -10 dBm RF: ON"},
                                                            'oscillation': {'min-peak-pwr': '6.0',
                                                                            'passband': '1:511'}}


    def test_safely_start_test_signal(self):
        """ Verify that the provided command is executed and handlers are registered correctly"""

        # test value
        start_cmd = 'echo "Start the signal!"'
        stop_cmd = 'echo "Stop the signal!"'

        # setup test
        with patch.object(check_hardware, 'register_exit_handler'), \
             patch.object(check_hardware, 'register_signal_handlers'), \
             patch.object(check_hardware, 'start_watchdog_daemon'):

            # trigger action
            check_hardware.safely_start_test_signal(start_cmd, stop_cmd)

            # assert correct behavior
            check_hardware.check_call.assert_called_with(start_cmd, shell=True)
            check_hardware.register_exit_handler.assert_called_with(stop_cmd)
            check_hardware.register_signal_handlers.assert_called_with(stop_cmd)
            check_hardware.start_watchdog_daemon.assert_called_with(os.getpid(), stop_cmd)

    def test_safely_start_test_signal_logs_and_reraises_CalledProcessError(self):
        """ Verify that the provided command is executed and handlers are registered correctly"""

        # test value
        start_cmd = 'echo "Start the signal!"'
        stop_cmd = 'echo "Stop the signal!"'

        # setup test
        with patch.object(check_hardware, 'register_exit_handler'), \
             patch.object(check_hardware, 'register_signal_handlers'), \
             patch.object(check_hardware, 'start_watchdog_daemon'), \
             patch.object(check_hardware, 'check_call', MagicMock(side_effect=subprocess.CalledProcessError('', ''))), \
             patch.object(check_hardware.logger, 'error'):

            with self.assertRaises(subprocess.CalledProcessError):
                # trigger action
                check_hardware.safely_start_test_signal(start_cmd, stop_cmd)

            # assert correct behavior
            check_hardware.logger.error.assert_called()

    def test_safely_start_test_signal_from_ParameterSet_turns_signal_and_waits_for_status_correctly(self):
        """ Verify that the commands from ParameterSet are passed on to safely_start_test_signal and wait_for_test_signal_status"""

        # test value
        start_cmd = 'echo set config 56.0 -10 | nc ncu 8093'
        stop_cmd = 'echo bye | nc ncu 8093'
        expected_status_cmd = "echo 'Frequency: 56 MHz Power level: -10 dBm RF: ON'"
        expected_ok_status = "Frequency: 56 MHz Power level: -10 dBm RF: ON"

        # setup test
        with patch.object(check_hardware, 'safely_start_test_signal'), \
             patch.object(check_hardware, 'wait_for_test_signal_status'):

            # trigger action
            check_hardware.safely_start_test_signal_from_ParameterSet(self.elem_settings_testsignal_with_status)

            # assert correct behavior
            check_hardware.safely_start_test_signal.assert_called_with(start_cmd, stop_cmd)
            check_hardware.wait_for_test_signal_status.assert_called_with(expected_status_cmd, expected_ok_status)

    def test_safely_start_test_signal_from_ParameterSet_does_nothing_when_no_stationsignal_keys_in_ParameterSet(self):
        """ Verify that the commands from ParameterSet are passed on to safely_start_test_signal and wait_for_test_signal_status is not called"""

        # setup test
        with patch.object(check_hardware, 'safely_start_test_signal'), \
             patch.object(check_hardware, 'wait_for_test_signal_status'):

            # trigger action
            check_hardware.safely_start_test_signal_from_ParameterSet(self.elem_settings_no_testsignal)

            # assert correct behavior
            check_hardware.safely_start_test_signal.assert_not_called()
            check_hardware.wait_for_test_signal_status.assert_not_called()

    def test_safely_start_test_signal_from_ParameterSet_only_starts_signal_when_no_status_keys_in_ParameterSet(self):
        """ Verify that safely_start_test_signal and wait_for_test_signal_status are not called"""

        # test value
        start_cmd = 'echo set config 56.0 -10 | nc ncu 8093'
        stop_cmd = 'echo bye | nc ncu 8093'

        # setup test
        with patch.object(check_hardware, 'safely_start_test_signal'), \
             patch.object(check_hardware, 'wait_for_test_signal_status'):
            # trigger action
            check_hardware.safely_start_test_signal_from_ParameterSet(self.elem_settings_testsignal)

            # assert correct behavior
            check_hardware.safely_start_test_signal.assert_called_with(start_cmd, stop_cmd)
            check_hardware.wait_for_test_signal_status.assert_not_called()

    def test_stop_test_signal(self):
        """ Verify that the provided command is executed """

        # test value
        cmd = 'echo "Stop the signal! 1"'

        # trigger action
        check_hardware.stop_test_signal(cmd)

        # assert correct behavior
        os._exit.assert_not_called()
        check_hardware.check_call.assert_called_with(cmd, shell=True)   # command is executed

    def test_stop_test_signal_and_exit_defaults_to_code_1(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # test value
        cmd = 'echo "Stop the signal! 2"'

        # trigger action
        check_hardware.stop_test_signal_and_exit(cmd)

        # assert correct behavior
        os._exit.assert_called_with(1)                        # exit code correct
        check_hardware.check_call.assert_called_with(cmd, shell=True)   # command is executed

    def test_stop_test_signal_and_exit_handles_signal_correctly(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # test value
        cmd = 'echo "Stop the signal! 2"'
        signal_code = 42

        # trigger action
        check_hardware.stop_test_signal_and_exit(cmd, signal_code, KeyboardInterrupt())

        # assert correct behavior
        os._exit.assert_called_with(signal_code)                        # exit code correct
        check_hardware.check_call.assert_called_with(cmd, shell=True)   # command is executed

    def test_wait_for_test_signal_status_waits_for_correct_status(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # test value
        status_cmd = 'mockme'
        responses = ['ne', 'ja\n', 'ne']
        waitfor = 'ja'

        with patch.object(check_hardware, 'check_output', MagicMock(side_effect=responses)),\
             patch('time.sleep'):

            # trigger action
            check_hardware.wait_for_test_signal_status(status_cmd, waitfor)

            # assert correct behavior
            check_hardware.check_output.called_with(status_cmd, shell=True)   # command is executed
            self.assertEqual(check_hardware.check_output.call_count, 2)

    def test_wait_for_test_signal_status_raises_RuntimeError_when_retry_limit_reached(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # test value
        limit=15
        status_cmd = 'mockme'
        responses = ['ne'] * limit  # only 30 are read
        responses.append('ja')
        waitfor = 'ja'

        with patch.object(check_hardware, 'check_output', MagicMock(side_effect=responses)),\
             patch('time.sleep'):

            # trigger action

            with self.assertRaises(RuntimeError):
                check_hardware.wait_for_test_signal_status(status_cmd, waitfor, retry_limit=limit)

            # assert correct behavior
            check_hardware.check_output.called_with(status_cmd, shell=True)   # command is executed
            self.assertEqual(check_hardware.check_output.call_count, limit)


    def test_register_signal_handlers_stops_test_signal_on_POSIX_signal(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # test value
        cmd = 'echo "Stop the signal! 3"'

        # register handlers we want to test
        check_hardware.register_signal_handlers(cmd)

        # trigger action:
        pid = os.getpid()
        os.kill(pid, signal.SIGINT)     # code 2
        os.kill(pid, signal.SIGABRT)    # code 6
        os.kill(pid, signal.SIGTERM)    # code 15

        # assert correct behavior
        os._exit.assert_has_calls([call(2), call(6), call(15)])         # all signal error codes correct
        check_hardware.check_call.assert_called_with(cmd, shell=True)   # command is executed

    def test_register_exit_handler_stops_test_signal_on_normal_exit(self):
        """ Verify that the provided command is executed and os._exit is called with correct return code """

        # This test turned out nastier than expected.
        # The problem is that we cannot catch the SystemExit within the test, because the atexit hooks only fire after
        # the test exits (even after tearDownClass), so we will get a stacktrace printed, but cmake won't count the
        # assert failures as failure of the test.
        # Note: As long as we use the watchdog, this is redundant anyway and we could also change the implementation
        #       to explicitely turn the test signal off before it exits and test for that instead.
        #       But who wants the easy way out, right? ;)
        # FIXME: Find a way to make sure this test fails if the assertion fails or find a smarter way to test this.

        # test value
        cmd = 'echo "Stop the signal! 4"'

        # assert correct behavior
        def assert_on_exit():
            logger.info('>>>----> Asserting on exit!')
            check_hardware.check_call.assert_called_with(cmd, shell=True)  # command is executed

        # register a handler to trigger the assert.
        atexit.register(assert_on_exit)

        # register handlers we want to test
        check_hardware.register_exit_handler(cmd)

        # The test will now regularly exit with code 0, hopefully triggering all these hooks


    def test_start_watchdog_daemon_stops_test_signal_when_provided_pid_is_killed(self):
        """ Verify that the provided command is executed when watched process dies """

        tmpfile = "/tmp/t_checkhardware.%s" % time.time()

        # test value
        good_message = 'Stop the signal! 5'
        cmd = 'echo "%s" > %s' % (good_message, tmpfile)

        # start dummy process
        p = subprocess.Popen(['sleep', '120'])

        # start watchdog for dummy process
        check_hardware.start_watchdog_daemon(p.pid, cmd)

        # kill dummy
        os.kill(p.pid, signal.SIGKILL)
        os.wait()

        # check temporary file to confirm the watchdog command has been executed
        for i in range (30):
            if os.path.isfile(tmpfile):
                break
            time.sleep(1)
        self.assertTrue(os.path.isfile(tmpfile))
        with open(tmpfile) as f:
            lines = f.read().split('\n')
            self.assertTrue(good_message in lines)   # cmd has been executed

        os.remove(tmpfile)


    # FIXME: Move this to t_settings once that exists
    def test_settings_parset_raises_KeyError_when_accessing_missing_key(self):

        # assert KeyError if setting not there
        with self.assertRaises(KeyError):
            logger.info(self.elem_settings_no_testsignal.parset['testsignal']['status-cmd'])


    # FIXME: Move this to t_settings once that exists
    def test_settings_contains_testsignal_commands_from_config_file(self):

        # test_values
        expected_start_cmd = "echo set config 56.0 -10 | nc ncu 8093"
        expected_stop_cmd = "echo bye | nc ncu 8093"
        expected_status_cmd = "echo 'Frequency: 56 MHz Power level: -10 dBm RF: ON'"
        expected_ok_status = "Frequency: 56 MHz Power level: -10 dBm RF: ON"

        # read settings
        f = os.environ.get('srcdir')+'/test-check_hardware.conf'
        settings = TestSettings(filename=f)
        elem_settings = settings.group('rcumode.5.element')
        start_cmd = elem_settings.parset['testsignal']['start-cmd']
        stop_cmd = elem_settings.parset['testsignal']['stop-cmd']
        status_cmd = elem_settings.parset['testsignal']['status-cmd']
        ok_status = elem_settings.parset['testsignal']['ok-status']

        # assert correct values
        self.assertEqual(start_cmd, expected_start_cmd)
        self.assertEqual(stop_cmd, expected_stop_cmd)
        self.assertEqual(status_cmd, expected_status_cmd)
        self.assertEqual(ok_status, expected_ok_status)

    def test_main_turns_signal_with_commands_from_settings(self):

        # test values
        expected_start_cmd = "echo set config 56.0 -10 | nc ncu 8093"
        expected_stop_cmd = "echo bye | nc ncu 8093"
        expected_status_cmd = "echo 'Frequency: 56 MHz Power level: -10 dBm RF: ON'"
        expected_ok_status = "Frequency: 56 MHz Power level: -10 dBm RF: ON"

        # setup tests
        # todo: mock the ParameterSet instead, once the imports are resolved and this can be done straight-forward
        check_hardware.conf_file = r'test-check_hardware.conf'
        check_hardware.confpath = os.environ.get('srcdir')+'/'
        check_hardware.TestSettings = TestSettings

        # pretend to be a station
        # FIXME: correct behavior of mocked-out parts should be covered by additional tests
        # FIXME: why is all this actually necessary when I only run an element test?
        with patch.object(check_hardware, 'read_station_config', MagicMock(return_value=(1, 1, 1, 1, 1, 1, 1))), \
             patch.object(check_hardware, 'safely_start_test_signal'), \
             patch.object(check_hardware, 'wait_for_test_signal_status'), \
             patch.object(check_hardware, 'swlevel', MagicMock(return_value=(5, None))), \
             patch.object(check_hardware, 'rspctl'), \
             patch.object(check_hardware, 'RSP'), \
             patch.object(check_hardware, 'check_active_boards', MagicMock(return_value=(1, 1))), \
             patch.object(check_hardware, 'check_active_tbbdriver', MagicMock(return_value=True)), \
             patch.object(check_hardware, 'check_active_rspdriver', MagicMock(return_value=True)), \
             patch.object(check_hardware, 'reset_rsp_settings'), \
             patch.object(check_hardware, 'HBA'), \
             patch.object(check_hardware, 'reset_48_volt'), \
             patch.object(check_hardware, 'tbbctl'), \
             patch.object(os, 'listdir'), \
             patch.object(os, 'remove'):      # I'm scared...

            # patch arguments: pretend script was started with these.
            # -TST (test mode)
            # -e5: (element test in mode 5)
            # Names optimized for disk space
            testargs = ["check_hardware.py", '-TST', '-e5', '-s5']
            with patch.object(sys, 'argv', testargs):
                # trigger action
                check_hardware.main() # Warning: Something acts as a fork bomb when mocks are not setup properly!

            check_hardware.safely_start_test_signal.assert_called_with(expected_start_cmd, expected_stop_cmd)
            check_hardware.wait_for_test_signal_status.assert_called_with(expected_status_cmd, expected_ok_status)
            self.assertEqual(check_hardware.safely_start_test_signal.call_count, 2)
            self.assertEqual(check_hardware.wait_for_test_signal_status.call_count, 2)


if __name__ == "__main__":
    logger.level = logging.DEBUG
    unittest.main()
