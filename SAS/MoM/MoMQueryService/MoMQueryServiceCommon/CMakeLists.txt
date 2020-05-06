# $Id$

lofar_package(MoMQueryServiceCommon 1.0)

include(PythonInstall)

set(_py_files
  config.py
)

python_install(${_py_files} DESTINATION lofar/mom/momqueryservice)

