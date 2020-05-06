# $Id: CMakeLists.txt 38601 2017-10-09 18:42:23Z klazema $

include(PythonInstall)

python_install(
  tbb_config.py
  tbb_util.py
  tbb_freeze.py
  tbb_load_firmware.py
  tbb_release_recording.py
  tbb_restart_recording.py
  tbb_set_storage.py
  tbb_start_recording.py
  tbb_upload_to_cep.py
  tbb_caltables.py
  tbb_cable_delays.py
  DESTINATION lofar/mac/tbb
)

