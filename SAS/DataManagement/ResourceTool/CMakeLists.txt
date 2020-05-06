# $Id$

lofar_package(ResourceTool 1.0 DEPENDS ResourceAssignmentService PyCommon)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  resourcetool.py
)

python_install(${_py_files} DESTINATION lofar/sas/datamanagement/resourcetool)

lofar_add_bin_scripts(resourcetool)

add_subdirectory(test)
