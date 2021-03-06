# - Try to find a Python module.
# The macro PYTHON_FIND_PACKAGE(module) tries to find python module <module>.
#
# Variables defined by this module:
#  PYTHON_<MODULE>       - file path of python <module>, if found (cached)
#  PYTHON_<MODULE>_FOUND - true if python <module> was found, else false.

# Copyright (C) 2015
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
# $Id$

# Search for the Python interpreter.
find_package(PythonInterp 3)

# -----------------------------------------------------------------------------
# find_python_module(module [REQUIRED])
#
# Find the python module <module>.
# Set variable PYTHON_<MODULE> to the file path of <module> (cached).
# Set variable PYTHON_<MODULE>_FOUND to TRUE if <module> was found, else
# set it to FALSE.
# The REQUIRED option stops processing with an error message if the module
# <module> cannot be found.
# The HINTS option can be used to give a path (or colon-separated list of 
# paths) that are prepended to the search path.
# -----------------------------------------------------------------------------
include(CMakeParseArguments)

macro(find_python_module _module)
  # Name of module in uppercase.
  string(TOUPPER "${_module}" _MODULE)

  list(FIND ARGV REQUIRED is_required)

  IF(BUILD_DOCUMENTATION)
    IF(is_required GREATER -1)
        # Removing REQUIRED option while looking for package.
        # This allows cmake to continue configuring so you could make the doc,
        # but building the code might not be possible.
        # In case the package is not found, a WARNING is issued below.
        list(REMOVE_ITEM ARGV REQUIRED)
        list(REMOVE_ITEM ARGN REQUIRED)
    ENDIF()
  ENDIF(BUILD_DOCUMENTATION)

  cmake_parse_arguments(PYTHON_${_MODULE}_FIND
                        "REQUIRED"
                        "HINTS"
                        ""
                        ${ARGN}
                       )

  if(NOT "${PYTHON_${_MODULE}_FIND_UNPARSED_ARGUMENTS}" STREQUAL "")
    MESSAGE(FATAL_ERROR "Unknown arguments: ${PYTHON_${_MODULE}_FIND_UNPARSED_ARGUMENTS}")
  endif()

  # Try to find the python module, if we have not found it yet.
  if(NOT PYTHON_${_MODULE})
    # Try to import the python module we need to find, and get its file path.
    if(PYTHON_EXECUTABLE)
      set(ENV{PYTHONPATH} ${PYTHON_${_MODULE}_FIND_HINTS}:$ENV{PYTHONPATH})
      set(_cmd "from __future__ import print_function; import ${_module}; print(${_module}.__file__)")
      execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" "-c" "${_cmd}"
        RESULT_VARIABLE _result
        OUTPUT_VARIABLE _output
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE)

      # Set PYTHON_<MODULE> variable in the cache, if <module> was found.
      if(_result EQUAL 0)
        set(PYTHON_${_MODULE} ${_output} CACHE FILEPATH 
          "Path to python module ${_module}")
      endif()

    endif()
  endif()

  # Report result, and set PYTHON_<MODULE>_FOUND
  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(PYTHON_${_MODULE} DEFAULT_MSG 
    PYTHON_${_MODULE})

  if(NOT PYTHON_${_MODULE}_FOUND)
    if(is_required GREATER -1)
      message(WARNING "Removed REQUIRED option while looking for python module '${_module}' because BUILD_DOCUMENTATION=${BUILD_DOCUMENTATION}. This allows cmake to continue configuring so you could make the doc, but building the code might not be possible.")
    endif(is_required GREATER -1)
  endif(NOT PYTHON_${_MODULE}_FOUND)

endmacro()
