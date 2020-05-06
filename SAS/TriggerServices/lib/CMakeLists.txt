lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

find_python_module(gcn REQUIRED)

set(_py_files
    trigger_service.py
    trigger_service_rpc.py
    trigger_cancellation_service.py
    voevent_listener.py
    voevent_decider.py
    task_info_cache.py
    config.py
    )

python_install(${_py_files}
    DESTINATION lofar/triggerservices)


