#!/usr/bin/env python3
# test lib

from checkhardware_lib.spectrum_checks import *
from .data import *
from .lofar import *

test_version = '0815'

logger = None


def init_test_lib():
    global logger
    logger = logging.getLogger()
    logger.debug("init logger test_lib")


# HBASubband = dict( DE601C=155, DE602C=155, DE603C=284, DE604C=474, DE605C=479, FR606C=155, SE607C=287, UK608C=155 )
# DefaultLBASubband = 301
# DefaultHBASubband = 155











