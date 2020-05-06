# $Id$

lofar_package(checkhardware 1.0 DEPENDS PyCommon)
include(PythonInstall)

# install for testing in cmake
set(_py_files
  check_hardware.py
)

python_install(${_py_files} DESTINATION lofar/lcu/checkhardware)


# Install files matching regex pattern in current directory and below
install(DIRECTORY . 
  DESTINATION stationtest
  USE_SOURCE_PERMISSIONS
  FILES_MATCHING REGEX "(README\\.txt|\\.(gold|m|py|sh))$"
  PATTERN ".svn" EXCLUDE)

install(DIRECTORY config/
  DESTINATION stationtest/configfiles
  USE_SOURCE_PERMISSIONS
  FILES_MATCHING REGEX "(\\.conf)$"
  PATTERN ".svn" EXCLUDE)


add_subdirectory(test)
add_subdirectory(checkhardware_lib)


