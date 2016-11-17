# - Try to find WINCC (Prozessvisualisierungs- und Steuerungssystem)
# Variables used by this module:
#  WINCC_ROOT_DIR     - WINCC root directory
# Variables defined by this module:
#  WINCC_FOUND        - System has WINCC
#  WINCC_DEFINITIONS  - Compiler definitions required for WINCC 
#  WINCC_INCLUDE_DIR  - "Top-level" WINCC include directory (cached)
#  WINCC_INCLUDE_DIRS - List of WINCC include directories
#  WINCC_LIBRARY_DIR  - WINCC library directory (cached)
#  WINCC_LIBRARIES    - List of all WINCC libraries

# Copyright (C) 2009
# ASTRON (Netherlands Institute for Radio Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: FindWINCC.cmake 29938 2014-08-19 14:11:24Z loose $

# Compiler definitions required for WINCC
set(wincc_definitions
  -D__UNIX
  -D__PC
  -DHAS_TEMPLATES=1 
  -DBC_DESTRUCTOR 
  -Dbcm_boolean_h 
  -DOS_LINUX 
  -DLINUX 
  -DDLLEXP_BASICS= 
  -DDLLEXP_CONFIGS= 
  -DDLLEXP_DATAPOINT= 
  -DDLLEXP_MESSAGES= 
  -DDLLEXP_MANAGER= 
  -DDLLEXP_CTRL=
  -DDLLEXP_BCM=
)
  
# Define WINCC include directories, relative to top-level include directory.
set(wincc_include_dirs 
  Basics/DpBasics 
  Basics/Variables 
  Basics/Utilities 
  Basics/NoPosix 
  BCMNew 
  Configs 
  Datapoint 
  Messages 
  Manager)

# Define WINCC libraries.
set(wincc_libraries 
  Manager
  Messages 
  Datapoint 
  Basics 
  bcm)
  
if(NOT WINCC_FOUND)

  # Get the WINCC version information. This information can be found in the file
  # VersInfo.mk, which sets a number of Makefile variables. The version string
  # that is used in the filenames of the shared libraries can be found in the
  # variable WINCC_DLL_VERS. This variable is either set directly, or composed
  # from the Makefile variables WINCC_VERSION_MAIN and WINCC_VERSION_BUILD.
  find_file(WINCC_VERSINFO_MK
    NAMES VersInfo.mk
    HINTS ${WINCC_ROOT_DIR}
    PATH_SUFFIXES api)
  mark_as_advanced(WINCC_VERSINFO_MK)

  if(NOT WINCC_VERSINFO_MK)
    set(_errmsg "Could NOT find file api/VersInfo.mk.\nPlease make sure that WINCC_ROOT_DIR is set to the root directory of your WINCC installation.")
    if(WINCC_FIND_REQUIRED)
      message(FATAL_ERROR "${_errmsg}")
    elseif(NOT WINCC_FIND_QUIETLY)
      message(STATUS "${_errmsg}")
    endif()
    return()
  endif()

  # Get the main version
  file(STRINGS ${WINCC_VERSINFO_MK} match REGEX "^PVSS_VERS *=")
  string(REGEX REPLACE "^.*= *([^ ]+)$" "\\1" PVSS_VERS "${match}")

  # Get the build version
  file(STRINGS ${WINCC_VERSINFO_MK} match REGEX "^PVSS_VERSION_BUILD *=")
  string(REGEX REPLACE "^.*= *([^ ]+)$" "\\1" PVSS_VERSION_BUILD "${match}")

  # Get the library version (which may contains Makefile variables)
  file(STRINGS ${WINCC_VERSINFO_MK} match REGEX "^PVSS_DLL_VERS *=")
  string(REGEX REPLACE "^.*= *([^ ]+)$" "\\1" match "${match}")

  # Replace Makefile variables $(name) with CMake variables ${name}
  string(REGEX REPLACE "\\(([^)]+)\\)" "{\\1}" match "${match}")

  # Replace the CMake variables with their contents
  string(CONFIGURE "${match}" PVSS_DLL_VERS)

  message(STATUS "Searching for WINCC ${PVSS_DLL_VERS}")

  # Search for the WINCC include directory
  find_path(WINCC_INCLUDE_DIR
    NAMES Basics/Utilities/Util.hxx
    HINTS ${WINCC_ROOT_DIR}
    PATH_SUFFIXES api/include)
  set(WINCC_INCLUDE_DIRS ${WINCC_INCLUDE_DIR})
  set(wincc_check_list WINCC_INCLUDE_DIR)
  
  # Search for the WINCC libraries
  string(TOLOWER "${CMAKE_SYSTEM_NAME}" osname)
  foreach(lib ${wincc_libraries})
    find_library(WINCC_${lib}_LIBRARY
      NAMES ${lib}${PVSS_DLL_VERS}
      HINTS ${WINCC_ROOT_DIR}
      PATH_SUFFIXES api/lib.${osname} bin)
    list(APPEND wincc_check_list WINCC_${lib}_LIBRARY)
  endforeach()

  # Mark all variables in wincc_check_list as advanced
  mark_as_advanced(${wincc_check_list})
  
  # Handle the QUIETLY and REQUIRED arguments and set WINCC_FOUND to TRUE if
  # all elements of wincc_check_list are TRUE.
  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(WINCC DEFAULT_MSG ${wincc_check_list})
  
  # Now it's time to fill the non-cached variables
  if(WINCC_FOUND)
    foreach(def ${wincc_definitions})
      set(WINCC_DEFINITIONS "${WINCC_DEFINITIONS} ${def}")
    endforeach()
    foreach(dir ${wincc_include_dirs})
      list(APPEND WINCC_INCLUDE_DIRS ${WINCC_INCLUDE_DIR}/${dir})
    endforeach()
    foreach(lib ${wincc_libraries})
      list(APPEND WINCC_LIBRARIES ${WINCC_${lib}_LIBRARY})
    endforeach()
  endif()

endif()
