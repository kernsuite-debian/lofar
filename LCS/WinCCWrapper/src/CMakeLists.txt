include(LofarPackageVersion)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include)

lofar_add_library(wincc_wrapper
    WinCCManager.cc
    WinCCResources.cc
    WinCCWrapper.cc
    ConnectWaitForAnswer.cc)

# Try to find Boost-Python.
# If found, build the bindings, otherwise give a warning.
FIND_PATH(BOOST_PYTHON_FOUND "boost/python.hpp")

if(BOOST_PYTHON_FOUND)
    # create python modules and boost python bindings

    include(LofarFindPackage)
    lofar_find_package(Python 3.4 REQUIRED)
    lofar_find_package(Boost REQUIRED COMPONENTS python3)
    include(PythonInstall)

    set(_py_files __init__.py)
    SET(WINCC_PACKAGE_PATH "lofar/common/wincc")
    python_install(${_py_files} DESTINATION ${WINCC_PACKAGE_PATH})

    lofar_add_library(pywincc MODULE WinCCWrapper_boost_python.cc)
    set_target_properties(pywincc PROPERTIES  PREFIX "" LIBRARY_OUTPUT_DIRECTORY ${PYTHON_BUILD_DIR}/${WINCC_PACKAGE_PATH})
    target_link_libraries(pywincc ${BOOST_LIBRARIES})
    target_link_libraries(pywincc wincc_wrapper)

    # This is a quick-and-dirty fix to install the Python binding module in the
    # right place. It will now be installed twice, because lofar_add_library()
    # will install it in $prefix/$libdir
    install(TARGETS pywincc DESTINATION ${PYTHON_INSTALL_DIR}/${WINCC_PACKAGE_PATH})
else()
  message (WARNING, "Boost-Python not found; not building python bindings for wincc.")
endif()

