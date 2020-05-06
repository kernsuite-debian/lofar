# $Id$

lofar_package(PyBDSM 1.0)

include(PythonInstall)

python_install(
  __init__.py
  DESTINATION lofar/bdsm)

include(FindPythonModule)
find_python_module(bdsf REQUIRED HINTS ${BDSF_ROOT_DIR})
add_subdirectory(test)
