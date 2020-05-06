#!/usr/bin/env python3

"""
This file provides the unit tests for the RATaskSpecified.py module, which is hereafter referred to
as Unit Under Test or simply uut
"""

import unittest
from unittest import mock

from lofar.sas.resourceassignment.rataskspecified.RATaskSpecified import \
    RATaskSpecifiedOTDBEventMessageHandler

from unittest.mock import MagicMock

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class TestingRATaskSpecified(RATaskSpecifiedOTDBEventMessageHandler):
    def __init__(self, otdbrpc, radbrpc, momrpc, send_bus):
        self.otdbrpc = otdbrpc
        self.radbrpc = radbrpc
        self.momrpc = momrpc
        self.send_bus = send_bus


class TestRATaskSpecified(unittest.TestCase):

    def setUp(self):
        self.task_main_id = 325
        self.task_status = "prescheduled"

        self.spec_result_tree = {'test': 11}

        self.mocked_spec = MagicMock()
        self.mocked_spec.as_dict.return_value = self.spec_result_tree

        specification_patcher = mock.patch(
            'lofar.sas.resourceassignment.rataskspecified.RATaskSpecified.Specification')
        self.addCleanup(specification_patcher.stop)
        self.specification_mock = specification_patcher.start()
        self.specification_mock.return_value = self.mocked_spec

        otdbrpc_patcher = mock.patch('lofar.sas.otdb.otdbrpc')
        self.addCleanup(otdbrpc_patcher.stop)
        self.otdbrpc_mock = otdbrpc_patcher.start()

        radbrpc_patcher = mock.patch('lofar.sas.resourceassignment.resourceassignmentservice.rpc')
        self.addCleanup(radbrpc_patcher.stop)
        self.radbrpc_mock = radbrpc_patcher.start()

        momrpc_patcher = mock.patch('lofar.mom.momqueryservice.momqueryrpc')
        self.addCleanup(momrpc_patcher.stop)
        self.momrpc_mock = momrpc_patcher.start()

        logger_patcher = mock.patch(
            'lofar.sas.resourceassignment.rataskspecified.RATaskSpecified.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        send_bus_patcher = mock.patch('lofar.messaging.ToBus')
        self.addCleanup(send_bus_patcher.stop)
        self.send_bus_mock = send_bus_patcher.start()

        self.raTaskSpecified = TestingRATaskSpecified(self.otdbrpc_mock, self.radbrpc_mock,
                                                      self.momrpc_mock, self.send_bus_mock)

    # start listening

    def test_start_listening_opens_otdbrpc(self):
        self.raTaskSpecified.start_handling()

        self.otdbrpc_mock.open.assert_called()

    def test_start_listening_opens_radbrpc(self):
        self.raTaskSpecified.start_handling()

        self.radbrpc_mock.open.assert_called()

    def test_start_listening_opens_momrpc(self):
        self.raTaskSpecified.start_handling()

        self.momrpc_mock.open.assert_called()

    def test_start_listening_opens_send_bus(self):
        self.raTaskSpecified.start_handling()

        self.send_bus_mock.open.assert_called()

    # stop listening

    def test_stop_listening_closes_otdbrpc(self):
        self.raTaskSpecified.stop_handling()

        self.otdbrpc_mock.close.assert_called()

    def test_stop_listening_closes_radbrpc(self):
        self.raTaskSpecified.stop_handling()

        self.radbrpc_mock.close.assert_called()

    def test_stop_listening_closes_momrpc(self):
        self.raTaskSpecified.stop_handling()

        self.momrpc_mock.close.assert_called()

    def test_stop_listening_closes_send_bus(self):
        self.raTaskSpecified.stop_handling()

        self.send_bus_mock.close.assert_called()

    # onObservationPrescheduled

    def test_onObservationPrescheduled_should_set_status_on_specification(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.assertEqual(self.mocked_spec.status, self.task_status)

    def test_onObservationPrescheduled_should_call_read_from_OTDB_with_predecessors(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.mocked_spec.read_from_OTDB_with_predecessors.assert_called_with(self.task_main_id,
                                                                             "otdb", {})

    def test_onObservationPrescheduled_should_call_read_from_mom(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.mocked_spec.read_from_mom.assert_called()

    def test_onObservationPrescheduled_should_call_update_start_end_times(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.mocked_spec.update_start_end_times.assert_called()

    def test_onObservationPrescheduled_should_log_before_sending_if_status_is_prescheduled(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.logger_mock.info.assert_any_call("Sending result: %s" % self.spec_result_tree)

    def test_onObservationPrescheduled_should_log_after_sending_if_status_is_prescheduled(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.logger_mock.info.assert_any_call("Result sent")

    def test_onObservationPrescheduled_should_send_message_if_status_is_prescheduled(self):
        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.assertEqual(self.send_bus_mock.send.call_args_list[0][0][0].content, self.spec_result_tree)

    def test_onObservationPrescheduled_should_log_if_status_is_not_prescheduled(self):
        def set_spec_status_to_error(main_id, id_source, found_specifications):
            self.mocked_spec.status = 'Error'

        self.mocked_spec.read_from_OTDB_with_predecessors.side_effect = set_spec_status_to_error

        self.raTaskSpecified.onObservationPrescheduled(self.task_main_id, self.task_status)

        self.logger_mock.warning.assert_any_call("Problem retrieving task %i" % self.task_main_id)


if __name__ == '__main__':
    unittest.main()
