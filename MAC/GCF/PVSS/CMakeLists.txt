# $Id$

lofar_package(GCFPVSS 1.0 DEPENDS Common GCFTM)

include(LofarFindPackage)
lofar_find_package(WINCC REQUIRED)

add_subdirectory(include/GCF/PVSS)
add_subdirectory(src)
add_subdirectory(test)
