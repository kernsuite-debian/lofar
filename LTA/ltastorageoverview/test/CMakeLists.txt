# $Id$

IF(BUILD_TESTING)
    lofar_find_package(Python 3.4 REQUIRED)
    include(PythonInstall)

    set(_py_files
      common_test_ltastoragedb.py)

    python_install(${_py_files} DESTINATION lofar/lta/ltastorageoverview/testing)

    include(FindPythonModule)
    find_python_module(flask.testing REQUIRED)

    include(LofarCTest)

    lofar_add_test(test_store)
    lofar_add_test(test_scraper)
    lofar_add_test(test_lso_webservice)
    lofar_add_test(test_ingesteventhandler)

    lofar_add_test(integration_test_store)
ENDIF()