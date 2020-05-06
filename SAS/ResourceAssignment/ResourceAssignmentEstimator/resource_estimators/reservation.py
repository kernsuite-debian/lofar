# reservation.py
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
# $Id: reservation.py 33534 2016-02-08 14:28:26Z jkuensem $

import logging
from math import ceil
from .base_resource_estimator import BaseResourceEstimator
from lofar.stationmodel.antennasets_parser import AntennaSetsParser

logger = logging.getLogger(__name__)

DATAPRODUCTS = "Observation.DataProducts."
COBALT = "Observation.ObservationControl.OnlineControl.Cobalt."

class ReservationResourceEstimator(BaseResourceEstimator):
    """ ResourceEstimator for LOFAR Observations
    """
    def __init__(self):
        logger.info("init ReservationResourceEstimator")
        super(ReservationResourceEstimator, self).__init__(name='reservation')
        self.required_keys = ('Observation.startTime',
                              'Observation.stopTime',
                              'Observation.VirtualInstrument.stationList',
                              )
        self.asp = AntennaSetsParser()

    def _calculate(self, parset, predecessor_estimates=[]):
        """ Return the max resources that may be actually used during reserved time.
            The base_resource_estimator adds an {'observation': } around this.
            The predecessor_estimates arg is just to implement the same interface as pipelines. Reservations have no predecessor.
        """
        logger.info("start estimate '{}'".format(self.name))
        logger.info('parset: %s ' % parset)
        # NOTE: Observation.stopTime may differ from real stop time, because of Cobalt block size not being exactly 1.0 s.
        duration = self._getDuration(parset.getString('Observation.startTime'),
                                     parset.getString('Observation.stopTime'))

        errors = []
        estimates = []

        # todo: correlator/cluster estimates?! (storage/bandwidth for test obs?)

        station_estimates = self.stations(parset)
        if station_estimates is None:
            errors.append('empty STATION resource estimate!')
            logger.error('resource estimate for STATIONS is empty!')
        else:
            estimates.extend(station_estimates)

        if not estimates:
            errors.append('Produced observation resource estimate list is empty!')
            logger.error('empty observation resource estimate list!')

        logger.debug('Observation resource estimate(s): {}'.format(estimates))
        result = {'errors': errors, 'estimates': estimates}
        return result

    def stations(self, parset):
        """ Estimate max  RSPs and RCUs per station. RCUs are encoded as a bitfield..
            Return list of estimates.
        """
        estimates = []
        antennaset = 'HBA_DUAL' # just choose any one available for all stations
        stationset = parset.getStringVector('Observation.VirtualInstrument.stationList')
        rculists = self.asp.get_receiver_units_configuration_per_station(antennaset, stationset)

        for station in stationset:

            rsps, channelbits = self._max_rsps(station)

            bitfield = len(rculists[station])*'1' # claim all RCUs irrespective of use in given antennaset, we actually only need the AntennasetsParser to obtain the number of RCUs

            est = {'resource_types': {'rcu': bitfield},
                   'resource_count': 1,
                   'root_resource_group': station}

            estimates.append(est)

            for rsp in rsps:
                root_resource_group = station+rsp
                est = {'resource_types': {},
                       'resource_count': 1,
                       'root_resource_group': root_resource_group}
                est['resource_types']['bandwidth'] = 3000000000
                est['resource_types']['rsp'] = channelbits

                estimates.append(est)

        return estimates

    def _max_rsps(self, station):
        """
        Takes station name and list of antennafields.
        Returns list with one or both required rsps and number of channelbits.
        """
        if station.startswith('CS'):
            required_rsps = ['RSP0', 'RSP1']
        else:
            required_rsps = ['RSP']

        nrSubbands = 61
        nrBitsPerSample = 16
        nrLanes = 4  # todo: is this the meaning of magic number 4 from the ticket? Is it the same on all station types?
        channelbits = nrSubbands * nrBitsPerSample * nrLanes

        return required_rsps, channelbits

