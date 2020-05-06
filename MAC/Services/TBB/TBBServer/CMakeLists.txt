lofar_package(TBBServer 2.0 DEPENDS TBB TBBClient TBBServiceCommon PyMessaging OTDB_Services ResourceAssignmentService pyparameterset)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
