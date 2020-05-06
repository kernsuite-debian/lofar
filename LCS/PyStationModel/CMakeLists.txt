# $Id: CMakeLists.txt 720 2014-12-08 16:29:33Z loose $

lofar_package(PyStationModel 1.0 DEPENDS PyCommon StaticMetaData)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

python_install(
    antennasets_parser.py
    DESTINATION lofar/stationmodel
)

add_subdirectory(test)
