lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

set(_py_files
    tbb_alert_voevent_publisher.py
    config.py)

python_install(${_py_files}
    DESTINATION lofar/tbbalertvoeventpublisher)


