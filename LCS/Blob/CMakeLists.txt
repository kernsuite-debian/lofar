# $Id: CMakeLists.txt 14773 2010-01-09 14:42:06Z loose $

lofar_package(Blob 1.2 DEPENDS Common)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa)
lofar_find_package(Blitz)

add_subdirectory(include/Blob)
add_subdirectory(src)
add_subdirectory(test)
