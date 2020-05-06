# $Id$

include(LofarCTest)

include(LofarFindPackage)

lofar_find_package(Casacore REQUIRED COMPONENTS python)
if(CASA_PYTHON3_LIBRARY)
  #This test is disabled due to boost-python linking problems on CEP3
  #lofar_add_test(tStationBeamNCP)
else(CASA_PYTHON3_LIBRARY)
  message(WARNING "Python-casacore was not found, disabling tStationBeamNCP")
endif(CASA_PYTHON3_LIBRARY)

lofar_add_test(tpystationresponse)
