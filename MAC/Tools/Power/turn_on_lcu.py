#!/usr/bin/env python3

## Turn on LCU power
## can only be used on LCU
##
## usage: ./turn_on_lcu.py
##
## Author: Pieter Donker (ASTRON)
## Last change: September 2014 

from st_ec_lib import *
import sys
import time

VERSION = '1.0.0' # version of this script    

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
        ec.printInfo(True)
        ec.getPowerStatus()
        ec.setPower(ec.P_LCU, ec.PWR_ON)
        print("waiting 10 seconds")
        time.sleep(10.0)
        ec.getPowerStatus()
        ec.printInfo(False)
        ec.disconnectHost()


