#!/usr/bin/env python
# coding: iso-8859-15
import re
import sys
import pgdb
from optparse import OptionParser
import getpass


INTRO = """
Created a file containing all antenna coordinates for the online software.
"""

def print_help():
    print("Usage: make_antenna_list [<stationname>]")

#
# findStationInfo(stationName)
#
def find_station_info(station_name):
    """
    Return all basic station info (eg. nr RSPboards) from a station.
    """
    pattern = re.compile("^"+station_name+"[ \t].*", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(open("../StaticMetaData/StationInfo.dat").read())
    if not match:
        raise "\nFatal error: "+station_name+" is not defined in file 'StationInfo.dat'"
    return match.group().split()


#
# MAIN
#
if __name__ == '__main__':
    parser = OptionParser("Usage: %prog [options] datafile")

    parser.add_option("-D", "--database",
                      dest="dbName",
                      type="string",
                      default="coordtest",
                      help="Name of StationCoordinates database to use")

    parser.add_option("-H", "--host",
                      dest="dbHost",
                      type="string",
                      default="dop50",
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
        sys.exit(1)

    filename = str(args[0])

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db.cursor()

    (name, stationID, stnType, int, lat, height, nrRSP, nrTBB, nrLBA, nrHBA, HBAsplit, LBAcal ) = findStationInfo(sys.argv[1])
    db = pgdb.connect(user="postgres", host="dop50", database="coordtest")

    print("#Stn	ID	Type	RSP	RCU	Pol	Position					Orientation")
    print("%s	%s	%s	%d	%d	-1	[%s,%s,%s]	[0,0,0]" % (name, stationID, "center", -1, -1, int, lat, height))

    for infoType in [ 'marker', 'lba', 'hba' ]:
        cursor = db.cursor()
        cursor.execute("select * from get_ref_objects(%s, %s)", (sys.argv[1], infoType))
        counter = 0
        while (1):
            record = cursor.fetchone()
            if record is None:
                break

            RSPnr = int(record[2]%100//4)
            print("%s	%s	%s%d	%d	%d	x	[%s,%s,%s]	[0,0,0]" % (name, stationID, infoType, int(record[2])%100, RSPnr, counter, record[3], record[4], record[5]))
            print("%s	%s	%s%d	%d	%d	y	[%s,%s,%s]	[0,0,0]" % (name, stationID, infoType, int(record[2])%100, RSPnr, counter+1, record[3], record[4], record[5]))
            counter = counter + 2
    db.close()
    sys.exit(1)
