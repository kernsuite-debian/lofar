# $Id$

lofar_package(DataManagementCommon 1.0 DEPENDS PyMessaging ResourceAssignmentService MoMQueryServiceClient)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  config.py
  path.py
  datamanagementbuslistener.py
)

lofar_add_bin_scripts(getPathForTask)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/common)
