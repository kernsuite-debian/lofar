# $Id: CMakeLists.txt 34529 2016-05-24 17:00:41Z mol $

lofar_add_package(CleanupCommon)
lofar_add_package(CleanupService)
lofar_add_package(CleanupClient)
lofar_add_package(AutoCleanupService)

lofar_package(Cleanup DEPENDS CleanupService CleanupClient AutoCleanupService CleanupCommon)

