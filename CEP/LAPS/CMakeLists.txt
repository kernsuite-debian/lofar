# $Id: CMakeLists.txt 29899 2014-08-12 12:43:23Z klijn $

lofar_add_package(Laps-GRIDInterface GRIDInterface)
lofar_add_package(Laps-ParsetCombiner ParsetCombiner)
lofar_add_package(Laps-DBToQDeamon DBToQDeamon)
lofar_add_package(Laps-QToPipeline QToPipeline)
lofar_add_package(Laps-Messaging Messaging)

add_subdirectory(test)

INSTALL(DIRECTORY DESTINATION var/run/laps)

