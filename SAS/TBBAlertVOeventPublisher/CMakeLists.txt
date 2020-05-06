
lofar_find_package(Python 3.4 REQUIRED)
lofar_package(TBBAlertVOeventPublisher 0.1 DEPENDS PyCommon)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)


