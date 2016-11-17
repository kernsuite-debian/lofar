# $Id: CMakeLists.txt 35142 2016-08-22 10:10:37Z schaap $

lofar_package(Pipeline-Recipes 0.1 DEPENDS Docker pyparameterset)

# The pipeline.cfg needs to know whether QPID is installed
include(LofarFindPackage)
lofar_find_package(QPID)

add_subdirectory(sip)
