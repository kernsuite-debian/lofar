
lofar_add_bin_scripts(ingestmomadapter
                      ingestjobmanagementserver)

# supervisord config files
install(FILES
  ingestmomadapter.ini
  ingestjobmanagementserver.ini
  DESTINATION etc/supervisord.d)

