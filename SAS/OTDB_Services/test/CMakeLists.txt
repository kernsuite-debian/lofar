# $Id: CMakeLists.txt 1576 2015-09-29 15:22:28Z loose $

if(BUILD_TESTING)
    include(LofarCTest)

    include(FindPythonModule)
    find_python_module(dateutil)

    include(PythonInstall)
    python_install(otdb_common_testing.py DESTINATION lofar/sas/otdb/testing)


    lofar_add_test(t_TreeService)
    lofar_add_test(t_TreeStatusEvents)
endif()




