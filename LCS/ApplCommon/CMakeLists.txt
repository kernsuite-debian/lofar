# $Id: CMakeLists.txt 34754 2016-06-20 10:56:00Z schaap $

lofar_package(ApplCommon 3.1 DEPENDS Common)

include(LofarFindPackage)
lofar_find_package(Boost COMPONENTS date_time regex REQUIRED)

add_subdirectory(include/ApplCommon)
add_subdirectory(src)
add_subdirectory(test)
