# $Id: CMakeLists.txt 28194 2014-02-05 14:41:55Z dijkema $

lofar_package(pystationresponse 1.0 DEPENDS StationResponse)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED COMPONENTS python)
lofar_find_package(Python 2.6 REQUIRED)
lofar_find_package(Pyrap REQUIRED)

add_subdirectory(src)
add_subdirectory(test)
