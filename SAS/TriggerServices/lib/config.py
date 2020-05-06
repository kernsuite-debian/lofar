
""" Config file for trigger services. """

# Messaging

from lofar.mac.tbb.tbb_util import expand_list

TRIGGER_SERVICENAME = "triggerservice"

# VO-Events
ALERT_BROKER_HOST = '10.87.15.250' # phobos.nfra.nl.
ALERT_BROKER_PORT = 8099
ALERT_PACKET_TYPE_FILTER = None  # list of int or None for all

DEFAULT_TBB_CEP_NODES = None # list of nodes to dump to, e.g. ["cpu%s" % str(num).zfill(2) for num in expand_list("01-50")], or None for all available
DEFAULT_TBB_SUBBANDS = expand_list("10-496")  # The subbands to dump. Note: When starting the recording (tbbservice_start_recording), the subband range HAS to cover 487 subbands (typically 10-496)
DEFAULT_TBB_STATIONS = ['cs001','cs002','cs003','cs004','cs005','cs006','cs007','cs011','cs013','cs017','cs021','cs024','cs026','cs028','cs030','cs031','cs032','cs101','cs103','cs201','cs301','cs302','cs401','cs501','rs106','rs205','rs208','rs210','rs305','rs306','rs307','rs310','rs406','rs407','rs409','rs503','rs508','rs509']  # List of stations to include in tbb dump (filtered for those who are actually observing at event ToA)

DEFAULT_TBB_PROJECT = "COM_ALERT"
DEFAULT_TBB_ALERT_MODE = "subband"
DEFAULT_TBB_BOARDS = expand_list("0-5")
DEFAULT_TBB_DUMP_DURATION = 5.0  # should be 5.0 in production

