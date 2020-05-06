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
    print("package nl.astron.lofar.sas.otb.jotdb3;", file = file)
    print(file = file)
    print("public class j%s implements java.io.Serializable {" % className, file = file)
    print('  private String itsName = "";', file = file)
    print(file = file)

def genConstructor(file, className, fieldList):
    print("  // Constructor", file = file)
    print("  public j%s ()" % className, file = file)
    print("  {", file = file)
    print("    itsTreeID   = 0;", file = file)
    print("    itsRecordID = 0;", file = file)
    print('    itsNodename = "";', file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print('    %s = "";' % args[1], file = file)
      if args[3] in tInt + tUint:
        print("    %s = 0;" % args[1], file = file)
      if args[3] in tBool:
        print("    %s = false;" % args[1], file = file)
      if args[3] in tFlt:
        print("    %s = 0.0;" % args[1], file = file)
    print("  }", file = file)
    print(file = file)
    print("  public j%s (int aTreeID, int aRecordID, String aParent, String arrayList)" % className, file = file)
    print("  {", file = file)
    print("    itsTreeID   = aTreeID;", file = file)
    print("    itsRecordID = aRecordID;", file = file)
    print("    itsNodename = aParent;", file = file)
    print('    String fields[] = arrayList.replace("{","").replace("}","").split(",");', file = file)
    print('    assert fields.length() == %d : fields.length() + " fields iso %d";' % (len(fieldList), len(fieldList)), file = file);
    print(file = file)
    idx = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("    %s = fields[%d];" % (args[1], idx), file = file)
      if args[3] in tInt + tUint:
        print("    %s = Integer.valueOf(fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tBool:
        print("    %s = Boolean.parseBoolean(fields[%d]);" % (args[1], idx), file = file)
      if args[3] in tFlt:
        print("    %s = Float.valueOf(fields[%d]);" % (args[1], idx), file = file)
      idx += 1
    print("  }", file = file)
    print(file = file)
    print("  // data access", file = file)
    print("  public int treeID()   { return itsTreeID; };", file = file)
    print("  public int recordID() { return itsRecordID; };", file = file)
    print("  public int nodeName() { return itsNodename; };", file = file)
    print(file = file)

def genCompareFunction(file, className, fieldList):
    print("  @Override", file = file)
    print("  public boolean equals(Object obj) {", file = file)
    print("    // if 2 objects are equal in reference, they are equal", file = file)
    print("    if (this == obj)", file = file)
    print("      return true;", file = file)
    print("    // type of object must match", file = file)
    print("    if not(obj instanceof j%s)" % className, file = file)
    print("      return false;", file = file)
    print("    j%s that = (j%s) obj;" % (className, className), file = file)
    print("    return", end = ' ', file = file)
    count = 0
    for field in fieldList:
      if count != 0:
         print("&&", file = file)
         print("          ", end = ' ', file = file)
      args = field.split()
      if args[3] in tText:
         print("that.%s.equals(this.%s)" % (args[1], args[1]), end = ' ', file = file)
      if args[3] in tInt + tUint + tFlt + tBool:
         print("that.%s == this.%s" % (args[1], args[1]), end = ' ', file = file)
      count += 1
    print(";", file = file)
    print("  }", file = file)
    print(file = file)

def genFieldDictFunction(file, className, fieldList):
    print("  // fieldDict()", file = file)
    print("  public String fieldDict() {", file = file)
    file.write('    return "{')
    count = 0
    for field in fieldList:
      args = field.split()
      if count != 0:
         print('+ ",', end = ' ', file = file)
      print('%s: "+%s' % (args[1], args[1]), end = ' ', file = file)
      count += 1
      if count % 3 == 0:
         print(file = file)
         print("         ", end = ' ', file = file)
    print('+"}";', file = file)
    print('  }', file = file)
    print(file = file)

def genPrintFunction(file, className, fieldList):
    print("  // print()", file = file)
    print("  public String print() {", file = file)
    print('    return "{recordID: "+itsRecordID+", treeID: "+itsTreeID+", nodename: "+itsNodename + ","+ fieldDict()+"}";', file = file)
    print("  }", file = file)
    print(file = file)

def genDatamembers(file, className, fieldList):
    print("  // -- datamembers --", file = file)
    print("  private int      itsTreeID;", file = file)
    print("  private int      itsRecordID;", file = file)
    print("  private String   itsNodename;", file = file)
    print(file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("  public String    %s;" % args[1], file = file)
      if args[3] in tInt + tUint:
        print("  public int       %s;" % args[1], file = file)
      if args[3] in tBool:
        print("  public boolean   %s;" % args[1], file = file)
      if args[3] in tFlt:
        print("  public float     %s;" % args[1], file = file)
    print("}", file = file)
    print(file = file)

# jRecordAccessInterface.java
def genInterfaceHeader(file):
    print("package nl.astron.lofar.sas.otb.jotdb3;", file = file)
    print("import java.rmi.Remote;", file = file)
    print("import java.rmi.RemoteException;", file = file)
    print("import java.util.Vector;", file = file)
    print(file = file)
    print("public interface jRecordAccessInterface extends Remote", file = file)
    print("{", file = file)
    print("  // Constants", file = file)
    print('  public static final String SERVICENAME="jRecordAccess";', file = file)
    print(file = file)

def genRAInterface(file, tablename):
    print("  //--- j%s ---" % tablename, file = file)
    print("  // get a single record", file = file)
    print("  public Vector<j%s> get%s (int recordID) throws RemoteException;" % (tablename, tablename), file = file)
    print("  public Vector<j%s> get%s (int treeID, String node) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get all records of one tree [and 1 type]", file = file)
    print("  public Vector<j%s> get%ss (int treeID) throws RemoteException;" % (tablename, tablename), file = file)
    print("  public Vector<j%s> get%ss (int treeID, String node) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get multiple records of multiple trees", file = file)
    print("  public Vector<j%s> get%ssOnTreeList (Vector<Integer> treeIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  public Vector<j%s> get%ssOnRecordList (Vector<Integer> recordIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get a single field of multiple records", file = file)
    print("  public Vector<j%s> get%sFieldOnRecordList (String fieldname, Vector<Integer> recordIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // save this record or 1 field of this record", file = file)
    print("  public boolean save%s(j%s aRec) throws RemoteException;" % (tablename, tablename), file = file)
    print("  public boolean save%sField(j%s aRec, int fieldIndex) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // save 1 field of multiple records", file = file)
    print("  public boolean save%sFields(int fieldIndex, vector<j%s> records) throws RemoteException;" % (tablename, tablename), file = file)

# jRecordAccess.java
def genRAHeader(file):
    print("package nl.astron.lofar.sas.otb.jotdb3;", file = file)
    print("import java.rmi.RemoteException;", file = file)
    print("import java.util.Vector;", file = file)
    print(file = file)
    print("public class jRecordAccess implements jRecordAccessInterface", file = file)
    print("{", file = file)
    print('  private String itsName = "";', file = file)
    print("  public jRecordAccess(String ext) {", file = file)
    print("    itsName = ext;", file = file)
    print("  }", file = file)
    print(file = file)

def genRAFunctions(file, tablename):
    print("  //--- j%s ---" % tablename, file = file)
    print("  // get a single record", file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%s (int recordID) throws RemoteException;" % (tablename, tablename), file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%s (int treeID, String node) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get all records of one tree [and 1 type]", file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%ss (int treeID) throws RemoteException;" % (tablename, tablename), file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%ss (int treeID, String node) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get multiple records of multiple trees", file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%ssOnTreeList (Vector<Integer> treeIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%ssOnRecordList (Vector<Integer> recordIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // get a single field of multiple records", file = file)
    print("  @Override", file = file)
    print("  public native Vector<j%s> get%sFieldOnRecordList (String fieldname, Vector<Integer> recordIDs) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // save this record or 1 field of this record", file = file)
    print("  @Override", file = file)
    print("  public native boolean save%s(j%s aRec) throws RemoteException;" % (tablename, tablename), file = file)
    print("  @Override", file = file)
    print("  public native boolean save%sField(j%s aRec, int fieldIndex) throws RemoteException;" % (tablename, tablename), file = file)
    print("  // save 1 field of multiple records", file = file)
    print("  @Override", file = file)
    print("  public native boolean save%sFields(int fieldIndex, vector<j%s> records) throws RemoteException;" % (tablename, tablename), file = file)

# jRecordAccess.h
def genRAdotHfileHeader(file):
    print("#ifndef __nl_astron_lofar_sas_otb_jotdb3_jRecordAccess__", file = file)
    print("#define __nl_astron_lofar_sas_otb_jotdb3_jRecordAccess__", file = file)
    print(file = file)
    print("#include <jni.h>", file = file)
    print(file = file)
    print("#ifdef __cplusplus", file = file)
    print('extern "C"', file = file)
    print("{", file = file)
    print("#endif", file = file)
    print(file = file)

def genRAdotHFileFunctions(file, tablename):
    print("  //--- j%s ---" % tablename, file = file)
    print("  // get a single record", file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%s__I (JNIEnv *env, jobject, jint);" % tablename, file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%s__ILjava_lang_String_2 (JNIEnv *env, jobject, jint, jstring);" % tablename, file = file)
    print("  // get all records of one tree [and 1 type]", file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%ss__I (JNIEnv *env, jobject, jint);" % tablename, file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%ss__ILjava_lang_String_2 (JNIEnv *env, jobject, jint, jstring);" % tablename, file = file)
    print("  // get multiple records of multiple trees", file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%ssOnTreeList (JNIEnv *env, jobject, jobject);" % tablename, file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%ssOnRecordList (JNIEnv *env, jobject, jobject);" % tablename, file = file)
    print("  // get a single field of multiple records", file = file)
    print("  JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%sFieldOnRecordList (JNIEnv *env, jobject, jstring, jobject);" % tablename, file = file)
    print("  // save this record or 1 field of this record", file = file)
    print("  JNIEXPORT jboolean JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_save%s(JNIEnv *env, jobject, jobject);" % tablename, file = file)
    print("  JNIEXPORT jboolean JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_save%sField(JNIEnv *env, jobject, jobject, jint);" % tablename, file = file)
    print("  // save 1 field of multiple records", file = file)
    print("  JNIEXPORT jboolean JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_save%sFields(JNIEnv *env, jobject, jint, jobject);" % tablename, file = file)
    print(file = file)

# jRecordAccess.cc
def genRAdotCCheader(file, tablename, fieldList):
    print("#include <lofar_config.h>", file = file)
    print("#include <Common/LofarLogger.h>", file = file)
    print("#include <Common/StringUtil.h>", file = file)
    print("#include <jni.h>", file = file)
    print("#include <jOTDB3/nl_astron_lofar_sas_otb_jotdb3_jRecordAccess.h>", file = file)
    print("#include <jOTDB3/nl_astron_lofar_sas_otb_jotdb3_jCommonRec.h>", file = file)
    print("#include <jOTDB3/nl_astron_lofar_sas_otb_jotdb3_jOTDBconnection.h>", file = file)
    print("#include <iostream>", file = file)
    print("#include <string>", file = file)
    print(file = file)
    print("using namespace LOFAR::OTDB;", file = file)
    print("using namespace std;", file = file)
    print(file = file)
    print("JNIEXPORT void JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_initRecordAccess (JNIEnv *env, jobject jRecordAccess) {", file = file)
    print("  string name = getOwnerExt(env, jRecordAccess);", file = file)
    print("}", file = file)
    print(file = file)

def genRAgetRecordFunction(file, tablename, fieldList):
    print("// ---- %s ----" % tablename, file = file)
    print("#include <OTDB/%s.h>" % tablename, file = file)
    print("// get%s(recordID)" % tablename, file = file)
    print("JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%s__I (JNIEnv *env, jobject jRecordAccess, jint recordID) {" % tablename, file = file)
    print("  %s aRec;" % tablename, file = file)
    print("  try {", file = file)
    print("    OTDBconnection* aConn=getConnection(getOwnerExt(env,jRecordAccess));", file = file)
    print("    aRec= %s::getRecord (aConn,recordID);" % tablename, file = file)
    print("  } catch (exception &ex) {", file = file)
    print('    cout << "Exception during %s::getRecord(" << recordID << ") " << ex.what() << endl;' % tablename, file = file)
    print('    env->ThrowNew(env->FindClass("java/lang/Exception"),ex.what());', file = file)
    print("  }", file = file)
    print("  return convert%s(env, aRec);" % tablename, file = file)
    print("}", file = file)
    print(file = file)

def genRAgetRecordsFunction(file, tablename, fieldList):
    print("// get%s(treeID, parentname)" % tablename, file = file)
    print("JNIEXPORT jobject JNICALL Java_nl_astron_lofar_sas_otb_jotdb3_jRecordAccess_get%s__ILjava_lang_String_2 (JNIEnv *env, jobject jRecordAccess, jint treeID, jstring node) {" % tablename, file = file)
    print("  %s aRec;" % tablename, file = file)
    print("  const char* nodeName;", file = file)
    print("  jboolean isCopy;", file = file)
    print("  try {", file = file)
    print("    OTDBconnection* aConn=getConnection(getOwnerExt(env,jRecordAccess));", file = file)
    print("    nodeName = env->GetStringUTFChars (node, &isCopy);", file = file)
    print("    aRec= %s::getRecord (aConn,treeID, nodeName);" % tablename, file = file)
    print("    env->ReleaseStringUTFChars (node, nodeName);", file = file)
    print("  } catch (exception &ex) {", file = file)
    print('    cout << "Exception during %s::getRecord(" << treeID << "," << node <<") " << ex.what() << endl;' % tablename, file = file)
    print("    env->ReleaseStringUTFChars (node, nodeName);", file = file)
    print('    env->ThrowNew(env->FindClass("java/lang/Exception"),ex.what());', file = file)
    print("  }", file = file)
    print("  return convert%s(env, aRec);" % tablename, file = file)
    print("}", file = file)
    print(file = file)

# jCommonRec.h
def genCRdotHfileHeader(file):
    print("#ifndef LOFAR_JOTDB_COMMON_H", file = file)
    print("#define LOFAR_JOTDB_COMMON_H", file = file)
    print(file = file)
    print("#include <jni.h>", file = file)
    print("#include <jOTDB3/Common.h>", file = file)
    print("#include <string>", file = file)
    print("#include <map>", file = file)
    print(file = file)

def genCRdotHFileFunctions(file, tablename):
    print("//--- j%s ---" % tablename, file = file)
    print("#include <OTDB/%s.h>" % tablename, file = file)
    print("jobject convert%s (JNIEnv *env, LOFAR::OTDB::%s aRec);" % (tablename, tablename), file = file)
    print("LOFAR::OTDB::%s convertj%s (JNIEnv *env, jobject jRec);" % (tablename, tablename), file = file)
    print(file = file)

# jCommonRec.cc
def genCRdotCCheader(file, tablename, fieldList):
    print("#include <lofar_config.h>", file = file)
    print("#include <Common/LofarLogger.h>", file = file)
    print("#include <Common/StringUtil.h>", file = file)
    print("#include <jOTDB3/nl_astron_lofar_sas_otb_jotdb3_jCommonRec.h>", file = file)
    print("#include <string>", file = file)
    print("#include <iostream>", file = file)
    print("#include <map>", file = file)
    print(file = file)
    print("using namespace LOFAR::OTDB;", file = file)
    print("using namespace std;", file = file)
    print(file = file)

def genCRtoJavaFunction(file, tablename, fieldList):
    print("// c++ --> java", file = file)
    print("jobject convert%s (JNIEnv *env, %s aRec)" % (tablename, tablename), file = file)
    print("{", file = file)
    print("  jobject   jRec;", file = file)
    print('  jclass    class_j%s    = env->FindClass("nl/astron/lofar/sas/otb/jotdb3/j%s");' % (tablename, tablename), file = file)
    print('  jmethodID mid_j%s_cons = env->GetMethodID(class_j%s, "<init>", "(IILjava/lang/String)V");' % (tablename, tablename), file = file)
    print(file = file)
    print("  stringstream ss (stringstream::in | stringstream::out);", file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
         print('  ss << aRec.%s;' % args[1], file = file)
         print('  string c%s = ss.str();' % args[1], file = file)
    print(file = file)
    print('  string arrayList = string("{") +', end = ' ', file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print("c%s + " % args[1], end = ' ', file = file)
      else:
        print("aRec.%s + " % args[1], end = ' ', file = file)
      count += 1
      if count != len(fieldList):
        print('"," +', end = ' ', file = file)
    print('"}";', file = file)
    print(file = file)
    print("  jstring jArrayList = env->NewStringUTF(arrayList.c_str());", file = file)
    print("  jstring jNodeName  = env->NewStringUTF(aRec.nodeName().c_str());", file = file)
    print("  jRec = env->NewObject (class_j%s, mid_j%s_cons, aRec.treeID(),aRec.recordID(),jNodeName,jArrayList);" % (tablename, tablename), file = file)
    print("  return jRec;", file = file)
    print("}", file = file)
    print(file = file)

def J2Sstring(tablename, fieldname):
    print("  // %s" % fieldname, file = file)
    print("  jstring %sStr  = (jstring)env->GetObjectField(jRec, fid_j%s_%s);" % (fieldname, tablename, fieldname), file = file)
    print("  const char* %sPtr = env->GetStringUTFChars(%sStr, 0);" % (fieldname, fieldname), file = file)
    print("  const string %s (%sPtr);" % (fieldname, fieldname), file = file)
    print("  env->ReleaseStringUTFChars(%sStr, %sPtr);" % (fieldname, fieldname), file = file)
    print(file = file)

def J2Sinteger(tablename, fieldname):
    print("  // %s" % fieldname, file = file)
    print("  integer %sInt  = (integer)env->GetIntegerField(jRec, fid_j%s_%s);" % (fieldname, tablename, fieldname), file = file)
    print("  ss << %sInt;", file = file)
    print("  string %s = ss.str();" % fieldname, file = file)
    print(file = file)

def J2Sboolean(tablename, fieldname):
    print("  // %s" % fieldname, file = file)
    print("  boolean %sBool  = (boolean)env->GetBooleanField(jRec, fid_j%s_%s);" % (fieldname, tablename, fieldname), file = file)
    print("  ss << %sBool;", file = file)
    print("  string %s = ss.str();" % fieldname, file = file)
    print(file = file)

def J2Sfloat(tablename, fieldname):
    print("  // %s" % fieldname, file = file)
    print("  float %sFlt  = (float)env->GetBooleanField(jRec, fid_j%s_%s);" % (fieldname, tablename, fieldname), file = file)
    print("  ss << %sFlt;", file = file)
    print("  string %s = ss.str();" % fieldname, file = file)
    print(file = file)

def genCRtoCppFunction(file, tablename, fieldList):
    print("// java --> c++", file = file)
    print("%s convertj%s (JNIEnv *env, jobject jRec)" % (tablename, tablename), file = file)
    print("{", file = file)
    print("  jclass    class_j%s = env->GetObjectClass(jRec);" % tablename, file = file)
    print('  jmethodID mid_j%s_treeID   = env->GetMethodID(class_j%s, "treeID", "()I");' % (tablename, tablename), file = file)
    print('  jmethodID mid_j%s_recordID = env->GetMethodID(class_j%s, "recordID", "()I");' % (tablename, tablename), file = file)
    print('  jmethodID mid_j%s_nodeName = env->GetMethodID(class_j%s, "nodeName", "()Ljava/lang/String");' % (tablename, tablename), file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        print('  jfieldID fid_j%s_%s = env->GetFieldID(class_j%s, "%s", "Ljava/lang/String;");' % (tablename, args[1], tablename, args[1]), file = file)
      if args[3] in tInt + tUint:
        print('  jfieldID fid_j%s_%s = env->GetFieldID(class_j%s, "%s", "I");' % (tablename, args[1], tablename, args[1]), file = file)
      if args[3] in tBool:
        print('  jfieldID fid_j%s_%s = env->GetFieldID(class_j%s, "%s", "B");' % (tablename, args[1], tablename, args[1]), file = file)
      if args[3] in tFlt:
        print('  jfieldID fid_j%s_%s = env->GetFieldID(class_j%s, "%s", "F");' % (tablename, args[1], tablename, args[1]), file = file)
    print(file = file)
    print("  // nodeName", file = file)
    print("  jstring nodeNamestr  = (jstring)env->CallObjectMethod(jRec, mid_j%s_nodeName);" % tablename, file = file)
    print("  const char* n = env->GetStringUTFChars(nodeNamestr, 0);", file = file)
    print("  const string nodeName (n);", file = file)
    print("  env->ReleaseStringUTFChars(nodeNamestr, n);", file = file)
    print(file = file)
    print("  stringstream ss (stringstream::in | stringstream::out);", file = file)
    print(file = file)
    for field in fieldList:
      args = field.split()
      if args[3] in tText:
        J2Sstring(tablename, args[1])
      if args[3] in tInt + tUint:
        J2Sinteger(tablename, args[1])
      if args[3] in tBool:
        J2Sboolean(tablename, args[1])
      if args[3] in tFlt:
        J2Sfloat(tablename, args[1])
    print(file = file)
    print('  string arrayList = string("{") +', end = ' ', file = file)
    count = 0
    for field in fieldList:
      args = field.split()
      print("%s + " % args[1], end = ' ', file = file)
      count += 1
      if count != len(fieldList):
        print('"," +', end = ' ', file = file)
    print('"}";', file = file)
    print(file = file)
    print("  // Get original %s" % tablename, file = file)
    print("  %s aRec = %s((int)env->CallIntMethod (jRec, mid_j%s_treeID)," % (tablename, tablename, tablename), file = file)
    print("               (int)env->CallIntMethod (jRec, mid_j%s_recordID)," % (tablename), file = file)
    print("               nodeName, arrayList);", file = file)
    print("  return aRec;", file = file)
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

# Every table has its own java file with the Java equivalent of the C++ class.
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())

  print("j" + tablename + ".java")
  file = open("j" + tablename + ".java", "w")
  genHeader                (file, tablename)
  genConstructor           (file, tablename, fieldLines)
  genCompareFunction       (file, tablename, fieldLines)
  genFieldDictFunction     (file, tablename, fieldLines)
  genPrintFunction         (file, tablename, fieldLines)
  genDatamembers           (file, tablename, fieldLines)
  file.close()

# The rest of the files contain the collection of all record-types
print("jRecordAccessInterface.java")
file = open("jRecordAccessInterface.java", "w")
genInterfaceHeader(file)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genRAInterface(file, tablename)
print("}", file = file)
file.close()

print("jRecordAccess.java")
file = open("jRecordAccess.java", "w")
genRAHeader(file)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genRAFunctions(file, tablename)
print("}", file = file)
file.close()

print("nl_astron_lofar_sas_otb_jotdb3_jRecordAccess.h")
file = open("nl_astron_lofar_sas_otb_jotdb3_jRecordAccess.h", "w")
genRAdotHfileHeader(file)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genRAdotHFileFunctions(file, tablename)
print("#ifdef __cplusplus", file = file)
print("}", file = file)
print("#endif", file = file)
print("#endif /* __nl_astron_lofar_sas_otb_jotdb3_jRecordAccess__ */", file = file)
file.close()

print("nl_astron_lofar_sas_otb_jotdb3_jRecordAccess.cc")
file = open("nl_astron_lofar_sas_otb_jotdb3_jRecordAccess.cc", "w")
genRAdotCCheader(file, tablename, fieldLines)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genRAgetRecordFunction(file, tablename, fieldLines)
  genRAgetRecordsFunction(file, tablename, fieldLines)
#  genCRtoJavaFunction(file, tablename, fieldLines)
#  genCRtoCppFunction(file, tablename, fieldLines)
file.close()

print("nl_astron_lofar_sas_otb_jotdb3_jCommonRec.h")
file = open("nl_astron_lofar_sas_otb_jotdb3_jCommonRec.h", "w")
genCRdotHfileHeader(file)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genCRdotHFileFunctions(file, tablename)
print("#endif", file = file)
file.close()

print("nl_astron_lofar_sas_otb_jotdb3_jCommonRec.cc")
file = open("nl_astron_lofar_sas_otb_jotdb3_jCommonRec.cc", "w")
genCRdotCCheader(file, tablename, fieldLines)
for DBfile in DBfiles:
  tablename = lgrep("^table", open(DBfile).readlines())[0].split()[1]
  fieldLines = lgrep("^field", open(DBfile).readlines())
  genCRtoJavaFunction(file, tablename, fieldLines)
  genCRtoCppFunction(file, tablename, fieldLines)
file.close()

#  genGetRecordFunction1    (file, tablename, fieldLines)
#  genGetRecordFunction2    (file, tablename, fieldLines)
#  genGetRecordsFunction1   (file, tablename, fieldLines)
#  genGetRecordsFunction2   (file, tablename, fieldLines)
#  genGetRecordsOnTreeList  (file, tablename, fieldLines)
#  genGetRecordsOnRecordList(file, tablename, fieldLines)
#  genGetFieldOnRecordList  (file, tablename, fieldLines)
#  genSaveRecord            (file, tablename)
#  genSaveField             (file, tablename, fieldLines)
#  genSaveFields            (file, tablename, fieldLines)
#  genFieldName2Number      (file, tablename, fieldLines)
#  genFieldNamesFunction    (file, tablename, fieldLines)
#  genFieldValuesFunction   (file, tablename, fieldLines)
#  genEndOfFile             (file)
