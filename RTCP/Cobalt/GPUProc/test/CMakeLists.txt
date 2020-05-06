# $Id$

include(LofarCTest)

# Add current source directory to -I path. This is needed because some
# source files and headers in subdirectories include UnitTest.h
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

lofar_add_test(tBandPass tBandPass.cc)
lofar_add_test(t_generate_globalfs_locations)
lofar_add_test(tMPIReceive tMPIReceive.cc)
lofar_add_test(tRSPRawSender tRSPRawSender.cc)
if(UNITTEST++_FOUND)
  lofar_add_test(t_gpu_utils t_gpu_utils)
  lofar_add_test(tStationInput tStationInput)
  
endif()

add_subdirectory(Kernels)
add_subdirectory(Pipelines)
add_subdirectory(Storage)
add_subdirectory(SubbandProcs)
add_subdirectory(cuda)
