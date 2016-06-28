# $Id: CMakeLists.txt 31845 2015-06-18 10:13:45Z mol $

lofar_package(MessageBus 1.0 DEPENDS Common pyparameterset)

include(LofarFindPackage)
lofar_find_package(QPID)
lofar_find_package(LibXMLxx)
lofar_find_package(UnitTest++)

add_subdirectory(include/MessageBus)
add_subdirectory(src)
add_subdirectory(test)
