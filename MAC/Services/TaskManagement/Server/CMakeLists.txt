lofar_package(TaskManagementServer 1.0 DEPENDS TaskManagementCommon OTDB_Services MAC_Services ResourceAssignmentService PyMessaging PyCommon)

lofar_find_package(Python 3.4 REQUIRED)

add_subdirectory(bin)
add_subdirectory(lib)
add_subdirectory(test)
