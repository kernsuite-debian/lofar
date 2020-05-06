lofar_package(LTAIngestCommon 2.0 DEPENDS PyMessaging PyCommon)

python_install(config.py
               job.py
               srm.py
               DESTINATION lofar/lta/ingest/common)

lofar_add_bin_scripts(surl_to_turl)

add_subdirectory(test)
