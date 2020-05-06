lofar_package(LTAIngestServerCommon 2.0 DEPENDS LTAIngestCommon)

python_install(config.py
               DESTINATION lofar/lta/ingest/server)
