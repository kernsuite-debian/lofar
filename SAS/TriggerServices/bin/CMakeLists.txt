lofar_add_bin_scripts(triggerrestinterface)
lofar_add_bin_scripts(triggerservice)
lofar_add_bin_scripts(triggercancellationservice)

# supervisord config files
install(FILES
  triggerservice.ini
  triggercancellationservice.ini
  DESTINATION etc/supervisord.d)

