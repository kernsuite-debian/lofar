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
from lofar.messaging import RPCClient, RPCClientContextManagerMixin, DEFAULT_BROKER, DEFAULT_BUSNAME, DEFAULT_RPC_TIMEOUT
from lofar.sas.resourceassignment.resourceassignmentestimator.config import DEFAULT_RESOURCEESTIMATOR_SERVICENAME

''' Simple RPC client for ResourceEstimator Service
'''

logger = logging.getLogger(__name__)

class ResourceEstimatorRPC(RPCClientContextManagerMixin):
    def __init__(self, rpc_client: RPCClient = None):
        """Create an instance of the RADBRPC using the given RPCClient,
        or if None given, to a default RPCClient connecting to the DEFAULT_RESOURCEESTIMATOR_SERVICENAME service"""
        super().__init__()
        self._rpc_client = rpc_client or RPCClient(service_name=DEFAULT_RESOURCEESTIMATOR_SERVICENAME)

    @staticmethod
    def create(exchange: str = DEFAULT_BUSNAME, broker: str = DEFAULT_BROKER, timeout: int=DEFAULT_RPC_TIMEOUT):
        """Create a ResourceEstimatorRPC connecting to the given exchange/broker on the default DEFAULT_RESOURCEESTIMATOR_SERVICENAME service"""
        return ResourceEstimatorRPC(RPCClient(service_name=DEFAULT_RESOURCEESTIMATOR_SERVICENAME, exchange=exchange, broker=broker, timeout=timeout))

    def get_estimated_resources(self, specification_tree: dict) -> dict:
        return self._rpc_client.execute('get_estimated_resources', specification_tree=specification_tree)

