
find_python_module(requests REQUIRED) #sudo pip3 install requests

python_install(ingesttransferserver.py
               ltacp.py
               unspecifiedSIP.py
               ltaclient.py
               momclient.py
               sip.py
               ingestpipeline.py
               DESTINATION lofar/lta/ingest/server)
