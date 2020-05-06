# $Id$

lofar_package(pytools 1.0 DEPENDS Common)

include(LofarFindPackage)
lofar_find_package(Python 3.4 REQUIRED)
lofar_find_package(Boost REQUIRED COMPONENTS python3)

add_subdirectory(include/pytools)
add_subdirectory(src)
add_subdirectory(test)
