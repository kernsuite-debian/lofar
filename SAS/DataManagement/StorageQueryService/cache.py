#!/usr/bin/env python3
# $Id$

'''
TODO: add doc
'''
import logging
import datetime
from time import sleep
from threading import Thread, RLock, Event, current_thread
import os.path
import shutil
from functools import cmp_to_key
from concurrent import futures

from lofar.messaging import EventMessage, ToBus, DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.common.util import humanreadablesize
from lofar.common.datetimeutils import format_timedelta
from lofar.sas.datamanagement.storagequery.diskusage import getDiskUsageForPath as du_getDiskUsageForPath
from lofar.sas.datamanagement.storagequery.diskusage import getOTDBIdFromPath
from lofar.sas.datamanagement.storagequery.diskusage import DiskUsage
from lofar.sas.datamanagement.common.datamanagementbuslistener import DataManagementBusListener, DataManagementEventMessageHandler
from lofar.sas.otdb.OTDBBusListener import OTDBBusListener, OTDBEventMessageHandler
from lofar.common.util import waitForInterrupt
from lofar.sas.datamanagement.common.config import CEP4_DATA_MOUNTPOINT
from lofar.sas.datamanagement.common.config import DEFAULT_DM_NOTIFICATION_PREFIX

logger = logging.getLogger(__name__)

MAX_CACHE_ENTRY_AGE = datetime.timedelta(hours=3*24)


class _CacheManagerOTDBEventMessageHandler(OTDBEventMessageHandler):
    def __init__(self, cache_manager: 'CacheManager'):
        self.cache_manager = cache_manager

    def onObservationAborted(self, treeId, modificationTime):
        self.cache_manager.onObservationAborted(treeId, modificationTime)

    def onObservationFinished(self, treeId, modificationTime):
        self.cache_manager.onObservationFinished(treeId, modificationTime)


class _CacheManagerDataManagementEventMessageHandler(DataManagementEventMessageHandler):
    def __init__(self, cache_manager: 'CacheManager'):
        self.cache_manager = cache_manager

    def onTaskDeleted(self, otdb_id, deleted, paths, message=''):
        self.cache_manager.onTaskDeleted(otdb_id, deleted, paths, message)


class CacheManager:
    def __init__(self,
                 cache_path='.du_cache.py',
                 mountpoint=CEP4_DATA_MOUNTPOINT,
                 exchange=DEFAULT_BUSNAME,
                 broker=DEFAULT_BROKER):

        self._cache_path = cache_path

        self.otdb_listener = OTDBBusListener(_CacheManagerOTDBEventMessageHandler,
                                             handler_kwargs={'cache_manager': self},
                                             exchange=exchange,
                                             broker=broker,
                                             num_threads=1)

        self.dm_listener = DataManagementBusListener(_CacheManagerDataManagementEventMessageHandler,
                                                     handler_kwargs={'cache_manager': self},
                                                     exchange=exchange,
                                                     broker=broker,
                                                     num_threads=1)

        self.event_bus = ToBus(exchange=exchange, broker=broker)

        self._updateCacheThread = None
        self._running = False

        self._cacheLock = RLock()

        self._cache = {'path_du_results': {}, 'otdb_id2path': {} }
        self._last_cache_write_timestamp = datetime.datetime(1970, 1, 1)
        self._readCacheFromDisk()

        # dict to hold threading Events per path to prevent expensive multiple du calls for each path
        self._du_threading_events = {}
        self._du_threading_events_lock = RLock()

        self.disk_usage = DiskUsage(mountpoint=mountpoint,
                                    exchange=exchange,
                                    broker=broker)

    def _sendDiskUsageChangedNotification(self, path, disk_usage, otdb_id=None):
        try:
            msg = EventMessage(subject='%s.DiskUsageChanged' % DEFAULT_DM_NOTIFICATION_PREFIX,
                               content={ 'path': path,
                                         'disk_usage': disk_usage,
                                         'disk_usage_readable': humanreadablesize(disk_usage),
                                         'otdb_id': otdb_id })
            logger.info('Sending notification with subject %s to %s: %s', msg.subject, self.event_bus.exchange, msg.content)
            self.event_bus.send(msg)
        except Exception as e:
            logger.error(str(e))

    def _readCacheFromDisk(self):
        # maybe this cache on disk is slow, if so, revert to proper db solution
        try:
            if os.path.exists(self._cache_path):
                with open(self._cache_path, 'r') as file:
                    cache_from_disk = eval(file.read().strip()) #slow!
                    with self._cacheLock:
                        self._cache = cache_from_disk
                        if not isinstance(self._cache, dict):
                            self._cache = {'path_du_results': {}, 'otdb_id2path': {} }
                        if 'path_du_results' not in self._cache:
                            self._cache['path_du_results'] = {}
                        if 'otdb_id2path' not in self._cache:
                            self._cache['otdb_id2path'] = {}
        except Exception as e:
            logger.error("Error while reading in du cache: %s", e)
            with self._cacheLock:
                self._cache = {'path_du_results': {}, 'otdb_id2path': {} }


    def _writeCacheToDisk(self):
        try:
            # only persist (a subset of) the cache to disk every once in a while.
            if datetime.datetime.utcnow() - self._last_cache_write_timestamp > datetime.timedelta(minutes=5):
                cache_str = ''
                with self._cacheLock:
                    # Take a subset of the entire cache
                    # only the path_du_results for paths at project level (like /data/projects, /data/projects/LC9_001)
                    # Do not store path_du_results for deeper levels on disk, because that makes the disk read/write too slow,
                    # and the deeper levels can be obtained via rhb-du calls quite fast anyway.
                    # Furthermore, once a deeper level du results is stored in the memory cache, then it is also available for fast lookup.
                    # We just don't store these deep levels on disk.
                    sub_cache = { path:du_result for path,du_result in list(self._cache['path_du_results'].items())
                                  if self.getDepthToProjectsDir(path) <= 1 and du_result.get('found') }
                    cache_str = str(sub_cache)

                tmp_path = '/tmp/tmp_storagequery_cache.py'
                with open(tmp_path, 'w') as file:
                    file.write(cache_str)
                dir_path = os.path.dirname(self._cache_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                shutil.move(tmp_path, self._cache_path)
                self._last_cache_write_timestamp = datetime.datetime.utcnow()
        except Exception as e:
            logger.error("Error while writing du cache: %s", e)

    def _updateCache(self, du_result, send_notification=True):
        if not 'path' in du_result:
            return

        path = du_result['path']
        otdb_id = du_result.get('otdb_id')

        with self._cacheLock:
            path_cache = self._cache['path_du_results']
            otdb_id2path_cache = self._cache['otdb_id2path']

            if otdb_id is None:
                # try to look up the otdb in the path cache
                if path in path_cache:
                    otdb_id = du_result.get('otdb_id')

                # if still None, try to get the id from the path
                if otdb_id is None:
                    otdb_id = getOTDBIdFromPath(path)

            if not path in path_cache or path_cache[path]['disk_usage'] != du_result['disk_usage']:
                # update the cache entry, even when no du result found,
                # cause that will save disk queries next time.
                logger.info('updating cache entry: %s', du_result)
                path_cache[path] = du_result

            if otdb_id != None:
                otdb_id2path_cache[otdb_id] = path

            if not du_result['found']:
                # even when the du for the path is not found,
                # keep a copy in the cache for fast lookup by clients
                # Make sure the size is 0
                du_result['disk_usage'] = 0
                du_result['disk_usage_readable'] = humanreadablesize(0)

            path_cache[path]['cache_timestamp'] = datetime.datetime.utcnow()
            path_cache[path]['needs_update'] = False

        self._writeCacheToDisk()

        if send_notification:
            self._sendDiskUsageChangedNotification(path, du_result['disk_usage'], otdb_id)

    def _invalidateCacheEntryForPath(self, path):
        with self._cacheLock:
            path_cache = self._cache['path_du_results']
            if path in path_cache:
                path_cache[path]['needs_update'] = True

    def getOtdbIdsFoundOnDisk(self):
        with self._cacheLock:
            otdb_id2path_cache = self._cache['otdb_id2path']
            return sorted(list(otdb_id2path_cache.keys()))

    def getDiskUsagesForAllOtdbIds(self, force_update=False):
        otdb_ids = self.getOtdbIdsFoundOnDisk()

        result = {}
        for otdb_id in otdb_ids:
            result[otdb_id] = self.getDiskUsageForOTDBId(otdb_id, force_update=force_update)

        return result

    def getDepthToProjectsDir(self, path):
        return len(path.replace(self.disk_usage.path_resolver.projects_path, '').strip('/').split('/'))

    def _scanProjectsTree(self):
        try:
            def addSubDirectoriesToCache(directory):
                if not self._running:
                    return

                depth = self.getDepthToProjectsDir(directory)
                MAX_SCAN_DEPTH=2
                #depth=0 : projects
                #depth=1 : projects/<project>
                #depth=2 : projects/<project>/<obs>
                #depth=3 : projects/<project>/<obs>/<sub_dir>
                if depth > MAX_SCAN_DEPTH:
                    return

                if depth < MAX_SCAN_DEPTH:
                    logger.info('tree scan: scanning \'%s\'', directory)
                    sd_result = self.disk_usage.path_resolver.getSubDirectories(directory)

                    if sd_result['found']:
                        subdir_paths = [os.path.join(directory,sd) for sd in sd_result['sub_directories']]

                        for subdir_path in subdir_paths:
                            # recurse
                            addSubDirectoriesToCache(subdir_path)

                with self._cacheLock:
                    path_cache = self._cache['path_du_results']
                    add_empty_du_result_to_cache = not directory in path_cache

                if add_empty_du_result_to_cache:
                    logger.info('tree scan: adding \'%s\' with empty disk_usage to cache which will be du\'ed later', directory)
                    empty_du_result = {'found': True, 'disk_usage': None, 'path': directory, 'name': directory.split('/')[-1]}
                    self._updateCache(empty_du_result, send_notification=False)

                with self._cacheLock:
                    path_cache = self._cache['path_du_results']
                    if directory in path_cache:
                        # mark cache entry for directory to be updated
                        path_cache[directory]['needs_update'] = True

            addSubDirectoriesToCache(self.disk_usage.path_resolver.projects_path)
            logger.info('tree scan complete')

        except Exception as e:
            logger.exception(str(e))

    def _updateOldEntriesInCache(self):
        logger.info('starting updating old cache entries')
        while self._running:
            try:
                now = datetime.datetime.utcnow()
                with self._cacheLock:
                    path_cache = self._cache['path_du_results']
                    old_entries = [cache_entry for cache_entry in list(path_cache.values())
                                   if now - cache_entry['cache_timestamp'] > MAX_CACHE_ENTRY_AGE]
                    needs_update_entries = [cache_entry for cache_entry in list(path_cache.values())
                                            if cache_entry.get('needs_update', False)]

                updateable_entries = old_entries + needs_update_entries

                logger.info('%s old cache entries need to be updated, #age:%s #needs_update:%s',
                            len(updateable_entries),
                            len(old_entries),
                            len(needs_update_entries))

                if updateable_entries:
                    # sort them oldest to newest, 'needs_update' paths first
                    def compareFunc(entry1, entry2):
                        if entry1.get('needs_update') and not entry2.get('needs_update'):
                            return -1
                        if not entry1.get('needs_update') and entry2.get('needs_update'):
                            return 1

                        #depth1 = self.getDepthToProjectsDir(entry1['path'])
                        #depth2 = self.getDepthToProjectsDir(entry2['path'])

                        #if depth1 != depth2:
                            ## lower level dirs are sorted in front of higher level dirs
                            #return depth1 - depth2

                        if entry1['cache_timestamp'] < entry2['cache_timestamp']:
                            return -1
                        if entry1['cache_timestamp'] > entry2['cache_timestamp']:
                            return 1
                        return 0

                    updateable_entries = sorted(updateable_entries, key=cmp_to_key(compareFunc))

                    cacheUpdateStart = datetime.datetime.utcnow()

                    for i, cache_entry in enumerate(updateable_entries):
                        try:
                            # it might be that the cache_entry was already updated via another way
                            # so only update it if still to old or needs_update
                            now = datetime.datetime.utcnow()
                            if now - cache_entry['cache_timestamp'] > MAX_CACHE_ENTRY_AGE or cache_entry.get('needs_update', False):
                                path = cache_entry.get('path')
                                if path:
                                    logger.info('_updateOldEntriesInCache: examining entry %s/%s. timestamp:%s age:%s needs_update:%s path: \'%s\'',
                                                i,
                                                len(updateable_entries),
                                                cache_entry['cache_timestamp'],
                                                format_timedelta(now - cache_entry['cache_timestamp']),
                                                cache_entry.get('needs_update', False),
                                                path)

                                    #du a full update from disk, which might be (really) slow.
                                    result = du_getDiskUsageForPath(path)
                                    logger.debug('trying to update old entry in cache: %s', result)
                                    self._updateCache(result)
                        except Exception as e:
                            logger.error(str(e))

                        if not self._running:
                            logger.info('exiting _updateCacheThread')
                            return

                        if datetime.datetime.utcnow() - cacheUpdateStart > datetime.timedelta(minutes=10):
                            # break out of cache update loop if full update takes more than 1min
                            # next loop we'll start with the oldest cache entries again
                            logger.info('skipping remaining %s old cache entries updates, they will be updated next time', len(updateable_entries)-i)
                            break

                #update the CEP4 capacities in the RADB once in a while...
                self._updateCEP4CapacitiesInRADB()

                #sleep for a while, (or stop if requested)
                for i in range(60):
                    sleep(1)
                    if not self._running:
                        logger.info('exiting _updateCacheThread')
                        return

            except Exception as e:
                logger.exception(str(e))

    def _updateCEP4CapacitiesInRADB(self):
        try:
            df_result = self.disk_usage.getDiskFreeSpace()
            if df_result['found']:
                #get the total used space, and update the resource availability in the radb
                radbrpc = self.disk_usage.path_resolver.radbrpc
                storage_resources = radbrpc.getResources(resource_types='storage', include_availability=True)
                cep4_storage_resource = next(x for x in storage_resources if 'CEP4' in x['name'])

                total_capacity = df_result.get('disk_size')
                used_capacity = df_result.get('disk_usage')
                available_capacity = df_result.get('disk_free')

                logger.info('updating capacities for resource \'%s\' (id=%s) in the RADB: total=%s, used=%s, available=%s',
                            cep4_storage_resource['name'],
                            cep4_storage_resource['id'],
                            humanreadablesize(total_capacity),
                            humanreadablesize(used_capacity),
                            humanreadablesize(available_capacity))

                radbrpc.updateResourceAvailability(cep4_storage_resource['id'],
                                                   available_capacity=available_capacity,
                                                   total_capacity=total_capacity)
        except Exception as e:
            logger.error('_updateCEP4CapacitiesInRADB: %s', e)

    def open(self):
        logger.info("opening storagequeryservice cache...")
        self._running = True

        self.disk_usage.open()
        self.event_bus.open()

        self._scanProjectsTree()

        self._updateCacheThread = Thread(target=self._updateOldEntriesInCache)
        self._updateCacheThread.daemon = True
        self._updateCacheThread.start()

        self.otdb_listener.start_listening()
        self.dm_listener.start_listening()
        logger.info("opened storagequeryservice cache")

    def close(self):
        logger.info("closing storagequeryservice cache...")
        self._running = False

        self.otdb_listener.stop_listening()
        self.dm_listener.stop_listening()
        self._updateCacheThread.join()

        self.event_bus.close()
        self.disk_usage.close()
        logger.info("closed storagequeryservice cache")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def onObservationFinished(self, otdb_id, modificationTime):
        self._onDiskActivityForOTDBId(otdb_id)

    def onObservationAborted(self, otdb_id, modificationTime):
        self._onDiskActivityForOTDBId(otdb_id)

    def onTaskDeleted(self, otdb_id, deleted, paths, message=''):
        self._onDiskActivityForOTDBId(otdb_id)

        with self._cacheLock:
            if deleted and otdb_id != None and otdb_id in self._cache['otdb_id2path']:
                del self._cache['otdb_id2path'][otdb_id]

    def _onDiskActivityForOTDBId(self, otdb_id):
        result = self.disk_usage.getDiskUsageForOTDBId(otdb_id)
        self._updateCache(result)

        task_path = result.get('path')
        projects_path = self.disk_usage.path_resolver.projects_path

        # update all paths up the tree up to the projects_path
        # update the resource availability in the radb as well
        path = task_path
        while path:
            parent_path = '/'.join(path.split('/')[:-1])

            if projects_path.startswith(parent_path) and len(parent_path) < len(projects_path):
                break

            logger.info('invalidating cache entry for %s because disk usage for task %s in %s changed', parent_path, otdb_id, task_path)

            self._invalidateCacheEntryForPath(parent_path)

            path = parent_path

    def getDiskUsageForOTDBId(self, otdb_id, include_scratch_paths=True, force_update=False):
        return self.getDiskUsageForTask(otdb_id=otdb_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForMoMId(self, mom_id, include_scratch_paths=True, force_update=False):
        return self.getDiskUsageForTask(mom_id=mom_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForRADBId(self, radb_id, include_scratch_paths=True, force_update=False):
        return self.getDiskUsageForTask(radb_id=radb_id, include_scratch_paths=include_scratch_paths, force_update=force_update)

    def getDiskUsageForTask(self, radb_id=None, mom_id=None, otdb_id=None, include_scratch_paths=True, force_update=False):
        logger.info("cache.getDiskUsageForTask(radb_id=%s, mom_id=%s, otdb_id=%s, include_scratch_paths=%s, force_update=%s)",
                    radb_id, mom_id, otdb_id, include_scratch_paths, force_update)

        if otdb_id != None and not include_scratch_paths:
            with self._cacheLock:
                path = self._cache['otdb_id2path'].get(otdb_id)

            if path:
                logger.info('Using path from cache for otdb_id %s %s', otdb_id, path)
                return self.getDiskUsageForPath(path, force_update=force_update)

        logger.info("cache.getDiskUsageForTask could not find path in cache, determining path...")

        path_result = self.disk_usage.path_resolver.getPathForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, include_scratch_paths=include_scratch_paths)

        if path_result['found']:
            task_path = path_result['path']
            scratch_paths = path_result.get('scratch_paths', [])

            # get all du's in parallel over all paths
            paths = [task_path] + scratch_paths
            paths_du_result = self.getDiskUsageForPaths(paths, force_update=force_update)

            # split into project and subdir
            path_du_result = paths_du_result.pop(task_path)
            scratch_du_result = paths_du_result

            task_du_result = dict(path_du_result)

            # yield id's for if available, or None
            for id in ['radb_id', 'otdb_id', 'mom_id']:
                task_du_result[id] = path_result.get(id)

            if scratch_du_result:
                task_du_result['scratch_paths'] = scratch_du_result

            return task_du_result

        # still no path(s) found for otdb_id, now try from cache and ignore possible scratch paths
        if otdb_id != None:
            with self._cacheLock:
                path = self._cache['otdb_id2path'].get(otdb_id)

            if path:
                logger.info('Using path from cache for otdb_id %s %s (ignoring possible scratch/share paths)', otdb_id, path)
                return self.getDiskUsageForPath(path, force_update=force_update)

        return {'found': False, 'path': path_result['path']}

    def getDiskUsageForTasks(self, radb_ids=None, mom_ids=None, otdb_ids=None, include_scratch_paths=True, force_update=False):
        logger.info("cache.getDiskUsageForTasks(radb_ids=%s, mom_ids=%s, otdb_ids=%s)" % (radb_ids, mom_ids, otdb_ids))
        tasks_result = {'radb_ids': {}, 'mom_ids': {}, 'otdb_ids': {}}
        if radb_ids is None:
            radb_ids = []
        if mom_ids is None:
            mom_ids = []
        if otdb_ids is None:
            otdb_ids = []

        with futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:

            # helper function to expand parallel p_kwarg dict into kwargs
            def parallel_getDiskUsageForTask(p_kwarg):
                return self.getDiskUsageForTask(**p_kwarg)

            parallel_kwargs  = [{'radb_id':radb_id, 'include_scratch_paths': include_scratch_paths, 'force_update':force_update} for radb_id in radb_ids]
            parallel_kwargs += [{'mom_id':mom_id, 'include_scratch_paths': include_scratch_paths, 'force_update':force_update} for mom_id in mom_ids]
            parallel_kwargs += [{'otdb_id':otdb_id, 'include_scratch_paths': include_scratch_paths, 'force_update':force_update} for otdb_id in otdb_ids]
            results = list(executor.map(parallel_getDiskUsageForTask, parallel_kwargs))

            # collect results in a dict grouped by id_type
            for result in results:
                if result.get('radb_id') in radb_ids:
                    tasks_result['radb_ids'][result['radb_id']] = result
                if result.get('mom_id') in mom_ids:
                    tasks_result['mom_ids'][result['mom_id']] = result
                if result.get('otdb_id') in otdb_ids:
                    tasks_result['otdb_ids'][result['otdb_id']] = result

        logger.info("cache.getDiskUsageForTasks(radb_ids=%s, mom_ids=%s, otdb_ids=%s) returning: %s" % (radb_ids, mom_ids, otdb_ids, tasks_result))

        return tasks_result

    def getDiskUsageForPaths(self, paths, force_update=False):
        with futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:

            # helper function to expand parallel p_arg tuple into list of args
            def parallel_getDiskUsageForPath(p_arg):
                return self.getDiskUsageForPath(*p_arg)

            parallel_args = [(path, force_update) for path in paths]
            results = list(executor.map(parallel_getDiskUsageForPath, parallel_args))

            return { result['path']:result for result in results }

    def getDiskUsageForPath(self, path, force_update=False):
        logger.info("cache.getDiskUsageForPath('%s', force_update=%s)", path, force_update)
        needs_cache_update = False
        if not force_update:
            with self._cacheLock:
                needs_cache_update |= path not in self._cache['path_du_results']

        if needs_cache_update or force_update:
            logger.info("cache update needed for %s", path)

            # check if some other thread is already doing a du call for this path...
            with self._du_threading_events_lock:
                path_threading_event = self._du_threading_events.get(path)
                need_to_do_du_call = path_threading_event is None

                if need_to_do_du_call:
                    # no other thread is currently du'ing/updating this path
                    # so create a threading Event and store it in the dict,
                    # so other threads can wait for this event.
                    logger.info("updating the cache for %s current_thread=%s", path, current_thread().name)
                    path_threading_event = Event()
                    self._du_threading_events[path] = path_threading_event

            if need_to_do_du_call:
                # no other thread is currently du'ing/updating this path
                # so we need to do it here.
                result = du_getDiskUsageForPath(path)
                self._updateCache(result)

                # signal threads waiting for this same path du call
                # and do bookkeeping
                with self._du_threading_events_lock:
                    logger.info("signaling other threads that the cache was updated for %s current_thread=%s", path, current_thread().name)
                    path_threading_event.set()
                    del self._du_threading_events[path]
            else:
                logger.info("waiting for du call on other thread that will update the cache for %s current_thread=%s", path, current_thread().name)
                path_threading_event.wait()
                logger.info("another thread just updated the cache for %s current_thread=%s", path, current_thread().name)

        with self._cacheLock:
            if path in self._cache['path_du_results']:
                result = self._cache['path_du_results'][path]
            else:
                result = { 'found': False, 'path':path, 'message': 'unknown error' }
                if not self.disk_usage.path_resolver.pathExists(path):
                    result['message'] = 'No such path: %s' % path

        result['disk_usage_readable'] = humanreadablesize(result.get('disk_usage', 0))
        logger.info('cache.getDiskUsageForPath(\'%s\') result: %s', path, result)
        return result

    def getDiskUsageForTaskAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, force_update=False):
        logger.info("cache.getDiskUsageForTaskAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s)" % (radb_id, mom_id, otdb_id))
        task_du_result = self.getDiskUsageForTask(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, force_update=force_update)
        if task_du_result['found']:
            task_sd_result = self.disk_usage.path_resolver.getSubDirectories(task_du_result['path'])

            if task_sd_result['found']:
                subdir_paths = [os.path.join(task_du_result['path'],sd) for sd in task_sd_result['sub_directories']]
                subdirs_du_result = self.getDiskUsageForPaths(subdir_paths, force_update=force_update)

                result = {'found':True, 'task_directory': task_du_result, 'sub_directories': subdirs_du_result }
                logger.info("result for cache.getDiskUsageForTaskAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s): %s", radb_id, mom_id, otdb_id, result)
                return result

        logger.warning("result for cache.getDiskUsageForTaskAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s): %s", radb_id, mom_id, otdb_id, task_du_result)
        return task_du_result

    def getDiskUsageForProjectDirAndSubDirectories(self, radb_id=None, mom_id=None, otdb_id=None, project_name=None, force_update=False):
        logger.info("cache.getDiskUsageForProjectDirAndSubDirectories(radb_id=%s, mom_id=%s, otdb_id=%s)" % (radb_id, mom_id, otdb_id))
        path_result = self.disk_usage.path_resolver.getProjectDirAndSubDirectories(radb_id=radb_id, mom_id=mom_id, otdb_id=otdb_id, project_name=project_name)
        if path_result['found']:
            projectdir_path = path_result['path']
            subdir_paths = [os.path.join(path_result['path'], sd) for sd in path_result['sub_directories']]

            # get all du's in parallel over all paths
            paths = [projectdir_path] + subdir_paths
            paths_du_result = self.getDiskUsageForPaths(paths, force_update=force_update)

            # split into project and subdir
            projectdir_du_result = paths_du_result.pop(projectdir_path)
            subdirs_du_result = paths_du_result

            # create total result dict
            result = {'found':True, 'projectdir': projectdir_du_result, 'sub_directories': subdirs_du_result }
            logger.info('cache.getDiskUsageForProjectDirAndSubDirectories result: %s' % result)
            return result

        return path_result

    def getDiskUsageForProjectsDirAndSubDirectories(self, force_update=False):
        logger.info("cache.getDiskUsageForProjectsDirAndSubDirectories")
        projects_path = self.disk_usage.path_resolver.projects_path
        project_subdirs_result = self.disk_usage.path_resolver.getSubDirectories(projects_path)
        subdir_paths = [os.path.join(projects_path,sd) for sd in project_subdirs_result['sub_directories']] if project_subdirs_result['found'] else []

        # get all du's in parallel over all paths
        paths = [projects_path] + subdir_paths
        paths_du_result = self.getDiskUsageForPaths(paths, force_update=force_update)

        # split into project and subdir
        projectsdir_du_result = paths_du_result.pop(projects_path)
        subdirs_du_result = paths_du_result

        # create total result dict
        result = {'found':True, 'projectdir': projectsdir_du_result, 'sub_directories': subdirs_du_result }

        logger.info('cache.getDiskUsageForProjectsDirAndSubDirectories result: %s' % result)
        return result

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s %(message)s', level=logging.INFO)

    with CacheManager() as cm:
        waitForInterrupt()
