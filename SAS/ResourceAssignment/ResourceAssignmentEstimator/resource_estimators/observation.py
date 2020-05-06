# observation.py
#
# Copyright (C) 2016-2017
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
# $Id$

import logging
import pprint
from math import ceil
from .base_resource_estimator import BaseResourceEstimator
from lofar.stationmodel.antennasets_parser import AntennaSetsParser

logger = logging.getLogger(__name__)

DATAPRODUCTS = "Observation.DataProducts."
COBALT = "Observation.ObservationControl.OnlineControl.Cobalt."

class ObservationResourceEstimator(BaseResourceEstimator):
    """ ResourceEstimator for LOFAR Observations
    """
    def __init__(self):
        logger.info("init ObservationResourceEstimator")
        super(ObservationResourceEstimator, self).__init__(name='observation')
        self.required_keys = ('Observation.sampleClock',
                              'Observation.startTime',
                              'Observation.stopTime',
                              'Observation.antennaSet',
                              'Observation.nrBeams',
                              'Observation.Beam[0].subbandList',
                              'Observation.nrBitsPerSample',
                              'Observation.VirtualInstrument.stationList',
                              COBALT + 'Correlator.nrChannelsPerSubband',
                              COBALT + 'Correlator.integrationTime',
                              COBALT + 'BeamFormer.flysEye',
                              COBALT + 'BeamFormer.CoherentStokes.timeIntegrationFactor',
                              COBALT + 'BeamFormer.IncoherentStokes.timeIntegrationFactor',
                              'Observation.VirtualInstrument.stationList',
                              DATAPRODUCTS + 'Output_Correlated.enabled',
                              DATAPRODUCTS + 'Output_Correlated.identifications',
                              DATAPRODUCTS + 'Output_Correlated.storageClusterName',
                              DATAPRODUCTS + 'Output_CoherentStokes.enabled',
                              DATAPRODUCTS + 'Output_CoherentStokes.identifications',
                              DATAPRODUCTS + 'Output_CoherentStokes.storageClusterName',
                              COBALT + 'BeamFormer.CoherentStokes.which',
                              DATAPRODUCTS + 'Output_IncoherentStokes.enabled',
                              DATAPRODUCTS + 'Output_IncoherentStokes.identifications',
                              DATAPRODUCTS + 'Output_IncoherentStokes.storageClusterName',
                              COBALT + 'BeamFormer.IncoherentStokes.which'
                              )
        self.asp = AntennaSetsParser()

    def _calculate(self, parset, predecessor_estimates=[]):
        """ Calculate the resources needed by the different data product types that can be in a single observation.
            The predecessor_estimates argument is just to implement the same interface as pipelines. Observations have no predecessor.

            The following return value example is for an observation duration of 240.0 s and 3 data product types for 2 clusters.
            NOTE: 'nr_of_XX_files' is for that SAP estimate. The total is thus times the 'resource_count'.
                  'nr_of_cs_parts' is for a full CS TAB (per stokes component) in that SAP; not per estimate, which may still describe one part.

            See the calibration pipeline estimator for some explanation on why parts of this format are currently needed. It also has input_files.
        {
            'errors': [],
            'estimates': [{
                'resource_types': {'bandwidth': 35791395, 'storage': 1073741824},  # for each uv output data product (thus the total is times the resource_count value)
                'resource_count': 20, 'root_resource_group': 'CEP4',
                'output_files': {
                    'uv': [{'sap_nr': 0, 'identification': 'mom.G777955.B2.1.C.SAP000.uv.dps',
                            'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 0}}]
                }
            }, {'resource_types': {'bandwidth': 35791395, 'storage': 1073741824},  # idem
                'resource_count': 60, 'root_resource_group': 'CEP4',
                'output_files': {
                    'uv': [{'sap_nr': 1, 'identification': 'mom.G777955.B2.1.C.SAP001.uv.dps',
                            'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 20}}]
                }
            }, {'resource_types': {'bandwidth': 35791395, 'storage': 1073741824},  # idem
                'resource_count': 20, 'root_resource_group': 'CEP4',
                'output_files': {
                    'uv': [{'sap_nr': 2, 'identification': 'mom.G777955.B2.1.C.SAP002.uv.dps',
                            'properties': {'uv_file_size': 1073741824, 'nr_of_uv_files': 1, 'start_sb_nr': 80}}]
                }
            }, {'resource_types': {'bandwidth': 71582789, 'storage': 2147483648},  # for each quad (4 stokes) of cs output tab part (thus the total is times the resource_count value)
                'resource_count': 34, 'root_resource_group': 'DRAGNET',
                'output_files': {
                    'cs': [{'sap_nr': 0, 'identification': 'mom.G777955.B2.1.C.SAP000.cs.dps',
                            'properties': {'cs_file_size': 536870912, 'nr_of_cs_files': 4, 'nr_of_cs_stokes': 4,
                                           'nr_of_cs_parts': 2}}]  # parts per tab for this sap
                }
            }, {'resource_types': {'bandwidth': 71582789, 'storage': 2147483648},  # idem
                'resource_count': 6, 'root_resource_group': 'DRAGNET',
                'output_files': {
                    'cs': [{'sap_nr': 1, 'identification': 'mom.G777955.B2.1.C.SAP001.cs.dps',
                            'properties': {'cs_file_size': 536870912, 'nr_of_cs_files': 4, 'nr_of_cs_stokes': 4,
                                           'nr_of_cs_parts': 1, 'is_tab_nr': 0}}]  # parts per tab for this sap
                }
            }, {'resource_types': {'bandwidth': 17895698, 'storage': 536870912},  # for each 'is' output tab part (thus the total is times the resource_count value)
                'resource_count': 1, 'root_resource_group': 'DRAGNET',
                'output_files': {
                    'is': [{'sap_nr': 1, 'identification': 'mom.G777955.B2.1.C.SAP001.is.dps',
                            'properties': {'is_file_size': 536870912, 'nr_of_is_files': 1, 'nr_of_is_stokes': 1,
                                           'is_tab_nr': 0}}]  # IS can have >1 parts, but currently max 1 IS TAB per SAP
                }
            }]
        }
        """
        logger.info("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)
        # NOTE: observation estimates appear quite accurate. Most of the difference comes from Observation.stopTime
        # being planned instead of real stop time, because of Cobalt block size not being exactly 1.0 s.
        duration = self._getDuration(parset.getString('Observation.startTime'),
                                     parset.getString('Observation.stopTime'))

        errors = []
        estimates = []

        try:
            if parset.getBool('Observation.DataProducts.Output_Correlated.enabled'):
                estimates.extend(self.correlated(parset, duration))
        except ValueError as exc:
            logger.error(exc)
            errors.append(str(exc))

        try:
            if parset.getBool('Observation.DataProducts.Output_CoherentStokes.enabled'):
                estimates.extend(self.coherentstokes(parset, duration))
        except ValueError as exc:
            logger.error(exc)
            errors.append(str(exc))

        try:
            if parset.getBool('Observation.DataProducts.Output_IncoherentStokes.enabled'):
                estimates.extend(self.incoherentstokes(parset, duration))
        except ValueError as exc:
            logger.error(exc)
            errors.append(str(exc))

        if not estimates:
            logger.error('no data product estimates in observation resource estimate list!')
            errors.append('Produced observation resource estimate list has no data product estimates!')

        try:
            estimates.extend(self.stations(parset))
        except ValueError as exc:
            logger.error(exc)
            errors.append(str(exc))

        logger.debug('Observation resource estimates:\n' + pprint.pformat(estimates))
        result = {'errors': errors, 'estimates': estimates}
        return result

    def correlated(self, parset, duration):
        """ Estimate storage size and bandwidth needed for correlated ('uv')
            data products. Also add SAP properties needed by the propagator.
            The duration argument is a float in (fractional) seconds.
            Return list of estimates, max 1 SAP per estimate (easier for assigner),
            or raise ValueError on error.
        """
        logger.info("calculating correlated data size")

        storage_unit     = 512  # all sizes in bytes
        size_of_header   = 512
        size_of_overhead = 600000  # COBALT parset in MS HISTORY subtable + misc
        size_of_short    = 2
        size_of_visib    = 8  # a visibility is stored as a std::complex<float>
        nr_polarizations = 2
        channels_per_subband = parset.getInt(COBALT + 'Correlator.nrChannelsPerSubband', 64)  # defaults as in COBALT
        integration_time = parset.getFloat(COBALT + 'Correlator.integrationTime', 1)
        nr_virtual_stations = self._virtual_stations(parset)

        # Reflects MeasurementSets produced by the casacore LOFAR storage manager (LofarStMan)
        # The sub-expression '+ val-1) / val' computes a rounded (positive) integer division.
        integrated_seconds = int(duration / integration_time)
        nr_baselines = nr_virtual_stations * (nr_virtual_stations + 1) / 2
        data_size = (nr_baselines * channels_per_subband * nr_polarizations * nr_polarizations * \
                     size_of_visib + storage_unit-1) / storage_unit * storage_unit
        n_sample_size = (nr_baselines * channels_per_subband * size_of_short + storage_unit-1) / \
                        storage_unit * storage_unit
        file_size = (data_size + n_sample_size + size_of_header) * integrated_seconds + size_of_overhead  # bytes
        bandwidth = int(ceil(8 * file_size / duration))  # bits/second

        root_resource_group = parset.getString(DATAPRODUCTS + 'Output_Correlated.storageClusterName')

        nr_saps = parset.getInt('Observation.nrBeams')
        if nr_saps < 1:
            raise ValueError("Correlated data output enabled, but nrBeams < 1")

        # Estimates may differ per SAP for CS/IS. Decided to always produce a separate estimate per SAP.
        # Hence, need to annotate each SAP with the right identifications for pipeline predecessor input filtering.
        identifications = parset.getStringVector(DATAPRODUCTS + 'Output_Correlated.identifications')
        sap_idents = self._sap_identifications(identifications, nr_saps)

        total_files = 0  # sum of all subbands in all digital beams
        estimates = []
        for sap_nr in range(nr_saps):
            subbandList = parset.getStringVector('Observation.Beam[%d].subbandList' % sap_nr)
            nr_subbands = len(subbandList)
            if nr_subbands == 0:
                # Replace here by 'continue' (+ check total_files > 0 at the end) once we support separate subband lists for UV, CS, IS
                raise ValueError("Correlated data output enabled, but empty subband list for sap %d" % sap_nr)

            est = {'resource_types': {'bandwidth': bandwidth, 'storage': file_size},
                   'resource_count': nr_subbands,
                   'root_resource_group': root_resource_group,
                   'output_files': {'uv': [{'sap_nr': sap_nr, 'identification': sap_idents[sap_nr],
                                            'properties': {'uv_file_size': file_size, 'nr_of_uv_files': 1,  # thus total nr_of_uv_files is resource_count times 1
                                                           'start_sb_nr': total_files}}]}}
            total_files += nr_subbands
            estimates.append(est)

        logger.debug("Correlated data estimates:\n" + pprint.pformat(estimates))
        return estimates

    def coherentstokes(self, parset, duration):
        """ Estimate storage size and bandwidth needed for Coherent Stokes ('cs')
            data products. Also add SAP properties needed by the propagator.
            The duration argument is a float in (fractional) seconds.
            Return list of estimates, max 1 SAP per estimate (easier for assigner),
            or raise ValueError on error.
        """
        logger.info("calculate coherent stokes data size")

        size_of_sample = 4  # single precision float
        coherent_type = parset.getString(COBALT + 'BeamFormer.CoherentStokes.which')
        subbands_per_file = parset.getInt(COBALT + 'BeamFormer.CoherentStokes.subbandsPerFile', 512)
        if subbands_per_file < 0:
            raise ValueError('BeamFormer.CoherentStokes.subbandsPerFile may not be negative, but is %d' % subbands_per_file)
        if subbands_per_file == 0:
            subbands_per_file = 512
        samples_per_second = self._samples_per_second(parset)
        time_integration_factor = parset.getInt(COBALT + 'BeamFormer.CoherentStokes.timeIntegrationFactor')
        # Note that complex voltages (XXYY) cannot be meaningfully integrated (time_integration_factor 1)
        size_per_subband = (samples_per_second * size_of_sample * duration) / time_integration_factor
        nr_coherent = len(coherent_type)  # 'I' or 'IQUV' or 'XXYY'

        doFlysEye = parset.getBool(COBALT + 'BeamFormer.flysEye')
        root_resource_group = parset.getString(DATAPRODUCTS + 'Output_CoherentStokes.storageClusterName')

        nr_saps = parset.getInt('Observation.nrBeams')
        if nr_saps < 1:
            raise ValueError("Coherent Stokes data output enabled, but nrBeams < 1")

        # Estimates may differ per SAP for CS/IS. Decided to always produce a separate estimate per SAP.
        # Hence, need to annotate each SAP with the right identifications for pipeline predecessor input filtering.
        identifications = parset.getStringVector(DATAPRODUCTS + 'Output_CoherentStokes.identifications')
        sap_idents = self._sap_identifications(identifications, nr_saps)

        estimates = []
        for sap_nr in range(nr_saps):
            logger.info("checking SAP {}".format(sap_nr))
            subbandList = parset.getStringVector('Observation.Beam[%d].subbandList' % sap_nr)
            nr_subbands = len(subbandList)
            if nr_subbands == 0:
                raise ValueError("Coherent Stokes data output enabled, but empty subband list for sap %d" % sap_nr)
            nr_subbands_per_file = min(subbands_per_file, nr_subbands)

            nr_coherent_tabs = 0
            is_tab_nr = None

            nr_tabs = parset.getInt('Observation.Beam[%d].nrTiedArrayBeams' % sap_nr)
            for tab_nr in range(nr_tabs):
                if not parset.getBool("Observation.Beam[%d].TiedArrayBeam[%d].coherent" % (sap_nr, tab_nr)):
                    is_tab_nr = tab_nr
                    logger.info("coherentstokes: skipping incoherent tab")
                    continue
                nr_coherent_tabs += 1
            logger.info("added %d coherent tabs before considering tab rings and fly's eye tabs", nr_coherent_tabs)

            nr_tab_rings = parset.getInt('Observation.Beam[%d].nrTabRings' % sap_nr)
            if nr_tab_rings < 0:
                raise ValueError("SAP %d: nr of tab rings is < 0: %d" % (sap_nr, nr_tab_rings))
            elif nr_tab_rings > 0:
                nr_tabs = (3 * nr_tab_rings * (nr_tab_rings + 1) + 1)
                nr_coherent_tabs += nr_tabs
                logger.info("added %d tabs from %d tab rings", nr_tabs, nr_tab_rings)

            if doFlysEye:
                nr_tabs = self._virtual_stations(parset)
                nr_coherent_tabs += nr_tabs
                logger.info("added %d fly's eye tabs", nr_tabs)

            if nr_coherent_tabs == 0:
                raise ValueError("Coherent Stokes data output enabled, but no coherent tabs for sap %d" % sap_nr)

            # Keep XXYY/IQUV together (>1 parts still possible).
            # Else translator to parset filenames cannot know which stokes (nr_of_XX_stokes property too coarse).
            # Also for complex voltages (XXYY) only: pipeline needs all 4 XXYY accessible from the same node.
            #
            # NOTE: If a TAB is split into parts, then the last TAB part may contain fewer subbands.
            # Simplify: compute a single (max) file size for all TABs or TAB parts.
            file_size = int(nr_subbands_per_file * size_per_subband)  # bytes
            storage = file_size * nr_coherent  # bytes
            bandwidth = int(ceil(8 * storage / duration))  # bits/second
            nr_parts_per_tab = int(ceil(nr_subbands / float(nr_subbands_per_file)))  # thus per tab per stokes

            est = {'resource_types': {'storage': storage, 'bandwidth': bandwidth}, 
                   'resource_count': nr_coherent_tabs * nr_parts_per_tab,
                   'root_resource_group': root_resource_group,
                   'output_files': {'cs': [{'sap_nr': sap_nr, 'identification': sap_idents[sap_nr],
                                            'properties': {'cs_file_size': file_size, 'nr_of_cs_files': nr_coherent,
                                                           'nr_of_cs_stokes': nr_coherent, 'nr_of_cs_parts': nr_parts_per_tab}}]}}
            if is_tab_nr is not None:  # translator to filenames needs to know: it may not have all CS+IS info in one claim
                est['output_files']['cs'][0]['properties']['is_tab_nr'] = is_tab_nr
            estimates.append(est)

        logger.debug("Coherent Stokes data estimates:\n" + pprint.pformat(estimates))
        return estimates

    def incoherentstokes(self, parset, duration):
        """ Estimate storage size and bandwidth needed for Incoherent Stokes ('is')
            data products. Also add SAP properties needed by the propagator.
            The duration argument is a float in (fractional) seconds.
            Return list of estimates, max 1 SAP per estimate (easier for assigner),
            or raise ValueError on error.
        """
        logger.info("calculate incoherent stokes data size")

        size_of_sample = 4  # single precision float
        incoherent_type = parset.getString(COBALT + 'BeamFormer.IncoherentStokes.which')
        subbands_per_file = parset.getInt(COBALT + 'BeamFormer.IncoherentStokes.subbandsPerFile', 512)
        if subbands_per_file < 0:
            raise ValueError('BeamFormer.IncoherentStokes.subbandsPerFile may not be negative, but is %d' % subbands_per_file)
        if subbands_per_file == 0:
            subbands_per_file = 512
        samples_per_second = self._samples_per_second(parset)
        time_integration_factor = parset.getInt(COBALT + 'BeamFormer.IncoherentStokes.timeIntegrationFactor')
        size_per_subband = (samples_per_second * size_of_sample * duration) / time_integration_factor
        nr_incoherent = len(incoherent_type)  # 'I' or 'IQUV' ('XXYY' only possible for coherent stokes)

        root_resource_group = parset.getString(DATAPRODUCTS + 'Output_IncoherentStokes.storageClusterName')

        nr_saps = parset.getInt('Observation.nrBeams')
        if nr_saps < 1:
            raise ValueError("Incoherent Stokes data output enabled, but nrBeams < 1")

        # Estimates may differ per SAP for CS/IS. Decided to always produce a separate estimate per SAP.
        # Hence, need to annotate each SAP with the right identifications for pipeline predecessor input filtering.
        identifications = parset.getStringVector(DATAPRODUCTS + 'Output_IncoherentStokes.identifications')
        sap_idents = self._sap_identifications(identifications, nr_saps)

        estimates = []
        for sap_nr in range(nr_saps):
            logger.info("checking SAP {}".format(sap_nr))
            subbandList = parset.getStringVector('Observation.Beam[%d].subbandList' % sap_nr)
            nr_subbands = len(subbandList)
            if nr_subbands == 0:
                raise ValueError("Incoherent Stokes data output enabled, but empty subband list for sap %d" % sap_nr)
            nr_subbands_per_file = min(subbands_per_file, nr_subbands)

            # Atm can have 1 IS TAB per SAP, because its pointing is equal to the SAP pointing.
            # (When we support online coh dedisp and on multiple DMs, we can have >1 IS per SAP.)
            nr_incoherent_tabs = 0

            nr_tabs = parset.getInt('Observation.Beam[%d].nrTiedArrayBeams' % sap_nr)
            for tab_nr in range(nr_tabs):
                if parset.getBool("Observation.Beam[%d].TiedArrayBeam[%d].coherent" % (sap_nr, tab_nr)):
                    continue

                if nr_incoherent_tabs > 0:
                    # Could get here to produce >1 IS TAB copies, maybe for some software test
                    raise ValueError("SAP %i: >1 incoherent TAB not supported: TAB nrs %i and %i" % (sap_nr, tab_nr, is_tab_nr))
                is_tab_nr = tab_nr
                nr_incoherent_tabs += 1
            logger.info("added %d incoherent tab(s)", nr_incoherent_tabs)

            if nr_incoherent_tabs == 0:
                raise ValueError("Incoherent Stokes data output enabled, but no incoherent tabs for sap %d" % sap_nr)

            # Keep IQUV together (>1 parts still possible).
            # Else translator to parset filenames cannot know which stokes (nr_of_XX_stokes property too coarse).
            #
            # NOTE: If a TAB is split into parts, then the last TAB part may contain fewer subbands.
            # Simplify: compute a single (max) file size for all TABs or TAB parts.
            file_size = int(nr_subbands_per_file * size_per_subband)  # bytes
            storage = file_size * nr_incoherent  # bytes
            bandwidth = int(ceil(8 * storage / duration))  # bits/second
            nr_parts_per_tab = int(ceil(nr_subbands / float(nr_subbands_per_file)))  # thus per tab per stokes

            est = {'resource_types': {'storage': storage, 'bandwidth': bandwidth},
                   'resource_count': nr_incoherent_tabs * nr_parts_per_tab,
                   'root_resource_group': root_resource_group,
                   'output_files': {'is': [{'sap_nr': sap_nr, 'identification': sap_idents[sap_nr],
                                            'properties': {'is_file_size': file_size, 'nr_of_is_files': nr_incoherent,
                                                           'nr_of_is_stokes': nr_incoherent, 'is_tab_nr': is_tab_nr}}]}}
            estimates.append(est)

        logger.debug("Incoherent Stokes data estimates:\n" + pprint.pformat(estimates))
        return estimates

    def _samples_per_second(self, parset):
        """ set samples per second
        """
        samples_160mhz = 155648
        samples_200mhz = 196608
        sample_clock = parset.getInt('Observation.sampleClock')
        samples = samples_160mhz if 160 == sample_clock else samples_200mhz
        logger.info("samples per second for {} MHz clock = {}".format(sample_clock, samples))
        return samples

    def _virtual_stations(self, parset):
        """ calculate virtualnumber of stations
        """
        stationList = parset.getStringVector('Observation.VirtualInstrument.stationList')
        nr_virtual_stations = 0
        if parset.getString('Observation.antennaSet') in ('HBA_DUAL', 'HBA_DUAL_INNER'):
            for station in stationList:
                if 'CS' in station:
                    nr_virtual_stations += 2
                else:
                    nr_virtual_stations += 1
        else:
            nr_virtual_stations = len(stationList)
        logger.info("number of virtual stations = {}".format(nr_virtual_stations))
        return nr_virtual_stations

    def _extract_sap_nr(self, identification):
        """ Return sap nr as int from identification or None if
            no int xxx in '.SAPxxx.' in identification.
        """
        for s in identification.split('.'): # Find the SAP number, if present
            if 'SAP' not in s:
                continue
            try:
                return int(s[3:])
            except:
                pass

        return None

    def _sap_identifications(self, identifications, nr_saps):
        """ Return list with identifications' identification for sap i at index i,
            or '' at index i if no such identification for sap i.
            NOTE: identifications should not contain entries for multiple data product types,
            otherwise we cannot return a single identification per sap nr.

            For output, there must be exactly 1 (non-duplicate) identification string per
            data product type (how can you otherwise refer to it unambiguously?),
            and per sap (per sap for observations only, but always the case here).
        """
        sap_idents = [''] * nr_saps

        for ident in identifications:
            sap_nr = self._extract_sap_nr(ident)
            try:
                ident_seen = sap_idents[sap_nr]
            except Exception as e:  # e.g. sap_nr is None or out of bounds
                logger.error("Ignoring observation identification string with no or invalid sap nr: %s", str(e))
                continue

            if not ident_seen:
                sap_idents[sap_nr] = ident
            elif ident_seen != ident:
                logger.error("Cannot have multiple observation identifications per sap. Dropping %s", ident)  # see doc string

        return sap_idents

    def stations(self, parset):
        """ Estimate required  RSPs and RCUs per station.
            One or two RSP boards are returned per station depending on antennaset.
            RCUs are encoded as a bitfield, to be able to tell which RCUs are actually neeeded.
            Return list of estimates, or raise ValueError on error.
        """
        estimates = []
        antennaset = parset.getString('Observation.antennaSet')
        stationset = parset.getStringVector('Observation.VirtualInstrument.stationList')
        if not stationset:
            raise ValueError("Observation.VirtualInstrument.stationList is empty")
        rculists = self.asp.get_receiver_units_configuration_per_station(antennaset, stationset)

        for station in stationset:
            bitfield, count = self._rculist_to_bitfield(rculists[station])
            rsps, channelbits = self._required_rsps(station, antennaset, parset)

            est = {'resource_types': {'rcu': bitfield},
                   'resource_count': 1,
                   'station': station,
                   'root_resource_group': station}

            estimates.append(est)

            for rsp in rsps:
                root_resource_group = station+rsp
                est = {'resource_types': {},
                       'resource_count': 1,
                       'station': station,
                       'root_resource_group': root_resource_group}
                est['resource_types']['bandwidth'] = 3000000000
                est['resource_types']['rsp'] = channelbits

                estimates.append(est)

        return estimates

    def _rculist_to_bitfield(self, rculist):
        """
        Takes list of rcus as returned by Antennasets_parser ['LBL', 'LBH', None, ...] and encodes them as a bitfield.
        Each bit represents one rcu, value is 1 if rcu is not None in input list (= is used), 0 otherwise.
        Returns String representation of the bitfield and the number of used rcus.
        """
        bitfield = ""
        count = 0
        for rcu in rculist:
            if rcu is None:
                bitfield = bitfield+"0"
            else:
                bitfield = bitfield+"1"
                count = count + 1

        return bitfield, count

    def _required_rsps(self, station, antennaset, parset):
        """
        Takes station name and list of antennafields.
        Returns list with one or both required rsps and number of channelbits,
        or raises ValueError on error.
        """
        if station.startswith('CS'):
            required_rsps = ['RSP0'] # default
            if antennaset == 'HBA_ONE':
                required_rsps = ['RSP1']
            if antennaset in ['HBA_DUAL', 'HBA_DUAL_INNER']:
                required_rsps = ['RSP0', 'RSP1']
        else:
            required_rsps = ['RSP'] # default for non-core stations

        nr_saps = parset.getInt('Observation.nrBeams')
        if nr_saps < 1:
            raise ValueError('Observation.nrBeams must be at least 1, but is %d' % nr_saps)
        subBandList = []
        for nr in range(nr_saps):
            key = 'Observation.Beam['+str(nr)+'].subbandList'
            sblist = parset.getStringVector(key)
            if not sblist:
                raise ValueError("%s is empty" % key)
            subBandList.extend(sblist)

        nrSubbands = len(subBandList)
        nrBitsPerSample = parset.getInt('Observation.nrBitsPerSample')
        if nrBitsPerSample != 16 and nrBitsPerSample != 8 and nrBitsPerSample != 4:
            raise ValueError('Observation.nrBitsPerSample must be 16, 8, or 4, but is %d' % nrBitsPerSample)
        channelbits = nrSubbands * nrBitsPerSample

        return required_rsps, channelbits

