# $Id: CMakeLists.txt 27640 2013-12-04 08:02:49Z diepen $

lofar_package(PythonDPPP 0.1 DEPENDS DPPP pyparameterset)

# Try to find Boost-Python.
# If found, build this package. Otherwise give a warning.
FIND_PATH(BOOST_PYTHON_FOUND "boost/python.hpp")

if(BOOST_PYTHON_FOUND)
  include(LofarFindPackage)
  lofar_find_package(Python 3.4 REQUIRED)
  lofar_find_package(Boost REQUIRED COMPONENTS python3)
  lofar_find_package(Casacore COMPONENTS casa ms tables python REQUIRED)

  add_subdirectory(include/PythonDPPP)
  add_subdirectory(src)
  add_subdirectory(test)
else()
  message (WARNING, " Boost-Python not found; PythonDPPP will not be built.")
endif()
