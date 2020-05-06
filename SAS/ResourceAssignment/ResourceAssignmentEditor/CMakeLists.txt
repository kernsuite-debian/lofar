# $Id: CMakeLists.txt 30355 2014-11-04 13:46:05Z loose $

lofar_package(ResourceAssignmentEditor 1.0 DEPENDS MoMQueryService ResourceAssignmentService PyMessaging DataManagement LTAIngestClient)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
add_subdirectory(config)
