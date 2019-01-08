# $Id: CMakeLists.txt 39720 2018-06-15 11:37:36Z dijkema $

include(LofarCTest)

include(FindPythonModule)

find_python_module(pyrap)
if(PYTHON_PYRAP_FOUND)
  #This test is disabled due to boost-python linking problems on CEP3
  #lofar_add_test(tStationBeamNCP)
else(PYTHON_PYRAP_FOUND)
  message(WARNING "Python-casacore was not found, disabling tStationBeamNCP")
endif(PYTHON_PYRAP_FOUND)

lofar_add_test(tpystationresponse)
