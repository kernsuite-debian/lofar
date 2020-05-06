#! /usr/bin/env python3
import os
import re

def grep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [elem for elem in list if expr.search(open(elem).read())]

def lgrep(string, list):
    expr = re.compile(string, re.MULTILINE)
    return [ line for line in list if expr.search(line) ]

def genHeader(file, className):
    print("#include <lofar_config.h>", file = file)
    print("#include <Common/LofarLogger.h>", file = file)
    print("#include <Common/StringUtil.h>", file = file)
    print("#include <Common/StreamUtil.h>", file = file)
    print('#include "%s.h"' % className, file = file)
    print(file = file)
    print("using namespace pqxx;", file = file)
    print("namespace LOFAR {", file = file)
    print("  using namespace StringUtil;", file = file)
    print("  namespace OTDB {", file = file)
    print(file = file)

def genConstructor(file, className, fieldList):
    print("// Constructor", file = file)
    print("%s::%s(uint aTreeID, uint aRecordID, const string& aParent, const string& arrayString):" % (className, className), file = file)
    print("  itsTreeID(aTreeID),", file = file)
    print("  itsRecordID(aRecordID),", file = file)
    print("  itsNodename(aParent)", file = file)
    print("{", file = file)
    print("  string input(arrayString);", file = file)
    print('  rtrim(input, "}\\")");', file = file)
    print('  ltrim(input, "(\\"{");', file = file)
    print("  vector<string> fields(split(input, ','));", file = file)
    print('  ASSERTSTR(fields.size() == %d, fields.size() << " fields iso %d");' % (len(fieldList), len(fieldList)), file = file);
    print(file = file)
    idx = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("  %s = fields[%d];" % (args[1], idx), file = file)
      if args[3] in tInt:
        print("  %s = StringToInt32(fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tUint:
        print("  %s = StringToUint32(fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tBool:
        print("  %s = StringToBool(fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tFlt:
        print("  %s = StringToFloat(fields[%d]);" % (args[1], idx), file = file)
      idx += 1
    print("}", file = file)
    print(file = file)
    print('%s::%s(): itsTreeID(0),itsRecordID(0), itsNodename("")' % (className, className), file = file)
    print("{", file = file)
    idx = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tInt + tUint:
        print("  %s = 0;" % args[1], file = file)
      if args[3] in tBool:
        print("  %s = false;" % args[1], file = file)
      if args[3] in tFlt:
        print("  %s = 0.0;" % args[1], file = file)
      idx += 1
    print("}", file = file)
    print(file = file)

def genGetRecordsFunction1(file, className, fieldList):
    print("// getRecords(connection, treeID)", file = file)
    print("vector<%s> %s::getRecords(OTDBconnection *conn, uint32 treeID)" % (className, className), file = file)
    print("{", file = file)
    print("  vector<%s>  container;" % className, file = file)
    print(file = file)
    print('  work    xAction(*(conn->getConn()), "getRecord");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecords(%%d)", treeID));' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  uint32  nrRecs(res.size());", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    uint32   recordID;", file = file)
    print('    res[i]["recordid"].to(recordID);', file = file)
    print("    string   nodeName;", file = file)
    print('    res[i]["nodename"].to(nodeName);', file = file)
    print("    container.push_back(%s(treeID,recordID,nodeName,res[i][3].c_str()));" % className, file = file)
    print("  }", file = file)
    print("  return(container);", file = file)
    print("}", file = file)
    print(file = file)

def genGetRecordsFunction2(file, className, fieldList):
    print("// getRecords(connection, treeID, nodename)", file = file)
    print("vector<%s> %s::getRecords(OTDBconnection *conn, uint32 treeID, const string& nodename)" % (className, className), file = file)
    print("{", file = file)
    print("  vector<%s>  container;" % className, file = file)
    print(file = file)
    print('  work    xAction(*(conn->getConn()), "getRecord");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecords(%%d, \'%%s\')", treeID, nodename.c_str()));' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  uint32  nrRecs(res.size());", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    uint32   recordID;", file = file)
    print('    res[i]["recordid"].to(recordID);', file = file)
    print("    string   nodeName;", file = file)
    print('    res[i]["nodename"].to(nodeName);', file = file)
    print("    container.push_back(%s(treeID,recordID,nodeName,res[i][3].c_str()));" % className, file = file)
    print("  }", file = file)
    print("  return(container);", file = file)
    print("}", file = file)
    print(file = file)

def genGetRecordFunction1(file, className, fieldList):
    print("// getRecord(connection, recordID)", file = file)
    print("%s %s::getRecord(OTDBconnection *conn, uint32 recordID)" % (className, className), file = file)
    print("{", file = file)
    print('  work    xAction(*(conn->getConn()), "getRecord");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecord(%%d)", recordID));' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  if (!res.size()) {", file = file)
    print("     return (%s());" % className, file = file)
    print("  }", file = file)
    print("  uint32   treeID;", file = file)
    print('  res[0]["treeid"].to(treeID);', file = file)
    print("  string   nodeName;", file = file)
    print('  res[0]["nodename"].to(nodeName);', file = file)
    print("  return(%s(treeID,recordID,nodeName,res[0][3].c_str()));" % className, file = file)
    print("}", file = file)
    print(file = file)

def genGetRecordFunction2(file, className, fieldList):
    print("// getRecord(connection, treeID, nodename)", file = file)
    print("%s %s::getRecord(OTDBconnection *conn, uint32 treeID, const string& nodename)" % (className, className), file = file)
    print("{", file = file)
    print('  work    xAction(*(conn->getConn()), "getRecord");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecord(%%d, \'%%s\')", treeID, nodename.c_str()));' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  if (!res.size()) {", file = file)
    print("     return (%s());" % className, file = file)
    print("  }", file = file)
    print("  uint32   recordID;", file = file)
    print('  res[0]["recordid"].to(recordID);', file = file)
    print("  string   nodeName;", file = file)
    print('  res[0]["nodename"].to(nodeName);', file = file)
    print("  return(%s(treeID,recordID,nodeName,res[0][3].c_str()));" % className, file = file)
    print("}", file = file)
    print(file = file)

def genGetRecordsOnTreeList(file, className, fieldList):
    print("// getRecordsOnTreeList(connection, vector<treeid>)", file = file)
    print("vector<%s> %s::getRecordsOnTreeList  (OTDBconnection *conn, vector<uint32> treeIDs)" % (className, className), file = file)
    print("{", file = file)
    print("  vector<%s>  container;" % className, file = file)
    print(file = file)
    print("  ostringstream oss;", file = file)
    print('  writeVector(oss, treeIDs, ",", "{", "}");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecordsOnTreeList(\'%%s\')", oss.str().c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "getRecordsOnTreeList");', file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  uint32  nrRecs(res.size());", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    uint32   treeID;", file = file)
    print('    res[i]["treeid"].to(treeID);', file = file)
    print("    uint32   recordID;", file = file)
    print('    res[i]["recordid"].to(recordID);', file = file)
    print("    string   nodeName;", file = file)
    print('    res[i]["nodename"].to(nodeName);', file = file)
    print("    container.push_back(%s(treeID,recordID,nodeName,res[i][3].c_str()));" % className, file = file)
    print("  }", file = file)
    print("  return(container);", file = file)
    print("}", file = file)
    print(file = file)

def genGetRecordsOnRecordList(file, className, fieldList):
    print("// getRecordsOnRecordList(connection, vector<RecordID>)", file = file)
    print("vector<%s> %s::getRecordsOnRecordList(OTDBconnection *conn, vector<uint32> recordIDs)" % (className, className), file = file)
    print("{", file = file)
    print("  vector<%s>  container;" % className, file = file)
    print(file = file)
    print("  ostringstream oss;", file = file)
    print('  writeVector(oss, recordIDs, ",", "{", "}");', file = file)
    print('  string  command(formatString("SELECT * from %sgetRecordsOnRecordList(\'%%s\')", oss.str().c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "getRecordsOnRecordList");', file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  uint32  nrRecs(res.size());", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    uint32   treeID;", file = file)
    print('    res[i]["treeid"].to(treeID);', file = file)
    print("    uint32   recordID;", file = file)
    print('    res[i]["recordid"].to(recordID);', file = file)
    print("    string   nodeName;", file = file)
    print('    res[i]["nodename"].to(nodeName);', file = file)
    print("    container.push_back(%s(treeID,recordID,nodeName,res[i][3].c_str()));" % className, file = file)
    print("  }", file = file)
    print("  return(container);", file = file)
    print("}", file = file)
    print(file = file)

def genGetFieldOnRecordList(file, className, fieldList):
    print("// getFieldOnRecordList(connection, fieldname, vector<RecordID>)", file = file)
    print("vector<string> %s::getFieldOnRecordList(OTDBconnection *conn, const string& fieldname, vector<uint32> recordIDs)" % className, file = file)
    print("{", file = file)
    print("  vector<string>  container;", file = file)
    print(file = file)
    print("  int	fieldIdx(fieldnameToNumber(fieldname));", file = file)
    print("  if (fieldIdx < 0) {", file = file)
    print('    LOG_FATAL_STR("Field " << fieldname << " is not defined for structure %s");' % className, file = file)
    print("    return (container);", file = file)
    print("  }", file = file)
    print("  ostringstream oss;", file = file)
    print('  writeVector(oss, recordIDs, ",", "{", "}");', file = file)
    print('  string  command(formatString("SELECT * from %sgetFieldOnRecordList(%%d, \'%%s\')", fieldIdx, oss.str().c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "getFieldOnRecordList");', file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  uint32  nrRecs(res.size());", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print('    container.push_back(res[i][0].c_str() ? res[i][0].c_str() : "");', file = file)
    print("  }", file = file)
    print("  return(container);", file = file)
    print("}", file = file)
    print(file = file)

def genSaveRecord(file, className):
    print("// save(connection)", file = file)
    print("bool %s::save(OTDBconnection *conn)" % className, file = file)
    print("{", file = file)
    print('  string  command(formatString("SELECT * from %sSaveRecord(%%d, %%d, %%d, \'%%s\', \'{%%s}\')", conn->getAuthToken(), itsRecordID, itsTreeID, itsNodename.c_str(), fieldValues().c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "saveRecord%s");' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  bool    updateOK(false);", file = file)
    print('  res[0]["%ssaverecord"].to(updateOK);' % className, file = file)
    print("  if (updateOK) {", file = file)
    print("    xAction.commit();", file = file)
    print("  }", file = file)
    print("  return(updateOK);", file = file)
    print("}", file = file)
    print(file = file)

def genSaveField(file, className, fieldList):
    print("// saveField(connection, fieldIndex)", file = file)
    print("bool %s::saveField(OTDBconnection *conn, uint fieldIndex)" % className, file = file)
    print("{", file = file)
    print('  ASSERTSTR(fieldIndex < %d, "%s has only %d fields, not " << fieldIndex);' % (len(fieldList), className, len(fieldList)), file = file)
    print('  string  command(formatString("SELECT * from %sSaveField(%%d, %%d, %%d, %%d, \'%%s\')", conn->getAuthToken(), itsRecordID, itsTreeID, fieldIndex+1, fieldValue(fieldIndex).c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "saveField%s");' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  bool    updateOK(false);", file = file)
    print('  res[0]["%ssavefield"].to(updateOK);' % className, file = file)
    print("  if (updateOK) {", file = file)
    print("    xAction.commit();", file = file)
    print("  }", file = file)
    print("  return(updateOK);", file = file)
    print("}", file = file)
    print(file = file)

def genSaveFields(file, className, fieldList):
    print("// saveFields(connection, fieldIndex, vector<%s>)" % className, file = file)
    print("bool %s::saveFields(OTDBconnection *conn, uint fieldIndex, vector<%s>  records)" % (className, className), file = file)
    print("{", file = file)
    print('  ASSERTSTR(fieldIndex < %d, "%s has only %d fields, not " << fieldIndex);' % (len(fieldList), className, len(fieldList)), file = file)
    print("  string	recordNrs;", file = file)
    print("  string	fieldValues;", file = file)
    print("  size_t	nrRecs = records.size();", file = file)
    print("  recordNrs.reserve(nrRecs*5);    // speed up things a little", file = file)
    print("  fieldValues.reserve(nrRecs*30);", file = file)
    print("  for (uint i = 0; i < nrRecs; i++) {", file = file)
    print("    recordNrs.append(toString(records[i].recordID()));", file = file)
    print("    fieldValues.append(records[i].fieldValue(fieldIndex));", file = file)
    print("    if (i < nrRecs-1) {", file = file)
    print('      recordNrs.append(",");', file = file)
    print('      fieldValues.append(",");', file = file)
    print("    }", file = file)
    print("  }", file = file)
    print(file = file)
    print('  string  command(formatString("SELECT * from %sSaveFields(%%d, %%d, \'{%%s}\', \'{%%s}\')", conn->getAuthToken(), fieldIndex+1, recordNrs.c_str(), fieldValues.c_str()));' % className, file = file)
    print('  work    xAction(*(conn->getConn()), "saveFields%s");' % className, file = file)
    print("  result  res(xAction.exec(command));", file = file)
    print("  bool    updateOK(false);", file = file)
    print('  res[0]["%ssavefields"].to(updateOK);' % className, file = file)
    print("  if (updateOK) {", file = file)
    print("    xAction.commit();", file = file)
    print("  }", file = file)
    print("  return(updateOK);", file = file)
    print("}", file = file)
    print(file = file)

def genFieldNamesFunction(file, className, fieldList):
    print("// fieldNames()", file = file)
    print("string %s::fieldNames() const" % className, file = file)
    print("{", file = file)
    print('  return("' + fieldNameList(fieldList) + '");', file = file)
    print("};", file = file)
    print(file = file)

def genFieldValuesFunction(file, className, fieldList):
    print("// fieldValues()", file = file)
    print("string %s::fieldValues() const" % className, file = file)
    print("{", file = file)
    print("    ostringstream    oss;", file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      if count % 3 == 0:
         print("    oss", end = ' ', file = file)
      if count != 0:
         print('<< ","', end = ' ', file = file)
      if args[3] in tText + tInt + tUint + tFlt:
         print('<< %s' % args[1], end = ' ', file = file)
      if args[3] in tBool:
         print('<< (%s ? "true" : "false")' % args[1], end = ' ', file = file)
      count += 1
      if count % 3 == 0:
         print(";", file = file)
    print(";", file = file)
    print(file = file)
    print("    return (oss.str());", file = file)
    print("};", file = file)
    print(file = file)
    print("// fieldValue(fieldIndex)", file = file)
    print("string %s::fieldValue(uint fieldIndex) const" % className, file = file)
    print("{", file = file)
    print("  switch(fieldIndex) {", file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
         print('  case %d: return(%s); break;' % (count, args[1]), file = file)
      if args[3] in tInt + tUint + tFlt:
         print('  case %d: return(toString(%s)); break;' % (count, args[1]), file = file)
      if args[3] in tBool:
         print('  case %d: return(%s ? "true" : "false"); break;' % (count, args[1]), file = file)
      count += 1
    print("  };", file = file)
    print('  return("");', file = file)
    print("};", file = file)
    print(file = file)

def genFieldDictFunction(file, className, fieldList):
    print("// fieldDict()", file = file)
    print("string %s::fieldDict() const" % className, file = file)
    print("{", file = file)
    print("    ostringstream    oss;", file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      if count % 3 == 0:
         print("    oss", end = ' ', file = file)
      if count != 0:
         print('<< ","', end = ' ', file = file)
      if args[3] in tText + tInt + tUint + tFlt:
         print('<< "%s:" << %s' % (args[1], args[1]), end = ' ', file = file)
      if args[3] in tBool:
         print('<< "%s:" << (%s ? "true" : "false")' % (args[1], args[1]), end = ' ', file = file)
      count += 1
      if count % 3 == 0:
         print(";", file = file)
    print(";", file = file)
    print(file = file)
    print("    return (oss.str());", file = file)
    print("};", file = file)
    print(file = file)

def genPrintFunction(file, className, fieldList):
    print("// print(os)", file = file)
    print("ostream& %s::print(ostream& os) const" % className, file = file)
    print("{", file = file)
    print('  os << "{recordID:" << itsRecordID << ",treeID:" << itsTreeID << ",nodename:" << itsNodename;', file = file)
    print('  os << ",{" << fieldDict() << "}";', file = file)
    print('  return (os);', file = file)
    print("}", file = file)
    print(file = file)

def genCompareFunction(file, className, fieldList):
    print("// operator==", file = file)
    print("bool %s::operator==(const %s& that) const" % (className, className), file = file)
    print("{", file = file)
    print("  return (", end = ' ', file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      if count != 0:
         print(" && ", end = ' ', file = file)
      print("%s==that.%s" % (args[1], args[1]), end = ' ', file = file)
      count += 1
    print(");", file = file)
    print("}", file = file)
    print(file = file)

def genFieldName2Number(file, className, fieldList):
    print("// fieldnameToNumber(fieldname)", file = file)
    print("int %s::fieldnameToNumber(const string& fieldname)" % className, file = file)
    print("{", file = file)
    count = 1
    for field in fieldList:
      args = field.split()
      print('  if (fieldname == "%s") return(%d);' % (args[1], count), file = file)
      count += 1
    print("  return(-1);", file = file)
    print("}", file = file)
    print(file = file)

def genEndOfFile(file):
    print(file = file)
    print("  } // namespace OTDB", file = file)
    print("} // namespace LOFAR", file = file)
    print(file = file)

def genHeaderFile(file, className, fieldList):
    print("#ifndef LOFAR_OTDB_%s_H" % className.upper(), file = file)
    print("#define LOFAR_OTDB_%s_H" % className.upper(), file = file)
    print(file = file)
    print("#include <pqxx/pqxx>", file = file)
    print("#include <OTDB/OTDBconnection.h>", file = file)
    print("#include <Common/LofarTypes.h>", file = file)
    print("#include <Common/lofar_string.h>", file = file)
    print("#include <Common/lofar_vector.h>", file = file)
    print("namespace LOFAR {", file = file)
    print("  namespace OTDB {", file = file)
    print(file = file)
    print("class %s" % className, file = file)
    print("{", file = file)
    print("public:", file = file)
    print("  %s(uint aTreeID, uint aRecordID, const string& aParent, const string& arrayString);" % className, file = file)
    print("  %s();" % className, file = file)
    print(file = file)
    print("  // get a single record", file = file)
    print("  static %s         getRecord (OTDBconnection *conn, uint32 recordID);" % className, file = file)
    print("  static %s         getRecord (OTDBconnection *conn, uint32 treeID, const string& node);" % className, file = file)
    print("  // get a all record of 1 tree [and 1 type]", file = file)
    print("  static vector<%s> getRecords(OTDBconnection *conn, uint32 treeID);" % className, file = file)
    print("  static vector<%s> getRecords(OTDBconnection *conn, uint32 treeID, const string& node);" % className, file = file)
    print("  // get a multiple records of multiple trees", file = file)
    print("  static vector<%s> getRecordsOnTreeList  (OTDBconnection *conn, vector<uint32> treeIDs);" % className, file = file)
    print("  static vector<%s> getRecordsOnRecordList(OTDBconnection *conn, vector<uint32> recordIDs);" % className, file = file)
    print("  // get a a single field of multiple records", file = file)
    print("  static vector<string> getFieldOnRecordList(OTDBconnection *conn, const string& fieldname, vector<uint32> recordIDs);", file = file)
    print(file = file)
    print("  // save this record or 1 field", file = file)
    print("  bool save(OTDBconnection *conn);", file = file)
    print("  bool saveField(OTDBconnection *conn, uint fieldIndex);", file = file)
    print("  // save 1 field of multiple records", file = file)
    print("  static bool saveFields(OTDBconnection *conn, uint fieldIndex, vector<%s>  records);" % className, file = file)
    print(file = file)
    print("  // helper function", file = file)
    print("  static int fieldnameToNumber(const string& fieldname);", file = file)
    print("  string fieldNames () const;", file = file)
    print("  string fieldValues() const;", file = file)
    print("  string fieldDict  () const;", file = file)
    print("  string fieldValue (uint fieldIndex) const;", file = file)
    print(file = file)
    print("  // data access", file = file)
    print("  uint32 treeID()      const { return (itsTreeID);   }", file = file)
    print("  uint32 recordID()    const { return (itsRecordID); }", file = file)
    print("  string nodeName()    const { return (itsNodename); }", file = file)
    print(file = file)
    print("  // for operator<<", file = file)
    print("  ostream& print (ostream& os) const;", file = file)
    print(file = file)
    print("  // operator==", file = file)
    print("  bool operator==(const %s& that) const;" % className, file = file)
    print(file = file)
    print("  // -- datamembers --", file = file)
    print("private:", file = file)
    print("  uint32    itsTreeID;", file = file)
    print("  uint32    itsRecordID;", file = file)
    print("  string    itsNodename;", file = file)
    print("public:", file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("  string    %s;" % args[1], file = file)
      if args[3] in tInt:
        print("  int32     %s;" % args[1], file = file)
      if args[3] in tUint:
        print("  uint32    %s;" % args[1], file = file)
      if args[3] in tBool:
        print("  bool      %s;" % args[1], file = file)
      if args[3] in tFlt:
        print("  float     %s;" % args[1], file = file)
    print("};", file = file)
    print(file = file)
    print("// operator<<", file = file)
    print("inline ostream& operator<< (ostream& os, const %s& anObj)" % className, file = file)
    print("{ return (anObj.print(os)); }", file = file)
    print(file = file)
    print("  } // namespace OTDB", file = file)
    print("} // namespace LOFAR", file = file)
    print("#endif", file = file)
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

  file = open(tablename + ".cc", "w")
  genHeader                (file, tablename)
  genConstructor           (file, tablename, fieldLines)
  genGetRecordFunction1    (file, tablename, fieldLines)
  genGetRecordFunction2    (file, tablename, fieldLines)
  genGetRecordsFunction1   (file, tablename, fieldLines)
  genGetRecordsFunction2   (file, tablename, fieldLines)
  genGetRecordsOnTreeList  (file, tablename, fieldLines)
  genGetRecordsOnRecordList(file, tablename, fieldLines)
  genGetFieldOnRecordList  (file, tablename, fieldLines)
  genSaveRecord            (file, tablename)
  genSaveField             (file, tablename, fieldLines)
  genSaveFields            (file, tablename, fieldLines)
  genFieldName2Number      (file, tablename, fieldLines)
  genFieldNamesFunction    (file, tablename, fieldLines)
  genFieldValuesFunction   (file, tablename, fieldLines)
  genFieldDictFunction     (file, tablename, fieldLines)
  genPrintFunction         (file, tablename, fieldLines)
  genCompareFunction       (file, tablename, fieldLines)
  genEndOfFile             (file)
  file.close()

  file = open(tablename + ".h", "w")
  genHeaderFile(file, tablename, fieldLines)
  file.close()

