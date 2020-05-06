#!/usr/bin/env python3

# Copyright (C) 2017    ASTRON (Netherlands Institute for Radio Astronomy)
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

# $Id$

'''
'''
import logging
from datetime import timedelta
from optparse import OptionParser
from mysql import connector
from mysql.connector.errors import OperationalError
import json

from lofar.common import dbcredentials

logger=logging.getLogger(__file__)


def _idsFromString(id_string):
    if not isinstance(id_string, str):
        raise ValueError('Expected a string, got a ' + str(type(id_string)))

    # parse text: it should contain a list of ints
    # filter out everything else to prevent sql injection
    ids = [int(y) for y in [x.strip() for x in id_string.split(',')] if y.isdigit()]
    return ids


def _isListOfInts(items):
    if not items:
        return False

    if not isinstance(items, list):
        return False

    for x in items:
        if not isinstance(x, int):
            return False

    return True


def _toIdsString(ids):
    if isinstance(ids, int):
        ids_list = [ids]
    elif _isListOfInts(ids):
        ids_list = ids
    else:
        ids_list = _idsFromString(ids)

    if not ids_list:
        raise ValueError("Could not find proper ids in: " + ids)

    ids_str = ','.join([str(ident) for ident in ids_list])
    return ids_str


class MoMDatabaseWrapper:
    """Handler class for details query in mom db.

       Note that transactions are NOT supported."""
    def __init__(self, dbcreds: dbcredentials.DBCredentials = None):
        self.dbcreds = dbcreds or dbcredentials.DBCredentials().get('MoM')
        self.conn = None
        self.cursor = None

        self.useradministration_db = self.dbcreds.config["useradministration_database"]
        self.momprivilege_db = self.dbcreds.config["momprivilege_database"]

    def connect(self):
        if self.conn is None:
            connect_options = self.dbcreds.mysql_connect_options()
            connect_options['connection_timeout'] = 5

            logger.debug("Connecting to %s", self.dbcreds.stringWithHiddenPassword())
            self.conn = connector.connect(**connect_options)
            logger.debug("Connected to %s", self.dbcreds.stringWithHiddenPassword())

            # Make sure we get fresh data for each SELECT. Alternatively, we could call
            # commit() after each SELECT.
            #
            # Note that we can only set the transaction isolation level if there is no
            # transaction going on (uncommitted reads or writes).
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED");

    def disconnect(self):
        if self.conn is not None:
            logger.debug("Disconnecting from %s", self.dbcreds.stringWithHiddenPassword())
            self.cursor.close()
            self.cursor = None
            self.conn.close()
            self.conn = None
            logger.debug("Disconnected from %s", self.dbcreds.stringWithHiddenPassword())

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def _executeSelectQuery(self, query, data=None):
        # try to execute query on flaky lofar mysql connection
        # max of 3 tries, on success return result
        # use new connection for every query,
        # because on the flaky lofar network a connection may appear functional but returns improper results.
        maxtries = 3

        if data is not None and type(data) not in (tuple, dict):
            raise ValueError('Need data as tuple or dict, got ' + str(type(data)))

        for i in range(maxtries):
            try:
                self.connect()
                self.cursor.execute(query, data)
                result = self.cursor.fetchall()
                self.disconnect() # needed for selects on cached results
                return result
            except (OperationalError, AttributeError) as e:
                logger.error(str(e))

                if i+1 == maxtries:
                    raise e

                self.disconnect()

    def _executeInsertQuery(self, query, data=None):
        # try to execute query on flaky lofar mysql connection
        # max of 3 tries, on success return the row id
        # use new connection for every query,
        # because on the flaky lofar network a connection may appear functional but returns improper results.
        maxtries = 3

        for i in range(maxtries):
            try:
                self.connect()
                self.cursor.execute(query, data)
                self.conn.commit()
                return self.cursor.lastrowid
            except (OperationalError, AttributeError) as e:
                logger.error(str(e))

                if i+1 == maxtries:
                    raise e

                self.disconnect()

    def _executeUpdateQuery(self, query, data=None):
        # try to execute query on flaky lofar mysql connection
        # max of 3 tries, on success return number of affected rows
        # use new connection for every query,
        # because on the flaky lofar network a connection may appear functional but returns improper results.
        maxtries = 3

        for i in range(maxtries):
            try:
                self.connect()
                print(query, data)
                self.cursor.execute(query, data)
                rowcount = self.cursor.rowcount
                self.conn.commit()
                return rowcount
            except (OperationalError, AttributeError) as e:
                logger.error(str(e))

                if i + 1 == maxtries:
                    raise e
                self.disconnect()

    def add_trigger(self, user_name, host_name, project_name, meta_data):
        logger.info("add_trigger for user_name: %s, host_name: %s, project_name: %s, meta_data: %s",
                    user_name, host_name, project_name, meta_data)

        query = """insert into lofar_trigger (username, hostname, projectname, metadata)
values (%s, %s, %s, %s)"""
        parameters = (user_name, host_name, project_name, meta_data)

        row_id = self._executeInsertQuery(query, parameters)

        logger.info("add_trigger for user_name(%s), host_name(%s), project_name(%s), meta_data(%s): %s",
                    user_name, host_name, project_name, meta_data, row_id)

        return row_id

    def cancel_trigger(self, trigger_id, reason):
        logger.info("cancel_trigger for trigger_id: %s, reason: %s", trigger_id, reason)

        query = """UPDATE lofar_trigger
                SET cancelled=1, cancelled_at=NOW(), cancelled_reason=%s
                WHERE id = %s"""
        parameters = (reason, str(trigger_id))
        rowcount = self._executeUpdateQuery(query, parameters)

        if rowcount < 1:
            raise ValueError("cancel_trigger for trigger_id: %s returned affected row count of %s" % (trigger_id, rowcount))

        logger.info("cancel_trigger for trigger_id: %s done. Affected rows: %s", trigger_id, rowcount)

    def update_trigger_quota(self, project_name):
        logger.info("update_trigger_quota for project: %s", project_name)

        query = """SELECT * FROM lofar_trigger
                   WHERE projectname = %s
                   AND cancelled = 0"""

        parameters = (project_name,)
        rows = self._executeSelectQuery(query, parameters)
        if len(rows) == 0:
            raise ValueError('No trigger quota found for project %s' % project_name)

        numtriggers = len(rows)

        query = """UPDATE resource
                   JOIN resourcetype ON resource.resourcetypeid = resourcetype.id
                   JOIN mom2object ON resource.projectid=mom2object.id
                   SET resource.used=%s
                   WHERE resourcetype.type = 'LOFAR_TRIGGERS'
                   AND mom2object.name = %s"""

        parameters = (numtriggers, project_name)
        rowcount = self._executeUpdateQuery(query, parameters)

        if rowcount < 1:
            raise ValueError("update_trigger_quota for project %s returned returned affected row count of %s" % (project_name, rowcount))

        logger.info("update_trigger_quota for project %s done. Affected rows: %s", project_name, rowcount)

    def get_project_priority(self, project_name):
        logger.info("get_project_priority for project_name: %s", project_name)

        query = """SELECT priority FROM project
join mom2object on project.mom2objectid=mom2object.id
where mom2object.name = %s"""
        parameters = (project_name, )

        rows = self._executeSelectQuery(query, parameters)

        if not rows:
            raise ValueError("project name (%s) not found in MoM database" % project_name)

        priority = rows[0]['priority']

        logger.info("get_project_priority for project_name (%s): %s", project_name, priority)

        return priority

    def allows_triggers(self, project_name):
        """returns whether a project is allowed to submit triggers
        :param project_name:
        :return: Boolean
        """
        logger.info("allows_triggers for project_name: %s", project_name)

        query = """SELECT allowtriggers FROM project
join mom2object on project.mom2objectid=mom2object.id
where mom2object.name = %s"""
        parameters = (project_name, )

        rows = self._executeSelectQuery(query, parameters)

        if not rows:
            raise ValueError("project name (%s) not found in MoM database" % project_name)

        allows = rows[0]['allowtriggers']

        logger.info("allows_triggers for project_name (%s) result: %s", project_name, allows)

        return allows

    def authorized_add_with_status(self, user_name, project_name, job_type, status):
        """returns whether user is allowed in project to move a certain jobtype to a certain state
        :param user_name:
        :param project_name:
        :param job_type: should be either 'observation', 'ingest' or 'pipeline'
        :param status: status should be either 'opened' or 'approved'
        :return: Boolean
        """
        if status not in ['opened', 'approved']:
            raise ValueError("status should be either 'opened' or 'approved'")

        if job_type not in ['observation', 'ingest', 'pipeline']:
            raise ValueError("job_type should be either 'observation', 'ingest' or 'pipeline'")

        logger.info("authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s",
                    user_name, project_name, job_type, status)

        status_type = {
            'observation': 'OBSERVATION',
            'ingest': 'EXPORT',
            'pipeline': 'POSTPROCESS'
        }

        # query have opened status hardcoded because this is domain knowledge and works for the current requirements.
        # If more status transitions are needed this query will be more complex
        # The or on the status will then not be valid anymore.
        query_system_rights = """SELECT 1 FROM """ + self.useradministration_db + """.useraccount as useraccount
        join """ + self.useradministration_db + """.useraccountsystemrole as system_role on useraccount.userid=system_role.useraccountid
        join """ + self.momprivilege_db + """.statustransitionrole as transition_role on system_role.systemroleid=transition_role.roleid
        join """ + self.momprivilege_db + """.statustransition as transition on transition_role.statustransitionid=transition.id
        join status as open_status on open_status.code='opened'
        join status as status on status.id=transition.newstatusid
        and (transition.oldstatusid=0 or transition.oldstatusid=open_status.id)
        where status.code=%s and
        status.type='""" + status_type[job_type] + """' and
        open_status.type='""" + status_type[job_type] + """' and
        transition_role.roletype="nl.astron.useradministration.data.entities.SystemRole" and
        useraccount.username=%s"""
        parameters = (status, user_name)

        rows_system_rights = self._executeSelectQuery(query_system_rights, parameters)

        # query have opened status hardcoded because this is domain knowledge and works for the current requirements.
        # If more status transitions are needed this query will be more complex.
        # The or on the status will then not be valid anymore.
        query_project_rights = """SELECT 1 FROM mom2object as project
        join member as member on member.projectid=project.id
        join registeredmember as registered_member on registered_member.memberid=member.id
        join """ + self.useradministration_db + """.useraccount as useraccount on registered_member.userid=useraccount.id
        join memberprojectrole as member_project_role on member_project_role.memberid=member.id
        join projectrole as project_role on project_role.id=member_project_role.projectroleid
        join """ + self.momprivilege_db + """.statustransitionrole as transition_role on project_role.id=transition_role.roleid
        join """ + self.momprivilege_db + """.statustransition as transition on transition_role.statustransitionid=transition.id
        join status as open_status on open_status.code='opened'
        join status as status on status.id=transition.newstatusid
        and (transition.oldstatusid=0 or transition.oldstatusid=open_status.id)
        where status.code=%s and
        status.type='""" + status_type[job_type] + """' and
        open_status.type='""" + status_type[job_type] + """' and
        transition_role.roletype="nl.astron.mom2.data.entities.ProjectRole" and
        useraccount.username=%s and
        project.name=%s"""
        parameters = (status, user_name, project_name)

        rows_project_rights = self._executeSelectQuery(query_project_rights, parameters)

        authorized = len(rows_system_rights) != 0 or len(rows_project_rights) != 0

        logger.info("authorized_add_with_status for user_name: %s project_name: %s job_type: %s status: %s result: %s",
                    user_name, project_name, job_type, status, authorized)

        return authorized

    def folder_exists(self, folder_path):
        """ returns true if folder exists
        :param folder_path:
        :return: Boolean
        """
        logger.info("folder_exists for folder: %s", folder_path)

        project_name, folders = self._get_project_name_and_folders(folder_path)

        query = self._build_folder_exists_query(len(folders))
        parameters = tuple(folders) + (project_name, )

        rows = self._executeSelectQuery(query, parameters)

        exists = len(rows) != 0

        logger.info("folder_exists for folder (%s): %s", folder_path, exists)

        return exists

    def _get_project_name_and_folders(self, folder_path):
        if not folder_path.startswith('/'):
            raise ValueError("Folder path (%s) does not start with a /" % folder_path)

        path_parts = folder_path.split('/')

        project_name = path_parts[1]

        if project_name == "":
            raise ValueError("Folder path (%s) should minimally have a project" % folder_path)

        if len(path_parts) > 2:
            if path_parts[-1] == "":
                folders = path_parts[2:-1]
            else:
                folders = path_parts[2:]
        else:
            folders = []

        return project_name, folders

    def _build_folder_exists_query(self, folder_count):
        query = """SELECT 1\nFROM mom2object as project """
        parent_id = "project"

        for index in range(folder_count):
            folder_alias = "folder%s" % index
            query += """\njoin mom2object as """ + folder_alias + """ on
            """ + folder_alias + """.parentid=""" + parent_id + """.id and
            """ + folder_alias + """.mom2objecttype="FOLDER" and
            """ + folder_alias + """.name=%s"""
            parent_id = folder_alias

        query += """\nwhere project.mom2objecttype="PROJECT" and project.name=%s"""

        return query

    def is_project_active(self, project_name):
        """ returns true if project is available and active
        :param project_name:
        :return: Boolean
        """
        logger.info("is_project_active for project name: %s", project_name)

        query = """SELECT 1
        FROM mom2object as project
        left join mom2objectstatus as status on project.currentstatusid = status.id
        where project.mom2objecttype='PROJECT' and status.statusid = 7 and project.name = %s;"""
        parameters = (project_name, )

        rows = self._executeSelectQuery(query, parameters)

        is_active = len(rows) != 0

        logger.info("is_project_active for project (%s): %s", project_name, is_active)

        return is_active

    def is_user_operator(self, user_name = None):
        """ Check if user_name is an operator.
        :param user_name: The string that the tables are checked against.
        :return: True if the user_name has the operator role assigned.
        """
        if user_name is None:
            raise ValueError("user name cannot be undefined")

        logger.info('is_user_operator for user name %s', user_name)

        query = '''select *
            from '''+ self.useradministration_db + '''.useraccount
            join ''' + self.useradministration_db + '''.useraccountsystemrole
            join ''' + self.useradministration_db + '''.systemrole
            where
                useraccount.username = %s and
                useraccountsystemrole.useraccountid = useraccount.userid and
                systemrole.name = "Operator" and
                useraccountsystemrole.systemroleid = systemrole.id'''
        parameters = (user_name, )
        rows = self._executeSelectQuery(query, parameters)

        isOperator = False
        # If a user_name has the operator role assigned at least one
        # row will be returned.  No rows will be returned if the user
        # name has no operator role assigned.
        if len(rows) > 0:
            # We have a winner!
            isOperator = True

        logger.info('%s is %san operator.', user_name,
            'not ' if isOperator is False else '')

        return isOperator

    def get_trigger_id(self, mom_id):
        """ returns trigger id if mom_id has an trigger id else returns a None
        :param mom_id:
        :return: Integer or None
        """
        logger.info("get_trigger_id for mom_id: %s", mom_id)

        trigger_id = None
        misc = self._get_misc_contents(mom_id)
        if misc and 'trigger_id' in misc:
            trigger_id = misc['trigger_id']

        logger.info("get_trigger_id for mom_id (%s): %s", mom_id, trigger_id)
        return trigger_id

    def get_trigger_quota(self, project_name):
        """ returns trigger quota as tuple (current, max)
        :param project_name
        :return: (Integer, Integer)
        """
        logger.info("get_trigger_quota for project_name: %s", project_name)

        query = """SELECT used, allocation FROM resource
                            JOIN resourcetype ON resource.resourcetypeid = resourcetype.id
                            JOIN mom2object ON resource.projectid=mom2object.id
                            WHERE resourcetype.type = 'LOFAR_TRIGGERS'
                            AND mom2object.name = %s"""

        parameters = (project_name,)
        rows = self._executeSelectQuery(query, parameters)
        if len(rows) == 0:
            raise ValueError("no trigger quota found for project_name %s in MoM database" % project_name)

        quota = (rows[0]['used'],rows[0]['allocation'])
        logger.info("get_trigger_quota for project_name %s: %s", project_name, quota)
        return quota

    def get_projectname_for_trigger(self, trigger_id):
        """ returns project id for given trigger id
        :param trigger_id
        :return: String
        """
        logger.info("get_projectname_for_trigger: %s", trigger_id)

        query = """SELECT projectname FROM lofar_trigger WHERE id = %s"""
        parameters = (str(trigger_id),)

        rows = self._executeSelectQuery(query, parameters)
        if len(rows) == 0:
            raise ValueError("trigger_id (%s) not found in MoM database" % trigger_id)

        projectname = rows[0]['projectname']
        logger.info("get_projectname_for_trigger %s: %s", trigger_id, projectname)
        return projectname

    def get_project_details(self, mom_id):
        """get the pi and contact author email addresses for a project mom id
        :param a project mom id
        :rtype dict with pi_email and author_email keys containing the corresponding emails addresses as values
        """
        logger.info("get_project_details for mom_id: %s", mom_id)

        query = """SELECT project_role.name, user.email FROM mom2object as project
join member as member on member.projectid=project.id
join registeredmember as registered_member on registered_member.memberid=member.id
join """ + self.useradministration_db + """.useraccount as useraccount on registered_member.userid=useraccount.id
join """ + self.useradministration_db + """.user as user on user.id=useraccount.id
join memberprojectrole as member_project_role on member_project_role.memberid=member.id
join projectrole as project_role on project_role.id=member_project_role.projectroleid
where project.mom2id = %s and (project_role.name = "Pi" or project_role.name = "Contact author");"""
        parameters = (mom_id, )

        rows = self._executeSelectQuery(query, parameters)

        result = {"pi_email": "", "author_email": ""}

        for row in rows:
            if row["name"] == "Pi":
                result["pi_email"] = row["email"]
            if row["name"] == "Contact author":
                result["author_email"] = row["email"]

        logger.info("get_project_details for mom_id (%s): %s", mom_id, result)

        return result

    def get_project_priorities_for_objects(self, mom_ids):
        """ get the project priorities for given mom object mom_ids (observations/pipelines/reservations)
        :param mom_ids: mixed mom_ids comma seperated string of mom2object id's, or list of ints
        :rtype list of dict's key value pairs with the project priorities
        """
        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.info("get_project_priorities for mom ids: %s", ids_str)

        parameters = tuple(map(int, ids_str.split(',')))
        placeholder = (len(parameters)*'%s,')[:-1]

        query = '''
                SELECT project.priority as project_priority, object.mom2id as object_mom2id
                FROM mom2object as object
                left join project as project on project.mom2objectid = object.ownerprojectid
                where object.mom2id in (%s)
                order by object_mom2id
                ''' % placeholder

        rows = self._executeSelectQuery(query, parameters)

        logger.info("Found %d results for mom id(s): %s", len(rows) if rows else 0, ids_str)

        result = {}
        for row in rows:
            pprio = row['project_priority']
            mom2id = row['object_mom2id']
            result[mom2id] = pprio

        logger.info(result)

        return result

    def connect_to_predecessor(self, mom_id: int, predecessor_mom_id: int):
        '''connect the mom-object given by the mom_id to the mom-object given by the predecessor_mom_id.
        :raises if the object is not in in 'opened' status
        :raises if the both objects are not in the same group
        :param mom_id: the mom2id of the object
        :param predecessor_mom_id: the mom2id of the predecessor object
        '''
        # fetch the both objects from the db
        objects = self.getObjectDetails([mom_id, predecessor_mom_id])
        object = objects[mom_id]
        predecessor = objects[predecessor_mom_id]

        # check for correct status
        if object['object_status'] != 'opened':
            raise ValueError("Cannot connect object %s to predecessor %s because its status is not 'opened'" % (object, predecessor))

        if object['object_group_id'] != predecessor['object_group_id']:
            raise ValueError("Cannot connect object %s to predecessor %s because they are not in the same group" % (object, predecessor))

        # magic MoM-business-logic-like string parsing...
        # MoM specs encode precesessors with so called 'topology' strings (or comma seperated strings for multiple predecessors)
        # these topology strings are translated in mom2id's (prefixed with an M)
        # and then MoM can link the two objects to each other on a 'opened' to 'approved' status change (you can do such status change with the momhttpclient)
        topopolgy_group_prefix = 'mom.G%d.' % (object['object_group_id'])
        expected_object_predecessor_string_part = predecessor['object_topology'].replace(topopolgy_group_prefix, '')
        replacement_object_predecessor_string_part = 'M%d' % (predecessor_mom_id)

        object_predecessor_string = object.get('object_predecessor_string') or ''
        object_predecessor_string_parts = [x.strip() for x in object_predecessor_string.split(',')]
        new_object_predecessor_string_parts = [replacement_object_predecessor_string_part if p == expected_object_predecessor_string_part else p for p in  object_predecessor_string_parts]
        new_object_predecessor_string = ','.join(new_object_predecessor_string_parts)

        if object_predecessor_string != new_object_predecessor_string:
            logger.info("connect_to_predecessor: updating predecessor_string of %s from '%s' to '%s'", mom_id, object_predecessor_string, new_object_predecessor_string)
            self._executeUpdateQuery("UPDATE mom2object set predecessor = %s where mom2id=%s", (new_object_predecessor_string, mom_id))
        else:
            if replacement_object_predecessor_string_part in object_predecessor_string_parts:
                logger.info("connect_to_predecessor: %s is already a connected predecessor of %s according to it's topology %s %s",
                               predecessor_mom_id, mom_id, predecessor, object)
            else:
                logger.warning("connect_to_predecessor: %s is not a predecessor of %s according to it's topology %s %s",
                               predecessor_mom_id, mom_id, predecessor, object)

    def getObjectDetailsOfObservationsAndPipelinesInGroup(self, mom_group_id):
        group_object = self.getObjectDetails(mom_group_id)[mom_group_id]
        if group_object['object_type'] != 'FOLDER' and group_object['object_group_id'] != group_object['object_mom2id']:
            raise ValueError("object with mom_group_id=%s is not a group folder: %s" % (mom_group_id, group_object))

        mom_group_object_id = group_object['object_mom2objectid']
        obs_pl_mom_ids = [x['mom2id'] for x in self._executeSelectQuery("select * from mom2object where parentid=%s",(mom_group_object_id,))
                          if 'OBSERVATION' in x['mom2objecttype'] or 'PIPELINE' in x['mom2objecttype']]
        return list(self.getObjectDetails(obs_pl_mom_ids).values())

    def getGroupsInGroup(self, mom_group_id):
        group_object = self.getObjectDetails(mom_group_id)[mom_group_id]
        if group_object['object_type'] != 'FOLDER' and group_object['object_group_id'] != group_object['object_mom2id']:
            raise ValueError("object with mom_group_id=%s is not a group folder: %s" % (mom_group_id, group_object))

        mom_group_object_id = group_object['object_mom2objectid']
        groups_mom_ids = [x['mom2id'] for x in self._executeSelectQuery("select * from mom2object where parentid=%s",(mom_group_object_id,))
                          if 'FOLDER' == x['mom2objecttype']]
        return list(self.getObjectDetails(groups_mom_ids).values())

    def getObjectDetails(self, mom_ids):
        """
        get the object details (project_mom2id, project_name,
        project_description, object_mom2id, object_name, object_description,
        object_type, object_group_id, object_group_name, object_status) for given mom object mom_ids
        :param mom_ids: mixed mom_ids comma seperated string of mom2object id's, or list of ints
        :rtype list of dict's key value pairs with the project details
        """
        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.debug("getObjectDetails for mom ids: %s", ids_str)

        parameters = tuple(map(int, ids_str.split(',')))
        placeholder = (len(parameters)*'%s,')[:-1]

        # TODO: make a view for this query in momdb!
        query = '''SELECT project.mom2id as project_mom2id, project.id as project_mom2objectid, project.name as
        project_name, project.description as project_description, object.mom2id as object_mom2id,
        object.id as object_mom2objectid, object.name as object_name, object.description as object_description,
        object.mom2objecttype as object_type, status.code as object_status, mostatus.pending as object_status_pending,
        object.group_id as object_group_id,
        object.topology as object_topology, object.predecessor as object_predecessor_string,
        grp.id as object_group_mom2objectid, grp.name as object_group_name, grp.description as object_group_description,
        parent_grp.id as parent_group_mom2objectid, parent_grp.mom2id as parent_group_mom2id,
        parent_grp.name as parent_group_name, parent_grp.description as parent_group_description
        FROM mom2object as object
        left join mom2object as project on project.id = object.ownerprojectid
        left join mom2object as grp on grp.mom2id = object.group_id
        left join mom2objectstatus as mostatus on object.currentstatusid = mostatus.id
        inner join status on mostatus.statusid = status.id
        left join mom2object as parent_grp on parent_grp.id = grp.parentid
        where object.mom2id in (%s)
        order by project_mom2id
        ''' % ids_str
        #TODO: get rid of stupid _toIdsString method, and use param argument of _executeSelectQuery everywhere
        #so the connector can take care of proper string parsing and prevent sql injection.
        rows = self._executeSelectQuery(query)

        logger.debug("Found %d results for mom id(s): %s", len(rows) if rows else 0, ids_str)

        result = {}
        for row in rows:
            object_mom2id = row['object_mom2id']
            result[object_mom2id] = dict(row)

        return result

    def getProjects(self):
        """
        get the list of all projects with columns (project_mom2id, project_name,
        project_description, status_name, status_id, last_user_id,
        last_user_name, statustime)
        :rtype list of dict's key value pairs with all projects
        """
        # TODO: make a view for this query in momdb!
        query = '''SELECT project_object.mom2id as mom2id, project_object.name as name, project_object.description as description,
                          statustype.code as status_name,  statustype.id as status_id,
                          status.userid as last_user_id, status.name as last_user_name, status.statustime as statustime,
                          project.priority as priority, project.allowtriggers as allow_triggers,
                          r.used as num_used_triggers, r.allocation as num_allowed_triggers
                    FROM mom2object as project_object
                    LEFT JOIN project ON project.mom2objectid = project_object.id
                    LEFT JOIN (SELECT projectid, used, allocation
                               FROM resource
                               JOIN resourcetype ON resource.resourcetypeid = resourcetype.id
                               WHERE resourcetype.type = 'LOFAR_TRIGGERS') r ON r.projectid = project.mom2objectid
                    LEFT JOIN mom2objectstatus as status ON project_object.currentstatusid = status.id
                    LEFT JOIN status as statustype ON status.statusid=statustype.id
                    WHERE project_object.mom2objecttype='PROJECT'
                    ORDER BY mom2id;
                    '''

        result = self._executeSelectQuery(query)

        logger.info("Found %d projects", len(result))

        # convert types
        for p in result:
            p['allow_triggers'] = bool(p['allow_triggers'])
            p['num_used_triggers'] = 0 if p['num_used_triggers'] is None else int(p['num_used_triggers'])
            p['num_allowed_triggers'] = 0 if p['num_allowed_triggers'] is None else int(p['num_allowed_triggers'])

        return result

    def getProject(self, project_mom2id):
        """
        get project for the given project_mom2id with columns (project_mom2id, project_name,
        project_description, status_name, status_id, last_user_id,
        last_user_name, statustime)
        """
        ids_str = _toIdsString(project_mom2id)

        # TODO: make a view for this query in momdb!
        query = '''SELECT project.mom2id as mom2id, project.name as name, project.description as description,
                statustype.code as status_name,  statustype.id as status_id,
        status.userid as last_user_id, status.name as last_user_name, status.statustime as statustime
        FROM mom2object as project
        left join mom2objectstatus as status on project.currentstatusid = status.id
        left join status as statustype on status.statusid=statustype.id
        where project.mom2objecttype='PROJECT' and project.mom2id = %s
        order by mom2id;
        '''
        parameters = (ids_str, )

        result = self._executeSelectQuery(query, parameters)

        return result

    def get_triggers(self, user_name = None):
        # Make sure that the user_name is not empty.
        if user_name is None:
            user_name = "*"

        query = '''
        select
            obj_status.code,
            obj_status.type,
            lofar_trigger.arrivaltime,
            mom.name,
            mom.mom2id as mom_id,
            mom.id as momurl_id,
            lofar_trigger.*
        from ''' + self.useradministration_db + '''.useraccount as useraccount
        join registeredmember as registeredmember
        join member as project_member
        join mom2object as mom
        join lofar_trigger as lofar_trigger
        join status as obj_status
        join mom2objectstatus as mom2objectstatus
        where
            useraccount.userid = registeredmember.userid and
            registeredmember.memberid = project_member.id and
            project_member.projectid = mom.id and
            mom.name = lofar_trigger.projectname and
            mom2objectstatus.id = mom.currentstatusid and
            obj_status.id = mom2objectstatus.statusid'''

        parameters = ()
        # If the user is an operator then skip this and the result
        # will contain all triggers.
        if self.is_user_operator(user_name) is False:
            query += ''' and useraccount.username = %s'''
            parameters = (user_name, )

        rows = self._executeSelectQuery(query, parameters)

        result = {}
        for row in rows:
            mom_id = str(row['mom_id'])
            projectName = row['projectname']
            trigger_id = str(row['id'])
            arrival_time = row['arrivaltime'].isoformat()
            status = str(row['type']) + ', ' + str(row['code'])
            momurl_id = str(row['momurl_id'])

            result[trigger_id] = {'mom_id': mom_id,
                'project_name': projectName,
                'arrival_time': arrival_time,
                'status': status,
                'momurl_id': momurl_id}

        logger.debug('Received the following triggers from the DB: %s', result)

        return result

    def get_trigger_spec(self, user_name = None, trigger_id = None):
        # Make sure that the user_name is not empty.
        if user_name is None:
            raise ValueError("user name cannot be undefined")

        if trigger_id is None:
            raise ValueError("trigger id cannot be undefined")

        logger.info("Getting trigger spec for user '%s' and trigger "
            "id %s", user_name, trigger_id)

        query = '''select
            lofar_trigger.metadata as metadata
        from ''' + self.useradministration_db + '''.useraccount as useraccount
        join registeredmember as registeredmember
        join member as project_member
        join mom2object as mom
        join lofar_trigger as lofar_trigger
        where
            lofar_trigger.id = %s and
            useraccount.userid = registeredmember.userid and
            registeredmember.memberid = project_member.id and
            project_member.projectid = mom.id and
            mom.name = lofar_trigger.projectname'''

        parameters = [trigger_id]
        if self.is_user_operator(user_name) is False:
            query += ''' and useraccount.username = %s'''
            parameters.append(user_name)

        rows = self._executeSelectQuery(query, tuple(parameters))
        # The DB returns multiple rows that contain the same data.
        # Just choose row 0's metadata.
        result = str(rows[0]['metadata'])

        logger.info('received a trigger spec for user %s and trigger '
            'id %d', user_name, trigger_id)
        logger.debug('Received this trigger spec from the DB: %s',
            result)

        return result

    def getProjectTaskIds(self, project_mom2id):
        if not project_mom2id:
            return {}

        ids_str = _toIdsString(project_mom2id)

        logger.info("getProjectTaskIds for project_mom2id: %s", ids_str)

        query = '''SELECT tasks.mom2id FROM mom2object tasks
                    inner join mom2object project on project.id = tasks.ownerprojectid
                    where project.mom2id = %s and
                    (tasks.mom2objecttype = 'LOFAR_OBSERVATION' or tasks.mom2objecttype like \'%%PIPELINE%%\');'''
        parameters = (ids_str, )

        rows = self._executeSelectQuery(query, parameters)

        result = {'project_mom2id': project_mom2id, 'task_mom2ids': [r['mom2id'] for r in rows]}

        logger.info('task ids for project: %s', result)

        return result

    def getPredecessorIds(self, mom_ids):
        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.info("getPredecessorIds for mom ids: %s", ids_str)

        query = '''SELECT mom2id, predecessor
        FROM mom2object
        where mom2id in (%s)
        order by mom2id;
        '''
        parameters = (ids_str, )

        rows = self._executeSelectQuery(query, parameters)

        result = {}
        for row in rows:
            mom2id = row['mom2id']
            pred_string = row['predecessor']
            pred_id_list = [y[1:] for y in [x.strip() for x in pred_string.split(',')] if y[0] == 'M'] if pred_string else []
            pred_id_list = [int(x) for x in pred_id_list if x.isdigit()]
            result[str(mom2id)] = pred_id_list

        for mom2id in ids_str.split(','):
            if mom2id not in result:
                result[mom2id] = []

        logger.info('predecessors: %s', result)

        return result

    def getSuccessorIds(self, mom_ids):
        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.info("getSuccessorIds for mom ids: %s", ids_str)

        condition = ' OR '.join(['predecessor LIKE \'%%M%s%%\'' % x for x in ids_str.split(',')])

        # TODO: make a view for this query in momdb!
        query = '''SELECT mom2id, predecessor
        FROM mom2object
        where %s
        order by mom2id;
        '''
        parameters = (condition, )
        rows = self._executeSelectQuery(query, parameters)

        result = {}
        for mom2id in ids_str.split(','):
            result[mom2id] = []

        for row in rows:
            suc_mom2id = row['mom2id']
            pred_string = row['predecessor']
            pred_id_list = [y[1:] for y in [x.strip() for x in pred_string.split(',')] if y[0] == 'M'] if pred_string else []
            for mom2id in ids_str.split(','):
                if mom2id in pred_id_list:
                    result[str(mom2id)].append(suc_mom2id)

        logger.info('successors: %s', result)

        return result

    def getTaskIdsGraph(self, mom2id):
        """
        Get the fully connected graph of interconnected tasks given any mom2id in that graph
        returns: dict with mom2id:node as key value pairs, where each node is a dict with items
        node_mom2id, predecessor_ids, successor_ids
        """

        def extendGraphWithPredecessorsAndSuccessors(graph, current_node_id):
            node = graph[current_node_id]
            node_mom2id = node['node_mom2id']

            new_node_ids = set()

            node_pred_ids = self.getPredecessorIds(node_mom2id).get(str(node_mom2id), [])
            for pred_id in node_pred_ids:
                if pred_id not in node['predecessor_ids']:
                    node['predecessor_ids'].append(pred_id)

                pred_node = graph.get(pred_id)

                if not pred_node:
                    graph[pred_id] = {'node_mom2id': pred_id,
                                      'predecessor_ids': [],
                                      'successor_ids': [node_mom2id]}

                    new_node_ids.add(pred_id)

            node_succ_ids = self.getSuccessorIds(node_mom2id).get(str(node_mom2id), [])
            for succ_id in node_succ_ids:
                if succ_id not in node['successor_ids']:
                    node['successor_ids'].append(succ_id)

                succ_node = graph.get(succ_id)

                if not succ_node:
                    graph[succ_id] = {'node_mom2id': succ_id,
                                      'predecessor_ids': [node_mom2id],
                                      'successor_ids': []}

                    new_node_ids.add(succ_id)

            # recurse
            for new_node_id in new_node_ids:
                extendGraphWithPredecessorsAndSuccessors(graph, new_node_id)

        # start with simple graph with the given node_mom2id
        the_graph = {mom2id: {'node_mom2id': mom2id,
                              'predecessor_ids': [],
                              'successor_ids': []}}

        # recursively append next layers until done.
        extendGraphWithPredecessorsAndSuccessors(the_graph, mom2id)

        # the_graph is now complete, return it
        return the_graph

    def getTaskIdsInGroup(self, mom_group_ids):
        if not mom_group_ids:
            return {}

        ids_str = _toIdsString(mom_group_ids)

        logger.info("getTaskIdsInGroup for mom group ids: %s", ids_str)

        query = '''SELECT mom2id, group_id FROM mom2object
        where group_id in (%s)
        and (mom2objecttype = 'LOFAR_OBSERVATION' or mom2objecttype like \'%%PIPELINE%%\')'''
        parameters = (ids_str, )

        rows = self._executeSelectQuery(query, parameters)

        result = {}
        for group_id in ids_str.split(','):
            result[group_id] = []

        for row in rows:
            mom2id = row['mom2id']
            group_id = row['group_id']
            result[str(group_id)].append(mom2id)

        logger.info('task ids per group: %s', result)

        return result

    def getGroupsInParentGroup(self, mom_parent_group_ids):
        if not mom_parent_group_ids:
            return {}

        ids_str = _toIdsString(mom_parent_group_ids)

        logger.debug("getGroupsInParentGroup for mom parent group ids: %s", ids_str)

        query = '''SELECT parent.id as parent_mom2object_id, parent.mom2id as parent_mom2id,
                    grp.mom2id as group_mom2id, grp.id as group_mom2object_id, grp.name as group_name,
                    grp.description as group_description
                    from mom2object parent
                    inner join mom2object grp on parent.id = grp.parentid
                    where parent.mom2id in (%s)
                    and grp.group_id = grp.mom2id'''
        parameters = (ids_str, )

        rows = self._executeSelectQuery(query, parameters)

        result = {}
        for parent_group_id in ids_str.split(','):
            result[parent_group_id] = []

        for row in rows:
            parent_group_id = row['parent_mom2id']
            result[str(parent_group_id)].append(row)

        logger.info("getGroupsInParentGroup result: %s", result)

        return result

    def getTaskIdsInParentGroup(self, mom_parent_group_ids):
        if not mom_parent_group_ids:
            return {}

        ids_str = _toIdsString(mom_parent_group_ids)

        logger.debug("getTaskIdsInParentGroup for mom parent group ids: %s", ids_str)

        groups_result = self.getGroupsInParentGroup(ids_str)

        result = {}
        for parent_mom2id, groups in list(groups_result.items()):
            task_mom2ids_for_parent = set()
            group_ids = [x['group_mom2id'] for x in groups]
            group_tasks_id_result = self.getTaskIdsInGroup(group_ids)
            for group_id, task_mom2ids in list(group_tasks_id_result.items()):
                task_mom2ids_for_parent |= set(task_mom2ids)

            result[parent_mom2id] = list(task_mom2ids_for_parent)

        logger.info('getTaskIdsInParentGroup: %s', result)

        return result

    def getMoMIdsForOTDBIds(self, otdb_ids):
        """
        reverse lookup from otdb_id(s) to mom2id(s)
        returns: dict with otdb_id(s) in keys, mom2id(s) as values
        """

        if not otdb_ids:
            return {}

        ids_str = _toIdsString(otdb_ids)

        logger.debug("getMoMIdsForOTDBIds for otdb ids: %s" % ids_str)

        result = {int(otdb_id): None for otdb_id in ids_str.split(',')}

        # first query all observations
        query = '''SELECT obs.observation_id as otdb_id, mo.mom2id as mom2id
                   FROM lofar_observation obs
                   INNER JOIN mom2object mo on mo.id = obs.mom2objectid
                   WHERE obs.observation_id IN (%s)
                   ''' % (ids_str,)

        rows = self._executeSelectQuery(query)

        for row in rows:
            if row['mom2id'] is not None:
                result[row['otdb_id']] = row['mom2id']

        # then query all pipelines and combine the results
        query = '''SELECT pl.pipeline_id as otdb_id, mo.mom2id as mom2id
                   FROM lofar_pipeline pl
                   INNER JOIN mom2object mo on mo.id = pl.mom2objectid
                   WHERE pl.pipeline_id IN (%s)
                   ''' % (ids_str,)

        rows = self._executeSelectQuery(query)

        for row in rows:
            if row['mom2id'] is not None:
                result[row['otdb_id']] = row['mom2id']

        logger.info("getMoMIdsForOTDBIds: %s" % result)
        return result

    def getOTDBIdsForMoMIds(self, mom_ids):
        """
        lookup from mom2id(s) to otdb_id(s)
        returns: dict with mom2id(s) in keys, otdb_id(s) as values
        """

        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.debug("getOTDBIdsForMoMIds for otdb ids: %s" % ids_str)

        result = {int(mom_id): None for mom_id in ids_str.split(',')}

        # first query all observations
        query = '''SELECT obs.observation_id as otdb_id, mo.mom2id as mom2id
                   FROM lofar_observation obs
                   INNER JOIN mom2object mo on mo.id = obs.mom2objectid
                   WHERE mo.mom2id IN (%s)
                   ''' % (ids_str,)

        rows = self._executeSelectQuery(query)

        for row in rows:
            if row['mom2id'] is not None:
                result[row['mom2id']] = row['otdb_id']

        # then query all pipelines and combine the results
        query = '''SELECT pl.pipeline_id as otdb_id, mo.mom2id as mom2id
                   FROM lofar_pipeline pl
                   INNER JOIN mom2object mo on mo.id = pl.mom2objectid
                   WHERE mo.mom2id IN (%s)
                   ''' % (ids_str,)

        rows = self._executeSelectQuery(query)

        for row in rows:
            if row['mom2id'] is not None:
                result[row['mom2id']] = row['otdb_id']

            logger.info("getOTDBIdsForMoMIds: %s" % result)
        return result

    def getDataProducts(self, mom_ids):
        if not mom_ids:
            return {}

        ids_str = _toIdsString(mom_ids)

        logger.info("getDataProducts for mom ids: %s", ids_str)

        query = '''SELECT mo.id as momobject_id, mo.mom2id as mom2id,
                   mop.id as parent_momobject_id, mop.mom2id as parent_mom2id,
                   dp.id, dp.name, dp.exported, dp.status, dp.fileformat
                   FROM mom2object mo
                   inner join dataproduct dp on mo.id = dp.mom2objectid
                   left join mom2object mop on mop.id = mo.parentid
                   where not isnull(dp.fileformat) and
                   (mo.mom2id in (%s)
                   or mo.parentid in (SELECT mo_parent.id FROM mom2object mo_parent where mo_parent.mom2id in (%s)))
                   ''' % (ids_str, ids_str)

        rows = self._executeSelectQuery(query)

        result = {}
        for mom2id in ids_str.split(','):
            result[int(mom2id)] = []

        for row in rows:
            if row['mom2id'] in result:
                result[row['mom2id']].append(dict(row))
            else:
                if row['parent_mom2id'] not in result:
                    result[row['parent_mom2id']] = []

                result[row['parent_mom2id']].append(dict(row))

        for mom2id, dps in list(result.items()):
            logger.info('Found %s dataproducts for mom2id %s', len(dps), mom2id)

        return result

        pass

    def _get_misc_contents(self, mom_id):
        """
        Get deserialized contents of misc field for given obs id. May be empty if mom_id exists but misc is empty.
        Returns None if no entry found for mom id
        :param mom_id: int
        :return: dict or None
        """
        logger.info("getting misc for mom_id: %s", mom_id)

        misc = None

        query = """SELECT mom.mom2id, mom.mom2objecttype, obs_spec.misc
                FROM mom2object as mom
                join lofar_observation as obs on mom.mom2objecttype = "LOFAR_OBSERVATION" and mom.id = obs.mom2objectid
                join lofar_observation_specification as obs_spec on
                  mom.mom2objecttype = "LOFAR_OBSERVATION" and obs.user_specification_id = obs_spec.id
                where mom.mom2id=%s
                union
                SELECT mom.mom2id, mom.mom2objecttype, pipeline.misc
                FROM mom2object as mom
                join lofar_pipeline as pipeline on mom.mom2objecttype like "%PIPELINE%"
                and mom.id = pipeline.mom2objectid
                where mom.mom2id=%s;"""
        parameters = (mom_id, mom_id)
        rows_misc = self._executeSelectQuery(query, parameters)
        logger.info("_get_misc_contents(mom_id=%s) rows_misc: %s", mom_id, rows_misc)

        if rows_misc:
            misc = {}
            misc_json = rows_misc[0]['misc']
            if misc_json:
                misc = json.loads(misc_json)

        return misc

    def get_trigger_time_restrictions(self, mom_id):
        """
        Returns min start and max end times and min/max duration for given mom id.
        :param mom_id: int
         :return: dict
         """
        logger.info("get_trigger_time_restrictions for mom_id: %s", mom_id)
        result = {"minStartTime": None, "minDuration": None, "maxDuration": None, "maxEndTime": None, "trigger_id": None}
        misc = self._get_misc_contents(mom_id)
        if misc is None:
            logger.info("no misc contents found for mom_id %s db", mom_id)
            return result

        if "trigger_id" in misc:
            result["trigger_id"] = misc['trigger_id']

        if 'timeWindow' in misc:
            time_window = misc['timeWindow']
            if "trigger_id" not in misc:
                raise NotImplementedError("TimeWindow specified for a non-triggered observation %s" % mom_id)
            if "minStartTime" in time_window:
                result["minStartTime"] = time_window["minStartTime"].replace('T', ' ')  # The T is from XML
            if "maxDuration" in time_window:
                result["maxDuration"] = timedelta(seconds=float(time_window["maxDuration"]))
            if "minDuration" in time_window:
                result["minDuration"] = timedelta(seconds=float(time_window["minDuration"]))
            if "maxEndTime" in time_window:
                result["maxEndTime"] = time_window["maxEndTime"].replace('T', ' ')  # The T is from XML
        return result

    def get_station_selection(self, mom_id):
        """
        Get the station selection represented as resource groups with min/max values for given mom id.
        :param mom_id: int
        :return: list of dict

        """
        logger.info("get_station_selection for mom_id: %s", mom_id)

        misc = self._get_misc_contents(mom_id)
        if misc is None:
            logger.info("no misc contents found for mom_id %s db", mom_id)
            return None

        station_selection = misc.get('stationSelection')

        logger.info("get_station_selection for mom_id (%s): %s", mom_id, station_selection)

        return station_selection


    def get_storagemanager(self, mom_id):
        """ returns storagemanager if mom_id has that in the misc field or else None.
        Raises ValueError if no entry is found for given mom_id
        :param mom_id:
        :return: string or None
        """
        logger.info("get_storagemanager for mom_id: %s", mom_id)

        misc = self._get_misc_contents(mom_id)
        if misc is None:
            logger.info("no misc contents found for mom_id %s db", mom_id)
            return None
        storagemanager = misc.get('storagemanager')

        logger.info("get_storagemanager for mom_id (%s): %s", mom_id, storagemanager)
        return storagemanager

if __name__ == '__main__':
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)
    with MoMDatabaseWrapper() as momdb:
        momdb.getObjectDetailsOfObservationsAndPipelinesInGroup(959088)
        # pprint(momdb.getObjectDetailsOfObservationsAndPipelinesInGroup(959079))
        # momdb.connect_to_predecessor(959087, 959086)
        # momdb._executeUpdateQuery("UPDATE mom2object set predecessor = %s where mom2id=%s",
        #                  ('M959083,M959082', 959085))
