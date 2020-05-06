# $Id$

include(LofarCTest)
include(FindPythonModule)

# We need to create a symlink to the parmdbm executable in the current
# binary directory, so that the test program(s) can find it.
lofar_create_target_symlink(
  parmdbm
  ${CMAKE_CURRENT_BINARY_DIR}/parmdbm)

find_python_module(numpy)
if(PYTHON_NUMPY_FOUND)
  lofar_add_test(tpyparmdb DEPENDS parmdbm _parmdb)
else(PYTHON_NUMPY_FOUND)
  message(WARNING "Numpy not found, disabling tpyparmdb test")
endif(PYTHON_NUMPY_FOUND)
