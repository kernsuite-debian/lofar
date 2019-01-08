# $Id: CMakeLists.txt 39709 2018-06-14 12:07:59Z dijkema $

lofar_package(pystationresponse 1.0 DEPENDS StationResponse)

include(LofarFindPackage)
lofar_find_package(Python 2.6 REQUIRED)
lofar_find_package(Boost REQUIRED COMPONENTS python)
lofar_find_package(Casacore REQUIRED COMPONENTS python)

add_subdirectory(src)
add_subdirectory(test)
