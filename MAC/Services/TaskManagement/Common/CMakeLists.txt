lofar_package(TaskManagementCommon 1.0)

lofar_find_package(Python 3.4 REQUIRED)

include(PythonInstall)

set(_py_files
  __init__.py
  config.py
)

python_install(${_py_files} DESTINATION lofar/mac/services/taskmanagement/common)
