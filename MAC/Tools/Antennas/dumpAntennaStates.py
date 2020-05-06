#!/usr/bin/env python3
# coding: iso-8859-15
import sys
import pg
import getpass
from optparse import OptionParser

#
# MAIN
#
if __name__ == '__main__':
    """
    dumpAntennaStates dumps teh state of all antennas as set in OTDB into a
    file (default file is 'hardware_states.out') so it can be used to restore
    that info in a station's WinCC database. Use putback_pvss.py for that.
    """

    parser = OptionParser("Usage: %prog [options]")
    parser.add_option("-D", "--database",
                      dest="dbName",
                      type="string",
                      default="LOFAR_4",
                      help="Name of OTDB database to use")

    parser.add_option("-H", "--host",
                      dest="dbHost",
                      type="string",
                      default="sasdb.control.lofar",
                      help="Hostname of OTDB database")

    parser.add_option("-P", "--port",
                      dest="dbPort",
                      type="int",
                      default="5432",
                      help="Port of OTDB database")

    parser.add_option("-U", "--user",
                      dest="dbUser",
                      type="string",
                      default="postgres",
                      help="Username of OTDB database")

    parser.add_option("-F", "--file",
                      dest="outfile",
                      type="string",
                      default="/globalhome/lofarsys/AntennaInfo/hardware_states.out",
                      help="File to write the result to")

    # parse arguments

    (options, args) = parser.parse_args()

    if not options.dbName:
        print("Provide the name of OTDB database to use!")
        print()
        parser.print_help()
        sys.exit(0)

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser
    filename = options.outfile

    dbPassword = getpass.getpass()

    # calling stored procedures only works from the pg module for some reason.
    print("Connecting...", end=' ')
    otdb = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    print("\nQuerying database...", end=' ')
    HWstates = otdb.query("select p.pvssname,k.value,k.time from pickvt k " +
                          "left join picparamref p on p.paramid=k.paramid " +
                          "where pvssname like '%%RCU%%state' OR pvssname like '%%BA%%state' " +
                          "order by p.pvssname,k.time").dictresult()
    otdb.close()

    print("\nWriting file...", end=' ')
    file = open(filename, 'w')
    for rec in HWstates:
        file.write("%s | %s | %s\n" % (rec['pvssname'], rec['value'], rec['time']))
    file.close()
    print("\nDone")

    sys.exit(0)
