# Wrapper around WinCC API to read/write to datapoints from/to WinCC database, includes boost python bindings
lofar_package(WinCCWrapper 1.0 )

include(LofarFindPackage)

#hard-coded path where wincc api can be found on build systems
#set(WINCC_ROOT_DIR /opt/WinCC_OA/3.15 CACHE PATH "root dir where the WinCC_OA api can be found")
lofar_find_package(WINCC)

IF(WINCC_FOUND)
    lofar_find_package(Boost REQUIRED python3)
    lofar_find_package(Python 3.4 REQUIRED)

    add_subdirectory(include)
    add_subdirectory(src)
ELSE()
    MESSAGE(WARNING "The WinCC_OA API could not be found (WINCC_ROOT_DIR=${WINCC_ROOT_DIR}). Hence, the WinCCWrapper library cannot be build. We do continue with cmake-configure and build however, because for development one could use a mocked WinCCWrapper as well.")
ENDIF(WINCC_FOUND)

# add subdir test anyway, it will install a mock, even on non-WinCC API systems.
add_subdirectory(test)
