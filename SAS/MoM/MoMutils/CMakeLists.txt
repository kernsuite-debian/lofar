# $Id$

lofar_package(MoMutils 1.0 DEPENDS MoMSimpleAPIs PyCommon)

include(PythonInstall)
include(FindPythonModule)

find_python_module(requests REQUIRED)
find_python_module(mysql REQUIRED)

set(_py_files
  predecessor_connections.py
)

python_install(${_py_files} DESTINATION lofar/mom/utils)

lofar_add_bin_scripts(fix_mom_predecessor_connections)