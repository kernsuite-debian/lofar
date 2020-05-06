# $Id$

lofar_package(TaskPrescheduler 1.0 DEPENDS PyMessaging ResourceAssignmentService OTDB_Services MoMQueryServiceClient pyparameterset RACommon)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  taskprescheduler.py
)

python_install(${_py_files} DESTINATION lofar/sas/resourceassignment/taskprescheduler)

lofar_add_bin_scripts(taskprescheduler)

# supervisord config files
install(FILES
  taskprescheduler.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(lib)
add_subdirectory(test)
