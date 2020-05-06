# $Id$

lofar_package(GSM 1.0)

include(LofarFindPackage)
lofar_find_package(Python 3.4 REQUIRED)

include(FindPythonModule)
find_python_module(monetdb REQUIRED)

add_subdirectory(src)
#add_subdirectory(db)
add_subdirectory(test)
