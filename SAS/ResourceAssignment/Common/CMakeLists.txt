# $Id: CMakeLists.txt 30355 2014-11-04 13:46:05Z loose $

lofar_package(RACommon 0.1 DEPENDS pyparameterset MoMQueryService ResourceAssignmentService )

include(PythonInstall)
set(USE_PYTHON_COMPILATION Off)

add_subdirectory(lib)
add_subdirectory(test)
