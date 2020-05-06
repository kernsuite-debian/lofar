# $Id$

lofar_package(Scheduler 1.0)

# Search for Qt4 and setup CMake environment for it
IF(BUILD_DOCUMENTATION)
  find_package(Qt4 COMPONENTS QtCore QtGui QtSql QtTest)
  IF(NOT Qt4_FOUND)
    message(WARNING "Removed REQUIRED option while looking for package 'Qt4' because BUILD_DOCUMENTATION=${BUILD_DOCUMENTATION}. This allows cmake to continue configuring so you could make the doc, but building the code might not be possible.")
  ENDIF()
ELSE()
  find_package(Qt4 COMPONENTS QtCore QtGui QtSql QtTest REQUIRED)
ENDIF(BUILD_DOCUMENTATION)

IF(Qt4_FOUND)
  include(${QT_USE_FILE})

  # Add current source- and binary directory to include path
  set(CMAKE_INCLUDE_CURRENT_DIR ON)

  add_subdirectory(src)
  add_subdirectory(test)
ENDIF(Qt4_FOUND)
