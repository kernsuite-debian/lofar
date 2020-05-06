#!/usr/bin/env python3

# Copyright (C) 2012-2015    ASTRON (Netherlands Institute for Radio Astronomy)
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

# $Id:  $
import unittest
import uuid
from datetime import datetime
from mysql import connector
import logging
import json
from datetime import datetime, timedelta

from lofar.common.datetimeutils import parseDatetime

logger = logging.getLogger(__name__)

from unittest import mock

try:
    import testing.mysqld
except ImportError as e:
    print(str(e))
    print('Please install python3 package testing.mysqld: sudo pip3 install testing.mysqld')
    exit(3)    # special lofar test exit code: skipped test

from lofar.common.dbcredentials import Credentials
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC

from lofar.mom.momqueryservice.momqueryservice import MoMQueryServiceMessageHandler, MoMDatabaseWrapper

trigger_specification = '<?xml version="1.0" encoding="UTF-8"?>\
<p:trigger xsi:schemaLocation="http://www.astron.nl/LofarTrigger LofarTrigger.xsd"\
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:p2="http://www.astron.nl/LofarSpecification"\
    xmlns:p="http://www.astron.nl/LofarTrigger" xmlns:p1="http://www.astron.nl/LofarBase">\
    <version>version</version>\
    <name>name</name>\
    <description>description</description>\
    <projectReference>\
        <ProjectCode>test-lofar</ProjectCode>\
    </projectReference>\
    <contactInformation>\
        <name>name</name>\
        <email>email</email>\
        <phoneNumber>phoneNumber</phoneNumber>\
        <affiliation>affiliation</affiliation>\
    </contactInformation>\
    <userName>holties</userName>\
    <comment>comment</comment>\
    <event>\
        <identification>identification</identification>\
        <description>description</description>\
        <type>VOEvent</type>\
    </event>\
    <specification>\
        <version>version</version>\
        <projectReference>\
            <ProjectCode>test-lofar</ProjectCode>\
        </projectReference>\
        <userName>holties</userName>\
        <comment>comment</comment>\
        <generatorName>generatorVersion</generatorName>\
        <generatorVersion>generatorVersion</generatorVersion>\
    </specification>\
    <generatorName></generatorName>\
    <generatorVersion></generatorVersion>\
</p:trigger>'

single_trigger_result = \
{
    '1':
    {
        'mom_id': '23',
        'project_name': 'project name',
        'arrival_time': '2017-02-24 16:14:05',
        'status': 'finished',
        'momurl_id': '12345'
    },
}

multiple_triggers_result = \
{
    '1':
    {
        'mom_id': '23',
        'project_name': 'project name',
        'arrival_time': '2017-02-24 16:14:05',
        'status': 'finished',
        'momurl_id': '12345'
    },
    '2':
    {
        'mom_id': '32',
        'project_name': 'project name',
        'arrival_time': '2017-02-24 15:14:05',
        'status': 'finished',
        'momurl_id': '54321'
    },
}

# share database for better performance
def populate_db(mysqld):

        connection = connector.connect(**mysqld.dsn())
        cursor = connection.cursor()

         # useradmin db
        cursor.execute("CREATE DATABASE useradministration")
        cursor.execute("CREATE TABLE useradministration.useraccount ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "userid int(11) NOT NULL DEFAULT '0', "
                       "username varchar(20) NOT NULL DEFAULT '', "
                       "password varchar(32) NOT NULL DEFAULT '', "
                       "publickey varchar(32) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "UNIQUE KEY useraccount_UNIQ (username) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1787 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE useradministration.useraccountsystemrole ("
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "useraccountid int(11) NOT NULL DEFAULT '0', "
                       "systemroleid int(11) NOT NULL DEFAULT '0', "
                       "indexid int(11) NOT NULL DEFAULT '0', "
                       "PRIMARY KEY (id), "
                       "KEY useraccount_useraccountsystemrole_IND (useraccountid), "
                       "KEY systemrole_useraccountsystemrole_IND (systemroleid), "
                       "KEY useraccount_index_useraccountsystemrole_IND (indexid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=3413 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE useradministration.user ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "title varchar(100) DEFAULT NULL, "
                       "firstname varchar(100) DEFAULT NULL, "
                       "lastname varchar(100) NOT NULL DEFAULT '', "
                       "email varchar(100) DEFAULT NULL, "
                       "phone1 varchar(100) DEFAULT NULL, "
                       "phone2 varchar(100) DEFAULT NULL, "
                       "fax varchar(100) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY user_lastname_IND (lastname) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1790 DEFAULT CHARSET=latin1")
        # mom database
        cursor.execute("CREATE DATABASE mom")
        cursor.execute("USE mom")
        cursor.execute("CREATE TABLE mom2objectstatus ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "name varchar(255) DEFAULT NULL, "
                       "roles varchar(512) DEFAULT NULL, "
                       "userid int(11) DEFAULT NULL, "
                       "statusid int(11) DEFAULT NULL, "
                       "mom2objectid int(11) DEFAULT NULL, "
                       "indexid int(11) DEFAULT NULL, "
                       "statustime datetime NOT NULL DEFAULT '1000-01-01 00:00:00.000000', "
                       "pending tinyint(1) DEFAULT 0, "
                       "PRIMARY KEY (id) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1725902 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE mom2object ("
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "parentid int(11) DEFAULT NULL, "
                       "indexid int(11) DEFAULT NULL, "
                       "mom2id int(11) NOT NULL DEFAULT 0, "
                       "mom2objecttype char(25) NOT NULL, "
                       "name varchar(100) NOT NULL DEFAULT '', "
                       "description varchar(255) DEFAULT NULL, "
                       "ownerprojectid int(11) DEFAULT NULL, "
                       "currentstatusid int(11) DEFAULT NULL, "
                       "topology varchar(100) DEFAULT NULL, "
                       "predecessor varchar(512) DEFAULT NULL, "
                       "topology_parent tinyint(1) DEFAULT 0, "
                       "group_id int(11) DEFAULT 0, "
                       "datasize bigint(20) DEFAULT 0, "
                       "PRIMARY KEY (id), "
                       "UNIQUE KEY mom2object_UNIQ (mom2id) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=331855 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE status ("
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "code char(15) NOT NULL DEFAULT '', "
                       "type char(20) NOT NULL, "
                       "description varchar(100) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "UNIQUE KEY status_UNIQ (code,type) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=712 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE member ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "projectid int(11) DEFAULT NULL, "
                       "indexid int(11) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY mom2object_member_FK (projectid), "
                       "KEY indexid_IND (indexid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1010 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE registeredmember ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "memberid int(11) DEFAULT NULL, "
                       "userid int(11) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY member_registeredmember_FK (memberid), "
                       "KEY userid_IND (userid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=768 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE memberprojectrole ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "memberid int(11) DEFAULT NULL, "
                       "indexid int(11) DEFAULT NULL, "
                       "projectroleid int(11) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY member_memberprojectrole_FK (memberid), "
                       "KEY projectrole_memberprojectrole_FK (projectroleid), "
                       "KEY indexid_IND (indexid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1167 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE projectrole ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "name char(15) NOT NULL DEFAULT '', "
                       "description varchar(100) DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "UNIQUE KEY projectrole_UNIQ (name) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE project ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "mom2objectid int(11) DEFAULT NULL, "
                       "releasedate date DEFAULT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY mom2object_IND (mom2objectid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=latin1")
        cursor.execute("ALTER TABLE project "
                       "ADD allowtriggers BOOLEAN NOT NULL DEFAULT FALSE AFTER releasedate, "
                       "ADD priority int(11) NOT NULL DEFAULT 1000 AFTER allowtriggers")
        cursor.execute("CREATE TABLE lofar_trigger ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "username varchar(120) NOT NULL DEFAULT '', "
                       "hostname varchar(128) NOT NULL DEFAULT '', "
                       "arrivaltime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                       "projectname varchar(100) NOT NULL DEFAULT '', "
                       "metadata TEXT NOT NULL, "
                       "cancelled BOOLEAN NOT NULL DEFAULT 0, "
                       "cancelled_at timestamp NULL, "
                       "cancelled_reason char(255), "
                       "PRIMARY KEY (id), "
                       "FOREIGN KEY (username) REFERENCES useradministration.useraccount(username)"
                       ") ")
        cursor.execute("CREATE TABLE lofar_observation ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "mom2objectid int(11) DEFAULT NULL, "
                       "observation_id int(11) DEFAULT NULL, "
                       "instrument char(32) DEFAULT NULL, "
                       "user_specification_id int(11) DEFAULT NULL, "
                       "system_specification_id int(11) DEFAULT NULL,"
                       "default_template varchar(50) DEFAULT NULL,"
                       "tbb_template varchar(50) DEFAULT NULL,"
                       "tbb_piggyback_allowed tinyint(1) DEFAULT '0',"
                       "parset mediumtext,"
                       "nr_output_correlated int(11) DEFAULT NULL,"
                       "nr_output_beamformed int(11) DEFAULT NULL,"
                       "nr_output_coherent_stokes int(11) DEFAULT NULL,"
                       "nr_output_incoherent_stokes int(11) DEFAULT NULL,"
                       "nr_output_flyseye int(11) DEFAULT NULL,"
                       "nr_output_correlated_valid int(11) DEFAULT NULL,"
                       "nr_output_beamformed_valid int(11) DEFAULT NULL,"
                       "nr_output_coherent_stokes_valid int(11) DEFAULT NULL,"
                       "nr_output_incoherent_stokes_valid int(11) DEFAULT NULL,"
                       "nr_output_flyseye_valid int(11) DEFAULT NULL,"
                       "feedback text,"
                       "aartfaac_piggyback_allowed bit(1) DEFAULT b'1',"
                       "storage_cluster_id int(11) DEFAULT NULL,"
                       "processing_cluster_id int(11) DEFAULT NULL,"
                       "nico_testing int(11) DEFAULT NULL,"
                       "PRIMARY KEY (id),"
                       "KEY lofar_observation_observation_id_IND (observation_id),"
                       "KEY mom2object_lofar_observation_FK (mom2objectid),"
                       "KEY user_specification_lofar_observation_FK (user_specification_id),"
                       "KEY system_specification_lofar_observation_FK (system_specification_id)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=52874 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE lofar_observation_specification ("
                       "id int(11) NOT NULL AUTO_INCREMENT,"
                       "type char(8) DEFAULT NULL,"
                       "correlated_data tinyint(1) DEFAULT '1',"
                       "filtered_data tinyint(1) DEFAULT '0',"
                       "beamformed_data tinyint(1) DEFAULT '0',"
                       "coherent_stokes_data tinyint(1) DEFAULT '0',"
                       "incoherent_stokes_data tinyint(1) DEFAULT '0',"
                       "antenna char(20) DEFAULT NULL,"
                       "clock_mode char(10) DEFAULT NULL,"
                       "instrument_filter char(15) DEFAULT NULL,"
                       "integration_interval double DEFAULT NULL,"
                       "channels_per_subband int(11) DEFAULT NULL,"
                       "cn_integration_steps int(11) DEFAULT NULL,"
                       "pencilbeams_flyseye tinyint(1) DEFAULT '0',"
                       "pencilbeams_nr_pencil_rings int(11) DEFAULT NULL,"
                       "pencilbeams_ring_size double DEFAULT NULL,"
                       "stokes_selection char(4) DEFAULT NULL,"
                       "stokes_integrate_channels tinyint(1) DEFAULT NULL,"
                       "stokes_integration_steps int(11) unsigned DEFAULT NULL,"
                       "station_set char(15) DEFAULT NULL,"
                       "timeframe char(4) DEFAULT NULL,"
                       "starttime datetime DEFAULT NULL,"
                       "endtime datetime DEFAULT NULL,"
                       "spec_duration double DEFAULT NULL,"
                       "coherent_dedisperse_channels tinyint(1) DEFAULT '0',"
                       "dispersion_measure float DEFAULT NULL,"
                       "subbands_per_file_cs int(11) DEFAULT NULL,"
                       "subbands_per_file_bf int(11) DEFAULT NULL,"
                       "collapsed_channels_cs int(11) DEFAULT NULL,"
                       "collapsed_channels_is int(11) DEFAULT NULL,"
                       "downsampling_steps_cs int(11) DEFAULT NULL,"
                       "downsampling_steps_is int(11) DEFAULT NULL,"
                       "which_cs char(4) DEFAULT NULL,"
                       "which_is char(4) DEFAULT NULL,"
                       "bypass_pff tinyint(1) DEFAULT '0',"
                       "enable_superterp tinyint(1) DEFAULT '0',"
                       "flyseye tinyint(1) DEFAULT '0',"
                       "tab_nr_rings int(11) DEFAULT NULL,"
                       "tab_ring_size float DEFAULT NULL,"
                       "bits_per_sample int(11) DEFAULT NULL,"
                       "misc text,"
                       "PRIMARY KEY (id),"
                       "KEY lofar_observation_specification_type_IND (type)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=105645 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE lofar_pipeline ("
                       "id int(11) NOT NULL AUTO_INCREMENT,"
                       "mom2objectid int(11) DEFAULT NULL,"
                       "starttime datetime DEFAULT NULL,"
                       "endtime datetime DEFAULT NULL,"
                       "pipeline_id int(11) DEFAULT NULL,"
                       "pending tinyint(1) DEFAULT '0',"
                       "template varchar(100) DEFAULT NULL,"
                       "runtimeDirectory varchar(255) DEFAULT NULL,"
                       "resultDirectory varchar(255) DEFAULT NULL,"
                       "workingDirectory varchar(255) DEFAULT NULL,"
                       "parset longtext,"
                       "nr_output_correlated int(11) DEFAULT NULL,"
                       "nr_output_beamformed int(11) DEFAULT NULL,"
                       "nr_output_instrument_model int(11) DEFAULT NULL,"
                       "nr_output_skyimage int(11) DEFAULT NULL,"
                       "nr_output_correlated_valid int(11) DEFAULT NULL,"
                       "nr_output_beamformed_valid int(11) DEFAULT NULL,"
                       "nr_output_instrument_model_valid int(11) DEFAULT NULL,"
                       "nr_output_skyimage_valid int(11) DEFAULT NULL,"
                       "feedback text,"
                       "demixing_parameters_id int(11) DEFAULT NULL,"
                       "bbs_parameters_id int(11) DEFAULT NULL,"
                       "duration double DEFAULT NULL,"
                       "storage_cluster_id int(11) DEFAULT NULL,"
                       "processing_cluster_id int(11) DEFAULT NULL,"
                       "misc text,"
                       "PRIMARY KEY (id),"
                       "KEY lofar_pipeline_pipeline_id_IND (pipeline_id),"
                       "KEY mom2object_lofar_pipeline_FK (mom2objectid),"
                       "KEY demixing_parameters_FK (demixing_parameters_id),"
                       "KEY bbs_parameters_FK (bbs_parameters_id)"
                       ") ENGINE=InnoDB AUTO_INCREMENT=75471 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE resource ("
                       "id int(11) NOT NULL auto_increment,"
                       "projectid int(11) default NULL,"
                       "resourcetypeid int(11) NOT NULL,"
                       "allocation double default NULL,"
                       "used double default NULL,"
                       "unit varchar(50) NOT NULL DEFAULT '',"
                       "projectpath varchar(255) default NULL,"
                       "PRIMARY KEY (id),"
                       "KEY resourcetype_resource_IND (resourcetypeid),"
                       "KEY mom2object_resource_FK (projectid)"
                       # "CONSTRAINT mom2object_resource_FK FOREIGN KEY (projectid) REFERENCES mom2object (id) ON DELETE CASCADE ON UPDATE NO ACTION,"
                       # "CONSTRAINT resourcetype_resource_FK FOREIGN KEY (resourcetypeid) REFERENCES resourcetype (id)"
                       ") ENGINE=InnoDB DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE  resourcetype ("
                       "id int(11) NOT NULL auto_increment, "
                       "name varchar(255) NOT NULL, "
                       "hosturi varchar(255) default NULL,"
                       "type varchar(50) NOT NULL,"
                       "PRIMARY KEY (id),"
                       "KEY resourcetype_name_IND (name)"
                       ") ENGINE=InnoDB DEFAULT CHARSET=latin1")
        # mom privilege
        cursor.execute("CREATE DATABASE momprivilege")
        cursor.execute("CREATE TABLE momprivilege.statustransitionrole ( "
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "statustransitionid int(11) DEFAULT NULL, "
                       "roleid int(11) NOT NULL, "
                       "roletype char(100) NOT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY roletype_IND (roleid,roletype), "
                       "KEY statustransition_statustransitionrole_FK (statustransitionid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=8572 DEFAULT CHARSET=latin1")
        cursor.execute("CREATE TABLE momprivilege.statustransition ("
                       "id int(11) NOT NULL AUTO_INCREMENT, "
                       "oldstatusid int(11) NOT NULL, "
                       "newstatusid int(11) NOT NULL, "
                       "PRIMARY KEY (id), "
                       "KEY oldstatus_IND (oldstatusid), "
                       "KEY newstatus_IND (oldstatusid) "
                       ") ENGINE=InnoDB AUTO_INCREMENT=1272 DEFAULT CHARSET=latin1")
        cursor.close()
        connection.commit()
        connection.close()


Mysqld = None # testing.mysqld.MysqldFactory(cache_initialized_db = True, on_initialized = populate_db)

def tearDownModule():
    # clear cached database at end of tests
    if Mysqld:
        Mysqld.clear_cache()

class TestMoMQueryServiceMessageHandler(unittest.TestCase):
    database_credentials = Credentials()
    database_credentials.host = "localhost"
    database_credentials.user = "root"
    database_credentials.database = "testdb"
    database_credentials.password = None
    database_credentials.config = {"useradministration_database": "useradministration",
                                   "momprivilege_database": "momprivilege"}

    project_name = "project name"
    folder = "/project/folder"

    def setUp(self):
        tobus_patcher = mock.patch("lofar.messaging.ToBus")
        self.addCleanup(tobus_patcher.stop)
        self.tobus_mock = tobus_patcher.start()

        mom_database_wrapper_patcher = mock.patch('lofar.mom.momqueryservice.momqueryservice.MoMDatabaseWrapper')
        self.addCleanup(mom_database_wrapper_patcher.stop)
        self.mom_database_wrapper_mock = mom_database_wrapper_patcher.start()

        self.project_details_query_handler = MoMQueryServiceMessageHandler(dbcreds = self.database_credentials)
        self.project_details_query_handler.init_tobus()
        self.project_details_query_handler.start_handling()

    def test_IsProjectActive_returns_active_true_when_mom_wrapper_returns_true(self):
        self.mom_database_wrapper_mock().is_project_active.return_value = True

        return_value = self.project_details_query_handler.is_project_active(self.project_name)

        self.assertTrue(return_value['active'])

    def test_IsProjectActive_returns_active_false_when_mom_wrapper_returns_false(self):
        self.mom_database_wrapper_mock().is_project_active.return_value = False

        return_value = self.project_details_query_handler.is_project_active(self.project_name)

        self.assertFalse(return_value['active'])

    def test_FolderExists_return_exists_true_when_mom_wrapper_returns_true(self):
        self.mom_database_wrapper_mock().folder_exists.return_value = True

        return_value = self.project_details_query_handler.folder_exists(self.folder)

        self.assertTrue(return_value['exists'])

    def test_FolderExists_return_exists_false_when_mom_wrapper_returns_false(self):
        self.mom_database_wrapper_mock().folder_exists.return_value = False

        return_value = self.project_details_query_handler.folder_exists(self.folder)

        self.assertFalse(return_value['exists'])

    def test_authorized_add_with_status_returns_autorized_false_when_mom_wrapper_returns_false(self):
        user_name = "user"
        project_name = "project"
        job_type = "observation"
        status = "approved"

        self.mom_database_wrapper_mock().authorized_add_with_status.return_value = False

        return_value = self.project_details_query_handler.authorized_add_with_status(user_name, project_name, job_type,
                                                                                     status)

        self.assertFalse(return_value['authorized'])

    def test_allows_triggers_returns_allows_true_when_mom_wrapper_returns_true(self):
        project_name = "project"

        self.mom_database_wrapper_mock().allows_triggers.return_value = True

        return_value = self.project_details_query_handler.allows_triggers(project_name)

        self.assertTrue(return_value['allows'])

    def test_allows_triggers_returns_allows_false_when_mom_wrapper_returns_false(self):
        project_name = "project"

        self.mom_database_wrapper_mock().allows_triggers.return_value = False

        return_value = self.project_details_query_handler.allows_triggers(project_name)

        self.assertFalse(return_value['allows'])

    def test_get_project_priority_returns_priority_that_the_mom_wrapper_returs(self):
        project_name = "project"

        self.mom_database_wrapper_mock().get_project_priority.return_value = 1000

        return_value = self.project_details_query_handler.get_project_priority(project_name)

        self.assertEqual(return_value['priority'], 1000)

    def test_add_trigger_returns_row_id_that_the_mom_wrapper_returns(self):
        project_name = "project"
        host_name = "host name"
        user_name = "user name"
        meta_data = "meta data"

        row_id = 55

        self.mom_database_wrapper_mock().add_trigger.return_value = row_id

        return_value = self.project_details_query_handler.add_trigger(user_name, host_name, project_name, meta_data)

        self.assertEqual(return_value['row_id'], row_id)

    def test_add_trigger_calls_update_trigger_quota_with_correct_projectname(self):
        project_name = "project"
        host_name = "host name"
        user_name = "user name"
        meta_data = "meta data"
        row_id = 44

        self.project_details_query_handler.add_trigger(user_name, host_name, project_name, meta_data)

        self.mom_database_wrapper_mock().update_trigger_quota.assert_called_with(project_name)

    def test_get_triggers_query(self):
        user_name = 'user_name'

        self.mom_database_wrapper_mock().get_triggers.return_value = \
            multiple_triggers_result

        return_value = self.project_details_query_handler.get_triggers(
            user_name)

        self.assertEqual(len(return_value['triggers']), 2)

    def test_get_trigger_spec(self):
        user_name = 'user_name'
        trigger_id = '307'

        self.mom_database_wrapper_mock().get_trigger_spec.return_value = \
            trigger_specification

        return_value = self.project_details_query_handler.get_trigger_spec(
            user_name, trigger_id)

        self.assertEqual(len(return_value['trigger_spec']),
            len(trigger_specification))

    # def test_get_trigger_id_returns_trigger_id_when_mom_wrapper_returns_an_id(self):
    #     trigger_id = 1234
    #
    #     self.mom_database_wrapper_mock().get_trigger_id.return_value = trigger_id
    #
    #     return_value = self.project_details_query_handler.get_trigger_id(5432)
    #
    #     self.assertEqual(return_value['trigger_id'], trigger_id)
    #
    # def test_get_trigger_id_returns_status_ok_when_mom_wrapper_returns_an_id(self):
    #     trigger_id = 1234
    #
    #     self.mom_database_wrapper_mock().get_trigger_id.return_value = trigger_id
    #
    #     return_value = self.project_details_query_handler.get_trigger_id(5432)
    #
    #     self.assertEqual(return_value['status'], "OK")
    #
    # def test_get_trigger_id_returns_status_error_when_mom_wrapper_returns_none(self):
    #     self.mom_database_wrapper_mock().get_trigger_id.return_value = None
    #
    #     return_value = self.project_details_query_handler.get_trigger_id(5432)
    #
    #     self.assertEqual(return_value['status'], "Error")
    #
    # def test_get_trigger_id_returns_error_when_mom_wrapper_returns_none(self):
    #     mom_id = 5432
    #
    #     self.mom_database_wrapper_mock().get_trigger_id.return_value = None
    #
    #     return_value = self.project_details_query_handler.get_trigger_id(mom_id)
    #
    #     self.assertEqual(return_value['errors'][0], "No trigger_id for mom_id: " + str(mom_id))
    #
    # def test_get_project_details_returns_author_email(self):
    #     author_email = "author@email.com"
    #     self.mom_database_wrapper_mock().get_project_details.return_value = \
    #         {"author_email": author_email, "pi_email": "pi@email.com"}
    #
    #     return_value = self.project_details_query_handler.get_project_details(24343)
    #
    #     self.assertEqual(return_value["author_email"], author_email)

    def test_get_project_details_returns_pi_email(self):
        pi_email = "pi@email.com"
        self.mom_database_wrapper_mock().get_project_details.return_value = \
            {"author_email": "author@email.com", "pi_email": pi_email}

        return_value = self.project_details_query_handler.get_project_details(24343)

        self.assertEqual(return_value["pi_email"], pi_email)

    def test_get_trigger_time_restrictions_returns_what_the_mom_wrapper_returns(self):
        min_start_time = "2017-01-01T12:00:00"
        max_end_time = "2017-01-02T01:00:03.0000"
        min_duration = 300
        max_duration = 600

        return_value = {"minStartTime": min_start_time, "maxEndTime": max_end_time,
                        "minDuration": min_duration, "maxDuration": max_duration}

        self.mom_database_wrapper_mock().get_trigger_time_restrictions.return_value = return_value

        result = self.project_details_query_handler.get_trigger_time_restrictions(1234)

        self.assertEqual(return_value, result)

    def test_get_station_selection_returns_what_the_mom_wrapper_returns(self):
        resource_group = "SuperTerp"
        rg_min = 1
        rg_max = 3

        self.mom_database_wrapper_mock().get_station_selection.return_value = \
            [{"resourceGroup": resource_group, "min": rg_min, "max": rg_max}]

        result = self.project_details_query_handler.get_station_selection(1234)

        self.assertEqual(result[0]["resourceGroup"], resource_group)
        self.assertEqual(result[0]["min"], rg_min)
        self.assertEqual(result[0]["max"], rg_max)

    def test_get_trigger_quota_returns_what_the_mom_wrapper_returns(self):
        used = 5
        max = 10
        self.mom_database_wrapper_mock().get_trigger_quota.return_value = (used, max)
        result = self.project_details_query_handler.get_trigger_quota(self.project_name)
        self.assertEqual(result["used_triggers"], used)
        self.assertEqual(result["allocated_triggers"], max)

    def test_update_trigger_quota_returns_what_get_trigger_quota_returns(self):
        used = 5
        max = 10
        self.mom_database_wrapper_mock().get_trigger_quota.return_value = (used, max)

        result = self.project_details_query_handler.get_trigger_quota(self.project_name)
        self.assertEqual(result["used_triggers"], used)
        self.assertEqual(result["allocated_triggers"], max)

    def test_cancel_trigger_calls_update_trigger_quota_with_correct_projectname(self):
        project = 'myproject'
        trigger = 1234
        self.mom_database_wrapper_mock().get_projectname_for_trigger.return_value = project
        self.mom_database_wrapper_mock().get_trigger_quota.return_value = (1, 10)

        self.project_details_query_handler.cancel_trigger(trigger, "That's why!")
        self.mom_database_wrapper_mock().get_projectname_for_trigger.assert_called_with(trigger)
        self.mom_database_wrapper_mock().update_trigger_quota.assert_called_with(project)

    def test_cancel_trigger_returns_what_get_trigger_quota_returns(self):
        used = 5
        max = 10
        self.mom_database_wrapper_mock().get_trigger_quota.return_value = (used, max)

        result = self.project_details_query_handler.cancel_trigger(1234, 'no reason')
        self.assertEqual(result["used_triggers"], used)
        self.assertEqual(result["allocated_triggers"], max)

    def test_get_storagemanager_returns_what_the_mom_wrapper_returns(self):

        return_value = "d.y.s.c.o."
        self.mom_database_wrapper_mock().get_storagemanager.return_value = return_value
        result = self.project_details_query_handler.get_storagemanager(1234)

        self.assertEqual(return_value, result)

# @unittest.skip("Skipped because " \
#                "1) mocking at qpidmessaging level, which is way to low. "\
#                "2) testing only the rpc is not that interesting. "\
#                "Suggesting to replace this tests by a full fledged momquery rpc/service/db integration test.")
class TestMomQueryRPC(unittest.TestCase):
    test_id = 1234
    trigger_id = 12345
    message_id = str(uuid.uuid4())
    folder = "/project/folder"
    user_name = "user name"
    project_name = "project name"
    meta_data = "meta data"
    host_name = "host name"
    job_type = "observation"
    status = "opened"
    author_email = "author@example.com"
    pi_email = "pi@example.com"
    test_priority = 42
    min_start_time = "2017-01-01"
    max_end_time = "2017-01-02"
    min_duration = 300
    max_duration = 600
    resourceGroup = "SuperTerp"
    rg_min = 1
    rg_max = 3
    used_triggers = 1
    allocated_triggers = 10

    def setUp(self):
        logger_patcher = mock.patch('lofar.mom.momqueryservice.momqueryrpc.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        self.rpc_mock = mock.MagicMock()

        self.momrpc = MoMQueryRPC(self.rpc_mock)

    def test_object_details_query(self):
        test_id = 1234
        self.momrpc.getObjectDetails(test_id)

        self.rpc_mock.execute.assert_called_with('getObjectDetails', mom_ids=str(test_id))

    def test_is_user_operator_logs_before_query(self):
        self.momrpc.isUserOperator(self.user_name)

        self.logger_mock.info.assert_any_call("Requesting if user %s is an operator", self.user_name)

    def test_is_user_operator_logs_after_query_1(self):
        self.momrpc.isUserOperator(self.user_name)

        self.logger_mock.info.assert_any_call("User %s is %san operator", self.user_name, '')

    def test_is_user_operator_logs_after_query_2(self):
        self.rpc_mock.execute.return_value = {'is_operator': False}

        self.momrpc.isUserOperator(self.user_name)

        self.logger_mock.info.assert_any_call("User %s is %san operator", self.user_name, 'not ')

    def test_is_user_operator_query(self):
        result = self.momrpc.isUserOperator(self.user_name)

        self.assertTrue(result['is_operator'])

    def test_is_project_active_query(self):
        result = self.momrpc.isProjectActive(self.project_name)

        self.assertTrue(result['active'])

    def test_is_project_active_logs_before_query(self):
        self.momrpc.isProjectActive(self.project_name)

        self.logger_mock.info.assert_any_call("Requesting if project: %s is active", self.project_name)

    def test_is_project_active_logs_after_query(self):
        result = self.momrpc.isProjectActive(self.project_name)

        self.logger_mock.info.assert_any_call("Received Project is active: %s", result)

    def test_folder_exists_active_query(self):
        result = self.momrpc.folderExists(self.folder)

        self.assertTrue(result['exists'])

    def test_is_project_logs_before_query(self):
        self.momrpc.folderExists(self.folder)

        self.logger_mock.info.assert_any_call("Requesting folder: %s exists", self.folder)

    def test_is_project_logs_after_query(self):
        result = self.momrpc.folderExists(self.folder)

        self.logger_mock.info.assert_any_call("Received folder exists: %s", result)

    def test_authorized_add_with_status_logs_before_query(self):
        self.momrpc.authorized_add_with_status(self.user_name, self.project_name, self.job_type, self.status)

        self.logger_mock.info.assert_any_call(
            "Requesting authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s",
            self.user_name, self.project_name, self.job_type, self.status)

    def test_authorized_add_with_status_logs_after_query(self):
        result = self.momrpc.authorized_add_with_status(self.user_name, self.project_name, self.job_type, self.status)

        self.logger_mock.info.assert_any_call(
            "Received authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s result: %s",
            self.user_name, self.project_name, self.job_type, self.status, result)

    def test_authorized_add_with_status_query(self):
        result = self.momrpc.authorized_add_with_status(self.user_name, self.project_name, self.job_type, self.status)

        self.assertTrue(result['authorized'])

    def test_allows_triggers_logs_before_query(self):
        self.momrpc.allows_triggers(self.project_name)

        self.logger_mock.info.assert_any_call("Requesting allows_triggers for project_name: %s", self.project_name)

    def test_allows_triggers_logs_after_query(self):
        result = self.momrpc.allows_triggers(self.project_name)

        self.logger_mock.info.assert_any_call(
            "Received allows_triggers for project_name (%s): %s", self.project_name, result)

    def test_allows_triggers_query(self):
        result = self.momrpc.allows_triggers(self.project_name)

        self.assertTrue(result['allows'])

    def test_get_project_priority_logs_before_query(self):
        self.momrpc.get_project_priority(self.project_name)

        self.logger_mock.info.assert_any_call("Requestion get_project_priority for project_name: %s", self.project_name)

    def test_get_project_priority_logs_after_query(self):
        result = self.momrpc.get_project_priority(self.project_name)

        self.logger_mock.info.assert_any_call(
            "Received get_project_priority for project_name (%s): %s", self.project_name, result)

    def test_get_project_priority_query(self):
        self.momrpc.get_project_priority(self.project_name)

        self.rpc_mock.execute.assert_called_with('get_project_priority',
                                                   project_name=self.project_name)

    def test_add_trigger_logs_before_query(self):
        self.momrpc.add_trigger(self.user_name, self.host_name, self.project_name, self.meta_data)

        self.logger_mock.info.assert_any_call(
            "Requestion add_trigger for user_name: %s, host_name: %s, project_name: %s and meta_data: %s",
            self.user_name, self.host_name, self.project_name, self.meta_data)

    def test_add_trigger_logs_after_query(self):
        result = self.momrpc.add_trigger(self.user_name, self.host_name, self.project_name, self.meta_data)

        self.logger_mock.info.assert_any_call(
            "Received add_trigger for user_name (%s), host_name(%s), project_name(%s) and meta_data(%s): %s",
            self.user_name, self.host_name, self.project_name, self.meta_data, result)

    def test_add_trigger_query(self):
        self.momrpc.add_trigger(self.user_name, self.host_name, self.project_name, self.meta_data)

        self.rpc_mock.execute.assert_called_with('add_trigger', user_name=self.user_name,
                                                 host_name=self.host_name,
                                                 project_name=self.project_name,
                                                 meta_data=self.meta_data)

    def test_add_trigger_query_returns_value_from_rpc(self):
        self.rpc_mock.execute.return_value = 42

        res = self.momrpc.add_trigger(self.user_name, self.host_name, self.project_name, self.meta_data)

        self.assertEqual(42, res)

    def test_get_triggers_logs_before_query(self):
        self.momrpc.get_triggers(self.user_name)

        self.logger_mock.info.assert_any_call("Requesting triggers for "
            "user %s", self.user_name)

    def test_get_triggers_logs_after_query(self):
        self.rpc_mock.execute.return_value = [{"trigger_id": 1}]

        self.momrpc.get_triggers(self.user_name)

        self.logger_mock.info.assert_any_call("Received %d triggers for user %s", 1, self.user_name)

    def test_get_triggers_query(self):
        self.momrpc.get_triggers(self.user_name)

        self.rpc_mock.execute.assert_called_with('get_triggers', user_name = self.user_name)

    def test_get_trigger_spec_logs_before_query(self):
        self.momrpc.get_trigger_spec(self.user_name, self.trigger_id)

        self.logger_mock.info.assert_any_call("Requesting trigger spec for user %s and trigger id %s", self.user_name, self.trigger_id)

    def test_get_trigger_spec_logs_after_query(self):
        trigger_spec = self.momrpc.get_trigger_spec(self.user_name, self.trigger_id)

        self.logger_mock.info.assert_any_call("Received a trigger spec with size %d for trigger id %s of user %s", len(trigger_spec['trigger_spec']), self.trigger_id, self.user_name)

    def test_get_trigger_spec(self):
        self.momrpc.get_trigger_spec(self.user_name, self.trigger_id)

        self.rpc_mock.execute.assert_called_with('get_trigger_spec', user_name = self.user_name,
                                                   trigger_id = self.trigger_id)

    # @mock.patch('lofar.messaging.messagebus.proton.utils.BlockingConnection')
    # def test_get_trigger_id_logs_before_query(self):
    #     self.receiver_mock.receive.return_value = self.qpid_message_get_trigger_id
    #
    #     mom_id = 6789
    #
    #     qpid_mock.Message = Message
    #     qpid_mock.Connection().session().senders = [self.sender_mock]
    #     qpid_mock.Connection().session().next_receiver.return_value = self.receiver_mock
    #
    #     self.momrpc.get_trigger_id(mom_id)
    #
    #     self.logger_mock.info.assert_any_call("Requesting GetTriggerId for mom_id: %s", mom_id)
    #
    # @mock.patch('lofar.messaging.messagebus.proton.utils.BlockingConnection')
    # def test_get_trigger_id_logs_after_query(self):
    #     self.receiver_mock.receive.return_value = self.qpid_message_get_trigger_id
    #
    #     mom_id = 6789
    #
    #     qpid_mock.Message = Message
    #     qpid_mock.Connection().session().senders = [self.sender_mock]
    #     qpid_mock.Connection().session().next_receiver.return_value = self.receiver_mock
    #
    #     result = self.momrpc.get_trigger_id(mom_id)
    #
    #     self.logger_mock.info.assert_any_call("Received trigger_id: %s", result)
    #
    # @mock.patch('lofar.messaging.messagebus.proton.utils.BlockingConnection')
    # def test_get_trigger_id_query(self):
    #     self.receiver_mock.receive.return_value = self.qpid_message_get_trigger_id
    #
    #     mom_id = 6789
    #
    #     qpid_mock.Message = Message
    #     qpid_mock.Connection().session().senders = [self.sender_mock]
    #     qpid_mock.Connection().session().next_receiver.return_value = self.receiver_mock
    #
    #     result = self.momrpc.get_trigger_id(mom_id)
    #
    #     self.assertEqual(result["trigger_id"], self.trigger_id)
    #     self.assertEqual(result["status"], "OK")

    def test_get_project_details_logs_before_query(self):
        mom_id = 6789

        self.momrpc.get_project_details(mom_id)

        self.logger_mock.info.assert_any_call("Requesting get_project_details for mom_id: %s", mom_id)

    def test_get_project_details_logs_after_query(self):
        mom_id = 6789

        result = self.momrpc.get_project_details(mom_id)

        self.logger_mock.info.assert_any_call("Received get_project_details: %s", result)

    def test_get_project_details_query(self):
        mom_id = 6789

        self.momrpc.get_project_details(mom_id)

        self.rpc_mock.execute.assert_called_with('get_project_details', mom_id=mom_id)

    def test_get_project_priorities_for_objects_query(self):
        self.momrpc.get_project_priorities_for_objects(self.test_id)

        self.rpc_mock.execute.assert_called_with('get_project_priorities_for_objects',
                                                   mom_ids=str(self.test_id))

    def test_get_time_restrictions_query(self):
        self.momrpc.get_trigger_time_restrictions(self.test_id)

        self.rpc_mock.execute.assert_called_with('get_trigger_time_restrictions',
                                                   mom_id=self.test_id)

    def test_get_station_selection_query(self):
        self.momrpc.get_station_selection(self.test_id)

        self.rpc_mock.execute.assert_called_with('get_station_selection', mom_id=self.test_id)

    def test_get_trigger_quota_query(self):
        result = self.momrpc.get_trigger_quota(self.project_name)

        self.rpc_mock.execute.assert_called_with('get_trigger_quota',
                                                   project_name=self.project_name)

    def test_update_trigger_quota(self):
        self.momrpc.update_trigger_quota(self.project_name)

        self.rpc_mock.execute.assert_called_with('update_trigger_quota', project_name=self.project_name)

    def test_cancel_trigger(self):
        reason = 'Because I say so'
        self.momrpc.cancel_trigger(self.test_id, reason)

        self.rpc_mock.execute.assert_called_with('cancel_trigger', trigger_id=self.test_id,
                                                   reason=reason)

class TestMoMDatabaseWrapper(unittest.TestCase):
    database_credentials = Credentials()
    database_credentials.host = "localhost"
    database_credentials.user = "root"
    database_credentials.database = "testdb"
    database_credentials.password = None
    database_credentials.config = {"useradministration_database": "useradministration",
                                   "momprivilege_database": "momprivilege"}

    project_name = "project name"
    folder = "/project/folder1/folder2"

    user_name = "user name"
    meta_data = "meta data"
    host_name = "host name"
    job_type = "observation"
    status = "opened"

    mom_id = 84903
    trigger_id = 294093

    project_priority = 42

    def setUp(self):
        logger_patcher = mock.patch('lofar.mom.simpleapis.momdbclient.logger')
        self.addCleanup(logger_patcher.stop)
        self.logger_mock = logger_patcher.start()

        mysql_patcher = mock.patch('lofar.mom.simpleapis.momdbclient.connector')
        self.addCleanup(mysql_patcher.stop)
        self.mysql_mock = mysql_patcher.start()

        self.mom_database_wrapper = MoMDatabaseWrapper(self.database_credentials)

    def test_is_user_operator_logs_start_of_query(self):
        self.mom_database_wrapper.is_user_operator(self.user_name)

        self.logger_mock.info.assert_any_call("is_user_operator for user name %s", self.user_name)

    def test_is_user_operator_true_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'1': 1}]

        self.mom_database_wrapper.is_user_operator(self.user_name)

        self.logger_mock.info.assert_any_call("%s is %san operator.", self.user_name, "")

    def test_is_user_operator_false_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        self.mom_database_wrapper.is_user_operator(self.user_name)

        self.logger_mock.info.assert_any_call("%s is %san operator.", self.user_name, "not ")

    def test_is_user_operator_return_true_when_query_returns_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'1': 1}]

        return_value = self.mom_database_wrapper.is_user_operator(
            self.user_name)

        self.assertTrue(return_value)

    def test_is_user_operator_return_false_when_query_returns_no_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        return_value = self.mom_database_wrapper.is_user_operator(self.user_name)

        self.assertFalse(return_value)

    def test_is_project_active_logs_start_of_query(self):
        self.mom_database_wrapper.is_project_active(self.project_name)

        self.logger_mock.info.assert_any_call("is_project_active for project name: %s", self.project_name)

    def test_is_project_active_logs_end_of_query(self):
        is_active = False

        self.mom_database_wrapper.is_project_active(self.project_name)

        self.logger_mock.info.assert_any_call("is_project_active for project (%s): %s", self.project_name, is_active)

    def test_is_project_active_return_true_when_query_returns_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'1': 1}]

        return_value = self.mom_database_wrapper.is_project_active(self.project_name)

        self.assertTrue(return_value)

    def test_is_project_active_return_false_when_query_returns_no_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        return_value = self.mom_database_wrapper.is_project_active(self.project_name)

        self.assertFalse(return_value)

    def test_folder_exists_logs_start_of_query(self):
        self.mom_database_wrapper.folder_exists(self.folder)

        self.logger_mock.info.assert_any_call("folder_exists for folder: %s", self.folder)

    def test_folder_exists_logs_stop_of_query(self):
        exists = False

        self.mom_database_wrapper.folder_exists(self.folder)

        self.logger_mock.info.assert_any_call("folder_exists for folder (%s): %s", self.folder, exists)

    def test_folder_exists_returns_true_when_query_returns_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'1': 1}]

        return_value = self.mom_database_wrapper.folder_exists(self.folder)

        self.assertTrue(return_value)

    def test_folder_exists_returns_false_when_query_returns_no_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        return_value = self.mom_database_wrapper.folder_exists(self.folder)

        self.assertFalse(return_value)

    def test_folder_exists_raises_ValueError_on_empty_folder_path(self):
        empty_path = ""

        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.folder_exists(empty_path)

        self.assertEqual(str(exception.exception), "Folder path () does not start with a /")

    def test_folder_exists_raises_ValueError_on_folder_path_with_no_parent(self):
        no_parent_path = "/"

        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.folder_exists(no_parent_path)

        self.assertEqual(str(exception.exception), "Folder path (/) should minimally have a project")

    def test_authorized_add_with_status_logs_start_of_query(self):
        self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name, self.job_type,
                                                             self.status)

        self.logger_mock.info.assert_any_call(
            "authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s",
            self.user_name, self.project_name, self.job_type, self.status)

    def test_authorized_add_with_status_logs_stop_of_query(self):
        authorized = False

        self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name, self.job_type,
                                                             self.status)

        self.logger_mock.info.assert_any_call(
            "authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s result: %s",
            self.user_name, self.project_name, self.job_type, self.status, authorized)

    def test_authorized_add_with_status_returns_true_when_query_returns_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'1': 1}]

        return_value = self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                            self.job_type, self.status)
        self.assertTrue(return_value)

    def test_authorized_add_with_status_returns_false_when_query_returns_no_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        return_value = self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                            self.job_type, self.status)

        self.assertFalse(return_value)

    def test_authorized_add_with_status_throws_ValueError_when_status_is_not_approved_or_opened(self):
        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                 self.job_type, "aborted")

        self.assertEqual(str(exception.exception), "status should be either 'opened' or 'approved'")

    def test_authorized_add_with_status_throws_ValueError_when_job_type_is_not_observation_or_pipeline_ingest(self):
        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                 "measurment", self.status)

        self.assertEqual(str(exception.exception), "job_type should be either 'observation', 'ingest' or 'pipeline'")

    def test_allows_triggers_logs_start_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'allowtriggers': True}]

        self.mom_database_wrapper.allows_triggers(self.project_name)

        self.logger_mock.info.assert_any_call("allows_triggers for project_name: %s", self.project_name)

    def test_allows_triggers_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'allowtriggers': True}]

        result = self.mom_database_wrapper.allows_triggers(self.project_name)

        self.logger_mock.info.assert_any_call(
            "allows_triggers for project_name (%s) result: %s", self.project_name, result)

    def test_allows_triggers_returns_throws_exception_when_query_returns_no_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.allows_triggers(self.project_name)

        self.assertEqual(str(exception.exception), "project name (%s) not found in MoM database" % self.project_name)

    def test_allows_triggers_returns_true_when_query_returns_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'allowtriggers': True}]

        return_value = self.mom_database_wrapper.allows_triggers(self.project_name)

        self.assertTrue(return_value)

    def test_get_project_priority_logs_start_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'priority': 1000}]

        self.mom_database_wrapper.get_project_priority(self.project_name)

        self.logger_mock.info.assert_any_call("get_project_priority for project_name: %s", self.project_name)

    def test_get_project_priority_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'priority': 1000}]

        return_value = self.mom_database_wrapper.get_project_priority(self.project_name)

        self.logger_mock.info.assert_any_call(
            "get_project_priority for project_name (%s): %s", self.project_name, return_value)

    def test_get_project_priority_returns_priority_when_query_returns_a_row(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [{'priority': 1000}]

        return_value = self.mom_database_wrapper.get_project_priority(self.project_name)

        self.assertEqual(return_value, 1000)

    def test_get_project_priority_throws_exception_when_query_returns_no_row(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.get_project_priority(self.project_name)

        self.assertEqual(str(exception.exception), "project name (%s) not found in MoM database" % self.project_name)

    def test_add_trigger_logs_start_of_query(self):
        self.mysql_mock.connect().cursor().lastrowid = 34

        self.mom_database_wrapper.add_trigger(self.user_name, self.host_name, self.project_name, self.meta_data)

        self.logger_mock.info.assert_any_call(
            "add_trigger for user_name: %s, host_name: %s, project_name: %s, meta_data: %s",
            self.user_name, self.host_name, self.project_name, self.meta_data)

    def test_add_trigger_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().lastrowid = 34

        result = self.mom_database_wrapper.add_trigger(
            self.user_name, self.host_name, self.project_name, self.meta_data)

        self.logger_mock.info.assert_any_call(
            "add_trigger for user_name(%s), host_name(%s), project_name(%s), meta_data(%s): %s",
            self.user_name, self.host_name, self.project_name, self.meta_data, result)

    def test_add_trigger_returns_row_id_from_query(self):
        self.mysql_mock.connect().cursor().lastrowid = 34

        result = self.mom_database_wrapper.add_trigger(
            self.user_name, self.host_name, self.project_name, self.meta_data)

        self.assertEqual(result, 34)

    def test_get_trigger_id_logs_start_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'misc': '{"trigger_id": ' + str(self.trigger_id) + '}'}]

        self.mom_database_wrapper.get_trigger_id(self.mom_id)

        self.logger_mock.info.assert_any_call("get_trigger_id for mom_id: %s", self.mom_id)

    def test_get_trigger_id_logs_end_of_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'misc': '{"trigger_id": ' + str(self.trigger_id) + '}'}]

        self.mom_database_wrapper.get_trigger_id(self.mom_id)

        self.logger_mock.info.assert_any_call("get_trigger_id for mom_id (%s): %s", self.mom_id, self.trigger_id)

    def test_get_trigger_id_returns_row_id_from_query(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'misc': '{"trigger_id": ' + str(self.trigger_id) + '}'}]

        result = self.mom_database_wrapper.get_trigger_id(self.mom_id)

        self.assertEqual(result, self.trigger_id)

    def test_get_triggers_query(self):
        user_name = 'user_name'
        result = \
        [
            {
                'mom_id': self.mom_id,
                'projectname': self.project_name,
                'arrivaltime': datetime.strptime('2017-02-24 15:14:05', '%Y-%m-%d %H:%M:%S'),
                'type': self.job_type,
                'code': self.status,
                'momurl_id': self.mom_id,
                'id': '1'
            },
            {
                'mom_id': self.mom_id,
                'projectname': self.project_name,
                'arrivaltime': datetime.strptime('2017-02-24 16:14:05', '%Y-%m-%d %H:%M:%S'),
                'type': self.job_type,
                'code': self.status,
                'momurl_id': self.mom_id,
                'id': '2'
        }
        ]

        self.mysql_mock.connect().cursor().fetchall.return_value = result

        return_value = self.mom_database_wrapper.get_triggers(
            user_name)

        self.assertEqual(len(return_value), len(multiple_triggers_result))

    def test_get_trigger_spec_no_user_name(self):
        user_name = None
        trigger_id = '307'

        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_spec(
                user_name, trigger_id)

    def test_get_trigger_spec_no_trigger_id(self):
        user_name = 'user_name'
        trigger_id = None

        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_spec(
                user_name, trigger_id)

    def test_get_trigger_spec(self):
        user_name = 'user_name'
        trigger_id = '307'

        self.mysql_mock.connect().cursor().fetchall.return_value = \
            {0: {'metadata': trigger_specification}}

        return_value = self.mom_database_wrapper.get_trigger_spec(
            user_name, trigger_id)

        self.assertEqual(len(return_value), len(trigger_specification))

    def test_get_project_details_logs_start_of_query(self):
        details_result = [{"name": "Contact author", "email": "author@example.com"},
                          {"name": "Pi", "email": "pi@example.com"}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        self.mom_database_wrapper.get_project_details(self.mom_id)

        self.logger_mock.info.assert_any_call("get_project_details for mom_id: %s", self.mom_id)

    def test_get_project_details_logs_end_of_query(self):
        expected_result = {"pi_email": "pi@example.com", "author_email": "author@example.com"}
        details_result = [{"name": "Contact author", "email": "author@example.com"},
                          {"name": "Pi", "email": "pi@example.com"}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        self.mom_database_wrapper.get_project_details(self.mom_id)

        self.logger_mock.info.assert_any_call("get_project_details for mom_id (%s): %s", self.mom_id, expected_result)

    def test_get_project_details_returns_details(self):
        expected_result = {"pi_email": "pi@example.com", "author_email": "author@example.com"}
        details_result = [{"name": "Contact author", "email": "author@example.com"},
                          {"name": "Pi", "email": "pi@example.com"}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_project_details(self.mom_id)

        self.assertEqual(result, expected_result)

    def test_get_project_priorities_for_objects_returns_priorities(self):
        expected_result = {self.mom_id: self.project_priority}
        details_result = [{"project_priority": self.project_priority, "object_mom2id": self.mom_id}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_project_priorities_for_objects(self.mom_id)

        self.assertEqual(result, expected_result)

    def test_get_station_selection_returns_info_from_misc_field(self):
        resource_group = "SuperTerp"
        rg_min = 1
        rg_max = 3
        station_selection = [{"resourceGroup": resource_group, "min": rg_min, "max": rg_max}]

        expected_result = station_selection
        details_result = [{"mom2id": self.mom_id, "mom2objecttype": self.job_type,
                           "misc": json.dumps({"stationSelection": station_selection})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_station_selection(self.mom_id)
        self.assertEqual(result, expected_result)

    def test_get_station_selection_on_empty_query_result(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mom_database_wrapper.get_station_selection(1234))

    def test_get_station_selection_if_station_selection_not_present_in_misc(self):
        details_result = [{"mom2id": self.mom_id, "mom2objecttype": self.job_type,
                           "misc": json.dumps({"timeWindow": {'minDuration': 300, 'maxDuration': 300}})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        self.assertIsNone(self.mom_database_wrapper.get_station_selection(1234))

    def test_get_time_restrictions_returns_misc_field_info_from_query_result(self):
        min_start_time = "2017-01-01T12:00:00"
        max_end_time = "2017-01-04T01:00:00"
        min_duration = 300
        max_duration = 600.1

        timewindow = {"minStartTime": min_start_time,
                      "maxEndTime": max_end_time,
                      "minDuration": min_duration,
                      "maxDuration": max_duration}
        details_result = [{"mom2id": self.mom_id, "mom2objecttype": self.job_type,
                           "misc": json.dumps({"timeWindow": timewindow, "trigger_id": self.trigger_id})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_trigger_time_restrictions(self.mom_id)

        self.assertEqual(result['trigger_id'], self.trigger_id)
        self.assertEqual(result['minStartTime'], min_start_time.replace('T', ' '))
        self.assertEqual(result['maxEndTime'], max_end_time.replace('T', ' '))
        self.assertEqual(result['minDuration'], timedelta(seconds = min_duration))
        self.assertEqual(result['maxDuration'], timedelta(seconds = max_duration))

    def test_get_time_restrictions_returns_None_if_no_timewindow(self):
        details_result = [{"mom2id": self.mom_id, "mom2objecttype": self.job_type,
                           "misc": json.dumps({"trigger_id": self.trigger_id})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_trigger_time_restrictions(self.mom_id)

        self.assertEqual(result['trigger_id'], self.trigger_id)
        self.assertEqual(result['minStartTime'], None)
        self.assertEqual(result['maxEndTime'], None)
        self.assertEqual(result['minDuration'], None)
        self.assertEqual(result['maxDuration'], None)

    def test_get_time_restrictions_on_empty_query_result(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        expected_sane_default = {'minStartTime': None,
                                 'minDuration': None,
                                 'maxDuration': None,
                                 'maxEndTime': None,
                                 'trigger_id': None}
        self.assertEqual(expected_sane_default, self.mom_database_wrapper.get_trigger_time_restrictions(1234))

    def test_get_time_restrictions_throws_NotImplementedError_when_misc_has_timeWindow_but_no_trigger_id(self):
        min_start_time = "2017-01-01T12:00:00"
        max_end_time = "2017-01-04T01:00:00"
        min_duration = 300
        max_duration = 600

        timewindow = {"minStartTime": min_start_time,
                      "maxEndTime": max_end_time,
                      "minDuration": min_duration,
                      "maxDuration": max_duration}

        details_result = [{"mom2id": self.mom_id, "mom2objecttype": self.job_type,
                           "misc": json.dumps({"timeWindow": timewindow})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        with self.assertRaises(NotImplementedError) as ex:
            self.mom_database_wrapper.get_trigger_time_restrictions(self.mom_id)
            self.assertEqual(str(ex.exception), "TimeWindow specified for a non-triggered observation %s" % self.mom_id)

    def test_get_trigger_quota_throws_ValueError_if_query_returns_no_rows(self):
        details_result = []
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_quota(1234)

    def test_get_trigger_quota_returns_values_from_query_result(self):
        used_t = 5
        max_t = 10
        details_result = [{"used":used_t, "allocation": max_t}]
        expected_result = (used_t, max_t)
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        result = self.mom_database_wrapper.get_trigger_quota(1234)
        self.assertEqual(result, expected_result)

    def test_cancel_trigger_throws_ValueError_if_update_does_not_affect_rows(self):
        self.mysql_mock.connect().cursor().rowcount = 0
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.cancel_trigger(1234, 'no reason')

    def test_cancel_trigger_does_not_raise_exception_if_queries_affect_rows(self):
        self.mysql_mock.connect().cursor().rowcount = 1
        self.mom_database_wrapper.cancel_trigger(1234, 'no reason')

    def test_update_trigger_quota_throws_ValueError_if_select_query_returns_empty_result(self):
        # select active trigger count
        self.mysql_mock.connect().cursor().fetchall.return_value = []
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.update_trigger_quota('myproject')

    def test_update_trigger_quota_throws_ValueError_if_update_query_cannot_modify_any_rows(self):
        # update resource use
        self.mysql_mock.connect().cursor().fetchall.return_value = [7]    # let select pass, to see if update fails
        self.mysql_mock.connect().cursor().rowcount = 0
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.update_trigger_quota('myproject')

    def test_update_trigger_quota_does_not_raise_exception_if_select_is_not_empty_and_update_affected_rows(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = [7]    # let select pass, to see if update fails
        self.mysql_mock.connect().cursor().rowcount = 1
        self.mom_database_wrapper.update_trigger_quota('myproject')

    def test_get_storagemanager_returns_value_from_query_result(self):
        value = "d.y.s.c.o."
        self.mysql_mock.connect().cursor().fetchall.return_value = \
            [{'misc': '{"storagemanager": \"' + value + '\"}'}]
        result = self.mom_database_wrapper.get_storagemanager(self.mom_id)
        self.assertEqual(result, value)

    def test_get_storagemanager_on_empty_query_result(self):
        self.mysql_mock.connect().cursor().fetchall.return_value = []

        self.assertIsNone(self.mom_database_wrapper.get_storagemanager(1234))

    def test_get_storagemanager_returns_None_if_station_selection_not_present_in_misc(self):
        details_result = [{"misc": json.dumps({"timeWindow": {'minDuration': 300, 'maxDuration': 300}})}]
        self.mysql_mock.connect().cursor().fetchall.return_value = details_result

        self.assertIsNone(self.mom_database_wrapper.get_storagemanager(1234))

#TODO: remove skip of unittest
@unittest.skip("Skipping integration test")
class IntegrationTestMoMDatabaseWrapper(unittest.TestCase):
    database_credentials = Credentials()
    database_credentials.host = "localhost"
    database_credentials.user = "root"
    database_credentials.database = "mom"
    database_credentials.password = None
    database_credentials.config = {"useradministration_database": "useradministration",
                                   "momprivilege_database": "momprivilege"}

    project_name = "project name"
    folder = "/project/folder1/folder2"

    user_name = "lofar"
    job_type = "observation"
    status = "opened"

    trigger_id = 1002

    def setUp(self):
        logger.info('setting up test MoM database...')

        self.mysqld = Mysqld()    # for a fresh one, use: self.mysqld = testing.mysqld.Mysqld()

        # set up fresh connection to the mom (!) database.
        self.connection = connector.connect(**self.mysqld.dsn())
        self.connection.cursor().execute('USE mom')    # Attention: the dsn actually points to a different db
        self.connection.commit()

        # create db wrapper for tests
        self.database_credentials.port = self.mysqld.dsn()['port']

        self.mom_database_wrapper = MoMDatabaseWrapper(self.database_credentials)

        logger.info('...finished setting up test MoM database')

    def tearDown(self):
        self.connection.close()
        self.mysqld.stop()

    def execute(self, query, fetch = False):
        cursor = self.connection.cursor(dictionary = True)
        cursor.execute(query)
        ret = None
        if fetch:
            ret = cursor.fetchall()
        self.connection.commit()
        cursor.close()
        return ret

    def test_is_project_active_returns_false_on_empty_mom2object_table(self):
        self.assertFalse(self.mom_database_wrapper.is_project_active("project_name"))

    def test_is_project_active_returns_true_when_project_with_correct_name_and_status_is_available(self):
        self.execute("insert into mom2object values(169900, NULL, NULL, 183526, 'PROJECT', 'LC0_011', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")
        self.execute("insert into mom2objectstatus values(966855, 'Pizzo, Dr. Roberto Francesco', "
                     "'Administrative, LTA User, manager, Operator, Prospective, Review Manager, Reviewer, Scientist, "
                     "System Scientist, Telescope Astronomer', 531, 7, 169900, 0, '2012-12-18 09:47:50', 0)")

        self.assertTrue(self.mom_database_wrapper.is_project_active("LC0_011"))

    def test_folder_exists_returns_false_on_empty_table(self):
        self.assertFalse(self.mom_database_wrapper.folder_exists("/project/folder1/folder2"))

    def test_folder_exists_returns_true_when_folder_exists(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 11, 'PROJECT', 'project', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")
        self.execute("insert into mom2object values(2, 1, NULL, 22, 'FOLDER', 'folder1', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")
        self.execute("insert into mom2object values(3, 2, NULL, 33, 'FOLDER', 'folder2', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")

        self.assertTrue(self.mom_database_wrapper.folder_exists(self.folder))

    def test_folder_exists_returns_true_when_folder_exists_and_path_ends_on_forward_slash(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 11, 'PROJECT', 'project', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")
        self.execute("insert into mom2object values(2, 1, NULL, 22, 'FOLDER', 'folder1', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")
        self.execute("insert into mom2object values(3, 2, NULL, 33, 'FOLDER', 'folder2', "
                     "'Pulsar timing with LOFAR', NULL, 966855, NULL, NULL, 0, 0, 0)")

        self.assertTrue(self.mom_database_wrapper.folder_exists(self.folder))

    def test_authorized_add_with_status_returns_false_on_empty_db(self):
        self.assertFalse(self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                              self.job_type, self.status))

    def test_authorized_add_with_status_returns_true_on_when_rights_are_on_system_role(self):
        # insert user
        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')"
                     % self.user_name)
        # setup status
        self.execute("insert into status values(101, 'opened', 'OBSERVATION', '')")
        self.execute("insert into status values(104, 'approved', 'OBSERVATION', "
                     "'The specification is in accordance with wishes of the PI.')")
        # setup status transitions
        self.execute("insert into momprivilege.statustransition values(1003, 0, 101)")
        self.execute("insert into momprivilege.statustransition values(1059, 101, 104)")
        # setup transition role
        self.execute("insert into momprivilege.statustransitionrole "
                     "values(1, 1003, 9, 'nl.astron.useradministration.data.entities.SystemRole')")
        self.execute("insert into momprivilege.statustransitionrole "
                     "values(2, 1059, 9, 'nl.astron.useradministration.data.entities.SystemRole')")
        # user account system role
        self.execute("insert into useradministration.useraccountsystemrole values(533, 1, 9, 0)")

        self.assertTrue(self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                             'observation', "approved"))
        self.assertTrue(self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                             'observation', "opened"))

    def test_authorized_add_with_status_returns_true_on_when_rights_are_on_project_role(self):
        # insert user
        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')"
                     % self.user_name)
        # setup status
        self.execute("insert into status values(101, 'opened', 'OBSERVATION', '')")
        self.execute("insert into status values(104, 'approved', 'OBSERVATION', "
                     "'The specification is in accordance with wishes of the PI.')")
        # setup status transitions
        self.execute("insert into momprivilege.statustransition values(1003, 0, 101)")
        self.execute("insert into momprivilege.statustransition values(1059, 101, 104)")
        # setup transition role
        self.execute("insert into momprivilege.statustransitionrole "
                     "values(1, 1003, 1, 'nl.astron.mom2.data.entities.ProjectRole')")
        self.execute("insert into momprivilege.statustransitionrole "
                     "values(2, 1059, 1, 'nl.astron.mom2.data.entities.ProjectRole')")
        # setup project role
        self.execute("insert into projectrole values(1, 'Pi', NULL)")
        # setup member project role
        self.execute("insert into memberprojectrole values(1, 1, 0, 1)")
        # setup registered member
        self.execute("insert into registeredmember values(1, 1, 1)")
        # setup member
        self.execute("insert into member values(1, 1, 0)")
        # setup project
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})

        self.assertTrue(self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                             'observation', 'approved'))
        self.assertTrue(self.mom_database_wrapper.authorized_add_with_status(self.user_name, self.project_name,
                                                                             'observation', 'opened'))

    def test_allows_triggers_returns_raises_exception_on_empty_db(self):
        with self.assertRaises(ValueError) as exception:
            self.assertFalse(self.mom_database_wrapper.allows_triggers(self.project_name))

        self.assertEqual(str(exception.exception), "project name (%s) not found in MoM database" % self.project_name)

    def test_allows_triggers_returns_true_when_project_allows_triggers(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        self.execute("insert into project values(1, 1, '2012-09-14', TRUE, 1000)")

        self.assertTrue(self.mom_database_wrapper.allows_triggers(self.project_name))

    def test_allows_triggers_returns_false_when_project_does_not_allow_triggers(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        self.execute("insert into project values(1, 1, '2012-09-14', FALSE, 1000)")

        self.assertFalse(self.mom_database_wrapper.allows_triggers(self.project_name))

    def test_get_project_priority_raises_exception_on_empty_database(self):
        with self.assertRaises(ValueError) as exception:
            self.mom_database_wrapper.get_project_priority(self.project_name)

        self.assertEqual(str(exception.exception), "project name (%s) not found in MoM database" % self.project_name)

    def test_get_project_priority_returns_priority_of_project(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        self.execute("insert into project values(1, 1, '2012-09-14', FALSE, 5000)")

        priority = self.mom_database_wrapper.get_project_priority(self.project_name)

        self.assertEqual(priority, 5000)

    def test_add_trigger_returns_row_id_1_on_empty_table(self):
        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')"
                     % self.user_name)
        result = self.mom_database_wrapper.add_trigger(self.user_name, "host name", "project name", "meta data")

        self.assertEqual(result, 1)

    def test_add_trigger_returns_row_id_2_on_insert_delete_insert_on_empty_database(self):
        # It is (maybe) not likely that triggers will be deleted but at least the code can handle it
        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')"
                     % self.user_name)

        self.mom_database_wrapper.add_trigger(self.user_name, "host name", "project name", "meta data")
        self.execute("delete from lofar_trigger "
                     "where id = 1")
        result = self.mom_database_wrapper.add_trigger(self.user_name, "host name", "project name", "meta data")

        self.assertEqual(result, 2)

    def test_get_trigger_id_returns_None_on_empty_database(self):
        result = self.mom_database_wrapper.get_trigger_id("1")

        self.assertEqual(result, None)

    def test_get_trigger_id_returns_id_for_lofar_observation(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', "
                     "'test-lofar', NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{\"trigger_id\": %(trigger_id)s}')" % {"trigger_id": self.trigger_id})

        result = self.mom_database_wrapper.get_trigger_id("2")

        self.assertEqual(result, self.trigger_id)

    def test_get_trigger_id_returns_none_for_lofar_observation_with_empty_misc(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', "
                     "'test-lofar', NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 2, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '')")

        result = self.mom_database_wrapper.get_trigger_id("2")

        self.assertEqual(result, None)

    def test_get_trigger_id_returns_none_for_lofar_observation_with_empty_json(self):
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', "
                     "'test-lofar', NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 2, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{}')")

        result = self.mom_database_wrapper.get_trigger_id("2")

        self.assertEqual(result, None)

    def test_get_trigger_id_returns_id_for_lofar_pipeline(self):
        self.execute("insert into mom2object values(1, 104711, 4, 2, 'CALIBRATION_PIPELINE', 'Target Pipeline 1.3', "
                     "'Target Pipeline 1.3 [1.P3]', 1, 1722446, 'mom_msss_117430.1.P3', 'M117434,M117435', 0, 117430,"
                     " 0)")
        # id, mom2objectid, starttime, endtime, pipeline_id, pending, template, runtimeDirectory, resultDirectory, workingDirectory, parset, nr_output_correlated, nr_output_beamformed, nr_output_instrument_model, nr_output_skyimage, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_instrument_model_valid, nr_output_skyimage_valid, feedback, demixing_parameters_id, bbs_parameters_id, duration, storage_cluster_id, processing_cluster_id, misc
        self.execute("insert into lofar_pipeline values(1761, 1, NULL, NULL, 63722, 0, "
                     "'Calibration Pipeline Calibrator', NULL, NULL, NULL, 'parset', 0, NULL, 244, NULL, 0, 0, NULL, 0,"
                     " NULL, 3071, 3071, NULL, NULL, NULL, '{\"trigger_id\": %(trigger_id)s}')"
                     % {"trigger_id": self.trigger_id})

        result = self.mom_database_wrapper.get_trigger_id("2")

        self.assertEqual(result, self.trigger_id)

    def test_get_project_details_returns_empty_list_on_empty_database(self):
        result = self.mom_database_wrapper.get_project_details(2334)

        self.assertEqual(result, {"pi_email": "", "author_email": ""})

    def test_get_project_details_returns_correct_emails_with_filled_database(self):
        self.execute("insert into mom2object "
                     "values(111, NULL, NULL, 2334, 'PROJECT', 'CEP4tests', 'Project for CEP4 tests', "
                     "NULL, 1725713, NULL, NULL, 0, NULL, NULL);")

        self.execute("insert into member "
                     "values(1, 111, 0);")
        self.execute("insert into member "
                     "values(2, 111, 0);")

        self.execute("insert into registeredmember "
                     "values(1, 1, 1);")
        self.execute("insert into registeredmember "
                     "values(2, 2, 2);")

        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, 'user1', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk');")
        self.execute("insert into useradministration.useraccount "
                     "values(2, 2, 'user2', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk');")

        self.execute("insert into useradministration.user "
                     "values(1, 'ir.', 'pi', 'user', 'pi@example.com', 797, NULL, NULL);")
        self.execute("insert into useradministration.user "
                     "values(2, 'ir.', 'author', 'user', 'author@example.com', 797, NULL, NULL);")

        self.execute("insert into projectrole values(1, 'Pi', NULL);")
        self.execute("insert into projectrole values(4, 'Contact author', NULL);")

        self.execute("insert into memberprojectrole values(1, 1, 0, 1);")
        self.execute("insert into memberprojectrole values(2, 2, 0, 4);")

        result = self.mom_database_wrapper.get_project_details(2334)

        self.assertEqual(result, {"pi_email": "pi@example.com", "author_email": "author@example.com"})

    def test_get_object_details_returns_empty_dict_on_empty_database(self):

            result = self.mom_database_wrapper.getObjectDetails(1234)
            self.assertEqual(result, {})

    def test_get_object_details_returns_correct_details(self):

        oid = 2345
        statusid = 101
        status = 'opened'
        pname = 'myproject_' + str(1)

        self.execute("insert into mom2object values(%s, NULL, NULL, %s, 'PROJECT', '%s', 'x', "
                     "NULL, %s, NULL, NULL, 0, 0, 0)"
                     % (1, 1, pname, statusid))

        self.execute("insert into project values(%s, %s, '2012-09-14', FALSE, 0)"
                     % (1, 1))

        self.execute("insert into mom2object values(%s, NULL, NULL, %s , 'OBSERVATION', 'x', "
                     "'x', %s, %s, 'x', 'x', 0, NULL,"
                     " 0)"
                     % (2, oid, 1, statusid))

        self.execute("insert into status values(%s, '%s', 'OBSERVATION', %s)" % (statusid, status, statusid))

        self.execute("insert into mom2objectstatus values(%s, 'PI','LTA User', %s, %s, %s, 0, '2012-12-18 09:47:50', 0)"
                     % (statusid, statusid, statusid, oid))

        result = self.mom_database_wrapper.getObjectDetails(oid)

        self.assertTrue(str(oid) in list(result.keys()))
        self.assertEqual(result[str(oid)]['object_mom2id'], oid)
        self.assertEqual(result[str(oid)]['object_status'], status)
        self.assertEqual(result[str(oid)]['project_name'], pname)

    def test_get_project_priorities_for_objects_returns_correct_priorities(self):
        object_ids = [3344, 1234, 7654]
        project_prios = [42, 24, 12]

        # add separate projects with a pipeline each:
        for oid in object_ids:
            i = object_ids.index(oid)
            prio = project_prios[i]

            eid = i + 1

            self.execute("insert into mom2object values(%s, NULL, NULL, %s, 'PROJECT', '%s', 'x', "
                         "NULL, 0, NULL, NULL, 0, 0, 0)"
                         % (eid, eid, 'myproject_' + str(i)))

            self.execute("insert into project values(%s, %s, '2012-09-14', FALSE, %s)"
                         % (eid, eid, prio))    # unique id in project table, refer to mom2object of our project

            self.execute("insert into mom2object values(%s, NULL, NULL, %s , 'PIPELINE', 'x', "
                         "'x', %s, NULL, 'x', 'x', 0, NULL,"
                         " 0)"
                         % (eid + 100, oid, eid))    # unique id for the pipeline, refer to project id

        return_value = self.mom_database_wrapper.get_project_priorities_for_objects(object_ids)

        for oid in object_ids:
            expected_prio = project_prios[object_ids.index(oid)]
            prio = return_value[oid]
            self.assertEqual(prio, expected_prio)

    def test_get_project_priorities_for_objects_returns_empty_dict_on_empty_database(self):

        return_value = self.mom_database_wrapper.get_project_priorities_for_objects("1234")
        self.assertEqual(return_value, {})

    def test_get_project_priorities_for_objects_returns_only_priorities_of_existing_objects(self):

        object_ids = [380, 747]
        extra_id = 787
        project_prios = [5, 6]

        # add separate projects with a pipeline each:
        for oid in object_ids:
            i = object_ids.index(oid)
            prio = project_prios[i]

            eid = i + 1

            self.execute("insert into mom2object values(%s, NULL, NULL, %s, 'PROJECT', '%s', 'x', "
                         "NULL, 0, NULL, NULL, 0, 0, 0)"
                         % (eid, eid, 'myproject_' + str(i)))

            self.execute("insert into project values(%s, %s, '2012-09-14', FALSE, %s)"
                         % (eid, eid, prio))    # unique id in project table, refer to mom2object of our project

            self.execute("insert into mom2object values(%s, NULL, NULL, %s , 'PIPELINE', 'x', "
                         "'x', %s, NULL, 'x', 'x', 0, NULL,"
                         " 0)"
                         % (eid + 100, oid, eid))    # unique id for the pipeline, refer to project id

        return_value = self.mom_database_wrapper.get_project_priorities_for_objects(object_ids + [extra_id])

        for oid in object_ids:
            self.assertTrue(oid in list(return_value.keys()))
        self.assertFalse(extra_id in list(return_value.keys()))

    def test_get_time_restrictions_throws_ValueError_on_empty_database(self):
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_time_restrictions(1234)

    def test_get_time_restrictions_throws_ValueError_if_no_time_restrictions_in_database(self):

        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, NULL)")

        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_time_restrictions(2)

    def test_get_time_restrictions_returns_correct_time_restrictions(self):
        min_start_time = "2017-01-01"
        max_end_time = "2017-01-02"
        min_duration = 300
        max_duration = 600

        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, %s, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{\"timeWindow\":{\"minStartTime\": \"%s\", \"maxEndTime\": \"%s\", \"minDuration\": %s, "
                     "\"maxDuration\": %s}}')"
                     % (min_duration, min_start_time, max_end_time, min_duration, max_duration))

        result = self.mom_database_wrapper.get_trigger_time_restrictions(2)

        self.assertEqual(result["minStartTime"], min_start_time)
        self.assertEqual(result["maxEndTime"], max_end_time)
        self.assertEqual(result["minDuration"], min_duration)
        self.assertEqual(result["maxDuration"], max_duration)

    def test_get_time_restrictions_returns_mom_duration_if_misc_empty(self):
        duration = 300

        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, %s, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, NULL)" % duration)

        result = self.mom_database_wrapper.get_trigger_time_restrictions(2)

        self.assertEqual(result["minDuration"], duration)
        self.assertEqual(result["maxDuration"], duration)

    def test_get_station_selection_throws_ValueError_on_empty_database(self):
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_station_selection(1234)

    def test_get_station_selection_throws_ValueError_if_not_present_in_misc(self):

        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{\"timeWindow\":{\"minDuration\": 300, \"maxDuration\": 600}}')")

        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_station_selection(1234)

    def test_get_station_selection_returns_correct_station_selection(self):
        resource_group = "SuperTerp"
        rg_min = 4
        rg_max = 9
        resource_group2 = "CS001"
        rg_min2 = 1

        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{\"stationSelection\": [{\"resourceGroup\": \"%s\", \"min\": %s, \"max\": %s}, "
                     "{\"resourceGroup\": \"%s\", \"min\": %s}]}')" % (resource_group, rg_min, rg_max,
                                                                       resource_group2, rg_min2))

        result = self.mom_database_wrapper.get_station_selection(2)

        self.assertEqual(result[0]["resourceGroup"], resource_group)
        self.assertEqual(result[0]["min"], rg_min)
        self.assertEqual(result[0]["max"], rg_max)
        self.assertEqual(result[1]["resourceGroup"], resource_group2)
        self.assertEqual(result[1]["min"], rg_min2)
    def test_get_trigger_quota_throws_ValueError_on_empty_database(self):
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.get_trigger_quota(self.project_name)

    def test_get_trigger_quota_returns_correct_quota(self):
        used = 5
        allocation = 10
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        self.execute("INSERT INTO resourcetype (id, name, type) VALUES (1, 'Lofar Triggers','LOFAR_TRIGGERS');")
        self.execute("insert into resource (resourcetypeid, projectid, used, allocation) "
                     "values(1, 2, %s, %s)" % (used, allocation))

        used_t, max_t = self.mom_database_wrapper.get_trigger_quota(self.project_name)
        self.assertEqual(used_t, used)
        self.assertEqual(allocation, max_t)

    def test_cancel_trigger_throws_ValueError_on_empty_database(self):
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.cancel_trigger(self.trigger_id, 'because I can')

    def test_cancel_trigger_cancels_trigger(self):
        self.execute("insert into useradministration.useraccount "
                          "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')" % self.user_name)
        self.execute("insert into lofar_trigger (id, username, hostname, projectname, metadata) "
                     "values (%s, '%s', 'host', 'myproject', 'meta')" % (self.trigger_id, self.user_name))

        reason = 'because I can'
        self.mom_database_wrapper.cancel_trigger(self.trigger_id, reason)

        result = self.execute("SELECT cancelled, cancelled_at, cancelled_reason "
                     "FROM lofar_trigger WHERE id = %s" % self.trigger_id, fetch = True)

        self.assertEqual(result[0]['cancelled'], 1)
        self.assertTrue(type(result[0]['cancelled_at']) is datetime)
        self.assertEqual(result[0]['cancelled_reason'], reason)

    def test_update_trigger_quota_throws_ValueError_on_empty_database(self):
        with self.assertRaises(ValueError):
            self.mom_database_wrapper.update_trigger_quota(self.project_name)

    def test_update_trigger_quota_updates_trigger_quota(self):
        # add project with trigger resource:
        used = 5
        self.execute("insert into mom2object values(1, NULL, NULL, 2, 'PROJECT', '%(project_name)s', 'test-lofar', "
                     "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        self.execute("INSERT INTO resourcetype (id, name, type) VALUES (1, 'Lofar Triggers','LOFAR_TRIGGERS');")
        self.execute("insert into resource (resourcetypeid, projectid, used, allocation) "
                     "values(1, 2, %s, 10)" % used)

        # add 3 triggers:
        self.execute("insert into useradministration.useraccount "
                     "values(1, 1, '%s', '26dcf77e2de89027e8895baea8e45057', 'sNgmwwN7fk')" % self.user_name)
        self.execute("insert into lofar_trigger (id, username, hostname, projectname, metadata) "
                     "values (%s, '%s', 'host', '%s', 'meta')" % (self.trigger_id, self.user_name, self.project_name))
        self.execute("insert into lofar_trigger (id, username, hostname, projectname, metadata) "
                     "values (%s, '%s', 'host', '%s', 'meta')" % (self.trigger_id + 1, self.user_name, self.project_name))
        self.execute("insert into lofar_trigger (id, username, hostname, projectname, metadata) "
                     "values (%s, '%s', 'host', '%s', 'meta')" % (self.trigger_id + 2, self.user_name, self.project_name))

        # check initial value
        used_t, max_t = self.mom_database_wrapper.get_trigger_quota(self.project_name)
        self.assertEqual(used_t, used)

        # call update
        self.mom_database_wrapper.update_trigger_quota(self.project_name)

        # check updated value
        used_t, max_t = self.mom_database_wrapper.get_trigger_quota(self.project_name)
        self.assertEqual(used_t, 3)

        # cancel one trigger, to see if flagged triggers are not considered in use any more
        self.mom_database_wrapper.cancel_trigger(self.trigger_id + 1, 'Because.')

        # call update
        self.mom_database_wrapper.update_trigger_quota(self.project_name)

        # check updated value
        used_t, max_t = self.mom_database_wrapper.get_trigger_quota(self.project_name)
        self.assertEqual(used_t, 2)

    def test_get_storagemanager_returns_correct_value_from_db(self):
        value = "d.y.s.c.o."
        self.execute(
            "insert into mom2object values(1, NULL, NULL, 2, 'LOFAR_OBSERVATION', '%(project_name)s', 'test-lofar', "
            "NULL, 1704653, NULL, NULL, 0, 0, 0)" % {"project_name": self.project_name})
        # id, mom2objectid, observation_id, instrument, user_specification_id, system_specification_id, default_template, tbb_template, tbb_piggyback_allowed, parset, nr_output_correlated, nr_output_beamformed, nr_output_coherent_stokes, nr_output_incoherent_stokes, nr_output_flyseye, nr_output_correlated_valid, nr_output_beamformed_valid, nr_output_coherent_stokes_valid, nr_output_incoherent_stokes_valid, nr_output_flyseye_valid, feedback, aartfaac_piggyback_allowed, storage_cluster_id, processing_cluster_id, nico_testing
        self.execute("insert into lofar_observation values(83, 1, NULL, 'Interferometer', 47, 48, NULL, NULL, 0,"
                     " NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL)")
        # id, type, correlated_data, filtered_data, beamformed_data, coherent_stokes_data, incoherent_stokes_data, antenna, clock_mode, instrument_filter, integration_interval, channels_per_subband, cn_integration_steps, pencilbeams_flyseye, pencilbeams_nr_pencil_rings, pencilbeams_ring_size, stokes_selection, stokes_integrate_channels, stokes_integration_steps, station_set, timeframe, starttime, endtime, spec_duration, coherent_dedisperse_channels, dispersion_measure, subbands_per_file_cs, subbands_per_file_bf, collapsed_channels_cs, collapsed_channels_is, downsampling_steps_cs, downsampling_steps_is, which_cs, which_is, bypass_pff, enable_superterp, flyseye, tab_nr_rings, tab_ring_size, bits_per_sample, misc
        self.execute("insert into lofar_observation_specification values(47, 'USER', 1, 0, 0, 0, 0, 'HBA Dual', "
                     "'160 MHz', '170-230 MHz', 1, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, 'Custom', NULL, NULL, "
                     "NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, "
                     "16, '{\"storagemanager\":\"%s\"')" % value)

        result = self.mom_database_wrapper.get_storagemanager(2)
        self.assertEqual(result, value)

if __name__ == "__main__":
    logging.basicConfig(format = '%(asctime)s %(levelname)s %(message)s', level = logging.INFO)
    unittest.main()
