lofar_package(TBBClient 2.0 DEPENDS PyMessaging PyCommon TBBServiceCommon)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
