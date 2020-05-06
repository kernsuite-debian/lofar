
lofar_add_bin_scripts(ingestwebserver)

# supervisord config files
install(FILES
  ingestwebserver.ini
  DESTINATION etc/supervisord.d)

