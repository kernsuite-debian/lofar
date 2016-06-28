# $Id: CMakeLists.txt 21245 2012-06-18 10:56:03Z diepen $

include(LofarCTest)

lofar_add_test(tMSLofarTable tMSLofarTable.cc)
lofar_add_test(tMSLofar tMSLofar.cc)
lofar_add_test(tMSLofar2 tMSLofar2.cc)
lofar_add_test(tBeamTables tBeamTables.cc)
