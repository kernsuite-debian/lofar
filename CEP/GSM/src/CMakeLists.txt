# $Id: CMakeLists.txt 32581 2015-10-15 13:45:24Z loose $

include(PythonInstall)

# Install Python modules
python_install(
  __init__.py
  gsmutils.py
  gsm_exceptions.py
  DESTINATION lofar/gsm)

lofar_add_bin_scripts(gsm.py)
