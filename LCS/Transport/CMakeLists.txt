# $Id: CMakeLists.txt 14280 2009-10-16 13:48:46Z loose $

lofar_package(Transport 2.3 DEPENDS Blob)

add_subdirectory(include/Transport)
add_subdirectory(src)
add_subdirectory(test)
