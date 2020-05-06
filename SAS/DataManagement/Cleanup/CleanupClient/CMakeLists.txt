# $Id$

lofar_package(CleanupClient 1.0 DEPENDS PyMessaging CleanupCommon)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  rpc.py
)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/cleanup)

lofar_add_bin_scripts(cleanup autocleanup_ingested_data)

