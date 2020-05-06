#!/usr/bin/env python3

## Reset trip system in EC unit
## can only be used on LCU
##
## usage: ./ec_reset_trip.py
##
## Author: Pieter Donker (ASTRON)
## Last change: september 2014 

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
        ec.printInfo(True)
        ec.getPowerStatus()
        ec.resetTrip()
        print("waiting 10 seconds")
        time.sleep(10.0)
        ec.getPowerStatus()
        ec.printInfo(False)
        ec.disconnectHost()


