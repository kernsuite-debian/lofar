# $Id: CMakeLists.txt 30977 2015-02-11 14:01:26Z mol $

include(PythonInstall)

python_install(
  __init__.py
  taskfeedbackdataproducts.py
  taskfeedbackprocessing.py
  taskfeedbackstate.py
  DESTINATION lofar/messagebus/protocols)
