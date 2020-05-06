# $Id$

lofar_package(ObservationStartListener 1.0 DEPENDS MessageBus pyparameterset)

include(LofarFindPackage)
lofar_find_package(Python 3.4 REQUIRED)

lofar_find_package(QPID)

add_subdirectory(etc)
add_subdirectory(src)
add_subdirectory(test)
