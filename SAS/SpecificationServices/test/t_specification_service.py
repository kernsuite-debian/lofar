#!/usr/bin/env python3

# Copyright (C) 2012-2017 ASTRON (Netherlands Institute for Radio Astronomy)
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

from lofar.specificationservices.specification_service import SpecificationHandler


class TestSpecificationHandler(unittest.TestCase):
    # TODO read from test xml file after merge
    xml = '''<spec:specification xmlns:base="http://www.astron.nl/LofarBase" xmlns:spec="http://www.astron.nl/LofarSpecification" xmlns:trigger="http://www.astron.nl/LofarTrigger" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><version>2.20</version>
                <projectReference>
                        <ProjectCode>LC7_030</ProjectCode>
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
                        <priority>1010</priority>
                        <triggerId><source>MoM</source><identifier>1</identifier></triggerId></activity>

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
                        <priority>1010</priority>
                        <triggerId><source>MoM</source><identifier>1</identifier></triggerId></activity>

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
                        <priority>1010</priority>
                        <triggerId><source>MoM</source><identifier>1</identifier></triggerId></activity>

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
                                        <demixAlways/>
                                        <demixIfNeeded/>
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>1010</priority>
                        <triggerId><source>MoM</source><identifier>1</identifier></triggerId></activity>

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
                                        <demixAlways/>
                                        <demixIfNeeded/>
                                        <ignoreTarget>false</ignoreTarget>
                                </demixingParameters>
                                <flaggingStrategy>LBAdefault</flaggingStrategy>
                        </pipeline>
                        <status>approved</status>
                        <qualityOfService>LATENCY</qualityOfService>
                        <priority>1010</priority>
                        <triggerId><source>MoM</source><identifier>1</identifier></triggerId></activity>

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
        </spec:specification>'''

    def setUp(self):
        validationrpc_patcher = mock.patch('lofar.specificationservices.specification_service.ValidationRPC')
        self.addCleanup(validationrpc_patcher.stop)
        self.validationrpc_mock = validationrpc_patcher.start()
        self.validationrpc_mock.create.side_effect = lambda **kwargs: self.validationrpc_mock
        self.validationrpc_mock.validate_mom_specification.return_value = {"valid": True}

        momqueryrpc_patcher = mock.patch('lofar.specificationservices.specification_service.MoMQueryRPC')
        self.addCleanup(momqueryrpc_patcher.stop)
        self.momqueryrpc_mock = momqueryrpc_patcher.start()
        self.momqueryrpc_mock.create.side_effect = lambda **kwargs: self.momqueryrpc_mock

        self.momqueryrpc_mock.folderExists.return_value = {"exists": False}
        self.momqueryrpc_mock.isProjectActive.return_value = {"active": True}

        translationrpc_patcher = mock.patch('lofar.specificationservices.specification_service.TranslationRPC')
        self.addCleanup(translationrpc_patcher.stop)
        self.translationrpc_mock = translationrpc_patcher.start()
        self.translationrpc_mock.create.side_effect = lambda **kwargs: self.translationrpc_mock

        momimportxml_bus_patcher = mock.patch('lofar.specificationservices.specification_service.ToBusOld')
        self.addCleanup(momimportxml_bus_patcher.stop)
        self.momimportxml_bus_mock = momimportxml_bus_patcher.start()

        self.handler = SpecificationHandler()

    def test_add_specification_should_raise_exception_when_lofax_xml_is_invalid(self):
        self.validationrpc_mock.validate_mom_specification.return_value = {"valid": False, "error": "error message"}

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", self.xml)

        self.assertEqual(str(exception.exception), "Invalid MoM specification: error message")

    def test_add_specification_should_raise_exception_when_spec_does_not_start_correctly(self):
        wrong_root_xml = "<xml></xml>"

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", wrong_root_xml)

        self.assertEqual(exception.exception.args[0], "Unexpected root element: ")

    @unittest.skip("Without this string the test wouldn't actually be skipped!")
    def test_add_specificaiotn_should_raise_exception_when_innermost_folder_exists(self):
        self.momqueryrpc_mock.folderExists.return_value = {"exists": True}

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", self.xml)

        self.assertEqual(str(exception.exception), "Innermost folder already exists: /LC7_030/TARGET_A/AARTFAAC-TRIGGERED/")

    def test_add_specificaiotn_should_raise_exception_when_project_is_not_active(self):
        self.momqueryrpc_mock.isProjectActive.return_value = {"active": False}

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", self.xml)

        self.assertEqual(str(exception.exception), "Project is not active: LC7_030")

    def test_Add_specification_should_raise_exception_when_activity_has_no_status_field(self):
        missing_status_xml = self.xml

        missing_status_xml = missing_status_xml.replace("<status>approved</status>", "", 1)

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", missing_status_xml)

        self.assertEqual("Activity has no status: ('0', '200')", str(exception.exception))

    # TODO test raise Exception("Specified action has to be in folder:

    def test_add_specification_should_raise_exception_when_activity_has_an_unpermitted_action(self):
        unpermitted_action_xml = self.xml

        unpermitted_action_xml = unpermitted_action_xml.replace("observation>", "ingest>", 2)

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", unpermitted_action_xml)

        self.assertTrue(str(exception.exception).startswith("Specified activity is not permitted: ('0', '200')"))

    def test_add_specification_should_raise_exception_when_activity_has_state_other_then_opened_or_approved(self):
        wrong_status_xml = self.xml

        wrong_status_xml = wrong_status_xml.replace("<status>approved</status>", "<status>prescheduled</status>", 1)

        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", wrong_status_xml)

        self.assertEqual("Specified activity is not going to permitted status: ('0', '200') -> 'prescheduled' not in ['opened', 'approved']", str(exception.exception))

    def test_add_specification_should_ask_for_observation_authentication_when_jobtype_is_measurement(self):
        self.handler.add_specification("user", self.xml)

        expected = [mock.call('user', 'LC7_030', 'observation', 'approved'),
                    mock.call('user', 'LC7_030', 'observation', 'approved'),
                    mock.call('user', 'LC7_030', 'observation', 'approved'),
                    mock.call('user', 'LC7_030', 'pipeline', 'approved'),
                    mock.call('user', 'LC7_030', 'pipeline', 'approved')]

        self.assertTrue(self.momqueryrpc_mock.authorized_add_with_status.call_args_list == expected)

    def test_add_specification_should_raise_exception_when_mom_spec_does_not_validate(self):
        self.validationrpc_mock.validate_mom_specification.return_value = {"valid": False, "error": "error message"}
        with self.assertRaises(Exception) as exception:
            self.handler.add_specification("user", self.xml)

        self.assertEqual("Invalid MoM specification: error message", str(exception.exception))

    def test_add_specification_should_send_correctly_translated_spec_to_mom(self):
        self.handler.add_specification("user", self.xml)

        self.assertTrue(any('.send' in call[0] for call in self.momimportxml_bus_mock.mock_calls))

if __name__ == "__main__":
    unittest.main()
