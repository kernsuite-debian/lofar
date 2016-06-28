# $Id: CMakeLists.txt 21849 2012-08-30 10:52:23Z loose $

lofar_package(LMWCommon 0.1 DEPENDS Common Blob)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED)
lofar_find_package(Casacore COMPONENTS casa REQUIRED)

add_subdirectory(include/LMWCommon)
add_subdirectory(share)
add_subdirectory(src)
add_subdirectory(test)
