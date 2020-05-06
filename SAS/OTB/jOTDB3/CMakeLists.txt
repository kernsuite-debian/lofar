# $Id: CMakeLists.txt 14714 2009-12-21 13:32:38Z loose $

lofar_package(jOTDB3 1.0 DEPENDS Common OTDB)

include(LofarFindPackage)
lofar_find_package(Boost REQUIRED COMPONENTS date_time)
lofar_find_package(PQXX REQUIRED)

# Don't use lofar_find_package(JNI), because we don't need to link in the
# JNI libraries; we only need the JNI header files.
IF(BUILD_DOCUMENTATION)
  find_package(JNI)
  IF(NOT JNI_FOUND)
    message(WARNING "Removed REQUIRED option while looking for package 'JNI' because BUILD_DOCUMENTATION=${BUILD_DOCUMENTATION}. This allows cmake to continue configuring so you could make the doc, but building the code might not be possible.")
  ENDIF()
ELSE()
  find_package(JNI REQUIRED)
ENDIF()

include_directories(${JNI_INCLUDE_DIRS})

add_subdirectory(include/jOTDB3)
add_subdirectory(src)
#add_subdirectory(test)
