lofar_add_package(LTAIngestServerCommon)
lofar_add_package(LTAIngestAdminServer)
lofar_add_package(LTAIngestTransferServer)
lofar_add_package(LTAIngestWebServer)

lofar_package(LTAIngestServer 2.0 DEPENDS LTAIngestAdminServer LTAIngestTransferServer)
