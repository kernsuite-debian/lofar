# $Id: CMakeLists.txt 35890 2016-11-03 13:16:09Z schoenmakers $

lofar_add_package(OTDB)
lofar_add_package(OTB)
lofar_add_package(OTDB_SQL OTDB/sql)
lofar_add_package(QPIDInfrastructure)
lofar_add_package(Scheduler)
lofar_add_package(SAS_Feedback Feedback_Service)
lofar_add_package(CleanupTool)
lofar_add_package(OTDB_Services)
lofar_add_package(XML_generator)

add_subdirectory(MoM)
add_subdirectory(ResourceAssignment)
add_subdirectory(DataManagement)
