# $Id$

lofar_package(MoMSimpleAPIs 1.0)

include(PythonInstall)
include(FindPythonModule)

find_python_module(requests REQUIRED)
find_python_module(mysql REQUIRED)

set(_py_files
  momhttpclient.py
  momdbclient.py
)

python_install(${_py_files} DESTINATION lofar/mom/simpleapis)

