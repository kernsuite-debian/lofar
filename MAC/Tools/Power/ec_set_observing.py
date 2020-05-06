#!/usr/bin/env python3
#
# Look for RCUs in ON mode and set EC to observing
#
# 2016 P.Donker
#
# this script is called by a cron job every minute

import os
os.chdir('/opt/lofar/sbin/')

import socket
import time
import subprocess


from st_ec_lib import *

def main():
    host = getIP()
    if host == None:
        print("===============================================")
        print("ERROR, this script can only run on a station")
        print("===============================================")

    ec = EC(host)
    ec.printInfo(False)

    observing = 0

    # look for RCU's in ON state
    response = cmd('/opt/lofar/bin/rspctl --rcu')
    for line in response.splitlines():
        if 'RCU[' in line:
            data = line.strip().split(',')[0].split()[-1]
            if data == 'ON':
                observing = 1

    #print "set observing %d" % observing
    ec.connectToHost()
    ec.setObserving(observing)
    time.sleep(0.5)
    ec.disconnectHost()

# excecute commandline cmd
def cmd(command):
    cmd_list = command.split()
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (so, se) = proc.communicate()
    so = so.decode("UTF-8")
    return(so)

# start main()
if __name__ == "__main__":
    main()



