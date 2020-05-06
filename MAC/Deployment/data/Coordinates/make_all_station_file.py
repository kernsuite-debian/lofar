#!/usr/bin/env python
# coding: iso-8859-15
#
# Make AntennaField.conf and iHBADeltas.conf file for given station and date
#

import sys
import pgdb
import pg
import numpy as np
import getpass
from optparse import OptionParser
from database import getDBname, getDBhost, getDBport, getDBuser


##
def print_help():
    print("Usage: make_all_station_file  date")
    print("    <date>      : yyyy.yy e.g. 2008.75 for Oct 1st 2008")

##
## write header to antennaField file
##
def writeAntennaFieldHeader(frame):
    # add to All Station config file
    dataStr = ''
    fileName = '../StaticMetaData/AntennaFields/All-AntennaFields.conf'
    file = open(fileName, 'w')

    dataStr += '#\n'
    dataStr += '# AntennaPositions for all stations\n'
    dataStr += '# %s target_date = %s\n' %(str(frame), sys.argv[1])
    dataStr += '# Created: %s\n' %(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    dataStr += '#\n'
    dataStr += '# NORMAL_VECTOR(1x3 matrix), floats\n'
    dataStr += '# ROTATION_MATRIX(3x3 matrix), order -> 1e row,2e row,3e row, floats\n'
    dataStr += '# CENTER_POS(1x3 matrix), floats\n'
    dataStr += '# ANTENNA_OFFSET(..x2x3), ..=number of antennas, order -> ANT0(Xpol(X,Y,Z),Ypol(X,Y,Z)),ANT1(.., floats\n'
    dataStr += '#\n'
    file.write(dataStr)
    file.close()
    return

##
## write normal vector
##
def writeNormalVector(station, anttype):
    try:
        cursor.execute("select * from get_normal_vector(%s, %s)", (station, anttype))
        vector = str(cursor.fetchone()[2]).replace('{','').replace('}','').split(',')
        vector = np.array([float(v) for v in vector])

        # write line to allStations file
        file = open('../StaticMetaData/AntennaFields/All-AntennaFields.conf', 'a')
        dataStr = '%s;%s;NORMAL_VECTOR;%6.6f;%6.6f;%6.6f\n' %\
                      (str(station), str(anttype), vector[0], vector[1], vector[2])
        file.write(dataStr)
        file.close()
    except:
        print('ERR, no normal-vector for %s, %s' %(station, anttype))
    return

#
# write rotation matrix
#
def writeRotationMatrix(station, anttype):
    try:
        cursor.execute("select * from get_rotation_matrix(%s, %s)", (station, anttype))
        matrix = str(cursor.fetchone()[2]).replace('{','').replace('}','').split(',')
        matrix = np.resize(np.array([float(m) for m in matrix]),(3,3))

        Shape = np.shape(matrix)
        
        # write line to allStations file
        file = open('../StaticMetaData/AntennaFields/All-AntennaFields.conf', 'a')
        dataStr = '%s;%s;ROTATION_MATRIX' %(str(station), str(anttype))
        for row in range(Shape[0]):
            for col in range(Shape[1]):
                dataStr += ';%10.10f' %(matrix[row, col])
        dataStr += '\n'
        file.write(dataStr)
        file.close()
    except:
        print('ERR, no rotation-matrix for %s, %s' %(station, anttype))
    return

##
## write antenna positions
##
def writeAntennaField(station, anttype, aPos):

    Shape = np.shape(aPos)
    Dims = len(Shape)
        
    # write line to allStations file
    file = open('../StaticMetaData/AntennaFields/All-AntennaFields.conf', 'a')
    if Dims == 1:
        dataStr = '%s;%s;CENTER_POS;%9.9f;%9.9f;%3.3f\n' %(str(station), str(anttype), aPos[0], aPos[1], aPos[2])
    elif Dims == 3:
        dataStr = '%s;%s;ANTENNA_OFFSET' %(str(station), str(anttype))
        for ant in range(Shape[0]):
            for pol in range(Shape[1]):
                for pos in range(Shape[2]):
                    dataStr += ';%6.6f' %(aPos[ant, pol, pos])
        dataStr += '\n'
    file.write(dataStr)
    file.close()
    return
    

##
## MAIN
##
if __name__ == '__main__':
    parser = OptionParser("""Usage: %prog [options] data
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

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    dbName = options.dbName
    dbHost = options.dbHost
    dbPort = options.dbPort
    dbUser = options.dbUser
    date = args[0]

    dbPassword = getpass.getpass()

    host = "{}:{}".format(dbHost, dbPort)

    db1 = pgdb.connect(user=dbUser, host=host, database=dbName, password=dbPassword)
    cursor = db1.cursor()

    # calling stored procedures only works from the pg module for some reason.
    db2 = pg.connect(user=dbUser, host=dbHost, dbname=dbName, port=dbPort, passwd=dbPassword)

    first = True
    for stationname in db2.query("select distinct o.stationname from object o inner join reference_coord r on r.id = o.id").getresult():
        station = stationname[0]
        date_years = float(sys.argv[1]) 
        frame = ''
    
        # from database select all antennas for given station and target-date
        cursor.execute("select * from get_gen_coord(%s, %f) order by objtype, number", (station, float(sys.argv[1])))
    
        # start with empty arrays
        aPosL = np.zeros((0,2,3))
        aPosH = np.zeros((0,2,3))
        
        aRefL  = [1.0,2.0,3.0]
        aRefH0 = [1.0,2.0,3.0]
        aRefH1 = [1.0,2.0,3.0]
        aRefH  = [1.0,2.0,3.0]
        # loop over all antennas
        while (1):
            record = cursor.fetchone()
            if record == None:
                break
            if first:     
                first = False
                frame = str(record[3])
                ## write positions to *.conf file
                writeAntennaFieldHeader(frame)
            
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
                                 
          
                if record[1] == 'LBA':
                    aPosL = np.concatenate((aPosL, [[even,odd]]), axis=0)
                
                elif record[1] == 'HBA' or record[1] == 'HBA0' or record[1] == 'HBA1':
                    aPosH = np.concatenate((aPosH, [[even,odd]]), axis=0)
                
        
        if int(np.shape(aPosL)[0]) == 0 or int(np.shape(aPosH)[0]) == 0:
            print('ERR, no data found for %s' %(station))
            exit(1)
             
        # do something with the data
        print('Making %s-AntennaField.conf with LBA shape=%s  HBA shape=%s' %(station, np.shape(aPosL), np.shape(aPosH)))
        aRef = None

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
    
    db1.close()
    db2.close()
    sys.exit(0)
