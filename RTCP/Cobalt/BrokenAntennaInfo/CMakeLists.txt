# $Id: CMakeLists.txt 22563 2012-10-30 18:50:15Z mol $

lofar_package(BrokenAntennaInfo 1.0 DEPENDS Common OTDB CoInterface)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa measures REQUIRED)
lofar_find_package(Boost REQUIRED COMPONENTS date_time)

add_subdirectory(src)
add_subdirectory(test)
