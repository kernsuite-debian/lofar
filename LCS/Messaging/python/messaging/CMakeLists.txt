# $Id$

lofar_package(PyMessaging 1.0 DEPENDS PyCommon)

lofar_find_package(Python 3.4 REQUIRED)

include(FindPythonModule)
find_python_module(kombu REQUIRED)
find_python_module(requests REQUIRED)

include(PythonInstall)

set(_py_files
  __init__.py
  config.py
  exceptions.py
  messagebus.py
  messages.py
  rpc.py
)

python_install(${_py_files} DESTINATION lofar/messaging)

add_subdirectory(test)
