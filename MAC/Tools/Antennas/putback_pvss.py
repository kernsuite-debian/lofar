#!/usr/bin/env python3
#
# Restore a station's WinCC broken hardware info from a dumpfile
# created by dumpAntennaStates.py.
#

from time import mktime, strptime, sleep, asctime, gmtime
from subprocess import Popen, PIPE
from socket import gethostname

#station = 'CS302'
station = gethostname()[:5].upper()

f = open('/globalhome/lofarsys/AntennaInfo/hardware_states.out', 'r')
pvss_old = f.readlines()
f.close()

bad_states = {}

# LOFAR.PIC.Core.CS302.LBA094.status_state | 50 | 2013-08-14 13:30:04.508

for line in pvss_old:
    if station not in line:
        continue

    info = line.split('|')

    key_list = info[0].split('.')
    key = '%s_%s_%s' % (key_list[0], key_list[1], key_list[4])
    value = int(info[1].strip()[0])
    timestamp_string = info[2].strip().split('.')[0]
    timestamp = mktime(strptime(timestamp_string, '%Y-%m-%d %H:%M:%S'))
    if key in bad_states:
        if timestamp > bad_states[key]['timestamp']:
            bad_states[key] = {'timestamp': timestamp, 'asctime': asctime(gmtime(timestamp)), 'value':value}
    else:
        bad_states[key] = {'timestamp': timestamp, 'value':value}

# put back values greeter than 10
for key, vals in sorted(bad_states.items()):
    if vals['value'] > 1:
        print(key, vals)
        # add extra argument to setObjectState force=true to reset failure.
        cmdline = Popen(['setObjectState', 'pvss_restore', key, str(vals['value'])], stdout=PIPE, stderr=PIPE)
        so, se = cmdline.communicate()
        sleep(0.2)
