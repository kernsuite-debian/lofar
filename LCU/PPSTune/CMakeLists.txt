# $Id: CMakeLists.txt 26657 2013-09-24 11:35:59Z schoenmakers $

lofar_package(PPSTune 1.0)

add_subdirectory(ppstune)

# Install files matching regex pattern in current directory and below
# Omit directories test and testdata from install

install(DIRECTORY . 
  DESTINATION sbin
  USE_SOURCE_PERMISSIONS
  FILES_MATCHING REGEX "\\.(py|sh)$"
  PATTERN ".svn" EXCLUDE
  PATTERN "test*" EXCLUDE)

