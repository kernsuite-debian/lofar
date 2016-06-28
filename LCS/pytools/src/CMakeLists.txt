# $Id: CMakeLists.txt 17197 2011-01-26 07:00:53Z diepen $

include(LofarPackageVersion)

lofar_add_library(lofar_pytools
        Package__Version.cc
        PycExcp.cc
        PycBasicData.cc
)

lofar_add_bin_program(versionpytools versionpytools.cc)

# Install Python modules
include(PythonInstall)
python_install(__init__.py DESTINATION lofar)


