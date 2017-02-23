# $Id: CMakeLists.txt 35903 2016-11-04 13:11:40Z loose $

# Create symbolic link to include directory.
execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink 
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_BINARY_DIR}/include/${PACKAGE_NAME})

# Install header files.
install(FILES
  Exceptions.h
  FromBus.h
  Message.h
  MessageBus.h
  NoQpidFallback.h
  ToBus.h
  XMLDoc.h
  DESTINATION include/${PACKAGE_NAME})

install(FILES
  Protocols/TaskFeedbackDataproducts.h
  Protocols/TaskFeedbackProcessing.h
  Protocols/TaskFeedbackState.h
  Protocols/TaskSpecificationSystem.h
  DESTINATION include/${PACKAGE_NAME}/Protocols)

