# $Id: CMakeLists.txt 720 2014-12-08 16:29:33Z loose $

lofar_package(PyCommon 1.0)

lofar_find_package(Python 2.6 REQUIRED)
include(PythonInstall)

include(FindPythonModule)
find_python_module(psycopg2)

set(_py_files
  __init__.py
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
  subprocess.py
  test_utils.py)

python_install(${_py_files} DESTINATION lofar/common)

add_subdirectory(test)
