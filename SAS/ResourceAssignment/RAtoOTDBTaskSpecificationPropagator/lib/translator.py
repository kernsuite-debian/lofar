#!/usr/bin/env python3

# Copyright (C) 2015-2017
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: resource_assigner.py 1580 2015-09-30 14:18:57Z loose $

"""
RAtoOTDBTaskSpecificationPropagator gets a task to be scheduled in OTDB,
reads the info from the RA DB and sends it to OTDB in the correct format.
"""

import logging
import pprint
from lofar.common.util import to_csv_string
from math import ceil, floor

from lofar.common import isProductionEnvironment, isTestEnvironment

#from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)

""" Prefix that is common to all parset keys, depending on the exact source. """
PREFIX="LOFAR.ObsSW.Observation."
##TODO use this.

class RAtoOTDBTranslator():
    def __init__(self):
        """
        RAtoOTDBTranslator translates values from the RADB into parset keys to be stored in an OTDB Tree
        """

    def getCep4LocationTestEnvPrefix(self):
        if isProductionEnvironment():
            return ''

        if isTestEnvironment():
            return 'test-'

        return 'dev-'

    def cep4DataPath(self, project_name, otdb_id):
        ''' Return the CEP4:path to the data dir on CEP4, depending on environment.
            "CEP4" is to be overwritten by a real storage hostname selected by slurm.
        '''
        return "CEP4:/data/%sprojects/%s/L%s" % (self.getCep4LocationTestEnvPrefix(), project_name, otdb_id)

    def dragnetDataPath(self, otdb_id, resource_name):
        ''' Return the hostname:path to the data dir on DRAGNET, depending on environment.
        '''
        if resource_name.startswith('drg'):
            host = resource_name[0 : 5] + '-ib.dragnet.infiniband.lofar'  # e.g. 'drg08-ib.[...]'
            dirname = resource_name[-5 : ]  # 'data1', 'data2', ...
            if not dirname.startswith('data'):
                # bug or test: log error & try as requested is best in both cases
                logger.error('dragnetDataPath: unexpected resource_name: %s', resource_name)

        elif resource_name.startswith('dragproc'):
            host = 'dragproc-10g.online.lofar'
            dirname = 'data'

        else:
            raise ValueError('dragnetDataPath: not a DRAGNET resource_name: %s' % resource_name)

        if not isProductionEnvironment():
            dirname += '/test'  # easy to identify, du(1) and auto-delete

        return '%s:/%s/L%s' % (host, dirname, otdb_id)

    def locationPath(self, cluster, project_name, otdb_id, resource_name):
        ''' Return 'host:path' depending on environment for storage resource
            'resource_name' on cluster 'cluster'.
        '''
        if cluster == 'CEP4':
            return self.cep4DataPath(project_name, otdb_id)
        if cluster == 'DRAGNET':
            return self.dragnetDataPath(otdb_id, resource_name)

        raise ValueError('locationPath: unknown cluster to determine storage locations for parset')

    def CreateCorrelated(self, storage_property_list, cluster, project_name, io_type):
        result = {}

        # Split storage_property_list in items wrt observation and wrt pipeline.
        total_nr_files = 0
        obs_max_uv_sap_nr = -1
        obs_next_sb_nrs_per_sap = []
        obs_locations = [None] * 1024  # the easy way and 1024 is enough even in 4 bit mode
        obs_filenames = [None] * 1024  # idem
        obs_skip = []
        pipeline_storage_props = []

        for prop in storage_property_list:
            if 'saps' not in prop:  ## It's a pipeline (no SAPs)
                pipeline_storage_props.append(prop)
                continue

            ## It's an observation (or pipeline input from an observation)
            for sap in prop['saps']:
                if 'nr_of_uv_files' not in sap['properties'] or sap['properties']['nr_of_uv_files'] < 1:
                    continue
                sap_nr = sap['sap_nr']
                if sap_nr > obs_max_uv_sap_nr:
                    added_sap_nrs = sap_nr - obs_max_uv_sap_nr  # assumes obs_max_uv_sap_nr: init to -1
                    obs_max_uv_sap_nr = sap_nr
                    obs_next_sb_nrs_per_sap.extend([-1] * added_sap_nrs)

                if obs_next_sb_nrs_per_sap[sap_nr] == -1:  # be robust to out of order sap nrs
                    obs_next_sb_nrs_per_sap[sap_nr] = sap['properties']['start_sb_nr']

                otdb_id = sap['properties']['uv_otdb_id']

                next_sb_nr = obs_next_sb_nrs_per_sap[sap_nr]
                for sb_nr in range(next_sb_nr, next_sb_nr + sap['properties']['nr_of_uv_files']):
                    obs_locations[sb_nr] = self.locationPath(cluster, project_name, otdb_id,
                                                             prop['resource_name']) + '/uv'
                    obs_filenames[sb_nr] = "L%d_SAP%03d_SB%03d_uv.MS" % (otdb_id, sap_nr, sb_nr)
                    obs_skip.append("0")  # what's this for?
                    total_nr_files += 1
                obs_next_sb_nrs_per_sap[sap_nr] = sb_nr + 1

        if obs_max_uv_sap_nr >= 0:
            assert total_nr_files != 0, 'CreateCorrelated: skipping obs parset filenames: total_nr_files = %d' % total_nr_files
            logger.info('CreateCorrelated: total_nr_files = %d', total_nr_files)

            obs_locations = [loc for loc in obs_locations if loc is not None]  # strip unused init values
            obs_filenames = [fn  for fn  in obs_filenames if fn  is not None]  # idem
            if len(obs_locations) != total_nr_files or len(obs_filenames) != total_nr_files:
                # If the total nr_of_uv_files in a SAP does not correspond to the start_sb_nr
                # props of this and the next SAP, entries have been overwritten. Bail in that case.
                logger.error('CreateCorrelated: skipping obs parset filenames: len(obs_locations) = %d and/or len(obs_filenames) = %d not equal to total_nr_files = %d',
                             len(obs_locations), len(obs_filenames), total_nr_files)
                raise ValueError('CreateCorrelated: skipping obs parset filenames: unexpected nr of locations and/or filenames vs total_nr_files')

            result[PREFIX + 'DataProducts.%s_Correlated.locations' % (io_type)] = '[' + to_csv_string(obs_locations) + ']'
            result[PREFIX + 'DataProducts.%s_Correlated.filenames' % (io_type)] = '[' + to_csv_string(obs_filenames) + ']'
            result[PREFIX + 'DataProducts.%s_Correlated.skip' % (io_type)]      = '[' + to_csv_string(obs_skip) + ']'


        # Pipeline (output, or input from another pipeline)
        locations = []
        filenames = []
        skip      = []
        sb_nr = 0

        for prop in pipeline_storage_props:
            if 'nr_of_uv_files' not in prop:
                continue
            if 'start_sb_nr' in prop:
                sb_nr = prop['start_sb_nr']
                filename_template = "L%d_SB%03d_uv.MS"
            elif 'start_sbg_nr' in prop: #Right now we're assuming this doesn't happen on raw data!
                sb_nr = prop['start_sbg_nr']
                filename_template = "L%d_SBG%03d_uv.MS"

            otdb_id = prop['uv_otdb_id']
            for _ in range(prop['nr_of_uv_files']):
                locations.append(self.locationPath(cluster, project_name, otdb_id,
                                                   prop['resource_name']) + '/uv')
                filenames.append(filename_template % (otdb_id, sb_nr))
                skip.append("0")
                sb_nr += 1

        if sb_nr == 0:
            return result

        result[PREFIX + 'DataProducts.%s_Correlated.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_Correlated.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_Correlated.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreateCoherentStokes(self, storage_property_list, cluster, project_name, io_type):
        result = {}

        max_cs_sap_nr = -1
        total_nr_files = 0
        next_tab_part_nrs_per_sap = []  # subband list is per sap
        nr_parts_per_tab_per_sap = []
        is_tab_nrs_per_sap = []  # not all saps have an incoherent stokes ('is') tab
        locations_per_sap = []  # contains a list of tab parts per sap
        filenames_per_sap = []  # idem
        skip = []

        for prop in storage_property_list:
            if 'saps' not in prop:
                continue

            for sap in prop['saps']:
                if 'nr_of_cs_files' not in sap['properties'] or sap['properties']['nr_of_cs_files'] < 1:
                    continue
                sap_nr = sap['sap_nr']
                if sap_nr > max_cs_sap_nr:
                    added_sap_nrs = sap_nr - max_cs_sap_nr  # assumes max_cs_sap_nr init to -1
                    max_cs_sap_nr = sap_nr
                    next_tab_part_nrs_per_sap.extend([ 0] * added_sap_nrs)
                    nr_parts_per_tab_per_sap .extend([ 0] * added_sap_nrs)
                    is_tab_nrs_per_sap       .extend([-1] * added_sap_nrs)
                    locations_per_sap.extend([[]] * added_sap_nrs)  # list of tabs (each with parts) per sap
                    filenames_per_sap.extend([[]] * added_sap_nrs)  # idem

                if nr_parts_per_tab_per_sap[sap_nr] == 0:  # be robust to out of order sap nrs
                    nr_parts_per_tab_per_sap[sap_nr] = sap['properties']['nr_of_cs_parts']  # regardless of claim size
                if 'is_tab_nr' in sap['properties']:
                    is_tab_nrs_per_sap[sap_nr] = sap['properties']['is_tab_nr']

                otdb_id = sap['properties']['cs_otdb_id']

                # Stokes (IQUV/XXYY) always come together in a claim, but we must match COBALT's filename order,
                # which is parts within stokes. We don't yet know the total nr of files.
                # First, do stokes within parts, then later reorder when we have all names.
                # The tab nr dim must be and remain the outer dim, even though it's sliced from the parts dim.
                # NOTE: nr_cs_stokes must be the same in all SAPs with CS TABs, see reordering code below.
                nr_cs_stokes = sap['properties']['nr_of_cs_stokes']  # the 'cs_stokes' term here can also mean cv XXYY
                nr_parts = int(sap['properties']['nr_of_cs_files'] / nr_cs_stokes)  # in this prop's claim!
                nparts_tab = nr_parts_per_tab_per_sap[sap_nr]  # alias for readability; this is also per stokes
                while nr_parts > 0:
                    tab_nr      = int(next_tab_part_nrs_per_sap[sap_nr] / nparts_tab)
                    tab_part_nr = int(next_tab_part_nrs_per_sap[sap_nr] % nparts_tab)
                    nparts_remain = min(nr_parts, nparts_tab - tab_part_nr)  # nr parts left before we go to the next tab

                    if is_tab_nrs_per_sap[sap_nr] != -1 and tab_nr >= is_tab_nrs_per_sap[sap_nr]:
                        tab_nr += 1  # skip IS tab nr
                    for part_nr in range(tab_part_nr, tab_part_nr + nparts_remain):
                        for stokes_nr in range(nr_cs_stokes):
                            locations_per_sap[sap_nr].append(self.locationPath(cluster, project_name, otdb_id,
                                                                               prop['resource_name']) + '/cs')
                            filenames_per_sap[sap_nr].append("L%d_SAP%03d_B%03d_S%d_P%03d_bf.h5" % \
                                    (otdb_id, sap_nr, tab_nr, stokes_nr, part_nr))
                            skip.append("0")  # what's this for?

                    next_tab_part_nrs_per_sap[sap_nr] += nparts_remain
                    total_nr_files += nparts_remain * nr_cs_stokes
                    nr_parts -= nparts_remain

        if max_cs_sap_nr == -1:
            return result

        logger.info('CreateCoherentStokes: total_nr_files = %d', total_nr_files)

        # Reorder parts and stokes dims, then concat lists in locations_per_sap and in filenames_per_sap
        # NOTE: nr_cs_stokes is set in a SAP above. Though given per SAP, the reordering here assumes it is the same in all SAPs with CS TABs!
        locations2_per_sap = [[]] * len(locations_per_sap)
        filenames2_per_sap = [[]] * len(filenames_per_sap)
        for sap_nr in range(max_cs_sap_nr + 1):
            locations2_per_sap[sap_nr] = [None] * len(locations_per_sap[sap_nr])
            filenames2_per_sap[sap_nr] = [None] * len(filenames_per_sap[sap_nr])

            nr_parts = nr_parts_per_tab_per_sap[sap_nr]
            nr_tabs = int(len(locations_per_sap[sap_nr]) / (nr_cs_stokes * nr_parts))
            for tab_nr in range(nr_tabs):
                for part_nr in range(nr_parts):
                    for stokes_nr in range(nr_cs_stokes):
                        locations2_per_sap[sap_nr][tab_nr * nr_parts * nr_cs_stokes + stokes_nr * nr_parts + part_nr] = \
                         locations_per_sap[sap_nr][tab_nr * nr_parts * nr_cs_stokes + part_nr * nr_cs_stokes + stokes_nr]
                        filenames2_per_sap[sap_nr][tab_nr * nr_parts * nr_cs_stokes + stokes_nr * nr_parts + part_nr] = \
                         filenames_per_sap[sap_nr][tab_nr * nr_parts * nr_cs_stokes + part_nr * nr_cs_stokes + stokes_nr]
     
        locations = []
        filenames = []
        for i in range(len(locations_per_sap)):
            locations.extend(locations2_per_sap[i])
            filenames.extend(filenames2_per_sap[i])

        if None in locations:
            logger.error('CreateCoherentStokes: None in locations = %s', locations)
        if None in filenames:
            logger.error('CreateCoherentStokes: None in filenames = %s', filenames)
        assert None not in locations and None not in filenames, 'CreateCoherentStokes: skipping obs parset filenames: None in locations and/or filenames'

        result[PREFIX + 'DataProducts.%s_CoherentStokes.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_CoherentStokes.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_CoherentStokes.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreateIncoherentStokes(self, storage_property_list, cluster, project_name, io_type):
        result = {}

        max_is_sap_nr = -1
        total_nr_files = 0
        next_tab_part_nrs_per_sap = []  # subband list is per sap
        locations_per_sap = []  # contains a list of tab parts per sap; there can be max 1 IS tab per SAP
        filenames_per_sap = []  # idem
        skip = []

        for prop in storage_property_list:
            if 'saps' not in prop:
                continue

            for sap in prop['saps']:
                if 'nr_of_is_files' not in sap['properties'] or sap['properties']['nr_of_is_files'] < 1:
                    continue
                sap_nr = sap['sap_nr']
                if sap_nr > max_is_sap_nr:
                    added_sap_nrs = sap_nr - max_is_sap_nr  # assumes max_is_sap_nr init to -1
                    max_is_sap_nr = sap_nr
                    next_tab_part_nrs_per_sap.extend([0] * added_sap_nrs)
                    locations_per_sap.extend([[]] * added_sap_nrs)  # list of parts per sap (max 1 IS tab per sap)
                    filenames_per_sap.extend([[]] * added_sap_nrs)  # idem

                otdb_id = sap['properties']['is_otdb_id']

                # Stokes (IQUV) always come together in a claim, but we must match COBALT's filename order,
                # which is parts within stokes. We don't yet know the total nr of files.
                # First, do stokes within parts, then later reorder when we have all names.
                # NOTE: nr_is_stokes must be the same in all SAPs with an IS TAB, see reordering code below.
                nr_is_stokes = int(sap['properties']['nr_of_is_stokes'])
                nr_parts = int(sap['properties']['nr_of_is_files'] / nr_is_stokes)  # in this prop's claim!
                next_part_nr = next_tab_part_nrs_per_sap[sap_nr]
                for part_nr in range(next_part_nr, next_part_nr + nr_parts):
                    for stokes_nr in range(nr_is_stokes):
                        locations_per_sap[sap_nr].append(self.locationPath(cluster, project_name, otdb_id,
                                                                           prop['resource_name']) + '/is')
                        filenames_per_sap[sap_nr].append("L%d_SAP%03d_B%03d_S%d_P%03d_bf.h5" % \
                                (otdb_id, sap_nr, sap['properties']['is_tab_nr'], stokes_nr, part_nr))
                        skip.append("0")  # what's this for?
                next_tab_part_nrs_per_sap[sap_nr] += nr_parts
                total_nr_files += nr_parts * nr_is_stokes

        if max_is_sap_nr == -1:
            return result

        logger.info('CreateIncoherentStokes: total_nr_files = %d', total_nr_files)

        # Concat lists in locations_per_sap and in filenames_per_sap, and reorder parts and stokes dims.
        # NOTE: nr_is_stokes is set in a SAP above. Though given per SAP, the reordering here assumes it is the same in all SAPs with an IS TAB!
        locations = [None] * total_nr_files
        filenames = [None] * total_nr_files
        file_nr = 0
        for sap_nr in range(max_is_sap_nr + 1):
            nr_parts = next_tab_part_nrs_per_sap[sap_nr]
            for part_nr in range(nr_parts):
                for stokes_nr in range(nr_is_stokes):
                    locations[file_nr + stokes_nr * nr_parts + part_nr] = locations_per_sap[sap_nr][nr_is_stokes * part_nr + stokes_nr]
                    filenames[file_nr + stokes_nr * nr_parts + part_nr] = filenames_per_sap[sap_nr][nr_is_stokes * part_nr + stokes_nr]
            file_nr += nr_parts * nr_is_stokes

        if None in locations:
            logger.error('CreateIncoherentStokes: None in locations = %s', locations)
        if None in filenames:
            logger.error('CreateIncoherentStokes: None in filenames = %s', filenames)
        assert None not in locations and None not in filenames, 'CreateIncoherentStokes: skipping obs parset filenames: None in locations and/or filenames'

        result[PREFIX + 'DataProducts.%s_IncoherentStokes.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_IncoherentStokes.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_IncoherentStokes.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreateInstrumentModel(self, storage_property_list, cluster, project_name, io_type, sb_nr = 0):
        locations = []
        filenames = []
        skip      = []
        result = {}

        for prop in storage_property_list:
            if 'nr_of_im_files' not in prop:
                continue
            if 'start_sb_nr' in prop:
                sb_nr = prop['start_sb_nr']

            otdb_id = prop['im_otdb_id']
            for _ in range(prop['nr_of_im_files']):
                locations.append(self.locationPath(cluster, project_name, otdb_id,
                                                   prop['resource_name']) + '/im')
                filenames.append("L%d_SB%03d_inst.INST" % (otdb_id, sb_nr))
                skip.append("0")
                sb_nr += 1

        if not locations:
            return result

        result[PREFIX + 'DataProducts.%s_InstrumentModel.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_InstrumentModel.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_InstrumentModel.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreateSkyImage(self, storage_property_list, cluster, project_name, io_type):
        sbg_nr = 0
        locations = []
        filenames = []
        skip      = []
        result = {}

        for prop in storage_property_list:
            if 'nr_of_img_files' not in prop:
                continue

            otdb_id = prop['img_otdb_id']
            for _ in range(prop['nr_of_img_files']):
                locations.append(self.locationPath(cluster, project_name, otdb_id,
                                                   prop['resource_name']) + '/img')
                filenames.append("L%d_SBG%03d_sky.IM" % (otdb_id, sbg_nr))
                skip.append("0")
                sbg_nr += 1

        if not locations:
            return result

        result[PREFIX + 'DataProducts.%s_SkyImage.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_SkyImage.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_SkyImage.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreatePulsarPipeline(self, storage_property_list, cluster, project_name, io_type):
        p_nr = 0
        locations = []
        filenames = []
        skip      = []
        result = {}

        for prop in storage_property_list:
            if 'nr_of_pulp_files' not in prop:
                continue

            otdb_id = prop['pulp_otdb_id']
            for _ in range(prop['nr_of_pulp_files']):
                locations.append(self.locationPath(cluster, project_name, otdb_id,
                                                   prop['resource_name']) + '/pulp')
                filenames.append("L%d_P%03d_pulp.tgz" % (otdb_id, p_nr))
                skip.append("0")
                p_nr += 1

        if not locations:
            return result

        result[PREFIX + 'DataProducts.%s_Pulsar.locations' % (io_type)] = '[' + to_csv_string(locations) + ']'
        result[PREFIX + 'DataProducts.%s_Pulsar.filenames' % (io_type)] = '[' + to_csv_string(filenames) + ']'
        result[PREFIX + 'DataProducts.%s_Pulsar.skip' % (io_type)]      = '[' + to_csv_string(skip) + ']'
        return result

    def CreateStorageKeys(self, storage_property_list, cluster, project_name, io_type):
        result = {}

        result.update(self.CreateCorrelated      (storage_property_list, cluster, project_name, io_type))
        result.update(self.CreateCoherentStokes  (storage_property_list, cluster, project_name, io_type))
        result.update(self.CreateIncoherentStokes(storage_property_list, cluster, project_name, io_type))
        result.update(self.CreateInstrumentModel (storage_property_list, cluster, project_name, io_type))
        result.update(self.CreateSkyImage        (storage_property_list, cluster, project_name, io_type))
        result.update(self.CreatePulsarPipeline  (storage_property_list, cluster, project_name, io_type))

        return result

    def ProcessStorageInfo(self, otdb_id, storage_info, cluster, project_name):
        logging.info('processing the storage for %i' % (otdb_id))

        parset_dict =      self.CreateStorageKeys(storage_info['input'],  cluster, project_name, "Input")
        parset_dict.update(self.CreateStorageKeys(storage_info['output'], cluster, project_name, "Output"))

        return parset_dict

    def CreateParset(self, otdb_id, ra_info, project_name, mom_info):
        """
        :param mom_info: Specification object
        """
        logger.info('CreateParset for %s' % (otdb_id,))

        parset = {}
        #parset[PREFIX+'momID'] = str(mom_id)
        if ra_info:
            logger.info('start=%s, end=%s' % (ra_info['starttime'], ra_info['endtime']))
            parset[PREFIX+'startTime'] = ra_info['starttime'].strftime('%Y-%m-%d %H:%M:%S')
            parset[PREFIX+'stopTime'] = ra_info['endtime'].strftime('%Y-%m-%d %H:%M:%S')

            # Station resources are dealt with as follows:
            #   * Station list: This is part of the specification, so already in OTDB. The RA only checks for conflicts.
            #   * Data slots: Stations & Cobalt derive a default data-slot mapping, so no need to specify one until Cobalt
            #                 can read data from the same antenna field for multiple observations (=the use case for data
            #                 slots).
            # Cobalt resources are dealt with as follows:
            #   * Cobalt.blockSize is part of the specification.
            #   * Cobalt resources are not modelled and allocated, so the defaults (cbt001-8) will be used.

            if 'storage' in ra_info:
                logging.info("Adding storage claims to parset\n" + pprint.pformat(ra_info['storage']))
                parset.update(self.ProcessStorageInfo(otdb_id, ra_info['storage'], ra_info['cluster'], project_name))

            if ra_info['type'] == 'observation':
                # Atm, the observation inspection plots start script are CEP4-specific,
                # and the results are expected to be posted from a single cluster (i.e. CEP4).
                # (Inspection plots from station subband stats are independent from this and always avail.)
                if any(key.endswith('.locations') and 'CEP4:' in val for key, val in list(parset.items())):
                    logging.info("CreateParset: Adding inspection plot commands to parset")
                    parset[PREFIX+'ObservationControl.OnlineControl.inspectionHost'] = 'head01.cep4.control.lofar'
                    parset[PREFIX+'ObservationControl.OnlineControl.inspectionProgram'] = 'inspection-plots-observation.sh'

                #special case for dynspec projects for Richard Fallows
                ## JK: you know, we had someone entering 'special cases' like this based on pulsar names in the GLOW
                ## control software, giving everyone a puzzled expression on their face and a big headache when figuring
                ## out why the system was sometimes behaving so funny...
                # FIXME: please find a better way to do this or remove this hack when not necessary any more!
                if project_name in ['IPS_Commissioning', 'LC6_001', 'LC7_001', 'LC8_001', 'LC9_001', 'LT10_001', 'LT10_002', 'LT10_006']:
                    logging.info("CreateParset: Overwriting inspectionProgram parset key for dynspec")
                    parset[PREFIX+'ObservationControl.OnlineControl.inspectionProgram'] = '/data/home/lofarsys/dynspec/scripts/inspection-dynspec-observation.sh'

        # Everything else gets added though the mom-otdb-adapter, this is only here to not have to change the code
        # in the "no longer maintained" MoM and mom-otdb-adapter
        storagemanager = mom_info.storagemanager
        if storagemanager is not None: # should be "" or "dysco"
            logging.info("Adding storagemanager to parset: %s" % storagemanager)
            parset[PREFIX+"ObservationControl.PythonControl.DPPP.msout.storagemanager.name"] = storagemanager

        return parset
