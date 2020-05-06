# $Id: CMakeLists.txt 32679 2015-10-26 09:31:56Z schaap $

if(BUILD_TESTING)
    include(LofarCTest)

    include(FindPythonModule)
    find_python_module(dateutil)

    include(PythonInstall)
    python_install(radb_common_testing.py DESTINATION lofar/sas/resourceassignment/database/testing)

    lofar_add_test(t_radb_functionality)
    lofar_add_test(t_radb_performance)

    set_tests_properties(t_radb_functionality PROPERTIES TIMEOUT 300)
    set_tests_properties(t_radb_performance PROPERTIES TIMEOUT 300)
endif()