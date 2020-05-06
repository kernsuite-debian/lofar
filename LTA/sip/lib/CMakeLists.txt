# $Id$

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
  __init__.py
  siplib.py
  ltasip.py
  feedback.py
  validator.py
  constants.py
  visualizer.py
  query.py
)


set(resource_files
  station_coordinates.conf
)


python_install(${_py_files}
               DESTINATION lofar/lta/sip)

install(FILES ${resource_files}
  DESTINATION ${PYTHON_INSTALL_DIR}/lofar/lta/sip)


install(FILES ${resource_files}
  DESTINATION ${PYTHON_BUILD_DIR}/lofar/lta/sip)


