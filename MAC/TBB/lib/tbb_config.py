from os import getenv
from lofar.common.lcu_utils import wrap_command_in_lcu_head_node_ssh_call

# todo: The following list is not complete, make tbb operator aware of that!
groups_with_6boards = ['superterp',
                       'core',
                       'remote',
                       'nl',
                       'even',
                       'odd',
                       'today_core',
                       'today_remote',
                       'today_nl', ]

lowest_frequency = 100.0
highest_frequency = 200.0
sub_band_width = 0.1953125
number_of_samples = 1024.0
k_DM = 4148.808
slice_size = number_of_samples / (highest_frequency * 1e6) 

lofarroot = getenv("LOFARROOT")
if False and lofarroot is not None:
    tbb_command = lofarroot + "/bin/tbbctl"
    rsp_command = lofarroot + "/bin/rspctl"
else:
    tbb_command = "/opt/lofar/bin/tbbctl"
    rsp_command = "/opt/lofar/bin/rspctl"

lcurun_command = wrap_command_in_lcu_head_node_ssh_call(['lcurun'])

supported_modes = ['rawvoltage', 'subband']
