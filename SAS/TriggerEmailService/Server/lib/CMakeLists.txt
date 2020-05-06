include(PythonInstall)

set(_py_files
  __init__.py
  TriggerEmailService.py
  Templates.py
)

python_install(${_py_files} DESTINATION lofar/sas/TriggerEmailService)
