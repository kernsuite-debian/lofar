lofar_add_bin_scripts(specificationservice)
lofar_add_bin_scripts(specificationtranslationservice)
lofar_add_bin_scripts(specificationvalidationservice)

# supervisord config files
install(FILES
  specificationservice.ini
  specificationtranslationservice.ini
  specificationvalidationservice.ini
  DESTINATION etc/supervisord.d)
