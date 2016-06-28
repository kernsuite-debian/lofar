# $Id: CMakeLists.txt 20828 2012-05-02 11:24:10Z loose $

add_f2py_module(_pytesselate
  pytess_simple.f
  pytess_roundness.f
  DESTINATION ${PYTHON_INSTALL_DIR}/lofar/bdsm)

