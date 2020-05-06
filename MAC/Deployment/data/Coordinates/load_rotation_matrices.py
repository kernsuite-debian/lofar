#!/usr/bin/env python
# coding: iso-8859-15
import sys
import pgdb
import pg
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
    return [line.strip().split(',') for line in lines[3:]]


##
def get_rotation_matrix(line):
    # print line
    station = str(line[0]).upper().strip()
    anttype = str(line[1]).upper().strip()
    # make db matrix [3][3]
    matrix = "ARRAY[[%f,%f,%f],[%f,%f,%f],[%f,%f,%f]]" %\
             (float(line[2]), float(line[3]), float(line[4]),
              float(line[5]), float(line[6]), float(line[7]),
              float(line[8]), float(line[9]), float(line[10]))

    return(station, anttype, matrix)


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

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    # print sys.argv
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    # check syntax of invocation
    # Expected syntax: load_measurement stationname objecttypes datafile
    #
    if (len(sys.argv) != 2):
        print("Syntax: %s datafile" % sys.argv[0])
        sys.exit(1)
    filename = str(sys.argv[1])

    lines = get_rotation_lines(filename)
    for line in lines:
        (stationname,anttype,matrix) = get_rotation_matrix(line)
        if stationname == 'CS001':
            print(stationname,'  ',anttype,'  ',matrix[0])

        # check stationname
        cursor.execute("select name from station")
        stations = cursor.fetchall()

        station = []
        station.append(stationname)
        if station not in stations:
            print("station %s is not a legal stationame" % stationname)
            sys.exit(1)
        try:
            db2.query("select * from add_rotation_matrix('%s','%s',%s)" %
                      (stationname, anttype, matrix))
            print(stationname,'  ',anttype,'  ',matrix)
        except:
            print('ERR, station=%s has no types defined' %(stationname))

    print(' Done')
    db1.close()
    db2.close()
    sys.exit(0)
