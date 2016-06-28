# $Id: CMakeLists.txt 34754 2016-06-20 10:56:00Z schaap $

include(LofarCTest)

file(COPY
  ${CMAKE_CURRENT_SOURCE_DIR}/python-coverage.sh
  DESTINATION ${CMAKE_BINARY_DIR}/bin)

lofar_add_test(t_dbcredentials)
lofar_add_test(t_methodtrigger)
