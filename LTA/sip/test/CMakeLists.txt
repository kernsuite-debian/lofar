# $Id: CMakeLists.txt 32909 2015-11-18 10:26:41Z schaap $
include(LofarCTest)

lofar_add_test(test_validator)
lofar_add_test(test_siplib)
lofar_add_test(test_feedback)
lofar_add_test(test_visualizer)



set(test_resource_files
  sipfrommom.xml
  valid_sip.xml
  testmetadata_file.Correlated.modified
)


install(FILES ${test_resource_files}
               DESTINATION /tmp/)
