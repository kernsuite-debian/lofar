# $Id: CMakeLists.txt 14280 2009-10-16 13:48:46Z loose $

lofar_package(PLC 2.1 DEPENDS Common Blob Transport)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED)

add_subdirectory(include/PLC)
add_subdirectory(src)
add_subdirectory(test)
