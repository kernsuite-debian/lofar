#!/usr/bin/env python3
import os
# This script reads infile and creates sql files for each part in the infile in the
# outdir directory. It also replaces references to the indatabase with references
# to the outdatabase.
# It creates a file for each view and table and trigger that is defined in the infile.
# It creates separate files for filling the tables.
# The script assumes the infile is a dump of a MySQL MoM 3 database.

# To use this script, change the variables defined below.

infile = "backup_lofar_mom3.sql.1"
indatabase = "lofar_mom3"
outdatabase = "lofar_mom_test_rt_trigger"
outdir = "test/"

# You probably want to run this script on copies of lofar_mom3, lofar_mom3privileges
# useradministration and lofar_idm.
# The results can be fed to mysql with a command like:
# > ls -1 *.sql | awk '{ print "source",$0 }' | mysql --batch -u <user> -h mysqltest1.control.lofar -p<password>

# If you leave these blank or have them the same as indatabase, the script will skip them.
# The core MoM database references these.
inIDMdatabase = "lofar_idm"
outIDMdatabase = "lofar_mom_test_rt_trigger_idm"
inUserAdmindatabase = "useradministration"
outUserAdmindatabase = "lofar_mom_test_rt_trigger_useradmin"

if os.listdir(outdir) != []:
    print("Output directory not empty! Aborting")
    exit()

outfile = open(outdir + "000000_CREATE_DATABASE.sql", 'w')

# Please note that "Comments" in the SQL that look like this
# /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
# are not really comments, but conditionals, which mean that they will
# only be interpreted by MySQL and only if the version is above e.g. 4.01.01
# see https://dev.mysql.com/doc/refman/5.7/en/comments.html

# This script is not robust, but tries to be efficient based on assumptions
# on the current mom database. When adding new triggers or views, it might need updates.
# after running this script a "grep <indatabase> *.sql" should be used to verify

# The script works as follows:
# Main loop:
# 1) Scan for DROP TABLE IF EXISTS or LOCK TABLES or TRIGGER
#    - DROP TABLE IF EXISTS will mean the creation of a table or view follows
#    - LOCK TABLES means a WRITE of the contents of the table follows
#    - TRIGGER means a definition of a trigger follows
# 2) Buffer any blank lines and comments (starting with --) as those are above the actual SQL statements.
# 3) If one of those in step 1 is found make a new sql file based on the VIEW/TABLE/TRIGGER name
# 4) Write the buffered lines
# 5) Write each line until we start finding blanks or comments again
#
# This mostly works because MySQLdump puts comments and blank lines between each block of statements.
# There are a few exceptions the code needs to handle:
#
# Exception 1:
# The start of the MySQL dump up to the USE statement.
# We want all of this in 000000_CREATE_DATABASE.sql
#
# Exception 2:
# Detection of the end of the file on "Dump completed"
#
# Exception 3:
# Triggers
# These do not have comments or blank lines to separate them from the CREATE and WRITE
# They also might have comments or blank lines in the TRIGGER definition.
# These always follow an UNLOCK TABLES (from a WRITE) are currently in MoM none are defined on empty tables.
# There are no blank lines that follow the UNLOCK TABLES, but lines with
# conditional defines starting with /*!50003 to set things like character encoding
# If we find DELIMITER ;; then we know a trigger follows until we find END */;;
# There might be zero or more triggers after that.
# 
# What we do for Triggers is that be are on guard to look for them after each 
# UNLOCK TABLES (possible_trigger = True), and if we find one (trigger = True)
# we break the main loop until we find the end of a trigger.
#
# =======================================================================================
# 
# Replacing the database name.
# The database name is used in several locations:
# - database creation
# - Triggers
# - Generated views for the BiRT viewer (starting with /*!50001 VIEW )
# - Comments
# - USE statements
# - Foreign keys
# We only check for these and not all lines of the SQL, as this saves having to parse the
# WRITE statements that are 99% of the SQL and by far the longest lines.

# Fun state machine to parse a SQL dump follows

buffer = "" # Buffer to store lines until we know what we found next
use_found = False # When to close the CREATE_DATABASE script
line_nr = 0
possible_trigger = False
trigger = False
with open(infile) as f:
    for line in f:
        if not use_found or trigger or (line[0:13] == "/*!50001 VIEW") or (line[0:2] == '--') or \
           "CONSTRAINT" in line[0:len("CONSTRAINT") + 2]:
            # "/*!50001 VIEW" are special BiRT viewer generated views
            if indatabase in line: #doing this for each line would be expensive
                line = line.replace(indatabase, outdatabase)
            if inIDMdatabase and (indatabase != inIDMdatabase) and inIDMdatabase in line: 
                line = line.replace(inIDMdatabase, outIDMdatabase)
            if inUserAdmindatabase and (indatabase != inUserAdmindatabase) and inUserAdmindatabase in line: 
                line = line.replace(inUserAdmindatabase, outUserAdmindatabase)
        if line[0:3] == "USE":
            if use_found:
                outfile = open(outdir + "%06d_" % line_nr + "USE_%s.sql" % outdatabase, 'w')
                outfile.write(buffer)
                buffer = ""
                if indatabase in line: # could also be in the first if in the for loop
                    line = line.replace(indatabase, outdatabase)
                outfile.write(line)
            else:
                use_found = True # End of the general database creation
                outfile.write(buffer)
                buffer = ""
                outfile.write(line)
        elif "UNLOCK TABLES" in line: # Triggers on a table are possible after the WRITE
            possible_trigger = True
            outfile.write(line)
        elif possible_trigger and line[0:8] == "/*!50003":
            buffer += line
        elif possible_trigger and "DELIMITER ;;" in line: # Trigger code follows
            buffer += line
            trigger = True
            possible_trigger = False
        elif "END */;;" in line: # End of trigger code
            trigger = False
            outfile.write(line)
            possible_trigger = True # There might be more trigger code.
        elif not trigger and (line[0:2] == '--' or line.isspace() or not use_found):
            buffer += line
        elif buffer: # We should have a line that tells us what is happening next
            print(line)
            outfile.close()
            possible_trigger = False
            filename = line.translate(None, '/*;`!@=\n()').replace(' ','_')
            if 'DROP_TABLE_IF_EXISTS_' in filename:
                filename = 'CREATE_TABLE_OR_VIEW_' + \
                           filename[filename.find('DROP_TABLE_IF_EXISTS_') 
                           + len('DROP_TABLE_IF_EXISTS_'):]
            if 'LOCK_TABLES_' in filename:
                filename = 'WRITE_TABLE_' + filename[len('WRITE_TABLE_'):-len('WRITE;')]
            if 'TRIGGER' in line:
                filename = 'CREATE_' + \
                           filename[filename.find('TRIGGER'):-len('_FOR_EACH_ROW_BEGIN')]
            outfile = open(outdir + "%06d_" % line_nr + filename + ".sql", 'w')
            outfile.write(buffer)
            buffer = ""
            outfile.write(line)
        elif trigger:
            outfile.write(line)
        elif "Dump completed" in line: # Last line of dump
            outfile.write(buffer)
            buffer = ""
            outfile.close()
            break
        else:
            outfile.write(line)
        line_nr += 1