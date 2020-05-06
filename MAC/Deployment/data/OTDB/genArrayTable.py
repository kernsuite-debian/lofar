#! /usr/bin/env python3
import os
import re

def grep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [elem for elem in list if expr.search(open(elem).read())]

def lgrep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [ line for line in list if expr.search(line) ]

def createTable(file, tablename, fieldlist):
    print("-- table " + tablename + "Table", file = file)
    print("DROP TABLE " + tablename + "Table   CASCADE;", file = file)
    print("DROP SEQUENCE " + tablename + "ID;", file = file)
    print(file = file)
    print("CREATE SEQUENCE " + tablename + "ID;", file = file)
    print(file = file)
    print("CREATE TABLE " + tablename + "Table (", file = file)
    print("    recordID            INT4         NOT NULL DEFAULT nextval('" + tablename + "ID'),", file = file)
    print("    treeID              INT4         NOT NULL,", file = file)
    print("    nodeName            VARCHAR      NOT NULL,", file = file)
    print("    infoArray           VARCHAR[]    DEFAULT '{}',", file = file)
    print("    CONSTRAINT " + tablename + "_PK      PRIMARY KEY(recordID)", file = file)
    print(") WITHOUT OIDS;", file = file)
    print("CREATE INDEX " + tablename + "_treeid ON " + tablename + "Table (treeID);", file = file)
    print(file = file)

def createType(file, tablename, fieldlist):
    print("-- type " + tablename, file = file)
    print("DROP TYPE " + tablename + " CASCADE;", file = file)
    print("CREATE TYPE " + tablename + " AS (", file = file)
    print("  recordID            INT4,", file = file)
    print("  treeID              INT4,", file = file)
    print("  nodename            VARCHAR,", file = file)
    print("  infoArray           VARCHAR[]", file = file)
    print(");", file = file)
    print(file = file)

def getRecord1(file, tablename):
    print("-- " + tablename + "GetRecord(recordID)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecord(INTEGER)", file = file)
    print("RETURNS %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("  BEGIN", file = file)
    print("    SELECT recordid,treeid,nodename,infoarray INTO vRecord", file = file)
    print("      FROM %sTable WHERE recordID = $1;" % tablename, file = file)
    print("    RETURN vRecord;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getRecord2(file, tablename):
    print("-- " + tablename + "GetRecord(treeID, nodename)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecord(INTEGER, VARCHAR)", file = file)
    print("RETURNS %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("  BEGIN", file = file)
    print("    SELECT recordid,treeid,nodename,infoarray INTO vRecord", file = file)
    print("      FROM %sTable WHERE treeID=$1 AND nodename=$2;" % tablename, file = file)
    print("    RETURN vRecord;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getRecords1(file, tablename):
    print("-- " + tablename + "GetRecords(treeID)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecords(INTEGER)", file = file)
    print("RETURNS SETOF %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("  BEGIN", file = file)
    print("    FOR vRecord IN SELECT recordid,treeid,nodename,infoarray", file = file)
    print("      FROM %sTable WHERE treeid = $1 ORDER BY recordid" % tablename, file = file)
    print("    LOOP", file = file)
    print("      RETURN NEXT vRecord;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getRecords2(file, tablename):
    print("-- " + tablename + "GetRecords(treeID, nodename)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecords(INTEGER, VARCHAR)", file = file)
    print("RETURNS SETOF %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("  BEGIN", file = file)
    print("    FOR vRecord IN SELECT recordid,treeid,nodename,infoarray", file = file)
    print("      FROM %sTable WHERE treeid=$1 AND nodename LIKE $2 ORDER BY recordid" % tablename, file = file)
    print("    LOOP", file = file)
    print("      RETURN NEXT vRecord;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getRecordsOnTreeList(file, tablename):
    print("-- " + tablename + "GetRecordsOnTreeList(treeID[])", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecordsOnTreeList(INTEGER[])", file = file)
    print("RETURNS SETOF %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("    x        INTEGER;", file = file)
    print("  BEGIN", file = file)
    print("    FOREACH x in ARRAY $1", file = file)
    print("    LOOP", file = file)
    print("      FOR vRecord IN SELECT recordid,treeid,nodename,infoarray", file = file)
    print("          FROM %sTable WHERE treeid = x ORDER BY recordid" % tablename, file = file)
    print("      LOOP", file = file)
    print("        RETURN NEXT vRecord;", file = file)
    print("      END LOOP;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getRecordsOnRecordList(file, tablename):
    print("-- " + tablename + "GetRecordsOnRecordList(treeID[])", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetRecordsOnRecordList(INTEGER[])", file = file)
    print("RETURNS SETOF %s AS $$" % tablename, file = file)
    print("  DECLARE", file = file)
    print("    vRecord  RECORD;", file = file)
    print("    x        INTEGER;", file = file)
    print("  BEGIN", file = file)
    print("    FOREACH x in ARRAY $1", file = file)
    print("    LOOP", file = file)
    print("      SELECT recordid,treeid,nodename,infoarray INTO vRecord", file = file)
    print("      FROM %sTable WHERE recordid = x;" % tablename, file = file)
    print("      RETURN NEXT vRecord;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getFields1(file, tablename):
    print("-- " + tablename + "GetFieldOnrecordList(fieldnr, recordNrs)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetFieldOnRecordList(INTEGER, INTEGER[])", file = file)
    print("RETURNS SETOF VARCHAR AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vResult  VARCHAR;", file = file)
    print("    recNr    INTEGER;", file = file)
    print("  BEGIN", file = file)
    print("    FOREACH recNr IN ARRAY $2", file = file)
    print("    LOOP", file = file)
    print("      SELECT infoarray[$1] INTO vResult FROM %sTable where recordID=recNr;" % tablename, file = file)
    print("      RETURN NEXT vResult;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def getFields2(file, tablename):
    print("-- " + tablename + "GetFieldOnRecordList2(recordNrs, fieldnr)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "GetFieldOnRecordList2(TEXT, INTEGER)", file = file)
    print("RETURNS SETOF VARCHAR AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vResult  VARCHAR;", file = file)
    print("    recNr    INTEGER;", file = file)
    print("    vQuery   TEXT;", file = file)
    print("  BEGIN", file = file)
    print("    vQuery:='SELECT infoarray['||$1||'] FROM %sTable where recordID in ('||$2||')';" % tablename, file = file)
    print("    FOR vResult in EXECUTE vQuery", file = file)
    print("    LOOP", file = file)
    print("      RETURN NEXT vResult;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN;", file = file)
    print("  END", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def saveRecord(file, tablename):
    print("-- " + tablename + "SaveRecord(auth, recordID, treeID, nodename, array)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "SaveRecord(INTEGER, INTEGER, INTEGER, VARCHAR, VARCHAR[])", file = file)
    print("RETURNS BOOLEAN AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vFunction    CONSTANT INT2 := 1;", file = file)
    print("    vIsAuth      BOOLEAN;", file = file)
    print("    vAuthToken   ALIAS FOR $1;", file = file)
    print("    vTreeID      %sTable.treeID%%TYPE;" % tablename, file = file)
    print("    vRecordID    %sTable.recordID%%TYPE;" % tablename, file = file)
    print("  BEGIN", file = file)
    checkAuthorisation(file, 3)
    checkTreeExistance(file, 3)
    print("    SELECT recordID INTO vRecordID from %sTable where recordID=$2;" % tablename, file = file)
    print("    IF NOT FOUND THEN", file = file)
    print("      INSERT INTO %sTable (recordID,treeID,nodeName,infoArray) VALUES($2,$3,$4,$5);" % tablename, file = file)
    print("    ELSE", file = file)
    print("      UPDATE %sTable set infoarray=$5 where recordID=$2;" % tablename, file = file)
    print("    END IF;", file = file)
    print("    RETURN TRUE;", file = file)
    print("  END;", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def saveField(file, tablename):
    print("-- " + tablename + "SaveField(auth, recordID, treeID, fieldIndex, stringValue)", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "SaveField(INTEGER, INTEGER, INTEGER, INTEGER, VARCHAR)", file = file)
    print("RETURNS BOOLEAN AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vFunction    CONSTANT INT2 := 1;", file = file)
    print("    vIsAuth      BOOLEAN;", file = file)
    print("    vAuthToken   ALIAS FOR $1;", file = file)
    print("    vTreeID      %sTable.treeID%%TYPE;" % tablename, file = file)
    print("    vRecordID    %sTable.recordID%%TYPE;" % tablename, file = file)
    print("  BEGIN", file = file)
    checkAuthorisation(file, 3)
    checkTreeExistance(file, 3)
    print("    UPDATE %sTable set infoarray[$4]=$5 where recordID=$2;" % tablename, file = file)
    print("    RETURN TRUE;", file = file)
    print("  END;", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def saveFields(file, tablename):
    print("-- " + tablename + "SaveFields(auth, fieldIndex, recordID[], stringValue[])", file = file)
    print("CREATE OR REPLACE FUNCTION " + tablename + "SaveFields(INTEGER, INTEGER, INTEGER[], VARCHAR[])", file = file)
    print("RETURNS BOOLEAN AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vFunction    CONSTANT INT2 := 1;", file = file)
    print("    vIsAuth      BOOLEAN;", file = file)
    print("    vAuthToken   ALIAS FOR $1;", file = file)
    print("    i            INTEGER;", file = file)
    print("    x            INTEGER;", file = file)
    print("  BEGIN", file = file)
    checkAuthorisation(file, 0)
    print("    i := 1;", file = file)
    print("    FOREACH x IN ARRAY $3", file = file)
    print("    LOOP", file = file)
    print("      UPDATE %sTable set infoarray[$2]=$4[i] where recordID=x;" % tablename, file = file)
    print("      i := i + 1;", file = file)
    print("    END LOOP;", file = file)
    print("    RETURN TRUE;", file = file)
    print("  END;", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def exportDefinition(file, tablename, fieldlist):
    print("-- export" + tablename + "Definition()", file = file)
    print("CREATE OR REPLACE FUNCTION export" + tablename + "Definition()", file = file)
    print("RETURNS TEXT AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vResult  TEXT;", file = file)
    print("  BEGIN", file = file)
    print("    vResult:='" + tablename + "<recordID,treeID,nodename" + fieldnames(fieldlist) + ">';", file = file)
    print("    RETURN vResult;", file = file)
    print("  END;", file = file)
    print("$$ language plpgsql IMMUTABLE;", file = file)
    print(file = file)

def exportRecord(file, tablename, fieldlist):
    print("-- export" + tablename + "(recordNr)", file = file)
    print("CREATE OR REPLACE FUNCTION export" + tablename + "(INT4)", file = file)
    print("RETURNS TEXT AS $$", file = file)
    print("  DECLARE", file = file)
    print("    vRec     RECORD;", file = file)
    print("    vResult  TEXT;", file = file)
    print("  BEGIN", file = file)
    print("    SELECT * INTO vRec FROM " + tablename + "Table WHERE recordID=$1;", file = file)
    print("    IF NOT FOUND THEN", file = file)
    print("      RAISE EXCEPTION E'" + tablename + " with recordnr \\'%\\' not found',$1;", file = file)
    print("    END IF;", file = file)
    line = "    vResult := '{treeID:' || text(vRec.treeID) || ',recordID:' || text(vRec.recordID) "
    count = 2
    for field in fieldlist:
      line += fieldAsText(count - 1, field.split())
      count += 1
      if count % 3 == 0:
        print(line + ";", file = file)
        line = "    vResult := vResult "
    line += "|| '}';"
    print(line, file = file)
    print("    RETURN vResult;", file = file)
    print("  END;", file = file)
    print("$$ language plpgsql;", file = file)
    print(file = file)

def fieldAndType(args):
    if args[3] in tInt:
      return args[1].ljust(30) + "INT4        "
    if args[3] in tUint:
      return args[1].ljust(30) + "INT4        "
    if args[3] in tFlt:
      return args[1].ljust(30) + "FLOAT       "
    if args[3] in tBool:
      return args[1].ljust(30) + "BOOLEAN     "
    if args[3] in tText:
      return args[1].ljust(30) + "VARCHAR     "
    return args[1].ljust(30) + "???         "

def fieldAndTypeAndDefault(args):
    if args[3] in tText:
      return fieldAndType(args) + " DEFAULT " + args[7]
    return fieldAndType(args) + " DEFAULT '" + args[7] + "'"

def fieldnames(fieldlist):
    result = ""
    for field in fieldlist:
      result += "," + field.split()[1]
    return result

def fieldAsText(indexNr, args):
    if args[3] in tText:
      return "|| ',%s:' || textValue(vRec.infoArray[%d])" % (args[1], indexNr)
    return "|| ',%s:' || vRec.infoArray[%d]" % (args[1], indexNr)

def checkAuthorisation(file, treeIDIdx):
    print("    -- check autorisation(authToken, tree, func, parameter)", file = file)
    print("    vIsAuth := FALSE;", file = file)
    if treeIDIdx:
      print("    SELECT isAuthorized(vAuthToken, $%d, vFunction, 0) INTO vIsAuth;" % treeIDIdx, file = file)
    else:
      print("    SELECT isAuthorized(vAuthToken, 0, vFunction, 0) INTO vIsAuth;", file = file)
    print("    IF NOT vIsAuth THEN", file = file)
    print("      RAISE EXCEPTION 'Not authorized';", file = file)
    print("    END IF;", file = file)
    print(file = file)

def checkTreeExistance(file, treeIDIdx):
    print("    -- check tree existance", file = file)
    print("    SELECT treeID INTO vTreeID FROM OTDBtree WHERE treeID=$%d;" % treeIDIdx, file = file)
    print("    IF NOT FOUND THEN", file = file)
    print("      RAISE EXCEPTION 'Tree %% does not exist', $%d;" % treeIDIdx, file = file)
    print("    END IF;", file = file)
    print(file = file)

# MAIN
tText = ["text", "vtext", "ptext" ]
tBool = ["bool", "vbool", "pbool" ]
tInt = ["int", "vint", "pint", "long", "vlong", "plong" ]
tUint = ["uint", "vuint", "puint", "ulng", "vulng", "pulng" ]
tFlt = ["flt", "vflt", "pflt", "dbl", "vdbl", "pdbl" ]

compfiles = [cf for cf in os.listdir('.') if cf.endswith(".comp")]
DBfiles = grep("^table.", compfiles)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  print("tablename=" + tablename)
  fieldLines = lgrep("^field", open(DBfile).readlines())

  file = open("create_" + tablename + ".sql", "w")
  createTable           (file, tablename, fieldLines)
  createType            (file, tablename, fieldLines)
  exportDefinition      (file, tablename, fieldLines)
  exportRecord          (file, tablename, fieldLines)
  getRecord1            (file, tablename)
  getRecord2            (file, tablename)
  getRecords1           (file, tablename)
  getRecords2           (file, tablename)
  getRecordsOnTreeList  (file, tablename)
  getRecordsOnRecordList(file, tablename)
  getFields1            (file, tablename)
  getFields2            (file, tablename)
  saveRecord            (file, tablename)
  saveField             (file, tablename)
  saveFields            (file, tablename)
  file.close()

