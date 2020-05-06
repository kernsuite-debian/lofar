#!/usr/bin/env python3

# Copyright (C) 2017
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


import logging
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_BUSNAME, \
    DEFAULT_BROKER, DEFAULT_RPC_TIMEOUT
from lofar.mac.config import DEFAULT_OBSERVATION_CONTROL_SERVICE_NAME

''' Simple RPC client for Service ObservationControl2
'''

logger = logging.getLogger(__name__)


class ObservationControlRPCClient(RPCClientContextManagerMixin):
    def __init__(self, rpc_client : RPCClient = RPCClient(service_name=DEFAULT_OBSERVATION_CONTROL_SERVICE_NAME)):
        super().__init__()
        self._rpc_client = rpc_client

    @staticmethod
    def create(exchange=DEFAULT_BUSNAME, broker=DEFAULT_BROKER, timeout=DEFAULT_RPC_TIMEOUT):
        """Create a OTDBRPC connecting to the given exchange/broker on the default DEFAULT_OTDB_SERVICENAME service"""
        return ObservationControlRPCClient(
            RPCClient(service_name=DEFAULT_OBSERVATION_CONTROL_SERVICE_NAME,
                      exchange=exchange, broker=broker, timeout=timeout))

    def abort_observation(self, sas_id):
        return self._rpc_client.execute('AbortObservation', sas_id=sas_id)
