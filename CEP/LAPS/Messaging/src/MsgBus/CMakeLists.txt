# $Id: CMakeLists.txt 30341 2014-11-03 14:22:52Z peterzon $

include(PythonInstall)

python_install(
  __init__.py
  MsgBus.py
  DESTINATION LAPS/)