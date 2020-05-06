include(PythonInstall)

set(_py_files
  __init__.py
  taskmanagement_rpc.py
)

python_install(${_py_files} DESTINATION lofar/mac/services/taskmanagement/client)
