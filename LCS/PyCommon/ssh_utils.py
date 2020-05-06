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

import logging
logger = logging.getLogger(__name__)

def ssh_cmd_list(host, user='lofarsys'):
    '''
    returns a subprocess compliant command list to do an ssh call to the given node
    uses ssh option -T to disable remote pseudo terminal
    uses ssh option -q for ssh quiet mode (no ssh warnings/errors)
    uses ssh option -o StrictHostKeyChecking=no to prevent prompts about host keys
    :param host: the node name or ip address
    :param user: optional username, defaults to 'lofarsys'
    :return: a subprocess compliant command list
    '''
    return ['ssh', '-T', '-o StrictHostKeyChecking=no', user+'@'+host]


