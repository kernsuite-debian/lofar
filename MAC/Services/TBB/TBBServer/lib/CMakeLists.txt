
include(PythonInstall)

python_install(tbbservice.py
               tbbservice_config.py
               DESTINATION lofar/mac/tbbservice/server)
