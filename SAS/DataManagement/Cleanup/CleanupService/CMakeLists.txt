# $Id$

lofar_package(CleanupService 1.0 DEPENDS PyMessaging DataManagementCommon CleanupCommon)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  service.py
)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/cleanup)

lofar_add_bin_scripts(cleanupservice)

# supervisord config files
install(FILES
  cleanupservice.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(test)
