# service
lofar_add_bin_scripts(taskmanagement)

# supervisord config files
install(FILES
  taskmanagement.ini
  DESTINATION etc/supervisord.d)
