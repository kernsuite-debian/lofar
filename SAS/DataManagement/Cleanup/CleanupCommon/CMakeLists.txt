# $Id$

lofar_package(CleanupCommon 1.0 )

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  config.py
)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/cleanup)

