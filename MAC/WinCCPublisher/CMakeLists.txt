lofar_package(WinCCPublisher 1.0 DEPENDS Messaging WinCCWrapper)

include(LofarFindPackage)
lofar_find_package(WINCC REQUIRED)
lofar_find_package(QPID REQUIRED)

include_directories(${WinCCWrapper_SOURCE_DIR}/include/)

add_subdirectory(src)
add_subdirectory(test)
