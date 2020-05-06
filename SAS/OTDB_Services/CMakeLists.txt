# $Id$

lofar_package(OTDB_Services 1.0 DEPENDS PyMessaging)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

#find_python_module(pg REQUIRED) # sudo aptitude install python3-pg

lofar_add_bin_scripts(
  getOTDBParset
  setOTDBTreeStatus
  treeService
  treeStatusEvents
  setCorrelatorHeadNode
)

set(_py_files
  config.py
  otdbrpc.py
  OTDBBusListener.py
  TreeService.py
  TreeStatusEvents.py
)

# supervisord config files
install(FILES
  TreeService.ini
  TreeStatusEvents.ini
  OTDB_Services.ini
  DESTINATION etc/supervisord.d)

python_install(${_py_files} DESTINATION lofar/sas/otdb)

add_subdirectory(test)

