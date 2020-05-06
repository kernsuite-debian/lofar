include(LofarCTest)

IF(BUILD_TESTING)
    lofar_find_package(WINCC)

    IF(WINCC_FOUND)
        include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include)

        lofar_add_bin_program(WinCCSet WinCCSet.cc)
        lofar_add_bin_program(WinCCGet WinCCGet.cc)
        lofar_add_bin_program(WinCCQuery WinCCQuery.cc)
        find_package(Boost COMPONENTS program_options system REQUIRED)

        target_link_libraries(WinCCQuery
            wincc_wrapper
            ${Boost_LIBRARIES}

        )

    ENDIF(WINCC_FOUND)
ENDIF(BUILD_TESTING)

# always add the mock.py module with the mocked WinCCWrapper, so it is available for development and testing,
# even without an active wincc instance.
include(PythonInstall)
python_install(mock.py DESTINATION lofar/common/wincc/test)
