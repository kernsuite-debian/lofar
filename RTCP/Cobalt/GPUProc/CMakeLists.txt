# $Id$

# Note: in Cobalt1 the initial implementation was in OpenCL.
# But the dev-team changed to CUDA quite soon.
# The OpenCL implementation was sort of mirrored and kept in sync with the CUDA implementation.
# But, the OpenCL was never really used in production...
# So, for Cobalt2 we (Jan David and Jorrit) decided to remove the OpenCL implementation to reduced maintenance costs.
# If we would like to see/use the OpenCL implementation, just have a look in svn history.

set(_gpuproc_deps "")

# We use runtime compilation, except for 2 tests compiled by nvcc.
# nvcc passes our C++ flags to GCC for C compilation printing spurious warnings. Suppress.
set(CUDA_PROPAGATE_HOST_FLAGS OFF)
lofar_find_package(CUDA 4.1 REQUIRED)
lofar_find_package(CUDADriver REQUIRED)

if(LOFAR_BUILD_VARIANT MATCHES "^DEBUG$")
  list(APPEND CUDA_NVCC_FLAGS -g -G)
endif()

lofar_package(GPUProc 1.0 DEPENDS Common Stream ApplCommon CoInterface InputProc MACIO BrokenAntennaInfo MessageBus Docker pyparameterset ${_gpuproc_deps})

lofar_find_package(OpenMP REQUIRED)
lofar_find_package(Boost REQUIRED)
lofar_find_package(MPI REQUIRED)
lofar_find_package(LibNuma)
lofar_find_package(FFTW3 COMPONENTS single double threads REQUIRED)
lofar_find_package(UnitTest++)

# InputProc/Delays.h drags in a dependency on casa; hence we need to add the
# following line. This should be fixed someday.
lofar_find_package(Casacore COMPONENTS casa)

if(USE_VALGRIND)
  lofar_find_package(Valgrind)
  if(VALGRIND_FOUND)
    add_definitions(-DUSE_VALGRIND)
  else()
    message(WARNING "USE_VALGRIND requested, but not found!")
  endif()
endif()  

add_subdirectory(src)
add_subdirectory(test)
add_subdirectory(share)
add_subdirectory(etc)
