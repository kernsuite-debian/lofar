#!/usr/bin/env python
import re
import pg
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser


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
# getStationList
#
def get_station_list():
    """
    Returns a list containing all stationnames
    """
    pattern = re.compile("^[A-Z]{2}[0-9]{3}[ \t].*", re.IGNORECASE | re.MULTILINE)
    return [station.split()[0] for station in
            pattern.findall(open("../StaticMetaData/StationInfo.dat").read())]


#
# MAIN
#
if __name__ == '__main__':
    parser = OptionParser("Usage: %prog [options]")

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

    print("Connecting to database ", dbName)

    db = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    pol = 2 # number of polarizations
    for station in get_station_list():
        print(find_station_info(station))
        if (len(find_station_info(station)) < 13):
            continue

        (name, stationID, stnType, long, lat, height, nrRSP, nrTBB, nrLBA, nrHBA, nrPowecs, HBAsplit, LBAcal, Aartfaac ) = find_station_info(station)

        if height[0] != '0':
            print("updating %s to the coordinate database " % station)
            for lba in range(0, int(nrLBA)*2):
                db.query("select * from add_object('%s', '%s', %d)" % (name, "LBA", lba))
            db.query("select * from add_object('%s', '%s', %d)" % (name, "CLBA", -1))
            if HBAsplit == 'Yes':
                for hba in range(0, int(nrHBA)):
                    db.query("select * from add_object('%s', '%s', %d)" % (name, "HBA0", hba))
                db.query("select * from add_object('%s', '%s', %d)" % (name, "CHBA0", -1))
                for hba in range(int(nrHBA), int(nrHBA)*2):
                    db.query("select * from add_object('%s', '%s', %d)" % (name, "HBA1", hba))
                db.query("select * from add_object('%s', '%s', %d)" % (name, "CHBA1", -1))
            else:
                for hba in range(0, int(nrHBA)*2):
                    db.query("select * from add_object('%s', '%s', %d)" % (name, "HBA", hba))
                db.query("select * from add_object('%s', '%s', %d)" % (name, "CHBA", -1))
# ... to be continued
