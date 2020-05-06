# service
lofar_add_bin_scripts(TriggerEmailService)

# supervisord config files
install(FILES
  TriggerEmailService.ini
  DESTINATION etc/supervisord.d)
