# $Id$

lofar_add_package(OTDB)
lofar_add_package(OTB)
lofar_add_package(OTDB_SQL OTDB/sql)
lofar_add_package(QPIDInfrastructure)
lofar_add_package(Scheduler)
lofar_add_package(SAS_Feedback Feedback_Service)
lofar_add_package(OTDB_Services)
lofar_add_package(XML_generator)
lofar_add_package(TriggerServices)
lofar_add_package(TriggerEmailService)
lofar_add_package(SpecificationServices)
lofar_add_package(XSD)
lofar_add_package(TBBAlertVOeventPublisher)

add_subdirectory(MoM)
add_subdirectory(ResourceAssignment)
add_subdirectory(DataManagement)
