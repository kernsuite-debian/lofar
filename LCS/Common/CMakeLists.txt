# $Id: CMakeLists.txt 21849 2012-08-30 10:52:23Z loose $

lofar_package(Common 3.3)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa)
lofar_find_package(Boost REQUIRED)
lofar_find_package(Readline)

add_subdirectory(include/Common)
add_subdirectory(src)
add_subdirectory(test)
