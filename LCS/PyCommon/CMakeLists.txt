# $Id: CMakeLists.txt 720 2014-12-08 16:29:33Z loose $

lofar_package(PyCommon 1.0)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

include(FindPythonModule)
find_python_module(psycopg2)

set(_py_files
  __init__.py
  ssh_utils.py
  cep4_utils.py
  threading_utils.py
  lcu_utils.py
  cache.py
  dbcredentials.py
  defaultmailaddresses.py
  factory.py
  math.py
  methodtrigger.py
  util.py
  postgres.py
  datetimeutils.py
  flask_utils.py
  h5_utils.py
  subprocess_utils.py
  xmlparse.py
  test_utils.py)

python_install(${_py_files} DESTINATION lofar/common)

lofar_add_bin_scripts(dbcredentials)

add_subdirectory(test)
