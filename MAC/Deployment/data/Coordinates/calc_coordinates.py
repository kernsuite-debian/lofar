#!/usr/bin/env python
# coding: iso-8859-15
import sys
import pgdb
import pg
from copy import deepcopy
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser

INTRO = """
Conversion between ETRS89 and ITRS2000 coordinates based on
 Memo : Specifications for reference frame fixing in the analysis of a
        EUREF GPS campaign
 By Claude Boucher and Zuheir Altamimi

 which is available from EUREF

 In this utility I use the translational coefficients obtained by method "A" in
 section 4 and the rotational coefficients in section 5, both for the 2000 (00)
 reference frame.
"""


def subtract(a, b):
    return [x - y for x, y in zip(a, b)]

def print_help():
    print("Usage: calc_coordinates <stationname> <objecttype> date")
    print("    <objecttype>: LBA|HBA|HBA0|HBA1|marker")
    print("    <date>      : yyyy.yy e.g. 2008.75 for Oct 1st 2008")

def solve(m, y):
    """
    solve Mx=y. The algorithm is Gauss-Jordan elimination
    without pivoting, which is allowed in this case as M is
    dominated by the diagonal.
    """
    dim = len(y)
    a = deepcopy(m)
    sol = deepcopy(y)
    if (len(a) != len(a[0])) or len(a[0]) != len(y):
        raise 'Incompatible dimensions'
    for row in range(dim):
        scale = 1./float(a[row][row])
        a[row] = [x*scale for x in a[row]]
        sol[row] = scale*float(sol[row])
        for ix in range(dim):
            if ix != row:
                factor = float(a[ix][row])
                a[ix] = subtract(a[ix], [factor*float(x) for x in a[row]])
                a[ix][row] = 0.0
                sol[ix] -= factor*float(sol[row])
    return sol


def convert(xetrs, date_years, trans):
    """
    Solve equation:
     /X\Etrs   /T0\  = [[  1     , -R2*dt,  R1*dt]  /X\Itrs2000
     |Y|     - |T1|     [  R2*dt ,  1    , -R0*dt]  |Y|
     \Z/       \T2/     [ -R1*dt , R0*dt ,  1]]     \Z/
    """
    #
    # get translate parameters from database
    # ref-frame    = trans[0]
    # TOO          = trans[1:4]   = Tx,Ty,Tz
    # mas          = trans[5:8]   = Rx,Ry,Rz
    # diagonal(sf) = trans[4] + 1 = sf
    #

    t00 = [float(t) for t in trans[1:4]]  # meters
    rdot00 = [float(t) for t in trans[5:8]]  # mas
    # print "T00=[%e %e %e]    Rdot00=[%e %e %e]" % (t00[0], t00[1], t00[2],
    #                                                rdot00[0], rdot00[1], rdot00[2])

    dt = date_years - 1989.0
    # print 'date_years=%f  dt=%f' %(date_years, dt)
    sf = float(trans[4]) + 1.
    # print 'sf=',sf
    matrix = [[sf, -rdot00[2]*dt, rdot00[1]*dt],
              [rdot00[2]*dt, sf, -rdot00[0]*dt],
              [-rdot00[1]*dt, rdot00[0]*dt, sf]]
    xshifted = subtract(xetrs, t00)
    # print "Matrix=", matrix
    return solve(matrix, xshifted)


#
# MAIN
#
if __name__ == '__main__':
    parser = OptionParser("""Usage: %prog [options]  <stationname> <objecttype> date
    <objecttype>: LBA|HBA|HBA0|HBA1|marker
    <date>      : yyyy.yy e.g. 2008.75 for Oct 1st 2008""")

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
    if len(args) != 3:
        parser.print_help()
        sys.exit(1)

    station_name = str(args[0]).upper()
    object_type = str(args[1]).upper()
    date_years = float(args[2])

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    cursor.execute("select * from get_transformation_info('ITRF2005')")
    trans = cursor.fetchone()

    cursor.execute("select * from get_ref_objects(%s, %s)", (str(sys.argv[1]).upper(), str(sys.argv[2]).upper()))
    
    print("\n%s    %s    %8.3f" %(str(sys.argv[1]).upper(), str(sys.argv[2]).upper(),float(sys.argv[3])))

    while (1):
        record = cursor.fetchone()
        if record is None:
            print('record even = None')
            break
        # print record
        XEtrs = [float(record[4]),
                 float(record[5]),
                 float(record[6])]
        # print 'XEtrs=',XEtrs
        XItrs2000 = convert(XEtrs, date_years, trans)

        # write output to generated_coord ??
        print("%s %d    %14.6f    %14.6f    %14.6f" %(str(record[1]), record[2], XItrs2000[0], XItrs2000[1],XItrs2000[2]))
        db2.query("select * from add_gen_coord('%s','%s',%s,%s,%s,%s,%s,'%s')" %\
                 (record[0], record[1], record[2], XItrs2000[0], XItrs2000[1], XItrs2000[2], date_years, 'ITRF2005'))
	#record = None
    
    db1.close()
    db2.close()
    sys.exit(0)
