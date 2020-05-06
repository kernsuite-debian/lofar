lofar_package(AutoCleanupService 1.0 DEPENDS PyMessaging CleanupClient LTAIngestClient)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

lofar_add_bin_scripts(autocleanupservice)

# supervisord config files
install(FILES
  autocleanupservice.ini
  DESTINATION etc/supervisord.d)

