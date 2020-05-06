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

# $Id$

import logging
import time
from datetime import datetime, timedelta
import sys
import os
import os.path
from lofar.lta.ltastorageoverview import store
from lofar.common.util import humanreadablesize
from lofar.common.datetimeutils import monthRanges

logger = logging.getLogger()

def main():
    from optparse import OptionParser
    from lofar.common import dbcredentials

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='runs the lta scraper and stores results in the speficied database.')
    parser.add_option('-V', '--verbose', dest='verbose', action='store_true', help='verbose logging')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="LTASO")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.DEBUG if options.verbose else logging.INFO)

    dbcreds = dbcredentials.parse_options(options)

    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    db = store.LTAStorageDb(dbcreds, options.verbose)

    sites = db.sites()

    numFilesTotal = sum([db.numFilesInSite(s['id']) for s in sites])
    totalFileSize = sum([db.totalFileSizeInSite(s['id']) for s in sites])

    print('\n*** TOTALS *** #files=%s total_size=%s' % (humanreadablesize(numFilesTotal, ''),
                                                        humanreadablesize(totalFileSize)))

    for site in sites:
        numFilesInSite = db.numFilesInSite(site['id'])
        totalFileSizeInSite = db.totalFileSizeInSite(site['id'])

        print('\n--- %s ---  #files=%s total_size=%s' % (site['name'],
                                                         humanreadablesize(numFilesInSite, ''),
                                                         humanreadablesize(totalFileSizeInSite)))

        root_dirs = db.rootDirectoriesForSite(site['id'])

        for root_dir in root_dirs:
            numFilesInTree = db.numFilesInTree(root_dir['root_dir_id'])
            totalFileSizeInTree = db.totalFileSizeInTree(root_dir['root_dir_id'])

            print("  %s #files=%d total_size=%s" % (root_dir['dir_name'], numFilesInTree, humanreadablesize(totalFileSizeInTree)))

    utcnow = datetime.utcnow()
    monthbegin = datetime(utcnow.year, utcnow.month, 1)
    monthend =  datetime(utcnow.year, utcnow.month+1, 1) - timedelta(milliseconds=1)
    print('\n\n*** CHANGES THIS MONTH %s ***' % monthbegin.strftime('%Y/%m'))

    for site in sites:
        root_dirs = db.rootDirectoriesForSite(site['id'])

        numChangedFilesInSite = db.numFilesInSite(site['id'],
                                                  monthbegin,
                                                  monthend)

        if numChangedFilesInSite == 0:
            print('\n--- %s --- None' % (site['name'],))
            continue

        totalChangedFileSizeInSite = db.totalFileSizeInSite(site['id'],
                                                            monthbegin,
                                                            monthend)

        print('\n--- %s --- #files=%d total_size=%s' % (site['name'],
                                                        numChangedFilesInSite,
                                                        humanreadablesize(totalChangedFileSizeInSite)))

        for root_dir in root_dirs:
            changedFiles = db.filesInTree(root_dir['dir_id'], monthbegin, monthend)

            if len(changedFiles) > 0:
                numFilesInTree = db.numFilesInTree(root_dir['dir_id'],
                                                   monthbegin,
                                                   monthend)
                totalFileSizeInTree = db.totalFileSizeInTree(root_dir['dir_id'],
                                                             monthbegin,
                                                             monthend)

                print("  %s #files=%d total_size=%s" % (root_dir['dir_name'],
                                                        numFilesInTree,
                                                        humanreadablesize(totalFileSizeInTree)))

                # filter unique dirs containing changed files
                dirsWithChangedFiles = set([(x[0], x[1]) for x in changedFiles])

                # sort by name
                dirsWithChangedFiles = sorted(dirsWithChangedFiles, key=lambda x: x[1])

                for dir in dirsWithChangedFiles:
                    numFilesInTree = db.numFilesInTree(dir[0], monthbegin, monthend)
                    totalFileSizeInTree = db.totalFileSizeInTree(dir[0], monthbegin, monthend)

                    print("    %s #files=%d total_size=%s" % (dir[1], numFilesInTree, humanreadablesize(totalFileSizeInTree)))

    print('\n\n*** CHANGES PER MONTH ***')

    min_date, max_date = db.datetimeRangeOfFilesInTree()
    if min_date and max_date:
        month_ranges = monthRanges(min_date, max_date)

        for site in sites:
            print('\n--- %s ---' % site['name'])

            for month_range in month_ranges:
                numFilesInSite = db.numFilesInSite(site['id'], month_range[0], month_range[1])
                totalFileSizeInSite = db.totalFileSizeInSite(site['id'], month_range[0], month_range[1])

                print("  %s %s %s #files=%d total_size=%s" % (site['name'], month_range[0], month_range[1], numFilesInSite, humanreadablesize(totalFileSizeInSite)))


if __name__ == "__main__":
    main()

