# $Id$

include(FindPythonModule)

find_python_module(fabric)

lofar_add_bin_scripts(
  pipelinecontrol
  observationcontrol2
)

python_install(
  PipelineControl.py
  ObservationControl2.py
  observation_control_rpc.py
  config.py
  DESTINATION lofar/mac
)

# supervisord config files
install(FILES
  pipelinecontrol.ini
  observationcontrol2.ini
  DESTINATION etc/supervisord.d)
