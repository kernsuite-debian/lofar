#!/usr/bin/env python
# coding: iso-8859-15
from __future__ import print_function
import re
import sys
import pgdb
import pg
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser


#
# getCoordLines
#
def get_coord_lines(filename):
    """
    Returns a list containing all lines with coordinates
    """
    pattern = re.compile(r"^[HLC]{1}[0-9A-Z ]+,.*", re.IGNORECASE | re.MULTILINE)
    # print pattern.findall(open(filename).read())
    return [line for line in pattern.findall(open(filename).read())]


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

    if len(args) != 1:
        parser.print_help()
        sys.exit(0)

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser
    filename = args[0]

    dbPassword = getpass.getpass()

    # check syntax of invocation
    # Expected syntax: load_measurement stationname objecttypes datafile
    #
    if (len(sys.argv) != 2):
        print("Syntax: %s datafile" % sys.argv[0])
        sys.exit(1)
    filename = str(sys.argv[1])
    stationname = filename[ filename.find('/')+1 : filename.find('/')+1 + 5].upper()

    objecttype = 'LBA, HBA'
    refSys = 'ETRS89'
    refFrame = 'ETRF89'
    method = 'derived'
    date = '2010-01-01'
    pers1 = 'Brentjens'
    pers2 = 'Donker'
    pers3 = ''
    derived = ''
    absRef = ''
    comment = 'expected coordinates, Brentjens'
    # check some data against the database
    station = []
    station.append(stationname)

    host = "{}:{}".format(dbHost, dbPort)

    db = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db.cursor()

    # check person2
    cursor.execute("select name from personnel where name = '%s'" % pers2)
    if cursor.rowcount != 1:
        print("Person: '%s' is not in the personnel file, add it (Y/N)?" % pers2)
        if input().upper() == "Y":
            insertcmd = db.cursor()
            insertcmd.execute("insert into personnel values ('%s')" % pers2)
            db.commit()
        else:
            sys.exit(1)

    # check stationname
    cursor.execute("select name from station")
    stations = cursor.fetchall()
    if station not in stations:
        print("File %s does not refer to a station; continuing with next file" % filename)
        sys.exit()
    db.close()

    # show metadata to user
    print('file                 : ', filename)
    print('station              : ', stationname)
    print('object types         : ', objecttype)
    print('reference system     : ', refSys)
    print('reference frame      : ', refFrame)
    print('measurement method   : ', method)
    print('measurement date     : ', date)
    print('person 1             : ', pers1)
    print('person 2             : ', pers2)
    print('person 3             : ', pers3)
    print('absolute reference   : ', absRef)
    print('comment              : ', comment)

    # if raw_input('Continue processing this file (Y/N)?').upper() != "Y":
    #   sys.exit(1)

    print('processing ', end=' ')
    sys.stdout.flush()
    # calling stored procedures only works from the pg module for some reason.
    db = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    sX = sY = sZ = 0
    pol = 2  # number of polarizations
    for cline in get_coord_lines(sys.argv[1]):
        if stationname == 'CS002':
            print(cline)
        (name, X, Y, Z, P, Q, R, rcuX, rcuY) = cline.strip().split(',')
        # set object type (LBA, HBA, HBA0 or HBA1)
        objecttype = name.strip()
        print(objecttype, end=' ')

        if(objecttype == 'CLBA' or objecttype == 'CHBA0' or
           objecttype == 'CHBA1' or objecttype == 'CHBA'):
            number = -1
            # make sure the object exists
            db.query("select * from add_object('%s','%s',%s)" % (stationname, objecttype, number))
            # add the coord.
            db.query("select * from add_ref_coord('%s','%s',%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %
                     (stationname, objecttype, number,
                      X, Y, Z, sX, sY, sZ,
                      refSys, refFrame, method, date,
                      pers1, pers2, pers3, absRef, derived, comment))
            continue  # next line

        antType = name[:1]

        if antType == 'L':
            objecttype = 'LBA'

        elif antType == 'H':
            antNumber = int(name[1:])
            # if core station make 2 hba fields of 24 tiles each
            if stationname[:1] == 'C':
                if antNumber < 24:
                    objecttype = 'HBA0'
                else:
                    objecttype = 'HBA1'
            else:                      # remote station or internation station one hba filed
                objecttype = 'HBA'
        else:
           print('??',name, end=' ')

        sys.stdout.flush()

        # add RCU X coordinates
        number = int(name[1:]) * pol
        # print objecttype, number
        # make sure the object exists
        db.query("select * from add_object('%s','%s',%s)" % (stationname, objecttype, number))
        # add the coord.
        db.query("select * from add_ref_coord('%s','%s',%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %
                 (stationname, objecttype, number, X, Y, Z, sX, sY, sZ, refSys, refFrame, method,
                  date, pers1, pers2, pers3, absRef, derived, comment))

        # add RCU Y coordinates
        number = (int(name[1:]) * pol) + 1
        # print objecttype, number
        # make sure the object exists
        db.query("select * from add_object('%s','%s',%s)" % (stationname, objecttype, number))
        # add the coord.
        db.query("select * from add_ref_coord('%s','%s',%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %
                 (stationname, objecttype, number, X, Y, Z, sX, sY, sZ, refSys, refFrame, method,
                  date, pers1, pers2, pers3, absRef, derived, comment))
    print(' Done')
