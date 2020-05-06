#! /usr/bin/env python3
import os
import re

def grep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [elem for elem in list if expr.search(open(elem).read())]

def lgrep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [ line for line in list if expr.search(line) ]

def genHeader(file, className, fieldList):
#    print >>file, "#include <pqxx/pqxx>"
    print("#include <lofar_config.h>", file = file)
    print("#include <Common/LofarLogger.h>", file = file)
    print("#include <Common/StringUtil.h>", file = file)
    print("#include <Common/StreamUtil.h>", file = file)
    print("#include <OTDB/OTDBconnection.h>", file = file)
    print('#include "%s.h"' % className, file = file)
    print(file = file)
    print("using namespace pqxx;", file = file)
    print("using namespace LOFAR;", file = file)
    print("using namespace StringUtil;", file = file)
    print("using namespace OTDB;", file = file)
    print(file = file)
    genData(file, className, fieldList)
    print("int main() {", file = file)
    print("  srand(6863655);", file = file)
    print(file = file)
    print('  OTDBconnection*	otdbConn = new OTDBconnection("paulus", "boskabouter", "ArrayTest", "localhost");', file = file)
    print('  ASSERTSTR(otdbConn, "Can\'t allocated a connection object to database \'ArrayTest\'");', file = file)
    print('  ASSERTSTR(otdbConn->connect(), "Connect failed");', file = file)
    print('  ASSERTSTR(otdbConn->isConnected(), "Connection failed");', file = file)
    print(file = file)

def genData(file, className, fieldList):
    print("// genDataString - helper function", file = file)
    print("string genDataString()", file = file)
    print("{", file = file)
    print("  string result;", file = file)
    print('  string charset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");', file = file)
    print("  int    nrChars(charset.length());", file = file)
    print("  string field;", file = file)
    print("  field.resize(15);", file = file)
    idx = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("  for(int i=0; i<15;i++) { field[i]=charset[rand()%%nrChars]; }; result += field; // %s" % args[1], file = file)
      if args[3] in tInt:
        print("  result += toString(rand()%%2 ? rand() : -rand()); // %s" % args[1], file = file)
      if args[3] in tUint:
        print("  result += toString(rand()); // %s" % args[1], file = file)
      if args[3] in tBool:
        print('  result += (rand()%%2 ? "true" : "false"); // %s' % args[1], file = file)
      if args[3] in tFlt:
        print("  result += toString(rand() %% 100000 * 3.1415926); // %s" % args[1], file = file)
      idx += 1
      if idx < len(fieldList):
        print('  result.append(",");', file = file)
    print("  return (result);", file = file)
    print("}", file = file)
    print(file = file)

def genConstructor(file, className, fieldList):
    print("  // Test Constructors", file = file)
    print('  cout << "Testing Constructors" << endl;', file = file)
    print("  %s    object1;" % className, file = file)
    print('  cout << "Default constructed object:" << object1 << endl;', file = file)
    print(file = file)
    print("  string contents(genDataString());", file = file)
    print('  %s    object2(25, 625, "theNameOfTheNode", contents);' % className, file = file)
    print('  cout << object2 << endl;', file = file)
    print("  ASSERT(object2.treeID()   == 25);", file = file)
    print("  ASSERT(object2.recordID() == 625);", file = file)
    print('  ASSERT(object2.nodeName() == "theNameOfTheNode");', file = file)
    print("  vector<string>   fields(split(contents, ','));", file = file)
    idx = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("  ASSERT(object2.%s == fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tInt:
        print("  ASSERT(object2.%s == StringToInt32(fields[%d]));" % (args[1], idx), file = file)
      if args[3] in tUint:
        print("  ASSERT(object2.%s == StringToUint32(fields[%d]));" % (args[1], idx), file = file)
      if args[3] in tBool:
        print("  ASSERT(object2.%s == StringToBool(fields[%d]));" % (args[1], idx), file = file)
      if args[3] in tFlt:
        print("  ASSERT(object2.%s == StringToFloat(fields[%d]));" % (args[1], idx), file = file)
      idx += 1
    print(file = file)

def genGetRecords(file, className, fieldList):
    print("  // getRecords(connection, treeID)", file = file)
    print('  cout << "Testing getRecords(connection, treeID)" << endl;', file = file)
    print("  vector<%s> container(%s::getRecords(otdbConn, 25));" % (className, className), file = file)
    print("  ASSERT(container.size() == 16);", file = file)
    print("  container = %s::getRecords(otdbConn, 333);" % className, file = file)
    print("  ASSERT(container.size() == 0);", file = file)
    print(file = file)
    print("  // getRecords(connection, treeID, nodename)", file = file)
    print('  cout << "Testing getRecords(connection, treeID, nodeName)" << endl;', file = file)
    print('  container = %s::getRecords(otdbConn, 25, "firstHalf%%");' % className, file = file)
    print('  ASSERTSTR(container.size() == 8, container.size() << " records returned");', file = file)
    print('  container = %s::getRecords(otdbConn, 333, "secondHalf_10");' % className, file = file)
    print('  ASSERTSTR(container.size() == 0, container.size() << " records returned");', file = file)
    print('  container = %s::getRecords(otdbConn, 25, "secondHalf_10");' % className, file = file)
    print('  ASSERTSTR(container.size() == 1, container.size() << " records returned");', file = file)
    print(file = file)
    print("  // getRecord(connection, recordID)", file = file)
    print('  cout << "Testing getRecord(connection, recordID)" << endl;', file = file)
    print("  %s record(%s::getRecord(otdbConn, container[0].recordID()));" % (className, className), file = file)
    print("  ASSERT(container[0] == record);", file = file)
    print(file = file)
    print("  // getRecord(connection, treeID, nodename)", file = file)
    print('  cout << "Testing getRecord(connection, treeID, nodename)" << endl;', file = file)
    print("  %s record2(%s::getRecord(otdbConn, container[0].treeID(), container[0].nodeName()));" % (className, className), file = file)
    print("  ASSERT(record == record2);", file = file)
    print(file = file)
    print("  // getRecordsOnTreeList(connection, vector<treeid>)", file = file)
    print('  cout << "Testing getRecordsOnTreeList(connection, vector<treeID>)" << endl;', file = file)
    print("  vector<uint>  treeIDs;", file = file)
    print("  treeIDs.push_back(25);", file = file)
    print("  treeIDs.push_back(61);", file = file)
    print("  container = %s::getRecordsOnTreeList(otdbConn, treeIDs);" % className, file = file)
    print("  ASSERT(container.size() == 32);", file = file)
    print("  // All the saved records are in the container now, compare them with the original ones.", file = file)
    print("  for (uint i = 0; i < 32; i++) {", file = file)
    print("    ASSERT(container[i] == origRecs[i]);", file = file)
    print("  }", file = file)
    print(file = file)
    print("  // getRecordsOnRecordList(connection, vector<RecordID>)", file = file)
    print('  cout << "Testing getRecordsOnRecordList(connection, vector<recordID>)" << endl;', file = file)
    print("  vector<uint>  recordIDs;", file = file)
    print("  recordIDs.push_back(container[4].recordID());", file = file)
    print("  recordIDs.push_back(container[14].recordID());", file = file)
    print("  recordIDs.push_back(container[24].recordID());", file = file)
    print("  recordIDs.push_back(container[17].recordID());", file = file)
    print("  vector<%s> smallContainer = %s::getRecordsOnRecordList(otdbConn, recordIDs);" % (className, className), file = file)
    print("  ASSERT(smallContainer.size() == 4);", file = file)
    print(file = file)
    print("  // getFieldOnRecordList(connection, fieldname, vector<RecordID>)", file = file)
    fieldname = fieldList[5].split()[1]
    print('  cout << "Testing getFieldOnRecordList(connection, \'%s\', vector<recordID>)" << endl;' % fieldname, file = file)
    print("  fields.clear();", file = file)
    print('  fields = %s::getFieldOnRecordList(otdbConn, "%s", recordIDs);' % (className, fieldname), file = file)
    print("  ASSERT(fields.size() == 4);", file = file)
    print('  ASSERTSTR(fields[0] == toString(container[4].%s), fields[0] << " ? " << toString(container[4].%s));' % (fieldname, fieldname), file = file)
    print('  ASSERTSTR(fields[1] == toString(container[14].%s), fields[1] << " ? " << toString(container[14].%s));' % (fieldname, fieldname), file = file)
    print('  ASSERTSTR(fields[2] == toString(container[24].%s), fields[2] << " ? " << toString(container[24].%s));' % (fieldname, fieldname), file = file)
    print('  ASSERTSTR(fields[3] == toString(container[17].%s), fields[3] << " ? " << toString(container[17].%s));' % (fieldname, fieldname), file = file)
    print(file = file)

def genSaveRecords(file, className):
    print("  // fill database for tree 25 and 61", file = file)
    print('  cout << "Testing save() by adding records for tree 25 and 61" << endl;', file = file)
    print("  // First make sure that these trees exist in the database", file = file)
    print("  try {", file = file)
    print('    work    xAction(*(otdbConn->getConn()), "newTree");', file = file)
    print('    result  res(xAction.exec("insert into OTDBtree (treeID,originid,momID,classif,treetype,state,creator) values (25,1,0,3,20,300,1);"));', file = file)
    print("    xAction.commit();", file = file)
    print("  } catch (...) {};", file = file)
    print("  try {", file = file)
    print('    work    xAction(*(otdbConn->getConn()), "newTree");', file = file)
    print('    result  res(xAction.exec("insert into OTDBtree (treeID,originid,momID,classif,treetype,state,creator) values (61,1,0,3,20,300,1);"));', file = file)
    print("    xAction.commit();", file = file)
    print("  } catch (...) {};", file = file)
    print("  string  mask;", file = file)
    print("  vector<%s>   origRecs;" % className, file = file)
    print("  for (int i = 0; i < 32; i++) {", file = file)
    print('    if ((i % 16)/ 8) mask="secondHalf_%d"; ', file = file)
    print('    else mask="firstHalf_%d";', file = file)
    print("    origRecs.push_back(%s(25+(i/16)*36, i+1, formatString(mask.c_str(), i), genDataString()));" % className, file = file)
    print("  }", file = file)
    print("  for (int i = 0; i < 32; i++) {", file = file)
    print("    origRecs[i].save(otdbConn);", file = file)
    print("  }", file = file)
    print(file = file)

def genSaveField(file, className, fieldList):
    print("  // saveField(connection, fieldIndex)", file = file)
    print('  cout << "Testing saveField(connection, fieldIndex)" << endl;', file = file)
    print('  string    newValue;', file = file)
    args = fieldList[1].split()
    if args[3] in tText:
      print("  newValue.resize(15);", file = file)
      print('  string charset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");', file = file)
      print("  int    nrChars(charset.length());", file = file)
      print("  for(int i=0; i<15; i++) { newValue[i]=charset[rand()%nrChars]; };", file = file)
    if args[3] in tInt:
      print("  newValue = toString(rand()%2 ? rand() : -rand());", file = file)
    if args[3] in tUint:
      print("  newValue = toString(rand());", file = file)
    if args[3] in tBool:
      print('  newValue = (rand()%2 ? "true" : "false");', file = file)
    if args[3] in tFlt:
      print("  newValue = toString(rand() % 100000 * 3.1415926);", file = file)
    print("  container[13].%s = newValue;" % args[1], file = file)
    print("  ASSERT(container[13].saveField(otdbConn, 1));", file = file)
    print("  %s record13(%s::getRecord(otdbConn, container[13].recordID()));" % (className, className), file = file)
    print("  ASSERT(container[13] == record13);", file = file)
    print(file = file)

def genSaveFields(file, className, fieldList):
    print("  // saveFields(connection, fieldIndex, vector<%s>)" % className, file = file)
    print('  cout << "Testing saveFields(connection, fieldIndex, vector<%s>)" << endl;' % className, file = file)
    print('  vector<%s>::iterator    iter = smallContainer.begin();' % className, file = file)
    print('  vector<%s>::iterator    end  = smallContainer.end();' % className, file = file)
    print('  while(iter != end) {', file = file)
    args = fieldList[0].split()
    if args[3] in tText:
      print("  iter->%s.resize(15);" % args[1], file = file)
      print('  string charset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789");', file = file)
      print("  int    nrChars(charset.length());", file = file)
      print("  for(int c=0; c<15; c++) { iter->%s[c]=charset[rand()%%nrChars]; };" % args[1], file = file)
    if args[3] in tInt:
      print("  iter->%s = toString(rand()%2 ? rand() : -rand());" % args[1], file = file)
    if args[3] in tUint:
      print("  iter->%s = toString(rand());" % args[1], file = file)
    if args[3] in tBool:
      print('  iter->%s = (rand()%2 ? "true" : "false");' % args[1], file = file)
    if args[3] in tFlt:
      print("  iter->%s = toString(rand() % 100000 * 3.1415926);" % args[1], file = file)
    print('    iter++;', file = file)
    print('  }', file = file)
    print("  ASSERT(%s::saveFields(otdbConn, 0, smallContainer));" % className, file = file)
    print("  vector<%s> smallContainer2 = %s::getRecordsOnRecordList(otdbConn, recordIDs);" % (className, className), file = file)
    print("  ASSERT(smallContainer2.size() == smallContainer.size());", file = file)
    print("  for (uint i = 0; i < smallContainer.size(); i++) {", file = file)
    print("    ASSERT(smallContainer[i] == smallContainer2[i]);", file = file)
    print("  }", file = file)

def nbnbnbnb():
    print("	 string	recordNrs;", file = file)
    print("	 string	fieldValues;", file = file)
    print("  size_t	nrRecs = records.size();", file = file)
    print("	 recordNrs.reserve(nrRecs*5);    // speed up things a little", file = file)
    print("	 fieldValues.reserve(nrRecs*30);", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    recordNrs.append(toString(records[i].recordID()));", file = file)
    print("    fieldValues.append(records[i].fieldValue(fieldIndex));", file = file)
    print("    if (i < nrRecs-1) {", file = file)
    print('      recordNrs.append(",");', file = file)
    print('      fieldValues.append(",");', file = file)
    print("    }", file = file)
    print("  }", file = file)
    print(file = file)
    print('  string  command(formatString("SELECT * from %sSaveFields(%%d, %%d, \'{%%s}\', \'{%%s}\')", conn->getAuthToken(), fieldIndex, recordNrs.c_str(), fieldValues.c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "saveFields%s");' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  bool    updateOK(false);", file = file)
    print('  res[0]["%ssaverecord"].to(updateOK);' % className, file = file)
    print("  if (updateOK) {", file = file)
    print("    xAction.commit();", file = file)
    print("  }", file = file)
    print("  return(updateOK);", file = file)
    print("}", file = file)
    print(file = file)

def genEndOfFile(file):
    print(file = file)
    print('  cout << "ALL TESTS PASSED SUCCESSFUL" << endl;', file = file)
    print("  return(1);", file = file)
    print("}", file = file)
    print(file = file)

def fieldNameList(fieldlist):
    result = ""
    for field in fieldlist:
      if result != "":
        result += ","
      result += field.split()[1]
    return result

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

  file = open("t" + tablename + ".cc", "w")
  genHeader        (file, tablename, fieldLines)
  genConstructor   (file, tablename, fieldLines)
  genSaveRecords   (file, tablename)
  genGetRecords    (file, tablename, fieldLines)
  genSaveField     (file, tablename, fieldLines)
  genSaveFields    (file, tablename, fieldLines)
  genEndOfFile             (file)
  file.close()

