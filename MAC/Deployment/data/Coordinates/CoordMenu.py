#!/usr/bin/env python
# P.Donker ASTRON
# and Arno Schoenmakers the Great
import sys
import pg
from subprocess import Popen
import os
import getpass
from optparse import OptionParser
from database import getDBname, getDBhost, getDBport, getDBuser

VERSION = '0.0.2' # version of this script
default_targetdate='2009.5'

def menu():
    print("""
    |=====================================|
    | Coordinates menu                    |
    |=====================================|
    | 0   do all (1,2,3,4,5,6,7,9,11)     |
    | 1   destroy and create CDB          |
    | 2   create CDB objects              |
    | 3   load all normal-vectors         |
    | 4   load all rotation matrices      |
    | 5   load all hba_rotations          |
    | 6   calculate all HBADeltas         |
    | 7   load all ETRF(expected) files   |
    | 8   load one measurement file       |
    | 9   transform all ETRF to ITRF      |
    | 10  transform one ETRF to ITRF      |
    | 11  make all conf files             |
    | 12  make one conf file              |
    | Q   quit                            |
    |_____________________________________|
    """)


def get_input_with_default(prompt, default_value):
    answer = default_value
    try:
        input = raw_input # Python2 and Python3 compatible
    except NameError:
        pass
    answer = input(prompt+" ["+str(default_value)+"]: ")
    if (len(answer) == 0):
        answer = default_value
    return answer


def create_cdb():
    print('Creating new database')
    res = Popen('./create_CDB.sh').wait()
    print(res)


def create_cdb_objects():
    print('Creating database objects')
    res = Popen('./create_CDB_objects.py').wait()
    print(res)


def load_normal_vectors():
    print('Loading normal vectors')
    filename = get_input_with_default("enter filename to load", "data/normal_vectors.dat")
    if len(filename) == 0:
        print('Error, No filename given')
        sys.exit()
    if not os.path.exists(filename):
        print("File does not exist")
        sys.exit()
    res = Popen(['./load_normal_vectors.py', filename]).wait()
    if (res != 0):
        sys.exit(1)
    # time.sleep(3)


def load_rotation_matrices():
    print('Loading rotation matrices')
    filename = get_input_with_default("enter filename to load", "data/rotation_matrices.dat")
    if len(filename) == 0:
        print('Error, No filename given')
        sys.exit()
    if not os.path.exists(filename):
        print("File does not exist")
        sys.exit()
    res = Popen(['./load_rotation_matrices.py', filename]).wait()
    if (res != 0):
        sys.exit(1)
    # time.sleep(3)


def load_hba_rotations():
    print('Loading hba field rotations')
    filename = get_input_with_default("enter filename to load", "data/hba-rotations.csv")
    if len(filename) == 0:
        print('Error, No filename given')
        sys.exit()
    if not os.path.exists(filename):
        print("File does not exist")
        sys.exit()
    res = Popen(['./load_hba_rotations.py', filename]).wait()
    if (res != 0):
        sys.exit(1)
    # time.sleep(3)


def calculate_hba_deltas():
    print('calculating hba-deltas')
    # time.sleep(3)
    res = Popen(['./calc_hba_deltas.py']).wait()
    if (res != 0):
        sys.exit(1)


def load_all_etrf():
    print('loading all ETRF files from .//ETRF_FILES')
    os.chdir(os.curdir+'/ETRF_FILES')
    dirs = sorted(os.listdir(os.curdir))
    for dir in dirs:
        os.chdir(os.curdir+'/'+dir)
        files = os.listdir(os.curdir)
        for filename in files:
            if not os.path.exists(filename):
                print("File ",filename,"does not exist")
                sys.exit()
            res = Popen(['../../load_expected_pos.py', filename]).wait()
            if (res != 0):
                sys.exit(1)
        os.chdir(os.pardir)
    os.chdir(os.pardir)


def load_measurement():
    print('load one measurement file')
    filename = get_input_with_default("enter filename to load", "")
    if len(filename) == 0:
        print('Error, No filename given')
        sys.exit()
    if not os.path.exists(filename):
        print("File ",filename,"does not exist")
        sys.exit()
    res = Popen(['./load_measurementfile.py', filename]).wait()
    if (res != 0):
        sys.exit(1)


def transform_all(db_host, db_port, db_name, db_user, db_password):
    db = pg.connect(user=db_user, host=db_host, dbname=db_name, port=db_port, passwd=db_password)
    print('Transform all ETRF coordinates to ITRF coordinates for given date')
    target = get_input_with_default("Enter target_date", default_targetdate)
    sql = "select distinct o.stationname from object o inner join field_rotations r on r.id = o.id"
    all_stations = db.query(sql).getresult()
    sql = "select distinct o.stationname from object o inner join reference_coord r on r.id = o.id"
    ref_stations = db.query(sql).getresult()

    for stationname in ref_stations:
        station = stationname[0]
        if 0 != Popen(['./calc_coordinates.py', station, "LBA", target]).wait():
            sys.exit(1)
        if 0 != Popen(['./calc_coordinates.py', station, "CLBA", target]).wait():
            sys.exit(1)
        # if station[:1] == 'C': # core station
        if 0 != Popen(['./calc_coordinates.py', station, "HBA0", target]).wait():
            sys.exit(1)
        if 0 != Popen(['./calc_coordinates.py', station, "CHBA0", target]).wait():
            sys.exit(1)
        if 0 != Popen(['./calc_coordinates.py', station, "HBA1", target]).wait():
            sys.exit(1)
        if 0 != Popen(['./calc_coordinates.py', station, "CHBA1", target]).wait():
            sys.exit(1)
        # else: #remote or international station
        if 0 != Popen(['./calc_coordinates.py', station, "HBA", target]).wait():
            sys.exit(1)
        if 0 != Popen(['./calc_coordinates.py', station, "CHBA", target]).wait():
            sys.exit(1)

    db.close()
    missing_stations = list(set(all_stations) - set(ref_stations))
    for stationname in missing_stations:
        station = stationname[0]
        print("Station with known HBA rotation but no ETRF: ",station)


def transform_one():
    print('Transform ETRF coordinates to ITRF coordinates for given station and date')
    station = get_input_with_default("Enter station       ", "")
    anttype = get_input_with_default("Enter type (LBA|HBA|HBA0|HBA1|CLBA|CHBA0|CHBA1|CHBA)", "")
    target = get_input_with_default("Enter target_date   ", default_targetdate)
    res = Popen(['./calc_coordinates.py', station, anttype, target]).wait()
    if (res != 0):
        sys.exit(1)


def make_all_conf_files(db_host, db_port, db_name, db_user, db_password):
    db = pg.connect(user=db_user, host=db_host, dbname=db_name, port=db_port, passwd=db_password)
    print('Make all AntennaField.conf and iHBADeltas.conf files for given date')
    target = get_input_with_default("Enter target_date", default_targetdate)
    query = """select distinct o.stationname from
    object o inner join reference_coord r on r.id = o.id"""
    results = db.query(query).getresult()
    for stationname in results:
        station = stationname[0]
        res = Popen(['./make_conf_files.py', station, target]).wait()
        if (res != 0):
            sys.exit(1)
    res = Popen(['./make_all_station_file.py', target]).wait()
    if (res != 0):
        sys.exit(1)
    db.close()


def make_one_conf_file():
    print('Make one AntennaField.conf and iHBADeltas.conf file for given date')
    station = get_input_with_default("Enter station    ", "")
    target = get_input_with_default("Enter target_date", default_targetdate)
    res = Popen(['./make_conf_files.py', station, target]).wait()
    if (res != 0):
        sys.exit(1)


if __name__ == "__main__":
    parser = OptionParser("Usage: %prog")

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

    dbPassword = None

    while(1):
        menu()

        try:
            input = raw_input # Python2 and Python3 compatible
        except NameError:
            pass
        sel = input('Enter choice :')
        if sel.upper() == 'Q':
            sys.exit(1)
        if sel == '1':
            create_cdb()
        if sel == '2':
            create_cdb_objects()
        if sel == '3':
            load_normal_vectors()
        if sel == '4':
            load_rotation_matrices()
        if sel == '5':
            load_hba_rotations()
        if sel == '6':
            calculate_hba_deltas()
        if sel == '7':
            load_all_etrf()
        if sel == '8':
            load_measurement()
        if sel == '9':
            if dbPassword is None:
                dbPassword = getpass.getpass("Database password:")
            transform_all(dbHost, dbPort, dbName, dbUser, dbPassword)
        if sel == '10':
            transform_one()
        if sel == '11':
            if dbPassword is None:
                dbPassword = getpass.getpass("Database password:")
            make_all_conf_files(dbHost, dbPort, dbName, dbUser, dbPassword)
        if sel == '12':
            make_one_conf_file()
        if sel == '0':
            if dbPassword is None:
                dbPassword = getpass.getpass("Database password:")
            create_cdb()
            create_cdb_objects()
            load_normal_vectors()
            load_rotation_matrices()
            load_hba_rotations()
            calculate_hba_deltas()
            load_all_etrf()
            transform_all(dbHost, dbPort, dbName, dbUser, dbPassword)
            make_all_conf_files(dbHost, dbPort, dbName, dbUser, dbPassword)
