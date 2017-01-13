# $Id: CMakeLists.txt 36096 2016-12-02 10:13:05Z mol $

lofar_package(PyBDSM 1.0)
enable_language(Fortran)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED COMPONENTS python)
lofar_find_package(Python 2.6 REQUIRED)
lofar_find_package(Numpy REQUIRED)

add_subdirectory(src)
add_subdirectory(test)
