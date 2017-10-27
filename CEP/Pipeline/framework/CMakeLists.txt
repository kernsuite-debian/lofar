# $Id: CMakeLists.txt 37520 2017-05-31 08:07:25Z dijkema $

lofar_package(Pipeline-Framework 0.1 DEPENDS MessageBus)

include(FindPythonModule)
find_python_module(xmlrunner REQUIRED)

add_subdirectory(lofarpipe)
