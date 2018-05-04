# $Id: CMakeLists.txt 38972 2018-01-30 14:17:21Z schaap $

lofar_add_package(MACIO)       # MAC I/O related functions
lofar_add_package(GCF)         # Generic Control Framework
lofar_add_package(APL)         # Application subdirectory
lofar_add_package(Deployment)  # Deployment related functions
lofar_add_package(Navigator2)
lofar_add_package(MACTools Tools)
lofar_add_package(MAC_Services Services)
lofar_add_package(WinCC_Datapoints Deployment/data/PVSS)
lofar_add_package(OTDB_Comps Deployment/data/OTDB)
lofar_add_package(StaticMetaData Deployment/data/StaticMetaData)
lofar_add_package(WinCCPublisher WinCCPublisher)
lofar_add_package(TaskManagement Services/TaskManagement)


