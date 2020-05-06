# $Id$

lofar_package(MessageLogger 1.0 DEPENDS PyMessaging)

lofar_find_package(Python 3.4 REQUIRED)

include(PythonInstall)
python_install(messagelogger.py DESTINATION lofar/messaging)

lofar_add_bin_scripts(messagelogger)

# supervisord config files
install(FILES
  messagelogger.ini
  DESTINATION etc/supervisord.d)

