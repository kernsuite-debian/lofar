# $Id$

IF(BUILD_TESTING)
    lofar_find_package(Python 3.4 REQUIRED)

    include(PythonInstall)

    set(_py_files
      postgres.py)

    python_install(${_py_files} DESTINATION lofar/common/testing)

    include(FindPythonModule)
    find_python_module(testing.postgresql)

    include(LofarCTest)

    file(COPY
      ${CMAKE_CURRENT_SOURCE_DIR}/python-coverage.sh
      DESTINATION ${CMAKE_BINARY_DIR}/bin)

    lofar_add_test(t_cache)
    lofar_add_test(t_dbcredentials)
    lofar_add_test(t_defaultmailaddresses)
    lofar_add_test(t_methodtrigger)
    lofar_add_test(t_util)
    lofar_add_test(t_test_utils)
    lofar_add_test(t_cep4_utils)
    lofar_add_test(t_postgres)
ENDIF()