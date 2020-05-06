# $Id: CMakeLists.txt 32679 2015-10-26 09:31:56Z schaap $
include(LofarCTest)
include(FindPythonModule)

find_python_module(mysql)
find_python_module(testing.mysqld)

lofar_add_test(t_momqueryservice)

