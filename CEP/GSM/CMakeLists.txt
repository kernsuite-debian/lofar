# $Id: CMakeLists.txt 22948 2012-11-23 08:54:47Z loose $

lofar_package(GSM 1.0)

include(LofarFindPackage)
lofar_find_package(Python 2.6 REQUIRED)

add_subdirectory(src)
#add_subdirectory(db)
add_subdirectory(test)
