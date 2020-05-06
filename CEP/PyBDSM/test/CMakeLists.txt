# $Id$

include(LofarCTest)

configure_file(setpythonpath.run_tmpl setpythonpath.run_script)
lofar_add_test(tbdsm_import)
lofar_add_test(tbdsm_process_image)
