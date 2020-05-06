# $Id$

lofar_package(MoMQueryServiceServer 1.0 DEPENDS PyMessaging MoMQueryServiceCommon MoMQueryServiceClient MoMSimpleAPIs)

include(PythonInstall)
include(FindPythonModule)

set(_py_files
  momqueryservice.py
)

python_install(${_py_files} DESTINATION lofar/mom/momqueryservice)

lofar_add_bin_scripts(momqueryservice)

# supervisord config files
install(FILES
  momqueryservice.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(test)
