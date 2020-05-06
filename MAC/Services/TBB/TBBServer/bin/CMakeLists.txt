
lofar_add_bin_scripts(tbbservice)

# supervisord config files
install(FILES
  tbbservice.ini
  DESTINATION etc/supervisord.d)

