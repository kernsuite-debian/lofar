
python_install(ingestwebserver.py
               DESTINATION lofar/lta/ingest/webserver)


set(web_files
    static/js/jquery.min.js
    static/js/highcharts.js)

foreach(web_file ${web_files})
    get_filename_component(web_file_path ${web_file} PATH)
    get_filename_component(web_file_abs ${web_file} ABSOLUTE)

    file(MAKE_DIRECTORY ${_build_dir}/${web_file_path})
    execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink ${web_file_abs} ${_build_dir}/${web_file})

    install(FILES ${web_file_abs} DESTINATION ${PYTHON_INSTALL_DIR}/lofar/lta/ingest/webserver/${web_file_path})
endforeach(web_file ${web_files})
