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

# TODO: add comment to methods
# TODO: reuse connection in methods (take care of exceptions closing the connection)
# TODO: use generators and yield for faster and more memory efficient processing of results.

import datetime
import logging
from lofar.common import dbcredentials
from lofar.common.postgres import PostgresDatabaseConnection
from lofar.common.postgres import FETCH_NONE,FETCH_ONE,FETCH_ALL

logger = logging.getLogger(__name__)

class EntryNotFoundException(Exception):
    pass


class LTAStorageDb(PostgresDatabaseConnection):
    """LTAStorageDb is a python API to the ltaso postgres database."""

    def __init__(self, dbcreds=None):
        """Create an instance of a LTAStorageDb
        :param dbcredentials.DBCredentials dbcreds: the credential for logging in into the db
        """
        super(LTAStorageDb, self).__init__(dbcreds=dbcreds)

    def insertSite(self, siteName, srmurl):
        """insert a site into the database
        :param string siteName: the name of the site
        :param string srmurls: the srm url to that site
        :return int: the new id of the inserted site
        """
        site_id = self.executeQuery('insert into lta.site (name, url) values (%s, %s) returning id;', (siteName, srmurl), fetch=FETCH_ONE)['id']
        self.commit()
        return site_id

    def insertSiteIfNotExists(self, siteName, srmurl):
        """insert a site into the database and return the id.
        If the site already exists, then the id of that site is just returned.
        :param string siteName: the name of the site
        :param string srmurls: the srm url to that site
        :return int: the new id of the inserted site
        """
        site = self.siteByName(siteName)

        if site:
            return site['id']

        return self.insertSite(siteName, srmurl)

    def insertRootDirectory(self, siteName, rootDirectory):
        """
        Insert a root directory for a site. Each site has at least one root directory (with no parent).
        For all non-root directories, use insertSubDirectory.
        Beware: Uniqueness of the root dir for a site is not enforced.
        :param string siteName: the name of the site (should already be in the database)
        :param string rootDirectory: the full path of the directory
        :return integer: the new id of the inserted root directory
        """
        site = self.siteByName(siteName)

        if not site:
            raise EntryNotFoundException()

        site_id = site['id']

        dir_id = self.executeQuery('insert into lta.directory (name) values (%s) returning id;', [rootDirectory], fetch=FETCH_ONE)['id']

        self.executeQuery('insert into lta.site_root_dir (site_id, root_dir_id) values (%s, %s);', (site_id, dir_id))
        self.commit()
        return dir_id

    def insertSubDirectory(self, sub_directory_path, parent_dir_id):
        """
        Insert a sub directory which is a child of the directory with parent_dir_id
        :param int parent_dir_id: the id of this subdirectories parent
        :param string sub_directory_path: the full path of the subdirectory
        :return integer: the new id of the inserted subdirectory
        """
        result = self.executeQuery('insert into lta.directory (name, parent_dir_id) values (%s, %s) returning id;', (sub_directory_path, parent_dir_id), fetch=FETCH_ONE)

        if result and 'id' in result:
            self.commit()
            return result['id']

        return None

    def insertSubDirectories(self, subDirectoryPaths, parentDirId, directoryLastVisitTime = None):
        """
        Insert multiple sub directories which are all a child of the directory with parent_dir_id
        :param int parent_dir_id: the id of this subdirectories parent
        :param [string] subDirectoryPaths: a list of full paths of the subdirectories
        :return [integer]: a list of new ids of the inserted subdirectories
        """
        with self._connection.cursor() as cursor:
            insert_values = ','.join(cursor.mogrify('(%s, %s)', (name, parentDirId)).decode('utf-8') for name in subDirectoryPaths)

        query = '''insert into lta.directory (name, parent_dir_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        subDirIds = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in subDirIds if x < 0]:
            logger.error("One or more subDirectoryPaths could not be inserted. Rolling back.")
            self.rollback()
            return None

        if directoryLastVisitTime:
            with self._connection.cursor() as cursor:
                insert_values = ','.join(cursor.mogrify('(%s, %s)', (directoryLastVisitTime, id)).decode('utf-8') for id in subDirIds)

            query = '''insert into scraper.last_directory_visit (visit_date, dir_id)
            VALUES {values}
            RETURNING id;'''.format(values=insert_values)

            ldvIds = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

            if [x for x in ldvIds if x < 0]:
                logger.error("One or more scraper.last_directory_visit's could not be inserted. Rolling back.")
                self.rollback()
                return None

        self.commit()
        return subDirIds

    def insert_missing_directory_tree_if_needed(self, dir_path, site_id):
        """Insert all directories in the dir_path tree which are not in the database yet.
        example: root_dir         = '/path/to/root'
                 known_subdir_1   = '/path/to/root/sub1'
                 known_subdir_2   = '/path/to/root/sub1/sub2'
                 (input) dir_path = '/path/to/root/sub1/sub2/sub3/sub4'
                 would insert '/path/to/root/sub1/sub2/sub3 under known_subdir_2 and
                              '/path/to/root/sub1/sub2/sub3/sub4' under the new sub3 dir.
        :param str dir_path: a full path to a (sub)directory
        :param int site_id: the id of the site for which you want to insert the dir tree.
        :return: a dict of the inserted directories with their new dir id's.
        """
        # for this site (which might have multiple root dirs), find the root_dir under which this dir_path belongs
        parent_root_dir = self.get_root_dir_for_dir_path(dir_path, site_id)

        if parent_root_dir is None:
            raise LookupError("Could not find parent root dir for site_id=%d for dir_path=%s" % (site_id, dir_path))

        # find the lowest known dir in the database
        # and get the list of missing subdirs for dir_path, which are not in the database ye
        missing_child_dirs, lowest_known_db_dir = self._get_lowest_known_directory(dir_path, parent_root_dir)

        # now we should have a known parent dir from the db, and we know which child dirs are missing.
        # append the missing children in reverse order
        # (from just under the known parent, down to the lowest missing subdir).
        result = {}
        missing_childs_parent_dir_id = lowest_known_db_dir['dir_id']
        for missing_child_dir in reversed(missing_child_dirs):
            missing_childs_parent_dir_id = self.insertSubDirectory(missing_child_dir, missing_childs_parent_dir_id)
            result[missing_child_dir] = missing_childs_parent_dir_id

        # return the dict of inserted child dirs with their new dir id's
        return result

    def deleteDirectory(self, dir_id, commit=True):
        """
        delete the directory with id dir_id. Cascacades and also deletes all subdirs, files and stats under this directory.
        :param int dir_id: the id of the directory to be deleted
        :param bool commit: optional, commit directly when True
        """
        self.executeQuery('DELETE FROM lta.directory where id = %s;', (dir_id,), fetch=FETCH_NONE)

        if commit:
            self.commit()


    def insertFileInfo(self, name, size, creation_date, parent_dir_id, commit=True):
        fileinfo_id = self.executeQuery('insert into lta.fileinfo (name, size, creation_date, dir_id) values (%s, %s, %s, %s) returning id;',
                                        (name.split('/')[-1], size, creation_date, parent_dir_id))

        if commit:
            self.commit()
        return fileinfo_id

    def insertFileInfos(self, file_infos):
        with self._connection.cursor() as cursor:
            insert_values = [cursor.mogrify('(%s, %s, %s, %s)', (f[0].split('/')[-1], f[1], f[2], f[3])).decode('utf-8') for f in file_infos]

        insert_values = ','.join([x for x in insert_values])

        query = '''insert into lta.fileinfo (name, size, creation_date, dir_id)
        VALUES {values}
        RETURNING id;'''.format(values=insert_values)

        ids = [x['id'] for x in self.executeQuery(query, fetch=FETCH_ALL)]

        if [x for x in ids if x < 0]:
            logger.error("One or more file_infos could not be inserted. Rolling back.")
            self.rollback()
            return None

        self.commit()
        return ids

    def updateFileInfoSize(self, id, size, commit=True):
        fileinfo_id = self.executeQuery('''update lta.fileinfo set size=%s where id=%s;''', (size, id))

        if commit:
            self.commit()

    def deleteFileInfoFromDirectory(self, file_name, dir_id, commit=True):
        self.executeQuery('DELETE FROM lta.fileinfo where dir_id = %s and name = %s;', (dir_id,file_name), fetch=FETCH_NONE)

        if commit:
            self.commit()

    def updateDirectoryLastVisitTime(self, dir_id, timestamp, commit=True):
        self.executeQuery('''update scraper.last_directory_visit
                             set visit_date=%s
                             where dir_id = %s;''', (timestamp, dir_id), fetch=FETCH_NONE)

        if commit:
            self.commit()

    def directoryLastVisitTime(self, dir_id):
        """
        get the timestamp when the directory was last visited.
        :param int dir_id: the id of the directory
        :return datetime: the timestamp when the directory was last visited.
        """
        result = self.executeQuery('''select visit_date FROM scraper.last_directory_visit
                                      where dir_id = %s;''', (dir_id,), fetch=FETCH_ONE)
        if result is None:
            return None
        return result.get('visit_date')

    def sites(self):
        '''returns list of tuples (id, name, url) of all sites'''
        return self.executeQuery('SELECT id, name, url FROM lta.site;', fetch=FETCH_ALL)

    def site(self, site_id):
        '''returns tuple (id, name, url) for site with id=site_id'''
        return self.executeQuery('SELECT id, name, url FROM lta.site where id = %s;', [site_id], FETCH_ONE)

    def siteByName(self, site_name):
        '''returns tuple (id, name, url) for site with id=site_id'''
        return self.executeQuery('SELECT id, name, url FROM lta.site where name = %s;', [site_name], FETCH_ONE)

    def siteQuota(self, site_id):
        '''returns list of quota tuples (site_id, site_name, quota, valid_until_date)'''
        return self.executeQuery('SELECT * FROM lta.site_quota;', FETCH_All)

    def insertSiteQuota(self, site_id, quota, valid_until_date, commit=True):
        """
        insert the quota for a given site with a date until which this quota is valid.
        :param int site_id: the id of the site for which you want to set the quota.
        :param int quota: the quota in number of bytes.
        :param datetime valid_until_date: the timestamp until which this given quota is valid.
        :param bool commit: do/don't commit immediately.
        :return: the id of the new quota
        """
        id =  self.executeQuery('INSERT INTO lta.site_quota(site_id, quota, valid_until_date) values (%s, %s, %s) RETURNING id;',
                                (site_id, quota, valid_until_date))
        if commit:
            self.commit()
        return id

        '''returns list of quota tuples (site_id, site_name, quota, valid_until_date)'''
        return self.executeQuery('SELECT * FROM lta.site_quota;', FETCH_All)

    def directory(self, dir_id):
        '''returns lta.directory (id, name, site_id, site_name) for the given dir_id'''
        return self.executeQuery('''SELECT dir.id as dir_id, dir.name as dir_name, site.id as site_id, site.name as site_name
            FROM lta.site_root_dir
            join lta.site site on site.id = site_root_dir.site_id
            join lta.directory_closure dc on dc.ancestor_id = site_root_dir.root_dir_id
            join lta.directory dir on dir.id = dc.descendant_id
            where dc.descendant_id = %s;
            ''', [dir_id], fetch=FETCH_ONE)

    def directoryByName(self, dir_name, site_id=None):
        """
        returns lta.directory (id, name, site_id, site_name) for the given dir_name
        :param string dir_name: the directory to search for
        :param int site_id: optional site_id to limit the search for this given site.
        :return:
        """
        query = '''SELECT dir.id as dir_id, dir.name as dir_name, site.id as site_id, site.name as site_name
            FROM lta.site_root_dir
            join lta.site site on site.id = site_root_dir.site_id
            join lta.directory_closure dc on dc.ancestor_id = site_root_dir.root_dir_id
            join lta.directory dir on dir.id = dc.descendant_id
            where dir.name = %s'''
        args = [dir_name]
        if site_id is not None:
            query += " and site.id = %s"
            args.append(site_id)

        return self.executeQuery(query, args, fetch=FETCH_ONE)

    def dir_id(self, site_id, directory_name):
        '''returns lta.directory id for the given site_id, directory_name'''
        result = self.executeQuery('''SELECT dir.id
            FROM lta.site_root_dir
            join lta.directory_closure dc on dc.ancestor_id = site_root_dir.root_dir_id
            join lta.directory dir on dir.id = dc.descendant_id
            where site_root_dir.site_id = %s
            and dir.name = %s;''', [site_id, directory_name], fetch=FETCH_ONE)

        if result['id']:
            return result['id']

        return -1

    def rootDirectories(self):
        '''returns list of all root directories for all sites'''
        return self.executeQuery('''SELECT * FROM lta.site_root_directory;''', fetch=FETCH_ALL)

    def rootDirectoriesForSite(self, site_id):
        '''returns list of all root directories (id, name) for given site_id'''
        return self.executeQuery('''SELECT * FROM lta.site_root_directory where site_id = %s;''', [site_id], fetch=FETCH_ALL)

    def rootDirectory(self, root_dir_id):
        '''returns the root directory for the given root_dir_id'''
        return self.executeQuery('''SELECT * FROM lta.site_root_directory WHERE root_dir_id = %s;''',
                                 [root_dir_id], fetch=FETCH_ONE)

    def get_root_dir_for_dir_path(self, dir_path, site_id):
        """
        find the root_dir under which this dir_path at the given site_id belongs
        :param str dir_path: a full path to a (sub)directory
        :param int site_id: the id of the site which contains the root dir under which the dir_path resides.
        :return: the dict for the root directory under which the given dir_path resides.
        """
        root_dirs = self.rootDirectoriesForSite(site_id)
        return next((rd for rd in root_dirs if dir_path.startswith(rd['dir_name'])), None)

    def subDirectories(self, dir_id, depth = 1, includeSelf=False):
        '''returns list of all sub directories up to the given depth (id, name, parent_dir_id, depth) for the given dir_id'''
        if depth == 1 and not includeSelf:
            return self.executeQuery('''
                SELECT dir.id as id, dir.name as name, dir.parent_dir_id as parent_dir_id
                FROM lta.directory dir
                where dir.parent_dir_id = %s;
                ''', (dir_id, ), fetch=FETCH_ALL)
        return self.executeQuery('''
            SELECT dir.id as id, dir.name as name, dir.parent_dir_id as parent_dir_id, lta.directory_closure.depth as depth
            FROM lta.directory_closure
            join lta.directory dir on dir.id = lta.directory_closure.descendant_id
            where ancestor_id = %s and depth <= %s and depth > %s
            order by depth asc;
            ''', (dir_id, depth, -1 if includeSelf else 0), fetch=FETCH_ALL)

    def parentDirectories(self, dir_id):
        return self.executeQuery('''
            SELECT dir.* FROM lta.directory_closure dc
            join lta.directory dir on dir.id = dc.ancestor_id
            where dc.descendant_id = %s and depth > 0
            order by depth desc;
            ''', [dir_id], fetch=FETCH_ALL)

    def _get_lowest_known_directory(self, dir_path, parent_root_dir):
        """
        given the dir_path, find try to find the lowest known dir which is a subdir under the given parent_root_dir
        example: root_dir         = '/path/to/root'
                 known_subdir_1   = '/path/to/root/sub1'
                 known_subdir_2   = '/path/to/root/sub1/sub2'
                 (input) dir_path = '/path/to/root/sub1/sub2/sub3/sub4'
                 would return (['/path/to/root/sub1/sub2/sub3/sub4', '/path/to/root/sub1/sub2/sub3'], <dict_for_known_subdir_2>)
        :param str dir_path: a full directory path (which should start with the same path as the parent root dir)
        :param dict parent_root_dir: a self.rootDirectory() result dict the supposed parent root dir
        :return: a tuple (list, dict) where the list is the list of missing full subdir paths, and the dict is the
                 lowest known subdir, or None if not found.
        """
        site_id = parent_root_dir['site_id']
        missing_child_dirs = []

        # search for dir_path in the database... it might already be known
        climbing_dir_path = dir_path
        db_dir = self.directoryByName(climbing_dir_path, site_id)
        # if climbing_dir_path is not known, then walk up one dir, and repeat until at top.
        while db_dir is None and parent_root_dir['dir_name'] != climbing_dir_path:
            # climb up one dir, add lowest subdir as missing child
            path_parts = climbing_dir_path.split('/')
            missing_child_dirs.append(climbing_dir_path)
            climbing_dir_path = '/'.join(path_parts[:-1])
            db_dir = self.directoryByName(climbing_dir_path, site_id)

        # return the list of missing_child_dirs (which might be empty)
        # and the found lowest found db_dir (which might be None)
        return missing_child_dirs, db_dir

    def _date_bounded(self, query, args, table_column, from_date=None, to_date=None):
        result_query = query
        result_args = args
        if from_date:
            result_query += ' and {column} >= %s'.format(column=table_column)
            result_args += (from_date,)

        if to_date:
            result_query += ' and {column} <= %s'.format(column=table_column)
            result_args += (to_date,)

        return result_query, result_args

    def filesInDirectory(self, dir_id, from_date=None, to_date=None):
        query = '''SELECT * FROM lta.fileinfo
        where dir_id = %s'''

        args = (dir_id,)

        query, args = self._date_bounded(query, args, 'fileinfo.creation_date', from_date, to_date)

        return self.executeQuery(query, args, fetch=FETCH_ALL)

    def numFilesInDirectory(self, dir_id, from_date=None, to_date=None):
        query = '''SELECT count(id) FROM lta.fileinfo
        where dir_id = %s'''

        args = (dir_id,)

        query, args = self._date_bounded(query, args, 'fileinfo.creation_date', from_date, to_date)

        result = self.executeQuery(query, args, fetch=FETCH_ONE)

        if result['count']:
            return result['count']

        return 0

    def directoryTreeStats(self, dir_id):
        query = '''SELECT * FROM metainfo.stats WHERE dir_id = %s'''
        args = (dir_id,)

        return self.executeQuery(query, args, fetch=FETCH_ONE)

    def filesInTree(self, base_dir_id, from_date=None, to_date=None):
        query = '''SELECT dir.id as dir_id, dir.name as dir_name, dc.depth as dir_depth, fi.id as file_id, fi.name as file_name, fi.size as file_size, fi.creation_date as file_creation_date
        FROM lta.directory_closure dc
        JOIN lta.directory dir on dir.id = dc.descendant_id
        JOIN lta.fileinfo fi on fi.dir_id = dc.descendant_id
        WHERE dc.ancestor_id = %s'''

        args = (base_dir_id,)

        query, args = self._date_bounded(query, args, 'fi.creation_date', from_date, to_date)

        return self.executeQuery(query, args, fetch=FETCH_ALL)

    def totalFileSizeAndNumFilesInSite(self, site_id, from_date=None, to_date=None):
        query = '''SELECT * FROM metainfo.get_site_stats(%s, %s, %s)'''
        args = (site_id, from_date, to_date)

        return self.executeQuery(query, args, fetch=FETCH_ONE)

    def totalFileSizeAndNumFilesInTree(self, base_dir_id, from_date=None, to_date=None):
        query = '''SELECT * FROM metainfo.get_tree_stats(%s, %s, %s)'''
        args = (base_dir_id, from_date, to_date)

        return self.executeQuery(query, args, fetch=FETCH_ONE)

    def totalFileSizeInTree(self, base_dir_id, from_date=None, to_date=None):
        return self.totalFileSizeAndNumFilesInTree(base_dir_id, from_date, to_date)['tree_total_file_size']

    def numFilesInTree(self, base_dir_id, from_date=None, to_date=None):
        return self.totalFileSizeAndNumFilesInTree(base_dir_id, from_date, to_date)['tree_num_files']

    def numFilesInSite(self, site_id, from_date=None, to_date=None):
        return self.totalFileSizeAndNumFilesInSite(site_id, from_date, to_date)['tree_num_files']

    def totalFileSizeInSite(self, site_id, from_date=None, to_date=None):
        return self.totalFileSizeAndNumFilesInSite(site_id, from_date, to_date)['tree_total_file_size']

    def datetimeRangeOfFilesInTree(self, base_dir_id = None):
        query = '''SELECT min(fileinfo.creation_date) as min_creation_date,
                   max(fileinfo.creation_date) as max_creation_date
                   FROM lta.fileinfo
                   LIMIT 1'''
        args = None

        if base_dir_id:
            query += '''\njoin lta.directory_closure dc on dc.descendant_id = lta.fileinfo.dir_id
            where ancestor_id = %s'''
            args = [base_dir_id]

        result = self.executeQuery(query, args, fetch=FETCH_ONE)

        if result:
            return (result['min_creation_date'], result['max_creation_date'])

        utcnow = datetime.datetime.utcnow()
        return (utcnow, utcnow)

    def mostRecentVisitDate(self):
        result = self.executeQuery('''
            SELECT visit_date FROM scraper.last_directory_visit
            order by visit_date desc
            limit 1
            ''', fetch=FETCH_ONE)

        if result:
            return result['visit_date']

        return datetime.datetime(2011, 1, 1)

    def numDirectoriesNotVisitedSince(self, timestamp):
        result = self.executeQuery('''
            SELECT count(dir_id) FROM scraper.last_directory_visit
            WHERE visit_date < %s
            ''', [timestamp], fetch=FETCH_ONE)

        if result:
            return result['count']

        return 0

    def siteQuotaUsages(self):
        return self.executeQuery('''SELECT * FROM metainfo.site_quota_usage;''', fetch=FETCH_ALL)

    def siteQuotaRootDirStats(self):
        return self.executeQuery('''SELECT * FROM metainfo.site_quota_root_dir_stats;''', fetch=FETCH_ALL)

    def visitStats(self, before_timestamp = None):
        if not before_timestamp:
            before_timestamp = datetime.datetime.utcnow()

        sites = self.sites()
        siteStats = {}

        for site in sites:
            site_id = site['id']
            site_name = site['name']
            siteStats[site_name] = {'site_id': site_id}

            visits = self.executeQuery('''
                select *
                from scraper.site_scraper_last_directory_visit
                where site_id = %s
                and last_visit < %s
                order by last_visit asc
                ''', [site_id, before_timestamp], fetch=FETCH_ALL)

            siteStats[site_name]['queue_length'] = len(visits)
            if len(visits) > 0:
                siteStats[site_name]['least_recent_visited_dir_id'] = visits[0]['dir_id']
                siteStats[site_name]['least_recent_visit'] = visits[0]['last_visit']

        return siteStats



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)
    dbcreds = dbcredentials.DBCredentials().get('LTASO')
    with LTAStorageDb(dbcreds, True) as db:
        print(db.rootDirectoriesForSite(1))
        print(db.dir_id(1, 'rootDir_0'))
