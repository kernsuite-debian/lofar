
find_python_module(pysimplesoap REQUIRED) # sudo pip3 install PySimpleSOAP

python_install(ingestmomadapter.py
               ingestjobmanagementserver.py
               DESTINATION lofar/lta/ingest/server)
