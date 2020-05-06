lofar_package(TaskManagementClient 1.0 DEPENDS TaskManagementCommon PyMessaging PyCommon)

lofar_find_package(Python 3.4 REQUIRED)

add_subdirectory(lib)
add_subdirectory(test)
