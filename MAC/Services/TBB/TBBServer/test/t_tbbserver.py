#!/usr/bin/env python3

import unittest
import uuid
from lofar.messaging.messagebus import TemporaryQueue

import logging
logger = logging.getLogger(__name__)

#TODO: add tests for tbbservice

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    with TemporaryQueue(__name__) as tmp_queue:

        logger.warning("TODO: add tests for tbbservice!")
        exit(3)

        # and run all tests
        unittest.main()

