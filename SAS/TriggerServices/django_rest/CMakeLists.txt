lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)
include(FindPythonModule)
find_python_module(django REQUIRED)
find_python_module(rest_framework REQUIRED)     # pip install djangorestframework
find_python_module(rest_framework_xml REQUIRED) # pip install djangorestframework-xml
find_python_module(ldap REQUIRED)

set(_py_files
    manage.py
    urls.py
    )

python_install(${_py_files}
    DESTINATION lofar/triggerservices/)

add_subdirectory(restinterface)
