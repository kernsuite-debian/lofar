# defaultmailaddresses.py: default mail addresses for the LOFAR software
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: $
#
"""
This package contains the default mail addresses used in the LOFAR software
"""

from ConfigParser import ConfigParser
import os
import pwd
from glob import glob

# obtain the environment, and add USER and HOME if needed (since supervisord does not)
environ = os.environ
user_info = pwd.getpwuid(os.getuid())
environ.setdefault("HOME", user_info.pw_dir)
environ.setdefault("USER", user_info.pw_name)



def findfiles(pattern):
  """ Returns a list of files matched by `pattern'.
      The pattern can include environment variables using the
      {VAR} notation.
  """
  try:
    return glob(pattern.format(**environ))
  except KeyError:
    return []


# Addresses used for the pipelines
class PipelineEmailConfig():
    """
        Pipeline email configuration class
    """

    def __init__(self, filepatterns = None):
        if filepatterns is None:
            filepatterns = ["{LOFARROOT}/etc/email/*.ini",
                    "{HOME}/.lofar/email/*.ini"]# TODO correct the pattern here
        self.configfiles = sum([findfiles(p) for p in filepatterns],[])
        if not self.configfiles:
            raise Exception("no config file found")
        self.config = None

    def load_config(self):
        self.config = ConfigParser()
        self.config.read(self.configfiles)

    def get(self, key):
        if not self.config:
            self.load_config()
        return self.config.get("Pipeline",key)

    def __getitem__(self, what):
        return self.get(what)




