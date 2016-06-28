# $Id: CMakeLists.txt 16887 2010-12-08 10:46:43Z diepen $

lofar_package(MS 0.1 DEPENDS Common Blob LMWCommon)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa measures ms tables REQUIRED)

add_subdirectory(include/MS)
add_subdirectory(src)
add_subdirectory(test)
