# $Id: CMakeLists.txt 32333 2015-08-28 08:15:24Z schaap $
include(LofarCTest)
include(FindPythonModule)

find_python_module(uuid REQUIRED)

lofar_add_test(t_taskmanagement_rpc)
