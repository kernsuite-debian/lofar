# $Id: CMakeLists.txt 34529 2016-05-24 17:00:41Z mol $

include(LofarCTest)

file(COPY
  ${CMAKE_CURRENT_SOURCE_DIR}/python-coverage.sh
  DESTINATION ${CMAKE_BINARY_DIR}/bin)

lofar_add_test(t_dbcredentials)
lofar_add_test(t_methodtrigger)
