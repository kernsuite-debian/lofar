
lofar_add_bin_scripts(ingesttransferserver
                      ltacp
                      ingestpipeline)

# supervisord config files
install(FILES
  ingesttransferserver.ini
  DESTINATION etc/supervisord.d)

add_subdirectory(md5a32bc)
