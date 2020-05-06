
lofar_find_package(Python 3.4 REQUIRED)
lofar_package(TriggerServices 0.1 DEPENDS PyMessaging MoMQueryService SpecificationServices OTDB_Services ResourceAssignmentService TBB TBBClient TriggerEmailService)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
add_subdirectory(django_rest)


