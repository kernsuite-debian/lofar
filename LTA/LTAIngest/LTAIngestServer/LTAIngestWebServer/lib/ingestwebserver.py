#!/usr/bin/env python3

# Copyright (C) 2015
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import sys
import os, os.path
from functools import cmp_to_key
from datetime import datetime, timedelta
from lofar.common.util import humanreadablesize
from lofar.common import isDevelopmentEnvironment
from lofar.common.datetimeutils import totalSeconds
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME
from lofar.lta.ingest.client.rpc import IngestRPC

logger = logging.getLogger()

try:
    from flask import Flask
    from flask import request
    from flask import redirect
    from flask import url_for
except ImportError as e:
    print(e)
    print('Please install python3 flask: sudo pip3 install Flask')
    exit(-1)

__root_path = os.path.dirname(os.path.realpath(__file__))

'''The flask webservice app'''
app = Flask('Ingest',
            instance_path = __root_path,
            template_folder = os.path.join(__root_path, 'templates'),
            static_folder = os.path.join(__root_path, 'static'),
            instance_relative_config = True)

print(app.static_folder)

ingestrpc = None

@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    report = ingestrpc.getStatusReport()

    def compare_func(a, b):
        if a[1]['priority'] != b[1]['priority']:
            return int(b[1]['priority']) - int(a[1]['priority'])

        if a[1]['jobs']['running'] != b[1]['jobs']['running']:
            return int(b[1]['jobs']['running']) - int(a[1]['jobs']['running'])

        if a[1]['jobs']['to_do'] != b[1]['jobs']['to_do']:
            return int(b[1]['jobs']['to_do']) - int(a[1]['jobs']['to_do'])

        if a[0] < b[0]:
            return -1

        if a[0] > b[0]:
            return 1

        return 0

    sorted_items = sorted(list(report.items()), key=cmp_to_key(compare_func))

    nr_of_jobs_in_queue = 0
    for status_dict in list(report.values()):
        nr_of_jobs_in_queue += status_dict['jobs']['to_do']
        nr_of_jobs_in_queue += status_dict['jobs']['scheduled']
        nr_of_jobs_in_queue += status_dict['jobs']['retry']

    body = '''<p style="max-width: 1400px; margin: auto; margin-bottom: 12px; text-align: right;">Help and monitoring: <a href="https://www.astron.nl/lofarwiki/doku.php?id=engineering:software:ingest_services#faq_support" target=_blank>Ingest FAQ</a> / <a href="https://proxy.lofar.eu/zabbix/screens.php?sid=3ffcb45c82da9d9d&form_refresh=1&fullscreen=0&elementid=25&groupid=0&hostid=0" target=_blank>Zabbix ingest network transfer speeds</a> / <a href="https://lofar.astron.nl/birt-viewer/frameset?__report=Ingest.rptdesign&sample=my+parameter" target=_blank>MoM BIRT view of exports</a> / <a href="http://web.grid.sara.nl/cgi-bin/lofar.py" target=_blank>SARA maintenance</a> / <a href="http://scu001.control.lofar:9632/" target=_blank>LTA storage overview</a></p>'''

    body += '''<p style="max-width: 1400px; margin: auto; margin-bottom: 8px; font-size: 16px; font-weight: bold">Total #jobs waiting in queue: %s</p>''' % nr_of_jobs_in_queue
    body += '''<table>'''
    body += '''<tr><th>Export ID</th><th>Project</th><th>priority</th><th># to do</th><th># scheduled</th><th># running</th><th># retry</th><th># failed</th><th># finished</th><th># total</th><th>submitter(s)</th><th>LTA site</th><th>Remove</th></tr>'''
    for export_id, status_dict in sorted_items:
        priority_form = '''<div>%s <form method="post" action="update_priority">
                                   <input type="hidden" name="export_id" value="%s"></input>
                                   <button type="submit" name="priority" value="%s">+</button>
                               </form>
                               <form method="post" action="update_priority">
                                   <input type="hidden" name="export_id" value="%s"></input>
                                   <button type="submit" name="priority" value="%s">-</button>
                               </form>
                           </div>''' % (status_dict['priority'],
                                        export_id,
                                        status_dict['priority'] + 1,
                                        export_id,
                                        status_dict['priority'] - 1)

        remove_form = '''<form method="post" action="remove_export_job">
                            <button type="submit" name="export_id" value="%s" class="remove-button"></button>
                         </form>
                         ''' % (export_id,)

        body += '''<tr><td class="td-center">%s</td><td class="td-left">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="td-left">%s</td><td class="td-left">%s</td><td class="td-center">%s</td></tr>''' % (
            export_id,
            ', '.join(status_dict.get('projects', ['-'])),
            priority_form,
            status_dict['jobs']['to_do'],
            status_dict['jobs']['scheduled'],
            status_dict['jobs']['running'],
            status_dict['jobs']['retry'],
            status_dict['jobs']['failed'],
            status_dict['jobs']['finished'],
            sum(status_dict['jobs'].values()),
            '; '.join(status_dict.get('submitters', ['-'])),
            ', '.join(status_dict.get('lta_sites', ['-'])),
            remove_form)

    body += '''<tfoot><tr><td>Totals</td><td></td><td></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td></td><td></td><td></td></tr><tfoot>''' % (
        sum([x['jobs']['to_do'] for x in list(report.values())]),
        sum([x['jobs']['scheduled'] for x in list(report.values())]),
        sum([x['jobs']['running'] for x in list(report.values())]),
        sum([x['jobs']['retry'] for x in list(report.values())]),
        sum([x['jobs']['failed'] for x in list(report.values())]),
        sum([x['jobs']['finished'] for x in list(report.values())]),
        sum([sum(x['jobs'].values()) for x in list(report.values())]))

    body += '''</table>'''
    body += '''<p style="max-width: 1400px; margin: auto; margin-bottom: 8px;">Priority 0=paused, 1=lowest ... 9=highest</p>'''

    all_running_jobs_series_data = ''
    all_finished_jobs_series_data = ''

    # all_running_jobs_timestamps = []
    # for export_id, status_dict in report.items():
        # if 'series' in status_dict:
            # running_jobs_series = status_dict['series'].get('running_jobs')
            # if running_jobs_series and running_jobs_series['timestamps']:
                # all_running_jobs_timestamps += running_jobs_series['timestamps']

    # #get sorted list of unique timestamps
    # all_running_jobs_timestamps = sorted(list(set(all_running_jobs_timestamps)))
    # epoch = datetime.fromtimestamp(0)

    # for export_id, status_dict in report.items():
        # if 'series' in status_dict:
            # running_jobs_series = status_dict['series'].get('running_jobs')
            # if running_jobs_series and running_jobs_series['timestamps']:
                # #stacked area charts in highcharts need to have the same x-values
                # #zero-order interpolate this series timestamps/values
                # #and map it on the all_timestamps x-values
                # tv_dict = {t:v for t,v in zip(running_jobs_series['timestamps'], running_jobs_series['values'])}
                # data = []
                # prev_value = 0
                # for t in all_running_jobs_timestamps:
                    # if t in tv_dict:
                        # value = tv_dict[t]
                        # data.append('[%s,%s]' % (int(1000*totalSeconds(t-epoch)),value))
                        # prev_value = value
                    # else:
                        # data.append('[%s,%s]' % (int(1000*totalSeconds(t-epoch)),prev_value))

                # data = ','.join(data)
                # series = '''{name:'%s', data:[%s]}''' % (export_id, data)
                # all_running_jobs_series_data += series + ', '

            # finished_jobs_series = status_dict['series'].get('finished_jobs')
            # if finished_jobs_series and finished_jobs_series['timestamps']:
                # total_num_jobs = sum(status_dict['jobs'].values())

                # data = []
                # for t,v in zip(finished_jobs_series['timestamps'], finished_jobs_series['values']):
                    # data.append('[%s,%s]' % (int(1000*totalSeconds(t-epoch)), 100.0*v/total_num_jobs))

                # data = ','.join(data)
                # series = '''{name:'%s', data:[%s]}''' % (export_id, data)
                # all_finished_jobs_series_data += series + ', '

    return ''' <!DOCTYPE html>
<html>
<head>
  <title>Ingest Job Queue Monitor</title>
  <meta http-equiv="refresh" content="60">
  <script type="text/javascript" src="/static/js/jquery.min.js"></script>
  <script type="text/javascript" src="/static/js/highcharts.js"></script>
  <style>
    body {
        font-family: lucida console;
        font-size: 12px;
    }
    table {
        border-collapse: collapse;
        width: 100%%;
        max-width: 1400px;
        margin-left: auto;
        margin-right: auto;
    }
    td, th {
        border: 1px solid #dddddd;
        text-align: right;
        padding: 8px;
    }
    tr:nth-child(even) {
        background-color: #eeeeee;
    }
    th, tfoot {
        background-color: #aaaaaa;
    }
    th {
        text-align: center;
    }
    button, input, form {
        display:inline-block;
        border-width: 2px;
        width: 24px;
        height: 24px;
    }
    .remove-button {
        padding: 4px;
        background-image: url(data:image/svg+xml;utf8;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pgo8IS0tIEdlbmVyYXRvcjogQWRvYmUgSWxsdXN0cmF0b3IgMTkuMC4wLCBTVkcgRXhwb3J0IFBsdWctSW4gLiBTVkcgVmVyc2lvbjogNi4wMCBCdWlsZCAwKSAgLS0+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeD0iMHB4IiB5PSIwcHgiIHZpZXdCb3g9IjAgMCA0NDMgNDQzIiBzdHlsZT0iZW5hYmxlLWJhY2tncm91bmQ6bmV3IDAgMCA0NDMgNDQzOyIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgd2lkdGg9IjE2cHgiIGhlaWdodD0iMTZweCI+CjxnPgoJPHJlY3QgeD0iNjEuNzg1IiB5PSIxMjgiIHdpZHRoPSI2MCIgaGVpZ2h0PSIyOTAiIGZpbGw9IiMwMDAwMDAiLz4KCTxwYXRoIGQ9Ik0yMTEuNzg1LDI1MC42NVYxMjhoLTYwdjI5MGg0NC4xNzJjLTE0Ljg2MS0yMS4wNjctMjMuNjAyLTQ2Ljc0Ni0yMy42MDItNzQuNDMgICBDMTcyLjM1NiwzMDcuMTQ1LDE4Ny40ODYsMjc0LjE5MywyMTEuNzg1LDI1MC42NXoiIGZpbGw9IiMwMDAwMDAiLz4KCTxwYXRoIGQ9Ik0zMDEuNzg1LDIxNC4xNDFsMC04Ni4xNDFoLTYwdjEwMC45MThDMjU5LjczMSwyMTkuNDg4LDI4MC4xNDQsMjE0LjE0MSwzMDEuNzg1LDIxNC4xNDF6IiBmaWxsPSIjMDAwMDAwIi8+Cgk8cGF0aCBkPSJNMzIxLjc4NSwzOGgtODMuMzg0VjBIMTI1LjE2OXYzOEg0MS43ODV2NjBoMjgwVjM4eiBNMTU1LjE2OSwzMGg1My4yMzJ2OGgtNTMuMjMyVjMweiIgZmlsbD0iIzAwMDAwMCIvPgoJPHBhdGggZD0iTTMwMS43ODUsMjQ0LjE0MWMtNTQuODI2LDAtOTkuNDI5LDQ0LjYwNC05OS40MjksOTkuNDI5UzI0Ni45NTksNDQzLDMwMS43ODUsNDQzczk5LjQzLTQ0LjYwNCw5OS40My05OS40MyAgIFMzNTYuNjExLDI0NC4xNDEsMzAxLjc4NSwyNDQuMTQxeiBNMzU1Ljk2MSwzNzYuNTMzbC0yMS4yMTMsMjEuMjEzbC0zMi45NjMtMzIuOTYzbC0zMi45NjMsMzIuOTYzbC0yMS4yMTMtMjEuMjEzbDMyLjk2My0zMi45NjMgICBsLTMyLjk2My0zMi45NjNsMjEuMjEzLTIxLjIxM2wzMi45NjMsMzIuOTYzbDMyLjk2My0zMi45NjNsMjEuMjEzLDIxLjIxM2wtMzIuOTYzLDMyLjk2M0wzNTUuOTYxLDM3Ni41MzN6IiBmaWxsPSIjMDAwMDAwIi8+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPGc+CjwvZz4KPC9zdmc+Cg==);
        background-repeat: no-repeat;
        background-position: center center;
    }
    .td-center {
        text-align: center;
    }
    .td-left {
        text-align: left;
    }
  </style>
</head>
<body>
%s

<!--
<div id="running_jobs_chart" style="min-width: 310px; max-width: 1400px; height: 400px; margin: 0 auto; padding-top: 10px;"></div>
<div id="finished_jobs_chart" style="min-width: 310px; max-width: 1400px; height: 400px; margin: 0 auto; padding-top: 10px;"></div>
<script>
    $(function () {
        $('#running_jobs_chart').highcharts({
            chart: {
                type: 'area'
            },
            title: {
                text: 'Running jobs'
            },
            xAxis: {
                type: 'datetime',
                title: {
                    text: 'time'
                }
            },
            yAxis: {
                title: {
                    text: '#jobs'
                },
            },
            plotOptions: {
                area: {
                    stacking: 'normal',
                    step: 'left',
                    lineColor: '#666666',
                    lineWidth: 1,
                    marker: {
                        enabled: false
                    }
                }
            },
            series: [%s]
        });

        $('#finished_jobs_chart').highcharts({
            chart: {
                type: 'line'
            },
            title: {
                text: 'Progress'
            },
            xAxis: {
                type: 'datetime',
                title: {
                    text: 'time'
                }
            },
            yAxis: {
                title: {
                    text: 'percentage done'
                },
                min: 0,
                max: 100,
            },
            plotOptions: {
                line: {
                    step: 'left',
                    lineWidth: 2,
                    marker: {
                        enabled: false
                    }
                }
            },
            series: [%s]
        });
    });
</script>
-->
</body>
</html>
''' % (body, all_running_jobs_series_data, all_finished_jobs_series_data)

@app.route('/update_priority', methods = ['POST'])
def update_priority():
    try:
        ingestrpc.setExportJobPriority(request.form['export_id'], request.form['priority'])
    except Exception as e:
        logger.error(e)
    return redirect(url_for('index'), code = 302)

@app.route('/remove_export_job', methods = ['POST'])
def remove_export_job():
    try:
        ingestrpc.removeExportJob(request.form['export_id'])
    except Exception as e:
        logger.error(e)
    return redirect(url_for('index'), code = 302)

def main():
    # make sure we run in UTC timezone
    import os
    os.environ['TZ'] = 'UTC'

    from optparse import OptionParser

    # Check the invocation arguments
    parser = OptionParser('%prog [options]',
                          description = 'run the ingest web server')
    parser.add_option('-p', '--port', dest = 'port', type = 'int', default = 9632, help = 'port number on which to host the webserver, default: %default')
    parser.add_option('-b', '--broker', dest = 'broker', type = 'string', default = DEFAULT_BROKER, help = 'Address of the broker, default: %default')
    parser.add_option('-e', '--exchange', dest = 'exchange', type = 'string', default = DEFAULT_BUSNAME, help = 'Name of the bus exchange on the broker, default: %s' % DEFAULT_BUSNAME)
    (options, args) = parser.parse_args()

    logging.basicConfig(format = '%(asctime)s %(levelname)s %(message)s',
                        level = logging.INFO)

    global ingestrpc
    ingestrpc = IngestRPC.create(exchange = options.exchange, broker = options.broker)

    with ingestrpc:
        app.run(debug = isDevelopmentEnvironment(), threaded = True, host = '0.0.0.0', port = options.port)

if __name__ == '__main__':
    main()
