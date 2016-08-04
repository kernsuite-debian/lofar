# $Id: CMakeLists.txt 34529 2016-05-24 17:00:41Z mol $

lofar_package(Pipeline-Recipes 0.1 DEPENDS Docker)

# The pipeline.cfg needs to know whether QPID is installed
include(LofarFindPackage)
lofar_find_package(QPID)

add_subdirectory(sip)
