# $Id: CMakeLists.txt 15052 2010-02-24 11:04:19Z loose $

# List of header files that will be installed.
set(inst_HEADERS
  CombinerProcessControl.h
  SPWCombine.h)

# Create symbolic link to include directory.
execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink 
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_BINARY_DIR}/include/SPWCombine)

# Install header files.
install(FILES ${inst_HEADERS} DESTINATION include/${PACKAGE_NAME})
