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

# $Id: scraper.py 43211 2019-06-18 18:55:40Z klazema $

# TODO: add comments to methods
# TODO: code cleanup
# TODO: scraper should be able to process each directory more than once. Requires changes in store.py

import subprocess
import logging
import time
import datetime
import sys
import socket
import os
import os.path
import threading
import multiprocessing
from lofar.lta.ltastorageoverview import store
from lofar.common.util import humanreadablesize
from lofar.common.subprocess_utils import communicate_returning_strings
from random import random, randint

logger = logging.getLogger()

VISIT_INTERVAL = datetime.timedelta(days=7)
LEXAR_HOST = 'ingest@lexar004.control.lofar'

class FileInfo:
    '''Simple struct to hold filename and size'''
    def __init__(self, filename, size, created_at):
        '''
        Parameters
        ----------
        filename : string
        size : int
        '''
        self.filename = filename
        self.size = size
        self.created_at = created_at

    def __str__(self):
        return self.filename + " " + humanreadablesize(self.size) + " " + str(self.created_at)

class SrmlsException(Exception):
    '''Exception which is raised when an srmls command failes'''
    def __init__(self, command, exitcode, stdout, stderr):
        self.command = command
        self.exitcode = exitcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "%s failed with code %d.\nstdout: %s\nstderr: %s" % \
                (self.command, self.exitcode, self.stdout, self.stderr)

class ParseException(Exception):
    '''Exception which is raised when parsing srmls results fails'''
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Location:
    '''A Location is a directory at a storage site which can be queried with getResult()'''
    def __init__(self, srmurl, directory):
        '''
        Parameters
        ----------
        srmurl : string
            the srm url of the storage site. for example: srm://srm.grid.sara.nl:8443
        directory : int
            a directory at the storage site. for example: /pnfs/grid.sara.nl/data/lofar/storage
        '''
        self.srmurl = srmurl.rstrip('/')
        self.directory = directory.rstrip('/') if len(directory) > 1 else directory

        if not self.srmurl.startswith('srm://'):
            raise ValueError('malformed srm url: %s' % (self.srmurl,))

        if not self.directory.startswith('/'):
            raise ValueError('malformed directory path: "%s". should start with a /' % (self.directory,))

    def path(self):
        '''returns the full path srmurl + directory'''
        return self.srmurl + self.directory

    def isRoot(self):
        '''is this a root directory?'''
        return self.directory == '/'

    def parentDir(self):
        '''returns parent directory path'''
        if self.isRoot():
            return '/'
        stripped = self.directory.rstrip('/')
        ridx = stripped.rindex('/')
        if ridx == 0:
            return '/'
        return stripped[:ridx]

    def parentLocation(self):
        '''returns a Location object for the parent directory'''
        return Location(self.srmurl, self.parentDir())

    def __str__(self):
        '''returns the full path'''
        return self.path()

    def getResult(self, offset=0):
        '''Returns LocationResult with the subdirectries and files in at this location'''
        foundFiles = []
        foundDirectories = []

        logger.info("Scanning %s with offset=%s", self.path(), offset)

        # the core command: do an srmls call and parse the results
        # srmls can only yield max 900 items in a result, hence we can recurse for the next 900 by using the offset
        cmd = ['ssh', '-tt', '-n', '-x', '-q', LEXAR_HOST,
               "srmls -l -count=900 -offset=%d %s%s" % (
                offset,
                self.srmurl,
                self.directory) ]

        logger.debug(' '.join(cmd))
        p = subprocess.Popen(cmd, stdin=open('/dev/null'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logs = communicate_returning_strings(p)
        # logger.debug('Shell command for %s exited with code %s' % (self.path(), p.returncode))
        loglines = logs[0].split('\n')

        # parse logs from succesfull command
        if p.returncode == 0 and len(loglines) > 1:
            entries = []
            entry = []

            for line in loglines:
                entry.append(line)

                if 'Type:' in line:
                    entries.append(entry)
                    entry = []

            for lines in entries:
                if len(lines) < 2:
                    continue
                pathLine = lines[0].strip()
                pathLineItems = [x.strip() for x in pathLine.split()]
                entryType = lines[-1].strip().split('Type:')[-1].strip()

                if len(pathLineItems) < 2:
                    raise ParseException("path line shorter than expected: %s" % pathLine)

                if entryType.lower() == 'directory':
                    dirname = pathLineItems[1]
                    if dirname.rstrip('/') == self.directory.rstrip('/'):
                        # skip current directory
                        continue

                    if len(dirname) < 1 or not dirname[0] == '/':
                        raise ParseException("Could not parse dirname from line: %s\nloglines:\n%s"
                            % (pathLineItems[1], logs[0]))

                    foundDirectories.append(Location(self.srmurl, dirname.rstrip('/')))
                elif entryType.lower() == 'file':
                    try:
                        filesize = int(pathLineItems[0])
                        filename = pathLineItems[1]
                        timestamplines = [x for x in lines if 'ed at:' in x]
                        timestampline = None
                        for line in timestamplines:
                            if 'created' in line and '1970' not in line:
                                timestampline = line
                                break
                            timestampline = line
                        timestamppart = timestampline.split('at:')[1].strip()
                        timestamp = datetime.datetime.strptime(timestamppart + ' UTC', '%Y/%m/%d %H:%M:%S %Z')
                        foundFiles.append(FileInfo(filename, filesize, timestamp))
                    except Exception as e:
                        raise ParseException("Could not parse fileproperies:\n%s\nloglines:\n%s"
                            % (str(e), logs[0]))
                else:
                    logger.error("Unknown type: %s" % entryType)

            # recurse and ask for more files if we hit the 900 line limit
            if len(entries) >= 900:
                logger.debug('There are more than 900 lines in the results')
                extraResult = self.getResult(offset + 900)
                logger.debug('extraResult %s' % str(extraResult))
                foundDirectories += extraResult.subDirectories
                foundFiles += extraResult.files
        else:
            raise SrmlsException(' '.join(cmd), p.returncode, logs[0], logs[1])

        return LocationResult(self, foundDirectories, foundFiles)


class LocationResult:
    '''Holds the query result for a Location: a list of subDirectories and/or a list of files'''
    def __init__(self, location, subDirectories = None, files = None):
        '''
        Parameters
        ----------
        location : Location
            For which location this result was generated. (i.e. it is the parent of the subdirectories)

        subDirectories : [Location]
            A list of subdirectories

        files : [FileInfo]
            A list of files in this location
        '''
        self.location = location
        self.subDirectories = subDirectories if subDirectories else []
        self.files = files if files else []

    def __str__(self):
        return "LocationResult: path=%s # subdirs=%d # files=%d totalFileSizeOfDir=%s" % (self.location.path(), self.nrOfSubDirs(), self.nrOfFiles(), humanreadablesize(self.totalFileSizeOfDir()))

    def nrOfSubDirs(self):
        return len(self.subDirectories)

    def nrOfFiles(self):
        return len(self.files)

    def totalFileSizeOfDir(self):
        return sum([fileinfo.size for fileinfo in self.files])


class ResultGetterThread(threading.Thread):
    '''Helper class to query Locations asynchronously for results.
    Gets the result for the first Location in the locations deque and appends it to the results deque
    Appends the subdirectory Locations at the end of the locations deque for later processing'''
    def __init__(self, dbcreds, dir_id):
        threading.Thread.__init__(self)
        self.daemon = True
        self.dbcreds = dbcreds
        self.dir_id = dir_id

    def run(self):
        '''A single location is pop\'ed from the locations deque and the results are queried.
        Resulting subdirectories are appended to the locations deque'''
        try:
            with store.LTAStorageDb(self.dbcreds) as db:
                dir = db.directory(self.dir_id)

                if not dir:
                    return

                dir_id = dir['dir_id']
                dir_name = dir['dir_name']

                site_id = dir['site_id']
                site = db.site(site_id)
                srm_url = site['url']

            location = Location(srm_url, dir_name)

            try:
                def rescheduleVisit():
                    for i in range(5):
                        try:
                            with store.LTAStorageDb(self.dbcreds) as db:
                                logger.info('Rescheduling %s for new visit.' % (location.path(),))
                                db.updateDirectoryLastVisitTime(self.dir_id, datetime.datetime.utcnow() - VISIT_INTERVAL + datetime.timedelta(mins=1))
                                break
                        except:
                            time.sleep(1)


                # get results... long blocking
                result = location.getResult()
                logger.info(result)

                with store.LTAStorageDb(self.dbcreds) as db:
                    # convert the result.files list into a dict
                    #with (filename, dir_id) as key and a tuple with all file info as value
                    result_file_tuple_dict = {}
                    for file in result.files:
                        filename = file.filename.split('/')[-1]
                        key = (filename, dir_id)
                        file_tuple = (filename, int(file.size), file.created_at, dir_id)
                        result_file_tuple_dict[key] = file_tuple

                    # create a dict of all already known files from the db
                    known_file_dict = {}
                    for file in db.filesInDirectory(dir_id):
                        key = (str(file['name']), dir_id)
                        known_file_dict[key] = file

                    # now compare the result and known (filename, dir_id) sets
                    # and find out which a new, and which are known.
                    # compare only by (filename, dir_id) because for a given file the size and/or date might have changed,
                    # but that does not make it a new/unique file.
                    result_file_key_set = set(result_file_tuple_dict.keys())
                    known_file_key_set = set(known_file_dict.keys())
                    new_file_key_set = result_file_key_set - known_file_key_set
                    removed_file_key_set = known_file_key_set - result_file_key_set

                    logger.info("%s %s: %d out of %d files are new, and %d are already known", site['name'],
                                                                                                dir_name,
                                                                                                len(new_file_key_set),
                                                                                                len(result_file_key_set),
                                                                                                len(known_file_key_set))

                    if new_file_key_set:
                        new_file_tuple_set = [result_file_tuple_dict[key] for key in new_file_key_set]
                        file_ids = db.insertFileInfos(new_file_tuple_set)

                        if len(file_ids) != len(new_file_tuple_set):
                            rescheduleVisit()

                    if known_file_key_set:
                        for key, known_file in list(known_file_dict.items()):
                            if key in result_file_tuple_dict:
                                result_file_tuple = result_file_tuple_dict[key]

                                known_size = int(known_file['size'])

                                result_size = result_file_tuple[1]

                                if known_size != result_size:
                                    logger.info("%s %s: updating %s (id=%d) size from %d to %d",
                                                site['name'], dir_name, known_file['name'], known_file['id'],
                                                known_size, result_size)
                                    db.updateFileInfoSize(known_file['id'], result_size)

                    if removed_file_key_set:
                        for removed_file_key in removed_file_key_set:
                            db.deleteFileInfoFromDirectory(removed_file_key[0], removed_file_key[1])

                    # skip empty nikhef dirs
                    filteredSubDirectories = [loc for loc in result.subDirectories
                                              if not ('nikhef' in loc.srmurl and 'generated' in loc.directory) ]

                    # skip sksp spectroscopy project
                    filteredSubDirectories = [loc for loc in filteredSubDirectories
                                              if not ('sara' in loc.srmurl and 'sksp' in loc.directory and 'spectro' in loc.directory) ]

                    subDirectoryNames = [loc.directory for loc in filteredSubDirectories]

                    if subDirectoryNames:
                        #check for already known subdirectories in the db
                        known_subDirectoryNames_set = set(subdir['name'] for subdir in db.subDirectories(dir_id))

                        new_subdir_name_set = set(subDirectoryNames) - known_subDirectoryNames_set;

                        logger.info("%s %s: %d out of %d subdirs are new, and %d are already known", site['name'], dir_name, len(new_subdir_name_set), len(subDirectoryNames), len(known_subDirectoryNames_set))

                        if new_subdir_name_set:
                            subdir_ids = db.insertSubDirectories(new_subdir_name_set, dir_id)

                            if len(subdir_ids) != len(new_subdir_name_set):
                                rescheduleVisit()

            except (SrmlsException, ParseException) as e:
                logger.error('Error while scanning %s\n%s' % (location.path(), str(e)))

                if 'does not exist' in str(e):
                    with store.LTAStorageDb(self.dbcreds) as db:
                        db.deleteDirectory(self.dir_id)
                else:
                    rescheduleVisit()

        except Exception as e:
            logger.exception(str(e))

            with store.LTAStorageDb(self.dbcreds) as db:
                logger.info('Rescheduling dir_id %d for new visit.' % (self.dir_id,))
                db.updateDirectoryLastVisitTime(self.dir_id, datetime.datetime.utcnow() - VISIT_INTERVAL)

def populateDbWithLTASitesAndRootDirs(db):
    """
    Helper method to fill empty database with (hardcoded) information about our LTA partners/sites/quotas
    """
    if not db.sites():
        #db.insertSite('nikhef', 'srm://tbn18.nikhef.nl:8446')
        sara_id = db.insertSiteIfNotExists('sara', 'srm://srm.grid.sara.nl:8443')
        juelich_id = db.insertSiteIfNotExists('juelich', 'srm://lofar-srm.fz-juelich.de:8443')
        poznan_id = db.insertSiteIfNotExists('poznan', 'srm://lta-head.lofar.psnc.pl:8443')

        # insert the LTA site root dir(s)
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/software')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/ops')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/storage')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/eor')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/pulsar')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/cosmics')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/surveys')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/user')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/proc')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/trans')
        db.insertRootDirectory('sara', '/pnfs/grid.sara.nl/data/lofar/lotest')
        db.insertRootDirectory('juelich', '/pnfs/fz-juelich.de/data/lofar/ops')
        db.insertRootDirectory('poznan', '/lofar/ops')
        #db.insertRootDirectory('nikhef', '/dpm/nikhef.nl/home/lofar')

        def end_of_year(year):
            '''little helper function which returns a datetime timestamp for the end of the given year'''
            return datetime.datetime(year, 12, 31, 23, 59, 59)

        # insert quota as given by our LTA partners
        db.insertSiteQuota(sara_id, 5e15, end_of_year(2012))
        db.insertSiteQuota(sara_id, 8e15, end_of_year(2013))
        db.insertSiteQuota(sara_id, 11e15, end_of_year(2014))
        db.insertSiteQuota(sara_id, 14e15, end_of_year(2015))
        db.insertSiteQuota(sara_id, 17e15, end_of_year(2016))
        db.insertSiteQuota(sara_id, 20e15, end_of_year(2017))
        db.insertSiteQuota(sara_id, 23e15, end_of_year(2018))

        db.insertSiteQuota(juelich_id, 2.5e15, end_of_year(2013))
        db.insertSiteQuota(juelich_id, 4.5e15, end_of_year(2014))
        db.insertSiteQuota(juelich_id, 6.5e15, end_of_year(2015))
        db.insertSiteQuota(juelich_id, 8.5e15, end_of_year(2016))
        db.insertSiteQuota(juelich_id, 10.5e15, end_of_year(2017))
        db.insertSiteQuota(juelich_id, 12.5e15, end_of_year(2018))

        db.insertSiteQuota(poznan_id, 0.5e15, end_of_year(2016))
        db.insertSiteQuota(poznan_id, 3.5e15, end_of_year(2017))
        db.insertSiteQuota(poznan_id, 5.5e15, end_of_year(2018))


def main():
    '''the main function scanning all locations and gathering the results'''

    from optparse import OptionParser
    from lofar.common import dbcredentials
    from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
    from lofar.lta.ltastorageoverview.ingesteventhandler import LTASOIngestEventHandler, IngestEventMesssageBusListener

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='runs the lta scraper and stores results in the speficied database.')
    parser.add_option('-j', '--parallel', dest='parallel', type='int', default=8, help='number of parallel srmls jobs to run, default: %default')

    parser.add_option('-b', '--broker', dest='broker', type='string', default=DEFAULT_BROKER,
                      help='Address of the messaging broker, default: %default')
    parser.add_option('-e', '--exchange', dest='exchange', type='string',
                      default=DEFAULT_BUSNAME,
                      help='Name of the bus exchange on the broker on which the ingest notifications are published, default: %default')

    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="LTASO")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)
    options.parallel = max(1, min(8*multiprocessing.cpu_count(), options.parallel))
    logger.info("Using maximum number of parallel srmls jobs: %d" % options.parallel)

    dbcreds = dbcredentials.parse_options(options)
    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    db = store.LTAStorageDb(dbcreds)
    populateDbWithLTASitesAndRootDirs(db)

    # for each site we want one or more ResultGetterThreads
    # so make a dict with a list per site based on the locations
    getters = dict([(site['name'],[]) for site in db.sites()])

    # some helper functions
    def numLocationsInQueues():
        '''returns the total number of locations in the queues'''
        return db.numDirectoriesNotVisitedSince(datetime.datetime.utcnow() - VISIT_INTERVAL)

    def totalNumGetters():
        '''returns the total number of parallel running ResultGetterThreads'''
        return sum([len(v) for v in list(getters.values())])

    def cleanupFinishedGetters():
        # get rid of old finished ResultGetterThreads
        finishedGetters = dict([(site_name, [getter for getter in getterList if not getter.isAlive()]) for site_name, getterList in list(getters.items())])
        for site_name,finishedGetterList in list(finishedGetters.items()):
            for finishedGetter in finishedGetterList:
                getters[site_name].remove(finishedGetter)


    # the main loop
    # loop over the locations and spawn ResultGetterThreads to get the results parallel
    # use load balancing over the different sites and with respect to queue lengths
    # do not overload this host system
    with IngestEventMesssageBusListener(handler_type=LTASOIngestEventHandler,
                                        handler_kwargs={'dbcreds': dbcreds},
                                        exchange=options.exchange, broker=options.broker):
        while True:

            cleanupFinishedGetters()

            # spawn new ResultGetterThreads
            # do not overload this host system
            num_waiting = numLocationsInQueues()
            while (num_waiting > 0 and
                   totalNumGetters() < options.parallel and
                   os.getloadavg()[0] < 4*multiprocessing.cpu_count()):
                sitesStats = db.visitStats(datetime.datetime.utcnow() - VISIT_INTERVAL)

                for site_name, site_stats in list(sitesStats.items()):
                    numGetters = len(getters[site_name])
                    queue_length = site_stats['queue_length']
                    weight = float(queue_length) / float(20 * (numGetters + 1))
                    if numGetters == 0 and queue_length > 0:
                        weight = 1e6 # make getterless sites extra important, so each site keeps flowing
                    site_stats['# get'] = numGetters
                    site_stats['weight'] = weight

                totalWeight = max(1.0, sum([site_stats['weight'] for site_stats in list(sitesStats.values())]))

                logger.debug("siteStats:\n%s" % str('\n'.join([str((k, v)) for k, v in list(sitesStats.items())])))

                # now pick a random site using the weights
                chosen_site_name = None
                cumul = 0.0
                r = random()
                for site_name,site_stats in list(sitesStats.items()):
                    ratio = site_stats['weight']/totalWeight
                    cumul += ratio

                    if r <= cumul and site_stats['queue_length'] > 0:
                        chosen_site_name = site_name
                        break

                if not chosen_site_name:
                    break

                chosen_dir_id = sitesStats[chosen_site_name]['least_recent_visited_dir_id']
                db.updateDirectoryLastVisitTime(chosen_dir_id, datetime.datetime.utcnow())

                logger.debug("chosen_site_name: %s chosen_dir_id: %s", chosen_site_name, chosen_dir_id)

                # make and start a new ResultGetterThread the location deque of the chosen site
                newGetter = ResultGetterThread(dbcreds, chosen_dir_id)
                newGetter.start()
                getters[chosen_site_name].append(newGetter)

                cleanupFinishedGetters()

                # refresh num_waiting
                num_waiting = numLocationsInQueues()
                logger.info('numLocationsInQueues=%d totalNumGetters=%d siteQueueLengths: %s load_5min: %.1f' % (num_waiting,
                                                                                                                 totalNumGetters(),
                                                                                                                 ' '.join(['%s:%d' % (name, stats['queue_length']) for name, stats in list(sitesStats.items())]),
                                                                                                                 os.getloadavg()[0]))

            # sleep before main loop next iteration
            # to wait for some results
            # and some getters to finish
            time.sleep(30 if num_waiting <= options.parallel else 0.25)

        # all locations were processed

if __name__ == "__main__":
    main()

