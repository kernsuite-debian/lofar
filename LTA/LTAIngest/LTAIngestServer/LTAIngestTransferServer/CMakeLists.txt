lofar_package(LTAIngestTransferServer 2.0 DEPENDS LTACommon LTAIngestCommon LTAIngestServerCommon PyMessaging PyCommon MoMSimpleAPIs MessageLogger)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
