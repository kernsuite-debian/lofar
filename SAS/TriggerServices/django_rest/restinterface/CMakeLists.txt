lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
    __init__.py
    credentials.py
    settings.py
    urls.py
    wsgi.py
    )

python_install(${_py_files}
    DESTINATION lofar/triggerservices/restinterface/)


add_subdirectory(triggerinterface)
