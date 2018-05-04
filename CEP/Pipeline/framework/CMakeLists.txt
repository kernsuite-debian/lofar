# $Id: CMakeLists.txt 39261 2018-03-23 08:30:24Z schoenmakers $

lofar_package(Pipeline-Framework 0.1 DEPENDS MessageBus PyCommon)

include(FindPythonModule)
find_python_module(xmlrunner REQUIRED)

add_subdirectory(lofarpipe)
