# $Id$

# Python can be explicitly disabled, if only the C++ libraries are needed
if(USE_PYTHON)
  lofar_package(MessageBus 1.0 DEPENDS Common pyparameterset)
else(USE_PYTHON)
  lofar_package(MessageBus 1.0 DEPENDS Common)
endif(USE_PYTHON)

include(LofarFindPackage)
lofar_find_package(QPID)
lofar_find_package(UnitTest++)

add_subdirectory(include/MessageBus)
add_subdirectory(src)
add_subdirectory(test)
