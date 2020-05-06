SET(CMAKE_C_FLAGS "-std=gnu99")

#tmp hack until #8256 is merged into trunk
SET(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)

lofar_add_bin_program(md5a32bc md5a32bc.c adler32.c)
