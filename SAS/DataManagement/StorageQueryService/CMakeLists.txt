# $Id$

lofar_package(StorageQueryService 1.0 DEPENDS PyMessaging MoMQueryServiceClient DataManagementCommon OTDB_Services)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  config.py
  rpc.py
  service.py
  diskusage.py
  cache.py
)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/storagequery)

lofar_add_bin_scripts(storagequery storagequeryservice)

# supervisord config files
install(FILES
  storagequeryservice.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(test)
