# $Id$

include(FindPythonModule)
find_python_module(flask REQUIRED)

python_install(
    __init__.py
    scraper.py
    store.py
    report.py
    ingesteventhandler.py
    webservice/webservice.py
    webservice/__init__.py
    DESTINATION lofar/lta/ltastorageoverview)

set(sql_files ltaso/create_db_ltastorageoverview.sql)
lofar_add_data_files(${sql_files})

set(web_files webservice/templates/index.html)

install(FILES ${web_files}
  DESTINATION ${PYTHON_INSTALL_DIR}/lofar/lta/ltastorageoverview/webservice/templates/)

foreach(web_file ${web_files})
    get_filename_component(web_file_path ${web_file} PATH)
    get_filename_component(web_file_abs ${web_file} ABSOLUTE)

    file(MAKE_DIRECTORY ${_build_dir}/${web_file_path})
    execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink ${web_file_abs} ${_build_dir}/${web_file})
endforeach(web_file ${web_files})

