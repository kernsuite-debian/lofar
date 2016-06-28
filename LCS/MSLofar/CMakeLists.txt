# $Id: CMakeLists.txt 17574 2011-03-18 09:07:29Z diepen $

lofar_package(MSLofar 0.1 DEPENDS ApplCommon Common)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa measures ms tables REQUIRED)

add_subdirectory(include/MSLofar)
add_subdirectory(src)
add_subdirectory(test)
