# Copyright (C) 2018 ASTRON (Netherlands Institute for Radio Astronomy)
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

from lofar.lta.ltastorageoverview import store
from lofar.lta.ingest.common.srm import *
from lofar.lta.ingest.client.ingestbuslistener import IngestEventMesssageBusListener, IngestEventMessageHandler
from lofar.messaging import DEFAULT_BROKER, DEFAULT_BUSNAME

import logging
logger = logging.getLogger(__name__)

class LTASOIngestEventHandler(IngestEventMessageHandler):
    def __init__(self, dbcreds):
        self._dbcreds = dbcreds
        super().__init__(log_subject_filters=("JobFinished", "TaskFinished"))

    def onJobFinished(self, job_dict):
        """onJobFinished is called upon receiving a JobFinished message.
        In this LTASOIngestEventHandler, it calls _schedule_srmurl_for_visit to schedule the finished surl for a scraper visit.
        :param job_dict: dictionary with the finised job"""
        self._schedule_srmurl_for_visit(job_dict.get('srm_url'))

    def onTaskFinished(self, task_dict):
        """onTaskFinished is called upon receiving a TaskFinished message. (when all dataproducts of a observation/pipeline were ingested)
        In this LTASOIngestEventHandler, it calls _schedule_srmurl_for_visit to schedule the finished surl for a scraper visit.
        :param task_dict: dictionary with the finished task"""
        self._schedule_srmurl_for_visit(task_dict.get('srm_url'))

    def _schedule_srmurl_for_visit(self, srm_url):
        """process the given srm_url, insert it in the db if needed, and mark it as not visited,
        so that the scraper will visit it soon.
        :param srm_url: a valid srm url like: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
        :return: None
        """
        if srm_url:
            with store.LTAStorageDb(self._dbcreds) as db:
                site = self._get_site_from_db(srm_url)
                dir_path = get_dir_path_in_site(srm_url)
                directory = db.directoryByName(dir_path, site['id'])

                if directory is None:
                    dir_id = self._insert_missing_directory_tree_if_needed(srm_url).get(dir_path)
                else:
                    dir_id = directory.get('dir_id')

                if dir_id is not None:
                    self._mark_directory_for_a_visit(dir_id)

    def _mark_directory_for_a_visit(self, dir_id):
        """
        update the directory's last visit time to unix-epoch (which is the lowest possible visit timestamp), so that it
        appears in the visitStats which are used by the scraper to determine the next directory to be visited.
        :param int dir_id: the id of the directory
        :return: None
        """
        with store.LTAStorageDb(self._dbcreds) as db:
            return db.updateDirectoryLastVisitTime(dir_id, datetime.fromtimestamp(0))

    def _get_site_from_db(self, srm_url):
        """
        find the site entry in the database for the given srm_url.
        raises a lookup error if not found.
        :param string srm_url: a valid srm url
        :return: a site entry dict from the database
        """
        site_url = get_site_surl(srm_url)

        # find site in db
        with store.LTAStorageDb(self._dbcreds) as db:
            site = next((s for s in db.sites() if s['url'] == site_url), None)
            if site is None:
                raise LookupError('Could not find site %s in database %s' % (site_url, self._dbcreds.database))
            return site

    def _insert_missing_directory_tree_if_needed(self, srm_url):
        # example url: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884/L652884_SAP000_B000_P001_bf_e619e5da.tar
        # or for a dir: srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
        # site_url then becomes: srm://lofar-srm.fz-juelich.de:8443
        # dir_path then becomes: /pnfs/fz-juelich.de/data/lofar/ops/projects/lc8_029/652884
        site = self._get_site_from_db(srm_url)
        dir_path = get_dir_path_in_site(srm_url)

        with store.LTAStorageDb(self._dbcreds) as db:
            return db.insert_missing_directory_tree_if_needed(dir_path, site['id'])
