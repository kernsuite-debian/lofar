# $Id$

lofar_package(MoMQueryServiceClient 1.0 DEPENDS MoMQueryServiceCommon PyMessaging)

include(PythonInstall)

set(_py_files
  momqueryrpc.py
)

python_install(${_py_files} DESTINATION lofar/mom/momqueryservice)

lofar_add_bin_scripts(momquery)