#!/usr/bin/env python
# coding: iso-8859-15
import re
import sys
import pgdb
import pg
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser


#
# getHeaderLines
#
def get_header_lines(filename):
    """
    Returns a list containing all lines that do NOT contains coordinate data.
    """
    pattern = re.compile("^[a-zA-Z]+.*", re.IGNORECASE | re.MULTILINE)
    answer = {}
    for line in pattern.findall(open(filename).read()):
        if line.count(';') == 1:
            (key, value) = line.split(';')
            answer[key] = value
    return answer


#
# getCoordLines
#
def get_coord_lines(filename):
    """
    Returns a list containing all lines with coordinates
    """
    pattern = re.compile("^[0-9]+;.*", re.IGNORECASE | re.MULTILINE)
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

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser

    # check syntax of invocation
    # Expected syntax: load_measurement stationname objecttypes datafile
    #
    if (len(sys.argv) != 2):
        print("Syntax: %s datafile" % sys.argv[0])
        sys.exit(1)

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db.cursor()

    # process metadata info
    absRef = derived = comment = ""
    stationname = objecttype = refSys = refFrame = method = date = pers1 = pers2 = pers3 = absRef = derived = comment = ""

    metadata = get_header_lines(args[0])
    if "stationname" in metadata:
        stationname = metadata["stationname"]
    if "infotype" in metadata:
        objecttype = metadata["infotype"]
    if "ref_system" in metadata:
        refSys = metadata["ref_system"]
    if "ref_frame" in metadata:
        refFrame = metadata["ref_frame"]
    if "method" in metadata:
        method = metadata["method"]
    if "measure_date" in metadata:
        date = metadata["measure_date"]
    if "person1" in metadata:
        pers1 = metadata["person1"]
    if "person2" in metadata:
        pers2 = metadata["person2"]
    if "person3" in metadata:
        pers3 = metadata["person3"]
    if "absolute_reference" in metadata:
        absRef = metadata["absolute_reference"]
    if "comment" in metadata:
        comment = metadata["comment"]

    # check some data against the database
    station = []
    station.append(stationname)
    objtype = []
    objtype.append(objecttype)

    # check stationname
    cursor.execute("select name from station")
    stations = cursor.fetchall()
    if station not in stations:
        print("station %s is not a legal stationame" % stationname)
        sys.exit(1)
    # check objecttype
    cursor.execute("select * from object_type")
    objecttypes = cursor.fetchall()
    if objtype not in objecttypes:
        print("objecttype must be one of: ",  objecttypes)
        sys.exit(1)
    # check person1
    cursor.execute("select name from personnel where name = '%s'" % pers1)
    if cursor.rowcount != 1:
        print("Person: '%s' is not in the personnel file, add it (Y/N)?" % pers1)
        if input().upper() == "Y":
            insertcmd = db.cursor()
            insertcmd.execute("insert into personnel values ('%s')" % pers1)
            db.commit()
        else:
            sys.exit(1)
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
    # check person3
    cursor.execute("select name from personnel where name = '%s'" % pers3)
    if cursor.rowcount != 1:
        print("Person: '%s' is not in the personnel file, add it (Y/N)?" % pers3)
        if input().upper() == "Y":
            insertcmd = db.cursor()
            insertcmd.execute("insert into personnel values ('%s')" % pers3)
            db.commit()
        else:
            sys.exit(1)
    db.close()

    # show metadata to user
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

    if input('Continue processing this file (Y/N)?').upper() != "Y":
        sys.exit(1)

    # calling stored procedures only works from the pg module for some reason.
    db = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)
    for cline in get_coord_lines(args[0]):
        (number, X, Y, Z, sX, sY, sZ) = cline.split(';')
        print(objecttype, number)
        # make sure the object exists
        db.query("select * from add_object('%s','%s',%s)" % (stationname, objecttype, number))
        # add the coord.
        db.query("""select * from add_ref_coord('%s','%s',%s,%s,%s,%s,%s,%s,%s,'%s',
        '%s','%s','%s','%s','%s','%s','%s','%s','%s')""" %
                 (stationname, objecttype, number, X, Y, Z, sX, sY, sZ, refSys, refFrame, method,
                  date, pers1, pers2, pers3, absRef, derived, comment))
