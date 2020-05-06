# $Id$

include(LofarCTest)
include(FindPythonModule)

lofar_find_package(Python 3.4 REQUIRED)

lofar_add_test(tPipelineControl)

