# $Id$

lofar_package(Pipeline-Recipes 0.1 DEPENDS Docker pyparameterset)

# The pipeline.cfg needs to know whether QPID is installed
include(LofarFindPackage)
lofar_find_package(QPID)

add_subdirectory(sip)
