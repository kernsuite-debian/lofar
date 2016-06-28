# $Id: CMakeLists.txt 23213 2012-12-07 13:00:09Z loose $

include(LofarPackageVersion)

lofar_add_library(applcommon
  Package__Version.cc
  AntField.cc
  AntennaSets.cc
  Observation.cc
  PosixTime.cc
  StationConfig.cc
  StationDatatypes.cc
  StationInfo.cc)

lofar_add_bin_program(versionapplcommon versionapplcommon.cc)

