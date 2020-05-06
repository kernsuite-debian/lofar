# $Id: CMakeLists.txt  $

lofar_package(Cobalt_validation)

# we choose a bit of an odd location for the validation scripts.
# yes, the scripts validate script and the individual tests are executable, so you could think they belong in bin or sbin...
# but we do not want the validation test directory tree in bin or sbin
# We also want the validation "suite" in a self contained folder,
# so we choose pragmatically for share/validation
SET(DEST "share/validation")
FILE(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/${DEST})

# add the validate script...
INSTALL(PROGRAMS validate DESTINATION ${DEST})

# and add convenience symlink in the build dir
EXECUTE_PROCESS(COMMAND ${CMAKE_COMMAND} -E create_symlink
                ${CMAKE_CURRENT_SOURCE_DIR}/validate
                ${CMAKE_BINARY_DIR}/${DEST}/validate)

# add "normal" files to installation and add symlink
SET(files README validation_utils.sh)
FOREACH(file ${files})
    INSTALL(FILES ${file} DESTINATION ${DEST})

    EXECUTE_PROCESS(COMMAND ${CMAKE_COMMAND} -E create_symlink
                    ${CMAKE_CURRENT_SOURCE_DIR}/${file}
                    ${CMAKE_BINARY_DIR}/${DEST}/${file})
ENDFOREACH()


# and add each and every subdirectory tree as-is.
FILE(GLOB children RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/*)
FOREACH(child ${children})
    IF(IS_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${child})
        INSTALL(DIRECTORY ${child}
                USE_SOURCE_PERMISSIONS
                DESTINATION ${DEST})
        EXECUTE_PROCESS(COMMAND ${CMAKE_COMMAND} -E create_symlink
                        ${CMAKE_CURRENT_SOURCE_DIR}/${child}
                        ${CMAKE_BINARY_DIR}/${DEST}/${child})
    ENDIF()
ENDFOREACH()

