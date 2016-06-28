# $Id: CMakeLists.txt 32215 2015-08-18 11:41:34Z loose $

lofar_add_package(Pipeline-Framework framework)
lofar_add_package(Pipeline-Recipes recipes)

add_subdirectory(test)

INSTALL(DIRECTORY DESTINATION var/run/pipeline)
INSTALL(DIRECTORY DESTINATION var/log)
