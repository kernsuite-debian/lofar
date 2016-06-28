# $Id: CMakeLists.txt 30977 2015-02-11 14:01:26Z mol $

# Create symbolic link to include directory.
execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink 
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_BINARY_DIR}/include/${PACKAGE_NAME}/Protocols)

# Install header files.
install(FILES
  TaskFeedbackDataproducts.h
  TaskFeedbackProcessing.h
  TaskFeedbackState.h
  TaskSpecificationSystem.h
  DESTINATION include/${PACKAGE_NAME}/Protocols)
