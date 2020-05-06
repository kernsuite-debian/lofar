# $Id: CMakeLists.txt  $

set(_py_files
    __init__.py
    cable_reflection.py
    down.py
    down_old.py
    flat.py
    noise.py
    oscillation.py
    peakslib.py
    rf_power.py
    short.py
    spurious.py
    summator_noise.py
    tools.py
)

python_install(${_py_files} DESTINATION lofar/lcu/checkhardware/checkhardware_lib/spectrum_checks)
