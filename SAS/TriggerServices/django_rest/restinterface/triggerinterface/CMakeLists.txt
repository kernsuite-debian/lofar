lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
    __init__.py
    config.py
    admin.py
    apps.py
    views.py
    )

python_install(${_py_files}
    DESTINATION lofar/triggerservices/restinterface/triggerinterface)
