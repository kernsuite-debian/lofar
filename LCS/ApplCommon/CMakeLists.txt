# $Id: CMakeLists.txt 34547 2016-05-27 13:39:59Z mol $

lofar_package(ApplCommon 3.1 DEPENDS Common)

include(LofarFindPackage)
lofar_find_package(Boost COMPONENTS date_time regex REQUIRED)

add_subdirectory(include/ApplCommon)
add_subdirectory(src)
add_subdirectory(test)
