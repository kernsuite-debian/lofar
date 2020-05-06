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

# $Id: webservice.py 42507 2019-04-09 19:08:50Z schaap $

# TODO: add comment to methods
# TODO: code cleanup
# TODO: where to store the sqlite database?

import sys
import os
import os.path
from datetime import datetime
import logging
from flask import Flask
from flask import render_template
from flask import json
from lofar.lta.ltastorageoverview import store
from lofar.common.util import humanreadablesize
from lofar.common.datetimeutils import monthRanges

logger = logging.getLogger(__name__)

__root_path = os.path.dirname(os.path.realpath(__file__))

'''The flask webservice app'''
app = Flask('LTA storage overview',
            instance_path=__root_path,
            template_folder=os.path.join(__root_path, 'templates'),
            static_folder=os.path.join(__root_path, 'static'),
            instance_relative_config=True)

db = None

@app.route('/')
@app.route('/index.html')
def index():
    # TODO: serve html first, and let client request data via ajax
    usages = {}

    colors = {'sara': {'used': '#90ed7d', 'free': '#c5f6bc'},
              'juelich': {'used': '#494950', 'free': '#a1a1aa'},
              'poznan': {'used': '#7cb5ec', 'free': '#bcdaf5'}}

    sites = db.sites()
    sitesDict = { s['name']:s for s in sites }
    sites = [sitesDict[sitename] for sitename in ['poznan', 'juelich', 'sara'] if sitename in sitesDict]

    total_lta_size = 0.0
    total_lta_num_files = 0
    for site in sites:
        totals = db.totalFileSizeAndNumFilesInSite(site['id'])
        total_lta_size += totals['tree_total_file_size']
        total_lta_num_files += totals['tree_num_files']
        usages[site['name']] = totals['tree_total_file_size']

    if total_lta_size > 0:
        storagesitedata='[' + ', '.join(['''{name: "%s %s", color:'%s', y: %.2f}''' % (site['name'], humanreadablesize(usages[site['name']]),
                                                                                       colors[site['name']]['used'],
                                                                                       100.0*usages[site['name']]/total_lta_size) for site in sites]) + ']'
    else:
        storagesitedata ='[]'

    min_date, max_date = db.datetimeRangeOfFilesInTree()
    logger.info("datetimeRangeOfFilesInTree: min_date=%s, max_date=%s", min_date, max_date)
    if min_date is None:
        min_date = datetime(2012, 1, 1)
    if max_date is None:
        max_date = datetime.utcnow()
    min_date = max(datetime(2012, 1, 1), min_date)
    logger.info("month_ranges: min_date=%s, max_date=%s", min_date, max_date)
    month_ranges = monthRanges(min_date, max_date, 1)

    # convert end-of-month timestamps to milliseconds since epoch
    epoch = datetime.utcfromtimestamp(0)
    datestamps=[('%d' % ((x[1] - epoch).total_seconds()*1000,)) for x in month_ranges]

    usage_per_month_series='['
    deltas_per_month_series='['
    for site in sites:
        deltas_per_month = [db.totalFileSizeInSite(site['id'], from_date=mr[0], to_date=mr[1]) for mr in month_ranges]
        data = ', '.join(['[%s, %s]' % (x[0], str(x[1])) for x in zip(datestamps, deltas_per_month)])
        deltas_per_month_series += '''{name: '%s', color:'%s', data: [%s]},\n''' % (site['name'], colors[site['name']]['used'], data)

        cumulatives = [deltas_per_month[0]]
        for delta in deltas_per_month[1:]:
            cumulative = cumulatives[-1] + delta
            cumulatives.append(cumulative)

        data = ', '.join(['[%s, %s]' % (x[0], str(x[1])) for x in zip(datestamps, cumulatives)])
        usage_per_month_series += '''{name: '%s', color:'%s', data: [%s]},\n''' % (site['name'], colors[site['name']]['used'], data)



    usage_per_month_series+=']'
    deltas_per_month_series+=']'

    quota_dir_stats = db.siteQuotaRootDirStats()
    quota_dir_stats = sorted(quota_dir_stats, reverse=True, key=lambda x: x['tree_total_file_size'])

    site_usages_per_site = {}
    latest_usages_per_site = {}
    for site_usage in db.siteQuotaUsages():
        site_name = site_usage['site_name']
        if site_name not in site_usages_per_site:
            site_usages_per_site[site_name] = []
        site_usages_per_site[site_name].append(site_usage)
        if site_name not in latest_usages_per_site:
            latest_usages_per_site[site_name] = site_usage
        if site_usage['valid_until_date'] > latest_usages_per_site[site_name]['valid_until_date']:
            latest_usages_per_site[site_name] = site_usage


    quota_series='['
    storagesite_free_space='['
    site_tape_usages_table = '<table>\n'
    site_tape_usages_table += '<tr><th style="text-align: left;">site</th><th style="text-align: left;">directory</th><th>total #files</th><th>total file size</th><th>quota</th><th>free</th><th>expiration</th></tr>\n'
    total_lta_free_space = sum(u['space_left'] for u in list(latest_usages_per_site.values()) if u['space_left'] > 0)
    total_lta_quota = sum(u['quota'] for u in list(latest_usages_per_site.values()))

    for site_name in ['sara','juelich', 'poznan']:
        if site_name in latest_usages_per_site:
            latest_usage = latest_usages_per_site[site_name]
            site_tape_usages_table += '<tr style="font-weight: bold;"><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td>%s</td><td>%s</td><td>%s</td><td %s>%s</td><td>%s</td></tr>\n' % (latest_usage['site_name'], '', latest_usage['num_files'], humanreadablesize(latest_usage['total_file_size']), humanreadablesize(latest_usage['quota']), 'style="color: red;"' if latest_usage['space_left'] < 0 else '', humanreadablesize(latest_usage['space_left']), latest_usage['valid_until_date'])

            for qds in quota_dir_stats:
                if qds['site_name'] == site_name:
                    site_tape_usages_table += '<tr><td style="text-align: left;">%s</td><td style="text-align: left;">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
                        '', qds['dir_name'], qds['tree_num_files'], humanreadablesize(qds['tree_total_file_size']), '', '', '')

            storagesite_free_space += '''{name: "%s %s", color:'%s', y: %.2f}, ''' % (site_name,
                                                                                      humanreadablesize(latest_usage['space_left']),
                                                                                      colors[site_name]['free'],
                                                                                      max(0, 100.0 * latest_usage['space_left']) / total_lta_free_space)


    site_tape_usages_table += '</table>\n'

    for site_name in ['poznan','juelich', 'sara']:
        if site_name in site_usages_per_site:
            site_usages_for_site = site_usages_per_site[site_name]
            site_usages_for_site = sorted(site_usages_for_site, key=lambda x: x['valid_until_date'])
            data = ','.join('[%d, %s]' % ((su['valid_until_date'] - epoch).total_seconds()*1000, su['space_left']) for su in site_usages_for_site)
            quota_series+='''{ name:'%s_free', stack:'%s', color:'%s', data:[%s] },''' % (site_name,site_name,colors[site_name]['free'],data)
            data = ','.join('[%d, %s]' % ((su['valid_until_date'] - epoch).total_seconds()*1000, su['total_file_size']) for su in site_usages_for_site)
            quota_series+='''{ name:'%s_used', stack:'%s', color:'%s', data:[%s] },''' % (site_name,site_name,colors[site_name]['used'], data)


    quota_series+=']'
    storagesite_free_space+=']'

    return render_template('index.html',
                           title='LTA storage overview',
                           storagesitetitle='LTA Storage Site Usage',
                           storagesitesubtitle='Total: %s #dataproducts: %s' % (humanreadablesize(total_lta_size, 'B', 1000), humanreadablesize(total_lta_num_files, '', 1000)),
                           storagesite_free_space_title='LTA Storage Site Free Space',
                           storagesite_free_space_subtitle='Total free space: %s Current total quota: %s' % (humanreadablesize(total_lta_free_space, 'B', 1000),humanreadablesize(total_lta_quota, 'B', 1000)),
                           storagesitedata=storagesitedata,
                           storagesite_free_space=storagesite_free_space,
                           usage_per_month_series=usage_per_month_series,
                           deltas_per_month_series=deltas_per_month_series,
                           quota_series=quota_series,
                           site_tape_usages=site_tape_usages_table,
                           data_gathered_timestamp=db.mostRecentVisitDate().strftime('%Y/%m/%d %H:%M:%S'))

@app.route('/rest/sites/')
def get_sites():
    return json.jsonify({'sites': db.sites()})

@app.route('/rest/sites/<int:site_id>')
def get_site(site_id):
    return json.jsonify(db.site(site_id))

@app.route('/rest/sites/usages')
def get_sites_usages():
    sites = {'sites_usages': db.sites()}

    for site in sites['sites_usages']:
        rootDirs = db.rootDirectoriesForSite(site['id'])

        site_usage = 0
        for rootDir in rootDirs:
            usage = int(db.totalFileSizeInTree(rootDir['dir_id']))
            site_usage += usage
        site['usage'] = site_usage
        site['usage_hr'] = humanreadablesize(site_usage)

    return json.jsonify(sites)

@app.route('/rest/rootdirectories/',)
def get_rootDirectories():
    rootDirs = {'rootDirectories': db.rootDirectories()}
    return json.jsonify(rootDirs)

@app.route('/rest/directory/<int:dir_id>/subdirectories/',)
def get_directoryTree(dir_id):
    subDirsList = {'subdirectories': db.subDirectories(dir_id, 1, False)}
    return json.jsonify(subDirsList)

@app.route('/rest/directory/<int:dir_id>/files')
def get_filesInDirectory(dir_id):
    files = {'files': db.filesInDirectory(dir_id)}
    return json.jsonify(files)


def main():
    from optparse import OptionParser
    from lofar.common import dbcredentials

    # Check the invocation arguments
    parser = OptionParser("%prog [options]", description='runs the lta scraper and stores results in the speficied database.')
    parser.add_option_group(dbcredentials.options_group(parser))
    parser.set_defaults(dbcredentials="LTASO")
    (options, args) = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    dbcreds = dbcredentials.parse_options(options)

    logger.info("Using dbcreds: %s" % dbcreds.stringWithHiddenPassword())

    global db
    db = store.LTAStorageDb(dbcreds)

    app.run(debug=False,host='0.0.0.0',port=9632)

if __name__ == '__main__':
    main()

