#!/usr/bin/env python
# coding: iso-8859-15
import sys
import pgdb
import pg
from math import sin, cos
import numpy as np
from optparse import OptionParser
import getpass
from database import getDBname, getDBhost, getDBport, getDBuser


##
def get_rotation(station, anttype, cursor):
    cursor.execute("select * from get_field_rotation(%s, %s)", (station, anttype))
    record = cursor.fetchone()
    if record != None:
        rotation = float(record[2])
        return(rotation)
    print("Could not find field rotation for station",station,anttype)
    exit(1)


##
def get_rotation_matrix(station, anttype, cursor):
    matrix = np.zeros((3, 3))
    cursor.execute("select * from get_rotation_matrix(%s, %s)", (station, anttype))
    record = cursor.fetchone()
    if record != None:
        record = str(record[2]).replace('{', '').replace('}', '').split(',')
        print(record)
        cnt = 0
        for row in range(3):
            for col in range(3):
                matrix[row][col] = float(record[cnt])
                cnt += 1
    return(matrix)


##
def get_stations(anttype, cursor):
    stations = []
    query = """SELECT o.stationname FROM object o INNER JOIN rotation_matrices r ON r.id = o.id WHERE o.type='%s'""" % (anttype)
    print(query)
    cursor.execute(query)
    stations = cursor.fetchall()
    print(stations)
    return(stations)


##
def make_db_matrix(matrix):
    shape = np.shape(matrix)
    # make db matrix [16][3]
    dbmatrix = "ARRAY["
    for row in range(shape[0]):
        dbmatrix += "["
        for col in range(shape[1]):
            dbmatrix += "%f" % (float(matrix[row][col]))
            if (col + 1) < shape[1]:
                dbmatrix += ","
        dbmatrix += "]"
        if (row + 1) < shape[0]:
                dbmatrix += ","
    dbmatrix += "]"
    return(dbmatrix)


##
def rotate_pqr(coord, rad=0):
    matrix = np.array([[cos(rad), sin(rad), 0],
                       [-sin(rad), cos(rad), 0],
                       [0, 0, 1]])
    return(np.inner(matrix, coord))


##
def rotate_pqr2etrf(coord, matrix):
    return(np.inner(matrix, coord))


##
if __name__ == "__main__":
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

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    ideltas = np.zeros((16, 3))
    deltas = np.zeros((16, 3))

    deltas_other = np.array([[-1.875,  1.875, 0.0],
                             [-0.625,  1.875, 0.0],
                             [0.625,  1.875, 0.0],
                             [1.875,  1.875, 0.0],
                             [-1.875,  0.625, 0.0],
                             [-0.625,  0.625, 0.0],
                             [0.625,  0.625, 0.0],
                             [1.875,  0.625, 0.0],
                             [-1.875, -0.625, 0.0],
                             [-0.625, -0.625, 0.0],
                             [0.625, -0.625, 0.0],
                             [1.875, -0.625, 0.0],
                             [-1.875, -1.875, 0.0],
                             [-0.625, -1.875, 0.0],
                             [0.625, -1.875, 0.0],
                             [1.875, -1.875, 0.0]], float)
    
    deltas_de601 = np.array([[-1.875, -1.875, 0.0],
                             [-1.875, -0.625, 0.0],
                             [-1.875,  0.625, 0.0],
                             [-1.875,  1.875, 0.0],
                             [-0.625, -1.875, 0.0],
                             [-0.625, -0.625, 0.0],
                             [-0.625,  0.625, 0.0],
                             [-0.625,  1.875, 0.0],
                             [0.625, -1.875, 0.0],
                             [0.625, -0.625, 0.0],
                             [0.625,  0.625, 0.0],
                             [0.625,  1.875, 0.0],
                             [1.875, -1.875, 0.0],
                             [1.875, -0.625, 0.0],
                             [1.875,  0.625, 0.0],
                             [1.875,  1.875, 0.0]], float)

    for anttype in ('HBA', 'HBA0', 'HBA1'):
        print(anttype)
        for station in get_stations(anttype, cursor):
            print(station[0])

            # DE601 hba's have other placing 90deg ccw
            if station[0] == 'DE601':
                deltas = deltas_de601
                print(deltas)
            else:
                deltas = deltas_other

            rad = get_rotation(station, anttype, cursor)
            matrix = get_rotation_matrix(station, anttype, cursor)
            inr = 0
            for d in deltas:
                pqr = rotate_pqr(d, rad)
                etrf = rotate_pqr2etrf(pqr, matrix)
                ideltas[inr] = etrf
                inr += 1
            matrix = make_db_matrix(ideltas)
            db2.query("select * from add_hba_deltas('%s','%s',%s)" % (station[0], anttype, matrix))
