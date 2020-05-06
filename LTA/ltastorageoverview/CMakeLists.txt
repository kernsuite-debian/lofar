# $Id$

lofar_find_package(Python 3.4 REQUIRED)
lofar_package(ltastorageoverview 0.1 DEPENDS PyCommon LTAIngestClient LTAIngestCommon)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
