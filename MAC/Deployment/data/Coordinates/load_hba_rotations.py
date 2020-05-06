#!/usr/bin/env python
# coding: iso-8859-15
import sys
import pgdb
import pg
from math import pi
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser


#
# getRotationLines
#
def get_rotation_lines(filename):
    """
    Returns a list containing all lines with rotations
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return [line.strip().split(',') for line in lines[1:]]


##
def get_rotation(line):
    hba0 = hba1 = None
    station = str(line[0]).upper()
    if line[1] != '':
        hba0 = (int(line[1])/360.) * 2. * pi
    if line[2] != '':
        hba1 = (int(line[2])/360.) * 2. * pi
    return(station, hba0, hba1)


#
# MAIN
#
if __name__ == '__main__':
    parser = OptionParser("Usage: %prog [options] datafile")

    parser.add_option("-D", "--database",
                      dest="dbName",
                      type="string",
                      default=getDBname(),
                      help="Name of StationCoordinates database to use")

    parser.add_option("-H", "--host",
                      dest="dbHost",
                      type="string",
                      default=getDBhost(),
                      help="Hostname of StationCoordinates database")

    parser.add_option("-P", "--port",
                      dest="dbPort",
                      type="int",
                      default=getDBport(),
                      help="Port of StationCoordinates database")

    parser.add_option("-U", "--user",
                      dest="dbUser",
                      type="string",
                      default=getDBuser(),
                      help="Username of StationCoordinates database")

    # parse arguments

    (options, args) = parser.parse_args()

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser

    # print sys.argv
    if len(args) != 1:
        parser.print_help()

    # check syntax of invocation
    # Expected syntax: load_measurement stationname objecttypes datafile
    #
    if (len(sys.argv) != 2):
        print("Syntax: %s datafile" % sys.argv[0])
        sys.exit(1)

    filename = str(args[0])

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    lines = get_rotation_lines(filename)
    for line in lines:
        (stationname, rotation0, rotation1) = get_rotation(line)

        # check stationname
        cursor.execute("select name from station")
        stations = cursor.fetchall()

        station = []
        station.append(stationname)
        if station not in stations:
            print("station %s is not a legal stationame" % stationname)
            sys.exit(1)
        try:
            if rotation1 == None:
                db2.query("select * from add_field_rotation('%s','HBA',%s)" %( stationname, rotation0))
                print('station %s  rotation=%f' %(stationname,rotation0))
            if rotation0 != None and rotation1 != None:
                db2.query("select * from add_field_rotation('%s','HBA0',%s)" %( stationname, rotation0))
                db2.query("select * from add_field_rotation('%s','HBA1',%s)" %( stationname, rotation1))
                print('station %s  rotation0=%f  rotation1=%f' %(stationname,rotation0, rotation1))
        except:
            print('WARN, station %s has no HBA types defined yet' %(stationname))
    print(' Done')
    db1.close()
    db2.close()
    sys.exit(0)
