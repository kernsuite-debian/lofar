# $Id$

lofar_package(pystationresponse 1.0 DEPENDS StationResponse)

include(LofarFindPackage)
lofar_find_package(Python 3.4 REQUIRED)
lofar_find_package(Boost REQUIRED COMPONENTS python3)
lofar_find_package(Casacore REQUIRED COMPONENTS python)

add_subdirectory(src)
add_subdirectory(test)
