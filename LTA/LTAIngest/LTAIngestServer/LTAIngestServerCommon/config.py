from lofar.common import isProductionEnvironment
from lofar.common import isTestEnvironment
from socket import gethostname

#server config is same as common config plus extra's
from lofar.lta.ingest.common.config import *

DEFAULT_INGEST_INCOMING_JOB_SUBJECT = DEFAULT_INGEST_PREFIX+".incoming_job"
DEFAULT_INGEST_JOB_FOR_TRANSFER_SUBJECT = DEFAULT_INGEST_PREFIX+".job_for_transfer"

DEFAULT_MOM_XMLRPC_HOST=hostnameToIp('lexar003.lexar.control.lofar' if isProductionEnvironment() and 'lexar' in gethostname() else
                                     'lexar004.lexar.control.lofar' if isTestEnvironment()  and 'lexar' in gethostname() else
                                     'localhost')
DEFAULT_MOM_XMLRPC_PORT=2010 if isProductionEnvironment() else 2009

MOM_BASE_URL = 'https://lcs029.control.lofar:8443/'# if isProductionEnvironment() else 'http://lofartest.control.lofar:8080/'

LTA_BASE_URL = 'https://%s:%s@lta-ingest.lofar.eu:9443/' if isProductionEnvironment() else 'https://%s:%s@lta-ingest-test.lofar.eu:19443/'

JOBS_DIR='/local/ingest/jobs' if isProductionEnvironment() else '/local/ingesttest/jobs' if isTestEnvironment() else '/tmp/ingest/jobs'
MAX_NR_OF_RETRIES=4
DEFAULT_JOB_PRIORITY = 4
MAX_NR_OF_JOBS=40

MAX_USED_BANDWITH_TO_START_NEW_JOBS=9.9e9 #Gbps
NET_IF_TO_MONITOR=['p2p1.2030', # outgoing traffic to Juelich
                   'p2p1.2033', # outgoing traffic to Poznan
                   'p2p1.992' # outgoing traffic to SARA
                   ] if isProductionEnvironment() else []

GLOBUS_TIMEOUT = 1800

TRANSFER_TIMEOUT = 300

FINISHED_NOTIFICATION_MAILING_LIST = []
if isProductionEnvironment():
    FINISHED_NOTIFICATION_MAILING_LIST += ['sos@astron.nl']

FINISHED_NOTIFICATION_BCC_MAILING_LIST=['schaap@astron.nl','softwaresupport@astron.nl']
if isProductionEnvironment():
    FINISHED_NOTIFICATION_BCC_MAILING_LIST += ['observer@astron.nl']

