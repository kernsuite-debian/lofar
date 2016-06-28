# $Id: CMakeLists.txt 14280 2009-10-16 13:48:46Z loose $

lofar_package(SPW_Combine 1.0 DEPENDS Common PLC)

include(LofarFindPackage)
lofar_find_package(Casacore COMPONENTS casa ms tables REQUIRED)

add_subdirectory(include/SPWCombine)
add_subdirectory(src)
#add_subdirectory(test)
