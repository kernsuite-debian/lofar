lofar_package(LTAIngestAdminServer 2.0 DEPENDS LTAIngestCommon LTAIngestServerCommon PyMessaging PyCommon MoMQueryServiceClient)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
