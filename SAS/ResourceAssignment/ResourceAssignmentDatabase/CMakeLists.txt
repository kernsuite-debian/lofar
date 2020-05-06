# $Id$

lofar_package(ResourceAssignmentDatabase 1.0 DEPENDS PyMessaging PyCommon)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  config.py
  radb.py
  radbpglistener.py
  radbbuslistener.py)

python_install(${_py_files} DESTINATION lofar/sas/resourceassignment/database)

lofar_add_bin_scripts(radbpglistener)

# supervisord config files
install(FILES
  radbpglistener.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(tests)

set(sql_files radb/sql/add_notifications.sql
              radb/sql/add_functions_and_triggers.sql
              radb/sql/add_resource_allocation_statics.sql
              radb/sql/add_virtual_instrument.sql
              radb/sql/create_database.sql
              radb/sql/create_and_populate_database.sql)

lofar_add_data_files(${sql_files})
