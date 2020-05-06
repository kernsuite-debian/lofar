# $Id: CMakeLists.txt 32985 2015-11-26 11:10:57Z schaap $

lofar_find_package(Python 3.4 REQUIRED)
lofar_package(sip 0.1 DEPENDS PyCommon LTACommon)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)

