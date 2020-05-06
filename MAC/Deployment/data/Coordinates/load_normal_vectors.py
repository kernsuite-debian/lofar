#!/usr/bin/env python
# coding: iso-8859-15
import sys
import pgdb
import pg
import getpass
from optparse import OptionParser
from database import getDBname, getDBhost, getDBport, getDBuser


#
# getRotationLines
#
def get_lines(filename):
    """
    Returns a list containing all lines with normal vectors
    """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return [line.strip().split(',') for line in lines[3:]]


##
def get_normal_vector(line):
    # print line
    station = str(line[0]).upper().strip()
    anttype = str(line[1]).upper().strip()
    # make db vector [3]
    vector = "ARRAY[%f,%f,%f]" % (float(line[2]), float(line[3]), float(line[4]))

    return(station, anttype, vector)


#
# MAIN
#
if __name__ == '__main__':
    parser = OptionParser("Usage: %prog [options] filename")

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

    # check stationname
    cursor.execute("select name from station")
    stations = cursor.fetchall()
    print(stations)

    lines = get_lines(filename)
    for line in lines:
        (stationname, anttype, vector) = get_normal_vector(line)

        station = []
        station.append(stationname)
        if station not in stations:
            print("station %s is not a legal stationame" % stationname)
            sys.exit(1)
        try:
            db2.query("select * from add_normal_vector('%s','%s',%s)" %(stationname, anttype, vector))
            print("%s    %s    %s" %(stationname,anttype,vector))
        except:
            print('ERR, station=%s has no types defined' %(stationname))
        
    print(' Done')
    db1.close()
    db2.close()
    sys.exit(0)
