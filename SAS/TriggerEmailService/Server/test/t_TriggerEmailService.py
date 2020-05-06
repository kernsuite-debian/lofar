#!/usr/bin/env python3

# Copyright (C) 2017 ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest import mock
import os

from lofar.sas.TriggerEmailService.TriggerEmailService import OTDBTriggerHandler, email, TriggerNotificationHandler


class TestEmailing(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch.dict(os.environ, {'LOFARENV': 'PRODUCTION'})
    @mock.patch("smtplib.SMTP")
    def test_email_should_send_to_sos_and_operator_when_in_production(self, smtplib_mock):
        smtp_mock = mock.MagicMock()
        smtplib_mock.return_value = smtp_mock

        email([], "", "", "<xml></xml>", "trigger.xml")

        self.assertIn("sos@astron.nl", smtp_mock.sendmail.call_args[0][1])
        self.assertIn("observer@astron.nl", smtp_mock.sendmail.call_args[0][1])

    @mock.patch.dict(os.environ, {'LOFARENV': 'TEST'})
    @mock.patch("smtplib.SMTP")
    def test_email_should_not_send_to_sos_and_operator_when_in_test(self, smtplib_mock):
        smtp_mock = mock.MagicMock()
        smtplib_mock.return_value = smtp_mock

        email([], "", "", "<xml></xml>", "trigger.xml")

        self.assertNotIn("sos@astron.nl", smtp_mock.sendmail.call_args[0][1])
        self.assertNotIn("observer@astron.nl", smtp_mock.sendmail.call_args[0][1])


class TestOTDBTriggerHandler(unittest.TestCase):
    project_name = "test_lofar"
    trigger_id = 1
    obs_sas_id = 22
    obs_mom_id = 44
    object_mom2objectid = 66
    mom_link = "https://lofar.astron.nl/mom3/user/project/setUpMom2ObjectDetails.do?view=" \
               "generalinfo&mom2ObjectId=%s" % object_mom2objectid

    def setUp(self):
        self.momqueryrpc_mock = mock.MagicMock()
        self.momqueryrpc_mock.getObjectDetails.return_value = {self.obs_mom_id: {"project_name": self.project_name,
                                                                                 "project_mom2id": 2,
                                                                                 "object_mom2objectid": self.object_mom2objectid}}
        self.momqueryrpc_mock.get_project_details.return_value = {
            "author_email": "author@example.com", "pi_email": "pi@example.com"
        }

        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': self.trigger_id, 'status': "OK" }
        self.momqueryrpc_mock.getMoMIdsForOTDBIds.return_value = {self.obs_sas_id: self.obs_mom_id}

        email_patcher = mock.patch('lofar.sas.TriggerEmailService.TriggerEmailService.email')
        self.addCleanup(email_patcher.stop)
        self.email_mock = email_patcher.start()

        logger_patcher = mock.patch('lofar.sas.TriggerEmailService.TriggerEmailService.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

    def test_start_handling_should_open_momquery_rpc(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.start_handling()

        self.momqueryrpc_mock.open.assert_called()

    def test_stop_handling_should_close_momquery_rpc(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.stop_handling()

        self.momqueryrpc_mock.close.assert_called()

    # Aborted

    def test_onObservationAborted_should_not_email_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.email_mock.assert_not_called()

    def test_onObservationAborted_should_email_when_its_a_trigger(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.email_mock.assert_called()

    def test_onObservationAborted_should_set_correct_subject(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][1])
        self.assertIn(self.project_name, self.email_mock.call_args[0][1])

    def test_onObservationAborted_should_set_correct_body(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_sas_id), self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_mom_id), self.email_mock.call_args[0][2])
        self.assertIn(self.mom_link, self.email_mock.call_args[0][2])

    # Scheduled

    def test_onObservationScheduled_should_not_email_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationScheduled(self.obs_sas_id, None)

        self.email_mock.assert_not_called()

    def test_onObservationScheduled_should_email_when_its_a_trigger(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationScheduled(self.obs_sas_id, None)

        self.email_mock.assert_called()

    def test_onObservationScheduled_should_set_correct_subject(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationScheduled(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][1])
        self.assertIn(self.project_name, self.email_mock.call_args[0][1])

    def test_onObservationScheduled_should_set_correct_body(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationScheduled(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_sas_id), self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_mom_id), self.email_mock.call_args[0][2])
        self.assertIn(self.mom_link, self.email_mock.call_args[0][2])

    # Finished

    def test_onObservationFinished_should_not_email_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationFinished(self.obs_sas_id, None)

        self.email_mock.assert_not_called()

    def test_onObservationFinished_should_email_when_its_a_trigger(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationFinished(self.obs_sas_id, None)

        self.email_mock.assert_called()

    def test_onObservationFinished_should_set_correct_subject(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationFinished(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][1])
        self.assertIn(self.project_name, self.email_mock.call_args[0][1])

    def test_onObservationFinished_should_set_correct_body(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationFinished(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_sas_id), self.email_mock.call_args[0][2])
        self.assertIn(str(self.obs_mom_id), self.email_mock.call_args[0][2])
        self.assertIn(self.mom_link, self.email_mock.call_args[0][2])

    #### Conflict

    def test_onObservationConflict_should_not_email_when_its_not_a_trigger(self):
        self.momqueryrpc_mock.get_trigger_id.return_value = {'trigger_id': None, 'status': "Error"}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.email_mock.assert_not_called()

    def test_onObservationConflict_should_email_when_its_a_trigger(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.email_mock.assert_called()

    def test_onObservationConflict_should_set_correct_subject(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][1])
        self.assertIn(self.project_name, self.email_mock.call_args[0][1])

    def test_onObservationConflict_should_set_correct_body(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationConflict(self.obs_sas_id, None)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])

    # when_trigger_send_email tests

    @mock.patch('time.sleep', return_value=None)
    def test_when_trigger_send_email_should_limit_the_amount_of_requests(self, _):
        self.momqueryrpc_mock.getMoMIdsForOTDBIds.return_value = {self.obs_sas_id: None}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.assertEqual(10, self.momqueryrpc_mock.getMoMIdsForOTDBIds.call_count)

    @mock.patch('time.sleep', return_value=None)
    def test_when_trigger_send_email_should_log_when_no_mom_id_can_be_found(self, _):
        self.momqueryrpc_mock.getMoMIdsForOTDBIds.return_value = {self.obs_sas_id: None}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        self.logger_mock.error.assert_any_call("Could not retrieve a mom_id for otdb_id: %s", self.obs_sas_id)

    @mock.patch('time.sleep', return_value=None)
    def test_when_trigger_send_email_should_wait_three_seconds_between_retries(self, sleep_mock):
        self.momqueryrpc_mock.getMoMIdsForOTDBIds.return_value = {self.obs_sas_id: None}

        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.onObservationAborted(self.obs_sas_id, None)

        sleep_mock.assert_called_with(3)
        self.assertEqual(10, sleep_mock.call_count)

    def test_when_trigger_send_email_should_log_when_sending_email(self):
        handler = OTDBTriggerHandler(self.momqueryrpc_mock)

        handler.when_trigger_send_email(self.obs_sas_id, "", "")

        self.logger_mock.info.assert_any_call(
            "Emailing otdb_id: %s, mom_id: %s, trigger_id: %s, template_subject: %s, template_body: %s",
            self.obs_sas_id, self.obs_mom_id, self.trigger_id, "", "")


class TestTriggerNotificationHandler(unittest.TestCase):
    project_name = "test_lofar"
    project_mom_id = 33
    trigger_id = 1
    obs_sas_id = 22
    obs_mom_id = 44
    start_time = "2016-11-23 15:21:44"
    stop_time = "2016-11-23 16:21:44"
    min_start_time = "2017-05-23 15:21:44"
    max_end_time = "2017-05-23 17:21:44"

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<trigger:trigger xsi:schemaLocation="http://www.astron.nl/LofarTrigger LofarTrigger.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:spec="http://www.astron.nl/LofarSpecification"
        xmlns:trigger="http://www.astron.nl/LofarTrigger" xmlns:base="http://www.astron.nl/LofarBase">
        <version>version</version>
        <name>name</name>
        <description>description</description>
        <projectReference>
                <ProjectCode>test-lofar</ProjectCode>
        </projectReference>
        <contactInformation>
                <name>Sander ter Veen</name>
                <email>veen@astron.nl</email>
                <phoneNumber>711</phoneNumber>
                <affiliation>ASTRON</affiliation>
        </contactInformation>
        <userName>veen</userName>
        <comment>comment</comment>
        <event>
                <identification>none</identification>
                <description>none</description>
                <type>VOEvent</type>
        </event>
        <specification>
                <version>2.20</version>
                <projectReference>
                        <ProjectCode>test-lofar</ProjectCode>
                </projectReference>
                <userName>veen</userName>
                <comment>comment</comment>
                <generatorName>Jan David Mol</generatorName>
                <generatorVersion>0.0</generatorVersion>

                <!-- folders -->
                <container>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>100</identifier>
                        </temporaryIdentifier>
                        <addToExistingContainer>false</addToExistingContainer>
                        <folder>
                                <name>TARGET_A</name>
                                <description>First target</description>
                                <topology>0</topology>
                        </folder>
                </container>
                <container>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>101</identifier>
                        </temporaryIdentifier>
                        <addToExistingContainer>false</addToExistingContainer>
                        <folder>
                                <name>AARTFAAC-TRIGGERED</name>
                                <description>Triggered observation by AARTFAAC (Preprocessing)</description>
                                <topology>0</topology>
                        </folder>
                </container>

                <!-- observation -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>200</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <observation>
                                <name>Target/1/TO</name>
                                <description>Target/1/TO (Target Observation)</description>
                                <instrument>Beam Observation</instrument>
                                <defaultTemplate>BeamObservation</defaultTemplate>
                                <tbbPiggybackAllowed>true</tbbPiggybackAllowed>
                                <aartfaacPiggybackAllowed>true</aartfaacPiggybackAllowed>
                                <correlatedData>true</correlatedData>
                                <coherentStokesData>false</coherentStokesData>
                                <incoherentStokesData>false</incoherentStokesData>
                                <antenna>LBA Outer</antenna>
                                <clock units="MHz">200</clock>
                                <instrumentFilter>30-90 MHz</instrumentFilter>
                                <integrationInterval>2.0</integrationInterval>
                                <channelsPerSubband>64</channelsPerSubband>
                                <bypassPff>false</bypassPff>
                                <enableSuperterp>false</enableSuperterp>
                                <numberOfBitsPerSample>8</numberOfBitsPerSample>
                                <stationSelectionSpecification>
                                        <stationSelection>
                                                <stationSet>Custom</stationSet>
                                                <stations>
                                                        <station><name>CS001</name></station>
                                                        <station><name>CS002</name></station>
                                                        <station><name>CS003</name></station>
                                                        <station><name>CS004</name></station>
                                                        <station><name>CS005</name></station>
                                                        <station><name>CS006</name></station>
                                                        <station><name>CS007</name></station>
                                                        <station><name>CS011</name></station>
                                                        <station><name>CS013</name></station>
                                                        <station><name>CS017</name></station>
                                                        <station><name>CS021</name></station>
                                                        <station><name>CS024</name></station>
                                                        <station><name>CS026</name></station>
                                                        <station><name>CS028</name></station>
                                                        <station><name>CS030</name></station>
                                                        <station><name>CS031</name></station>
                                                        <station><name>CS032</name></station>
                                                        <station><name>CS101</name></station>
                                                        <station><name>CS103</name></station>
                                                        <station><name>CS201</name></station>
                                                        <station><name>CS301</name></station>
                                                        <station><name>CS302</name></station>
                                                        <station><name>CS401</name></station>
                                                        <station><name>CS501</name></station>
                                                        <station><name>RS106</name></station>
                                                        <station><name>RS205</name></station>
                                                        <station><name>RS208</name></station>
                                                        <station><name>RS210</name></station>
                                                        <station><name>RS305</name></station>
                                                        <station><name>RS306</name></station>
                                                        <station><name>RS307</name></station>
                                                        <station><name>RS310</name></station>
                                                        <station><name>RS406</name></station>
                                                        <station><name>RS407</name></station>
                                                        <station><name>RS409</name></station>
                                                        <station><name>RS503</name></station>
                                                        <station><name>RS508</name></station>
                                                        <station><name>RS509</name></station>
                                                </stations>
                                        </stationSelection>
                                </stationSelectionSpecification>
                                <timeWindowSpecification>
                                        <timeFrame>UT</timeFrame>
                                        <startTime>2016-11-23T15:21:44</startTime>
                                        <duration>
                                                <duration>PT3600S</duration>
                                        </duration>
                                </timeWindowSpecification>
                        </observation>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- SAP 0 -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>300</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <measurement xsi:type="base:BeamMeasurement">
                                <name>Target</name>
                                <description>Target</description>
                                <ra>204.648425</ra>
                                <dec>-0.172222222222</dec>
                                <equinox>J2000</equinox>
                                <subbandsSpecification>
                                        <subbands>160..399</subbands>
                                </subbandsSpecification>
                                <measurementType>Target</measurementType>
                        </measurement>

                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

        <!-- SAP 1 -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>301</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <measurement xsi:type="base:BeamMeasurement">
                                <name>Calibrator</name>
                                <description>Calibrator</description>
                                <ra>123.400291667</ra>
                                <dec>48.2173833333</dec>
                                <equinox>J2000</equinox>
                                <subbandsSpecification>
                                        <subbands>160..339</subbands>
                                </subbandsSpecification>
                                <measurementType>Calibration</measurementType>
                        </measurement>

                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- Calibrator Averaging Pipeline -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>201</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <pipeline xsi:type="base:AveragingPipeline">
                                <name>Calibrator/1/CPT</name>
                                <description>Calibrator/1/CPT (Preprocessing)</description>
                                <processingCluster>
                                        <name>CEP4</name>
                                        <partition>cpu</partition>
                                        <numberOfTasks>24</numberOfTasks>
                                        <minRAMPerTask unit="byte">1000000000</minRAMPerTask>
                                        <minScratchPerTask unit="byte">100000000</minScratchPerTask>    
                                        <maxDurationPerTask>PT600S</maxDurationPerTask>
                                        <numberOfCoresPerTask>20</numberOfCoresPerTask>
                                        <runSimultaneous>true</runSimultaneous>
                                </processingCluster>
                                <defaultTemplate>Preprocessing Pipeline</defaultTemplate>
                                <demixingParameters>
                                        <averagingFreqStep>16</averagingFreqStep>
                                        <averagingTimeStep>1</averagingTimeStep>
                                        <demixFreqStep>16</demixFreqStep>
                                        <demixTimeStep>5</demixTimeStep>
                                        <demixAlways />
                                        <demixIfNeeded />
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- Target Averaging Pipeline -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>202</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <pipeline xsi:type="base:AveragingPipeline">
                                <name>Calibrator/1/CPT</name>
                                <description>Calibrator/1/CPT (Preprocessing)</description>
                                <processingCluster>
                                        <name>CEP4</name>
                                        <partition>cpu</partition>
                                        <numberOfTasks>24</numberOfTasks>
                                        <minRAMPerTask unit="byte">1000000000</minRAMPerTask>
                                        <minScratchPerTask unit="byte">100000000</minScratchPerTask>    
                                        <maxDurationPerTask>PT600S</maxDurationPerTask>
                                        <numberOfCoresPerTask>20</numberOfCoresPerTask>
                                        <runSimultaneous>true</runSimultaneous>
                                </processingCluster>
                                <defaultTemplate>Preprocessing Pipeline</defaultTemplate>
                                <demixingParameters>
                                        <averagingFreqStep>16</averagingFreqStep>
                                        <averagingTimeStep>1</averagingTimeStep>
                                        <demixFreqStep>16</demixFreqStep>
                                        <demixTimeStep>5</demixTimeStep>
                                        <demixAlways />
                                        <demixIfNeeded />
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

        <!-- SAP 0 data products -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>400</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>

                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- SAP 1 data products -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>401</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- Calibrator Pipeline dataproducts -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>402</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- Target Pipeline dataproducts -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>403</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

                <!-- folder 101 is child of folder 100 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>100</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>101</identifier>
                        </child>
                        <type>folder-folder</type>
                </relation>

                <!-- observation 200 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>200</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- measurements 300 is a child of observation 200 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>200</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>300</identifier>
                        </child>
                        <type>observation-measurement</type>
                </relation>

                <!-- measurement 301 is a child of observation 200 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>200</identifier>
                                <description>0</description>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>301</identifier>
                                <description>0</description>
                        </child>
                        <type>observation-measurement</type>
                </relation>

                <!-- dataproducts 400 are output of measurement 300 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>400</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>300</identifier>
                        </activity>
                        <type>producer</type>
                </relation>

                <!-- dataproducts 401 are output of measurement 301 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>401</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>301</identifier>
                        </activity>
                        <type>producer</type>
                </relation>


        <!-- SAP 1 is the calibrator for SAP 0 -->
                <relation xsi:type="spec:TwinRelation">
                        <first>
                                <source>0</source>
                                <identifier>301</identifier>
                        </first>
                        <second>
                                <source>0</source>
                                <identifier>300</identifier>
                        </second>
                        <type>calibrator-target</type>
                </relation>


                <!-- dataproducts 401 are input for pipeline 201 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>401</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>201</identifier>
                        </activity>
                        <type>user</type>
                </relation>

                <!-- dataproducts 402 are output of pipeline 201 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>402</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>201</identifier>
                        </activity>
                        <type>producer</type>
                </relation>

                <!-- pipeline 201 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>201</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- dataproducts 400 are input for pipeline 202 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>400</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>202</identifier>
                        </activity>
                        <type>user</type>
                </relation>

                <!-- pipeline 202 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>202</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- dataproducts 403 are output of pipeline 202 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>403</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>202</identifier>
                        </activity>
                        <type>producer</type>
                </relation>
        </specification>
        <generatorName>Jan David Mol</generatorName>
        <generatorVersion>0.0</generatorVersion>
</trigger:trigger>
"""
    xml_dwell = """<?xml version="1.0" encoding="UTF-8"?>
<trigger:trigger xsi:schemaLocation="http://www.astron.nl/LofarTrigger LofarTrigger.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:spec="http://www.astron.nl/LofarSpecification"
        xmlns:trigger="http://www.astron.nl/LofarTrigger" xmlns:base="http://www.astron.nl/LofarBase">
        <version>version</version>
        <name>name</name>
        <description>description</description>
        <projectReference>
                <ProjectCode>test-lofar</ProjectCode>
        </projectReference>
        <contactInformation>
                <name>Sander ter Veen</name>
                <email>veen@astron.nl</email>
                <phoneNumber>711</phoneNumber>
                <affiliation>ASTRON</affiliation>
        </contactInformation>
        <userName>veen</userName>
        <comment>comment</comment>
        <event>
                <identification>none</identification>
                <description>none</description>
                <type>VOEvent</type>
        </event>
        <specification>
                <version>2.20</version>
                <projectReference>
                        <ProjectCode>test-lofar</ProjectCode>
                </projectReference>
                <userName>veen</userName>
                <comment>comment</comment>
                <generatorName>Jan David Mol</generatorName>
                <generatorVersion>0.0</generatorVersion>

                <!-- folders -->
                <container>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>100</identifier>
                        </temporaryIdentifier>
                        <addToExistingContainer>false</addToExistingContainer>
                        <folder>
                                <name>TARGET_A</name>
                                <description>First target</description>
                                <topology>0</topology>
                        </folder>
                </container>
                <container>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>101</identifier>
                        </temporaryIdentifier>
                        <addToExistingContainer>false</addToExistingContainer>
                        <folder>
                                <name>AARTFAAC-TRIGGERED</name>
                                <description>Triggered observation by AARTFAAC (Preprocessing)</description>
                                <topology>0</topology>
                        </folder>
                </container>

                <!-- observation -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>200</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <observation>
                                <name>Target/1/TO</name>
                                <description>Target/1/TO (Target Observation)</description>
                                <instrument>Beam Observation</instrument>
                                <defaultTemplate>BeamObservation</defaultTemplate>
                                <tbbPiggybackAllowed>true</tbbPiggybackAllowed>
                                <aartfaacPiggybackAllowed>true</aartfaacPiggybackAllowed>
                                <correlatedData>true</correlatedData>
                                <coherentStokesData>false</coherentStokesData>
                                <incoherentStokesData>false</incoherentStokesData>
                                <antenna>LBA Outer</antenna>
                                <clock units="MHz">200</clock>
                                <instrumentFilter>30-90 MHz</instrumentFilter>
                                <integrationInterval>2.0</integrationInterval>
                                <channelsPerSubband>64</channelsPerSubband>
                                <bypassPff>false</bypassPff>
                                <enableSuperterp>false</enableSuperterp>
                                <numberOfBitsPerSample>8</numberOfBitsPerSample>
                                <stationSelectionSpecification>
                                        <stationSelection>
                                                <stationSet>Custom</stationSet>
                                                <stations>
                                                        <station><name>CS001</name></station>
                                                        <station><name>CS002</name></station>
                                                        <station><name>CS003</name></station>
                                                        <station><name>CS004</name></station>
                                                        <station><name>CS005</name></station>
                                                        <station><name>CS006</name></station>
                                                        <station><name>CS007</name></station>
                                                        <station><name>CS011</name></station>
                                                        <station><name>CS013</name></station>
                                                        <station><name>CS017</name></station>
                                                        <station><name>CS021</name></station>
                                                        <station><name>CS024</name></station>
                                                        <station><name>CS026</name></station>
                                                        <station><name>CS028</name></station>
                                                        <station><name>CS030</name></station>
                                                        <station><name>CS031</name></station>
                                                        <station><name>CS032</name></station>
                                                        <station><name>CS101</name></station>
                                                        <station><name>CS103</name></station>
                                                        <station><name>CS201</name></station>
                                                        <station><name>CS301</name></station>
                                                        <station><name>CS302</name></station>
                                                        <station><name>CS401</name></station>
                                                        <station><name>CS501</name></station>
                                                        <station><name>RS106</name></station>
                                                        <station><name>RS205</name></station>
                                                        <station><name>RS208</name></station>
                                                        <station><name>RS210</name></station>
                                                        <station><name>RS305</name></station>
                                                        <station><name>RS306</name></station>
                                                        <station><name>RS307</name></station>
                                                        <station><name>RS310</name></station>
                                                        <station><name>RS406</name></station>
                                                        <station><name>RS407</name></station>
                                                        <station><name>RS409</name></station>
                                                        <station><name>RS503</name></station>
                                                        <station><name>RS508</name></station>
                                                        <station><name>RS509</name></station>
                                                </stations>
                                        </stationSelection>
                                </stationSelectionSpecification>
                                <timeWindowSpecification>
                                        <timeFrame>UT</timeFrame>
                                        <minStartTime>2017-05-23T15:21:44</minStartTime>
                                        <maxEndTime>2017-05-23T17:21:44</maxEndTime>
                                        <duration>
                                                <duration>PT3600S</duration>
                                        </duration>
                                </timeWindowSpecification>
                        </observation>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- SAP 0 -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>300</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <measurement xsi:type="base:BeamMeasurement">
                                <name>Target</name>
                                <description>Target</description>
                                <ra>204.648425</ra>
                                <dec>-0.172222222222</dec>
                                <equinox>J2000</equinox>
                                <subbandsSpecification>
                                        <subbands>160..399</subbands>
                                </subbandsSpecification>
                                <measurementType>Target</measurementType>
                        </measurement>

                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

        <!-- SAP 1 -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>301</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <measurement xsi:type="base:BeamMeasurement">
                                <name>Calibrator</name>
                                <description>Calibrator</description>
                                <ra>123.400291667</ra>
                                <dec>48.2173833333</dec>
                                <equinox>J2000</equinox>
                                <subbandsSpecification>
                                        <subbands>160..339</subbands>
                                </subbandsSpecification>
                                <measurementType>Calibration</measurementType>
                        </measurement>

                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- Calibrator Averaging Pipeline -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>201</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <pipeline xsi:type="base:AveragingPipeline">
                                <name>Calibrator/1/CPT</name>
                                <description>Calibrator/1/CPT (Preprocessing)</description>
                                <processingCluster>
                                        <name>CEP4</name>
                                        <partition>cpu</partition>
                                        <numberOfTasks>24</numberOfTasks>
                                        <minRAMPerTask unit="byte">1000000000</minRAMPerTask>
                                        <minScratchPerTask unit="byte">100000000</minScratchPerTask>
                                        <maxDurationPerTask>PT600S</maxDurationPerTask>
                                        <numberOfCoresPerTask>20</numberOfCoresPerTask>
                                        <runSimultaneous>true</runSimultaneous>
                                </processingCluster>
                                <defaultTemplate>Preprocessing Pipeline</defaultTemplate>
                                <demixingParameters>
                                        <averagingFreqStep>16</averagingFreqStep>
                                        <averagingTimeStep>1</averagingTimeStep>
                                        <demixFreqStep>16</demixFreqStep>
                                        <demixTimeStep>5</demixTimeStep>
                                        <demixAlways />
                                        <demixIfNeeded />
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

                <!-- Target Averaging Pipeline -->
                <activity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>202</identifier>
                                <description>0</description>
                        </temporaryIdentifier>
                        <pipeline xsi:type="base:AveragingPipeline">
                                <name>Calibrator/1/CPT</name>
                                <description>Calibrator/1/CPT (Preprocessing)</description>
                                <processingCluster>
                                        <name>CEP4</name>
                                        <partition>cpu</partition>
                                        <numberOfTasks>24</numberOfTasks>
                                        <minRAMPerTask unit="byte">1000000000</minRAMPerTask>
                                        <minScratchPerTask unit="byte">100000000</minScratchPerTask>
                                        <maxDurationPerTask>PT600S</maxDurationPerTask>
                                        <numberOfCoresPerTask>20</numberOfCoresPerTask>
                                        <runSimultaneous>true</runSimultaneous>
                                </processingCluster>
                                <defaultTemplate>Preprocessing Pipeline</defaultTemplate>
                                <demixingParameters>
                                        <averagingFreqStep>16</averagingFreqStep>
                                        <averagingTimeStep>1</averagingTimeStep>
                                        <demixFreqStep>16</demixFreqStep>
                                        <demixTimeStep>5</demixTimeStep>
                                        <demixAlways />
                                        <demixIfNeeded />
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>10</priority>
                        <triggerId>
                                <source>0</source>
                                <identifier>0</identifier>
                        </triggerId>
                </activity>

        <!-- SAP 0 data products -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>400</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>

                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- SAP 1 data products -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>401</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- Calibrator Pipeline dataproducts -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>402</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

        <!-- Target Pipeline dataproducts -->
                <entity>
                        <temporaryIdentifier>
                                <source>0</source>
                                <identifier>403</identifier>
                        </temporaryIdentifier>
                        <dataproductType>UVDataProduct</dataproductType>
                        <storageCluster>
                                <name>CEP4</name>
                                <partition>/data/projects/</partition>
                        </storageCluster>
                </entity>

                <!-- folder 101 is child of folder 100 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>100</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>101</identifier>
                        </child>
                        <type>folder-folder</type>
                </relation>

                <!-- observation 200 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>200</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- measurements 300 is a child of observation 200 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>200</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>300</identifier>
                        </child>
                        <type>observation-measurement</type>
                </relation>

                <!-- measurement 301 is a child of observation 200 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>200</identifier>
                                <description>0</description>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>301</identifier>
                                <description>0</description>
                        </child>
                        <type>observation-measurement</type>
                </relation>

                <!-- dataproducts 400 are output of measurement 300 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>400</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>300</identifier>
                        </activity>
                        <type>producer</type>
                </relation>

                <!-- dataproducts 401 are output of measurement 301 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>401</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>301</identifier>
                        </activity>
                        <type>producer</type>
                </relation>


        <!-- SAP 1 is the calibrator for SAP 0 -->
                <relation xsi:type="spec:TwinRelation">
                        <first>
                                <source>0</source>
                                <identifier>301</identifier>
                        </first>
                        <second>
                                <source>0</source>
                                <identifier>300</identifier>
                        </second>
                        <type>calibrator-target</type>
                </relation>


                <!-- dataproducts 401 are input for pipeline 201 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>401</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>201</identifier>
                        </activity>
                        <type>user</type>
                </relation>

                <!-- dataproducts 402 are output of pipeline 201 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>402</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>201</identifier>
                        </activity>
                        <type>producer</type>
                </relation>

                <!-- pipeline 201 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>201</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- dataproducts 400 are input for pipeline 202 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>400</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>202</identifier>
                        </activity>
                        <type>user</type>
                </relation>

                <!-- pipeline 202 is child of folder 101 -->
                <relation xsi:type="spec:ChildRelation">
                        <parent>
                                <source>0</source>
                                <identifier>101</identifier>
                        </parent>
                        <child>
                                <source>0</source>
                                <identifier>202</identifier>
                        </child>
                        <type>folder-activity</type>
                </relation>

                <!-- dataproducts 403 are output of pipeline 202 -->
                <relation xsi:type="spec:ActivityEntityRelation">
                        <entity>
                                <source>0</source>
                                <identifier>403</identifier>
                        </entity>
                        <activity>
                                <source>0</source>
                                <identifier>202</identifier>
                        </activity>
                        <type>producer</type>
                </relation>
        </specification>
        <generatorName>Jan David Mol</generatorName>
        <generatorVersion>0.0</generatorVersion>
</trigger:trigger>
"""

    message_content = {
        "trigger_id": trigger_id,
        "project": project_name,
        "metadata": xml
    }

    dwell_message_content = {
        "trigger_id": trigger_id,
        "project": project_name,
        "metadata": xml_dwell
    }


    def setUp(self):
        self.momqueryrpc_mock = mock.MagicMock()
        self.momqueryrpc_mock.getProjects.return_value = [{"name": self.project_name, "mom2id": self.project_mom_id}]
        self.momqueryrpc_mock.get_project_details.return_value = {
            "author_email": "author@example.com", "pi_email": "pi@example.com"
        }

        email_patcher = mock.patch('lofar.sas.TriggerEmailService.TriggerEmailService.email')
        self.addCleanup(email_patcher.stop)
        self.email_mock = email_patcher.start()

        self.message = mock.MagicMock()
        self.message.content = self.message_content

        self.dwell_message = mock.MagicMock()
        self.dwell_message.content = self.dwell_message_content

    def test_start_handling_should_open_momquery_rpc(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.start_handling()

        self.momqueryrpc_mock.open.assert_called()

    def test_stop_handling_should_close_momquery_rpc(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.stop_handling()

        self.momqueryrpc_mock.close.assert_called()

    def test_handleMessage_should_email(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.handle_message(self.message)

        self.email_mock.assert_called()

    def test_handleMessage_should_set_correct_subject(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.handle_message(self.message)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][1])
        self.assertIn(self.project_name, self.email_mock.call_args[0][1])

    def test_handleMessage_should_set_correct_body(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.handle_message(self.message)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])
        self.assertIn(str(self.start_time), self.email_mock.call_args[0][2])
        self.assertIn(str(self.stop_time), self.email_mock.call_args[0][2])

    def test_handleMessage_should_set_correct_body_for_dwell_spec(self):
        handler = TriggerNotificationHandler(self.momqueryrpc_mock)

        handler.handle_message(self.dwell_message)

        self.assertIn(str(self.trigger_id), self.email_mock.call_args[0][2])
        self.assertIn(self.project_name, self.email_mock.call_args[0][2])
        self.assertIn(str(self.min_start_time), self.email_mock.call_args[0][2])
        self.assertIn(str(self.max_end_time), self.email_mock.call_args[0][2])


if __name__ == "__main__":
    unittest.main()
