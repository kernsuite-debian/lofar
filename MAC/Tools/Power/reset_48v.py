#!/usr/bin/env python3

## RESET 48V powersupply
## can only be used on LCU
##
## usage: ./reset_48v.py
##
## Author: Pieter Donker (ASTRON)
## Last change: september 2014

from st_ec_lib import *
import sys
import time

VERSION = '1.2.1' # version of this script

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
        ec.resetPower(ec.P_48)
        # Start a 5-sec polling loop for the 48V to be ON again
        counter = 0
        print("Polling status every 5 sec now...")
        while (counter < 8):
            time.sleep(5)
            status=ec.getPowerStatus()
            if status == 0 :
                counter += 1
            else:
                break

        if (counter == 8):
            print("Could not complete power cycle in time...")
            exitstate=1
        else:
            print("Allowing 10 sec for RSP boards to startup after power reset...")
            time.sleep(10)
            exitstate=0

        ec.printInfo(False)
        ec.disconnectHost()
        sys.exit(exitstate)
