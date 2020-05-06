# $Id$

lofar_package(pyparameterset 1.0 DEPENDS pytools)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED COMPONENTS python3)
lofar_find_package(Python 3.4 REQUIRED)

add_subdirectory(src)
add_subdirectory(test)
