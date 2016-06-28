# $Id: CMakeLists.txt 31976 2015-07-08 19:52:14Z dijkema $

include(LofarCTest)

lofar_add_test(tDirtyImage2)
#lofar_add_test(tClean2)
if (IDG_FOUND)
  lofar_add_test(tFTMachineIDG)
endif()


