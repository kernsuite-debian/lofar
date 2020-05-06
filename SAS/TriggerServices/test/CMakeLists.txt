include(LofarCTest)
include(FindPythonModule)

find_python_module(dateutil)

lofar_add_test(t_trigger_service)
lofar_add_test(t_trigger_cancellation_service)
lofar_add_test(t_voevent_listener)
lofar_add_test(t_voevent_decider)
