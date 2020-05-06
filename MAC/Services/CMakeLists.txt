# $Id$

lofar_package(MAC_Services 1.0 DEPENDS PyMessaging OTDB_Services pyparameterset Docker ResourceAssignmentService TBBService)

add_subdirectory(src)
add_subdirectory(test)
lofar_add_package(TBBService TBB)
