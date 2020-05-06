#!/usr/bin/env python3

## Print EC status
## can only be used on LCU
##
## usage: ./status.py
##
## Author: Pieter Donker (ASTRON)
## Last change: September 2014 

from st_ec_lib import *
import sys
import time

VERSION = '1.2.0' # version of this script    

# used variables
version = 0   # EC version
versionstr = 'V-.-.-'

##=======================================================================
## start of main program
##=======================================================================
if __name__ == '__main__':
    host = getIP()
    if host == None:
        print("============================================")
        print("ERROR, this script can only run on a station")
        print("============================================")
    else:
        ec = EC(host)
        ec.connectToHost()
        time.sleep(1.0)
        # version is used to check if function is available in firmware
        version,versionstr  = ec.getVersion()  
        ec.printInfo(True)
        ec.getStatus()
        ec.printInfo(False)
        ec.disconnectHost()


