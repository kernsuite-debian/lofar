#!/usr/bin/env python
# coding: iso-8859-15
#
# Make AntennaField.conf and iHBADeltas.conf file for given station and date
#

import sys
import pgdb
import pg
from datetime import *
from copy import deepcopy
from math import *
import numpy as np
import getpass
from optparse import OptionParser
from database import getDBname, getDBhost, getDBport, getDBuser


def print_help():
    print("Usage: make_conf_files <stationname> date")
    print("    <date>      : yyyy.yy e.g. 2008.75 for Oct 1st 2008")


## write hba deltas to a File
## Use new-style Blitz format (Blits 0.11) for array sizes, e.g. (0,2) x (0,3)
## For a 3 by 4 array
##
def writeHBADeltas(station,deltas):
    cursor.execute("select * from get_field_rotation(%s, %s)", (station, 'HBA'))
    record = cursor.fetchone()
    if record == None:
        cursor.execute("select * from get_field_rotation(%s, %s)", (station, 'HBA0'))
        record = cursor.fetchone()
        if record == None:
            print("Could not find field rotation for station",station)
            exit(1)
    rotation=degrees(record[2])
    filename = '../StaticMetaData/iHBADeltas/%s-iHBADeltas.conf' %(str(station).upper())
    f = open(filename,'w')
    f.write('#\n')
    f.write('# iHBADeltas for %s\n' %(str(station).upper()))
    f.write('# Created: %s\n' %(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    f.write('# Rotation: %3d degree\n' %rotation)
    f.write('#\n')
    f.write('HBADeltas\n')
    f.write('(0,%d) x (0,%d) [\n' %(np.shape(deltas)[0]-1,np.shape(deltas)[1]-1))
    for i in range(np.shape(deltas)[0]):
        f.write('  ')
        for j in range(np.shape(deltas)[1]):
            f.write('%8.3f' %(deltas[i][j]))
        f.write('\n')
    f.write(']\n')
    f.close()
    return

##
## write header to antennaField file
##
def writeAntennaFieldHeader(station,frame):
    # add to Station config file
    dataStr = ''
    fileName = '../StaticMetaData/AntennaFields/'+ station + '-AntennaField.conf'
    file = open(fileName, 'w')

    dataStr += '#\n'
    dataStr += '# AntennaPositions for %s\n' %(station)
    dataStr += '# %s target_date = %s\n' %(str(frame), sys.argv[2])
    dataStr += '# Created: %s\n' %(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dataStr += '#\n'
    file.write(dataStr)
    file.close()

    return

##
## write normal vector to antennaField file, in blitz format
## Use new-style Blitz format (Blits 0.11) for array sizes, e.g. (0,2) x (0,3)
## For a 3 by 4 array
##
def writeNormalVector(station, anttype):
    try:
        cursor.execute("select * from get_normal_vector(%s, %s)", (station, anttype))
        vector = str(cursor.fetchone()[2]).replace('{','').replace('}','').split(',')
        vector = np.array([float(v) for v in vector])

        dataStr = ''
        fileName = '../StaticMetaData/AntennaFields/'+ station + '-AntennaField.conf'
        file = open(fileName, 'a')

        if len(anttype) > 0:
            dataStr += '\nNORMAL_VECTOR '+str(anttype)+'\n'

        Shape = np.shape(vector)
        Dims = len(Shape)

        dataStr += '(0,' + str(Shape[0]-1) + ')'
        for dim in range(1,Dims):
            dataStr += ' x (0,' + str(Shape[dim]-1) + ')'

        dataStr += ' [ %10.6f %10.6f %10.6f ]\n' %(vector[0], vector[1], vector[2])

        file.write(dataStr)
        file.close()
    except:
        print('ERR, no normal-vector for %s, %s' %(station, anttype))
    return

##
## write rotation matrix to antennaField file, in blitz format
## Use new-style Blitz format (Blits 0.11) for array sizes, e.g. (0,2) x (0,3)
## For a 3 by 4 array
##
def writeRotationMatrix(station, anttype):
    try:
        cursor.execute("select * from get_rotation_matrix(%s, %s)", (station, anttype))
        matrix = str(cursor.fetchone()[2]).replace('{','').replace('}','').split(',')
        matrix = np.resize(np.array([float(m) for m in matrix]),(3,3))

        dataStr = ''
        fileName = '../StaticMetaData/AntennaFields/'+ station + '-AntennaField.conf'
        file = open(fileName, 'a')
        if len(anttype) > 0:
            dataStr += '\nROTATION_MATRIX '+str(anttype)+'\n'

        Shape = np.shape(matrix)
        Dims = len(Shape)

        dataStr +=  '(0,' + str(Shape[0]-1) + ')'
        for dim in range(1,Dims):
            dataStr += ' x (0,' + str(Shape[dim]-1) + ')'

        dataStr += ' [\n'
        for row in range(Shape[0]):
            for col in range(Shape[1]):
                dataStr += '%14.10f ' %(matrix[row, col])
            dataStr += '\n'
        dataStr += ']\n'
        file.write(dataStr)
        file.close()
    except:
        print('ERR, no rotation-matrix for %s, %s' %(station, anttype))
    return

##
## write antenna positions to antennaField file, in blitz format
## Use new-style Blitz format (Blits 0.11) for array sizes, e.g. (0,2) x (0,3)
## For a 3 by 4 array
##
def writeAntennaField(station, anttype, aPos):
    dataStr = ''
    fileName = '../StaticMetaData/AntennaFields/'+ station + '-AntennaField.conf'
    file = open(fileName, 'a')
    if len(anttype) > 0:
        dataStr += '\n'+str(anttype)+'\n'

    Shape = np.shape(aPos)
    Dims = len(Shape)

    dataStr += '(0,' + str(Shape[0]-1) + ')'
    for dim in range(1,Dims):
        dataStr += ' x (0,' + str(Shape[dim]-1) + ')'

    if Dims == 1:
        dataStr += ' [ %10.9f %10.9f %10.3f ]\n' %\
                    (aPos[0], aPos[1], aPos[2])
    elif Dims == 3:
        dataStr += ' [\n'
        for ant in range(Shape[0]):
            for pol in range(Shape[1]):
                for pos in range(Shape[2]):
                    dataStr += '%10.6f ' %(aPos[ant, pol, pos])
                if pol < (Shape[1] - 1):
                    dataStr += '  '
            dataStr += '\n'
        dataStr += ']\n'
    else: print('ERROR, no data for %s, %s' %(station, anttype))
    file.write(dataStr)
    file.close()
    return


##
## MAIN
##
if __name__ == '__main__':
    parser = OptionParser("""Usage: %prog [options] station data
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

    if len(sys.argv) != 3:
        print_help()
        sys.exit(1)

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser
    station = args[0].upper()
    date_years = args[1]

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    station = str(sys.argv[1]).upper()
    date_years = float(sys.argv[2]) 

    frame = ''

    # from database select all antennas for given station and target-date
    # The ''order by'' statement is needed to prevent mixup of even/odd pairs
    # as was seen on sas001 (Arno)
    cursor.execute("select * from get_gen_coord(%s, %f) order by objtype, number", (station, float(sys.argv[2])))

    # start with empty arrays
    aPosL = np.zeros((0,2,3))
    aPosH = np.zeros((0,2,3))

    aRefL  = [0.0,0.0,0.0]
    aRefH0 = [0.0,0.0,0.0]
    aRefH1 = [0.0,0.0,0.0]
    aRefH  = [0.0,0.0,0.0]
    # loop over all antennas
    while (1):
        record = cursor.fetchone()
        if record == None:
            break
        #print record
        # handle center coordinates
        if record[1] == 'CLBA':
            aRefL = [record[4],record[5],record[6]]
        elif  record[1] == 'CHBA0':
            aRefH0 = [record[4],record[5],record[6]]
        elif  record[1] == 'CHBA1':
            aRefH1 = [record[4],record[5],record[6]]
        elif  record[1] == 'CHBA':
            aRefH = [record[4],record[5],record[6]]
        else:
            # get coordinates for even antenna(X)
            even = [record[4],record[5],record[6]]

            # get coordinates for odd antenna(Y)
            record = cursor.fetchone()
            if record == None:
                break
            odd = [record[4],record[5],record[6]]

            # get used frame for translation
            frame = str(record[3])

            if record[1] == 'LBA':
                aPosL = np.concatenate((aPosL, [[even,odd]]), axis=0)

            elif record[1] == 'HBA' or record[1] == 'HBA0' or record[1] == 'HBA1':
                aPosH = np.concatenate((aPosH, [[even,odd]]), axis=0)

    if int(np.shape(aPosL)[0]) == 0 or int(np.shape(aPosH)[0]) == 0:
        print('ERR, no data found for %s' %(station))
        exit(1)

    # do somthing with the data
    print('Making %s-AntennaField.conf with LBA shape=%s  HBA shape=%s' %(station, np.shape(aPosL), np.shape(aPosH)))

    aRef = None

    ## write positions to *.conf file
    writeAntennaFieldHeader(station,frame)

    # write LBA information to AntennaPos.conf
    writeNormalVector(station, 'LBA')
    writeRotationMatrix(station, 'LBA')
    writeAntennaField(station, 'LBA', aRefL)
    aOffset = aPosL - [[aRefL,aRefL]]
    writeAntennaField(station, '', aOffset)

    # write HBA information to AntennaPos.conf
    # if not a core station
    if station[0] != 'C':
        writeNormalVector(station, 'HBA')
        writeRotationMatrix(station, 'HBA')
    writeAntennaField(station, 'HBA', aRefH)
    aOffset = aPosH - [[aRefH,aRefH]]
    writeAntennaField(station, '', aOffset)


    # if core station add also information for HBA0 and HBA1 fields
    if station[0] == 'C':
        # write information for HBA0
        writeNormalVector(station, 'HBA0')
        writeRotationMatrix(station, 'HBA0')
        writeAntennaField(station, 'HBA0', aRefH0)

        # write information for HBA1
        writeNormalVector(station, 'HBA1')
        writeRotationMatrix(station, 'HBA1')
        writeAntennaField(station, 'HBA1', aRefH1)


    ## get HBADeltas and write to file
    print('Making %s-iHBADeltas.conf' %(station))
    # if core station HBADeltas is array 32x3
    if station[0] == 'C':
        try:
            cursor.execute("select * from get_hba_deltas(%s, %s)", (station, 'HBA0'))
            record = cursor.fetchone()
            deltas = str(record[2]).replace('{','').replace('}','').split(',')

            cursor.execute("select * from get_hba_deltas(%s, %s)", (station, 'HBA1'))
            record = cursor.fetchone()
            deltas += str(record[2]).replace('{','').replace('}','').split(',')
            deltas = np.resize(np.array([float(d) for d in deltas]),(32,3))
            #print deltas
            writeHBADeltas(station,deltas)
        except:
            print('ERR, no hba-deltas for %s' %(station))
#            sys.exit(1)
    # if not core station HBADeltas is array 16x3
    else:
        try:
            cursor.execute("select * from get_hba_deltas(%s, %s)", (station,'HBA'))
            record = cursor.fetchone()
            deltas = str(record[2]).replace('{','').replace('}','').split(',')
            deltas = np.resize(np.array([float(d) for d in deltas]),(16,3))
            #print deltas
            writeHBADeltas(station,deltas)
        except:
            print('ERR, no hba-deltas for %s' %(station))
 #           sys.exit(1)

    db1.close()
    db2.close()
    sys.exit(0)
