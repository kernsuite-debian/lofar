# $Id$

include(LofarCTest)

set(_tests
  tRSPRaw
)

foreach(_test ${_tests})
  lofar_add_test(${_test} DEPENDS printRSP)  # printRSP is used in *-check-output.sh script
  if(BUILD_TESTING)
    set_tests_properties(${_test} PROPERTIES RUN_SERIAL ON)
  endif(BUILD_TESTING)
endforeach(_test ${_tests})
