# $Id: CMakeLists.txt 35890 2016-11-03 13:16:09Z schoenmakers $

include(LofarPackageVersion)
include(PythonInstall)

set(messagebus_LIB_SRCS
  Package__Version.cc
  FromBus.cc
  LogSink.cc
  Message.cc
  MessageBus.cc
  NoQpidFallback.cc
  ToBus.cc
  Util.cc
  XMLDoc.cc
  Protocols/TaskFeedbackState.cc)

set(messagebus_PROGRAMS
)

lofar_add_library(messagebus ${messagebus_LIB_SRCS})

foreach(prog ${messagebus_PROGRAMS})
  lofar_add_bin_program(${prog} ${prog}.cc)
endforeach(prog ${messagebus_PROGRAMS})

python_install(
  __init__.py
  messagebus.py
  message.py
  noqpidfallback.py
  DESTINATION lofar/messagebus)

add_subdirectory(Protocols)
