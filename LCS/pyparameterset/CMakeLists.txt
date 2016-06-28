# $Id: CMakeLists.txt 22948 2012-11-23 08:54:47Z loose $

lofar_package(pyparameterset 1.0 DEPENDS pytools)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED COMPONENTS python)
lofar_find_package(Python 2.6 REQUIRED)

add_subdirectory(src)
add_subdirectory(test)
