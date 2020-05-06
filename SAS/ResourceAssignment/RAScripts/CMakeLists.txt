# $Id$

lofar_package(RAScripts 1.0 DEPENDS PyMessaging ResourceAssignmentService OTDB_Services pyparameterset)

lofar_find_package(Python 3.4 REQUIRED)
include(PythonInstall)

lofar_add_bin_scripts(povero)
