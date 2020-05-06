lofar_find_package(Python 3.4 REQUIRED)
lofar_package(SpecificationServices 0.1 DEPENDS PyMessaging MoMQueryService MessageBus XSD)

include(PythonInstall)

add_subdirectory(lib)
add_subdirectory(bin)
add_subdirectory(test)
add_subdirectory(xml)

# TelescopeModel template files
lofar_add_data_files(xml/telescope_model_type1_template.xml)
lofar_add_data_files(xml/telescope_model_type2_template.xml)
