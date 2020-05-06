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

import os.path
from datetime import datetime, timedelta
from time import sleep
import errno
import os

# prevent annoying h5py future/deprecation warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"
import h5py

import logging
logger = logging.getLogger(__name__)

class SharedH5File():
    """
    Wrapper class aroung h5py.File to open an hdf5 file in read, write, or read/write mode safely,
    even when the file might be used simultanously by other processes.
    It waits for <timeout> seconds until the file becomes available.

    Example usage:

    with SharedH5File("foo.h5", 'r') as file:
        file["foo"] = "bar"

    """
    def __init__(self, path, mode='r', timeout=900):
        self._path = path
        self._mode = mode
        self._timeout = timeout
        self._file = None

    def open(self):
        start_timestamp = datetime.utcnow()
        while self._file is None:
            try:
                self._file = h5py.File(self._path, self._mode)
                return self._file
            except IOError:
                if self._path.startswith('~'):
                    # try again with tilde replaced
                    self._path = os.path.expanduser(self._path)
                    continue

                if not os.path.exists(self._path):
                    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self._path)

                logger.warning("Cannot open file '%s' with mode '%s'. Trying again in 1 sec...",
                               self._path, self._mode)
                sleep(max(0, min(1, self._timeout)))
                if datetime.utcnow() - start_timestamp > timedelta(seconds=self._timeout):
                    logger.error("Cannot open file '%s' with mode '%s', even after trying for %s seconds",
                                   self._path, self._mode, self._timeout)
                    raise

    def close(self):
        self._file.close()
        self._file = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

class WorkingDirContext():
    """
    A WorkingDirContext can be used to make sure that the raw-sibling-file of an h5 file can be read,
    because the working dir needs to be the dir of the h5 file (h5py demands that).
    When leaving this context, the working dir is restored to the situation before the context was entered.


    Example usage:

    with h5py.File("foo.h5", "r") as my_h5_file:
        with WorkingDirContext(my_h5_file):
            my_h5_file["foo"] = "bar"
    """
    def __init__(self, h5_file: h5py.File):
        self._h5_file = h5_file
        self._original_cwd = os.getcwd()

    def change_dir_to_h5_file(self):
        self._original_cwd = os.getcwd()
        os.chdir(os.path.dirname(self._h5_file.filename))

    def change_dir_to_original(self):
        os.chdir(self._original_cwd)

    def __enter__(self):
        self.change_dir_to_h5_file()
        return self._h5_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.change_dir_to_original()

