#!/usr/bin/env python3

import os
import socket
import sys
import pyrap.tables as pt


masterhost = sys.argv[2]
port = int( sys.argv[3] )
partnr = sys.argv[5]
msname = sys.argv[6]

antenna_table = pt.table( msname + "/ANTENNA")
name_col = antenna_table.getcol('NAME')
position_col = antenna_table.getcol( 'POSITION' )
antenna_table.close()

field_table = pt.table( msname + "/FIELD")
phase_dir_col = field_table.getcol('PHASE_DIR')
field_table.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((masterhost, port))
s.sendall(partnr.encode("ascii"))
s.recv(1024)
s.sendall(repr(name_col).encode("ascii"))
s.recv(1024)
s.sendall(repr(position_col).encode("ascii"))
s.recv(1024)
s.sendall(repr(phase_dir_col).encode("ascii"))
s.recv(1024)

s.close()
