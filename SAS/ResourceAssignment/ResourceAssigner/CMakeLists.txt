# $Id: CMakeLists.txt 30355 2014-11-04 13:46:05Z loose $

lofar_package(ResourceAssigner 0.1 DEPENDS PyMessaging PyCommon pyparameterset OTDB_Services RACommon ResourceAssignmentService MoMQueryServiceClient ResourceAssignmentEstimator CleanupClient StorageQueryService MAC_Services MessageBus )

include(PythonInstall)
set(USE_PYTHON_COMPILATION Off)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
