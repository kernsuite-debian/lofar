#!/usr/bin/env python3

# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

# $Id$

'''ResourceAssignmentEditor webservice serves a interactive html5 website for
viewing and editing lofar resources.'''

import sys
import os
import time
from optparse import OptionParser
from threading import Condition, Lock, current_thread, Thread
import _strptime
from datetime import datetime, timedelta
from json import loads as json_loads
import time
import logging
import subprocess
from dateutil import parser, tz
from flask import Flask
from flask import render_template
from flask import request
from flask import abort
from flask import url_for
from lofar.common.flask_utils import gzipped
from lofar.messaging.rpc import RPCException
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.sas.resourceassignment.resourceassignmenteditor.fakedata import *
from lofar.sas.resourceassignment.resourceassignmenteditor.changeshandler import ChangesHandler, CHANGE_DELETE_TYPE
from lofar.sas.resourceassignment.resourceassignmentservice.rpc import RADBRPC
from lofar.mom.momqueryservice.momqueryrpc import MoMQueryRPC
from lofar.sas.resourceassignment.resourceassignmenteditor.mom import updateTaskMomDetails
from lofar.sas.resourceassignment.resourceassignmenteditor.storage import updateTaskStorageDetails
from lofar.sas.datamanagement.cleanup.rpc import CleanupRPC
from lofar.sas.datamanagement.storagequery.rpc import StorageQueryRPC
from lofar.sas.otdb.otdbrpc import OTDBRPC
from lofar.common import isProductionEnvironment, isTestEnvironment
from lofar.common.util import humanreadablesize
from lofar.common.subprocess_utils import communicate_returning_strings
from lofar.common import dbcredentials
from lofar.sas.resourceassignment.database.radb import RADatabase

logger = logging.getLogger(__name__)

def asDatetime(isoString):
    if isoString[-1] == 'Z':
        isoString = isoString[:-1]
    if isoString[-4] == '.':
        isoString += '000'
    return datetime.strptime(isoString, '%Y-%m-%dT%H:%M:%S.%f')

def asIsoFormat(timestamp):
    return datetime.strftime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')

__root_path = os.path.dirname(os.path.realpath(__file__))

'''The flask webservice app'''
app = Flask('Scheduler',
            instance_path=__root_path,
            template_folder=os.path.join(__root_path, 'templates'),
            static_folder=os.path.join(__root_path, 'static'),
            instance_relative_config=True)

# Load the default configuration
app.config.from_object('lofar.sas.resourceassignment.resourceassignmenteditor.config.default')


try:
    import ujson

    def convertDictDatetimeValuesToString(obj):
        '''recursively convert all string values in the dict to buffer'''
        if isinstance(obj, list):
            return [convertDictDatetimeValuesToString(x) if (isinstance(x, dict) or isinstance(x, list)) else x for x in obj]

        return dict( (k, convertDictDatetimeValuesToString(v) if (isinstance(v, dict) or isinstance(v, list)) else asIsoFormat(v) if isinstance(v, datetime) else v) for k,v in list(obj.items()))

    def jsonify(obj):
        '''faster implementation of flask.json.jsonify using ultrajson and the above datetime->string convertor'''
        json_str = ujson.dumps(dict(convertDictDatetimeValuesToString(obj)))

        return app.response_class(json_str, mimetype='application/json')
except:
    from flask.json import jsonify
    from flask.json import JSONEncoder

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, datetime):
                    return asIsoFormat(obj)
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            return JSONEncoder.default(self, obj)

    app.json_encoder = CustomJSONEncoder


rarpc = None
otdbrpc = None
curpc = None
sqrpc = None
momqueryrpc = None
changeshandler = None

_radb_pool = {}
_radb_pool_lock = Lock()
_radb_dbcreds = None

def radb():
    global _radb_pool, _radb_pool_lock

    if _radb_dbcreds:
        with _radb_pool_lock:
            thread = current_thread()
            tid = thread.ident
            now = datetime.utcnow()
            if tid not in _radb_pool:
                logger.info('creating radb connection for thread %s', tid)
                _radb_pool[tid] = { 'connection': RADatabase(dbcreds=_radb_dbcreds),
                                    'last_used': now }

            thread_conn_obj = _radb_pool[tid]
            thread_conn_obj['last_used'] = now

            threshold = timedelta(minutes=5)
            obsolete_connections_tids = [tid for tid,tco in list(_radb_pool.items()) if now - tco['last_used'] > threshold]

            for tid in obsolete_connections_tids:
                logger.info('deleting radb connection for thread %s', tid)
                del _radb_pool[tid]

            return thread_conn_obj['connection']

    return rarpc

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
@gzipped
def index():
    '''Serves the ResourceAssignmentEditor's index page'''
    return render_template('index.html', title='Scheduler')

@app.route('/projects')
@app.route('/projects.htm')
@app.route('/projects.html')
@gzipped
def projects():
    return render_template('projects.html', title='Projects')

@app.route('/rest/config')
@gzipped
def config():
    config = {'mom_base_url':'',
              'lta_base_url':'',
              'inspection_plots_base_url':'https://proxy.lofar.eu/inspect/HTML/',
              'sky_view_base_url':'http://dop344.astron.nl:5000/uvis/id'}

    if isProductionEnvironment():
        config['mom_base_url'] = 'https://lofar.astron.nl/mom3'
        config['lta_base_url'] = 'http://lofar.target.rug.nl/'
    elif isTestEnvironment():
        config['mom_base_url'] = 'http://lofartest.control.lofar:8080/mom3'
        config['lta_base_url'] = 'http://lofar-test.target.rug.nl/'

    return jsonify({'config': config})

@app.route('/rest/resources')
@gzipped
def resources():
    result = radb().getResources(include_availability=True)
    return jsonify({'resources': result})

@app.route('/rest/resources/<int:resource_id>')
@gzipped
def resource(resource_id):
    result = radb().getResources(resource_ids=[resource_id], include_availability=True)
    if result:
        return jsonify(result[0])
    return jsonify({})

@app.route('/rest/resources/<int:resource_id>/resourceclaims')
@gzipped
def resourceclaimsForResource(resource_id):
    return resourceclaimsForResourceFromUntil(resource_id, None, None)

@app.route('/rest/resources/<int:resource_id>/resourceclaims/<string:fromTimestamp>')
@gzipped
def resourceclaimsForResourceFrom(resource_id, fromTimestamp=None):
    return resourceclaimsForResourceFromUntil(resource_id, fromTimestamp, None)

@app.route('/rest/resources/<int:resource_id>/resourceclaims/<string:fromTimestamp>/<string:untilTimestamp>')
@gzipped
def resourceclaimsForResourceFromUntil(resource_id, fromTimestamp=None, untilTimestamp=None):
    if fromTimestamp and isinstance(fromTimestamp, str):
        fromTimestamp = asDatetime(fromTimestamp)

    if untilTimestamp and isinstance(untilTimestamp, str):
        untilTimestamp = asDatetime(untilTimestamp)

    claims = radb().getResourceClaims(lower_bound=fromTimestamp,
                                      upper_bound=untilTimestamp,
                                      resource_ids=[resource_id],
                                      extended=False,
                                      include_properties=True)
    return jsonify({'resourceclaims': claims})

@app.route('/rest/resourcegroups')
@gzipped
def resourcegroups():
    result = radb().getResourceGroups()
    return jsonify({'resourcegroups': result})

@app.route('/rest/resourcegroupmemberships')
@gzipped
def resourcegroupsmemberships():
    result = radb().getResourceGroupMemberships()
    return jsonify({'resourcegroupmemberships': result})

@app.route('/rest/resourceclaims')
def resourceclaims():
    return resourceclaimsFromUntil(None, None)

@app.route('/rest/resourceclaims/<string:fromTimestamp>')
def resourceclaimsFrom(fromTimestamp=None):
    return resourceclaimsFromUntil(fromTimestamp, None)

@app.route('/rest/resourceclaims/<string:fromTimestamp>/<string:untilTimestamp>')
@gzipped
def resourceclaimsFromUntil(fromTimestamp=None, untilTimestamp=None):
    if fromTimestamp and isinstance(fromTimestamp, str):
        fromTimestamp = asDatetime(fromTimestamp)

    if untilTimestamp and isinstance(untilTimestamp, str):
        untilTimestamp = asDatetime(untilTimestamp)

    claims = radb().getResourceClaims(lower_bound=fromTimestamp, upper_bound=untilTimestamp, include_properties=True)
    return jsonify({'resourceclaims': claims})

@app.route('/rest/resourceusages')
@gzipped
def resourceUsages():
    return resourceUsagesFromUntil(None, None)

@app.route('/rest/resourceusages/<string:fromTimestamp>/<string:untilTimestamp>')
@gzipped
def resourceUsagesFromUntil(fromTimestamp=None, untilTimestamp=None):
    if fromTimestamp and isinstance(fromTimestamp, str):
        fromTimestamp = asDatetime(fromTimestamp)

    if untilTimestamp and isinstance(untilTimestamp, str):
        untilTimestamp = asDatetime(untilTimestamp)

    result = radb().getResourceUsages(lower_bound=fromTimestamp, upper_bound=untilTimestamp)
    return jsonify({'resourceusages': result})

@app.route('/rest/resources/<int:resource_id>/usages', methods=['GET'])
@app.route('/rest/resourceusages/<int:resource_id>', methods=['GET'])
@gzipped
def resourceUsagesForResource(resource_id):
    return resourceUsagesForResourceFromUntil(resource_id, None, None)

@app.route('/rest/resources/<int:resource_id>/usages/<string:fromTimestamp>/<string:untilTimestamp>', methods=['GET'])
@app.route('/rest/resourceusages/<int:resource_id>/<string:fromTimestamp>/<string:untilTimestamp>', methods=['GET'])
@gzipped
def resourceUsagesForResourceFromUntil(resource_id, fromTimestamp=None, untilTimestamp=None):
    if fromTimestamp and isinstance(fromTimestamp, str):
        fromTimestamp = asDatetime(fromTimestamp)

    if untilTimestamp and isinstance(untilTimestamp, str):
        untilTimestamp = asDatetime(untilTimestamp)

    result = radb().getResourceUsages(resource_ids=[resource_id], lower_bound=fromTimestamp, upper_bound=untilTimestamp)
    return jsonify({'resourceusages': result})

@app.route('/rest/tasks/<int:task_id>/resourceusages', methods=['GET'])
@gzipped
def resourceUsagesForTask(task_id):
    result = radb().getResourceUsages(task_ids=[task_id])
    return jsonify({'resourceusages': result})

@app.route('/rest/tasks/<int:task_id>/resourceclaims', methods=['GET'])
@gzipped
def resourceClaimsForTask(task_id):
    result = radb().getResourceClaims(task_ids=[task_id], extended=True, include_properties=True)
    return jsonify({'resourceclaims': result})

@app.route('/rest/tasks')
def getTasks():
    return getTasksFromUntil(None, None)

@app.route('/rest/tasks/<string:fromTimestamp>')
def getTasksFrom(fromTimestamp):
    return getTasksFromUntil(fromTimestamp, None)

@app.route('/rest/tasks/<string:fromTimestamp>/<string:untilTimestamp>')
@gzipped
def getTasksFromUntil(fromTimestamp=None, untilTimestamp=None):
    if fromTimestamp and isinstance(fromTimestamp, str):
        fromTimestamp = asDatetime(fromTimestamp)

    if untilTimestamp and isinstance(untilTimestamp, str):
        untilTimestamp = asDatetime(untilTimestamp)

    tasks = radb().getTasks(fromTimestamp, untilTimestamp)
    updateTaskDetails(tasks)

    return jsonify({'tasks': tasks})

def updateTaskDetails(tasks):
    #update the mom details and the storage details in parallel
    t1 = Thread(target=updateTaskMomDetails, args=(tasks, momqueryrpc))
    t2 = Thread(target=updateTaskStorageDetails, args=(tasks, sqrpc, curpc))
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    #wait for mom details thread to finish
    t1.join()

    #task details (such as name/description) from MoM are done
    #get extra details on reserved resources for reservations (while the storage details still run in t2)
    reservationTasks = [t for t in tasks if t['type'] == 'reservation']
    if reservationTasks:
        reservationClaims = radb().getResourceClaims(task_ids=[t['id'] for t in reservationTasks], extended=True, include_properties=False)
        task2claims = {}
        for claim in reservationClaims:
            if claim['task_id'] not in task2claims:
                task2claims[claim['task_id']] = []
            task2claims[claim['task_id']].append(claim)
        for task in reservationTasks:
            claims = task2claims.get(task['id'], [])
            task['name'] = ', '.join(c['resource_name'] for c in claims)
            task['description'] = 'Reservation on ' + task['name']

    #wait for storage details thread to finish
    t2.join()


@app.route('/rest/tasks/<int:task_id>', methods=['GET'])
@gzipped
def getTask(task_id):
    try:
        task = radb().getTask(task_id)

        if not task:
            abort(404)

        task['name'] = 'Task %d' % task['id']
        updateTaskDetails([task])
        return jsonify({'task': task})
    except Exception as e:
        abort(404)

    return jsonify({'task': None})

@app.route('/rest/tasks/otdb/<int:otdb_id>', methods=['GET'])
@gzipped
def getTaskByOTDBId(otdb_id):
    try:
        task = radb().getTask(otdb_id=otdb_id)

        if not task:
            abort(404)

        task['name'] = 'Task %d' % task['id']
        updateTaskDetails([task])
        return jsonify({'task': task})
    except Exception as e:
        abort(404)

    return jsonify({'task': None})

@app.route('/rest/tasks/mom/<int:mom_id>', methods=['GET'])
@gzipped
def getTaskByMoMId(mom_id):
    try:
        task = radb().getTask(mom_id=mom_id)

        if not task:
            abort(404)

        task['name'] = 'Task %d' % task['id']
        updateTaskDetails([task])
        return jsonify({'task': task})
    except Exception as e:
        abort(404)

    return jsonify({'task': None})

@app.route('/rest/tasks/mom/group/<int:mom_group_id>', methods=['GET'])
@gzipped
def getTasksByMoMGroupId(mom_group_id):
    try:
        mom_ids = momqueryrpc.getTaskIdsInGroup(mom_group_id)[str(mom_group_id)]
        tasks = radb().getTasks(mom_ids=mom_ids)
        updateTaskDetails(tasks)
        return jsonify({'tasks': tasks})
    except Exception as e:
        abort(404)

@app.route('/rest/tasks/mom/parentgroup/<int:mom_parent_group_id>', methods=['GET'])
@gzipped
def getTasksByMoMParentGroupId(mom_parent_group_id):
    try:
        mom_ids = momqueryrpc.getTaskIdsInParentGroup(mom_parent_group_id)[str(mom_parent_group_id)]
        tasks = radb().getTasks(mom_ids=mom_ids)
        updateTaskDetails(tasks)
        return jsonify({'tasks': tasks})
    except Exception as e:
        abort(404)

@app.route('/rest/tasks/<int:task_id>', methods=['PUT'])
def putTask(task_id):
    if 'Content-Type' in request.headers and \
            request.headers['Content-Type'].startswith('application/json'):
        try:
            updatedTask = json_loads(request.data.decode('utf-8'))

            if task_id != int(updatedTask['id']):
                abort(404, 'task_id in url is not equal to id in request.data')

            #check if task is known
            task = radb().getTask(task_id)
            if not task:
                abort(404, "unknown task %s" % str(updatedTask))

            # first handle start- endtimes...
            if 'starttime' in updatedTask or 'endtime' in updatedTask:
                logger.info('starttime or endtime in updatedTask: %s', updatedTask)
                if isProductionEnvironment():
                    abort(403, 'Editing of %s of tasks by users is not yet approved' % (time,))

                #update dict for otdb spec
                spec_update = {}

                for timeprop in ['starttime', 'endtime']:
                    if timeprop in updatedTask:
                        try:
                            updatedTask[timeprop] = asDatetime(updatedTask[timeprop])
                        except ValueError:
                            abort(400, 'timestamp not in iso format: ' + updatedTask[timeprop])
                        otdb_key = 'LOFAR.ObsSW.Observation.' + ('startTime' if timeprop == 'starttime' else 'stopTime')
                        spec_update[otdb_key] = updatedTask[timeprop].strftime('%Y-%m-%d %H:%M:%S')

                #update timestamps in both otdb and radb
                otdbrpc.taskSetSpecification(task['otdb_id'], spec_update)

                # update the task's (and its claims) start/endtime
                # do not update the tasks status directly via the radb. See few lines below. task status is routed via otdb (and then ends up in radb automatically)
                # it might be that editing the start/end time results in a (rabd)task status update (for example to 'conflict' due to conflicting claims)
                # that's ok, since we'll update the status to the requested status later via otdb (see few lines below)
                radb().updateTaskAndResourceClaims(task_id,
                                                   starttime=updatedTask.get('starttime'),
                                                   endtime=updatedTask.get('endtime'))

            # ...then, handle status update which might trigger resource assignment,
            # for which the above updated times are needed
            if 'status' in updatedTask:
                if isProductionEnvironment() and task['type'] == 'observation' and updatedTask['status'] == 'prescheduled':
                    abort(403, 'Scheduling of observations via the webscheduler by users is not (yet) allowed')

                try:
                    #update status in otdb only
                    #the status change will propagate automatically into radb via other services (by design)
                    otdbrpc.taskSetStatus(task['otdb_id'], updatedTask['status'])

                    #we expect the status in otdb/radb to eventually become what we asked for...
                    expected_status = updatedTask['status']

                    #block until radb and mom task status are equal to the expected_statuses (with timeout)
                    start_wait = datetime.utcnow()

                    while True:
                        task = radb().getTask(otdb_id=task['otdb_id'])
                        otdb_status = otdbrpc.taskGetStatus(task['otdb_id'])

                        logger.info('waiting for otdb/radb task status to be in [%s].... otdb:%s radb:%s',
                                    expected_status, otdb_status, task['status'])

                        if (task['status'] == expected_status and otdb_status == expected_status):
                            logger.info('otdb/radb task status now has the expected status %s otdb:%s radb:%s',
                                        expected_status, otdb_status, task['status'])
                            break

                        if datetime.utcnow() - start_wait > timedelta(seconds=10):
                            logger.warning('timeout while waiting for otdb/radb task status to get the expected status %s otdb:%s radb:%s',
                                        expected_status, otdb_status, task['status'])
                            break

                        time.sleep(0.1)
                except RPCException as e:
                    if 'does not exist' in str(e):
                        # task does not exist (anymore) in otdb
                        #so remove it from radb as well (with cascading deletes on specification)
                        logger.warning('task with otdb_id %s does not exist anymore in OTDB. removing task radb_id %s from radb', task['otdb_id'], task['id'])
                        radb().deleteSpecification(task['specification_id'])

            if 'data_pinned' in updatedTask:
                task = radb().getTask(task_id)

                if not task:
                    abort(404, "unknown task %s" % str(updatedTask))

                curpc.setTaskDataPinned(task['otdb_id'], updatedTask['data_pinned'])

            return "", 204
        except Exception as e:
            logger.error(e)
            abort(404, str(e))
    abort(406)

@app.route('/rest/tasks/<int:task_id>/cleanup', methods=['DELETE'])
def cleanupTaskData(task_id):
    try:
        delete_params = {}

        if 'Content-Type' in request.headers and (request.headers['Content-Type'].startswith('application/json') or request.headers['Content-Type'].startswith('text/plain')):
            delete_params = json_loads(request.data.decode('utf-8'))

        task = radb().getTask(task_id)

        if not task:
            abort(404, 'No such task (id=%s)' % task_id)

        logger.info("cleanup task data id=%s otdb_id=%s delete_params=%s", task_id, task['otdb_id'], delete_params)

        result = curpc.removeTaskData(task['otdb_id'],
                                      delete_is=delete_params.get('delete_is', True),
                                      delete_cs=delete_params.get('delete_cs', True),
                                      delete_uv=delete_params.get('delete_uv', True),
                                      delete_im=delete_params.get('delete_im', True),
                                      delete_img=delete_params.get('delete_img', True),
                                      delete_pulp=delete_params.get('delete_pulp', True),
                                      delete_scratch=delete_params.get('delete_scratch', True),
                                      force=delete_params.get('force_delete', False))
        logger.info(result)
        return jsonify(result)
    except Exception as e:
        abort(500)

@app.route('/rest/tasks/<int:task_id>/datapath', methods=['GET'])
@gzipped
def getTaskDataPath(task_id):
    try:
        task = radb().getTask(task_id)

        if not task:
            abort(404, 'No such task (id=%s)' % task_id)

        result = sqrpc.getPathForOTDBId(task['otdb_id'])
    except Exception as e:
        abort(500, str(e))

    if result['found']:
        return jsonify({'datapath': result['path']})
    abort(404, result['message'] if result and 'message' in result else '')

@app.route('/rest/tasks/otdb/<int:otdb_id>/diskusage', methods=['GET'])
@gzipped
def getTaskDiskUsageByOTDBId(otdb_id):
    try:
        result = sqrpc.getDiskUsageForTaskAndSubDirectories(otdb_id=otdb_id, force_update=request.args.get('force')=='true')
    except Exception as e:
        abort(500, str(e))

    if result['found']:
        return jsonify(result)
    abort(404, result['message'] if result and 'message' in result else '')

@app.route('/rest/tasks/<int:task_id>/diskusage', methods=['GET'])
@gzipped
def getTaskDiskUsage(task_id):
    try:
        result = sqrpc.getDiskUsageForTaskAndSubDirectories(radb_id=task_id, force_update=request.args.get('force')=='true')
    except Exception as e:
        abort(500, str(e))

    if result['found']:
        return jsonify(result)
    abort(404, result['message'] if result and 'message' in result else '')

@app.route('/rest/tasks/<int:task_id>/parset', methods=['GET'])
@gzipped
def getParset(task_id):
    try:
        task = radb().getTask(task_id)

        if not task:
            abort(404)

        return getParsetByOTDBId(task['otdb_id'])
    except Exception as e:
        abort(404)
    abort(404)

@app.route('/rest/tasks/otdb/<int:otdb_id>/parset', methods=['GET'])
@gzipped
def getParsetByOTDBId(otdb_id):
    try:
        logger.info('getParsetByOTDBId(%s)', otdb_id)
        parset = otdbrpc.taskGetSpecification(otdb_id=otdb_id)['specification']
        return '\n'.join(['%s=%s' % (k,parset[k]) for k in sorted(parset.keys())]), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        abort(404)
    abort(404)

@app.route('/rest/tasks/<int:task_id>/resourceclaims')
@gzipped
def taskResourceClaims(task_id):
    return jsonify({'taskResourceClaims': radb().getResourceClaims(task_ids=[task_id], include_properties=True)})

@app.route('/rest/tasktypes')
@gzipped
def tasktypes():
    result = radb().getTaskTypes()
    result = sorted(result, key=lambda q: q['id'])
    return jsonify({'tasktypes': result})

@app.route('/rest/taskstatustypes')
@gzipped
def getTaskStatusTypes():
    result = radb().getTaskStatuses()
    result = sorted(result, key=lambda q: q['id'])
    return jsonify({'taskstatustypes': result})

@app.route('/rest/resourcetypes')
@gzipped
def resourcetypes():
    result = radb().getResourceTypes()
    result = sorted(result, key=lambda q: q['id'])
    return jsonify({'resourcetypes': result})

@app.route('/rest/resourceclaimpropertytypes')
@gzipped
def resourceclaimpropertytypes():
    result = radb().getResourceClaimPropertyTypes()
    result = sorted(result, key=lambda q: q['id'])
    return jsonify({'resourceclaimpropertytypes': result})

@app.route('/rest/projects')
@gzipped
def getProjects():
    projects = []
    try:
        projects = momqueryrpc.getProjects()
        projects = [x for x in projects if x['status_id'] in [1, 7]]
        for project in projects:
            project['mom_id'] = project.pop('mom2id')
    except Exception as e:
        logger.error(e)
        projects.append({'name':'<unknown>', 'mom_id':-99, 'description': 'Container project for tasks for which we could not find a MoM project'})

    projects.append({'name':'OTDB Only', 'mom_id':-98, 'description': 'Container project for tasks which exists only in OTDB'})
    projects.append({'name':'Reservations', 'mom_id':-97, 'description': 'Container project for reservation tasks'})
    return jsonify({'momprojects': projects})

@app.route('/rest/projects/<int:project_mom2id>')
@gzipped
def getProject(project_mom2id):
    try:
        projects = momqueryrpc.getProjects()
        project = next(x for x in projects if x['mom2id'] == project_mom2id)
        return jsonify({'momproject': project})
    except StopIteration as e:
        logger.error(e)
        abort(404, "No project with mom2id %s" % project_mom2id)
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/projects/<int:project_mom2id>/tasks')
@gzipped
def getProjectTasks(project_mom2id):
    return getProjectTasksFromUntil(project_mom2id, None, None)

@app.route('/rest/projects/<int:project_mom2id>/tasks/<string:fromTimestamp>/<string:untilTimestamp>')
@gzipped
def getProjectTasksFromUntil(project_mom2id, fromTimestamp=None, untilTimestamp=None):
    try:
        if fromTimestamp and isinstance(fromTimestamp, str):
            fromTimestamp = asDatetime(fromTimestamp)

        if untilTimestamp and isinstance(untilTimestamp, str):
            untilTimestamp = asDatetime(untilTimestamp)

        task_mom2ids = momqueryrpc.getProjectTaskIds(project_mom2id)['task_mom2ids']

        tasks = radb().getTasks(mom_ids=task_mom2ids, lower_bound=fromTimestamp, upper_bound=untilTimestamp)
        updateTaskDetails(tasks)
        return jsonify({'tasks': tasks})
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/projects/<int:project_mom2id>/taskstimewindow')
@gzipped
def getProjectTasksTimeWindow(project_mom2id):
    try:
        task_mom2ids = momqueryrpc.getProjectTaskIds(project_mom2id)['task_mom2ids']

        timewindow = radb().getTasksTimeWindow(mom_ids=task_mom2ids)

        return jsonify(timewindow)
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/projects/<int:project_mom2id>/diskusage')
@gzipped
def getProjectDiskUsageById(project_mom2id):
    try:
        project = momqueryrpc.getProject(project_mom2id=project_mom2id)
        return getProjectDiskUsageByName(project['name'])
    except StopIteration as e:
        logger.error(e)
        abort(404, "No project with mom2id %s" % project_mom2id)
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/projects/<string:project_name>/diskusage')
@gzipped
def getProjectDiskUsageByName(project_name):
    try:
        result = sqrpc.getDiskUsageForProjectDirAndSubDirectories(project_name=project_name, force_update=request.args.get('force')=='true')
        return jsonify(result)
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/projects/diskusage')
@gzipped
def getProjectsDiskUsage():
    try:
        result = sqrpc.getDiskUsageForProjectsDirAndSubDirectories(force_update=request.args.get('force')=='true')
        return jsonify(result)
    except Exception as e:
        logger.error(e)
        abort(404, str(e))

@app.route('/rest/momobjectdetails/<int:mom2id>')
@gzipped
def getMoMObjectDetails(mom2id):
    details = momqueryrpc.getObjectDetails(mom2id)
    details = list(details.values())[0] if details else None
    if details:
        details['project_mom_id'] = details.pop('project_mom2id')
        details['object_mom_id'] = details.pop('object_mom2id')

    return jsonify({'momobjectdetails': details})

@app.route('/rest/updates/<int:sinceChangeNumber>')
@gzipped
def getUpdateEventsSince(sinceChangeNumber):
    changesSince = changeshandler.getChangesSince(sinceChangeNumber)
    return jsonify({'changes': changesSince})

@app.route('/rest/mostRecentChangeNumber')
@gzipped
def getMostRecentChangeNumber():
    mrcn = changeshandler.getMostRecentChangeNumber()
    return jsonify({'mostRecentChangeNumber': mrcn})

@app.route('/rest/updates')
def getUpdateEvents():
    return getUpdateEventsSince(-1)

@app.route('/rest/logEvents')
@gzipped
def getMostRecentLogEvents():
    return getLogEventsSince(datetime.utcnow() - timedelta(hours=6))

@app.route('/rest/logEvents/<string:fromTimestamp>')
@gzipped
def getLogEventsSince(fromTimestamp=None):
    if not fromTimestamp:
        fromTimestamp = datetime.utcnow() - timedelta(hours=6)
    eventsSince = changeshandler.getEventsSince(fromTimestamp)
    return jsonify({'logEvents': eventsSince})

@app.route('/rest/lofarTime')
@gzipped
def getLofarTime():
    return jsonify({'lofarTime': asIsoFormat(datetime.utcnow())})


#ugly method to generate html tables for all tasks
@app.route('/tasks.html')
@gzipped
def getTasksHtml():
    tasks = radb().getTasks()
    if not tasks:
        abort(404)

    updateTaskDetails(tasks)

    html = '<!DOCTYPE html><html><head><title>Tasks</title><style>table, th, td {border: 1px solid black; border-collapse: collapse; padding: 4px;}</style></head><body><table style="width:100%">\n'

    props = sorted(tasks[0].keys())
    html += '<tr>%s</tr>\n' % ''.join('<th>%s</th>' % prop for prop in props)

    for task in tasks:
        html += '<tr>'
        for prop in props:
            if prop in task:
                if prop == 'id':
                    html += '<td><a href="/rest/tasks/%s.html">%s</a></td> ' % (task[prop], task[prop])
                else:
                    html += '<td>%s</td> ' % task[prop]
        html += '</tr>\n'

    html += '</table></body></html>\n'

    return html

#ugly method to generate html tables for the task and it's claims
@app.route('/tasks/<int:task_id>.html', methods=['GET'])
@gzipped
def getTaskHtml(task_id):
    task = radb().getTask(task_id)

    if not task:
        abort(404, 'No such task %s' % task_id)

    task['name'] = 'Task %d' % task['id']
    updateTaskDetails([task])

    html = '<!DOCTYPE html><html><head><title>Tasks</title><style>table, th, td {border: 1px solid black; border-collapse: collapse; padding: 4px;}</style></head><body><table style="">\n'

    html += '<h1>Task %s</h1>' % task_id

    html += '<p><a href="/tasks/%s/log.html">%s log</a></p> ' % (task['id'], task['type'])

    html += '<p><a href="/rest/tasks/%s/parset">view %s parset</a></p> ' % (task['id'], task['type'])

    props = sorted(task.keys())
    html += '<tr><th>key</th><th>value</th></tr>\n'

    for prop in props:
        html += '<tr><td>%s</td>' % prop

        if prop == 'id':
            html += '<td><a href="/tasks/%s.html">%s</a></td> ' % (task[prop], task[prop])
        elif prop == 'predecessor_ids' or prop == 'successor_ids':
            ids = task[prop]
            if ids:
                html += '<td>%s</td> ' % ', '.join('<a href="/tasks/%s.html">%s</a>' % (id, id) for id in ids)
            else:
                html += '<td></td> '
        else:
            html += '<td>%s</td> ' % task[prop]

        html += '</tr>'

    html += '</table>\n<br>'

    claims = radb().getResourceClaims(task_ids=[task_id], extended=True, include_properties=True)

    if claims:
        html += '<h1>Claims</h1>'

        for claim in claims:
            html += '<table>'
            for claim_key,claim_value in list(claim.items()):
                if claim_key == 'properties':
                    html += '<tr><td>properties</td><td><table>'
                    if claim_value:
                        propnames = sorted(claim_value[0].keys())
                        html += '<tr>%s</tr>\n' % ''.join('<th>%s</th>' % propname for propname in propnames)
                        for prop in claim_value:
                            html += '<tr>%s</tr>\n' % ''.join('<td>%s</td>' % prop[propname] for propname in propnames)
                    html += '</table></td></tr>'
                elif claim_key == 'saps':
                    html += '<tr><td>saps</td><td><table>'
                    saps = claim_value
                    if saps:
                        sap_keys = ['sap_nr', 'properties']
                        html += '<tr>%s</tr>\n' % ''.join('<th>%s</th>' % sap_key for sap_key in sap_keys)
                        for sap in saps:
                            html += '<tr>'
                            for sap_key in sap_keys:
                                if sap_key == 'properties':
                                    html += '<td><table>'
                                    sap_props = sap[sap_key]
                                    if sap_props:
                                        propnames = sorted(sap_props[0].keys())
                                        html += '<tr>%s</tr>\n' % ''.join('<th>%s</th>' % propname for propname in propnames)
                                        for prop in sap_props:
                                            html += '<tr>%s</tr>\n' % ''.join('<td>%s</td>' % prop[propname] for propname in propnames)
                                    html += '</table></td>'
                                else:
                                    html += '<td>%s</td>' % (sap[sap_key])
                            html += '</tr>'
                    html += '</table></td></tr>'
                else:
                    html += '<tr><td>%s</td><td>%s</td></tr>' % (claim_key,claim_value)
            html += '</table>'
            html += '<br>'

    html += '</body></html>\n'

    return html

@app.route('/rest/tasks/<int:task_id>/resourceclaims.html', methods=['GET'])
@gzipped
def resourceClaimsForTaskHtml(task_id):
    claims = radb().getResourceClaims(task_ids=[task_id], extended=True, include_properties=True)

    if not claims:
        abort(404, 'No resource claims for task %s' % task_id)

    html = '<!DOCTYPE html><html><head><title>Tasks</title><style>table, th, td {border: 1px solid black; border-collapse: collapse; padding: 4px;}</style></head><body><table style="">\n'

    for claim in claims:
        html += '<tr><td>%s</td>' % claim

    html += '</table></body></html>\n'

    return html

@app.route('/tasks/<int:task_id>/log.html', methods=['GET'])
@gzipped
def getTaskLogHtml(task_id):
    task = radb().getTask(task_id)

    cmd = []
    if task['type'] == 'pipeline':
        cmd = ['ssh', 'lofarsys@head01.cep4.control.lofar', 'cat /data/log/pipeline-%s-*.log' % task['otdb_id']]
    else:
        cmd = ['ssh', 'mcu001.control.lofar', 'cat /opt/lofar/var/log/mcu001\\:ObservationControl\\[0\\]\\{%s\\}.log*' % task['otdb_id']]

    logger.info(' '.join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = communicate_returning_strings(proc)
    if proc.returncode == 0:
        return out, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    else:
        return err, 500, {'Content-Type': 'text/plain; charset=utf-8'}

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description='run the resource assignment editor web service')
    parser.add_option('--webserver_port', dest='webserver_port', type='int', default=7412, help='port number on which to host the webservice, default: %default')
    parser.add_option('-q', '--broker', dest='broker', type='string', default=DEFAULT_BROKER, help='Address of the qpid broker, default: %default')
    parser.add_option('--exchange', dest='exchange', type='string', default=DEFAULT_BUSNAME, help='Name of the bus exchange on the qpid broker, default: %default')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="RADB")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    global _radb_dbcreds
    _radb_dbcreds = dbcredentials.parse_options(options)
    if _radb_dbcreds.database:
        logger.info("Using dbcreds for direct RADB access: %s" % _radb_dbcreds.stringWithHiddenPassword())
    else:
        _radb_dbcreds = None

    global rarpc
    rarpc = RADBRPC.create(exchange=options.exchange, broker=options.broker)
    global otdbrpc
    otdbrpc = OTDBRPC.create(exchange=options.exchange, broker=options.broker)
    global curpc
    curpc = CleanupRPC.create(exchange=options.exchange, broker=options.broker)
    global sqrpc
    sqrpc = StorageQueryRPC.create(exchange=options.exchange, timeout=10, broker=options.broker)
    global momqueryrpc
    momqueryrpc = MoMQueryRPC.create(exchange=options.exchange, timeout=10, broker=options.broker)
    global changeshandler
    changeshandler = ChangesHandler(exchange=options.exchange,
                                    broker=options.broker, momqueryrpc=momqueryrpc, radbrpc=rarpc, sqrpc=sqrpc)

    with changeshandler, rarpc, otdbrpc, curpc, sqrpc, momqueryrpc:
        '''Start the webserver'''
        app.run(debug=options.verbose, threaded=True, host='0.0.0.0', port=options.webserver_port)

if __name__ == '__main__':
    main()
