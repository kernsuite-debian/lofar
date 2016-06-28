# $Id: CMakeLists.txt 14273 2009-10-16 10:08:29Z loose $

include(LofarPackageVersion)

lofar_add_library(plc
  Package__Version.cc
  DH_ProcControl.cc
  PCCmd.cc
  ProcessControl.cc
  ProcControlComm.cc
  ProcControlServer.cc
  ProcCtrlProxy.cc
  ProcCtrlCmdLine.cc
  ProcCtrlRemote.cc
  ACCmain.cc)

lofar_add_bin_program(versionplc versionplc.cc)
