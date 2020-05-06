include(LofarCTest)

IF(BUILD_TESTING)
    lofar_add_bin_program(wincclistener WinCCListener.cc)
ENDIF(BUILD_TESTING)
