lofar_package(TriggerEmailServiceServer 1.0 DEPENDS TriggerEmailServiceCommon OTDB_Services MoMQueryService PyMessaging PyCommon)

lofar_find_package(Python 3.4 REQUIRED)

add_subdirectory(bin)
add_subdirectory(lib)
add_subdirectory(test)
