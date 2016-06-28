# $Id: CMakeLists.txt 34754 2016-06-20 10:56:00Z schaap $

lofar_package(Pipeline-Recipes 0.1 DEPENDS Docker)

# The pipeline.cfg needs to know whether QPID is installed
include(LofarFindPackage)
lofar_find_package(QPID)

add_subdirectory(sip)
