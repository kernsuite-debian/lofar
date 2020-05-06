#!/usr/bin/env python
# coding: iso-8859-15
import pg
import getpass
from optparse import OptionParser
from database import getDBname, getDBhost, getDBport, getDBuser


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

    db = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    print(db.query("select * from reference_coord"))
    db.close()
