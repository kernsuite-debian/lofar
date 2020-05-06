#!/usr/bin/env python3

## RESET LCU power
## can only be used on LCU
##
## USE ONLY IF NORMAL SHUTDOWN IS NOT POSSIBLE
## usage: ./reset_lcu.py
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
        print("===============================================")
        print("ERROR, this script can only run on a station")
        print("===============================================")
    else:
        ec = EC(host)
        ec.connectToHost()
        time.sleep(1.0)
        ec.printInfo(True)
        ec.getPowerStatus()
        print("Turn off the mains voltage for 10 seconds")
        print("Use only if normal shutdown in not possible")
        if 'yes' == eval(input("Do you realy want to cycle LCU power [yes/no] : ")):
            print()
            print("================================")
            print("  cycle LCU power in 5 seconds  ")
            print("================================")
            time.sleep(5.0)
            ec.resetPower(ec.P_LCU)
            print("waiting 10 seconds")
            time.sleep(10.0)
            ec.getPowerStatus()
            print("waiting 10 seconds")
            time.sleep(10.0)
            ec.getPowerStatus()
            ec.printInfo(False)
            ec.disconnectHost()


