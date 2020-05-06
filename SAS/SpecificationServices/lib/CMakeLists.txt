# $Id$

lofar_find_package(Python 3.4 REQUIRED)

include(PythonInstall)
include(FindPythonModule)
find_python_module(lxml REQUIRED)
find_python_module(xmljson REQUIRED)

set(_py_files
  __init__.py
  config.py
  specification_service.py
  specification_service_rpc.py
  telescope_model.py
  telescope_model_xml_generator_type1.py
  translation_service.py
  translation_service_rpc.py
  validation_service.py
  validation_service_rpc.py
  lofarxml_to_momxmlmodel_translator.py
  lofarxml_to_momxml_translator.py
)

python_install(${_py_files}
               DESTINATION lofar/specificationservices)
