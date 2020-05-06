lofar_package(LTAIngestClient 2.0 DEPENDS LTAIngestCommon PyMessaging PyCommon)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
