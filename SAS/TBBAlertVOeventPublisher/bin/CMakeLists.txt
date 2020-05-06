lofar_add_bin_scripts(tbbalertvoeventpublisher)

# supervisord config files
install(FILES
  tbbalertvoeventpublisher.ini
  DESTINATION etc/supervisord.d)

