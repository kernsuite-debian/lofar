#!/usr/bin/env python3

"""
Start IPython cluster.
"""

import sys, logging, os
from optparse import OptionParser
from configparser import SafeConfigParser as ConfigParser
from lofarpipe.support.clusterhandler import ClusterHandler

parser = OptionParser()
parser.add_option(
    "--config", help="Pipeline configuration file", default="~/.pipeline.cfg"
)
parser.add_option(
    "--num-engines", help="Number of engines per node", default=8
)
options, args = parser.parse_args()

my_logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-7s: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
stream_handler.setFormatter(formatter)
my_logger.addHandler(stream_handler)
my_logger.setLevel(logging.DEBUG)

config = ConfigParser()
config.read(os.path.expanduser(options.config))

clusterhandler = ClusterHandler(config)
clusterhandler.start_cluster(options.num_engines)

