# $Id$

lofar_add_bin_scripts(ltastorageoverviewscraper
                      ltastorageoverviewreport
                      ltastorageoverviewwebservice)

# supervisord config files
install(FILES
  ltastorageoverviewscraper.ini
  ltastorageoverviewwebservice.ini
  DESTINATION etc/supervisord.d)
