# Copy the styling files to the build folder

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/customdoxygen.css.in"
  "${CMAKE_BINARY_DIR}/customdoxygen.css" @ONLY)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/doxy-boot.js.in"
  "${CMAKE_BINARY_DIR}/doxy-boot.js" @ONLY)
 
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/footer.html.in"
  "${CMAKE_BINARY_DIR}/footer.html" @ONLY)
 
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/header.html.in"
  "${CMAKE_BINARY_DIR}/header.html" @ONLY)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.min.js.in"
  "${CMAKE_BINARY_DIR}/bootstrap.min.js" @ONLY)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.min.css.in"
  "${CMAKE_BINARY_DIR}/bootstrap.min.css" @ONLY)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/jquery-2.1.1.min.js.in"
  "${CMAKE_BINARY_DIR}/jquery-2.1.1.min.js" @ONLY)
  
configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/jquery.powertip.min.js.in"
  "${CMAKE_BINARY_DIR}/jquery.powertip.min.js" @ONLY)

file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/LOFAR_logo.png" DESTINATION "${CMAKE_BINARY_DIR}")
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/glyphicons-halflings-regular.ttf" DESTINATION "${CMAKE_BINARY_DIR}")
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/glyphicons-halflings-regular.woff" DESTINATION "${CMAKE_BINARY_DIR}")
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/glyphicons-halflings-regular.eot" DESTINATION "${CMAKE_BINARY_DIR}")
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/glyphicons-halflings-regular.svg" DESTINATION "${CMAKE_BINARY_DIR}")
