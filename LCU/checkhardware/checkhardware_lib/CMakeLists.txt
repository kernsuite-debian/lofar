# $Id: CMakeLists.txt  $

set(_py_files
    __init__.py
    data.py
    db.py
    general.py
    hardware_tests.py
    hba.py
    lba.py
    lofar.py
    reporting.py
    rsp.py
    settings.py
    spu.py
    tbb.py
)

python_install(${_py_files} DESTINATION lofar/lcu/checkhardware/checkhardware_lib)

add_subdirectory(spectrum_checks)